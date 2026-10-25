"""NVE – to delkilder.

a) Forskriftsendringer på høring (HTML). Listen viser publiseringsdato, ikke frist, og
   avsluttede høringer er merket «(avsluttet)». For de som ikke er avsluttet, og som er
   publisert det siste året, hentes fristen fra detaljsiden.
b) Konsesjonssaker på høring (JSON-endepunktet siden selv bruker, `stadium=20`). Filtreres
   med samme geografi som Vegvesenets prosjekthøringer (Svein 25.10.2026).

robots.txt krever 20 sekunder mellom kall. Det håndteres av Nett.
"""

from __future__ import annotations

from datetime import date, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from horinger.datoer import (
    frist_etter_ord,
    fristtekst,
    i_dag,
    setning_med_frist,
    tolk_iso,
    tolk_punktumdato,
)
from horinger.geografi import GeografiFilter
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

INSTANS = "NVE"
BASE = "https://www.nve.no/"
FORSKRIFTER = BASE + "om-nve/regelverk/forskriftsendringer-paa-hoering/"
KONSESJONER = (
    BASE + "umbraco/api/license/getall?caseType=00&county=00&filterText=&municipality=00"
    "&pageNumber=1&pageSize=100&progress=0&size=0&stadium=20&type=0"
)
KONSESJON_LENKE = BASE + "konsesjon/konsesjonssaker/konsesjonssak?id={id}&type={type}"
MAKS_ALDER = timedelta(days=365)
# Uten frist på detaljsiden tas høringen bare med de første 90 dagene etter publisering.
UTEN_FRIST_DAGER = timedelta(days=90)


def tolk_forskriftsliste(html: str) -> list[dict]:
    """Gir høringene på listen som ikke er merket avsluttet, med publiseringsdato."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for lenke in suppe.select(".n-pagelist li > a[href]"):
        tittel = lenke.find("h3")
        meta = lenke.select_one(".n-pagelist-item-content-meta")
        tekst = tittel.get_text(" ", strip=True) if tittel else ""
        if not tekst or "(avsluttet)" in tekst.lower():
            continue
        resultat.append(
            {
                "tittel": tekst,
                "lenke": urljoin(BASE, lenke["href"]),
                "publisert": tolk_punktumdato(meta.get_text() if meta else ""),
            }
        )
    return resultat


def tolk_forskriftsdetalj(html: str, publisert: date | None) -> tuple[date | None, str, str]:
    """Finner fristen, setningen den står i og ingressen på en detaljside.

    Fristen kan være vag («innen høringsfristen desember 2026»). Da blir fristen None, og
    setningen vises som tekst.
    """
    suppe = BeautifulSoup(html, "html.parser")
    hoved = suppe.find("main") or suppe
    tekst = hoved.get_text(" ", strip=True)
    frist = frist_etter_ord(tekst, publisert)
    ingress = ""
    for avsnitt in hoved.find_all("p"):
        kandidat = avsnitt.get_text(" ", strip=True)
        if len(kandidat) > 60:
            ingress = kandidat[:400]
            break
    return frist, setning_med_frist(tekst), ingress


def tolk_konsesjoner(data: dict, geografi: GeografiFilter) -> list[dict]:
    """Konsesjonssaker på høring i kommunene geografien omfatter."""
    resultat = []
    for sak in data.get("Licenses") or []:
        kommune = (sak.get("Kommune") or "").strip()
        tittel = (sak.get("Tittel") or "").strip()
        if not geografi.vurder(f"{kommune} {tittel}").relevant:
            continue
        frist = tolk_iso(sak.get("Hoeringsfrist"))
        tiltakshaver = (sak.get("Tiltakshaver") or "").strip()
        ingress = ", ".join(x for x in (f"{kommune} kommune" if kommune else "", tiltakshaver) if x)
        resultat.append(
            {
                "instans": f"{INSTANS} (konsesjonssak)",
                "tittel": tittel,
                "lenke": KONSESJON_LENKE.format(id=sak.get("SoknadId"), type=sak.get("Type")),
                "frist": frist.date() if frist else None,
                "frist_tekst": f"Høringsfrist: {sak['HoeringsfristText']}"
                if sak.get("HoeringsfristText")
                else "",
                "publisert": (d.date() if (d := tolk_iso(sak.get("Dato"))) else None),
                "ingress": f"Konsesjonssøknad i {ingress}." if ingress else "",
            }
        )
    return resultat


class Nve(Kilde):
    """NVEs forskriftsendringer og konsesjonssaker på høring."""

    def hent(self) -> list[Hoering]:
        """Henter begge delkildene."""
        felt = self._forskrifter()
        geografi = GeografiFilter(self.felles.get("geografi", {}))
        felt += tolk_konsesjoner(self.nett.hent(KONSESJONER).json(), geografi)
        return [self.lag_hoering(**f) for f in felt]

    def _forskrifter(self) -> list[dict]:
        grense = i_dag() - MAKS_ALDER
        felt = []
        for h in tolk_forskriftsliste(self.nett.hent(FORSKRIFTER).text):
            if h["publisert"] and h["publisert"] < grense:
                continue
            frist, setning, ingress = tolk_forskriftsdetalj(
                self.nett.hent(h["lenke"]).text, h["publisert"]
            )
            if frist is None and (
                not h["publisert"] or h["publisert"] < i_dag() - UTEN_FRIST_DAGER
            ):
                continue
            felt.append(
                {
                    **h,
                    "instans": INSTANS,
                    "frist": frist,
                    "frist_tekst": fristtekst(frist, setning),
                    "ingress": ingress,
                }
            )
        return felt
