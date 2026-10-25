"""DSB – høringer og samtykkehøringer.

RSS-strømmen viser alle høringer (også «Høringer – samtykker» om anlegg for farlig stoff),
med publiseringsdato. Fristen står bare på detaljsiden («Høringsfrist 27.11.2026»), så
detaljsiden hentes for oppslag fra de siste 120 dagene. Samtykkehøringene gjelder enkeltanlegg
i hele landet og tas bare med når de treffer geografien (som Vegvesenets prosjekthøringer).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

from horinger import OSLO
from horinger.datoer import frist_etter_ord, i_dag, setning_med_frist
from horinger.geografi import GeografiFilter
from horinger.kilder.base import NYHET_MAKS_ALDER, Kilde
from horinger.modell import Hoering

INSTANS = "Direktoratet for samfunnssikkerhet og beredskap (DSB)"


def tolk_rss(xml: str) -> list[dict]:
    """Tittel, lenke, publiseringsdato og om det er en samtykkehøring."""
    rot = ET.fromstring(xml.lstrip("﻿").encode("utf-8"))
    resultat = []
    for item in rot.iter("item"):
        lenke = (item.findtext("link") or "").strip()
        dato = item.findtext("pubDate")
        publisert = parsedate_to_datetime(dato).astimezone(OSLO).date() if dato else None
        resultat.append(
            {
                "tittel": (item.findtext("title") or "").strip(),
                "lenke": lenke,
                "publisert": publisert,
                "samtykke": "/hoeringer-samtykker/" in lenke,
            }
        )
    return resultat


def tolk_detalj(html: str, publisert: date | None) -> tuple[date | None, str, str]:
    """Frist, fristtekst og ingress fra detaljsiden."""
    suppe = BeautifulSoup(html, "html.parser")
    hoved = suppe.find("main") or suppe
    tekst = hoved.get_text(" ", strip=True)
    frist = frist_etter_ord(tekst, publisert)
    avsnitt = hoved.find("p")
    ingress = avsnitt.get_text(" ", strip=True) if avsnitt else ""
    fristtekst = (
        f"Høringsfrist: {frist.strftime('%d.%m.%Y')}" if frist else setning_med_frist(tekst)
    )
    return frist, fristtekst, ingress


class Dsb(Kilde):
    """DSBs høringer, oppdaget via RSS."""

    def hent(self) -> list[Hoering]:
        """Henter RSS og detaljsidene til nye oppslag."""
        geografi = GeografiFilter(self.felles.get("geografi", {}))
        grense = i_dag() - NYHET_MAKS_ALDER
        resultat = []
        for h in tolk_rss(self.nett.hent(self.konfig["url"]).text):
            if h["publisert"] and h["publisert"] < grense:
                continue
            if h["samtykke"] and not geografi.vurder(h["tittel"]).relevant:
                continue
            frist, fristtekst, ingress = tolk_detalj(
                self.nett.hent(h["lenke"]).text, h["publisert"]
            )
            resultat.append(
                self.lag_hoering(
                    instans=INSTANS,
                    tittel=("Samtykkehøring: " if h["samtykke"] else "") + h["tittel"],
                    lenke=h["lenke"],
                    frist=frist,
                    frist_tekst=fristtekst,
                    publisert=h["publisert"],
                    ingress=ingress,
                )
            )
        return resultat
