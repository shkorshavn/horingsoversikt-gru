from datetime import date
from pathlib import Path

from horinger.kilder.regjeringen import Regjeringen, er_apen, tolk_side, velg

FIXTURES = Path(__file__).parent / "fixtures"
BASE = "https://www.regjeringen.no/no/dokument/hoyringar/id1763/"
EKSKLUDER = {"Energidepartementet", "Barne- og familiedepartementet", "Utenriksdepartementet"}


def _rader():
    return tolk_side((FIXTURES / "regjeringen_utvalg.html").read_text(encoding="utf-8"), BASE)


def test_side_tolkes():
    rader = _rader()
    assert len(rader) == 6
    kd = rader[4]
    assert kd["instans"] == "Kunnskapsdepartementet"
    assert kd["tittel"].startswith("Forslag til endringer i opplæringsloven og privatskoleloven")
    assert kd["lenke"] == (
        "https://www.regjeringen.no/no/dokumenter/horing-forslag-til-endringer-i-"
        "opplaringsloven-og-privatskolen-smagruppeundervisning-og-leksehjelp/id3170886/"
    )
    assert kd["frist"] == date(2027, 1, 7)
    assert kd["publisert"] == date(2026, 10, 7)
    assert kd["frist_tekst"] == "Høringsfrist: 07.01.2027"


def test_nynorsk_frist_og_status():
    nn = _rader()[1]
    assert nn["frist"] == date(2026, 11, 30)
    assert er_apen(nn["status"])


def test_velg_fjerner_lukkede_og_ekskluderte_departementer():
    valgt = velg(_rader(), EKSKLUDER)
    assert [r["instans"] for r in valgt] == [
        "Finansdepartementet",
        "Finansdepartementet",
        "Kunnskapsdepartementet",
    ]
    assert all("status" not in r for r in valgt)


def test_blar_til_to_sider_uten_apne():
    apen = (FIXTURES / "regjeringen_utvalg.html").read_text(encoding="utf-8")
    lukket = """<ul class="listing"><li><h2><a href="/no/dokumenter/x/id1/">X</a></h2>
      <div class="info"><span class="date">01.02.2026</span>
      <span class="department">Finansdepartementet</span></div>
      <p class="event-details"><span>Høringsfrist: 01.03.2026</span>
      <span>Status: Ferdigbehandlet</span></p></li></ul>"""
    sider = {1: apen, 2: lukket, 3: apen, 4: lukket, 5: lukket, 6: apen}

    class Nett:
        def __init__(self):
            self.sider = []

        def hent(self, url, **_):
            nr = int(url.rsplit("=", 1)[1])
            self.sider.append(nr)

            class Svar:
                text = sider.get(nr, "")

            return Svar()

    nett = Nett()
    kilde = Regjeringen(
        {"navn": "Regjeringen.no", "url": BASE},
        nett,
        {"ekskluder_departementer": sorted(EKSKLUDER)},
    )
    horinger = kilde.hent()
    assert nett.sider == [1, 2, 3, 4, 5]
    assert len(horinger) == 6  # 3 per side med åpne høringer, side 1 og 3
