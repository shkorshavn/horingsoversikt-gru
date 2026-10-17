"""Starter arbeidsflyten «Publiser» etter en innhenting.

En push gjort med GITHUB_TOKEN starter ikke andre arbeidsflyter. Derfor startes publiseringen
eksplisitt med GitHubs REST-API. Krever miljøvariablene GITHUB_TOKEN og GITHUB_REPOSITORY,
og at arbeidsflyten har `actions: write`.

Bruk:
    python verktoy/start_publisering.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

ARBEIDSFLYT = "publiser.yml"
GREN = "main"


def start() -> int:
    """Sender workflow_dispatch for publiseringen."""
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GITHUB_TOKEN og GITHUB_REPOSITORY må være satt.", file=sys.stderr)
        return 1
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    foresporsel = urllib.request.Request(
        f"{api}/repos/{repo}/actions/workflows/{ARBEIDSFLYT}/dispatches",
        data=json.dumps({"ref": GREN}).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(foresporsel, timeout=30) as svar:
        print(f"Publisering startet (HTTP {svar.status}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(start())
