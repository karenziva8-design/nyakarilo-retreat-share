"""Render the Nyakarilo pitch deck to web images and a social preview card."""
import io
import pathlib
import sys

import fitz  # pymupdf
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
PDF = ROOT / "Nyakarilo Agro-Tourism & Farmhouse Retreat - Investor Pitch Deck (3).pdf"
OUT = ROOT / "nyakarilo-deck"
PAGES = OUT / "pages"
ASSETS = OUT / "assets"
PAGES.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

doc = fitz.open(PDF)
print(f"pages={doc.page_count} size={doc[0].rect.width}x{doc[0].rect.height}")

# --- full-size page images for the on-page deck viewer -------------------
zoom = 2.0  # ~144 dpi of a 72 dpi page
mat = fitz.Matrix(zoom, zoom)
for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(matrix=mat, alpha=False)
    name = PAGES / f"page-{i:02d}.png"
    pix.save(name)
    print(f"{name.name} {pix.width}x{pix.height}")

# --- 1200x630 Open Graph card from the cover slide ----------------------
cover = doc[0].get_pixmap(matrix=fitz.Matrix(3.0, 3.0), alpha=False)
cover_img = Image.open(io.BytesIO(cover.tobytes("png"))).convert("RGB")
print(f"cover {cover_img.size}")

TARGET = (1200, 630)
ratio = TARGET[0] / TARGET[1]
w, h = cover_img.size
if w / h > ratio:                      # too wide -> trim the sides
    new_w = int(h * ratio)
    left = (w - new_w) // 2
    card = cover_img.crop((left, 0, left + new_w, h))
else:                                  # too tall -> trim top/bottom
    new_h = int(w / ratio)
    top = (h - new_h) // 2
    card = cover_img.crop((0, top, w, top + new_h))
card = card.resize(TARGET, Image.LANCZOS)

# copy the deck itself next to the page so the link can serve the download
pdf_out = ASSETS / "Nyakarilo-Investor-Pitch-Deck.pdf"
pdf_out.write_bytes(PDF.read_bytes())

card.save(ASSETS / "preview.jpg", quality=86, optimize=True)
print("wrote", ASSETS / "preview.jpg")
