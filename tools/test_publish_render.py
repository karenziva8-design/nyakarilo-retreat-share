"""Invariant checks for tools/publish_render.py.

Run with:  python tools/test_publish_render.py

These assert the properties that must hold for *every* valid input, not one
example: the git remote is normalised to a bare HTTPS repo URL no matter which
form it is written in, and the script refuses to do anything at all when the
API key is absent.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish_render as pr  # noqa: E402

CASES = [
    ("git@github.com:karenziva/nyakarilo.git", "https://github.com/karenziva/nyakarilo"),
    ("git@github.com:karenziva/nyakarilo", "https://github.com/karenziva/nyakarilo"),
    ("https://github.com/karenziva/nyakarilo.git", "https://github.com/karenziva/nyakarilo"),
    ("https://github.com/karenziva/nyakarilo", "https://github.com/karenziva/nyakarilo"),
]

failures = []

for remote, want in CASES:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True)
        subprocess.run(["git", "-C", tmp, "remote", "add", "origin", remote], check=True)
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            got = pr.repo_url()
        finally:
            os.chdir(cwd)
    ok = got == want == want
    print(f"{'ok ' if ok else 'FAIL'} {remote!r} -> {got!r}")
    if not ok:
        failures.append((remote, got, want))

# Property: an absent key must abort before any network call is attempted.
saved = os.environ.pop("RENDER_API_KEY", None)
try:
    try:
        pr.main()
        failures.append(("no API key", "returned normally", "sys.exit"))
        print("FAIL missing key did not abort")
    except SystemExit as exc:
        ok = "RENDER_API_KEY" in str(exc)
        print(f"{'ok ' if ok else 'FAIL'} missing key aborts: {exc}")
        if not ok:
            failures.append(("no API key", str(exc), "message naming the variable"))
finally:
    if saved is not None:
        os.environ["RENDER_API_KEY"] = saved

print(f"\n{len(CASES) + 1} checks, {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
