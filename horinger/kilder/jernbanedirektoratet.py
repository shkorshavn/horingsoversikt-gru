"""Jernbanedirektoratet – høringer i nyhetene.

Direktoratet har ingen høringsside. Nyhetene hentes fra WordPress sitt REST-API med søk på
«høring». Det gir mest omtale av høringer, så et oppslag tas bare med når det er fra de
siste 120 dagene og tittel eller tekst inneholder et søkeord som viser at noe faktisk sendes
på høring (sources.yaml, `sokeord`). Fristen kan være vag («midten av juni»). Da vises den
som tekst uten dato (Svein 25.10.2026), og oppslaget faller bort etter 120 dager.
"""

from __future__ import annotations

import html as html_lib

from bs4 import BeautifulSoup

from horinger.datoer import frist_etter_ord, i_dag, setning_med_frist, tolk_iso
from horinger.kilder.base import NYHET_MAKS_ALDER, Kilde
from horinger.modell import Hoering
from horinger.sokeord import Sokeord

INSTANS = "Jernbanedirektoratet"


def _tekst(html: str) -> str:
    return " ".join(BeautifulSoup(html or "", "html.parser").get_text(" ").split())


def tolk(innlegg: list[dict], sokeord: Sokeord, grense) -> list[dict]:
    """Oppslag som ser ut som høringer, med frist eller fristsetning."""
    resultat = []
    for p in innlegg:
        publisert = tolk_iso(p.get("date"))
        if publisert is None or publisert.date() < grense:
            continue
        tittel = html_lib.unescape(_tekst((p.get("title") or {}).get("rendered", "")))
        tekst = _tekst((p.get("content") or {}).get("rendered", ""))
        if not sokeord.treff(f"{tittel} {tekst}"):
            continue
        frist = frist_etter_ord(tekst, publisert.date())
        resultat.append(
            {
                "instans": INSTANS,
                "tittel": tittel,
                "lenke": p.get("link") or "",
                "frist": frist,
                "frist_tekst": setning_med_frist(tekst),
                "publisert": publisert.date(),
                "ingress": tekst[:300] + ("…" if len(tekst) > 300 else ""),
            }
        )
    return resultat


class Jernbanedirektoratet(Kilde):
    """Høringer omtalt i Jernbanedirektoratets nyheter."""

    def hent(self) -> list[Hoering]:
        """Søker etter «høring» i nyhetene via WordPress-API-et."""
        sokeord = Sokeord(self.konfig.get("sokeord", []), self.konfig.get("utelat_ord", []))
        data = self.nett.hent(self.konfig["url"]).json()
        return [self.lag_hoering(**f) for f in tolk(data, sokeord, i_dag() - NYHET_MAKS_ALDER)]
