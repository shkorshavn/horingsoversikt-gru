"""Bygger nettsidens datafiler fra de lagrede kilderesultatene.

Leser data/kilder/*.json og skriver:
- data/horinger.json: åpne høringer, med «første gang sett» og merket «ny»
- data/status.json: status per kilde
- data/arkiv.json: høringer med utløpt frist
- data/historikk.json: datoen hver høring første gang ble sett

Bruk:
    python -m horinger.bygg
"""

from __future__ import annotations

import argparse
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from horinger import OSLO
from horinger.datoer import i_dag
from horinger.dedup import dedupliser
from horinger.filer import les_json, les_konfig, skriv_json
from horinger.kilder import KILDER
from horinger.lager import les_kilde
from horinger.prioritet import Prioritet

log = logging.getLogger("horinger")

ROT = Path(__file__).resolve().parent.parent
NY_DAGER = 7
UTDATERT_DAGER = 8
# Noen kilder (f.eks. Vegvesenets regelverkshøringer) lister høringer mange år tilbake.
# Høringer med frist mer enn så mange dager før historikken startet, tas ikke med i arkivet.
ARKIV_FORAN_START_DAGER = 30
# Felt i høringene som alltid følger kildens oppsett i sources.yaml.
KONFIGFELT = ("kategori", "niva")


def _dato(verdi: str | None) -> date | None:
    return date.fromisoformat(verdi[:10]) if verdi else None


def _tid(verdi: str | None) -> datetime | None:
    return datetime.fromisoformat(verdi) if verdi else None


def kildestatus(kilde_konfig: dict, lagret: dict | None, naa: datetime) -> dict:
    """Status for én kilde slik den vises på nettsiden."""
    status = {
        "kilde": kilde_konfig["navn"],
        "kjoring": kilde_konfig.get("kjoring", "github"),
    }
    if not kilde_konfig.get("aktiv") or kilde_konfig.get("modul") not in KILDER:
        return {**status, "status": "ikke overvåket", "antall": 0}
    if lagret is None:
        return {**status, "status": "ikke hentet", "antall": 0}
    status.update(
        {
            "status": lagret["status"],
            "hentet": lagret.get("hentet"),
            "sist_ok": lagret.get("sist_ok"),
            "antall": 0,
        }
    )
    if lagret.get("feil"):
        status["feil"] = lagret["feil"]
    sist_ok = _tid(lagret.get("sist_ok"))
    if lagret["status"] == "ok" and sist_ok and naa - sist_ok > timedelta(days=UTDATERT_DAGER):
        status["status"] = "utdatert"
    return status


def bygg(konfig: dict, kildemappe: Path, utdata: Path, naa: datetime | None = None) -> dict:
    """Bygger datafilene. Gir tilbake en kort oppsummering."""
    naa = (naa or datetime.now(OSLO)).replace(microsecond=0)
    i_dag_ = naa.astimezone(OSLO).date() if naa.tzinfo else i_dag()

    historikk = les_json(utdata / "historikk.json") or {
        "opprettet": i_dag_.isoformat(),
        "forst_sett": {},
    }
    opprettet = _dato(historikk["opprettet"])
    forst_sett: dict[str, str] = historikk["forst_sett"]
    arkivgrense = opprettet - timedelta(days=ARKIV_FORAN_START_DAGER)
    arkiv = {
        h["id"]: h
        for h in (les_json(utdata / "arkiv.json") or {}).get("horinger", [])
        if _dato(h["utlopt"]) >= arkivgrense
    }
    forrige_apne = (les_json(utdata / "horinger.json") or {}).get("horinger", [])

    status: list[dict] = []
    alle: dict[str, dict] = {}
    prioritet = Prioritet(konfig.get("felles", {}))
    for kilde_konfig in konfig["kilder"]:
        lagret = None
        if kilde_konfig.get("aktiv") and kilde_konfig.get("modul") in KILDER:
            lagret = les_kilde(kildemappe, kilde_konfig["navn"])
        status.append(kildestatus(kilde_konfig, lagret, naa))
        # Tema og avsender tas fra gjeldende sources.yaml, og prioriteten beregnes på nytt,
        # slik at endringer der slår inn ved neste bygging uten ny henting.
        fra_konfig = {f: kilde_konfig[f] for f in KONFIGFELT if f in kilde_konfig}
        for h in (lagret or {}).get("horinger", []):
            if h["id"] in alle:
                continue
            h = {**h, **fra_konfig}
            h["prioritet"], h["prioritet_grunn"] = prioritet.vurder(h, kilde_konfig)
            alle[h["id"]] = h
    # Samme høring fra flere kilder vises én gang (etatens versjon, med lenke til den andre).
    alle = {h["id"]: h for h in dedupliser(list(alle.values()))}

    apne: list[dict] = []
    for h in alle.values():
        frist = _dato(h.get("frist"))
        if frist is not None and frist < arkivgrense:
            continue  # gammel høring fra før oversikten startet
        forst = forst_sett.setdefault(h["id"], i_dag_.isoformat())
        forst_dato = _dato(forst)
        h = dict(h)
        h["forst_sett"] = forst
        h["ny"] = forst_dato > opprettet and (i_dag_ - forst_dato).days < NY_DAGER
        if frist is not None and frist < i_dag_:
            h["ny"] = False
            h["utlopt"] = frist.isoformat()
            arkiv[h["id"]] = h
        else:
            arkiv.pop(h["id"], None)  # fristen kan være forlenget
            apne.append(h)

    # Høringer som er fjernet fra kilden etter at fristen gikk ut, skal også til arkivet.
    for h in forrige_apne:
        frist = _dato(h.get("frist"))
        if h["id"] not in alle and frist is not None and frist < i_dag_:
            arkiv[h["id"]] = {**h, "ny": False, "utlopt": frist.isoformat()}

    apne.sort(key=lambda h: (h.get("frist") is None, h.get("frist") or "", h["tittel"]))
    antall_per_kilde: dict[str, int] = {}
    for h in apne:
        antall_per_kilde[h["kilde"]] = antall_per_kilde.get(h["kilde"], 0) + 1
    for s in status:
        if s["status"] not in ("ikke overvåket", "ikke hentet"):
            s["antall"] = antall_per_kilde.get(s["kilde"], 0)

    generert = naa.isoformat()
    skriv_json(
        utdata / "horinger.json", {"generert": generert, "antall": len(apne), "horinger": apne}
    )
    skriv_json(utdata / "status.json", {"generert": generert, "kilder": status})
    arkivliste = sorted(arkiv.values(), key=lambda h: (h["utlopt"], h["tittel"]), reverse=True)
    skriv_json(
        utdata / "arkiv.json",
        {"generert": generert, "antall": len(arkivliste), "horinger": arkivliste},
    )
    # Historikken trenger bare høringer som fortsatt finnes i en kilde eller i arkivet.
    behold = {h["id"] for h in apne} | set(arkiv)
    historikk["forst_sett"] = {k: v for k, v in sorted(forst_sett.items()) if k in behold}
    skriv_json(utdata / "historikk.json", historikk)
    oppsummering = {
        "apne": len(apne),
        "nye": sum(1 for h in apne if h["ny"]),
        "arkiv": len(arkivliste),
    }
    log.info("Bygget: %(apne)d åpne høringer, %(nye)d nye, %(arkiv)d i arkivet", oppsummering)
    return oppsummering


def main(argv: list[str] | None = None) -> int:
    """Kommandolinje for byggingen."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--konfig", type=Path, default=ROT / "sources.yaml")
    parser.add_argument("--utdata", type=Path, default=ROT / "data")
    parser.add_argument("--kildemappe", type=Path)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    bygg(les_konfig(args.konfig), args.kildemappe or args.utdata / "kilder", args.utdata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
