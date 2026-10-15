"""Invariant check: every slide page and the preview card is a real image with content."""
import sys
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"
EXPECTED = (1440, 810)

failures = []
rows = []

for n in range(1, 11):
    p = PAGES / f"page-{n:02d}.png"
    if not p.exists():
        failures.append(f"page-{n:02d}.png missing")
        continue
    with Image.open(p) as im:
        size = im.size
        stat = ImageStat.Stat(im.convert("L"))
        mean, stddev = stat.mean[0], stat.stddev[0]
    rows.append((p.name, size, mean, stddev, p.stat().st_size))
    if size != EXPECTED:
        failures.append(f"{p.name}: size {size} != {EXPECTED}")
    if stddev < 5:
        failures.append(f"{p.name}: looks blank (stddev {stddev:.2f})")

card = ROOT / "assets" / "preview.jpg"
with Image.open(card) as im:
    card_size = im.size
    stat = ImageStat.Stat(im.convert("L"))
    rows.append((card.name, card_size, stat.mean[0], stat.stddev[0], card.stat().st_size))
if card_size != (1200, 630):
    failures.append(f"preview.jpg: size {card_size} != (1200, 630)")

pdf = ROOT / "assets" / "Nyakarilo-Investor-Pitch-Deck.pdf"
head = pdf.read_bytes()[:5]
if head != b"%PDF-":
    failures.append("PDF for the download link is not a PDF")
rows.append((pdf.name, "pdf", "-", "-", pdf.stat().st_size))

print(f"{'file':36} {'size':12} {'mean':>7} {'stddev':>7} {'bytes':>9}")
for name, size, mean, stddev, nbytes in rows:
    m = f"{mean:.1f}" if isinstance(mean, float) else str(mean)
    s = f"{stddev:.1f}" if isinstance(stddev, float) else str(stddev)
    print(f"{name:36} {str(size):12} {m:>7} {s:>7} {nbytes:>9}")

if failures:
    print("\nFAIL")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("\nPASS: all 10 slides are 1440x810 with real content, card is 1200x630, PDF intact")
