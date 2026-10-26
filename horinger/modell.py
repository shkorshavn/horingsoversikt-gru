"""Felles datamodell for en høring."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import date, datetime


def lag_id(lenke: str) -> str:
    """Lager en stabil, kort id ut fra lenken til høringen."""
    return hashlib.sha1(lenke.strip().encode("utf-8")).hexdigest()[:12]


@dataclass
class Hoering:
    """Én høring slik den lagres i data/horinger.json."""

    kilde: str
    kategori: str
    prioritet: int
    instans: str
    tittel: str
    lenke: str
    frist: date | None = None
    frist_tekst: str = ""
    # Frist med bare måned og år («desember 2026»): «2026-12». `frist` er da den 1. i måneden
    # (Svein 25.10.2026), og høringen arkiveres først når måneden er over.
    frist_maned: str = ""
    publisert: date | None = None
    ingress: str = ""
    hentet: datetime | None = None
    niva: str = ""
    # Høringsparter slik kilden lister dem (sprint 6). Kategorier og regionflagg beregnes i
    # bygg.py ut fra sources.yaml, slik at endringer der slår inn uten ny henting.
    horingsparter: list[str] = field(default_factory=list)
    # «Åpen for alle», «Ikke tilgjengelig» e.l.
    horingsparter_merknad: str = ""
    # Lenke til listen når den er et vedlegg (PDF), slik at den kan åpnes fra siden.
    horingsparter_lenke: str = ""
    # Saksfelt fra regjeringen.no (f.eks. «Skole og videregående opplæring»).
    saksfelt: list[str] = field(default_factory=list)
    # Versjonen av tolkingen som fylte inn høringspartene (se kilder/base.py).
    detalj_versjon: int = 0
    id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.id:
            self.id = lag_id(self.lenke)

    def til_dict(self) -> dict:
        """Gjør høringen om til en ordbok med datoer i ISO 8601."""
        data = asdict(self)
        for nokkel in ("frist", "publisert", "hentet"):
            verdi = data[nokkel]
            data[nokkel] = verdi.isoformat() if verdi else None
        return data
