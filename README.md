# Nyakarilo — Investor Pitch Deck, shareable web page

A single-page version of the pitch deck, made to be sent as one link and to show a
picture-and-text preview card when it is pasted into WhatsApp, Facebook, LinkedIn,
X or email.

## What is in here

| Path | What it is |
| --- | --- |
| `index.html` | The page. Headline, the key facts, the 10 slides, the budget table, the share buttons. |
| `styles.css` | All styling. |
| `app.js` | Copy-link button, the big slide viewer, and filling in the share links. |
| `pages/page-01.png … page-10.png` | The 10 slides, rendered from the PDF as images so they show on any phone. |
| `assets/preview.jpg` | The 1200×630 card that social media show as the preview. |
| `assets/Nyakarilo-Investor-Pitch-Deck.pdf` | The original PDF, offered as a download. |
| `tools/build_assets.py` | Re-renders the slide images and the preview card from the PDF. |
| `tools/set_canonical.py` | Points the preview tags at the live address after publishing. |
| `tools/update_contact.py` | Rewrites the investor name and e-mail on the deck's last slide, then re-render the images. |

## Editing the words

Open `index.html` and change the text directly — the headline, the facts, the
budget table. Nothing needs rebuilding for text.

If the PDF changes, replace `assets/Nyakarilo-Investor-Pitch-Deck.pdf` and re-run:

```
uv run --with pymupdf --with pillow python tools/build_assets.py
```

That rewrites `pages/*.png` and `assets/preview.jpg` from the new PDF.

## Changing the investor contact

The last slide of the deck and the footer of the page both name the person investors
should contact. The footer is plain text in `index.html`. The slide is inside the PDF,
so change both with:

```
uv run --with pymupdf python tools/update_contact.py
uv run --with pymupdf --with pillow python tools/build_assets.py
```

The first command edits the name and e-mail on the final slide in place, keeping the
typeface, size and colour; it does nothing if they are already up to date. `tools/fonts/Lato-Bold.ttf`
is the copy of the deck's typeface used for the new text — the font inside the PDF is
subsetted and cannot draw characters the slides did not already use.

## After publishing

Social networks need the full address of where the page lives, so once it is
online run:

```
python tools/set_canonical.py https://your-address-here
```

Then paste the link into each network's own preview checker (Facebook Sharing
Debugger, LinkedIn Post Inspector) to force it to pick up the new card.
