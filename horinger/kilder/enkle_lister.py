"""Etater med en enkel høringsliste i HTML: Helsedirektoratet, Bufdir og DiBK.

Alle tre viser tittel, lenke og «Høringsfrist» i listen, så detaljsidene trengs ikke.
"""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from horinger.datoer import i_dag, tolk_dato
from horinger.kilder.base import Kilde
from horinger.modell import Hoering


def _fristtekst(tekst: str) -> str:
    """«Høringsfrist: 03.12.2026» fra en tekstblokk, eller tom tekst."""
    tekst = " ".join(tekst.split())
    pos = tekst.lower().find("høringsfrist")
    return tekst[pos:].strip() if pos >= 0 else ""


def tolk_helsedirektoratet(html: str, base: str) -> list[dict]:
    """Høringene under overskriften «Ute på høring». «Under behandling» tas ikke med."""
    suppe = BeautifulSoup(html, "html.parser")
    overskrift = next(
        (h for h in suppe.find_all(["h2", "h3"]) if "ute på høring" in h.get_text().lower()),
        None,
    )
    if overskrift is None:
        return []
    resultat = []
    for el in overskrift.find_all_next(["a", "h2"]):
        if el.name == "h2":
            break
        if not isinstance(el, Tag) or not el.get("href") or not el.find("h3"):
            continue
        undertekst = el.select_one(".b-list-item-type__subheading")
        frist_tekst = _fristtekst(undertekst.get_text(" ") if undertekst else "")
        resultat.append(
            {
                "instans": "Helsedirektoratet",
                "tittel": el.find("h3").get_text(" ", strip=True),
                "lenke": urljoin(base, el["href"]),
                "frist": tolk_dato(frist_tekst),
                "frist_tekst": frist_tekst,
            }
        )
    return resultat


def tolk_bufdir(html: str, base: str) -> list[dict]:
    """Høringer med frist i dag eller senere. Listen har også eldre høringer under behandling."""
    suppe = BeautifulSoup(html, "html.parser")
    hoved = suppe.find("main") or suppe
    resultat = []
    for lenke in hoved.find_all("a", href=True):
        if "/hoeringer/" not in lenke["href"] and "/horinger/" not in lenke["href"]:
            continue
        blokk = lenke.find_parent(["li", "article"]) or lenke.parent
        frist_tekst = _fristtekst(blokk.get_text(" ") if blokk else "")
        frist = tolk_dato(frist_tekst, i_dag())
        if frist is None or frist < i_dag():
            continue
        resultat.append(
            {
                "instans": "Bufdir",
                "tittel": lenke.get_text(" ", strip=True),
                "lenke": urljoin(base, lenke["href"]),
                "frist": frist,
                "frist_tekst": frist_tekst,
            }
        )
    return resultat


def tolk_dibk(html: str, base: str) -> list[dict]:
    """Alle høringer på listen. Byggingen skiller åpne fra utløpte ut fra fristen."""
    suppe = BeautifulSoup(html, "html.parser")
    hoved = suppe.find("main") or suppe
    resultat = []
    for lenke in hoved.find_all("a", href=True):
        tekst = " ".join(lenke.get_text(" ").split())
        if "høringsfrist" not in tekst.lower():
            continue
        frist_tekst = _fristtekst(tekst)
        frist = tolk_dato(frist_tekst)
        tittel_el = lenke.find(["h2", "h3", "h4"])
        tittel = tittel_el.get_text(" ", strip=True) if tittel_el else ""
        resultat.append(
            {
                "instans": "Direktoratet for byggkvalitet (DiBK)",
                "tittel": tittel,
                "lenke": urljoin(base, lenke["href"]),
                "frist": frist,
                "frist_tekst": f"Høringsfrist: {frist.strftime('%d.%m.%Y')}" if frist else "",
                "ingress": "På oppdrag fra Kommunal- og distriktsdepartementet.",
            }
        )
    return resultat


TOLKERE = {
    "helsedirektoratet": tolk_helsedirektoratet,
    "bufdir": tolk_bufdir,
    "dibk": tolk_dibk,
}


class EnkelListe(Kilde):
    """Henter listesiden og tolker den med tolkeren som hører til modulen."""

    def hent(self) -> list[Hoering]:
        """Henter og tolker listesiden."""
        url = self.konfig["url"]
        tolker = TOLKERE[self.konfig["modul"]]
        return [self.lag_hoering(**f) for f in tolker(self.nett.hent(url).text, url)]
