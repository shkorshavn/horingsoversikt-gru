"""Henter høringer fra kildene og lagrer resultatet per kilde i data/kilder/.

Bygger også nettsidens datafiler (se bygg.py), med mindre --bare-kilder er satt.

Bruk:
    python -m horinger.kjor                          # alle aktive kilder
    python -m horinger.kjor --maskin github          # kildene som hentes på GitHub
    python -m horinger.kjor --maskin pc --bare-kilder  # regjeringen.no på Sveins PC
    python -m horinger.kjor --kilder Stortinget      # bare utvalgte kilder
    python -m horinger.kjor --raa raa/               # lagrer også rå svar fra kildene

Miljøvariabelen HORINGER_SIMULER_FEIL=<kildenavn> gjør én kilde utilgjengelig i kjøringen.
Den brukes bare til å teste feilhåndteringen.
"""

from __future__ import annotations

import argparse
import logging
import os
import time
import traceback
from datetime import datetime
from pathlib import Path

from horinger import OSLO
from horinger.bygg import bygg
from horinger.filer import les_konfig
from horinger.kilder import KILDER
from horinger.lager import lagre_kilde
from horinger.nett import Nett

__all__ = ["les_konfig", "kjor_kilder", "hent_kilde", "velg_kilder", "main"]

log = logging.getLogger("horinger")

ROT = Path(__file__).resolve().parent.parent


class SimulertFeil(Exception):
    """Brukes når HORINGER_SIMULER_FEIL er satt for en kilde."""


def velg_kilder(
    konfig: dict, utvalg: list[str] | None = None, maskin: str | None = None
) -> list[dict]:
    """Aktive kilder med modul, filtrert på navn og på hvilken maskin de hentes fra."""
    valgt = []
    for k in konfig["kilder"]:
        if not k.get("aktiv") or k.get("modul") not in KILDER:
            continue
        if utvalg and k["navn"] not in utvalg:
            continue
        if maskin and maskin != "alle" and k.get("kjoring", "github") != maskin:
            continue
        valgt.append(k)
    return valgt


def hent_kilde(
    kilde_konfig: dict, nett: Nett, felles: dict, simuler_feil: str | None = None
) -> dict:
    """Henter én kilde. Feil fanges og returneres som status, slik at resten kan fortsette."""
    navn = kilde_konfig["navn"]
    start = time.monotonic()
    hentet = datetime.now(OSLO).replace(microsecond=0).isoformat()
    try:
        if simuler_feil and simuler_feil == navn:
            raise SimulertFeil(f"Simulert feil for {navn} (HORINGER_SIMULER_FEIL)")
        funnet = KILDER[kilde_konfig["modul"]](kilde_konfig, nett, felles).hent()
        log.info("%s: %d høringer", navn, len(funnet))
        return {
            "kilde": navn,
            "status": "ok",
            "hentet": hentet,
            "antall": len(funnet),
            "sekunder": round(time.monotonic() - start, 1),
            "horinger": [h.til_dict() for h in funnet],
        }
    except Exception as feil:  # noqa: BLE001 – én kilde skal aldri stoppe resten
        log.error("%s feilet: %s", navn, feil)
        log.debug(traceback.format_exc())
        return {
            "kilde": navn,
            "status": "feil",
            "hentet": hentet,
            "antall": 0,
            "feil": f"{type(feil).__name__}: {feil}",
            "sekunder": round(time.monotonic() - start, 1),
            "horinger": [],
        }


def kjor_kilder(
    konfig: dict,
    nett: Nett,
    utvalg: list[str] | None = None,
    maskin: str | None = None,
    simuler_feil: str | None = None,
) -> list[dict]:
    """Henter de valgte kildene etter tur."""
    felles = konfig.get("felles", {})
    return [hent_kilde(k, nett, felles, simuler_feil) for k in velg_kilder(konfig, utvalg, maskin)]


def main(argv: list[str] | None = None) -> int:
    """Kommandolinje for innhentingen."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--konfig", type=Path, default=ROT / "sources.yaml")
    parser.add_argument("--utdata", type=Path, default=ROT / "data")
    parser.add_argument("--kildemappe", type=Path, help="Standard: <utdata>/kilder")
    parser.add_argument("--kilder", nargs="*", help="Kjør bare disse kildene (navn)")
    parser.add_argument(
        "--maskin",
        choices=["alle", "github", "pc"],
        default="alle",
        help="Kjør bare kildene som hentes fra denne maskinen (feltet `kjoring`)",
    )
    parser.add_argument(
        "--bare-kilder", action="store_true", help="Lagre kilderesultatene uten å bygge"
    )
    parser.add_argument("--raa", type=Path, help="Mappe for rå svar fra kildene")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    konfig = les_konfig(args.konfig)
    felles = konfig.get("felles", {})
    kildemappe = args.kildemappe or args.utdata / "kilder"
    nett = Nett(
        user_agent=felles["user_agent"],
        pause=float(felles.get("pause_sekunder", 1.0)),
        tidsavbrudd=float(felles.get("tidsavbrudd_sekunder", 30)),
        raa_mappe=args.raa,
    )
    simuler = os.environ.get("HORINGER_SIMULER_FEIL", "").strip() or None
    start = time.monotonic()
    resultater = kjor_kilder(konfig, nett, args.kilder, args.maskin, simuler)
    total = time.monotonic() - start
    for r in resultater:
        lagre_kilde(kildemappe, r)
    feil = [r["kilde"] for r in resultater if r["status"] != "ok"]
    log.info(
        "Hentet %d kilder (%d med feil: %s), %d kall, %.0f sekunder",
        len(resultater),
        len(feil),
        ", ".join(feil) or "ingen",
        nett.antall_kall,
        total,
    )
    if not args.bare_kilder:
        bygg(konfig, kildemappe, args.utdata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
