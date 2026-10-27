"""KI-sammendrag av høringene (sprint 8).

Hver høring får 1–2 setninger i klarspråk om hva som foreslås og hvem det gjelder. Grunnlaget
er avsender, tittel, ingress og teksten fra detaljsiden når den finnes (Svein 27.10.2026).
Sammendragene lagres i data/sammendrag.json med en sjekksum av grunnlaget, slik at hver høring
bare oppsummeres én gang (og på nytt bare hvis teksten endres).

Uten API-nøkkel (miljøvariabelen ANTHROPIC_API_KEY) hoppes steget over, og nettsiden viser
ingressen. En feil for én høring gir ingressen for den høringen, og resten fortsetter.
Kjøres bare i den ukentlige oppdateringen (Svein 27.10.2026), se .github/workflows/publiser.yml.

Samme kommando lager også relevansvurderingen («Hvorfor relevant for Gjøvikregionen?»),
se horinger/relevans.py.

Bruk:
    python -m horinger.sammendrag
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import time
from datetime import date, datetime
from pathlib import Path

from horinger import OSLO
from horinger.datoer import i_dag
from horinger.filer import les_json, les_konfig, skriv_json
from horinger.kilder import KILDER
from horinger.lager import les_kilde

log = logging.getLogger("horinger")

ROT = Path(__file__).resolve().parent.parent
MANGLER = "MANGLER"
# Økes når instruks eller tolking endres. Bufrede sammendrag med en annen versjon lages på nytt.
# 2: svar uten tekst (bare tenking, avbrutt av max_tokens) regnes som feil, ikke som «MANGLER».
# 3: strengere instruks om hvem høringen gjelder (to påfunn i vurderingen 27.10.2026).
VERSJON = 3


class TomtSvar(Exception):
    """Modellen ga ikke noe tekstsvar (f.eks. avbrutt av max_tokens under tenking)."""


INSTRUKS = """Du skriver korte sammendrag av offentlige høringer for kommuner i Gjøvikregionen.

Skriv på norsk bokmål i klarspråk: 1–2 setninger, høyst 45 ord.
- Si hva som foreslås eller skal vurderes. Si hvem det gjelder bare når teksten sier det
  uttrykkelig.
- Bruk bare opplysninger som står i teksten du får. Ikke gjett, ikke trekk egne slutninger, og
  ikke legg til noe. Bytt ikke ut hva høringen ber om innspill til, med hvem den gjelder.
- Ikke ta med høringsfrist, avsender eller oppfordring til å svare. Det vises for seg.
- Ikke gi vurderinger eller råd.
- Begynn rett på saken, uten «Høringen gjelder» eller «Dette er».

Gir teksten for lite å bygge på til å si hva som foreslås, svar bare: MANGLER"""


def grunnlag(h: dict) -> str:
    """Teksten modellen får for én høring."""
    deler = [
        f"Avsender: {h.get('instans', '')}",
        f"Tittel: {h.get('tittel', '')}",
    ]
    if h.get("ingress"):
        deler.append(f"Ingress: {h['ingress']}")
    if h.get("detaljtekst"):
        deler.append(f"Tekst fra høringssiden: {h['detaljtekst']}")
    return "\n".join(deler)


def sjekksum(tekst: str) -> str:
    """Kort sjekksum av grunnlaget. Endres teksten, lages sammendraget på nytt."""
    return hashlib.sha256(tekst.encode("utf-8")).hexdigest()[:16]


def rens_svar(tekst: str) -> str:
    """Svaret fra modellen: ett avsnitt, uten anførselstegn rundt. «MANGLER» blir tom tekst."""
    t = " ".join((tekst or "").split()).strip().strip("«»\"'")
    return "" if not t or t.upper().startswith(MANGLER) else t


class Sammendrag:
    """Lager og bufrer sammendrag ut fra `felles.sammendrag` i sources.yaml."""

    versjon = VERSJON

    def __init__(self, konfig: dict, klient=None) -> None:
        self.modell = konfig.get("modell", "claude-sonnet-5-5")
        self.maks_tokens = int(konfig.get("maks_tokens", 2000))
        self.pause = float(konfig.get("pause_sekunder", 0.5))
        self.maks_per_kjoring = int(konfig.get("maks_per_kjoring", 250))
        self.klient = klient

    def lag(self, h: dict) -> str:
        """Ett kall til API-et. Gir sammendraget, eller tom tekst når grunnlaget er for tynt."""
        return rens_svar(self.kall(INSTRUKS, grunnlag(h)))

    def kall(self, instruks: str, tekst: str) -> str:
        """Sender teksten til modellen og gir tekstsvaret. Svar uten tekst gir `TomtSvar`."""
        svar = self.klient.messages.create(
            model=self.modell,
            max_tokens=self.maks_tokens,
            system=instruks,
            messages=[{"role": "user", "content": tekst}],
        )
        tekst = "".join(b.text for b in svar.content if getattr(b, "type", "") == "text")
        if not tekst.strip():
            # Sonnet 5.5 tenker først (adaptiv tenking), og tenkingen teller mot max_tokens.
            # Et tomt svar er derfor en feil som prøves igjen neste uke, ikke «MANGLER».
            raise TomtSvar(f"tomt svar (stop_reason={getattr(svar, 'stop_reason', '?')})")
        return tekst

    def sjekksum(self, h: dict) -> str:
        """Sjekksum av det som avgjør svaret. Endres den, lages svaret på nytt."""
        return sjekksum(grunnlag(h))

    def felter(self, h: dict) -> dict:
        """Feltene som lagres i bufferen for én høring."""
        return {"tekst": self.lag(h)}

    def oppdater(self, horinger: list[dict], buffer: dict) -> dict:
        """Lager sammendrag for høringer som mangler eller har endret grunnlag.

        Gir tilbake oppsummering: antall nye, gjenbrukte, feil og hoppet over.
        """
        teller = {"nye": 0, "gjenbrukt": 0, "feil": 0, "uten_nokkel": 0, "utsatt": 0}
        for h in horinger:
            sum_ = self.sjekksum(h)
            lagret = buffer.get(h["id"])
            if lagret and lagret.get("sjekksum") == sum_ and lagret.get("versjon") == self.versjon:
                teller["gjenbrukt"] += 1
                continue
            if self.klient is None:
                teller["uten_nokkel"] += 1
                continue
            if teller["nye"] + teller["feil"] >= self.maks_per_kjoring:
                teller["utsatt"] += 1
                continue
            try:
                felter = self.felter(h)
            except Exception as feil:  # noqa: BLE001 – én høring skal ikke stoppe resten
                log.warning("Sammendrag for %s feilet: %s", h["id"], feil)
                teller["feil"] += 1
                continue
            buffer[h["id"]] = {
                "versjon": self.versjon,
                "sjekksum": sum_,
                **felter,
                "modell": self.modell,
                "laget": datetime.now(OSLO).replace(microsecond=0).isoformat(),
            }
            teller["nye"] += 1
            time.sleep(self.pause)
        return teller


def aktuelle_horinger(konfig: dict, kildemappe: Path, dag: date | None = None) -> list[dict]:
    """Høringene i kildefilene som ikke har utløpt frist (de som vises på siden)."""
    dag = dag or i_dag()
    resultat: list[dict] = []
    sett: set[str] = set()
    for k in konfig["kilder"]:
        if not k.get("aktiv") or k.get("modul") not in KILDER:
            continue
        for h in (les_kilde(kildemappe, k["navn"]) or {}).get("horinger", []):
            frist = h.get("frist")
            if h["id"] in sett or (frist and date.fromisoformat(frist[:10]) < dag):
                continue
            sett.add(h["id"])
            resultat.append(h)
    return resultat


def lag_klient(nokkel: str | None):
    """Anthropic-klient, eller None uten nøkkel. Nøkkelen skrives aldri til loggen."""
    if not nokkel:
        return None
    from anthropic import Anthropic  # importeres bare når nøkkelen finnes

    return Anthropic(api_key=nokkel, timeout=60.0, max_retries=2)


def kjor(
    konfig: dict, kildemappe: Path, utdata: Path, klient=None, dag: date | None = None
) -> dict:
    """Oppdaterer data/sammendrag.json. Sammendrag for høringer som er borte, slettes."""
    oppgave = Sammendrag(konfig.get("felles", {}).get("sammendrag", {}), klient)
    return kjor_oppgave(oppgave, "sammendrag", konfig, kildemappe, utdata, dag)


def kjor_oppgave(
    oppgave: Sammendrag,
    navn: str,
    konfig: dict,
    kildemappe: Path,
    utdata: Path,
    dag: date | None = None,
) -> dict:
    """Kjører én KI-oppgave over de åpne høringene og lagrer bufferen i data/<navn>.json.

    Svar for høringer som ikke lenger finnes i en kilde eller i arkivet, slettes.
    """
    sti = utdata / f"{navn}.json"
    lagret = les_json(sti) or {}
    buffer: dict = dict(lagret.get(navn, {}))
    horinger = aktuelle_horinger(konfig, kildemappe, dag)
    teller = oppgave.oppdater(horinger, buffer)
    # Behold svar for høringer som fortsatt finnes i en kilde eller i arkivet.
    arkiv = {h["id"] for h in (les_json(utdata / "arkiv.json") or {}).get("horinger", [])}
    behold = {h["id"] for h in horinger} | arkiv
    buffer = {k: v for k, v in sorted(buffer.items()) if k in behold}
    skriv_json(
        sti,
        {
            "generert": datetime.now(OSLO).replace(microsecond=0).isoformat(),
            "modell": oppgave.modell,
            navn: buffer,
        },
    )
    if oppgave.klient is None and teller["uten_nokkel"]:
        log.warning(
            "Ingen API-nøkkel (ANTHROPIC_API_KEY): %d høringer uten %s",
            teller["uten_nokkel"],
            navn,
        )
    log.info(
        "%s: %d nye, %d gjenbrukt, %d feil, %d utsatt",
        navn.capitalize(),
        teller["nye"],
        teller["gjenbrukt"],
        teller["feil"],
        teller["utsatt"],
    )
    return teller


def main(argv: list[str] | None = None) -> int:
    """Kommandolinje. Gir alltid 0: manglende sammendrag skal ikke stoppe publiseringen."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--konfig", type=Path, default=ROT / "sources.yaml")
    parser.add_argument("--utdata", type=Path, default=ROT / "data")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        klient = lag_klient(os.environ.get("ANTHROPIC_API_KEY", "").strip() or None)
        konfig = les_konfig(args.konfig)
    except Exception as feil:  # noqa: BLE001
        log.error("Sammendragene kunne ikke oppdateres: %s", feil)
        return 0
    # Relevansvurderingen (sprint 8, v2) kjøres i samme steg. Importen står her for å unngå
    # en sirkulær import (relevans bygger på klassene i denne modulen).
    from horinger.relevans import kjor as kjor_relevans

    for navn, steg in (("Sammendragene", kjor), ("Relevansvurderingene", kjor_relevans)):
        try:
            steg(konfig, args.utdata / "kilder", args.utdata, klient)
        except Exception as feil:  # noqa: BLE001 – det ene steget skal ikke stoppe det andre
            log.error("%s kunne ikke oppdateres: %s", navn, feil)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
