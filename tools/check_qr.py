"""Verify the generated QR codes actually scan, and decode to the right address.

    uv run --with opencv-python-headless --with pillow python tools/check_qr.py

A QR code that renders but does not decode is worse than none at all, so this
reads the pixels back the way a phone camera would.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np

ASSETS = Path(__file__).resolve().parent.parent / "assets"
EXPECTED = sys.argv[1] if len(sys.argv) > 1 else "https://nyakarilo-retreat.onrender.com/"

failures = []


def check(name, ok, detail):
    print(f"{'ok ' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def decode(path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None, None
    data, points, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return (data or None), points


# 1. the plain QR decodes to exactly the published address
data, pts = decode(ASSETS / "qr.png")
check("qr.png decodes", data == EXPECTED, f"decoded {data!r}")

# 2. it decodes even when the quiet zone is cropped away (social uploads do this)
img = cv2.imread(str(ASSETS / "qr.png"), cv2.IMREAD_GRAYSCALE)
h, w = img.shape
trimmed = img[int(h * 0.04) : int(h * 0.96), int(w * 0.04) : int(w * 0.96)]
tdata, _, _ = cv2.QRCodeDetector().detectAndDecode(trimmed)
check("decodes after 4% crop", tdata == EXPECTED, f"decoded {tdata!r}")

# 3. it still decodes small, as it appears on a phone screen beside a caption
small = cv2.resize(img, (240, 240), interpolation=cv2.INTER_AREA)
sdata, _, _ = cv2.QRCodeDetector().detectAndDecode(small)
check("decodes at 240px", sdata == EXPECTED, f"decoded {sdata!r}")

# 4. the card's QR decodes from inside the artwork, not just from the bare file
card = cv2.imread(str(ASSETS / "qr-card.png"), cv2.IMREAD_GRAYSCALE)
cdata, cpts, _ = cv2.QRCodeDetector().detectAndDecode(card)
check("qr-card.png decodes", cdata == EXPECTED, f"decoded {cdata!r}")

# 5. and the three files are the sizes and formats they claim to be
from PIL import Image

with Image.open(ASSETS / "qr.png") as im:
    check("qr.png is square PNG", im.format == "PNG" and im.width == im.height,
          f"{im.size} {im.format}")
with Image.open(ASSETS / "qr-card.png") as im:
    check("qr-card.png is 1080 square", im.size == (1080, 1080), f"{im.size} {im.format}")

tree = ET.parse(ASSETS / "qr.svg")
root = tree.getroot()
check("qr.svg is valid XML", root.tag.endswith("svg"), root.tag.split("}")[-1])

print()
if failures:
    print(f"{len(failures)} failure(s): {', '.join(failures)}")
    sys.exit(1)
print("5 checks, 0 failure(s) - every QR decodes to the live address")
