"""Felles grensesnitt for kildemodulene."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta

from horinger import OSLO
from horinger.datoer import MANEDER, finn_frist_maned, kort_ingress
from horinger.geografi import GeografiFilter
from horinger.modell import Hoering
from horinger.nett import Nett
from horinger.sokeord import Sokeord

# Kilder der høringene står i en nyhetsstrøm eller RSS (DSB, Nye Veier, Jernbanedirektoratet,
# Bane NOR): oppslag eldre enn dette åpnes ikke. Holder antall kall nede, og hindrer at gamle
# oppslag uten eksakt frist blir stående som åpne.
NYHET_MAKS_ALDER = timedelta(days=120)
MANEDSNAVN = list(MANEDER)


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
