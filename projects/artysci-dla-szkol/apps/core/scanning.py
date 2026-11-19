"""Malware scanning of uploaded files behind one interface (US-2.3A, D91: provider-neutral).

    scan(file) -> ScanResult.CLEAN | ScanResult.INFECTED | ScanResult.ERROR

The backend comes from `MALWARE_SCANNER`:

- ``clamd``: ClamAV's daemon over its INSTREAM protocol (stdlib sockets only). TCP with
  `CLAMD_HOST`/`CLAMD_PORT`, or a Unix socket with `CLAMD_SOCKET`. No address = ERROR, so
  nothing ever counts as scanned by accident (fail closed). Prod accepts only this backend.
- ``none``: no scanner (dev, pirx: D87). Every file passes and a warning line
  ``upload_unscanned`` marks it as not scanned.
- ``fake``: tests. Answers `MALWARE_SCANNER_FAKE_RESULT` (default ``clean``).

`scan()` never raises for scanner trouble: an unreachable or confused scanner is ERROR, and the
caller decides (retry, then leave the file pending).
"""

import enum
import logging
import socket
import struct
from typing import BinaryIO

from django.conf import settings

logger = logging.getLogger("apps.core.scanning")

CHUNK_SIZE = 64 * 1024
MAX_REPLY = 4096


class ScanResult(enum.StrEnum):
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"


BACKENDS = ("clamd", "none", "fake")


class ClamdScanner:
    """ClamAV daemon client. INSTREAM: ``zINSTREAM\\0``, then chunks prefixed with their
    length (4 bytes, big endian), then a zero-length chunk; the reply ends with ``\\0``:
    ``stream: OK``, ``stream: <name> FOUND`` or ``... ERROR``."""

    def __init__(self, *, host="", port=3310, socket_path="", timeout=30.0):
        self.host = host
        self.port = port
        self.socket_path = socket_path
        self.timeout = timeout

    def _connect(self) -> socket.socket:
        if self.socket_path:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect(self.socket_path)
            return sock
        return socket.create_connection((self.host, self.port), timeout=self.timeout)

    def scan(self, file: BinaryIO) -> ScanResult:
        if not (self.socket_path or self.host):
            logger.error("clamd address missing", extra={"event": "scan_misconfigured"})
            return ScanResult.ERROR
        try:
            with self._connect() as sock:
                sock.sendall(b"zINSTREAM\0")
                file.seek(0)
                while chunk := file.read(CHUNK_SIZE):
                    sock.sendall(struct.pack(">I", len(chunk)) + chunk)
                sock.sendall(struct.pack(">I", 0))
                reply = self._read_reply(sock)
        except OSError as exc:
            logger.warning(
                "clamd unreachable (%s)", type(exc).__name__, extra={"event": "scan_error"}
            )
            return ScanResult.ERROR
        return self._parse(reply)

    @staticmethod
    def _read_reply(sock: socket.socket) -> bytes:
        data = b""
        while b"\0" not in data and len(data) < MAX_REPLY:
            part = sock.recv(1024)
            if not part:
                break
            data += part
        return data.split(b"\0", 1)[0].strip()

    @staticmethod
    def _parse(reply: bytes) -> ScanResult:
        text = reply.decode("utf-8", "replace")
        if text.endswith(" OK"):
            return ScanResult.CLEAN
        if text.endswith(" FOUND"):
            # The signature name is safe to log (no user data); it helps the admin.
            signature = text.removeprefix("stream:").removesuffix("FOUND").strip()[:100]
            logger.warning("malware found: %s", signature, extra={"event": "scan_infected"})
            return ScanResult.INFECTED
        logger.warning("clamd error reply: %s", text[:100], extra={"event": "scan_error"})
        return ScanResult.ERROR


class NoScanner:
    """MALWARE_SCANNER=none: nothing is scanned; each file is logged as unscanned."""

    def scan(self, file: BinaryIO) -> ScanResult:
        logger.warning(
            "upload not scanned (MALWARE_SCANNER=none)", extra={"event": "upload_unscanned"}
        )
        return ScanResult.CLEAN


class FakeScanner:
    """Tests: the result comes from the setting `MALWARE_SCANNER_FAKE_RESULT`."""

    def scan(self, file: BinaryIO) -> ScanResult:
        return ScanResult(getattr(settings, "MALWARE_SCANNER_FAKE_RESULT", ScanResult.CLEAN))


def get_scanner():
    name = settings.MALWARE_SCANNER
    if name == "clamd":
        return ClamdScanner(
            host=settings.CLAMD_HOST,
            port=settings.CLAMD_PORT,
            socket_path=settings.CLAMD_SOCKET,
            timeout=settings.CLAMD_TIMEOUT,
        )
    if name == "none":
        return NoScanner()
    if name == "fake":
        return FakeScanner()
    raise ValueError(f"Unknown MALWARE_SCANNER {name!r}")


def scan(file: BinaryIO) -> ScanResult:
    """Scan `file` (read from the start) with the configured backend."""
    return get_scanner().scan(file)


def scan_stored(storage, key: str) -> ScanResult:
    """Scan a file already in `storage`. A file that cannot be read is ERROR."""
    try:
        with storage.open(key, "rb") as file:
            return scan(file)
    except OSError:
        logger.warning("stored file unreadable", extra={"event": "scan_error"})
        return ScanResult.ERROR
