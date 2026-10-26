"""Felles grensesnitt for kildemodulene."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta

from bs4 import BeautifulSoup

from horinger import OSLO
from horinger.datoer import MANEDER, finn_frist_maned, kort_ingress
from horinger.geografi import GeografiFilter
from horinger.horingsparter import (
    APEN_FOR_ALLE,
    IKKE_OPPGITT,
    IKKE_TILGJENGELIG,
    fra_html,
    fra_pdf,
)
from horinger.modell import Hoering
from horinger.nett import Nett, SperretAvRobots
from horinger.sokeord import Sokeord

# Kilder der høringene står i en nyhetsstrøm eller RSS (DSB, Nye Veier, Jernbanedirektoratet,
# Bane NOR): oppslag eldre enn dette åpnes ikke. Holder antall kall nede, og hindrer at gamle
# oppslag uten eksakt frist blir stående som åpne.
NYHET_MAKS_ALDER = timedelta(days=120)
MANEDSNAVN = list(MANEDER)

log = logging.getLogger("horinger")

# Økes når tolkingen av detaljsidene endres. Lagrede høringsparter med en annen versjon brukes
# ikke om igjen, slik at alle åpne høringer leses på nytt med den nye tolkingen.
DETALJ_VERSJON = 2


class Kilde(ABC):
    """En kilde henter høringer og gir dem tilbake som Hoering-objekter.

    `konfig` er kildens oppføring i sources.yaml, og `felles` er de felles
    innstillingene (bl.a. geografi og ekskluderte departementer).
    """

    def __init__(self, konfig: dict, nett: Nett, felles: dict | None = None) -> None:
        self.konfig = konfig
        self.nett = nett
        self.felles = felles or {}
        self.hentet = datetime.now(OSLO).replace(microsecond=0)

    @property
    def navn(self) -> str:
        """Kildens visningsnavn fra sources.yaml."""
        return self.konfig["navn"]

    def aktuell_for_regionen(self, tekst: str) -> bool:
        """Om teksten gjelder kommunene eller regionen (Svein 25.10.2026).

        Samme regel som løftet til høy prioritet: ordene i `felles.prioritet_loft.ord`
        (kommunene, fylkeskommunen, plan- og bygningsloven …) eller et sted i geografien.
        Brukes av etater uten egen høringsliste, som bare skal være med når det er aktuelt.
        """
        ord_ = Sokeord(self.felles.get("prioritet_loft", {}).get("ord", []))
        geografi = GeografiFilter(self.felles.get("geografi", {}))
        return bool(ord_.treff(tekst)) or geografi.vurder(tekst).relevant

    def krav_oppfylt(self, tekst: str) -> bool:
        """Kildens krav fra sources.yaml (`krav: aktuell_for_regionen`), ellers alltid sant."""
        if self.konfig.get("krav") == "aktuell_for_regionen":
            return self.aktuell_for_regionen(tekst)
        return True

    @abstractmethod
    def hent(self) -> list[Hoering]:
        """Henter høringene fra kilden."""

    def lag_hoering(
        self,
        *,
        instans: str,
        tittel: str,
        lenke: str,
        frist: date | None,
        frist_tekst: str = "",
        publisert: date | None = None,
        ingress: str = "",
    ) -> Hoering:
        """Lager en Hoering med kildens navn, kategori og prioritet fylt inn.

        Mangler fristen dag, men har måned og år, brukes den 1. i måneden, og fristteksten blir
        «Høringsfrist: desember 2026» (Svein 25.10.2026). Ingressen kuttes ved et helt ord.
        """
        frist_maned = ""
        if frist is None and (maned := finn_frist_maned(frist_tekst)):
            ar, mnd = maned
            frist = date(ar, mnd, 1)
            frist_maned = f"{ar}-{mnd:02d}"
            frist_tekst = f"Høringsfrist: {MANEDSNAVN[mnd - 1]} {ar}"
        return Hoering(
            kilde=self.navn,
            kategori=self.konfig.get("kategori", ""),
            niva=self.konfig.get("niva", ""),
            prioritet=int(self.konfig.get("prioritet", 3)),
            instans=" ".join(instans.split()),
            tittel=" ".join(tittel.split()),
            lenke=lenke.strip(),
            frist=frist,
            frist_tekst=" ".join(frist_tekst.split()),
            frist_maned=frist_maned,
            publisert=publisert,
            ingress=kort_ingress(ingress),
            hentet=self.hentet,
        )

    # -----------------------------------------------------------------------------------------
    # Høringsparter (sprint 6)

    def detaljfelt(self, suppe: BeautifulSoup) -> dict:
        """Ekstra felt fra detaljsiden. Regjeringen.no leser saksfelt her."""
        return {}

    def fyll_horingsparter(
        self, hoeringer: list[Hoering], forrige: dict[str, dict] | None = None
    ) -> int:
        """Fyller inn høringsparter for høringene fra denne kjøringen. Gir antall nye kall.

        Styres av `horingsparter` for kilden i sources.yaml:
        - `detalj: true`: detaljsiden leses for listen («Høringsinstanser»).
        - `pdf: true`: står listen i en PDF, leses den, der robots.txt tillater det.
        - `merknad`: fast merknad når kilden ikke har lister (f.eks. «Åpen for alle»).

        Det som ble funnet forrige gang (`forrige`, etter id), brukes om igjen, slik at bare nye
        høringer koster kall. Bare åpne høringer slås opp, og høyst `maks_per_kjoring`.
        En feil for én høring stopper aldri resten.
        """
        oppsett = self.konfig.get("horingsparter") or {}
        forrige = forrige or {}
        fast_merknad = oppsett.get("merknad", "")
        maks = int(oppsett.get("maks_per_kjoring", 60))
        kall = 0
        idag = datetime.now(OSLO).date()
        for h in hoeringer:
            gammel = forrige.get(h.id)
            if (
                gammel
                and gammel.get("detalj_versjon") == DETALJ_VERSJON
                and (gammel.get("horingsparter") or gammel.get("horingsparter_merknad"))
            ):
                h.horingsparter = list(gammel.get("horingsparter") or [])
                h.horingsparter_merknad = gammel.get("horingsparter_merknad", "")
                h.horingsparter_lenke = gammel.get("horingsparter_lenke", "")
                h.saksfelt = h.saksfelt or list(gammel.get("saksfelt") or [])
                h.detalj_versjon = DETALJ_VERSJON
                continue
            if not oppsett.get("detalj") or (h.frist is not None and h.frist < idag):
                h.horingsparter_merknad = h.horingsparter_merknad or fast_merknad
                continue
            if kall >= maks:
                log.info("%s: høyst %d detaljsider per kjøring, resten neste gang", self.navn, maks)
                break
            try:
                kall += self._les_horingsparter(h, bool(oppsett.get("pdf")))
            except Exception as feil:  # noqa: BLE001 – én høring skal ikke stoppe kilden
                # Uten merknad prøves høringen på nytt ved neste kjøring.
                log.warning("%s: høringsparter for %s: %s", self.navn, h.lenke, feil)
                continue
            if not h.horingsparter and not h.horingsparter_merknad:
                h.horingsparter_merknad = fast_merknad or IKKE_OPPGITT
        return kall

    def _les_horingsparter(self, h: Hoering, les_pdf: bool) -> int:
        h.detalj_versjon = DETALJ_VERSJON
        suppe = BeautifulSoup(self.nett.hent(h.lenke).text, "html.parser")
        kall = 1
        for nokkel, verdi in self.detaljfelt(suppe).items():
            setattr(h, nokkel, verdi)
        funnet = fra_html(suppe, h.lenke)
        h.horingsparter = funnet.parter
        if funnet.pdf and not funnet.parter:
            h.horingsparter_lenke = funnet.pdf
            if les_pdf:
                try:
                    svar = self.nett.hent(funnet.pdf)
                    kall += 1
                    if "pdf" in svar.headers.get("Content-Type", "pdf").lower():
                        h.horingsparter = fra_pdf(svar.content)
                except SperretAvRobots:
                    log.info("%s: høringslisten er sperret i robots.txt: %s", self.navn, funnet.pdf)
        if funnet.apen:
            h.horingsparter_merknad = APEN_FOR_ALLE
        elif funnet.pdf and not h.horingsparter:
            h.horingsparter_merknad = IKKE_TILGJENGELIG
        return kall
