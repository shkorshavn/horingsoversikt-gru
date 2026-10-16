import json
from datetime import date
from pathlib import Path

import pytest

from horinger.kilder.stortinget import Stortinget, neste_sesjon, sesjon_for, tolk_horing

FIXTURES = Path(__file__).parent / "fixtures"
KONFIG = {"navn": "Stortinget", "kategori": "Regjeringen og Stortinget", "prioritet": 1}


@pytest.mark.parametrize(
    "dato, forventet",
    [
        (date(2026, 9, 30), "2025-2026"),
        (date(2026, 10, 1), "2026-2027"),
        (date(2026, 12, 31), "2026-2027"),
        (date(2027, 1, 1), "2026-2027"),
        (date(2027, 9, 30), "2026-2027"),
    ],
)
def test_sesjon_for(dato, forventet):
    assert sesjon_for(dato) == forventet


def test_spor_naa_og_neste_sesjon():
    k = Stortinget(KONFIG, nett=None)
    assert k.sesjoner(date(2026, 9, 30)) == ["2025-2026", "2026-2027"]
    assert k.sesjoner(date(2026, 10, 1)) == ["2026-2027", "2027-2028"]
    assert neste_sesjon("2026-2027") == "2027-2028"


def _data():
    return json.loads((FIXTURES / "stortinget_2026-2027.json").read_text(encoding="utf-8"))


def test_tolker_ekte_svar():
    horinger = Stortinget(KONFIG, nett=None).tolk(_data())
    assert len(horinger) > 0
    for h in horinger:
        assert h.instans.startswith("Stortinget")
        assert h.lenke.startswith("https://www.stortinget.no/")
        assert h.tittel


def test_skriftlig_horing_bruker_innspillsfrist():
    rad = next(r for r in _data()["horinger_liste"] if r["id"] == 10005899)
    felter = tolk_horing(rad)
    assert felter["tittel"] == (
        "Representantforslag om en tydelig og forpliktende integreringskontrakt"
    )
    assert felter["instans"] == "Stortinget, Kommunal- og forvaltningskomiteen"
    assert felter["frist"] == date(2026, 10, 7)
    assert felter["frist_tekst"] == "Frist for skriftlig innspill: 07.10.2026 kl. 23:59"
    assert felter["lenke"].endswith("?h=10005899")


def test_muntlig_horing_bruker_pameldingsfrist():
    # Stortingets side for høring 10005977 viser bare «Frist for å søke» 26.10.2026 kl. 13.00
    rad = next(r for r in _data()["horinger_liste"] if r["id"] == 10005977)
    felter = tolk_horing(rad)
    assert felter["instans"] == "Stortinget, Næringskomiteen"
    assert felter["frist"] == date(2026, 10, 26)
    assert felter["frist_tekst"] == "Frist for å søke om å delta: 26.10.2026 kl. 13:00"
    assert felter["ingress"].startswith("Muntlig høring 04.11.2026.")


def test_muntlig_horing_uten_frister_bruker_hoeringsdagen():
    rad = next(r for r in _data()["horinger_liste"] if r["id"] == 10005976)
    felter = tolk_horing(rad)
    assert felter["frist"] == date(2026, 11, 13)
    assert felter["frist_tekst"].startswith("Ingen frist oppgitt.")


def test_avlyst_horing_tas_ikke_med():
    rad = dict(_data()["horinger_liste"][0], horing_status="Avlyst")
    assert tolk_horing(rad) is None


class _ProgramNett:
    def __init__(self, program):
        self.program = program
        self.kall = []

    def hent(self, url, **_):
        self.kall.append(url)
        program = self.program

        class Svar:
            def json(self):
                return program

        return Svar()


def test_kontrollhoring_bruker_programtittel_nar_den_finnes():
    nett = _ProgramNett(
        {"horingsprogram_liste": [{"tittel": "Høring om: Oppfølging av rammeavtaler"}]}
    )
    horinger = Stortinget(KONFIG, nett).tolk(_data(), hent_program=True)
    kontroll = next(h for h in horinger if h.lenke.endswith("?h=10005976"))
    assert kontroll.tittel == "Høring om: Oppfølging av rammeavtaler"
    assert kontroll.ingress.startswith("Kontrollhøring.")
    assert len(nett.kall) == 2  # bare de to kontrollhøringene


def test_kontrollhoring_uten_program_beholder_sakstittel():
    nett = _ProgramNett({"horingsprogram_liste": []})
    horinger = Stortinget(KONFIG, nett).tolk(_data(), hent_program=True)
    kontroll = next(h for h in horinger if h.lenke.endswith("?h=10005976"))
    assert kontroll.tittel.startswith("Redegjørelse av forsvarsministeren")
