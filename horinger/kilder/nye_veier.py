"""Nye Veier – oppdateringer fra Innlandet.

Siden er en nyhetsstrøm, ikke en høringsliste. Oppslag fra de siste 120 dagene som
inneholder et søkeord (sources.yaml, `sokeord`), åpnes. Siden gjelder bare Innlandet, så
det brukes ikke noe geografisk filter i tillegg. De tas bare med når detaljsiden har en frist
(«innen 3. juli 2026», «Frist for merknader er …»). Slik faller nyheter om grunnundersøkelser
og befaringer bort, selv om de nevner reguleringsplanen.
"""

from __future__ import annotations

from datetime import timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from horinger.datoer import frist_etter_ord, fristtekst, i_dag, setning_med_frist, tolk_punktumdato
from horinger.kilder.base import Kilde
from horinger.modell import Hoering
from horinger.sokeord import Sokeord

INSTANS = "Nye Veier"
NY_DAGER = timedelta(days=120)


def tolk_liste(html: str, base: str) -> list[dict]:
    """Alle oppslag: tittel, lenke, dato, prosjekt og ingress."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for kort in suppe.select("article.uk-news-card"):
        lenke = kort.select_one("h1 a[href]") or kort.find("a", href=True)
        if not lenke or lenke["href"].strip() in ("", "#"):
            continue
        dato = kort.select_one("span.uk-text-semibold")
        prosjekt = kort.select_one(".uk-label")
        ingress = kort.find("p")
        resultat.append(
            {
                "tittel": lenke.get_text(" ", strip=True),
                "lenke": urljoin(base, lenke["href"]),
                "publisert": tolk_punktumdato(dato.get_text() if dato else ""),
                "prosjekt": prosjekt.get_text(" ", strip=True) if prosjekt else "",
                "ingress": ingress.get_text(" ", strip=True) if ingress else "",
            }
        )
    return resultat


def tolk_detalj(html: str, publisert) -> tuple:
    """Frist og fristsetning fra detaljsiden."""
    suppe = BeautifulSoup(html, "html.parser")
    hoved = suppe.find("main") or suppe
    tekst = hoved.get_text(" ", strip=True)
    return frist_etter_ord(tekst, publisert), setning_med_frist(tekst)


class NyeVeier(Kilde):
    """Høringer og varsler fra Nye Veiers oppdateringer i Innlandet."""

    def hent(self) -> list[Hoering]:
        """Henter listen og detaljsidene til nye oppslag med søkeord."""
        url = self.konfig["url"]
        sokeord = Sokeord(self.konfig.get("sokeord", []), self.konfig.get("utelat_ord", []))
        grense = i_dag() - NY_DAGER
        resultat = []
        for h in tolk_liste(self.nett.hent(url).text, url):
            tekst = f"{h['tittel']} {h['prosjekt']} {h['ingress']}"
            if not h["publisert"] or h["publisert"] < grense or not sokeord.treff(tekst):
                continue
            frist, setning = tolk_detalj(self.nett.hent(h["lenke"]).text, h["publisert"])
            if frist is None:
                continue
            resultat.append(
                self.lag_hoering(
                    instans=f"{INSTANS}, {h['prosjekt']}" if h["prosjekt"] else INSTANS,
                    tittel=h["tittel"],
                    lenke=h["lenke"],
                    frist=frist,
                    frist_tekst=fristtekst(frist, setning),
                    publisert=h["publisert"],
                    ingress=h["ingress"],
                )
            )
        return resultat
