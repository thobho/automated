"""Size-based log rotation for the pirx dev units (stdlib only, no root, no logrotate).

systemd keeps the log files open (`StandardOutput=append:`), so each `*.log` is rotated with
copy + truncate: `web.log` -> `web.log.1` -> ... -> `web.log.<keep>`; older ones are dropped.
Usage: rotate_logs.py <log-dir> [max_bytes] [keep]
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_KEEP = 5


def rotate_file(path: Path, keep: int) -> None:
    oldest = path.with_name(f"{path.name}.{keep}")
    oldest.unlink(missing_ok=True)
    for i in range(keep - 1, 0, -1):
        src = path.with_name(f"{path.name}.{i}")
        if src.exists():
            src.rename(path.with_name(f"{path.name}.{i + 1}"))
    shutil.copyfile(path, path.with_name(f"{path.name}.1"))
    with path.open("r+b") as fh:
        fh.truncate(0)


def rotate_dir(
    log_dir: Path, max_bytes: int = DEFAULT_MAX_BYTES, keep: int = DEFAULT_KEEP
) -> list[Path]:
    rotated = []
    for path in sorted(log_dir.glob("*.log")):
        if path.is_file() and path.stat().st_size > max_bytes:
            rotate_file(path, keep)
            rotated.append(path)
    return rotated


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    max_bytes = int(argv[1]) if len(argv) > 1 else DEFAULT_MAX_BYTES
    keep = int(argv[2]) if len(argv) > 2 else DEFAULT_KEEP
    for path in rotate_dir(Path(argv[0]), max_bytes, keep):
        print(f"rotated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
