"""Ship the finished front page for make.fun news-image-20261122.

The entry is a single image — "THE WORLD IN ONE DAY", a newspaper front
page that sums up Sunday 22 November 2026 in 36 dated stories. The artwork
arrives beside this script as ``entry.png``. This program never draws,
downloads, or alters a pixel: it only carries the shipped bytes into the
output directory, and it refuses even that unless the file on disk is
byte-for-byte the artwork that was packed — right size, right SHA-256,
opening with the PNG signature and closing with an IEND chunk.

Standard library only, no network, no clock, no randomness: the same input
always yields the same output, byte for byte.
"""

import hashlib
import os
import sys
from pathlib import Path

# The packed artwork, measured when it was rendered: 190652 bytes, and the
# SHA-256 below, verified live with sha256sum before this file was written.
# If either number ever disagrees, the file on disk is not the artwork this
# program was written to publish.
EXPECTED_NAME = "entry.png"
EXPECTED_BYTES = 190652
EXPECTED_DIGEST = "36816702a8c3c34a6110e48a8f26318be7e12304983c893fe066183ae1ac1a74"

# A whole PNG opens with this 8-byte signature and ends with an IEND chunk.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND_MARK = b"IEND"

FALLBACK_DIR = "/output"


class Refusal(Exception):
    """The artwork on disk is not the packed one; publishing is refused."""


def digest_of(blob):
    """SHA-256 hex digest of a byte string."""
    return hashlib.sha256(blob).hexdigest()


def inspect(blob):
    """Summarise a blob as (size, digest, starts_as_png, ends_as_png)."""
    starts = blob[:8] == PNG_MAGIC
    ends = blob[-8:-4] == IEND_MARK if len(blob) >= 12 else False
    return len(blob), digest_of(blob), starts, ends


def load_packed_artwork(path):
    """Read the shipped file; return its bytes or refuse with the reason."""
    try:
        blob = path.read_bytes()
    except OSError as exc:
        raise Refusal("cannot read %s (%s)" % (path, exc))
    size, digest, starts, ends = inspect(blob)
    complaints = []
    if size != EXPECTED_BYTES:
        complaints.append("size is %d bytes, expected %d"
                          % (size, EXPECTED_BYTES))
    if digest != EXPECTED_DIGEST:
        complaints.append("sha256 %s is not the packed artwork" % digest)
    if not starts:
        complaints.append("does not start with the PNG signature")
    if not ends:
        complaints.append("does not end with an IEND chunk")
    if complaints:
        raise Refusal("%s: %s" % (path, "; ".join(complaints)))
    return blob


def choose_destination():
    """Where the entry goes: argv[1], MAKEFUN_OUTPUT_DIR, or /output."""
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", FALLBACK_DIR))


def publish():
    """Verify the shipped artwork, copy it out, then verify the copy."""
    here = Path(__file__).resolve().parent
    blob = load_packed_artwork(here / EXPECTED_NAME)

    dest_dir = choose_destination()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / EXPECTED_NAME
    dest.write_bytes(blob)

    # Re-read what was just written and compare the bytes themselves: the
    # copy must be the artwork too, not merely the same size.
    written = dest.read_bytes()
    if written != blob:
        raise Refusal("output %s differs byte-for-byte from the shipped artwork"
                      % dest)
    size, digest, starts, ends = inspect(written)
    if size != EXPECTED_BYTES or digest != EXPECTED_DIGEST:
        raise Refusal("output %s failed re-verification (size %d, sha256 %s)"
                      % (dest, size, digest))
    if not (starts and ends):
        raise Refusal("output %s is not a whole PNG" % dest)

    print("published %s (%d bytes, sha256 %s)" % (dest, size, digest))


if __name__ == "__main__":
    try:
        publish()
    except Refusal as exc:
        print("main.py: refusing to publish: %s" % exc, file=sys.stderr)
        raise SystemExit(1)
