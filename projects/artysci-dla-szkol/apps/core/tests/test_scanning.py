"""Malware scanning interface (US-2.3A): fake and none backends, the clamd INSTREAM protocol
against a local fake socket server, and a real clamd only when CLAMD_HOST is set."""

import io
import logging
import os
import socket
import socketserver
import struct
import tempfile
import threading

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from apps.core import scanning
from apps.core.scanning import ClamdScanner, ScanResult

# The standard antivirus test string (not malware; every scanner reports it).
EICAR = rb"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!H+H*"


class FakeClamd(socketserver.BaseRequestHandler):
    """Speaks clamd's INSTREAM: reads the command and the length-prefixed chunks, then
    answers `server.reply` (or, if None, OK / FOUND depending on the content)."""

    def handle(self):
        sock = self.request
        command = b""
        while not command.endswith(b"\0"):
            command += sock.recv(1)
        self.server.commands.append(command)
        received = b""
        while True:
            header = self._exact(4)
            (length,) = struct.unpack(">I", header)
            if length == 0:
                break
            received += self._exact(length)
        self.server.received.append(received)
        reply = self.server.reply
        if reply is None:
            reply = b"stream: Eicar-Test-Signature FOUND" if b"EICAR" in received else b"stream: OK"
        sock.sendall(reply + b"\0")

    def _exact(self, n):
        data = b""
        while len(data) < n:
            part = self.request.recv(n - len(data))
            if not part:
                raise ConnectionError
            data += part
        return data


def _serve(server):
    server.commands, server.received, server.reply = [], [], None
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@pytest.fixture
def clamd_tcp():
    server = _serve(socketserver.ThreadingTCPServer(("127.0.0.1", 0), FakeClamd))
    yield server
    server.shutdown()
    server.server_close()


@pytest.fixture
def clamd_unix():
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "clamd.sock")
    server = _serve(socketserver.ThreadingUnixStreamServer(path, FakeClamd))
    yield server, path
    server.shutdown()
    server.server_close()
    os.unlink(path)
    os.rmdir(folder)


def tcp_scanner(server, **kwargs):
    host, port = server.server_address
    return ClamdScanner(host=host, port=port, timeout=5, **kwargs)


def test_clamd_clean_file_sends_instream_in_chunks(clamd_tcp, monkeypatch):
    monkeypatch.setattr(scanning, "CHUNK_SIZE", 1000)
    data = b"x" * 2500
    assert tcp_scanner(clamd_tcp).scan(io.BytesIO(data)) == ScanResult.CLEAN
    assert clamd_tcp.commands == [b"zINSTREAM\0"]
    assert clamd_tcp.received == [data]


def test_clamd_reads_from_the_start_of_the_file(clamd_tcp):
    file = io.BytesIO(b"abc")
    file.read()
    assert tcp_scanner(clamd_tcp).scan(file) == ScanResult.CLEAN
    assert clamd_tcp.received == [b"abc"]


def test_clamd_found_is_infected_and_logged(clamd_tcp, caplog):
    with caplog.at_level(logging.WARNING, logger="apps.core.scanning"):
        assert tcp_scanner(clamd_tcp).scan(io.BytesIO(EICAR)) == ScanResult.INFECTED
    assert "Eicar-Test-Signature" in caplog.text


@pytest.mark.parametrize(
    "reply", [b"INSTREAM size limit exceeded. ERROR", b"stream: lstat() failed ERROR", b""]
)
def test_clamd_error_replies_are_errors(clamd_tcp, reply):
    clamd_tcp.reply = reply
    assert tcp_scanner(clamd_tcp).scan(io.BytesIO(b"data")) == ScanResult.ERROR


def test_clamd_over_a_unix_socket(clamd_unix):
    server, path = clamd_unix
    scanner = ClamdScanner(socket_path=path, timeout=5)
    assert scanner.scan(io.BytesIO(b"hello")) == ScanResult.CLEAN
    assert server.received == [b"hello"]


def test_clamd_unreachable_is_an_error(caplog):
    with socket.socket() as probe:  # a free port nobody listens on
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    scanner = ClamdScanner(host="127.0.0.1", port=port, timeout=2)
    with caplog.at_level(logging.WARNING, logger="apps.core.scanning"):
        assert scanner.scan(io.BytesIO(b"x")) == ScanResult.ERROR
    assert "clamd unreachable (ConnectionRefusedError)" in caplog.text


def test_clamd_without_an_address_is_an_error_without_connecting():
    assert ClamdScanner().scan(io.BytesIO(b"x")) == ScanResult.ERROR


def test_fake_backend_answers_the_setting(settings):
    settings.MALWARE_SCANNER = "fake"
    assert scanning.scan(io.BytesIO(b"x")) == ScanResult.CLEAN
    for value in ("infected", "error"):
        settings.MALWARE_SCANNER_FAKE_RESULT = value
        assert scanning.scan(io.BytesIO(b"x")) == ScanResult(value)


def test_none_backend_passes_and_logs_unscanned(settings, caplog):
    settings.MALWARE_SCANNER = "none"
    with caplog.at_level(logging.WARNING, logger="apps.core.scanning"):
        assert scanning.scan(io.BytesIO(b"x")) == ScanResult.CLEAN
    assert [r.event for r in caplog.records] == ["upload_unscanned"]


def test_clamd_backend_from_settings(settings):
    settings.MALWARE_SCANNER = "clamd"
    settings.CLAMD_HOST, settings.CLAMD_PORT, settings.CLAMD_SOCKET = "clamav", 3311, ""
    scanner = scanning.get_scanner()
    assert isinstance(scanner, ClamdScanner)
    assert (scanner.host, scanner.port) == ("clamav", 3311)


def test_unknown_backend_is_refused(settings):
    settings.MALWARE_SCANNER = "magic"
    with pytest.raises(ValueError, match="magic"):
        scanning.get_scanner()


def test_scan_stored_reads_the_file_and_missing_is_an_error(tmp_path, settings):
    settings.MALWARE_SCANNER_FAKE_RESULT = "infected"
    storage = FileSystemStorage(location=tmp_path)
    key = storage.save("a.bin", ContentFile(b"data"))
    assert scanning.scan_stored(storage, key) == ScanResult.INFECTED
    assert scanning.scan_stored(storage, "missing.bin") == ScanResult.ERROR


@pytest.mark.skipif(not os.environ.get("CLAMD_HOST"), reason="CLAMD_HOST not set (no real clamd)")
def test_real_clamd_detects_eicar():
    scanner = ClamdScanner(
        host=os.environ["CLAMD_HOST"], port=int(os.environ.get("CLAMD_PORT", "3310")), timeout=30
    )
    assert scanner.scan(io.BytesIO(b"harmless text")) == ScanResult.CLEAN
    assert scanner.scan(io.BytesIO(EICAR)) == ScanResult.INFECTED
