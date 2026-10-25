"""Etater med prioritet 2 og 3 (sprint 5).

Hver etat har en tolker for listesiden og eventuelt detaljsiden. Felles regler:

- Fristen hentes fra listen når den står der, ellers fra detaljsiden (`frist_etter_ord`).
- Oppslag uten eksakt dato tas med i inntil 90 dager etter publisering, med fristteksten som den
  står (f.eks. «desember 2026»). Uten publiseringsdato og uten frist tas de ikke med.
- Detaljsider hentes bare for oppslag fra de siste 120 dagene (`NYHET_MAKS_ALDER`).
- Kilder med `krav: aktuell_for_regionen` i sources.yaml tas bare med når teksten gjelder
  kommunene eller regionen (Svein 25.10.2026).
"""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from horinger.datoer import (
    frist_etter_ord,
    fristtekst,
    i_dag,
    setning_med_frist,
    tolk_dato,
    tolk_iso,
    tolk_punktumdato,
    tolk_tekstdato,
)
from horinger.geografi import GeografiFilter
from horinger.kilder.base import NYHET_MAKS_ALDER, Kilde
from horinger.modell import Hoering

UTEN_FRIST_DAGER = timedelta(days=90)
_PUBLISERT = re.compile(r"Publisert\s*:?\s*(\d{1,2}\.\s*\w+\s+\d{4}|\d{1,2}\.\d{1,2}\.\d{4})")


def _tekst(el) -> str:
    return " ".join(el.get_text(" ").split()) if el is not None else ""


def _hoved(html: str):
    suppe = BeautifulSoup(html, "html.parser")
    return suppe.find("main") or suppe


def detalj(html: str, referanse: date | None = None) -> dict:
    """Tittel, frist, fristtekst, publiseringsdato, ingress og tekst fra en detaljside."""
    hoved = _hoved(html)
    tekst = _tekst(hoved)
    pub = _PUBLISERT.search(tekst)
    publisert = tolk_dato(pub.group(1)) if pub else None
    frist = frist_etter_ord(tekst, referanse or publisert)
    ingress = next((_tekst(p) for p in hoved.find_all("p") if len(p.get_text(strip=True)) > 60), "")
    h1 = hoved.find("h1")
    return {
        "tittel": _tekst(h1),
        "frist": frist,
        "frist_tekst": fristtekst(frist, setning_med_frist(tekst)),
        "publisert": publisert,
        "ingress": ingress,
        "tekst": tekst,
    }


def tas_med(frist: date | None, publisert: date | None) -> bool:
    """Med frist: alltid (byggingen skiller åpne fra utløpte). Uten: bare de første 90 dagene."""
    if frist is not None:
        return True
    return publisert is not None and publisert >= i_dag() - UTEN_FRIST_DAGER


# ---------- Tolkere for listesidene ----------


def tolk_nkom(html: str, base: str) -> list[dict]:
    """Nkom: kort med tittel og ingress. Fristen står på detaljsiden."""
    hoved = _hoved(html)
    resultat = []
    for a in hoved.select("li a[href*='/hoeringer/']"):
        tittel = a.select_one(".h2")
        ingress = a.select_one(".text-normal")
        resultat.append(
            {
                "tittel": _tekst(tittel) or _tekst(a),
                "lenke": urljoin(base, a["href"]),
                "ingress": _tekst(ingress),
            }
        )
    return resultat


def tolk_landbruk(html: str, base: str) -> list[dict]:
    """Landbruksdirektoratet: lenkene under «På høring nå», med fristen i avsnittet etter."""
    hoved = _hoved(html)
    overskrift = next(
        (h for h in hoved.find_all("h2") if "på høring nå" in _tekst(h).lower()), None
    )
    if overskrift is None:
        return []
    resultat = []
    for el in overskrift.find_all_next(["a", "h2", "h3", "table"]):
        if el.name != "a":
            break
        neste = el.find_next(string=re.compile("Høringsfrist", re.I))
        frist_tekst = " ".join(neste.split()) if neste else ""
        resultat.append(
            {
                "tittel": _tekst(el),
                "lenke": urljoin(base, el["href"]),
                "frist": tolk_dato(frist_tekst),
                "frist_tekst": frist_tekst,
            }
        )
    return resultat


def tolk_riksantikvaren(html: str, base: str) -> list[dict]:
    """Riksantikvaren: artikler med tittel, ingress og «Publisert». Fristen står i ingressen."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for overskrift in suppe.select("article h2"):
        lenke = overskrift.find("a", href=True)
        art = overskrift.find_parent("article")
        if lenke is None or art is None:
            continue
        tittel = _tekst(overskrift)
        tekst = _tekst(art)
        pub = _PUBLISERT.search(tekst)
        publisert = tolk_dato(pub.group(1)) if pub else None
        ingress_el = art.find("p")
        ingress = _tekst(ingress_el)
        frist = frist_etter_ord(ingress or tekst, publisert)
        resultat.append(
            {
                "tittel": tittel,
                "lenke": urljoin(base, lenke["href"]),
                "frist": frist,
                "frist_tekst": fristtekst(frist, setning_med_frist(ingress)),
                "publisert": publisert,
                "ingress": ingress,
            }
        )
    return resultat


def er_fredningssak(tekst: str) -> bool:
    """Fredningssaker og stedsregistreringer gjelder enkeltsteder og filtreres på geografi."""
    return bool(re.search(r"(?i)\bfred(?:e|ing|ning)|nasjonalt viktig|kulturmiljø", tekst))


def tolk_mattilsynet(html: str, base: str) -> list[dict]:
    """Mattilsynet: tabell «Publisert – Tittel – Høringsfrist».

    Rader som «Bestilling til VKM …» er ikke høringer og tas ikke med.
    """
    suppe = BeautifulSoup(html, "html.parser")
    tabell = suppe.find("table")
    resultat = []
    for rad in tabell.find_all("tr")[1:] if tabell else []:
        celler = rad.find_all("td")
        if len(celler) < 3:
            continue
        tittel = _tekst(celler[1])
        if tittel.lower().startswith("bestilling"):
            continue
        lenke = rad.find("a", href=True)
        resultat.append(
            {
                "tittel": tittel,
                "lenke": urljoin(base, lenke["href"]) if lenke else base,
                "frist": tolk_punktumdato(_tekst(celler[2])),
                "frist_tekst": f"Høringsfrist: {_tekst(celler[2])}",
                "publisert": tolk_punktumdato(_tekst(celler[0])),
            }
        )
    return resultat


def tolk_arbeidstilsynet(html: str, base: str) -> list[dict]:
    """Arbeidstilsynet: kort for pågående høringer (`hearing-card--current`)."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat = []
    for kort in suppe.select("li.hearing-card--current"):
        lenke = kort.find("a", href=True)
        frist_tekst = _tekst(kort.select_one(".date"))
        resultat.append(
            {
                "tittel": _tekst(lenke),
                "lenke": urljoin(base, lenke["href"]),
                "frist": tolk_dato(frist_tekst),
                "frist_tekst": frist_tekst,
            }
        )
    return resultat


_POLITI_FRIST = re.compile(r"(?i)høring\w*\s+(?:til|fram til|frem til)\s+(\d{1,2}\.\s*\w+\s+\d{4})")


def tolk_politiet(html: str) -> list[dict]:
    """Politiets dokumentkort. Flere dokumenter fra samme høring (samme frist og dato) slås
    sammen, og kortet med «Høring» først i tittelen gir tittel og lenke."""
    suppe = BeautifulSoup(html, "html.parser")
    grupper: dict[tuple, list[dict]] = {}
    for kort in suppe.select("article"):
        lenke = kort.select_one("h3 a[href]")
        if lenke is None:
            continue
        beskrivelse = _tekst(kort.find("p"))
        felt = {
            dt.get_text(strip=True).rstrip(":"): _tekst(dd)
            for dt, dd in zip(kort.find_all("dt"), kort.find_all("dd"), strict=False)
        }
        treff = _POLITI_FRIST.search(beskrivelse)
        frist = tolk_tekstdato(treff.group(1)) if treff else frist_etter_ord(beskrivelse)
        if frist is None:
            continue  # f.eks. egne høringssvar
        dok = {
            "tittel": _tekst(lenke),
            "lenke": lenke["href"],
            "frist": frist,
            "frist_tekst": treff.group(0) if treff else setning_med_frist(beskrivelse),
            "publisert": tolk_tekstdato(felt.get("Gjelder fra", "")),
            "ingress": beskrivelse,
            "instans": felt.get("Avsender", ""),
        }
        grupper.setdefault((frist, dok["publisert"]), []).append(dok)
    resultat = []
    for dokumenter in grupper.values():
        dokumenter.sort(key=lambda d: not d["tittel"].lower().startswith("høring"))
        resultat.append(dokumenter[0])
    return resultat


def tolk_skatteetaten(html: str, base: str) -> list[dict]:
    """Skatteetaten: listen ligger som JSON (`allthedata`) i siden, uten frist."""
    treff = re.search(r"var allthedata\s*=\s*(\[.*?\]);", html, re.S)
    if not treff:
        return []
    resultat = []
    for h in json.loads(treff.group(1)):
        publisert = tolk_iso((h.get("properties") or {}).get("startPublish"))
        resultat.append(
            {
                "tittel": h.get("title") or "",
                "lenke": urljoin(base, h.get("url") or ""),
                "publisert": publisert.date() if publisert else None,
            }
        )
    return resultat


def tolk_dmp(html: str, base: str) -> list[dict]:
    """DMP: lenker til høringer med «Publisert». Fristen står på detaljsiden."""
    hoved = _hoved(html)
    resultat = []
    for a in hoved.find_all("a", href=True):
        tekst = _tekst(a)
        tittel = re.split(r"\s+Publisert", tekst)[0].strip()
        if not tittel.lower().startswith(("høring", "høyring")) or "/nyheter/" not in a["href"]:
            continue
        pub = _PUBLISERT.search(tekst) or _PUBLISERT.search(_tekst(a.parent))
        resultat.append(
            {
                "tittel": tittel,
                "lenke": urljoin(base, a["href"]),
                "publisert": tolk_dato(pub.group(1)) if pub else None,
            }
        )
    return resultat


def tolk_nasjonalarkivet(html: str, base: str) -> list[dict]:
    """Nasjonalarkivet: tittelliste uten datoer. Bare lenker til egne høringssider."""
    suppe = BeautifulSoup(html, "html.parser")
    resultat, sett = [], set()
    for a in suppe.select("li.t2-link-list-item a[href]"):
        tittel = _tekst(a.select_one(".t2-link-list-item__text") or a)
        lenke = urljoin(base, a["href"])
        if lenke in sett or lenke.lower().endswith(".pdf"):
            continue
        if not re.match(r"(?i)h[øo]y?ring|arbeidet med", tittel):
            continue
        sett.add(lenke)
        resultat.append({"tittel": tittel, "lenke": lenke})
    return resultat


# ---------- Kildene ----------


class ListeMedDetalj(Kilde):
    """Felles gang: listeside → (detaljside ved behov) → høringer som oppfyller kravene."""

    instans = ""
    maks_detaljer = 10

    def tolk_liste(self, html: str, base: str) -> list[dict]:
        """Overstyres per etat."""
        raise NotImplementedError

    def trenger_detalj(self, h: dict) -> bool:
        """Detaljsiden hentes når fristen mangler og oppslaget er nytt nok."""
        if h.get("frist"):
            return False
        pub = h.get("publisert")
        return pub is None or pub >= i_dag() - NYHET_MAKS_ALDER

    def hent(self) -> list[Hoering]:
        """Henter listen og detaljsidene som trengs."""
        svar = self.nett.hent(self.konfig["url"])
        liste = self.tolk_liste(svar.text, svar.url or self.konfig["url"])
        resultat, detaljer = [], 0
        for h in liste:
            if self.trenger_detalj(h) and detaljer < self.maks_detaljer:
                detaljer += 1
                d = detalj(self.nett.hent(h["lenke"]).text, h.get("publisert"))
                h = {
                    **h,
                    "frist": d["frist"],
                    "frist_tekst": d["frist_tekst"],
                    "publisert": h.get("publisert") or d["publisert"],
                    "ingress": h.get("ingress") or d["ingress"],
                    "_tekst": d["tekst"],
                }
            if not tas_med(h.get("frist"), h.get("publisert")):
                continue
            if not self.godta(h):
                continue
            resultat.append(
                self.lag_hoering(
                    instans=h.get("instans") or self.instans,
                    tittel=h["tittel"],
                    lenke=h["lenke"],
                    frist=h.get("frist"),
                    frist_tekst=h.get("frist_tekst", ""),
                    publisert=h.get("publisert"),
                    ingress=h.get("ingress", ""),
                )
            )
        return resultat

    def godta(self, h: dict) -> bool:
        """Kildens krav (f.eks. aktuell for regionen). Kan overstyres."""
        return self.krav_oppfylt(f"{h['tittel']} {h.get('ingress', '')} {h.get('_tekst', '')}")


class Nkom(ListeMedDetalj):
    """Nasjonal kommunikasjonsmyndighet."""

    instans = "Nasjonal kommunikasjonsmyndighet (Nkom)"

    def tolk_liste(self, html, base):
        return tolk_nkom(html, base)

    def trenger_detalj(self, h):
        return True  # listen har aldri frist


class Landbruksdirektoratet(ListeMedDetalj):
    """Landbruksdirektoratet, seksjonen «På høring nå»."""

    instans = "Landbruksdirektoratet"

    def tolk_liste(self, html, base):
        return tolk_landbruk(html, base)


class Riksantikvaren(ListeMedDetalj):
    """Riksantikvaren. Fredningssaker bare når de gjelder Innlandet fylke (Svein 25.10.2026)."""

    instans = "Riksantikvaren"

    def tolk_liste(self, html, base):
        return tolk_riksantikvaren(html, base)

    def trenger_detalj(self, h):
        return False  # fristen står i ingressen

    def hent(self):
        resultat = super().hent()
        return [h for h in resultat if h.frist is not None]  # uten frist er det ikke en høring

    def godta(self, h):
        tekst = f"{h['tittel']} {h.get('ingress', '')}"
        if er_fredningssak(tekst):
            # Enkeltsteder: bare i Innlandet fylke (Svein 25.10.2026, sprint 5 v2). Saker som
            # gjelder kommunene eller fylkeskommunene tas med uansett.
            return self.aktuell_for_regionen(tekst) or self.i_innlandet(tekst)
        return True

    def i_innlandet(self, tekst: str) -> bool:
        """Om teksten nevner en kommune i Innlandet fylke (`geografi.innlandet_kommuner`)."""
        kommuner = self.felles.get("geografi", {}).get("innlandet_kommuner", [])
        return GeografiFilter({"kommuner": kommuner}).vurder(tekst).relevant


class Nasjonalarkivet(ListeMedDetalj):
    """Riksarkivarens høringer."""

    instans = "Nasjonalarkivet"
    maks_detaljer = 3  # listen er sortert med nyeste først, og har 1–2 høringer i året

    def tolk_liste(self, html, base):
        return tolk_nasjonalarkivet(html, base)


class Dmp(ListeMedDetalj):
    """Direktoratet for medisinske produkter."""

    instans = "Direktoratet for medisinske produkter (DMP)"

    def tolk_liste(self, html, base):
        return tolk_dmp(html, base)


class Mattilsynet(ListeMedDetalj):
    """Mattilsynets regelverksutvikling."""

    instans = "Mattilsynet"

    def tolk_liste(self, html, base):
        return tolk_mattilsynet(html, base)

    def trenger_detalj(self, h):
        return False


class Arbeidstilsynet(ListeMedDetalj):
    """Arbeidstilsynets pågående høringer."""

    instans = "Arbeidstilsynet"

    def tolk_liste(self, html, base):
        return tolk_arbeidstilsynet(html, base)

    def trenger_detalj(self, h):
        return False


class Politiet(ListeMedDetalj):
    """Politidirektoratet og Innlandet politidistrikt (samme dokumentliste, ulik enhet)."""

    def tolk_liste(self, html, base):
        return tolk_politiet(html)

    def trenger_detalj(self, h):
        return False

    @property
    def instans(self):  # type: ignore[override]
        return self.konfig["navn"]


class Skatteetaten(ListeMedDetalj):
    """Skatteetatens høringer. Fristen står (av og til) på detaljsiden."""

    instans = "Skatteetaten"

    def tolk_liste(self, html, base):
        nye = [
            h
            for h in tolk_skatteetaten(html, base)
            if h["publisert"] and h["publisert"] >= i_dag() - NYHET_MAKS_ALDER
        ]
        return sorted(nye, key=lambda h: h["publisert"], reverse=True)


class EnkeltSide(Kilde):
    """En side som viser én høring om gangen (SSB). Tas med når den har en frist som ikke er
    passert, og når kravene i sources.yaml er oppfylt."""

    def hent(self) -> list[Hoering]:
        url = self.konfig["url"]
        d = detalj(self.nett.hent(url).text)
        if d["frist"] is None or d["frist"] < i_dag() or not self.krav_oppfylt(d["tekst"]):
            return []
        return [
            self.lag_hoering(
                instans=self.konfig.get("instans", self.navn),
                tittel=d["tittel"],
                lenke=url,
                frist=d["frist"],
                frist_tekst=d["frist_tekst"],
                publisert=d["publisert"],
                ingress=d["ingress"],
            )
        ]
