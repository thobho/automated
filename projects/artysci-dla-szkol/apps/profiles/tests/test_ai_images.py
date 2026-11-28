import json
import logging

import pytest
from django.test import override_settings

from apps.profiles import ai
from apps.profiles.ai import budget, images
from apps.profiles.models import AICall

from .test_ai import KEY, Transport

pytestmark = pytest.mark.django_db

PNG = images.PNG_MAGIC + b"fake-png-body"
JPEG = images.JPEG_MAGIC + b"fake-jpeg-body"


def messages(*data, text="Oceń stronę, kontakt: a@example.invalid"):
    parts = [{"type": "text", "text": text}] + [{"type": "image", "data": d} for d in data]
    return [{"role": "user", "content": parts}]


def send(client, msgs, **kwargs):
    kwargs.setdefault("purpose", "test")
    kwargs.setdefault("max_cost_usd", "0.01")
    return client.complete(msgs, **kwargs)


def test_image_part_refused_without_allow_images():
    client = ai.FakeClient()
    with pytest.raises(ai.AIError):
        send(client, messages(PNG))
    assert client.requests == []


@pytest.mark.parametrize("data", [b"GIF89a....", b"<svg/>", b"", b"x" * 10])
def test_unsupported_type_refused_before_sending(data):
    client = ai.FakeClient()
    with pytest.raises(ai.AIError):
        send(client, messages(data), allow_images=True)
    assert client.requests == []


def test_too_large_image_refused():
    client = ai.FakeClient()
    big = images.PNG_MAGIC + b"0" * images.MAX_IMAGE_BYTES
    with pytest.raises(ai.AIError):
        send(client, messages(big), allow_images=True)
    assert client.requests == []


def test_too_many_images_refused():
    client = ai.FakeClient()
    with pytest.raises(ai.AIError):
        send(client, messages(*[PNG] * (images.MAX_IMAGES_PER_CALL + 1)), allow_images=True)
    assert client.requests == []


def test_type_is_sniffed_not_trusted():
    client = ai.FakeClient()
    msgs = [
        {"role": "user", "content": [{"type": "image", "data": b"abc", "media_type": "image/png"}]}
    ]
    with pytest.raises(ai.AIError):
        send(client, msgs, allow_images=True)


@pytest.mark.parametrize("part", [{"type": "audio"}, {"type": "image", "data": "str"}, "x"])
def test_unknown_parts_refused(part):
    with pytest.raises(ai.AIError):
        send(ai.FakeClient(), [{"role": "user", "content": [part]}], allow_images=True)


def test_empty_parts_refused():
    with pytest.raises(ai.AIError):
        send(ai.FakeClient(), [{"role": "user", "content": []}], allow_images=True)


def test_fake_client_accepts_png_and_jpeg_and_scrubs_text():
    client = ai.FakeClient()
    result = send(client, messages(PNG, JPEG), allow_images=True)
    assert result.text
    sent = client.requests[0].messages[0]["content"]
    assert "a@example.invalid" not in sent[0]["text"]
    assert [p["type"] for p in sent] == ["text", "image", "image"]


def test_text_only_requests_unchanged_with_allow_images():
    client = ai.FakeClient()
    msgs = [{"role": "user", "content": "Cześć"}]
    send(client, msgs, allow_images=True)
    assert client.requests[0].messages == msgs


def test_estimate_counts_images():
    text_only = budget.estimate_prompt_tokens([{"role": "user", "content": "abc"}])
    with_two = budget.estimate_prompt_tokens(
        [
            {
                "role": "user",
                "content": [{"type": "text", "text": "abc"}] + [{"type": "image", "data": PNG}] * 2,
            }
        ]
    )
    assert with_two == text_only + 2 * images.IMAGE_TOKENS_ESTIMATE


@override_settings(AI_PRICE_PROMPT_USD_PER_MTOK="100", AI_PER_CALL_CAP_USD="0.5")
def test_per_call_cap_counts_images_and_sends_nothing():
    client = ai.FakeClient()
    # 8000 image tokens * 100 USD/Mtok = 0.8 USD > 0.5
    with pytest.raises(ai.AICapExceeded):
        send(client, messages(PNG, PNG), allow_images=True, max_cost_usd="0.5")
    assert client.requests == []


@override_settings(
    AI_PRICE_PROMPT_USD_PER_MTOK="10", AI_PER_CALL_CAP_USD="0.5", AI_DAILY_CAP_USD="0.05"
)
def test_daily_cap_sends_nothing():
    client = ai.FakeClient()
    with pytest.raises(ai.AICapExceeded):
        send(client, messages(PNG), allow_images=True, max_cost_usd="0.1")
    assert client.requests == []


def test_openrouter_body_has_data_url_and_no_image_is_logged_or_stored(caplog):
    caplog.set_level(logging.DEBUG)
    transport = Transport()
    client = ai.OpenRouterClient(api_key=KEY, transport=transport)
    send(client, messages(PNG), allow_images=True)
    parts = transport.sent["messages"][0]["content"]
    assert parts[1]["type"] == "image_url"
    assert parts[1]["image_url"]["url"].startswith("data:image/png;base64,")
    call = AICall.objects.get()
    stored = json.dumps({f.name: str(getattr(call, f.name)) for f in call._meta.fields})
    assert "base64" not in stored and "fake-png-body" not in stored
    assert "base64" not in caplog.text and "fake-png-body" not in caplog.text
