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

## Editing the words

Open `index.html` and change the text directly — the headline, the facts, the
budget table. Nothing needs rebuilding for text.

If the PDF changes, replace `assets/Nyakarilo-Investor-Pitch-Deck.pdf` and re-run:

```
uv run --with pymupdf --with pillow python tools/build_assets.py
```

That rewrites `pages/*.png` and `assets/preview.jpg` from the new PDF.

## After publishing

Social networks need the full address of where the page lives, so once it is
online run:

```
python tools/set_canonical.py https://your-address-here
```

Then paste the link into each network's own preview checker (Facebook Sharing
Debugger, LinkedIn Post Inspector) to force it to pick up the new card.
