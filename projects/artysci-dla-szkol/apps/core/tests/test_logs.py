import io
import json
import logging

import pytest
from django.contrib.auth import get_user_model

from apps.core import logs

FAKE_EMAIL = "jan.kowalski@example.invalid"
FAKE_TOKEN = "tok_9f8e7d6c5b4a39281706"


@pytest.fixture
def captured():
    """Lines written through the real formatter and filter, as parsed JSON."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logs.JsonFormatter())
    handler.addFilter(logs.RequestContextFilter())
    # "django" does not propagate to root (see LOGGING), so listen on both.
    loggers = [logging.getLogger(), logging.getLogger("django")]
    for logger in loggers:
        logger.addHandler(handler)
    yield lambda: [json.loads(line) for line in stream.getvalue().splitlines()]
    for logger in loggers:
        logger.removeHandler(handler)


# --- redact --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        f"user {FAKE_EMAIL} logged in",
        f"token={FAKE_TOKEN}",
        f'{{"api_key": "{FAKE_TOKEN}"}}',
        f"Authorization: Bearer {FAKE_TOKEN}",
        f"Cookie: sessionid={FAKE_TOKEN}; csrftoken=abc",
        f"/reset?email={FAKE_EMAIL}&token={FAKE_TOKEN}",
        f"password: {FAKE_TOKEN}",
        f"__Host-sessionid={FAKE_TOKEN}",
    ],
)
def test_redact_removes_emails_and_secrets(text):
    out = logs.redact(text)
    assert FAKE_EMAIL not in out
    assert FAKE_TOKEN not in out


def test_redact_truncates_ips():
    out = logs.redact("from 203.0.113.77 and 2001:db8:abcd:12:34::5")
    assert "203.0.113.77" not in out and "203.0.113.0" in out
    assert "2001:db8:abcd:12" not in out and "2001:db8:abcd::" in out


def test_redact_keeps_ordinary_text():
    text = "GET /artists/ 200 at 12:30:45, version 2.0.11"
    assert logs.redact(text) == text


@pytest.mark.parametrize(
    ("ip", "expected"),
    [("192.168.1.42", "192.168.1.0"), ("2001:db8:1:2::1", "2001:db8:1::"), ("junk", "")],
)
def test_truncate_ip(ip, expected):
    assert logs.truncate_ip(ip) == expected


def test_pseudonymise_user_is_stable_and_opaque():
    assert logs.pseudonymise_user(1) == logs.pseudonymise_user(1)
    assert logs.pseudonymise_user(1) != logs.pseudonymise_user(2)
    assert len(logs.pseudonymise_user(1)) == 16


# --- formatter -----------------------------------------------------------------------------


def test_log_line_is_json_without_pii(captured):
    logging.getLogger("apps.test").warning(
        "signup failed for %s with token=%s", FAKE_EMAIL, FAKE_TOKEN, extra={"path": "/x"}
    )
    (line,) = captured()
    raw = json.dumps(line)
    assert FAKE_EMAIL not in raw and FAKE_TOKEN not in raw
    assert line["level"] == "WARNING" and line["logger"] == "apps.test"
    assert line["request_id"] == "-" and line["user"] == "-"
    assert line["path"] == "/x"


def test_exceptions_are_redacted(captured):
    try:
        raise ValueError(f"bad address {FAKE_EMAIL}")
    except ValueError:
        logging.getLogger("apps.test").exception("boom")
    (line,) = captured()
    assert "ValueError" in line["exc"] and FAKE_EMAIL not in line["exc"]


def test_log_injection_stays_one_line(captured):
    logging.getLogger("apps.test").info('evil\n{"level": "CRITICAL"}')
    lines = captured()
    assert len(lines) == 1 and lines[0]["level"] == "INFO"


# --- middleware ----------------------------------------------------------------------------

pytestmark_db = pytest.mark.django_db


@pytestmark_db
def test_access_log_line(client, captured):
    response = client.get(
        f"/healthz?email={FAKE_EMAIL}&token={FAKE_TOKEN}",
        REMOTE_ADDR="203.0.113.77",
        HTTP_COOKIE=f"sessionid={FAKE_TOKEN}",
    )
    access = [line for line in captured() if line["logger"] == "access"]
    assert len(access) == 1
    line = access[0]
    raw = json.dumps(line)
    assert line["request_id"] == response["X-Request-ID"]
    assert len(line["request_id"]) == 32
    assert line["method"] == "GET" and line["path"] == "/healthz" and line["status"] == 200
    assert line["ip"] == "203.0.113.0"
    assert line["user"] == "-"
    assert isinstance(line["duration_ms"], float)
    for secret in (FAKE_EMAIL, FAKE_TOKEN, "203.0.113.77", "email=", "?"):
        assert secret not in raw


@pytestmark_db
def test_incoming_request_id_is_reused_only_if_well_formed(client):
    good = "abc-123_DEF.456"
    assert client.get("/healthz", HTTP_X_REQUEST_ID=good)["X-Request-ID"] == good
    bad = client.get("/healthz", HTTP_X_REQUEST_ID="x\nInjected: 1")["X-Request-ID"]
    assert bad != "x\nInjected: 1" and len(bad) == 32


@pytestmark_db
def test_logs_inside_a_request_carry_its_id(captured, rf):
    def view(request):
        logging.getLogger("apps.test").info("inside")
        from django.http import HttpResponse

        return HttpResponse()

    response = logs.RequestIdMiddleware(view)(rf.get("/"))
    inside = next(line for line in captured() if line["msg"] == "inside")
    assert inside["request_id"] == response["X-Request-ID"]


@pytestmark_db
def test_authenticated_user_is_pseudonymised(client, captured):
    user = get_user_model().objects.create_user(email=FAKE_EMAIL, password="x-long-password")
    client.force_login(user)
    client.get("/healthz")
    line = next(line for line in captured() if line["logger"] == "access")
    assert line["user"] == logs.pseudonymise_user(user.pk)
    assert FAKE_EMAIL not in json.dumps(line)


@pytestmark_db
def test_server_errors_log_at_error_level(captured, rf):
    from django.http import HttpResponseServerError

    logs.RequestIdMiddleware(lambda request: HttpResponseServerError())(rf.get("/"))
    line = next(line for line in captured() if line["logger"] == "access")
    assert line["level"] == "ERROR" and line["status"] == 500


def test_user_lookup_failure_does_not_break_logging(rf):
    class Broken:
        @property
        def is_authenticated(self):
            raise RuntimeError("session store down")

    request = rf.get("/")
    request.user = Broken()
    assert logs._user_of(request, resolve=True) == "-"


@pytestmark_db
def test_django_request_warnings_carry_the_request_id(client, captured):
    response = client.get(f"/no-such-page?email={FAKE_EMAIL}")
    line = next(line for line in captured() if line["logger"] == "django.request")
    assert line["msg"] == "Not Found: /no-such-page"
    assert line["request_id"] == response["X-Request-ID"]
