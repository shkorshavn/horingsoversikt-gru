"""Committer og pusher endrede filer i en mappe, med nye forsøk ved samtidige endringer.

Brukes av arbeidsflytene, både på GitHub og på GRUs PC (Windows), derfor i Python og ikke
i et skall-skript.

Bruk:
    python verktoy/git_lagre.py data/kilder "Data: Regjeringen.no hentet"
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

FORSOK = 4
GREN = "main"


def git(*args: str, sjekk: bool = True) -> subprocess.CompletedProcess:
    """Kjører en git-kommando og skriver kommandoen til loggen.

    `safe.directory` gjelder bare denne kommandoen. På GRUs PC kjører runneren som tjenesten
    NETWORK SERVICE, mens arbeidsmappen ble laget av en annen bruker. Da avviser git mappen
    («dubious ownership») etter at checkout-steget er ferdig. Ingen innstillinger på PC-en endres.
    """
    print("+ git", " ".join(args), flush=True)
    mappe = os.getcwd()
    return subprocess.run(["git", "-c", f"safe.directory={mappe}", *args], check=sjekk, text=True)


def lagre(mappe: str, melding: str) -> int:
    """Committer endringer i `mappe` og pusher til grenen som er sjekket ut."""
    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    git("add", "--all", "--", mappe)
    if git("diff", "--cached", "--quiet", sjekk=False).returncode == 0:
        print("Ingen endringer å lagre.")
        return 0
    git("commit", "-m", melding)
    for forsok in range(1, FORSOK + 1):
        if git("push", "origin", f"HEAD:{GREN}", sjekk=False).returncode == 0:
            return 0
        print(f"Push feilet (forsøk {forsok} av {FORSOK}). Henter siste endringer og prøver igjen.")
        git("pull", "--rebase", "origin", GREN, sjekk=False)
        time.sleep(5 * forsok)
    print("Klarte ikke å pushe.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(lagre(sys.argv[1], sys.argv[2]))
