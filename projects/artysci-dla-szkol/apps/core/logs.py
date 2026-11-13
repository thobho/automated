"""Structured JSON logging: request ids, pseudonymised users, redaction, access log.

One config for every environment (LOGGING in config/settings/base.py): each line on stdout is
one JSON object. No e-mail addresses, full IP addresses, cookie values or secrets end up in a
log line: messages, exception text and extra string fields go through `redact()`.
"""

import contextvars
import ipaddress
import json
import logging
import re
import time
import uuid
from datetime import UTC, datetime

from django.utils.crypto import salted_hmac

access_logger = logging.getLogger("access")

_current_request = contextvars.ContextVar("current_request", default=None)

REQUEST_ID_HEADER = "X-Request-ID"
_INCOMING_ID = re.compile(r"^[A-Za-z0-9_.-]{8,64}$")

# Extra fields a log call may pass with `extra={...}` that end up in the JSON line.
EXTRA_FIELDS = ("method", "path", "status", "duration_ms", "ip", "event", "count")

# --- Redaction -----------------------------------------------------------------------------

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
_SENSITIVE_NAMES = (
    r"password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|"
    r"authorization|cookie|session(?:id)?|csrf(?:token|middlewaretoken)?|__Host-[A-Za-z]+"
)
# key=value, key: value, "key": "value" (also inside query strings and JSON)
_KEY_VALUE = re.compile(
    rf"""(?ix)
    (\b[\w-]*(?:{_SENSITIVE_NAMES})[\w-]*["']?\s*[:=]\s*["']?)
    ([^\s"'&,;}}]+)
    """
)
_AUTH_SCHEME = re.compile(r"(?i)\b(bearer|basic|token)\s+[A-Za-z0-9._~+/=-]{8,}")
_IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
_IPV6_CANDIDATE = re.compile(r"(?<![\w:])[0-9A-Fa-f:]*:[0-9A-Fa-f:]*:[0-9A-Fa-f:.]*(?![\w:])")


def truncate_ip(value: str) -> str:
    """Keep the network part only: IPv4 /24, IPv6 /48. Anything else becomes ''."""
    try:
        ip = ipaddress.ip_address(value.strip())
    except ValueError:
        return ""
    prefix = 24 if ip.version == 4 else 48
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False).network_address)


def _mask_ip(match: re.Match) -> str:
    return truncate_ip(match.group(0)) or match.group(0)


def redact(text: str) -> str:
    """Remove e-mails, secrets (key=value, auth headers) and the host part of IP addresses."""
    text = _EMAIL.sub("[email]", text)
    text = _AUTH_SCHEME.sub(lambda m: f"{m.group(1)} [redacted]", text)
    text = _KEY_VALUE.sub(lambda m: f"{m.group(1)}[redacted]", text)
    text = _IPV4.sub(_mask_ip, text)
    return _IPV6_CANDIDATE.sub(_mask_ip, text)


# --- Who and which request -----------------------------------------------------------------


def pseudonymise_user(user_pk) -> str:
    """Stable, non-reversible id for a user (HMAC of the pk with SECRET_KEY)."""
    return salted_hmac("logs.user", str(user_pk)).hexdigest()[:16]


def _user_of(request, *, resolve: bool) -> str:
    """'-' for anonymous. Without `resolve`, only a user Django already loaded is used,
    so logging never triggers a session/database lookup by itself."""
    if request is None:
        return "-"
    try:
        user = getattr(request, "user", None) if resolve else getattr(request, "_cached_user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            return "-"
        return pseudonymise_user(user.pk)
    except Exception:  # e.g. session store down: logging must not fail
        return "-"


def client_ip(request) -> str:
    """Truncated client address. Only REMOTE_ADDR is trusted (proxy headers are spoofable
    until hosting is decided, D91)."""
    return truncate_ip(request.META.get("REMOTE_ADDR", ""))


class RequestContextFilter(logging.Filter):
    """Adds `request_id` and `user` to every record logged while a request is handled."""

    def filter(self, record):
        request = _current_request.get()
        if not hasattr(record, "request_id"):
            record.request_id = getattr(request, "request_id", "-") if request else "-"
        if not hasattr(record, "user"):
            record.user = _user_of(request, resolve=False)
        return True


class JsonFormatter(logging.Formatter):
    """One JSON object per line; known fields only, every string redacted."""

    def format(self, record):
        entry = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": redact(record.getMessage()),
            "request_id": getattr(record, "request_id", "-"),
            "user": getattr(record, "user", "-"),
        }
        for field in EXTRA_FIELDS:
            if hasattr(record, field):
                value = getattr(record, field)
                entry[field] = redact(value) if isinstance(value, str) else value
        if record.exc_info:
            entry["exc"] = redact(self.formatException(record.exc_info))
        return json.dumps(entry, ensure_ascii=False, default=str)


# --- Middleware ----------------------------------------------------------------------------


def _request_id(request) -> str:
    incoming = request.headers.get(REQUEST_ID_HEADER, "")
    return incoming if _INCOMING_ID.match(incoming) else uuid.uuid4().hex


class RequestIdMiddleware:
    """First middleware: assigns a request id (reuses a well-formed incoming X-Request-ID),
    returns it in the response header and writes one access log line per request.

    The access line has the path without the query string (it may carry tokens or e-mails).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = _request_id(request)
        token = _current_request.set(request)
        started = time.monotonic()
        try:
            response = self.get_response(request)
            response[REQUEST_ID_HEADER] = request.request_id
            self._log(request, response.status_code, started)
            return response
        finally:
            _current_request.reset(token)

    @staticmethod
    def _log(request, status: int, started: float) -> None:
        level = logging.ERROR if status >= 500 else logging.INFO
        access_logger.log(
            level,
            "%s %s %s",
            request.method,
            request.path,
            status,
            extra={
                "method": request.method,
                "path": request.path,
                "status": status,
                "duration_ms": round((time.monotonic() - started) * 1000, 1),
                "ip": client_ip(request),
                "user": _user_of(request, resolve=True),
            },
        )
