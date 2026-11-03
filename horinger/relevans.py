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
from horinger.tema import AlltidMed

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

Høringer om disse temaene er ALLTID relevante, uansett avsender:
- Mjøsa, innsjøer og elvene i Innlandet
- vannkvalitet, vannforvaltning og overvåking av innsjøer og vassdrag
- fartsgrenser og regler for båttrafikk på innsjøer og elver
- utslipp og avrenning til innsjøer og vassdrag
- ammunisjon eller annet avfall i Mjøsa eller andre innsjøer
- drikkevann og vannverk, flom og vassdragsregulering.

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
    """Gjør svaret om til {"relevant": bool, "hvorfor": str}. Ugyldig svar gir ValueError.

    Første JSON-objekt med «relevant» i svaret brukes, også når modellen skriver tekst eller
    flere objekter rundt (sprint 12: et svar med ekstra tekst etter JSON-en ble avvist).
    """
    tekst = tekst or ""
    dekoder = json.JSONDecoder()
    data = None
    for m in re.finditer(r"\{", tekst):
        try:
            kandidat, _ = dekoder.raw_decode(tekst, m.start())
        except ValueError:
            continue
        if isinstance(kandidat, dict) and "relevant" in kandidat:
            data = kandidat
            break
    if data is None:
        raise ValueError(f"svaret er ikke JSON med «relevant»: {tekst[:80]!r}")
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
        self.relevanskonfig = relevanskonfig

    def hopp_over(self, h: dict) -> bool:
        """Høringer som treffer en fast regel om å utelate, vurderes ikke av KI-en. Høringer som
        også treffer «alltid med», vurderes likevel, slik at de får «Hvorfor relevant»."""
        if AlltidMed(self.relevanskonfig.get("alltid_med")).treff_hoering(h):
            return False
        return fast_regel(h, self.relevanskonfig) is not None

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


def fast_regel(h: dict, konfig: dict) -> str | None:
    """Begrunnelsen fra første faste regel i `alltid_utelat` som treffer, ellers None.

    En regel treffer når tittelen begynner med `tittel_starter_med` (store og små bokstaver
    spiller ingen rolle). Faste regler går foran både KI-en og vernet (Svein 28.10.2026).
    """
    tittel = (h.get("tittel") or "").strip().casefold()
    for regel in konfig.get("alltid_utelat") or []:
        start = str(regel.get("tittel_starter_med") or "").strip().casefold()
        if start and tittel.startswith(start):
            return str(regel.get("grunn") or "Utelatt etter fast regel.")
    return None


def vurder(h: dict, svar: dict | None, konfig: dict) -> dict:
    """Feltene nettsiden får for én høring: `relevant` og `hvorfor_relevant`.

    Rekkefølgen (Svein 28.10. og 03.11.2026):
    1. «Alltid med» for Mjøsa og vann (`alltid_med`, sprint 12): alltid med. Treffet er lagret i
       `h["alltid_med"]` av bygg.py, ellers vurderes tittel og ingress her.
    2. Faste regler (`alltid_utelat`), f.eks. representantforslag: alltid utelatt.
    3. Vern: høringer der regionen er høringspart, som Gjøvik kommune har mottatt, eller som
       kommer fra et nivå i `aldri_utelat_niva`, utelates aldri.
    4. KI-vurderingen. Mangler den, er høringen med.
    """
    svar = svar or {}
    if h.get("alltid_med") or AlltidMed(konfig.get("alltid_med")).treff_hoering(h):
        hvorfor = svar.get("hvorfor", "") if svar.get("relevant", True) is not False else ""
        return {"relevant": True, "hvorfor_relevant": hvorfor}
    if (grunn := fast_regel(h, konfig)) is not None:
        return {"relevant": False, "hvorfor_relevant": grunn}
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
