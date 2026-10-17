import json
from datetime import datetime, timedelta

import pytest

from horinger import OSLO
from horinger.bygg import bygg
from horinger.lager import lagre_kilde

KONFIG = {
    "kilder": [
        {"navn": "Stortinget", "modul": "stortinget", "aktiv": True},
        {"navn": "Regjeringen.no", "modul": "regjeringen", "aktiv": True, "kjoring": "pc"},
        {"navn": "Udir", "aktiv": False},
    ]
}
MANDAG = datetime(2026, 10, 19, 10, 5, tzinfo=OSLO)


def _h(id_, frist, kilde="Stortinget", tittel=None):
    return {
        "id": id_,
        "kilde": kilde,
        "tittel": tittel or f"Høring {id_}",
        "frist": frist,
        "lenke": f"https://example.no/{id_}",
    }


def _lagre(mappe, kilde, horinger, naa, status="ok"):
    lagre_kilde(
        mappe,
        {
            "kilde": kilde,
            "status": status,
            "hentet": naa.isoformat(),
            "horinger": horinger,
            **({"feil": "Timeout"} if status == "feil" else {}),
        },
    )


def _les(mappe, navn):
    return json.loads((mappe / navn).read_text(encoding="utf-8"))


@pytest.fixture
def mapper(tmp_path):
    return tmp_path / "kilder", tmp_path


def test_forste_kjoring_ingen_er_nye(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-11-01")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    data = _les(ut, "horinger.json")
    assert data["antall"] == 1
    assert data["horinger"][0]["ny"] is False
    assert data["horinger"][0]["forst_sett"] == "2026-10-19"


def test_ny_hoering_merkes_i_sju_dager(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-12-01")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    uke2 = MANDAG + timedelta(days=7)
    _lagre(kilder, "Stortinget", [_h("a", "2026-12-01"), _h("b", "2026-12-01")], uke2)
    bygg(KONFIG, kilder, ut, uke2)
    ny = {h["id"]: h["ny"] for h in _les(ut, "horinger.json")["horinger"]}
    assert ny == {"a": False, "b": True}
    uke3 = uke2 + timedelta(days=7)
    _lagre(kilder, "Stortinget", [_h("a", "2026-12-01"), _h("b", "2026-12-01")], uke3)
    bygg(KONFIG, kilder, ut, uke3)
    assert not any(h["ny"] for h in _les(ut, "horinger.json")["horinger"])
    assert _les(ut, "historikk.json")["forst_sett"]["b"] == "2026-10-26"


def test_utlopte_gaar_til_arkiv(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-10-18"), _h("b", "2026-10-19")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    assert [h["id"] for h in _les(ut, "horinger.json")["horinger"]] == ["b"]  # frist i dag
    arkiv = _les(ut, "arkiv.json")
    assert [h["id"] for h in arkiv["horinger"]] == ["a"]
    assert arkiv["horinger"][0]["utlopt"] == "2026-10-18"


def test_hoering_fjernet_fra_kilden_etter_frist_arkiveres(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-10-20")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    neste = MANDAG + timedelta(days=7)
    _lagre(kilder, "Stortinget", [], neste)  # kilden viser ikke lenger høringen
    bygg(KONFIG, kilder, ut, neste)
    assert _les(ut, "horinger.json")["antall"] == 0
    assert [h["id"] for h in _les(ut, "arkiv.json")["horinger"]] == ["a"]


def test_forlenget_frist_tas_ut_av_arkivet(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-10-18")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    _lagre(kilder, "Stortinget", [_h("a", "2026-11-18")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    assert _les(ut, "arkiv.json")["antall"] == 0
    assert _les(ut, "horinger.json")["antall"] == 1


def test_duplikater_og_sortering(mapper):
    kilder, ut = mapper
    _lagre(
        kilder, "Stortinget", [_h("b", None), _h("c", "2026-12-01"), _h("a", "2026-11-01")], MANDAG
    )
    _lagre(kilder, "Regjeringen.no", [_h("a", "2026-11-01", "Regjeringen.no")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    assert [h["id"] for h in _les(ut, "horinger.json")["horinger"]] == ["a", "c", "b"]


def test_status_per_kilde(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-11-01")], MANDAG - timedelta(days=7))
    _lagre(kilder, "Stortinget", [], MANDAG, status="feil")
    bygg(KONFIG, kilder, ut, MANDAG)
    status = {s["kilde"]: s for s in _les(ut, "status.json")["kilder"]}
    assert status["Stortinget"]["status"] == "feil"
    assert status["Stortinget"]["feil"] == "Timeout"
    assert status["Stortinget"]["antall"] == 1  # data fra forrige vellykkede henting
    assert status["Stortinget"]["sist_ok"].startswith("2026-10-12")
    assert status["Regjeringen.no"]["status"] == "ikke hentet"
    assert status["Regjeringen.no"]["kjoring"] == "pc"
    assert status["Udir"]["status"] == "ikke overvåket"


def test_utdatert_kilde(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-12-01")], MANDAG - timedelta(days=9))
    bygg(KONFIG, kilder, ut, MANDAG)
    status = {s["kilde"]: s for s in _les(ut, "status.json")["kilder"]}
    assert status["Stortinget"]["status"] == "utdatert"


def test_aeoeaa_og_lf(mapper):
    kilder, ut = mapper
    _lagre(kilder, "Stortinget", [_h("a", "2026-12-01", tittel="Høring om ærfugl på Åsen")], MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)
    for navn in ("horinger.json", "status.json", "arkiv.json", "historikk.json"):
        raa = (ut / navn).read_bytes()
        assert b"\r\n" not in raa
    assert "Høring om ærfugl på Åsen" in (ut / "horinger.json").read_text(encoding="utf-8")


def test_gamle_hoeringer_fra_for_start_tas_ikke_med(mapper):
    kilder, ut = mapper
    gamle = [
        _h("eldgammel", "2019-03-01"),
        _h("grense", "2026-09-19"),
        _h("for-gammel", "2026-09-18"),
    ]
    _lagre(kilder, "Stortinget", gamle, MANDAG)
    bygg(KONFIG, kilder, ut, MANDAG)  # historikken starter 19. oktober
    assert [h["id"] for h in _les(ut, "arkiv.json")["horinger"]] == ["grense"]
    assert set(_les(ut, "historikk.json")["forst_sett"]) == {"grense"}
