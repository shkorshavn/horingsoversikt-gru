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
    publisert: date | None = None
    ingress: str = ""
    hentet: datetime | None = None
    niva: str = ""
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
