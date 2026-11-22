"""Publish the shipped front page for make.fun news-image-20261122.

The entry is one image: "THE WORLD IN ONE DAY", a newspaper front page
summing up Sunday 22 November 2026 in 36 verified stories. The artwork
ships beside this script as ``entry.png``; this program does not draw,
download, or change anything. It only carries the shipped bytes to the
output directory, and it refuses to do even that unless the file in front
of it is byte-for-byte the artwork we packed: right size, right SHA-256,
a PNG that opens with the PNG signature and closes with an IEND chunk.

Pure standard library, no network, no clock, no randomness: the same
input always produces the same output, byte for byte.
"""

import hashlib
import os
import sys
from pathlib import Path

# --- The shipped artwork, measured when it was packed ----------------------
# entry.png: 178222 bytes; SHA-256 verified live with sha256sum
# before this file was written. If either number ever disagrees, the artwork
# on disk is not the artwork this program was written to publish.
ARTWORK_NAME = "entry.png"
ARTWORK_SIZE = 178222
ARTWORK_SHA256 = "9bfe8067595a3be65b940354a4d33fa54855fe2609652d7102b54d593701f598"

# A whole PNG opens with this 8-byte signature and ends with an IEND chunk.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_IEND = b"IEND"

DEFAULT_OUTPUT_DIR = "/output"


def fail(message):
    """Abort with a clear error on stderr and a non-zero exit code."""
    print("main.py: refusing to publish: " + message, file=sys.stderr)
    raise SystemExit(1)


def measure(path):
    """Read a file and return (size, sha256, opens_as_png, closes_as_png)."""
    try:
        data = path.read_bytes()
    except OSError as exc:
        fail("cannot read %s (%s)" % (path, exc))
    digest = hashlib.sha256(data).hexdigest()
    opens_ok = data[: len(PNG_SIGNATURE)] == PNG_SIGNATURE
    closes_ok = data[-8:-4] == PNG_IEND if len(data) >= 12 else False
    return len(data), digest, opens_ok, closes_ok, data


def insist_artwork(path):
    """Return the artwork bytes, or abort if anything about them is off."""
    size, digest, opens_ok, closes_ok, data = measure(path)
    problems = []
    if size != ARTWORK_SIZE:
        problems.append("size is %d bytes, expected %d" % (size, ARTWORK_SIZE))
    if digest != ARTWORK_SHA256:
        problems.append("sha256 %s does not match the packed artwork" % digest)
    if not opens_ok:
        problems.append("does not open with the PNG signature")
    if not closes_ok:
        problems.append("does not close with an IEND chunk")
    if problems:
        fail("%s: %s" % (path, "; ".join(problems)))
    return data


def output_dir():
    """Where the entry goes: argv[1], MAKEFUN_OUTPUT_DIR, or /output."""
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))


def main():
    here = Path(__file__).resolve().parent
    source = here / ARTWORK_NAME
    data = insist_artwork(source)

    target_dir = output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / ARTWORK_NAME
    target.write_bytes(data)

    # Re-measure what we just wrote, and compare the bytes directly:
    # the copy must be the artwork too, not merely the same size.
    size, digest, opens_ok, closes_ok, copied = measure(target)
    if copied != data:
        fail("output %s differs byte-for-byte from the shipped artwork"
             % target)
    if size != ARTWORK_SIZE or digest != ARTWORK_SHA256:
        fail("output %s failed re-verification (size %d, sha256 %s)"
             % (target, size, digest))
    if not (opens_ok and closes_ok):
        fail("output %s is not a whole PNG" % target)

    print("published %s (%d bytes, sha256 %s)" % (target, size, digest))


if __name__ == "__main__":
    main()
