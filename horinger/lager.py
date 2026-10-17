"""Resultatet fra hver kilde lagres i en egen fil: data/kilder/<kilde>.json.

Slik kan kildene hentes på ulike maskiner (regjeringen.no på Sveins PC, resten på GitHub)
uten at kjøringene skriver over hverandres resultater. Feiler en kilde, beholdes høringene fra
forrige vellykkede henting, og tidspunktet for den står i `sist_ok`.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from horinger.filer import les_json, skriv_json

_ERSTATT = {"æ": "ae", "ø": "o", "å": "a"}


def filnavn(kildenavn: str) -> str:
    """Filnavn for en kilde, f.eks. «Regjeringen.no» → «regjeringen-no.json»."""
    navn = "".join(_ERSTATT.get(t, t) for t in kildenavn.lower())
    navn = unicodedata.normalize("NFKD", navn).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", navn).strip("-") + ".json"


def les_kilde(mappe: Path, kildenavn: str) -> dict | None:
    """Leser lagret resultat for en kilde, hvis det finnes."""
    return les_json(mappe / filnavn(kildenavn))


def lagre_kilde(mappe: Path, resultat: dict) -> dict:
    """Lagrer resultatet for én kilde og gir tilbake det som ble lagret.

    Ved feil beholdes høringene og `sist_ok` fra forrige lagrede resultat.
    """
    resultat = dict(resultat)
    forrige = les_kilde(mappe, resultat["kilde"])
    if resultat["status"] == "ok":
        resultat["sist_ok"] = resultat["hentet"]
    else:
        resultat["horinger"] = (forrige or {}).get("horinger", [])
        resultat["sist_ok"] = (forrige or {}).get("sist_ok")
    skriv_json(mappe / filnavn(resultat["kilde"]), resultat)
    return resultat
