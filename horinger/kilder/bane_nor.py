"""Bane NOR – varsler om planoppstart og høringer i prosjektene.

Høringene ligger som undersider til prosjektene, uten en samlet liste. Sitemapet har alle
adresser med endringsdato. Adresser fra de siste 120 dagene som inneholder et søkeord
(sources.yaml, `sokeord`, f.eks. «regulering», «horing», «planprogram»), åpnes. De tas med
når siden har en frist og treffer geografien (samme som Vegvesenets prosjekthøringer).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date, timedelta

from bs4 import BeautifulSoup

from horinger.datoer import (
    frist_etter_ord,
    fristtekst,
    i_dag,
    setning_med_frist,
    tolk_iso,
    tolk_tekstdato,
)
from horinger.geografi import GeografiFilter
from horinger.kilder.base import Kilde
from horinger.modell import Hoering
from horinger.sokeord import Sokeord

INSTANS = "Bane NOR"
NY_DAGER = timedelta(days=120)
_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
_PUBLISERT = re.compile(r"Publisert:\s*(\d{1,2}\.\s*\w+\s+\d{4})")


def tolk_sitemap(xml: str, sokeord: Sokeord, grense: date) -> list[str]:
    """Adresser med søkeord som er endret etter grensen, nyeste først."""
    rot = ET.fromstring(xml.lstrip("﻿").encode("utf-8"))
    funnet = []
    for url in rot.iter(f"{{{_NS['s']}}}url"):
        adresse = (url.findtext("s:loc", namespaces=_NS) or "").strip()
        endret = tolk_iso(url.findtext("s:lastmod", namespaces=_NS))
        if not adresse or endret is None or endret.date() < grense:
            continue
        if sokeord.treff(adresse.replace("-", " ")):
            funnet.append((endret, adresse))
    return [a for _, a in sorted(funnet, reverse=True)]


def tolk_detalj(html: str) -> dict:
    """Tittel, publiseringsdato, frist, fristsetning, ingress og hele teksten."""
    suppe = BeautifulSoup(html, "html.parser")
    hoved = suppe.find("main") or suppe
    tekst = " ".join(hoved.get_text(" ").split())
    tittel = hoved.find("h1")
    pub = _PUBLISERT.search(tekst)
    publisert = tolk_tekstdato(pub.group(1)) if pub else None
    ingress = next(
        (p.get_text(" ", strip=True) for p in hoved.find_all("p") if len(p.get_text()) > 60), ""
    )
    return {
        "tittel": tittel.get_text(" ", strip=True) if tittel else "",
        "publisert": publisert,
        "frist": frist_etter_ord(tekst, publisert),
        "frist_tekst": "",
        "setning": setning_med_frist(tekst),
        "ingress": ingress[:400],
        "tekst": tekst,
    }


class BaneNor(Kilde):
    """Planvarsler og høringer i Bane NORs prosjekter i området."""

    def hent(self) -> list[Hoering]:
        """Leser sitemapet og åpner nye sider med søkeord."""
        sokeord = Sokeord(self.konfig.get("sokeord", []), self.konfig.get("utelat_ord", []))
        geografi = GeografiFilter(self.felles.get("geografi", {}))
        adresser = tolk_sitemap(
            self.nett.hent(self.konfig["url"]).text, sokeord, i_dag() - NY_DAGER
        )
        resultat = []
        for adresse in adresser[: int(self.konfig.get("maks_sider", 15))]:
            d = tolk_detalj(self.nett.hent(adresse).text)
            if d["frist"] is None or not geografi.vurder(d["tekst"]).relevant:
                continue
            resultat.append(
                self.lag_hoering(
                    instans=INSTANS,
                    tittel=d["tittel"],
                    lenke=adresse,
                    frist=d["frist"],
                    frist_tekst=fristtekst(d["frist"], d["setning"]),
                    publisert=d["publisert"],
                    ingress=d["ingress"],
                )
            )
        return resultat
