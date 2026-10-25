"""Digdir – høringer om IT-standarder og Referansekatalogen.

Listen viser fristen ofte uten årstall («Høyringsfrist 4. november»). Da hentes detaljsiden,
som har opprettelsesdato («Laga: 12. september 2022») og status («Ferdig behandla»).
Årstallet utledes fra opprettelsesdatoen, og ferdig behandlede høringer tas ikke med.
"""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from horinger.datoer import tolk_dato, tolk_tekstdato
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

INSTANS = "Digitaliseringsdirektoratet (Digdir)"
_AR = re.compile(r"(?<!\d)(19|20)\d{2}(?!\d)")
_LAGA = re.compile(r"Laga:\s*(\d{1,2}\.\s*\w+\s+\d{4})", re.IGNORECASE)
_STATUS = re.compile(r"Status:\s*([^\n]+?)(?:\s{2,}|For denne|$)", re.IGNORECASE)


def tolk_liste(html: str, base: str) -> list[dict]:
    """Tittel, lenke og fristtekst for hver høring på listen."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for kort in suppe.select("article.teaser-card"):
        lenke = kort.find("a", href=True)
        tittel = kort.select_one(".teaser-card__title")
        frist = kort.select_one(".teaser-card__paragraph")
        if not lenke or not tittel:
            continue
        resultat.append(
            {
                "tittel": tittel.get_text(" ", strip=True),
                "lenke": urljoin(base, lenke["href"]),
                "frist_tekst": frist.get_text(" ", strip=True) if frist else "",
            }
        )
    return resultat


def har_ar(tekst: str) -> bool:
    """Om fristteksten har et årstall."""
    return bool(_AR.search(tekst or ""))


def tolk_detalj(html: str) -> tuple[date | None, str]:
    """Opprettelsesdato og status fra detaljsiden."""
    tekst = " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())
    laga = _LAGA.search(tekst)
    status = _STATUS.search(tekst)
    return (
        tolk_tekstdato(laga.group(1)) if laga else None,
        status.group(1).strip() if status else "",
    )


class Digdir(Kilde):
    """Digdirs høringsliste for standarder."""

    def hent(self) -> list[Hoering]:
        """Henter listen, og detaljsiden når fristen mangler årstall."""
        url = self.konfig["url"]
        resultat = []
        for h in tolk_liste(self.nett.hent(url).text, url):
            if har_ar(h["frist_tekst"]):
                frist = tolk_dato(h["frist_tekst"])
                if frist is None:  # f.eks. «1. kvartal 2017»: gammel og uten eksakt dato
                    continue
            else:
                laga, status = tolk_detalj(self.nett.hent(h["lenke"]).text)
                if "ferdig" in status.lower() or laga is None:
                    continue
                frist = tolk_dato(h["frist_tekst"], laga)
            resultat.append(self.lag_hoering(instans=INSTANS, frist=frist, **h))
        return resultat
