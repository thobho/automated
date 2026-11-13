import io
import json
import logging
import urllib.error
import urllib.request
from datetime import timedelta
from decimal import Decimal

import pytest
from django.test import override_settings
from django.utils import timezone

from apps.profiles import ai
from apps.profiles.ai import budget
from apps.profiles.ai.fake import example_for
from apps.profiles.ai.openrouter import urllib_transport
from apps.profiles.models import AICall

pytestmark = pytest.mark.django_db

KEY = "sk-or-test-key-never-logged"
MESSAGES = [
    {"role": "system", "content": "Piszesz opisy artystów."},
    {"role": "user", "content": "Zespół Dźwięki, kontakt: zespol@example.invalid, +48 601 234 567"},
]
OK_REPLY = {
    "id": "gen-123",
    "model": "anthropic/claude-haiku-5.5",
    "provider": "Google",
    "choices": [{"message": {"role": "assistant", "content": "Opis."}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 40, "completion_tokens": 3, "total_tokens": 43, "cost": 0.0000059},
}


class Transport:
    """Captures requests instead of sending them; replies with a fixed status and body."""

    def __init__(self, status=200, body=OK_REPLY, exc=None):
        self.status, self.body, self.exc = status, body, exc
        self.calls = []

    def __call__(self, url, headers, body, timeout):
        self.calls.append({"url": url, "headers": headers, "body": body, "timeout": timeout})
        if self.exc:
            raise self.exc
        raw = self.body if isinstance(self.body, bytes) else json.dumps(self.body).encode()
        return self.status, raw

    @property
    def sent(self):
        return json.loads(self.calls[-1]["body"])


def openrouter(transport, **kwargs):
    return ai.OpenRouterClient(api_key=KEY, transport=transport, **kwargs)


def call(client, **kwargs):
    kwargs.setdefault("purpose", "test")
    kwargs.setdefault("max_cost_usd", "0.01")
    return client.complete(MESSAGES, **kwargs)


# --- Request shape -----------------------------------------------------------------------


def test_request_shape_has_privacy_flags_pinned_model_and_pseudonymous_user():
    transport = Transport()
    call(openrouter(transport, providers=["google-vertex", "amazon-bedrock"]), user_ref=42)

    sent = transport.sent
    assert transport.calls[0]["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert sent["model"] == "anthropic/claude-haiku-5.5"
    assert "models" not in sent  # no model fallback list
    provider = sent["provider"]
    assert provider["data_collection"] == "deny"
    assert provider["zdr"] is True
    assert provider["only"] == ["google-vertex", "amazon-bedrock"]
    assert provider["order"] == ["google-vertex", "amazon-bedrock"]
    assert provider["allow_fallbacks"] is True
    assert provider["max_price"] == {"prompt": 0.11, "completion": 0.55}
    assert sent["usage"] == {"include": True}
    assert sent["user"].startswith("u-")
    assert "42" not in sent["user"]
    assert sent["user"] == ai.base.pseudonymous_user(42)  # stable
    assert 0 < sent["max_tokens"] <= 2048
    assert transport.calls[0]["headers"]["Authorization"] == f"Bearer {KEY}"


def test_request_body_contains_no_email_or_phone():
    transport = Transport()
    call(openrouter(transport))

    body = transport.calls[0]["body"].decode()
    assert "zespol@example.invalid" not in body
    assert "601 234 567" not in body
    assert "[email]" in body and "[phone]" in body


@override_settings(AI_SCRUB_NAMES=["Jan Kowalski"])
def test_configured_and_per_call_names_scrubbed():
    transport = Transport()
    openrouter(transport).complete(
        [{"role": "user", "content": "Jan Kowalski i Ewa Zielińska"}],
        purpose="test",
        max_cost_usd="0.01",
        scrub_names=["Ewa Zielińska"],
    )
    assert transport.sent["messages"][0]["content"] == "[name] i [name]"


def test_schema_becomes_strict_json_schema_and_requires_parameters():
    schema = {"type": "object", "properties": {"bio": {"type": "string"}}, "required": ["bio"]}
    transport = Transport(body={**OK_REPLY, "choices": [{"message": {"content": '{"bio": "x"}'}}]})
    result = call(openrouter(transport), schema=schema)

    assert transport.sent["response_format"] == {
        "type": "json_schema",
        "json_schema": {"name": "result", "strict": True, "schema": schema},
    }
    assert transport.sent["provider"]["require_parameters"] is True
    assert result.data == {"bio": "x"}


def test_anonymous_calls_use_system_user():
    transport = Transport()
    call(openrouter(transport))
    assert transport.sent["user"] == "system"


# --- Recording ---------------------------------------------------------------------------


def test_call_is_recorded_with_usage_cost_and_no_text():
    result = call(openrouter(Transport()), purpose="profile_draft")

    row = AICall.objects.get(pk=result.call_id)
    assert row.status == AICall.Status.OK
    assert row.cost_usd == Decimal("0.0000059")  # exactly usage.cost
    assert result.cost_usd == Decimal("0.0000059")
    assert (row.prompt_tokens, row.completion_tokens) == (40, 3)
    assert row.purpose == "profile_draft"
    assert row.model == "anthropic/claude-haiku-5.5"
    assert row.provider == "Google"
    assert row.generation_id == "gen-123"
    assert row.client == "openrouter"
    assert row.latency_ms >= 0
    stored = " ".join(str(v) for v in AICall.objects.values().get(pk=row.pk).values())
    assert "Dźwięki" not in stored and "Opis." not in stored


def test_missing_usage_cost_keeps_worst_case():
    body = {**OK_REPLY, "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
    result = call(openrouter(Transport(body=body)), max_cost_usd="0.02")
    assert AICall.objects.get(pk=result.call_id).cost_usd == Decimal("0.02")


@pytest.mark.parametrize(
    ("status", "body", "code"),
    [
        (402, {"error": {"code": 402, "message": "Insufficient credits"}}, "http_402"),
        (200, {"error": {"code": 502, "message": "upstream"}}, "http_502"),
        (500, b"<html>oops</html>", "bad_json"),
        (200, {"choices": []}, "no_choices"),
    ],
)
def test_provider_errors_raise_and_are_recorded_at_zero_cost(status, body, code):
    with pytest.raises(ai.AIProviderError) as info:
        call(openrouter(Transport(status=status, body=body)))
    assert info.value.code == code
    row = AICall.objects.get()
    assert (row.status, row.error, row.cost_usd) == ("error", code, Decimal(0))


def test_timeout_keeps_reserved_cost():
    exc = ai.AIProviderError("timed out", code="timeout", maybe_billed=True)
    with pytest.raises(ai.AIProviderError):
        call(openrouter(Transport(exc=exc)), max_cost_usd="0.03")
    row = AICall.objects.get()
    assert (row.status, row.error, row.cost_usd) == ("error", "timeout", Decimal("0.03"))


def test_unexpected_error_keeps_reserved_cost():
    with pytest.raises(RuntimeError):
        call(openrouter(Transport(exc=RuntimeError("boom"))), max_cost_usd="0.03")
    row = AICall.objects.get()
    assert (row.error, row.cost_usd) == ("unexpected", Decimal("0.03"))


def test_invalid_json_with_schema_raises_but_records_cost():
    with pytest.raises(ai.AIProviderError) as info:
        call(openrouter(Transport()), schema={"type": "object"})
    assert info.value.code == "invalid_json"
    row = AICall.objects.get()
    assert (row.status, row.cost_usd) == ("error", Decimal("0.0000059"))


# --- Cost caps and kill switch -----------------------------------------------------------


@override_settings(AI_DAILY_CAP_USD="0.05")
def test_daily_cap_reached_sends_nothing():
    AICall.objects.create(
        client="openrouter", purpose="x", model="m", status="ok", cost_usd=Decimal("0.05")
    )
    transport = Transport()
    with pytest.raises(ai.AICapExceeded):
        call(openrouter(transport))
    assert transport.calls == []
    assert AICall.objects.count() == 1


@override_settings(AI_DAILY_CAP_USD="0.05")
def test_daily_cap_counts_the_calls_worst_case():
    AICall.objects.create(
        client="fake", purpose="x", model="m", status="ok", cost_usd=Decimal("0.045")
    )
    with pytest.raises(ai.AICapExceeded):
        call(ai.FakeClient(), max_cost_usd="0.01")
    call(ai.FakeClient(), max_cost_usd="0.005")  # fits exactly


@override_settings(AI_DAILY_CAP_USD="0.05")
def test_pending_reservations_count_against_the_cap():
    AICall.objects.create(
        client="fake", purpose="x", model="m", status="pending", cost_usd=Decimal("0.05")
    )
    with pytest.raises(ai.AICapExceeded):
        call(ai.FakeClient())


@override_settings(AI_DAILY_CAP_USD="0.05")
def test_yesterdays_spend_does_not_count():
    row = AICall.objects.create(
        client="fake", purpose="x", model="m", status="ok", cost_usd=Decimal("1")
    )
    AICall.objects.filter(pk=row.pk).update(created_at=budget.start_of_today() - timedelta(1))
    assert call(ai.FakeClient()).call_id


@override_settings(AI_PER_CALL_CAP_USD="0.05")
@pytest.mark.parametrize("max_cost", ["0.06", "0", "-1"])
def test_per_call_cap_sends_nothing(max_cost):
    transport = Transport()
    with pytest.raises(ai.AICapExceeded):
        call(openrouter(transport), max_cost_usd=max_cost)
    assert transport.calls == []
    assert not AICall.objects.exists()


def test_prompt_too_expensive_for_max_cost_sends_nothing():
    transport = Transport()
    huge = [{"role": "user", "content": "x" * 300_000}]  # ~100k tokens at 0.11/M = 0.011 USD
    with pytest.raises(ai.AICapExceeded):
        openrouter(transport).complete(huge, purpose="test", max_cost_usd="0.01")
    assert transport.calls == []


def test_max_tokens_limited_by_max_cost():
    transport = Transport()
    call(openrouter(transport), max_cost_usd="0.0001")
    max_tokens = transport.sent["max_tokens"]
    prompt_tokens = budget.estimate_prompt_tokens(transport.sent["messages"])
    worst = (prompt_tokens * Decimal("0.11") + max_tokens * Decimal("0.55")) / 1_000_000
    assert 0 < max_tokens < 2048
    assert worst <= Decimal("0.0001")


@override_settings(AI_KILL_SWITCH=True)
def test_kill_switch_sends_nothing():
    transport = Transport()
    with pytest.raises(ai.AIDisabled):
        call(openrouter(transport))
    assert transport.calls == []
    assert not AICall.objects.exists()


@override_settings(AI_KILL_SWITCH=True)
def test_kill_switch_also_stops_the_fake_client():
    with pytest.raises(ai.AIDisabled):
        ai.complete(MESSAGES, purpose="test", max_cost_usd="0.01")


def test_blocked_calls_are_logged_without_prompt(caplog):
    with (
        override_settings(AI_KILL_SWITCH=True),
        caplog.at_level(logging.WARNING),
        pytest.raises(ai.AIDisabled),
    ):
        call(ai.FakeClient(), purpose="profile_draft")
    assert "blocked purpose=profile_draft" in caplog.text
    assert "zespol" not in caplog.text


# --- Input checks and config -------------------------------------------------------------


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [{"role": "tool", "content": "x"}],
        [{"role": "user", "content": [{"type": "text", "text": "a@example.invalid"}]}],
    ],
)
def test_invalid_messages_rejected(messages):
    with pytest.raises(ai.AIError):
        ai.FakeClient().complete(messages, purpose="test", max_cost_usd="0.01")


@pytest.mark.parametrize("purpose", ["", "x" * 51])
def test_invalid_purpose_rejected(purpose):
    with pytest.raises(ai.AIError):
        ai.FakeClient().complete(MESSAGES, purpose=purpose, max_cost_usd="0.01")


def test_openrouter_needs_key_and_providers():
    with pytest.raises(ai.AIConfigError):
        ai.OpenRouterClient()  # test settings: OPENROUTER_API_KEY=""
    with pytest.raises(ai.AIConfigError):
        ai.OpenRouterClient(api_key=KEY, providers=[])


@override_settings(AI_PRICE_COMPLETION_USD_PER_MTOK="0")
def test_zero_completion_price_is_a_config_error():
    with pytest.raises(ai.AIConfigError):
        ai.FakeClient()


def test_key_never_in_repr_or_logs(caplog):
    client = openrouter(Transport())
    assert KEY not in repr(client)
    with caplog.at_level(logging.DEBUG):
        call(client)
        with pytest.raises(ai.AIProviderError):
            call(openrouter(Transport(status=401, body={"error": {"code": 401}})))
    assert KEY not in caplog.text


def test_get_client_follows_settings():
    assert isinstance(ai.get_client(), ai.FakeClient)
    with override_settings(AI_CLIENT="openrouter", OPENROUTER_API_KEY=KEY):
        assert isinstance(ai.get_client(), ai.OpenRouterClient)
    with override_settings(AI_CLIENT="nope"), pytest.raises(ai.AIConfigError):
        ai.get_client()


# --- urllib transport (no network: urlopen is replaced) ----------------------------------


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return b'{"ok": true}'


def test_urllib_transport_posts_and_returns_body(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen.update(method=request.get_method(), data=request.data, timeout=timeout)
        return _Response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    status, raw = urllib_transport("https://example.invalid", {"A": "b"}, b"{}", 5)
    assert (status, raw) == (200, b'{"ok": true}')
    assert seen == {"method": "POST", "data": b"{}", "timeout": 5}


def test_urllib_transport_returns_http_errors(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url, 429, "Too Many", {}, io.BytesIO(b'{"error": {"code": 429}}')
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert urllib_transport("https://example.invalid", {}, b"{}", 5)[0] == 429


@pytest.mark.parametrize(
    ("exc", "code", "billed"),
    [
        (TimeoutError("slow"), "timeout", True),
        (urllib.error.URLError(TimeoutError("slow")), "timeout", True),
        (urllib.error.URLError("dns"), "network", False),
    ],
)
def test_urllib_transport_maps_network_errors(monkeypatch, exc, code, billed):
    def fake_urlopen(request, timeout):
        raise exc

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(ai.AIProviderError) as info:
        urllib_transport("https://example.invalid", {}, b"{}", 5)
    assert (info.value.code, info.value.maybe_billed) == (code, billed)


# --- FakeClient --------------------------------------------------------------------------


def test_fake_client_is_deterministic():
    first, second = call(ai.FakeClient()), call(ai.FakeClient())
    assert first.text == second.text
    assert first.text.startswith("[fake reply ")
    other = ai.FakeClient().complete(
        [{"role": "user", "content": "inny"}], purpose="test", max_cost_usd="0.01"
    )
    assert other.text != first.text


def test_fake_client_records_scrubbed_requests_and_its_cost():
    client = ai.FakeClient(cost_usd="0.001")
    result = call(client)
    assert "zespol@example.invalid" not in json.dumps(client.requests[0].messages)
    row = AICall.objects.get(pk=result.call_id)
    assert (row.client, row.status, row.cost_usd) == ("fake", "ok", Decimal("0.001"))


def test_fake_client_schema_reply_matches_schema():
    schema = {
        "type": "object",
        "properties": {
            "bio": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "years": {"type": "integer"},
            "kind": {"enum": ["band", "solo"]},
            "ok": {"type": "boolean"},
            "note": {"type": ["null", "string"]},
            "meta": {"type": "object", "properties": {"n": {"type": "number"}}},
            "none": {"type": "null"},
        },
    }
    first = call(ai.FakeClient(), schema=schema)
    assert first.data == call(ai.FakeClient(), schema=schema).data
    assert first.data["tags"] == [] and first.data["years"] == 0
    assert first.data["kind"] == "band" and first.data["ok"] is False
    assert first.data["meta"] == {"n": 0} and first.data["none"] is None
    assert first.data["bio"].startswith("fake-")


def test_fake_client_custom_reply():
    assert call(ai.FakeClient(reply="stała")).text == "stała"
    assert call(ai.FakeClient(reply=lambda r: r.purpose)).text == "test"


def test_example_for_defaults_to_object():
    assert example_for({}) == {}


def test_admin_list_is_read_only(admin_client):
    call(ai.FakeClient())
    response = admin_client.get("/django-admin/profiles/aicall/")
    assert response.status_code == 200
    assert admin_client.get("/django-admin/profiles/aicall/add/").status_code == 403


def test_start_of_today_is_local_midnight():
    start = budget.start_of_today()
    assert timezone.localtime(start).hour == 0
    assert start <= timezone.now()
