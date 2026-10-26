"""Gjøvik kommunes postliste (sprint 7): inngående høringsbrev de siste 14 dagene.

Postlistesiden bruker ACOS «nye-innsyn», som henter treffene som JSON fra
`POST /api/presentation/v2/nye-innsyn/overview` (kildekartleggingen, avsnitt 9 og 13, godkjent
i sprint 0). Innhentingen søker på hvert søkeord med filter på inngående dokumenter, nyeste
først, og blar til den møter journalposter som er eldre enn vinduet.

Personvern (Svein 26.10.2026): bare treff på søkeordene lagres, og avsender lagres bare når
det er en virksomhet. Postlister for flere kommuner kan legges til i `postlister` i
sources.yaml. Hver kommune lagres i data/kilder/postliste-<kommune>.json.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from horinger import OSLO
from horinger.datoer import i_dag
from horinger.filer import les_json, skriv_json
from horinger.lager import filnavn
from horinger.nett import Nett
from horinger.sokeord import Sokeord

log = logging.getLogger("horinger")

API = "/api/presentation/v2/nye-innsyn/overview"
MAKS_SIDER = 10  # per søkeord. 10 treff per side, nyeste først


def _dato(tekst: str) -> date | None:
    """«21.10.2026» → date."""
    m = re.fullmatch(r"\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*", tekst or "")
    return date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


class Postliste:
    """Henter inngående høringsbrev fra én kommunes postliste.

    `konfig` er kommunens oppføring under `postlister` i sources.yaml, og `felles` er
    `felles.postliste` (søkeord, ord som utelukker, ord som kjennetegner virksomheter).
    """

    def __init__(self, konfig: dict, nett: Nett, felles: dict) -> None:
        self.konfig = konfig
        self.nett = nett
        self.sokeord = list(felles.get("sokeord", []))
        self.filter = Sokeord(self.sokeord)
        self.utelat = [o.casefold() for o in felles.get("utelat_ord", [])]
        ord_ = felles.get("virksomhet_ord", [])
        # Lange ord kan stå inne i sammensatte ord («Omsorgsdepartementet»). Korte ord og
        # forkortelser («AS», «lag», «KS») må stå som hele ord.
        lange = [re.escape(o) for o in ord_ if len(o) >= 5]
        korte = [re.escape(o) for o in ord_ if len(o) < 5]
        deler = []
        if lange:
            deler.append("(?:" + "|".join(lange) + ")")
        if korte:
            deler.append(r"(?<![\wæøå])(?:" + "|".join(korte) + r")(?![\wæøå])")
        self.virksomhet = re.compile("|".join(deler), re.IGNORECASE) if deler else None
        self.vindu = int(felles.get("vindu_dager", 14))

    @property
    def navn(self) -> str:
        """Visningsnavn, f.eks. «Gjøvik kommunes postliste»."""
        return self.konfig["navn"]

    def _foresporsel(self, sokeord: str, side: int) -> dict:
        return {
            "type": 0,
            "keyValues": [
                {"key": "searchTerm", "value": sokeord},
                {"key": "Type", "value": self.konfig["dokumenttype_inngaaende"]},
                {"key": "page", "value": str(side)},
            ],
        }

    def _hoder(self) -> dict:
        # Endepunktet svarer bare når forespørselen ser ut som den postlistesiden selv sender
        # (avbrutt svar uten Origin og Referer, utforsket 26.10.2026).
        base = self.konfig["base"]
        return {
            "Accept": "application/json, text/plain, */*",
            "DeviceType": "desktop",
            "X-ANTI-CSRF": "1",
            "Origin": base,
            "Referer": base + self.konfig["side"],
        }

    def lenke(self, post: dict) -> str:
        """Lenke til journalposten på postlistesiden."""
        return (
            f"{self.konfig['base']}{self.konfig['side']}#/details/"
            f"{post['parentIdentifier']}/{post['identifier']}"
        )

    def er_svar(self, tittel: str) -> bool:
        """Om tittelen er et svar eller innspill til en høring, ikke et høringsbrev.

        Ordene i `utelat_ord` må stå først i tittelen (etter «Kopi -»), slik at «Høring – … frist
        for høringssvar» fortsatt tas med, mens «Kopi - Høringssvar - …» og «Innspill til varsel
        om oppstart …» utelates.
        """
        start = re.sub(r"^\s*(?:kopi|vs|sv|re)\s*[-:–]\s*", "", tittel.casefold())
        return any(start.startswith(o) for o in self.utelat)

    def er_virksomhet(self, avsender: str) -> bool:
        """Om avsenderen ser ut som en virksomhet (kommune, departement, AS …)."""
        return bool(self.virksomhet and avsender and self.virksomhet.search(avsender))

    def tolk(self, post: dict, grense: date) -> dict | None:
        """Gjør ett treff om til en journalpost, eller None når det ikke skal tas med."""
        egenskaper = post.get("properties") or {}
        dato = _dato(egenskaper.get("dato", ""))
        tittel = " ".join((post.get("title") or "").split())
        if dato is None or dato < grense or not tittel:
            return None
        if post.get("type") != "Inngående dokument" or not self.filter.treff(tittel):
            return None
        if self.er_svar(tittel):
            return None
        avsender = " ".join((egenskaper.get("avsender") or "").split())
        return {
            "id": post["identifier"],
            "kommune": self.konfig["kommune"],
            "dokument_id": egenskaper.get("dokumentID", ""),
            "dato": dato.isoformat(),
            "tittel": tittel,
            # Personvern: privatpersoner lagres ikke med navn (Svein 26.10.2026).
            "avsender": avsender if self.er_virksomhet(avsender) else "",
            "lenke": self.lenke(post),
        }

    def hent(self, dag: date | None = None) -> list[dict]:
        """Inngående høringsbrev i vinduet, uten duplikater, nyeste først."""
        grense = (dag or i_dag()) - timedelta(days=self.vindu)
        url = self.konfig["base"] + API
        # Endepunktet avbryter svaret uten informasjonskapslene som postlistesiden setter.
        # Siden hentes derfor først, slik nettleseren gjør (utforsket 26.10.2026).
        self.nett.hent(self.konfig["base"] + self.konfig["side"])
        funnet: dict[str, dict] = {}
        for sokeord in self.sokeord:
            for side in range(1, MAKS_SIDER + 1):
                svar = self.nett.hent(
                    url, metode="POST", json=self._foresporsel(sokeord, side), headers=self._hoder()
                ).json()
                treff = (svar.get("content") or {}).get("searchItems") or {}
                poster = treff.get("items") or []
                for post in poster:
                    if (jp := self.tolk(post, grense)) and jp["id"] not in funnet:
                        funnet[jp["id"]] = jp
                eldste = min(
                    (
                        d
                        for p in poster
                        if (d := _dato((p.get("properties") or {}).get("dato", "")))
                    ),
                    default=None,
                )
                if not treff.get("hasNextPage") or eldste is None or eldste < grense:
                    break
        return sorted(funnet.values(), key=lambda j: (j["dato"], j["id"]), reverse=True)


def postlistefil(mappe: Path, navn: str) -> Path:
    """Filen for én postliste i data/kilder/."""
    return mappe / filnavn(navn)


def hent_postliste(konfig: dict, nett: Nett, felles: dict, simuler_feil: str | None = None) -> dict:
    """Henter én postliste. En feil fanges og gis tilbake som status, som for kildene."""
    start = time.monotonic()
    hentet = datetime.now(OSLO).replace(microsecond=0).isoformat()
    navn = konfig["navn"]
    try:
        if simuler_feil and simuler_feil == navn:
            raise RuntimeError(f"Simulert feil for {navn} (HORINGER_SIMULER_FEIL)")
        poster = Postliste(konfig, nett, felles).hent()
        log.info("%s: %d inngående høringsbrev", navn, len(poster))
        return {
            "kilde": navn,
            "status": "ok",
            "hentet": hentet,
            "antall": len(poster),
            "sekunder": round(time.monotonic() - start, 1),
            "journalposter": poster,
        }
    except Exception as feil:  # noqa: BLE001 – postlista skal aldri stoppe resten
        log.error("%s feilet: %s", navn, feil)
        return {
            "kilde": navn,
            "status": "feil",
            "hentet": hentet,
            "antall": 0,
            "feil": f"{type(feil).__name__}: {feil}",
            "sekunder": round(time.monotonic() - start, 1),
            "journalposter": [],
        }


def lagre_postliste(mappe: Path, resultat: dict) -> dict:
    """Lagrer resultatet. Ved feil beholdes journalpostene og `sist_ok` fra forrige gang."""
    resultat = dict(resultat)
    sti = postlistefil(mappe, resultat["kilde"])
    forrige = les_json(sti) or {}
    if resultat["status"] == "ok":
        resultat["sist_ok"] = resultat["hentet"]
    else:
        resultat["journalposter"] = forrige.get("journalposter", [])
        resultat["sist_ok"] = forrige.get("sist_ok")
    skriv_json(sti, resultat)
    return resultat
