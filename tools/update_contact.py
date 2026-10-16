"""Replace the investor contact details on the deck's final slide.

The last slide of the deck carries the "direct investment inquiries" block. This
script rewrites the name and the e-mail address there in place, keeping the
original typeface, size and colour, and removing the old text from the page
rather than covering it up.

    uv run --with pymupdf python tools/update_contact.py [pdf] [--out pdf]

Defaults to the source deck at the top of the project, edited in place.
"""
import argparse
import os
import pathlib
import sys
import tempfile

import fitz  # pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_PDF = ROOT / "Nyakarilo Agro-Tourism & Farmhouse Retreat - Investor Pitch Deck (3).pdf"

OLD_NAME = "Urbain Byiringiro"
NEW_NAME = "KARENZI Valens"
OLD_MAIL = "urbanpac20@gmail.com"
NEW_MAIL = "karenziva8@gmail.com"


def find_span(page, needle, want_bold=None):
    """Return the span on the page whose text contains `needle`."""
    for block in page.get_text("rawdict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = "".join(c["c"] for c in span["chars"])
                if needle in text and (want_bold is None or ("Bold" in span["font"]) == want_bold):
                    return span, text
    return None, None


def contact_font(doc, page, name_part):
    """A usable Lato-Bold: the copy kept in tools/fonts, else the embedded one.

    The font embedded in the deck is subsetted to the characters the slides
    already use, so it cannot render new text — it comes second.
    """
    local = pathlib.Path(__file__).resolve().parent / "fonts" / "Lato-Bold.ttf"
    if local.exists():
        print(f"font {local.name}: {local.stat().st_size} bytes")
        return local
    return embedded_font(doc, page, name_part)


def embedded_font(doc, page, name_part):
    """Write an embedded font whose base name contains `name_part` to a temp file."""
    for entry in page.get_fonts(full=True):
        xref, basefont = entry[0], entry[3]
        if name_part.lower() in basefont.lower():
            base, fext, ftype_, buf = doc.extract_font(xref)
            if buf:
                tmp = pathlib.Path(tempfile.gettempdir()) / f"deck_{name_part}.{fext or 'ttf'}"
                tmp.write_bytes(buf)
                print(f"font {basefont}: {len(buf)} bytes -> {tmp}")
                return tmp
    return None


def card_background(page, spot, measured):
    """Sample the slide render at `spot` (page points) to get the card colour."""
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    x, y = int(round(spot[0] * 2)), int(round(spot[1] * 2))
    r, g, b = pix.pixel(x, y)[:3]
    print(f"card background at {measured}: #{r:02x}{g:02x}{b:02x}")
    return (r / 255, g / 255, b / 255)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?", default=str(DEFAULT_PDF))
    ap.add_argument("--out", default=None, help="write here instead of editing in place")
    args = ap.parse_args()

    path = pathlib.Path(args.pdf)
    doc = fitz.open(path)
    page = doc[doc.page_count - 1]

    name_span, name_text = find_span(page, OLD_NAME)
    mail_span, mail_text = find_span(page, OLD_MAIL)
    if not name_span and not mail_span:
        print("nothing to change: the last page already carries this name and e-mail")
        return 0

    fontfile = contact_font(doc, page, "Lato-Bold")

    # the cream card behind the block, sampled where no text sits
    bg = card_background(page, (660, 305), "empty area of the contact card")

    jobs = []
    if name_span:
        origin = name_span["chars"][0]["origin"]
        x0, y0, x1, y1 = name_span["bbox"]
        jobs.append((fitz.Rect(x0 - 1, y0 - 3, x1 + 2, y1 + 3), origin,
                     NEW_NAME, name_span["size"], name_span["color"]))
        print(f"name {name_text!r} -> {NEW_NAME!r} at {origin}")
    if mail_span:
        origin = mail_span["chars"][0]["origin"]
        x0, y0, x1, y1 = mail_span["bbox"]
        jobs.append((fitz.Rect(x0 - 1, y0 - 2, x1 + 1, y1 + 2), origin,
                     NEW_MAIL, mail_span["size"], mail_span["color"]))
        print(f"e-mail {mail_text!r} -> {NEW_MAIL!r} at {origin}")

    for rect, _origin, _text, _size, _color in jobs:
        annot = page.add_redact_annot(rect)
        annot.set_colors(stroke=bg, fill=bg)
        annot.update()
    page.apply_redactions()

    for _rect, origin, text, size, color in jobs:
        page.insert_text(
            origin,
            text,
            fontsize=size,
            fontname="LatoBoldReplacement" if fontfile else "helv",
            fontfile=str(fontfile) if fontfile else None,
            color=((color >> 16 & 255) / 255, (color >> 8 & 255) / 255, (color & 255) / 255),
        )

    # compress rather than append: an incremental save keeps the old text and the
    # whole replacement font in the file, which nearly doubles its size.
    out = pathlib.Path(args.out) if args.out else path
    tmp = out.with_suffix(".tmp-save.pdf")
    doc.save(tmp, garbage=4, deflate=True)
    os.replace(tmp, out)
    print("wrote", out)
    print("page 10 now says:", [t for t in page.get_text().splitlines() if "KARENZI" in t or "karenziva" in t])
    return 0


if __name__ == "__main__":
    sys.exit(main())
