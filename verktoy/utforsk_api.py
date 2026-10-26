"""Utforsking av API-er som krever POST (sprint 7: Gjøviks postliste).

Leser en liste med forespørsler fra miljøvariabelen UTFORSK_FORESPORSLER (JSON):
    [{"navn": "init", "metode": "POST", "url": "...", "json": {...}, "headers": {...}}]
og lagrer hvert svar som <navn>.<status>.txt i mappen fra --ut. Alle kall går gjennom
horinger.nett.Nett, med samme User-Agent, pause og robots.txt-sjekk som innhentingen.
Brukes bare manuelt, fra arbeidsflyten «Utforsk fra GitHub».
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROT))

from horinger.filer import les_konfig  # noqa: E402
from horinger.nett import Nett  # noqa: E402


def main() -> int:
    """Kjører forespørslene og lagrer svarene, også feilsvar."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ut", type=Path, default=Path("raa"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    felles = les_konfig(ROT / "sources.yaml")["felles"]
    nett = Nett(felles["user_agent"], pause=float(felles["pause_sekunder"]), raa_mappe=args.ut)
    args.ut.mkdir(parents=True, exist_ok=True)
    foresporsler = json.loads(os.environ.get("UTFORSK_FORESPORSLER", "[]"))
    for f in foresporsler:
        navn = f["navn"]
        try:
            svar = nett.hent(
                f["url"],
                metode=f.get("metode", "GET"),
                json=f.get("json"),
                headers=f.get("headers"),
            )
            status = svar.status_code
            innhold = svar.content
        except Exception as feil:  # noqa: BLE001
            status = "feil"
            innhold = f"{type(feil).__name__}: {feil}".encode()
        (args.ut / f"{navn}.{status}.txt").write_bytes(innhold)
        logging.info("%s: %s (%d byte)", navn, status, len(innhold))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
