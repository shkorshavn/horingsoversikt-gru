"""Felles grensesnitt for kildemodulene."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta

from horinger import OSLO
from horinger.modell import Hoering
from horinger.nett import Nett

# Kilder der høringene står i en nyhetsstrøm eller RSS (DSB, Nye Veier, Jernbanedirektoratet,
# Bane NOR): oppslag eldre enn dette åpnes ikke. Holder antall kall nede, og hindrer at gamle
# oppslag uten eksakt frist blir stående som åpne.
NYHET_MAKS_ALDER = timedelta(days=120)


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
        """Lager en Hoering med kildens navn, kategori og prioritet fylt inn."""
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
            publisert=publisert,
            ingress=" ".join(ingress.split()),
            hentet=self.hentet,
        )
