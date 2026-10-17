"""Avgjør om en planlagt kjøring skal gå videre.

GitHub bruker UTC og kjenner ikke sommertid. Arbeidsflytene startes derfor både kl. 08.00 og
09.00 UTC, og denne sjekken slipper bare gjennom kjøringen som tilsvarer kl. 10.00 norsk tid:
08.00 UTC om sommeren (UTC+2) og 09.00 UTC om vinteren (UTC+1). Sjekken bruker hvilken
tidsplan som startet kjøringen, ikke klokka, slik at forsinkede kjøringer også fungerer.

For regjeringen.no hoppes ekstraforsøkene tirsdag–fredag over hvis kilden er hentet de siste
seks dagene.

Bruk (i GitHub Actions):
    python -m horinger.tidsjekk --hendelse schedule --cron "0 8 * * 1"
    python -m horinger.tidsjekk ... --kilde-fil data/kilder/regjeringen-no.json --krev-fersk
Skriver «kjor=true» eller «kjor=false» til $GITHUB_OUTPUT.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from horinger import OSLO

NORSK_TIME = 10
FERSK_DAGER = 6


def skal_kjore(
    hendelse: str,
    cron: str,
    naa: datetime,
    sist_ok: datetime | None = None,
    krev_fersk: bool = False,
) -> tuple[bool, str]:
    """Gir (kjør?, grunn)."""
    if hendelse != "schedule":
        return True, f"startet manuelt ({hendelse})"
    deler = cron.split()
    if len(deler) < 2 or not deler[1].isdigit():
        return False, f"ukjent tidsplan «{cron}»"
    utc_time = int(deler[1])
    forskyvning = naa.astimezone(OSLO).utcoffset() / timedelta(hours=1)
    if utc_time + forskyvning != NORSK_TIME:
        return False, (
            f"tidsplanen {utc_time:02d}.00 UTC er kl. {utc_time + forskyvning:02.0f} norsk tid, "
            f"ikke {NORSK_TIME}"
        )
    lokal = naa.astimezone(OSLO)
    if krev_fersk and lokal.weekday() != 0 and sist_ok is not None:
        alder = naa - sist_ok
        if alder < timedelta(days=FERSK_DAGER):
            return False, f"kilden ble hentet for {alder.days} dager siden"
    return True, "planlagt kjøring kl. 10 norsk tid"


def main(argv: list[str] | None = None) -> int:
    """Kommandolinje. Skriver resultatet til $GITHUB_OUTPUT hvis den finnes."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hendelse", required=True)
    parser.add_argument("--cron", default="")
    parser.add_argument("--kilde-fil", type=Path)
    parser.add_argument("--krev-fersk", action="store_true")
    args = parser.parse_args(argv)

    sist_ok = None
    if args.kilde_fil and args.kilde_fil.is_file():
        verdi = json.loads(args.kilde_fil.read_text(encoding="utf-8")).get("sist_ok")
        sist_ok = datetime.fromisoformat(verdi) if verdi else None
    kjor, grunn = skal_kjore(args.hendelse, args.cron, datetime.now(UTC), sist_ok, args.krev_fersk)
    print(f"{'Kjører' if kjor else 'Hopper over'}: {grunn}")
    utfil = os.environ.get("GITHUB_OUTPUT")
    if utfil:
        with open(utfil, "a", encoding="utf-8") as fil:
            fil.write(f"kjor={'true' if kjor else 'false'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
