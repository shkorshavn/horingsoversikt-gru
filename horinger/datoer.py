"""Felles tolkning av datoer i formatene kildene bruker.

Se kildekartleggingen, avsnitt 10, for hvilke kilder som bruker hvilke formater.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta

from horinger import OSLO

MANEDER = {
    "januar": 1,
    "februar": 2,
    "mars": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "desember": 12,
}

_MANED_MONSTER = "|".join(MANEDER)

# 15.10.2026 eller 1.2.2026
_PUNKTUM = re.compile(r"(?<!\d)(\d{1,2})\.(\d{1,2})\.(\d{4})(?!\d)")
# 15. oktober 2026, 15.oktober 2026, 15. oktober (uten år)
_TEKST = re.compile(
    rf"(?<!\d)(\d{{1,2}})\.\s*({_MANED_MONSTER})(?:\s+(\d{{4}}))?",
    re.IGNORECASE,
)
# /Date(1760997540000+0200)/
_MS = re.compile(r"/Date\((-?\d+)([+-]\d{4})?\)/")
# Ord som innleder en frist i fritekst
_FRIST_ORD = re.compile(
    r"(høringsfrist|høyringsfrist|frist|innen|merknadsfrist|innspill)", re.IGNORECASE
)


def _lag_dato(dag: int, maned: int, ar: int) -> date | None:
    try:
        return date(ar, maned, dag)
    except ValueError:
        return None


def neste_forekomst(dag: int, maned: int, referanse: date) -> date | None:
    """Gir første dato med gitt dag og måned som er lik eller senere enn referansen."""
    kandidat = _lag_dato(dag, maned, referanse.year)
    if kandidat is None:
        return None
    if kandidat < referanse:
        kandidat = _lag_dato(dag, maned, referanse.year + 1)
    return kandidat


def tolk_punktumdato(tekst: str) -> date | None:
    """Tolker første dato på formen dd.mm.åååå i teksten."""
    treff = _PUNKTUM.search(tekst or "")
    if not treff:
        return None
    dag, maned, ar = (int(x) for x in treff.groups())
    return _lag_dato(dag, maned, ar)


def tolk_tekstdato(tekst: str, referanse: date | None = None) -> date | None:
    """Tolker første norske tekstdato («15. oktober 2026»).

    Mangler året, brukes neste forekomst etter referansedatoen. Uten referanse
    og uten år returneres None.
    """
    treff = _TEKST.search(tekst or "")
    if not treff:
        return None
    dag = int(treff.group(1))
    maned = MANEDER[treff.group(2).lower()]
    if treff.group(3):
        return _lag_dato(dag, maned, int(treff.group(3)))
    if referanse is None:
        return None
    return neste_forekomst(dag, maned, referanse)


def tolk_dato(tekst: str, referanse: date | None = None) -> date | None:
    """Tolker en dato i punktum- eller tekstformat, det som kommer først i teksten."""
    tekst = tekst or ""
    p = _PUNKTUM.search(tekst)
    t = _TEKST.search(tekst)
    if p and (not t or p.start() <= t.start()):
        return tolk_punktumdato(tekst[p.start() :])
    if t:
        return tolk_tekstdato(tekst[t.start() :], referanse)
    return None


def finn_frist(tekst: str, referanse: date | None = None) -> date | None:
    """Finner fristen i fritekst.

    Leter først etter en dato etter et fristord («Høringsfrist er 11. november
    2026», «innen 3. juli 2026»). Finnes ingen slik, brukes første dato i teksten.
    """
    tekst = " ".join((tekst or "").split())
    for ord_treff in _FRIST_ORD.finditer(tekst):
        rest = tekst[ord_treff.end() : ord_treff.end() + 80]
        dato = tolk_dato(rest, referanse)
        if dato:
            return dato
    return tolk_dato(tekst, referanse)


def tolk_ms_dato(verdi: str | None) -> datetime | None:
    """Tolker Stortingets /Date(ms+0200)/ til tid i norsk tidssone.

    Tomme verdier fra API-et (år 1) gir None.
    """
    treff = _MS.search(verdi or "")
    if not treff:
        return None
    ms = int(treff.group(1))
    tidspunkt = datetime(1970, 1, 1, tzinfo=UTC) + timedelta(milliseconds=ms)
    if tidspunkt.year < 1900:
        return None
    return tidspunkt.astimezone(OSLO)


def tolk_iso(verdi: str | None) -> datetime | None:
    """Tolker ISO 8601. Tid uten tidssone regnes som norsk tid."""
    if not verdi:
        return None
    try:
        tidspunkt = datetime.fromisoformat(verdi.replace("Z", "+00:00"))
    except ValueError:
        return None
    if tidspunkt.year < 1900:
        return None
    if tidspunkt.tzinfo is None:
        tidspunkt = tidspunkt.replace(tzinfo=OSLO)
    return tidspunkt.astimezone(OSLO)


def i_dag() -> date:
    """Dagens dato i norsk tid."""
    return datetime.now(OSLO).date()
