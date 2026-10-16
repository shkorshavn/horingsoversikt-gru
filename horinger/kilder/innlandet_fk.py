"""Innlandet fylkeskommune – høringer og offentlig ettersyn.

Fristen står i fritekst i ingressen («Høringsfrist er 11. november 2026»). Står
den ikke der, hentes detaljsiden. Kilden har ingen publiseringsdato.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from horinger.datoer import finn_frist, i_dag
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

log = logging.getLogger(__name__)

INSTANS = "Innlandet fylkeskommune"


def tolk_liste(html: str, base: str) -> list[dict]:
    """Tolker høringslisten. Fristen hentes fra ingressen der den finnes."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for kort in suppe.select(".article-preview"):
        lenke = kort.select_one(".article-preview-title a[href]")
        if not lenke:
            continue
        utdrag = kort.select_one(".article-preview-excerpt")
        ingress = utdrag.get_text(" ", strip=True) if utdrag else ""
        resultat.append(
            {
                "instans": INSTANS,
                "tittel": lenke.get_text(" ", strip=True),
                "lenke": urljoin(base, lenke["href"]),
                "frist": finn_frist(ingress, i_dag()),
                "frist_tekst": _fristsetning(ingress),
                "ingress": ingress,
            }
        )
    return resultat


def _fristsetning(tekst: str) -> str:
    """Plukker ut setningen som nevner fristen, slik kilden skrev den."""
    # Del ved punktum som avslutter en setning, ikke punktum etter tall («3. desember»).
    for setning in re.split(r"(?<!\d)[.!]\s+(?=[A-ZÆØÅ])", tekst):
        if "frist" in setning.lower() or "innen" in setning.lower():
            return setning.strip().rstrip(".") + "."
    return ""


class InnlandetFylkeskommune(Kilde):
    """Høringslisten til Innlandet fylkeskommune."""

    def hent(self) -> list[Hoering]:
        """Henter listen, og detaljsiden for høringer uten frist i ingressen."""
        url = self.konfig["url"]
        resultat = []
        for felter in tolk_liste(self.nett.hent(url).text, url):
            if felter["frist"] is None:
                self._frist_fra_detaljside(felter)
            resultat.append(self.lag_hoering(**felter))
        return resultat

    def _frist_fra_detaljside(self, felter: dict) -> None:
        try:
            side = BeautifulSoup(self.nett.hent(felter["lenke"]).text, "html.parser")
        except Exception as feil:  # noqa: BLE001
            log.warning("Kunne ikke hente %s: %s", felter["lenke"], feil)
            return
        tekst = (side.find("main") or side).get_text(" ", strip=True)
        felter["frist"] = finn_frist(tekst, i_dag())
        felter["frist_tekst"] = felter["frist_tekst"] or _fristsetning(tekst)
