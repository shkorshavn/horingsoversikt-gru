"""Regjeringen.no – høringer fra departementene.

Bare `?page=N` er tillatt i robots.txt, så filtrering skjer i koden: Bare
oppføringer med status «På høring»/«På høyring» tas med, og departementene i
`ekskluder_departementer` filtreres bort. Listen er sortert på publiseringsdato,
og innhentingen blar til den har sett to hele sider uten åpne høringer.

Merk: Regjeringen.no avviser GitHub Actions med en robotsjekk (Cloudflare).
Modulen virker fra vanlige nettverk, se kartleggingen og sprintrapport 1.
"""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from horinger.datoer import tolk_punktumdato
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

MAKS_SIDER = 20
SIDER_UTEN_APNE_FOR_STOPP = 2


def er_apen(status: str) -> bool:
    """«Status: På høring» eller nynorsk «På høyring»."""
    status = status.lower()
    return "på høring" in status or "på høyring" in status


def tolk_side(html: str, base: str) -> list[dict]:
    """Tolker én listeside. Returnerer alle oppføringer, også lukkede, med status."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for punkt in suppe.select("ul.listing > li"):
        lenke = punkt.select_one("h2 a[href]")
        if not lenke:
            continue
        dato = punkt.select_one(".info .date")
        departement = punkt.select_one(".info .department")
        ingress = punkt.select_one(".excerpts")
        frist_tekst = ""
        status = ""
        for detalj in punkt.select(".event-details span"):
            tekst = detalj.get_text(" ", strip=True)
            if "frist" in tekst.lower():
                frist_tekst = tekst
            elif tekst.lower().startswith("status"):
                status = tekst
        resultat.append(
            {
                "instans": departement.get_text(" ", strip=True) if departement else "",
                "tittel": lenke.get_text(" ", strip=True),
                "lenke": urljoin(base, lenke["href"]),
                "frist": tolk_punktumdato(frist_tekst),
                "frist_tekst": frist_tekst,
                "publisert": tolk_punktumdato(dato.get_text()) if dato else None,
                "ingress": ingress.get_text(" ", strip=True) if ingress else "",
                "status": status,
            }
        )
    return resultat


def velg(rader: list[dict], ekskluder: set[str]) -> list[dict]:
    """Beholder åpne høringer fra departementer som ikke er ekskludert."""
    return [
        {k: v for k, v in r.items() if k != "status"}
        for r in rader
        if er_apen(r["status"]) and r["instans"] not in ekskluder
    ]


class Regjeringen(Kilde):
    """Høringslisten på regjeringen.no."""

    def hent(self) -> list[Hoering]:
        """Blar gjennom listen til to hele sider er uten åpne høringer."""
        base = self.konfig["url"]
        ekskluder = set(self.felles.get("ekskluder_departementer", []))
        resultat: list[Hoering] = []
        sider_uten_apne = 0
        for side in range(1, MAKS_SIDER + 1):
            rader = tolk_side(self.nett.hent(f"{base}?page={side}").text, base)
            if not rader:
                break
            if any(er_apen(r["status"]) for r in rader):
                sider_uten_apne = 0
            else:
                sider_uten_apne += 1
                if sider_uten_apne >= SIDER_UTEN_APNE_FOR_STOPP:
                    break
            resultat.extend(self.lag_hoering(**f) for f in velg(rader, ekskluder))
        return resultat
