"""Generate a QR code for the published deck, in the deck's own colours.

    python tools/make_qr.py                          # the live Render address
    python tools/make_qr.py https://example.com      # any address

Writes three files into assets/:
    qr.png       high-resolution plain QR (dark green on cream)
    qr.svg       vector version, for printing
    qr-card.png  a 1080x1080 square card for Instagram / WhatsApp status

The QR itself sits on a light background with a dark foreground and a full
four-module quiet zone, so it scans on any phone camera. Error correction is
set to H (30%), the highest level, to survive a logo or a soft print.
"""

import sys
from pathlib import Path

import qrcode
import qrcode.image.svg
from PIL import Image, ImageDraw, ImageFont

URL = sys.argv[1] if len(sys.argv) > 1 else "https://nyakarilo-retreat.onrender.com/"

GREEN_900 = "#16311f"
GREEN_700 = "#2c5537"
CREAM = "#f4efe3"
TERRACOTTA = "#c4562b"

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)


def build_qr(box_size: int) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4,
    )
    qr.add_data(URL)
    qr.make(fit=True)
    return qr.make_image(fill_color=GREEN_900, back_color="#ffffff").convert("RGB")


def font(names, size):
    for name in names:
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_card(qr_img: Image.Image) -> Image.Image:
    size = 1080
    card = Image.new("RGB", (size, size), CREAM)
    d = ImageDraw.Draw(card)

    # header band
    band = 250
    d.rectangle([0, 0, size, band], fill=GREEN_900)
    d.rectangle([0, band, size, band + 8], fill=TERRACOTTA)

    serif = font(["georgiab.ttf", "timesbd.ttf", "arialbd.ttf"], 52)
    sans = font(["segoeui.ttf", "arial.ttf"], 34)
    small = font(["segoeui.ttf", "arial.ttf"], 26)

    def centred(text, f, y, fill):
        w = d.textlength(text, font=f)
        d.text(((size - w) / 2, y), text, font=f, fill=fill)

    centred("Nyakarilo Agro-Tourism", serif, 62, CREAM)
    centred("& Farmhouse Retreat", serif, 128, CREAM)
    centred("Investor Pitch Deck", sans, 198, "#d9744c")

    # white panel behind the QR
    inner = 560
    qr_img = qr_img.resize((inner, inner), Image.NEAREST)
    px, py = (size - inner) // 2, 305
    d.rounded_rectangle(
        [px - 24, py - 24, px + inner + 24, py + inner + 24], radius=24, fill="#ffffff"
    )
    card.paste(qr_img, (px, py))

    centred("Scan to open the deck", sans, py + inner + 58, GREEN_700)
    centred(URL.replace("https://", "").rstrip("/"), small, py + inner + 108, TERRACOTTA)
    return card


def main() -> int:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=24,
        border=4,
    )
    qr.add_data(URL)
    qr.make(fit=True)

    png_path = ASSETS / "qr.png"
    qr.make_image(fill_color=GREEN_900, back_color="#ffffff").save(png_path)

    svg_path = ASSETS / "qr.svg"
    qr.make_image(image_factory=qrcode.image.svg.SvgPathImage).save(svg_path)

    card_path = ASSETS / "qr-card.png"
    make_card(build_qr(10)).save(card_path)

    for p in (png_path, svg_path, card_path):
        print(f"{p.name:14} {p.stat().st_size:>9,} bytes")
    print(f"URL: {URL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
