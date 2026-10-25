"""Henter rå kopier av kjernekildenes sider til tests/fixtures.

Brukes for å lage og fornye testdata. Kjøres i GitHub Actions, fordi
utviklingsmiljøet ikke når kildene:

    python verktoy/hent_raa.py --ut raa/
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from horinger.kjor import ROT, les_konfig  # noqa: E402
from horinger.nett import Nett  # noqa: E402

ADRESSER = [
    "https://data.stortinget.no/eksport/sesjoner?format=json",
    "https://data.stortinget.no/eksport/horinger?sesjonid=2025-2026&format=json",
    "https://data.stortinget.no/eksport/horinger?sesjonid=2026-2027&format=json",
    "https://www.regjeringen.no/no/dokument/hoyringar/id1763/?page=1",
    "https://www.regjeringen.no/no/dokument/hoyringar/id1763/?page=8",
    "https://www.vegvesen.no/fag/publikasjoner/hoeringer/",
    "https://www.vegvesen.no/vegprosjekter/hoeringer-vegprosjekter/",
    "https://innlandetfylke.no/politikk/horinger/",
    "https://www.statsforvalteren.no/innlandet/horinger/",
    # Sprint 4: direktorater og etater med prioritet 1
    "https://www.miljodirektoratet.no/hearingslistpage/gethearings?skip=0&searchTerm=&searchExpired=false",
    "https://www.miljodirektoratet.no/hearingslistpage/gethearings?skip=20&searchTerm=&searchExpired=false",
    "https://www.nve.no/om-nve/hoeringer/",
    "https://www.nve.no/om-nve/regelverk/forskriftsendringer-paa-hoering/",
    "https://www.nve.no/umbraco/api/license/getall?caseType=00&county=00&filterText=&municipality=00&pageNumber=1&pageSize=100&progress=0&size=0&stadium=20&type=0",
    "https://www.dsb.no/rss/rss-dsb---horinger/",
    "https://www.dsb.no/horinger/horinger/",
    "https://www.helsedirektoratet.no/horinger",
    "https://www.bufdir.no/om/hoeringer/",
    "https://www.digdir.no/standarder/hoyringar/1502",
    "https://www.dibk.no/regelverk/horinger/hoyringar",
    "https://www.nyeveier.no/strekninger/innlandet/oppdateringer-fra-innlandet/",
    "https://www.jernbanedirektoratet.no/wp-json/wp/v2/posts?search=h%C3%B8ring&per_page=50&_fields=date,link,title,content",
    "https://www.banenor.no/nb-no/sitemap.xml",
]


def main() -> int:
    """Henter adressene og lagrer svarene, også feilsvar."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ut", type=Path, default=Path("raa"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    felles = les_konfig(ROT / "sources.yaml")["felles"]
    nett = Nett(felles["user_agent"], pause=float(felles["pause_sekunder"]), raa_mappe=args.ut)
    egne = os.environ.get("HENT_RAA_ADRESSER", "").split()
    adresser = egne or ADRESSER
    feil = 0
    for url in adresser:
        try:
            svar = nett.hent(url)
            logging.info("OK %s %s (%d byte)", svar.status_code, url, len(svar.content))
        except Exception as e:  # noqa: BLE001
            feil += 1
            logging.error("FEIL %s: %s", url, e)
    logging.info("%d av %d adresser feilet", feil, len(adresser))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
