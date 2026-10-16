"""Statsforvalteren i Innlandet – høringer.

Fristen står uten årstall («16. oktober kl. 23:59»). Året utledes fra adressen,
som inneholder publiseringsår og -måned (/horinger/2026/10/…): fristen er første
forekomst av datoen etter den første dagen i publiseringsmåneden.
"""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from horinger.datoer import i_dag, tolk_dato
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

INSTANS = "Statsforvalteren i Innlandet"
_AR_MANED = re.compile(r"/horinger/(\d{4})/(\d{1,2})/")


def referansedato(lenke: str) -> date:
    """Første dag i publiseringsmåneden fra adressen, ellers dagens dato."""
    treff = _AR_MANED.search(lenke)
    if treff:
        return date(int(treff.group(1)), int(treff.group(2)), 1)
    return i_dag()


def tolk_liste(html: str, base: str) -> list[dict]:
    """Tolker høringskortene på listesiden."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for kort in suppe.select("a.ds-card[href]"):
        if "/horinger/" not in kort["href"]:
            continue
        tittel = kort.select_one(".ds-card-title")
        innhold = kort.select_one(".ds-card-content")
        frist_tekst = ""
        for blokk in kort.find_all("div"):
            etikett = blokk.find("span", class_="ds-font-weight-bold")
            if etikett and "frist" in etikett.get_text().lower():
                frist_tekst = blokk.get_text(" ", strip=True)
                break
        lenke = urljoin(base, kort["href"])
        resultat.append(
            {
                "instans": INSTANS,
                "tittel": tittel.get_text(" ", strip=True) if tittel else "",
                "lenke": lenke,
                "frist": tolk_dato(frist_tekst, referansedato(lenke)),
                "frist_tekst": frist_tekst,
                "ingress": innhold.get_text(" ", strip=True) if innhold else "",
            }
        )
    return resultat


class Statsforvalteren(Kilde):
    """Høringslisten til Statsforvalteren i Innlandet."""

    def hent(self) -> list[Hoering]:
        """Henter listesiden."""
        url = self.konfig["url"]
        return [self.lag_hoering(**f) for f in tolk_liste(self.nett.hent(url).text, url)]
