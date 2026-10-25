"""Geografisk filter for landsdekkende lister.

Reglene er avklart med Svein 16.10.2026 og styres fra `geografi` i sources.yaml:

- høringer som nevner en kommune i `kommuner` eller et tettsted i `steder`, er relevante
- høringer som gjelder rv. 4, er relevante (hele strekningen, også Nittedal og Oslo)
- høringer som gjelder E6, er relevante bare sammen med en kommune i `e6_kommuner`
- Oslo og Nittedal står ikke i `kommuner`, og gir derfor bare treff sammen med rv. 4
"""

from __future__ import annotations

import re
from dataclasses import dataclass

RV4 = re.compile(r"\b(?:rv|riksveg|riksvei)\.?\s*4(?!\d)", re.IGNORECASE)
E6 = re.compile(r"\bE\s?6(?!\d)", re.IGNORECASE)


# Postadresser som «postboks 1010 Nordre Ål, 2605 Lillehammer» – Vegvesenets sentrale
# adresse står i nesten alle høringer og må ikke gi geografisk treff.
# Krever komma foran postnummeret, slik at «… 2026 Gjøvik kommune» ikke fjernes.
_POSTADRESSE = re.compile(r",\s*\d{4}\s+[A-ZÆØÅ][\wæøåÆØÅ-]*(?:\s+[A-ZÆØÅ][\wæøåÆØÅ-]*)?")


def fjern_postadresser(tekst: str) -> str:
    """Fjerner «postnummer sted» fra teksten før geografisk vurdering."""
    return _POSTADRESSE.sub(" ", tekst or "")


def _ordmonster(navn: list[str]) -> re.Pattern[str] | None:
    """Lager et mønster som treffer hele ord, med stor forbokstav som i stedsnavn."""
    if not navn:
        return None
    alternativer = "|".join(re.escape(n) for n in sorted(navn, key=len, reverse=True))
    return re.compile(rf"(?<!\w)(?:{alternativer})(?!\w)")


@dataclass
class Treff:
    """Resultatet av en geografisk vurdering."""

    relevant: bool
    grunn: str = ""


class GeografiFilter:
    """Avgjør om en tekst gjelder Gjøvikregionen, naboregionene eller traseen til Oslo."""

    def __init__(self, konfig: dict) -> None:
        self.kommuner = _ordmonster(konfig.get("kommuner", []))
        self.steder = _ordmonster(konfig.get("steder", []))
        self.e6_kommuner = _ordmonster(konfig.get("e6_kommuner", []))

    def vurder(self, tekst: str) -> Treff:
        """Vurderer om teksten er relevant, og oppgir grunnen."""
        tekst = fjern_postadresser(tekst)
        if self.kommuner and (m := self.kommuner.search(tekst)):
            return Treff(True, f"kommune: {m.group(0)}")
        if self.steder and (m := self.steder.search(tekst)):
            return Treff(True, f"sted: {m.group(0)}")
        if RV4.search(tekst):
            return Treff(True, "rv. 4")
        if E6.search(tekst) and self.e6_kommuner and (m := self.e6_kommuner.search(tekst)):
            return Treff(True, f"E6 og {m.group(0)}")
        return Treff(False)
