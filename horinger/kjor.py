"""Kjører alle aktive kilder og skriver data/horinger.json og data/status.json.

Bruk:
    python -m horinger.kjor                       # alle aktive kilder
    python -m horinger.kjor --kilder Stortinget   # bare utvalgte kilder
    python -m horinger.kjor --raa raa/            # lagrer også rå svar fra kildene
"""

from __future__ import annotations

import argparse
import json
import logging
import time
import traceback
from datetime import datetime
from pathlib import Path

import yaml

from horinger import OSLO
from horinger.datoer import i_dag
from horinger.kilder import KILDER
from horinger.modell import Hoering
from horinger.nett import Nett

log = logging.getLogger("horinger")

ROT = Path(__file__).resolve().parent.parent


def les_konfig(sti: Path) -> dict:
    """Leser sources.yaml."""
    with open(sti, encoding="utf-8") as fil:
        return yaml.safe_load(fil)


def kjor_kilder(
    konfig: dict, nett: Nett, utvalg: list[str] | None = None
) -> tuple[list[Hoering], list[dict]]:
    """Kjører kildene og samler høringer og status. Én feil stopper ikke resten."""
    felles = konfig.get("felles", {})
    alle: list[Hoering] = []
    status: list[dict] = []
    for kilde_konfig in konfig["kilder"]:
        navn = kilde_konfig["navn"]
        if utvalg and navn not in utvalg:
            continue
        modul = kilde_konfig.get("modul")
        if not kilde_konfig.get("aktiv") or modul not in KILDER:
            status.append({"kilde": navn, "status": "ikke overvåket", "antall": 0})
            continue
        start = time.monotonic()
        try:
            kilde = KILDER[modul](kilde_konfig, nett, felles)
            funnet = kilde.hent()
            alle.extend(funnet)
            status.append(
                {
                    "kilde": navn,
                    "status": "ok",
                    "antall": len(funnet),
                    "sekunder": round(time.monotonic() - start, 1),
                }
            )
            log.info("%s: %d høringer", navn, len(funnet))
        except Exception as feil:  # noqa: BLE001 – én kilde skal aldri stoppe resten
            log.error("%s feilet: %s", navn, feil)
            log.debug(traceback.format_exc())
            status.append(
                {
                    "kilde": navn,
                    "status": "feil",
                    "antall": 0,
                    "feil": f"{type(feil).__name__}: {feil}",
                    "sekunder": round(time.monotonic() - start, 1),
                }
            )
    return alle, status


def rydd(horinger: list[Hoering]) -> list[Hoering]:
    """Fjerner utløpte høringer og duplikater, og sorterer på frist."""
    i_dag_ = i_dag()
    unike: dict[str, Hoering] = {}
    for h in horinger:
        if h.frist is not None and h.frist < i_dag_:
            continue
        unike.setdefault(h.id, h)
    return sorted(unike.values(), key=lambda h: (h.frist is None, h.frist or i_dag_, h.tittel))


def skriv(horinger: list[Hoering], status: list[dict], mappe: Path, antall_kall: int) -> None:
    """Skriver horinger.json og status.json i UTF-8."""
    mappe.mkdir(parents=True, exist_ok=True)
    generert = datetime.now(OSLO).replace(microsecond=0).isoformat()
    (mappe / "horinger.json").write_text(
        json.dumps(
            {
                "generert": generert,
                "antall": len(horinger),
                "horinger": [h.til_dict() for h in horinger],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (mappe / "status.json").write_text(
        json.dumps(
            {"generert": generert, "antall_kall": antall_kall, "kilder": status},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    """Kommandolinje for innhentingen."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--konfig", type=Path, default=ROT / "sources.yaml")
    parser.add_argument("--utdata", type=Path, default=ROT / "data")
    parser.add_argument("--kilder", nargs="*", help="Kjør bare disse kildene (navn)")
    parser.add_argument("--raa", type=Path, help="Mappe for rå svar fra kildene")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    konfig = les_konfig(args.konfig)
    felles = konfig.get("felles", {})
    nett = Nett(
        user_agent=felles["user_agent"],
        pause=float(felles.get("pause_sekunder", 1.0)),
        tidsavbrudd=float(felles.get("tidsavbrudd_sekunder", 30)),
        raa_mappe=args.raa,
    )
    horinger, status = kjor_kilder(konfig, nett, args.kilder)
    horinger = rydd(horinger)
    skriv(horinger, status, args.utdata, nett.antall_kall)
    log.info("Ferdig: %d åpne høringer, %d kall", len(horinger), nett.antall_kall)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
