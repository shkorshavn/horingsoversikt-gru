"""Søkeordfilter for kilder der høringene står i en nyhetsstrøm (Nye Veier,
Jernbanedirektoratet og Bane NOR).

Ordene står i sources.yaml (`sokeord` og `utelat_ord` per kilde), slik at de kan justeres
uten kodeendring. Treff er ikke nok alene: kildene krever i tillegg en frist på detaljsiden,
eller at oppslaget er nytt (se den enkelte kilden).
"""

from __future__ import annotations

import re


class Sokeord:
    """Avgjør om en tekst ser ut som en høring, ut fra søkeord og ord som utelukker."""

    def __init__(self, sokeord: list[str], utelat: list[str] | None = None) -> None:
        self._ja = _monster(sokeord)
        self._nei = _monster(utelat or [])

    def treff(self, tekst: str) -> str:
        """Gir første søkeord som står i teksten, eller tom tekst hvis ingen (eller utelatt)."""
        tekst = tekst or ""
        if self._nei and self._nei.search(tekst):
            return ""
        if self._ja and (m := self._ja.search(tekst)):
            return m.group(0)
        return ""


def _monster(ord_: list[str]) -> re.Pattern[str] | None:
    if not ord_:
        return None
    alternativer = "|".join(re.escape(o) for o in sorted(ord_, key=len, reverse=True))
    return re.compile(rf"(?<![\wæøå])(?:{alternativer})", re.IGNORECASE)
