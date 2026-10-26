"""Legger innholdet i en mappe på en egen gren (overskrives hver gang).

Brukes av utforskingen på GRUs PC, der et skall-skript ikke kan brukes (Windows). Resultatet
kan da leses fra grenen, fordi vedlegg til kjøringer ikke kan lastes ned herfra.

Bruk:
    python verktoy/lagre_gren.py raa utforsk-pc
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def lagre(mappe: str, gren: str) -> int:
    """Kopierer mappen til en ny git-mappe og force-pusher den som `gren`."""
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    with tempfile.TemporaryDirectory() as tmp:
        mål = Path(tmp) / "ut"
        shutil.copytree(mappe, mål)

        def git(*a):
            subprocess.run(["git", *a], cwd=mål, check=True)

        git("init", "-q", "-b", gren)
        git("config", "user.name", "github-actions[bot]")
        git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
        git("add", "-A")
        git("commit", "-q", "-m", f"Utforsking {os.environ.get('GITHUB_RUN_ID', '')}")
        git("push", "-q", "-f", f"https://x-access-token:{token}@github.com/{repo}", gren)
    return 0


if __name__ == "__main__":
    raise SystemExit(lagre(sys.argv[1], sys.argv[2]))
