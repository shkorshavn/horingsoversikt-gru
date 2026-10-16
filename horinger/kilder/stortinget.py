"""Stortinget – komitéhøringer fra data.stortinget.no.

Spør både nåværende og neste sesjon, fordi høringer for neste sesjon publiseres
før sesjonen starter 1. oktober. Om en høring er åpen, avgjøres av fristen, ikke
av `horing_status`, som henger etter (kartleggingen 2.1).
"""

from __future__ import annotations

from datetime import date, datetime

from horinger.datoer import i_dag, tolk_ms_dato
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

API = "https://data.stortinget.no/eksport/horinger?sesjonid={sesjon}&format=json"
LENKE = "https://www.stortinget.no/no/Hva-skjer-pa-Stortinget/Horing/horing/?h={id}"


def sesjon_for(dato: date) -> str:
    """Sesjons-ID for en dato. Ny sesjon starter 1. oktober."""
    start = dato.year if dato.month >= 10 else dato.year - 1
    return f"{start}-{start + 1}"


def neste_sesjon(sesjon: str) -> str:
    """Sesjonen etter den gitte, f.eks. 2026-2027 → 2027-2028."""
    start = int(sesjon.split("-")[0]) + 1
    return f"{start}-{start + 1}"


def _tekst_tid(tid: datetime) -> str:
    return tid.strftime("%d.%m.%Y kl. %H:%M")


def tolk_horing(rad: dict) -> dict | None:
    """Gjør én høring fra API-et om til felter for Hoering. Avlyste høringer gir None."""
    if str(rad.get("horing_status", "")).lower() == "avlyst":
        return None
    saker = rad.get("horing_sak_info_liste") or []
    tittel = "; ".join(s.get("sak_tittel") or s.get("sak_korttittel") or "" for s in saker)
    henvisning = "; ".join(s.get("sak_henvisning") or "" for s in saker if s.get("sak_henvisning"))
    skriftlig = bool(rad.get("skriftlig"))

    if skriftlig:
        frist_tid = tolk_ms_dato(rad.get("innspillsfrist"))
        frist_tekst = f"Frist for skriftlig innspill: {_tekst_tid(frist_tid)}" if frist_tid else ""
        ingress = "Skriftlig høring."
    else:
        # Muntlige høringer: Stortingets sider viser bare fristen for å søke om å delta.
        # API-ets `innspillsfrist` vises ikke der, og brukes derfor ikke (stikkprøve
        # 16.10.2026, høring 10005957 og 10005977).
        pamelding = tolk_ms_dato(rad.get("anmodningsfrist_dato_tid"))
        hoeringsdag = tolk_ms_dato(rad.get("start_dato"))
        if pamelding:
            frist_tid = pamelding
            frist_tekst = f"Frist for å søke om å delta: {_tekst_tid(pamelding)}"
        else:
            frist_tid = hoeringsdag
            frist_tekst = (
                f"Ingen frist oppgitt. Høringen holdes {hoeringsdag:%d.%m.%Y}"
                if hoeringsdag
                else ""
            )
        ingress = "Muntlig høring" + (f" {hoeringsdag:%d.%m.%Y}." if hoeringsdag else ".")
    if henvisning:
        ingress += f" {henvisning}."

    komite = (rad.get("komite") or {}).get("navn", "")
    return {
        "instans": f"Stortinget, {komite}" if komite else "Stortinget",
        "tittel": tittel or f"Høring {rad.get('id')}",
        "lenke": LENKE.format(id=rad["id"]),
        "frist": frist_tid.date() if frist_tid else None,
        "frist_tekst": frist_tekst,
        "ingress": ingress,
    }


class Stortinget(Kilde):
    """Komitéhøringer fra Stortingets åpne data."""

    def sesjoner(self, dato: date | None = None) -> list[str]:
        """Nåværende og neste sesjon."""
        naa = sesjon_for(dato or i_dag())
        return [naa, neste_sesjon(naa)]

    def hent(self) -> list[Hoering]:
        """Henter høringer for nåværende og neste sesjon."""
        resultat: list[Hoering] = []
        for sesjon in self.sesjoner():
            data = self.nett.hent(API.format(sesjon=sesjon)).json()
            resultat.extend(self.tolk(data))
        return resultat

    def tolk(self, data: dict) -> list[Hoering]:
        """Tolker ett API-svar."""
        resultat = []
        for rad in data.get("horinger_liste") or []:
            felter = tolk_horing(rad)
            if felter:
                resultat.append(self.lag_hoering(**felter))
        return resultat
