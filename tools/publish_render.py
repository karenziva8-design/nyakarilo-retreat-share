"""Publish this folder to Render as a static site.

Run it with:  python tools/publish_render.py

It expects:
  * a git remote 'origin' already pointing at the public GitHub repo, and
    the branch already pushed (the site is built from the repo),
  * RENDER_API_KEY in the environment (never passed on the command line).

It creates the static site if it does not exist, then triggers a deploy and
prints the public URL. Re-running it re-deploys the existing site instead of
creating a second one.
"""

import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.render.com/v1"
SERVICE_NAME = "nyakarilo-retreat"
BRANCH = "main"


def call(method, path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        API + path,
        data=body,
        method=method,
        headers={
            "Authorization": "Bearer " + os.environ["RENDER_API_KEY"],
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        sys.exit(f"Render API {method} {path} failed: {exc.code} {exc.read().decode()}")


def repo_url():
    import subprocess

    out = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if out.startswith("git@github.com:"):
        out = "https://github.com/" + out[len("git@github.com:") :]
    if out.endswith(".git"):
        out = out[:-4]
    return out


def find_existing():
    for entry in call("GET", "/services?limit=100"):
        svc = entry.get("service", {})
        if svc.get("name") == SERVICE_NAME:
            return svc
    return None


def main():
    if not os.environ.get("RENDER_API_KEY"):
        sys.exit("RENDER_API_KEY is not set in this shell.")

    owner_id = call("GET", "/owners?limit=1")[0]["owner"]["id"]
    url = repo_url()

    svc = find_existing()
    if svc is None:
        svc = call(
            "POST",
            "/services",
            {
                "type": "static_site",
                "name": SERVICE_NAME,
                "ownerId": owner_id,
                "repo": url,
                "branch": BRANCH,
                "autoDeploy": "yes",
                "serviceDetails": {
                    "publishPath": ".",
                    "pullRequestPreviewsEnabled": "no",
                },
            },
        )["service"]
        print("created service", svc["id"])
    else:
        print("service already exists", svc["id"])

    deploy = call("POST", f"/services/{svc['id']}/deploys", {})
    print("deploy", deploy.get("id"), deploy.get("status"))
    print("URL:", svc["serviceDetails"].get("url") or svc.get("serviceDetails"))


if __name__ == "__main__":
    main()
