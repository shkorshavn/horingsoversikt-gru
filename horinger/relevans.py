"""KI-vurdering av om en høring er relevant for Gjøvikregionen (sprint 8, versjon 2).

For hver høring gir modellen to svar. Det ene er om høringen er relevant for kommunene eller
regionen. Det andre er én kort setning om hvorfor (Svein 27.10.2026).
Høringer som vurderes som ikke relevante, vises under «Utelatte høringer» på nettsiden med
begrunnelsen. De fjernes aldri helt.

Regionbeskrivelsen og eksemplene står i `felles.relevans` i sources.yaml. Endres de, vurderes
alle høringene på nytt ved neste ukentlige oppdatering, fordi de inngår i sjekksummen.
Modell, lengde og pause er de samme som for sammendraget (`felles.sammendrag`).

Kjøres sammen med sammendraget: `python -m horinger.sammendrag`.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from horinger.sammendrag import Sammendrag, grunnlag, kjor_oppgave, sjekksum

# Økes når tolkingen endres. Instruksen selv inngår i sjekksummen.
VERSJON = 1

MAL = """Du vurderer offentlige høringer for Gjøvikregionen Utvikling (GRU).

Om regionen:
{region}

Oppgave: Avgjør om høringen er relevant for kommunene i Gjøvikregionen eller for regionen,
og skriv én setning om hvorfor.

Relevant er høringer som kan påvirke
- kommunenes oppgaver, tjenester, økonomi, planlegging eller regelverk
- innbyggerne, næringslivet, arbeidsplassene eller kompetansemiljøene i regionen
- samferdsel, energi, natur, landbruk eller annen infrastruktur i Innlandet.
Nasjonale regler som gjelder alle kommuner eller hele landet, er relevante.

Ikke relevant er høringer som
- bare gjelder et annet område, f.eks. Svalbard, Nord-Norge, kysten eller havet
- bare gjelder en næring som knapt finnes i regionen, f.eks. fiske, skipsfart, havbruk eller
  petroleum
- er så smale eller tekniske at de ikke berører kommunene, innbyggerne eller næringslivet i
  regionen på noen merkbar måte.

Eksempler på høringer som IKKE er relevante:
{ikke_relevant}

Er du i tvil, regn høringen som relevant.

Svar med JSON og ingenting annet: {{"relevant": true eller false, "hvorfor": "..."}}
- «hvorfor»: én setning på norsk bokmål i klarspråk.
- Når høringen er relevant (høyst 25 ord): si konkret hva i høringen som berører kommunene
  eller regionen. Ikke gjenta sammendraget, og ikke overdriv.
- Når den ikke er relevant (høyst 15 ord): si bare hva den gjelder som gjør den uaktuell, f.eks.
  «Gjelder bare kystruten Bergen–Kirkenes.»
- Begynn rett på saken, uten «Høringen er relevant fordi».
- Bruk bare opplysninger fra teksten og fra beskrivelsen av regionen. Ikke gjett.
- Ikke legg til stedsnavn, avstander eller geografi som ikke står i teksten.
- Nevn regionens egne prosjekter og virksomheter (f.eks. rv. 4 eller NTNU i Gjøvik) bare når
  høringen gjelder dem eller fagfeltet deres direkte.
- Gir teksten for lite å bygge på, svar {{"relevant": true, "hvorfor": ""}}."""


def instruks(konfig: dict) -> str:
    """Instruksen til modellen, med regionbeskrivelse og eksempler fra sources.yaml."""
    eksempler = konfig.get("ikke_relevant_eksempler") or []
    return MAL.format(
        region=" ".join(str(konfig.get("region", "")).split()),
        ikke_relevant="\n".join(f"- {e}" for e in eksempler) or "- (ingen)",
    )


def tolk_svar(tekst: str) -> dict:
    """Gjør svaret om til {"relevant": bool, "hvorfor": str}. Ugyldig svar gir ValueError."""
    funn = re.search(r"\{.*\}", tekst or "", re.S)
    if not funn:
        raise ValueError(f"svaret er ikke JSON: {tekst[:80]!r}")
    data = json.loads(funn.group(0))
    relevant = data.get("relevant")
    if not isinstance(relevant, bool):
        raise ValueError(f"«relevant» mangler eller er ikke true/false: {relevant!r}")
    hvorfor = " ".join(str(data.get("hvorfor") or "").split()).strip("«»\"'")
    return {"relevant": relevant, "hvorfor": hvorfor}


class Relevans(Sammendrag):
    """Lager og bufrer relevansvurderingen. Bruker modell og grenser fra `felles.sammendrag`."""

    versjon = VERSJON

    def __init__(self, konfig: dict, relevanskonfig: dict, klient=None) -> None:
        super().__init__(konfig, klient)
        self.instruks = instruks(relevanskonfig)

    def sjekksum(self, h: dict) -> str:
        """Sjekksum av grunnlaget og instruksen, slik at nye eksempler gir ny vurdering."""
        return sjekksum(self.instruks + "\n" + grunnlag(h))

    def felter(self, h: dict) -> dict:
        """Ett kall til API-et for én høring."""
        return tolk_svar(self.kall(self.instruks, grunnlag(h)))


def kjor(
    konfig: dict, kildemappe: Path, utdata: Path, klient=None, dag: date | None = None
) -> dict:
    """Oppdaterer data/relevans.json. Vurderinger for høringer som er borte, slettes."""
    felles = konfig.get("felles", {})
    oppgave = Relevans(felles.get("sammendrag", {}), felles.get("relevans", {}), klient)
    return kjor_oppgave(oppgave, "relevans", konfig, kildemappe, utdata, dag)


def vurder(h: dict, svar: dict | None, konfig: dict) -> dict:
    """Feltene nettsiden får for én høring: `relevant` og `hvorfor_relevant`.

    Høringer der regionen er høringspart, som Gjøvik kommune har mottatt, eller som kommer fra
    et nivå i `aldri_utelat_niva` (Innlandet fylkeskommune og Statsforvalteren), utelates
    aldri. Mangler vurderingen, er høringen med.
    """
    svar = svar or {}
    relevant = svar.get("relevant", True) is not False
    vernet = (
        bool(h.get("regionflagg"))
        or bool(h.get("postliste"))
        or h.get("niva") in (konfig.get("aldri_utelat_niva") or [])
    )
    if not relevant and vernet:
        # Begrunnelsen for å utelate passer ikke når høringen likevel vises.
        return {"relevant": True, "hvorfor_relevant": ""}
    return {"relevant": relevant, "hvorfor_relevant": svar.get("hvorfor", "")}
