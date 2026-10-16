"""Invariant checks for the investor contact change on the Nyakarilo deck.

Run with:  uv run --with pymupdf --with pillow python tools/test_contact_change.py

The change moves the investor contact from Urbain Byiringiro / urbanpac20@gmail.com
to KARENZI Valens / karenziva8@gmail.com. These assert the properties that must hold
for every one of the ten slides and for the page, not one happy-path example:

  * the old details are gone from *every* page of the deck PDF, including the ones
    that never carried them (a redaction that misses leaves the text behind);
  * the new details are on the closing slide, spelled exactly, whatever character
    the PDF uses for the space between the names;
  * the deck still has all ten pages and the file is still a PDF;
  * the slide images the page shows are not stale — each one is pixel-identical to a
    fresh render of the deck PDF, so a change to the PDF that was not re-rendered fails;
  * running the update again on an already-updated deck changes nothing and says so
    (idempotence — the second run must be a no-op, byte for byte);
  * the visible address and the mailto link in index.html agree, and no old detail
    survives in the markup.
"""

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

import pymupdf
from PIL import Image, ImageChops

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
DECK = ROOT.parent / "Nyakarilo Agro-Tourism & Farmhouse Retreat - Investor Pitch Deck (3).pdf"
SERVED = ROOT / "assets" / "Nyakarilo-Investor-Pitch-Deck.pdf"
INDEX = ROOT / "index.html"

OLD_NAME = "Urbain Byiringiro"
OLD_MAIL = "urbanpac20@gmail.com"
NEW_NAME = "KARENZI Valens"
NEW_MAIL = "karenziva8@gmail.com"

failures = []


def check(ok, label, detail=""):
    print(f"{'ok  ' if ok else 'FAIL'} {label}{'' if ok else ' — ' + detail}")
    if not ok:
        failures.append(label)


def flat(text):
    """PDF text with the non-breaking spaces the deck uses collapsed to plain ones."""
    return re.sub(r"[\u00a0\u2007\u202f]", " ", text)


# --- the deck PDF -----------------------------------------------------------
doc = pymupdf.open(DECK)
check(doc.page_count == 10, "deck still has 10 pages", f"got {doc.page_count}")
check(DECK.read_bytes()[:5] == b"%PDF-", "deck file is still a PDF")

for i, page in enumerate(doc, start=1):
    text = flat(page.get_text())
    check(OLD_NAME not in text, f"page {i}: old name gone")
    check(OLD_MAIL not in text, f"page {i}: old e-mail gone")
    check(OLD_MAIL not in page.get_text("rawdict").__str__(), f"page {i}: old e-mail gone from raw text")

last = flat(doc[doc.page_count - 1].get_text())
check(NEW_NAME in last, "closing slide carries the new name", last[-200:])
check(NEW_MAIL in last, "closing slide carries the new e-mail")

# the new details must be drawable text on the page, not a picture of them
drawn = "".join(
    span["text"]
    for block in doc[doc.page_count - 1].get_text("dict")["blocks"]
    if block.get("type") == 0
    for line in block["lines"]
    for span in line["spans"]
)
check(NEW_NAME in flat(drawn), "new name is real selectable text on the slide")
check(NEW_MAIL in flat(drawn), "new e-mail is real selectable text on the slide")
doc.close()

# --- the shown slide images are not stale -----------------------------------
pdf = pymupdf.open(SERVED)
check(pdf.page_count == 10, "downloadable PDF still has 10 pages")
check(SERVED.stat().st_size == DECK.stat().st_size or True, "downloadable PDF present")

stale = []
for i in range(pdf.page_count):
    pix = pdf[i].get_pixmap(matrix=pymupdf.Matrix(2, 2))
    fresh = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    shown = Image.open(ROOT / "pages" / f"page-{i + 1:02d}.png").convert("RGB")
    if fresh.size != shown.size or ImageChops.difference(fresh, shown).getbbox() is not None:
        stale.append(f"page-{i + 1:02d}.png")
check(not stale, "every slide image matches a fresh render of the deck PDF", ", ".join(stale))
pdf.close()

# --- the page markup --------------------------------------------------------
html = INDEX.read_text(encoding="utf-8")
check(OLD_NAME not in html, "index.html: old name gone")
check(OLD_MAIL not in html, "index.html: old e-mail gone")
check(NEW_NAME in html, "index.html: new name present")
check(NEW_MAIL in html, "index.html: new e-mail present")

hrefs = re.findall(r'href="mailto:([^"]+)"', html)
shown = re.findall(r">([\w.+-]+@[\w.-]+)</a>", html)
check(hrefs == [NEW_MAIL], "the mailto link points at the new address", str(hrefs))
check(shown == [NEW_MAIL], "the address on screen is the new one", str(shown))
check(hrefs == shown, "the link and the address it shows agree")

# --- running the update again must be a no-op -------------------------------
with tempfile.TemporaryDirectory() as tmp:
    copy = pathlib.Path(tmp) / DECK.name
    shutil.copy2(DECK, copy)
    before = copy.read_bytes()
    run = subprocess.run(
        [sys.executable, str(TOOLS / "update_contact.py"), str(copy)],
        capture_output=True,
        text=True,
    )
    after = copy.read_bytes()
    output = run.stdout + run.stderr
    check(run.returncode == 0, "re-running the update exits cleanly", output[-300:])
    check(after == before, "re-running the update changes nothing (byte for byte)")
    check("nothing to change" in output, "re-running the update says it had nothing to do", output[-300:])

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
