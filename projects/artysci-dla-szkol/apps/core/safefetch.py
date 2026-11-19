"""The one way to fetch a URL a user gave us (US-2.2 website import): SSRF-safe HTTP GET.

No other code may request user-given URLs. The rules:

- only ``http`` and ``https``, no user-info, only the default ports (80, 443);
- the host is resolved once and *every* address must be public: loopback, private, link-local
  (incl. ``169.254.169.254``), shared (CGNAT), multicast, reserved and unspecified addresses
  and their IPv6 forms (incl. IPv4-mapped, 6to4 and NAT64 wrappers of such addresses) are
  refused before any connection;
- the socket connects to the checked address itself (no second DNS lookup), with the original
  host name for the ``Host`` header and for TLS (SNI and certificate check);
- every redirect target goes through the same checks, at most `max_redirects` of them;
- one hard deadline for the whole request (connect, headers and body, a watchdog shuts the
  socket) and a byte cap on the body; no compression is accepted (no decompression bombs).

Error messages are Polish and safe to show; they never contain the address.
"""

import http.client
import ipaddress
import socket
import ssl
import threading
import time
import urllib.parse
from dataclasses import dataclass, field

from django.conf import settings
from django.utils.translation import gettext_lazy as _

DEFAULT_PORTS = {"http": 80, "https": 443}
REDIRECT_CODES = {301, 302, 303, 307, 308}
MAX_URL_LENGTH = 2000
USER_AGENT = "artysci-dla-szkol-import/1.0 (+import strony artysty)"
NAT64 = ipaddress.ip_network("64:ff9b::/96")
CHUNK = 64 * 1024


class FetchError(Exception):
    """The URL cannot or may not be fetched. `code` is stable; `message` is Polish."""

    def __init__(self, code: str, message):
        super().__init__(code)
        self.code = code
        self.message = message


MESSAGES = {
    "bad_url": _("To nie jest poprawny adres strony."),
    "scheme": _("Adres musi zaczynać się od http:// albo https://."),
    "credentials": _("Adres nie może zawierać loginu ani hasła."),
    "port": _("Adres nie może wskazywać innego portu niż standardowy (80 lub 443)."),
    "blocked": _("Tego adresu nie można pobrać: wskazuje sieć wewnętrzną, a nie publiczną stronę."),
    "dns": _("Nie znaleziono serwera o tej nazwie. Sprawdź adres strony."),
    "other_host": _("Strona przekierowuje na inny serwis; pobieramy tylko Twoją stronę."),
    "redirects": _("Strona przekierowuje zbyt wiele razy."),
    "timeout": _("Strona odpowiadała zbyt długo."),
    "too_large": _("Strona jest zbyt duża."),
    "network": _("Nie udało się połączyć ze stroną."),
    "tls": _("Nie udało się nawiązać bezpiecznego połączenia (certyfikat strony)."),
}


def _error(code: str) -> FetchError:
    return FetchError(code, MESSAGES[code])


@dataclass(frozen=True)
class Target:
    scheme: str
    host: str  # ASCII (IDNA) host name or IP literal, without brackets
    port: int
    path: str  # path and query, never empty

    @property
    def url(self) -> str:
        host = f"[{self.host}]" if ":" in self.host else self.host
        default = DEFAULT_PORTS[self.scheme] == self.port
        return f"{self.scheme}://{host}{'' if default else f':{self.port}'}{self.path}"


@dataclass(frozen=True)
class Response:
    url: str  # final URL after redirects
    status: int
    content_type: str  # media type, lower case, without parameters
    body: bytes
    charset: str = ""
    redirects: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawResponse:
    status: int
    headers: dict  # lower-case names
    body: bytes


def _allow_loopback() -> bool:
    """Test-only escape hatch (SAFE_FETCH_ALLOW_LOOPBACK): lets a local synthetic site be
    imported in dev. Hosted settings (prod, pirx) refuse to load with it on."""
    return bool(getattr(settings, "SAFE_FETCH_ALLOW_LOOPBACK", False))


def check_url(url: str) -> Target:
    """Parse and check a URL without any network access. Raises `FetchError`."""
    url = (url or "").strip()
    if not url or len(url) > MAX_URL_LENGTH or any(ch.isspace() or ord(ch) < 32 for ch in url):
        raise _error("bad_url")
    try:
        parts = urllib.parse.urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise _error("bad_url") from exc
    if parts.scheme.lower() not in DEFAULT_PORTS:
        raise _error("scheme")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise _error("credentials")
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").rstrip(".")
    if not host:
        raise _error("bad_url")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        try:
            host = host.encode("idna").decode("ascii").lower()
        except UnicodeError as exc:
            raise _error("bad_url") from exc
    if port is None:
        port = DEFAULT_PORTS[scheme]
    elif port != DEFAULT_PORTS[scheme] and not _allow_loopback():
        raise _error("port")
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"
    return Target(scheme=scheme, host=host, port=port, path=path)


def check_offline(url: str) -> Target:
    """`check_url` plus the address check of an IP literal host: everything that can be refused
    without DNS. A host name passes (it is resolved and checked by `fetch`)."""
    target = check_url(url)
    try:
        ipaddress.ip_address(target.host)
    except ValueError:
        return target
    if not is_public(target.host):
        raise _error("blocked")
    return target


def _unwrap(ip: ipaddress.IPv4Address | ipaddress.IPv6Address):
    """The IPv4 address an IPv6 address carries (mapped, 6to4, NAT64), else the address."""
    if ip.version == 6:
        if ip.ipv4_mapped is not None:
            return ip.ipv4_mapped
        if ip.sixtofour is not None:
            return ip.sixtofour
        if ip in NAT64:
            return ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF)
    return ip


def is_public(address: str) -> bool:
    """True only for a globally reachable unicast address (IPv4 inside IPv6 is unwrapped)."""
    try:
        ip = _unwrap(ipaddress.ip_address(address.split("%", 1)[0]))
    except ValueError:
        return False
    if _allow_loopback() and ip.is_loopback:
        return True
    return ip.is_global and not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or (ip.version == 6 and ip.teredo is not None)
    )


# Tests replace this (no DNS in tests).
resolver = socket.getaddrinfo


def resolve_public(host: str, port: int) -> list[str]:
    """Every address of `host`; raises `FetchError` "blocked" if any is not public."""
    try:
        infos = resolver(host, port, type=socket.SOCK_STREAM)
    except (OSError, UnicodeError) as exc:
        raise _error("dns") from exc
    addresses = list(dict.fromkeys(info[4][0] for info in infos))
    if not addresses:
        raise _error("dns")
    if not all(is_public(address) for address in addresses):
        raise _error("blocked")
    return addresses


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout)
        self._address = address

    raw_sock = None  # kept for the watchdog: http.client drops `sock` once the body starts

    def connect(self):
        self.sock = self.raw_sock = socket.create_connection(
            (self._address, self.port), self.timeout
        )


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    raw_sock = None

    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._address = address

    def connect(self):
        sock = self.raw_sock = socket.create_connection((self._address, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def _shutdown(conn) -> None:
    sock = conn.raw_sock
    if sock is not None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass


def socket_transport(target: Target, address: str, *, timeout: float, max_bytes: int):
    """One GET of `target` over a socket connected to `address`. Returns `RawResponse`.

    Raises `FetchError` "timeout", "too_large", "tls" or "network". A watchdog shuts the
    socket at the deadline, so a server dripping bytes cannot hold the job longer.
    """
    cls = _PinnedHTTPSConnection if target.scheme == "https" else _PinnedHTTPConnection
    conn = cls(target.host, target.port, address, timeout)
    deadline = time.monotonic() + timeout
    expired = threading.Event()

    def stop():
        expired.set()
        _shutdown(conn)

    watchdog = threading.Timer(timeout, stop)
    watchdog.daemon = True
    watchdog.start()
    try:
        conn.request(
            "GET",
            target.path,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,image/*;q=0.8,*/*;q=0.1",
                "Accept-Encoding": "identity",
                "Connection": "close",
            },
        )
        response = conn.getresponse()
        headers = {k.lower(): v for k, v in response.getheaders()}
        length = headers.get("content-length", "")
        if length.isdigit() and int(length) > max_bytes:
            raise _error("too_large")
        body = bytearray()
        while True:
            if time.monotonic() > deadline:
                raise _error("timeout")
            chunk = response.read(min(CHUNK, max_bytes + 1 - len(body)))
            if not chunk:
                break
            body.extend(chunk)
            if len(body) > max_bytes:
                raise _error("too_large")
        if expired.is_set():
            raise _error("timeout")
        return RawResponse(response.status, headers, bytes(body))
    except FetchError:
        raise
    except ssl.SSLError as exc:
        raise _error("timeout" if expired.is_set() else "tls") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise _error("timeout") from exc
    except (OSError, http.client.HTTPException) as exc:
        raise _error("timeout" if expired.is_set() else "network") from exc
    finally:
        watchdog.cancel()
        conn.close()


# Tests replace this with a fake site; it is the only way the module opens connections.
transport = socket_transport


def _same_site(host: str, site_host: str) -> bool:
    def bare(name: str) -> str:
        return name[4:] if name.startswith("www.") else name

    return bare(host) == bare(site_host)


def _media_type(headers: dict) -> tuple[str, str]:
    value = headers.get("content-type", "")
    media_type, _sep, params = value.partition(";")
    charset = ""
    for param in params.split(";"):
        name, _eq, val = param.strip().partition("=")
        if name.lower() == "charset":
            charset = val.strip().strip('"').lower()
    return media_type.strip().lower(), charset


def fetch(
    url: str,
    *,
    max_bytes: int,
    timeout: float,
    max_redirects: int = 3,
    site_host: str = "",
) -> Response:
    """GET `url` under the rules above and return the final response (any status).

    `site_host` (optional) restricts the URL and every redirect to that host (``www.``
    ignored). `timeout` is per request (each redirect hop gets its own). Raises `FetchError`.
    """
    target = check_url(url)
    hops: list[str] = []
    while True:
        if site_host and not _same_site(target.host, site_host):
            raise _error("other_host")
        addresses = resolve_public(target.host, target.port)
        raw = None
        last_error: FetchError | None = None
        for address in addresses:
            try:
                raw = transport(target, address, timeout=timeout, max_bytes=max_bytes)
                break
            except FetchError as exc:
                if exc.code != "network":
                    raise
                last_error = exc
        if raw is None:
            raise last_error or _error("network")
        location = raw.headers.get("location", "")
        if raw.status in REDIRECT_CODES and location:
            if len(hops) >= max_redirects:
                raise _error("redirects")
            hops.append(target.url)
            target = check_url(urllib.parse.urljoin(target.url, location))
            continue
        media_type, charset = _media_type(raw.headers)
        return Response(
            url=target.url,
            status=raw.status,
            content_type=media_type,
            body=raw.body,
            charset=charset,
            redirects=hops,
        )
