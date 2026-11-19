#!/usr/bin/env python3
"""news-image-20261119: write the day's front page to /output/entry.png.

The image is the entry: this program ships it beside itself and copies it out
byte for byte, so two runs write the same file. No network, no randomness.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "entry.png"
MAX_BYTES = 1024 * 1024
SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def output_dir() -> Path:
    """The grader mounts /output; MAKEFUN_OUTPUT_DIR stands in outside it."""
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def png_size(data: bytes) -> tuple[int, int]:
    """Read width and height out of the IHDR chunk, refusing anything else."""
    if not data.startswith(PNG_MAGIC) or data[12:16] != b"IHDR":
        raise ValueError("not a PNG with an IHDR chunk first")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def main() -> int:
    verify_only = "--verify" in sys.argv[1:]
    data = IMAGE.read_bytes()
    try:
        width, height = png_size(data)
    except ValueError as exc:
        print(f"{IMAGE}: {exc}", file=sys.stderr)
        return 1
    if (width, height) != (SIDE, SIDE):
        print(f"{IMAGE} is {width}x{height}, the judge takes {SIDE}x{SIDE}", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print(f"{IMAGE} is {len(data)} bytes, over the {MAX_BYTES} cap", file=sys.stderr)
        return 1
    if verify_only:
        print(f"{IMAGE} is a {width}x{height} PNG of {len(data)} bytes, ready to enter")
        return 0
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "entry.png").write_bytes(data)
    print(f"wrote {out / 'entry.png'} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
