"""Felles HTTP-klient: User-Agent, pauser, tidsavbrudd og robots.txt."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import requests

log = logging.getLogger(__name__)


class SperretAvRobots(Exception):
    """Adressen er sperret i nettstedets robots.txt."""


class RobotsUtilgjengelig(Exception):
    """robots.txt kunne ikke hentes (nettverksfeil eller serverfeil), så ingenting hentes."""


@dataclass
class _Regel:
    tillat: bool
    monster: re.Pattern[str]
    lengde: int


@dataclass
class Robots:
    """Enkel tolkning av robots.txt med støtte for * og $ i stier."""

    regler: list[_Regel] = field(default_factory=list)
    crawl_delay: float | None = None

    @classmethod
    def tolk(cls, tekst: str, agent: str) -> Robots:
        """Henter reglene som gjelder for agenten, ellers for «*»."""
        grupper: list[tuple[list[str], list[str]]] = []
        agenter: list[str] = []
        linjer: list[str] = []
        forrige_var_agent = False
        for rå in tekst.splitlines():
            linje = rå.split("#", 1)[0].strip()
            if ":" not in linje:
                continue
            nokkel, verdi = (d.strip() for d in linje.split(":", 1))
            nokkel = nokkel.lower()
            if nokkel == "user-agent":
                if not forrige_var_agent and agenter:
                    grupper.append((agenter, linjer))
                    agenter, linjer = [], []
                agenter.append(verdi.lower())
                forrige_var_agent = True
            else:
                linjer.append(f"{nokkel}:{verdi}")
                forrige_var_agent = False
        if agenter:
            grupper.append((agenter, linjer))

        token = agent.split("/")[0].lower()
        valgt = next((g for g in grupper if any(a != "*" and a in token for a in g[0])), None)
        if valgt is None:
            valgt = next((g for g in grupper if "*" in g[0]), None)
        robots = cls()
        if valgt is None:
            return robots
        for linje in valgt[1]:
            nokkel, verdi = linje.split(":", 1)
            if nokkel in ("allow", "disallow") and verdi:
                monster = re.escape(verdi).replace(r"\*", ".*")
                if monster.endswith(r"\$"):
                    monster = monster[:-2] + "$"
                robots.regler.append(
                    _Regel(nokkel == "allow", re.compile("^" + monster), len(verdi))
                )
            elif nokkel == "crawl-delay":
                try:
                    robots.crawl_delay = float(verdi)
                except ValueError:
                    pass
        return robots

    def tillatt(self, sti: str) -> bool:
        """Lengste treff vinner; ved likt treff vinner allow."""
        beste: _Regel | None = None
        for regel in self.regler:
            if regel.monster.match(sti):
                if (
                    beste is None
                    or regel.lengde > beste.lengde
                    or (regel.lengde == beste.lengde and regel.tillat)
                ):
                    beste = regel
        return True if beste is None else beste.tillat


class Nett:
    """HTTP-klient som alle kildene bruker."""

    def __init__(
        self,
        user_agent: str,
        pause: float = 1.0,
        tidsavbrudd: float = 30.0,
        raa_mappe: Path | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.pause = pause
        self.tidsavbrudd = tidsavbrudd
        self.raa_mappe = raa_mappe
        self.okt = requests.Session()
        self.okt.headers.update({"User-Agent": user_agent, "Accept-Language": "nb,no;q=0.9"})
        self._robots: dict[str, Robots] = {}
        self._siste_kall: dict[str, float] = {}
        self.antall_kall = 0

    def _vent(self, vert: str, robots: Robots | None) -> None:
        pause = max(self.pause, (robots.crawl_delay if robots else None) or 0)
        siste = self._siste_kall.get(vert)
        if siste is not None:
            igjen = pause - (time.monotonic() - siste)
            if igjen > 0:
                time.sleep(igjen)
        self._siste_kall[vert] = time.monotonic()

    def robots_for(self, url: str) -> Robots:
        """Henter og husker robots.txt for vertens domene."""
        deler = urlsplit(url)
        vert = deler.netloc
        if vert in self._robots:
            return self._robots[vert]
        robots_url = f"{deler.scheme}://{vert}/robots.txt"
        self._vent(vert, None)
        try:
            svar = self.okt.get(robots_url, timeout=self.tidsavbrudd)
        except requests.RequestException as feil:
            raise RobotsUtilgjengelig(f"Kunne ikke hente {robots_url}: {feil}") from feil
        self.antall_kall += 1
        if svar.status_code >= 500:
            raise RobotsUtilgjengelig(f"{robots_url} svarte {svar.status_code}")
        robots = (
            Robots.tolk(svar.text.lstrip("\ufeff"), self.user_agent)
            if svar.status_code == 200
            else Robots()
        )
        self._robots[vert] = robots
        self._lagre_raa(robots_url, svar)
        return robots

    def hent(
        self,
        url: str,
        metode: str = "GET",
        json: dict | None = None,
        headers: dict | None = None,
    ) -> requests.Response:
        """Henter en adresse etter å ha sjekket robots.txt og ventet pausen."""
        deler = urlsplit(url)
        robots = self.robots_for(url)
        sti = deler.path + (f"?{deler.query}" if deler.query else "")
        if not robots.tillatt(sti):
            raise SperretAvRobots(f"{url} er sperret i robots.txt")
        self._vent(deler.netloc, robots)
        log.info("%s %s", metode, url)
        svar = self.okt.request(metode, url, json=json, headers=headers, timeout=self.tidsavbrudd)
        self.antall_kall += 1
        self._lagre_raa(url, svar)
        svar.raise_for_status()
        return svar

    def _lagre_raa(self, url: str, svar: requests.Response) -> None:
        if not self.raa_mappe:
            return
        self.raa_mappe.mkdir(parents=True, exist_ok=True)
        navn = re.sub(r"[^A-Za-z0-9._-]+", "_", url.split("://", 1)[-1])[:150]
        (self.raa_mappe / f"{navn}.{svar.status_code}.txt").write_bytes(svar.content)
