"""SSRF-safe fetch (US-2.2, SECURITY.md "Import ze strony"). DNS and the transport are faked;
the real socket transport is tested against a server on loopback (no outside network)."""

import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from apps.core import safefetch
from apps.core.safefetch import FetchError, RawResponse, Target

PUBLIC = "93.184.215.14"


class FakeNet:
    """DNS table + pages by URL; records every (host, address, path) connected to."""

    def __init__(self):
        self.dns: dict[str, list[str]] = {}
        self.pages: dict[str, RawResponse] = {}
        self.connections: list[tuple[str, str, str]] = []
        self.lookups: list[str] = []

    def resolver(self, host, port, type=0):
        self.lookups.append(host)
        if host in self.dns:
            return [(socket.AF_INET, type, 6, "", (a, port)) for a in self.dns[host]]
        try:  # IP literals resolve to themselves, like getaddrinfo
            import ipaddress

            ipaddress.ip_address(host)
        except ValueError as exc:
            raise socket.gaierror("no such host") from exc
        return [(socket.AF_INET, type, 6, "", (host, port))]

    def transport(self, target: Target, address, *, timeout, max_bytes):
        self.connections.append((target.host, address, target.path))
        page = self.pages.get(target.url)
        if page is None:
            return RawResponse(404, {"content-type": "text/html"}, b"")
        if len(page.body) > max_bytes:
            raise safefetch._error("too_large")
        return page


@pytest.fixture
def net(monkeypatch):
    fake = FakeNet()
    monkeypatch.setattr(safefetch, "resolver", fake.resolver)
    monkeypatch.setattr(safefetch, "transport", fake.transport)
    return fake


def html(body=b"<p>ok</p>", status=200, **headers):
    return RawResponse(status, {"content-type": "text/html; charset=utf-8", **headers}, body)


def fetch(url, **kw):
    return safefetch.fetch(url, max_bytes=kw.pop("max_bytes", 1000), timeout=1, **kw)


# --- forbidden addresses (table) -------------------------------------------------------------

FORBIDDEN = [
    ("http://127.0.0.1/", "blocked"),
    ("http://127.1.2.3/", "blocked"),
    ("http://10.0.0.5/", "blocked"),
    ("http://172.16.0.1/", "blocked"),
    ("http://192.168.1.1/", "blocked"),
    ("http://169.254.169.254/latest/meta-data/", "blocked"),
    ("http://100.64.0.1/", "blocked"),  # shared (CGNAT)
    ("http://0.0.0.0/", "blocked"),
    ("http://224.0.0.1/", "blocked"),  # multicast
    ("http://240.0.0.1/", "blocked"),  # reserved
    ("http://255.255.255.255/", "blocked"),
    ("http://198.18.0.1/", "blocked"),  # benchmarking
    ("http://192.0.2.1/", "blocked"),  # documentation
    ("http://[::1]/", "blocked"),
    ("http://[::]/", "blocked"),
    ("http://[::ffff:127.0.0.1]/", "blocked"),
    ("http://[::ffff:169.254.169.254]/", "blocked"),
    ("http://[::ffff:10.0.0.5]/", "blocked"),
    ("http://[fe80::1]/", "blocked"),  # link-local
    ("http://[fc00::1]/", "blocked"),  # unique local
    ("http://[ff02::1]/", "blocked"),  # multicast
    ("http://[2002:7f00:1::]/", "blocked"),  # 6to4 wrapping 127.0.0.1
    ("http://[64:ff9b::a9fe:a9fe]/", "blocked"),  # NAT64 wrapping 169.254.169.254
    ("http://[2001:db8::1]/", "blocked"),  # documentation
    ("http://[2001:0:4136:e378:8000:63bf:3fff:fdd2]/", "blocked"),  # Teredo
    ("http://[::127.0.0.1]/", "blocked"),  # IPv4-compatible (deprecated)
    ("ftp://example.com/", "scheme"),
    ("file:///etc/passwd", "scheme"),
    ("gopher://example.com/", "scheme"),
    ("javascript:alert(1)", "scheme"),
    ("http://user:pass@example.com/", "credentials"),
    ("http://user@example.com/", "credentials"),
    ("http://example.com:22/", "port"),
    ("http://example.com:8080/", "port"),
    ("http:///nohost", "bad_url"),
    ("http://exa mple.com/", "bad_url"),
    ("", "bad_url"),
    ("http://[::1/", "bad_url"),
]


@pytest.mark.parametrize(("url", "code"), FORBIDDEN)
def test_forbidden_urls_are_refused_without_a_connection(net, url, code):
    with pytest.raises(FetchError) as caught:
        fetch(url)
    assert caught.value.code == code
    assert str(caught.value.message)  # readable Polish message
    assert net.connections == []


@pytest.mark.parametrize(
    "address",
    ["127.0.0.1", "10.1.2.3", "169.254.169.254", "::1", "::ffff:192.168.0.1", "fd00::5"],
)
def test_public_name_resolving_to_private_address_is_refused(net, address):
    net.dns["artysta.example"] = [address]
    with pytest.raises(FetchError) as caught:
        fetch("http://artysta.example/")
    assert caught.value.code == "blocked"
    assert net.connections == []


def test_one_private_address_among_public_ones_is_enough_to_refuse(net):
    net.dns["artysta.example"] = [PUBLIC, "10.0.0.1"]
    with pytest.raises(FetchError, match="blocked"):
        fetch("http://artysta.example/")
    assert net.connections == []


def test_unknown_host_is_a_dns_error(net):
    with pytest.raises(FetchError) as caught:
        fetch("http://nie-ma.example/")
    assert caught.value.code == "dns"


@pytest.mark.parametrize(
    "address", ["93.184.215.14", "8.8.8.8", "2606:2800:21f:cb07:6820:80da:af6b:8b2c"]
)
def test_public_addresses_are_allowed(address):
    assert safefetch.is_public(address)


def test_is_public_rejects_garbage():
    assert not safefetch.is_public("not-an-ip")


# --- connection pinning, redirects ------------------------------------------------------------


def test_connects_to_the_checked_address_with_the_host_name(net):
    net.dns["artysta.example"] = [PUBLIC]
    net.pages["https://artysta.example/o-nas?x=1"] = html()
    response = fetch("https://Artysta.Example/o-nas?x=1")
    assert response.status == 200 and response.content_type == "text/html"
    assert response.charset == "utf-8"
    assert net.connections == [("artysta.example", PUBLIC, "/o-nas?x=1")]
    assert net.lookups == ["artysta.example"]  # one lookup, the address is reused


def test_redirect_to_private_address_is_refused(net):
    net.dns["artysta.example"] = [PUBLIC]
    net.dns["wewnetrzny.example"] = ["10.0.0.7"]
    net.pages["http://artysta.example/"] = html(status=302, location="http://wewnetrzny.example/")
    with pytest.raises(FetchError, match="blocked"):
        fetch("http://artysta.example/")
    assert [c[0] for c in net.connections] == ["artysta.example"]


def test_redirect_to_metadata_ip_is_refused(net):
    net.dns["artysta.example"] = [PUBLIC]
    net.pages["http://artysta.example/"] = html(
        status=301, location="http://169.254.169.254/latest/meta-data/"
    )
    with pytest.raises(FetchError, match="blocked"):
        fetch("http://artysta.example/")
    assert len(net.connections) == 1


def test_three_redirects_are_followed(net):
    net.dns["artysta.example"] = [PUBLIC]
    for n in range(3):
        net.pages[f"http://artysta.example/{n}"] = html(status=301, location=f"/{n + 1}")
    net.pages["http://artysta.example/3"] = html(b"koniec")
    response = fetch("http://artysta.example/0")
    assert response.body == b"koniec" and response.url == "http://artysta.example/3"
    assert len(response.redirects) == 3


def test_four_redirects_stop_the_fetch(net):
    net.dns["artysta.example"] = [PUBLIC]
    for n in range(4):
        net.pages[f"http://artysta.example/{n}"] = html(status=302, location=f"/{n + 1}")
    net.pages["http://artysta.example/4"] = html(b"koniec")
    with pytest.raises(FetchError, match="redirects"):
        fetch("http://artysta.example/0")
    assert len(net.connections) == 4  # the 5th URL is never requested


def test_redirect_to_ftp_is_refused(net):
    net.dns["artysta.example"] = [PUBLIC]
    net.pages["http://artysta.example/"] = html(status=302, location="ftp://artysta.example/")
    with pytest.raises(FetchError, match="scheme"):
        fetch("http://artysta.example/")


def test_site_host_restricts_redirects(net):
    net.dns["artysta.example"] = [PUBLIC]
    net.dns["obcy.example"] = [PUBLIC]
    net.pages["http://artysta.example/a"] = html(status=302, location="http://obcy.example/")
    with pytest.raises(FetchError, match="other_host"):
        fetch("http://artysta.example/a", site_host="www.artysta.example")
    assert [c[0] for c in net.connections] == ["artysta.example"]


def test_body_over_the_cap_is_refused(net):
    net.dns["artysta.example"] = [PUBLIC]
    net.pages["http://artysta.example/"] = html(b"x" * 2000)
    with pytest.raises(FetchError, match="too_large"):
        fetch("http://artysta.example/", max_bytes=1000)


def test_network_error_tries_the_next_address(net, monkeypatch):
    net.dns["artysta.example"] = [PUBLIC, "8.8.8.8"]
    calls = []

    def flaky(target, address, *, timeout, max_bytes):
        calls.append(address)
        if address == PUBLIC:
            raise safefetch._error("network")
        return html(b"ok")

    monkeypatch.setattr(safefetch, "transport", flaky)
    assert fetch("http://artysta.example/").body == b"ok"
    assert calls == [PUBLIC, "8.8.8.8"]


def test_network_error_on_every_address(net, monkeypatch):
    net.dns["artysta.example"] = [PUBLIC]

    def down(target, address, *, timeout, max_bytes):
        raise safefetch._error("network")

    monkeypatch.setattr(safefetch, "transport", down)
    with pytest.raises(FetchError, match="network"):
        fetch("http://artysta.example/")


def test_idn_host_is_encoded():
    assert safefetch.check_url("https://teatr-żak.example/").host == "xn--teatr-ak-83b.example"


def test_target_url_formats_ipv6_and_ports():
    assert Target("http", "::1", 8000, "/a").url == "http://[::1]:8000/a"
    assert Target("https", "a.example", 443, "/").url == "https://a.example/"


def test_loopback_escape_hatch_is_off_by_default_and_works_when_on(settings, net):
    assert safefetch.is_public("127.0.0.1") is False
    settings.SAFE_FETCH_ALLOW_LOOPBACK = True
    assert safefetch.is_public("127.0.0.1") is True
    assert safefetch.check_url("http://127.0.0.1:8765/").port == 8765
    assert safefetch.is_public("10.0.0.1") is False  # only loopback, never private ranges


# --- the real socket transport (loopback server, not the outside network) ---------------------


class _Handler(BaseHTTPRequestHandler):
    routes: dict = {}
    seen_hosts: list = []

    def do_GET(self):  # noqa: N802
        type(self).seen_hosts.append(self.headers.get("Host"))
        action = self.routes.get(self.path, "ok")
        if action == "slow":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            for _ in range(50):
                try:
                    self.wfile.write(b"x")
                    self.wfile.flush()
                except OSError:
                    return
                time.sleep(0.1)
            return
        body = b"y" * 5000 if action == "big" else b"<p>ok</p>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        if action != "no-length":
            self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body if action != "no-length" else b"z" * 5000)

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    _Handler.routes = {"/slow": "slow", "/big": "big", "/stream": "no-length"}
    _Handler.seen_hosts = []
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()


def test_socket_transport_uses_given_address_and_host_header(server):
    target = Target("http", "artysta.example", server, "/")
    raw = safefetch.socket_transport(target, "127.0.0.1", timeout=5, max_bytes=1000)
    assert raw.status == 200 and raw.body == b"<p>ok</p>"
    assert _Handler.seen_hosts == [f"artysta.example:{server}"]  # no DNS for the name


def test_socket_transport_stops_a_slow_page_at_the_deadline(server):
    target = Target("http", "artysta.example", server, "/slow")
    started = time.monotonic()
    with pytest.raises(FetchError, match="timeout"):
        safefetch.socket_transport(target, "127.0.0.1", timeout=0.5, max_bytes=10_000)
    assert time.monotonic() - started < 2


@pytest.mark.parametrize("path", ["/big", "/stream"])
def test_socket_transport_caps_the_body(server, path):
    target = Target("http", "artysta.example", server, path)
    with pytest.raises(FetchError, match="too_large"):
        safefetch.socket_transport(target, "127.0.0.1", timeout=5, max_bytes=1000)


def test_socket_transport_connection_refused_is_a_network_error():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    with pytest.raises(FetchError, match="network"):
        safefetch.socket_transport(
            Target("http", "a.example", port, "/"), "127.0.0.1", timeout=2, max_bytes=10
        )


def test_https_connection_uses_host_name_for_tls(monkeypatch):
    seen = {}

    class Ctx:
        def wrap_socket(self, sock, server_hostname):
            seen["sni"] = server_hostname
            return sock

    monkeypatch.setattr(
        safefetch.socket,
        "create_connection",
        lambda addr, timeout: seen.setdefault("addr", addr) and object(),
    )
    conn = safefetch._PinnedHTTPSConnection("artysta.example", 443, PUBLIC, 5)
    conn._context = Ctx()
    conn.connect()
    assert seen == {"addr": (PUBLIC, 443), "sni": "artysta.example"}


def test_hosted_settings_refuse_the_loopback_hatch(monkeypatch):
    import importlib
    import sys

    from django.core.exceptions import ImproperlyConfigured

    for key, value in {
        "DJANGO_SECRET_KEY": "x" * 60,
        "DJANGO_ALLOWED_HOSTS": "example.invalid",
        "DATABASE_URL": "sqlite://:memory:",
        "MEDIA_PUBLIC_BASE_URL": "https://media.example.invalid/",
        "MALWARE_SCANNER": "clamd",
        "SAFE_FETCH_ALLOW_LOOPBACK": "true",
    }.items():
        monkeypatch.setenv(key, value)
    for module in ("config.settings.base", "config.settings.hosted", "config.settings.prod"):
        monkeypatch.delitem(sys.modules, module, raising=False)
    with pytest.raises(ImproperlyConfigured, match="SAFE_FETCH_ALLOW_LOOPBACK"):
        importlib.import_module("config.settings.prod")
    for module in ("config.settings.base", "config.settings.hosted", "config.settings.prod"):
        monkeypatch.delitem(sys.modules, module, raising=False)
