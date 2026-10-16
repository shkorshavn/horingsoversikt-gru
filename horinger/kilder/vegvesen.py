"""Statens vegvesen – regelverkshøringer og høringer i vegprosjekter.

a) Regelverkshøringene gjelder hele landet og tas med alle.
b) Prosjekthøringene filtreres med det geografiske filteret (geografi.py). Listen
   har ikke kommunefelt, så filteret ser først på prosjektnavn, tittel og lenke,
   og henter detaljsiden bare når listen ikke gir treff.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from horinger.datoer import tolk_punktumdato
from horinger.geografi import GeografiFilter
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

log = logging.getLogger(__name__)

INSTANS = "Statens vegvesen"
_PUBLISERT = re.compile(r"Publisert:?\s*(\d{1,2}\.\d{1,2}\.\d{4})")
_MERKNADSFRIST = re.compile(r"(?:Merknadsfrist|Frist)[^:\d]*:?\s*(\d{1,2}\.\d{1,2}\.\d{4})")


def tolk_regelverk(html: str, base: str) -> list[dict]:
    """Tolker listen over regelverkshøringer."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for artikkel in suppe.select("article.article-list-item"):
        lenke = artikkel.select_one("a[href]")
        if not lenke:
            continue
        felter: dict[str, str] = {}
        for dt in artikkel.select("dl dt"):
            dd = dt.find_next_sibling("dd")
            if dd:
                felter[dt.get_text(strip=True).rstrip(":")] = dd.get_text(" ", strip=True)
        frist_tekst = felter.get("Høringsfrist", "")
        ingress = artikkel.find("p")
        referanse = felter.get("Referanse", "")
        resultat.append(
            {
                "instans": INSTANS,
                "tittel": lenke.get_text(" ", strip=True),
                "lenke": urljoin(base, lenke["href"]),
                "frist": tolk_punktumdato(frist_tekst),
                "frist_tekst": f"Høringsfrist: {frist_tekst}" if frist_tekst else "",
                "ingress": " ".join(
                    x
                    for x in [
                        ingress.get_text(" ", strip=True) if ingress else "",
                        f"Referanse: {referanse}." if referanse else "",
                    ]
                    if x
                ),
            }
        )
    return resultat


def tolk_prosjekter(html: str, base: str) -> list[dict]:
    """Tolker listen over høringer i vegprosjekter.

    Hver høring er en overskrift (prosjektnavn), et avsnitt med publiseringsdato og
    merknadsfrist, og et avsnitt med lenke til saken.
    """
    suppe = BeautifulSoup(html, "html.parser")
    beholder = suppe.select_one("main .editorial") or suppe.select_one(".editorial")
    if beholder is None:
        return []
    resultat = []
    for overskrift in beholder.find_all("h2"):
        prosjekt = overskrift.get_text(" ", strip=True)
        tekst_deler: list[str] = []
        lenke: Tag | None = None
        for soster in overskrift.find_next_siblings():
            if soster.name == "h2":
                break
            tekst_deler.append(soster.get_text(" ", strip=True))
            lenke = lenke or soster.find("a", href=True)
        tekst = " ".join(tekst_deler)
        frist = _MERKNADSFRIST.search(tekst)
        publisert = _PUBLISERT.search(tekst)
        if not lenke or not frist:
            continue
        sakstittel = lenke.get_text(" ", strip=True)
        resultat.append(
            {
                "instans": INSTANS,
                "tittel": f"{prosjekt}: {sakstittel}",
                "lenke": urljoin(base, lenke["href"]),
                "frist": tolk_punktumdato(frist.group(1)),
                "frist_tekst": f"Merknadsfrist: {frist.group(1)}",
                "publisert": tolk_punktumdato(publisert.group(1)) if publisert else None,
                "ingress": f"Vegprosjekt: {prosjekt}.",
            }
        )
    return resultat


class Vegvesen(Kilde):
    """Statens vegvesen, to lister."""

    def hent(self) -> list[Hoering]:
        """Henter regelverkshøringer og geografisk relevante prosjekthøringer."""
        url = self.konfig["url"]
        resultat = [self.lag_hoering(**f) for f in tolk_regelverk(self.nett.hent(url).text, url)]
        prosjekt_url = self.konfig.get("prosjekt_url")
        if prosjekt_url:
            filter_ = GeografiFilter(self.felles.get("geografi", {}))
            for felter in tolk_prosjekter(self.nett.hent(prosjekt_url).text, prosjekt_url):
                if self.er_relevant(felter, filter_):
                    resultat.append(self.lag_hoering(**felter))
        return resultat

    def er_relevant(self, felter: dict, filter_: GeografiFilter) -> bool:
        """Vurderer listen først, og detaljsiden bare hvis listen ikke gir treff."""
        treff = filter_.vurder(f"{felter['tittel']} {felter['lenke']}")
        if not treff.relevant:
            try:
                side = BeautifulSoup(self.nett.hent(felter["lenke"]).text, "html.parser")
                hoved = side.find("main") or side
                treff = filter_.vurder(hoved.get_text(" ", strip=True))
            except Exception as feil:  # noqa: BLE001 – en detaljside skal ikke stoppe listen
                log.warning("Kunne ikke hente %s: %s", felter["lenke"], feil)
        if treff.relevant:
            log.info("Relevant prosjekthøring (%s): %s", treff.grunn, felter["tittel"])
        return treff.relevant
