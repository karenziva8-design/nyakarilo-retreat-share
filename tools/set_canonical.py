"""Point the deck's link-preview tags at the real address once it is online.

Social networks (WhatsApp, Facebook, LinkedIn, X) will not follow a relative
image path, so the Open Graph tags need the full address of the published page.
The page ships with the token __CANONICAL__ in those tags; this script swaps it
for the real address.

    python tools/set_canonical.py https://example.onrender.com
    python tools/set_canonical.py --reset          # put the token back

Running it twice, or with a different address, always ends up correct.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGETS = [ROOT / "index.html"]
TOKEN = "__CANONICAL__"

# the tags that must carry a full address, and the attribute holding it
TAG_RE = re.compile(
    r'((?:rel="canonical"'
    r'|property="og:(?:url|image|image:secure_url)"'
    r'|name="twitter:image")'
    r'[^>]*?(?:href|content)=")([^"]*)(")'
)

# whatever base an earlier run left behind — the token, a real address, or a
# stack of both from an older version of this script
BASE_RE = re.compile(r"^(?:__CANONICAL__|https?://[^/]+/?)+")


def rewrite(base: str) -> None:
    base = base.rstrip("/") + "/"
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")

        def sub(m: re.Match[str], base: str = base) -> str:
            rest = BASE_RE.sub("", m.group(2))
            return m.group(1) + (base + rest if rest else base.rstrip("/")) + m.group(3)

        new = TAG_RE.sub(sub, text)
        path.write_text(new, encoding="utf-8")
        print(f"{path.name}: {'updated' if new != text else 'already correct'}")


def reset() -> None:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")

        def sub(m: re.Match[str]) -> str:
            return m.group(1) + TOKEN + BASE_RE.sub("", m.group(2)) + m.group(3)

        path.write_text(TAG_RE.sub(sub, text), encoding="utf-8")
        print(f"{path.name}: reset to the {TOKEN} token")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    if sys.argv[1] == "--reset":
        reset()
        return 0
    if not re.match(r"^https?://", sys.argv[1]):
        print("give a full address, e.g. https://nyakarilo.onrender.com")
        return 2
    rewrite(sys.argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
