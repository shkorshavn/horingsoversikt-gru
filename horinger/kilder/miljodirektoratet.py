"""Miljødirektoratet – høringer.

Henter JSON-endepunktet som høringssiden selv bruker (20 per side, `skip` for å bla).
Høringer med tema «Olje og gass» tas ikke med (Svein 25.10.2026), på samme måte som
Sokkeldirektoratet og Havtil er utelatt. Temaene som utelates, står i sources.yaml
(`utelat_tema`).
"""

from __future__ import annotations

from urllib.parse import urljoin

from horinger.datoer import tolk_punktumdato
from horinger.kilder.base import Kilde
from horinger.modell import Hoering

INSTANS = "Miljødirektoratet"
BASE = "https://www.miljodirektoratet.no/"
API = BASE + "hearingslistpage/gethearings?skip={skip}&searchTerm=&searchExpired=false"
MAKS_SIDER = 10


def tolk(data: dict, utelat_tema: set[str]) -> list[dict]:
    """Gjør én side fra API-et om til høringsfelt. Utelatte temaer hoppes over."""
    resultat = []
    for h in data.get("hearings") or []:
        tema = [t.strip() for t in h.get("subjects") or []]
        if utelat_tema & {t.lower() for t in tema}:
            continue
        frist = h.get("deadline") or ""
        ingress = "Tema: " + ", ".join(tema) + "." if tema else ""
        if h.get("hearingNumber"):
            ingress += f" Saksnummer {h['hearingNumber']}."
        resultat.append(
            {
                "instans": INSTANS,
                "tittel": h.get("title") or "",
                "lenke": urljoin(BASE, h.get("url") or ""),
                "frist": tolk_punktumdato(frist),
                "frist_tekst": f"Høringsfrist: {frist}" if frist else "",
                "publisert": tolk_punktumdato(h.get("published") or ""),
                "ingress": ingress.strip(),
            }
        )
    return resultat


class Miljodirektoratet(Kilde):
    """Miljødirektoratets åpne høringer."""

    def hent(self) -> list[Hoering]:
        """Blar gjennom API-et til alle åpne høringer er hentet."""
        utelat = {t.lower() for t in self.konfig.get("utelat_tema", [])}
        felt: list[dict] = []
        sett = 0
        for side in range(MAKS_SIDER):
            data = self.nett.hent(API.format(skip=side * 20)).json()
            antall = len(data.get("hearings") or [])
            sett += antall
            felt += tolk(data, utelat)
            if antall == 0 or sett >= int(data.get("totalMatching") or 0):
                break
        return [self.lag_hoering(**f) for f in felt]
