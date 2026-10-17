import json
from datetime import date, timedelta

import requests

from horinger import kilder
from horinger.datoer import i_dag
from horinger.kilder.base import Kilde
from horinger.kjor import kjor_kilder, rydd, skriv
from horinger.modell import Hoering


class GodKilde(Kilde):
    def hent(self):
        return [
            self.lag_hoering(
                instans="Testdepartementet",
                tittel="Høring om æ, ø og å",
                lenke="https://example.no/1",
                frist=i_dag() + timedelta(days=10),
            )
        ]


class FeilendeKilde(Kilde):
    def hent(self):
        raise requests.Timeout("tidsavbrudd etter 30 sekunder")


def _konfig():
    return {
        "felles": {},
        "kilder": [
            {"navn": "Feiler", "modul": "feil", "aktiv": True},
            {"navn": "God", "modul": "god", "aktiv": True, "kategori": "Test", "prioritet": 1},
            {"navn": "Av", "modul": "god", "aktiv": False},
        ],
    }


def test_en_feil_stopper_ikke_resten(monkeypatch):
    monkeypatch.setitem(kilder.KILDER, "god", GodKilde)
    monkeypatch.setitem(kilder.KILDER, "feil", FeilendeKilde)
    horinger, status = kjor_kilder(_konfig(), nett=None)
    assert len(horinger) == 1
    per_kilde = {s["kilde"]: s for s in status}
    assert per_kilde["Feiler"]["status"] == "feil"
    assert "Timeout" in per_kilde["Feiler"]["feil"]
    assert per_kilde["God"]["status"] == "ok"
    assert per_kilde["Av"]["status"] == "ikke overvåket"


def _h(lenke, frist):
    return Hoering(
        kilde="k", kategori="", prioritet=1, instans="i", tittel=lenke, lenke=lenke, frist=frist
    )


def test_rydd_fjerner_utlopte_og_duplikater():
    i_dag_ = i_dag()
    liste = [
        _h("a", i_dag_ - timedelta(days=1)),
        _h("b", i_dag_ + timedelta(days=5)),
        _h("b", i_dag_ + timedelta(days=5)),
        _h("c", i_dag_),
        _h("d", None),
    ]
    resultat = [h.lenke for h in rydd(liste)]
    assert resultat == ["c", "b", "d"]


def test_skriv_utf8_og_iso(tmp_path):
    h = _h("https://example.no/æøå", date(2026, 11, 11))
    h.tittel = "Høring – Østre Toten"
    skriv([h], [{"kilde": "k", "status": "ok", "antall": 1}], tmp_path, antall_kall=3)
    tekst = (tmp_path / "horinger.json").read_text(encoding="utf-8")
    assert "Høring – Østre Toten" in tekst
    data = json.loads(tekst)
    assert data["horinger"][0]["frist"] == "2026-11-11"
    status = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert status["antall_kall"] == 3


def test_niva_fra_konfig_kommer_med_i_json(tmp_path):
    kilde = GodKilde({"navn": "God", "niva": "Direktorater og etater"}, nett=None)
    (h,) = kilde.hent()
    assert h.til_dict()["niva"] == "Direktorater og etater"


def test_alle_kilder_har_gyldig_niva():
    from pathlib import Path

    import yaml

    konfig = yaml.safe_load(
        (Path(__file__).parent.parent / "sources.yaml").read_text(encoding="utf-8")
    )
    gyldige = {
        "Stortinget",
        "Regjeringen",
        "Direktorater og etater",
        "Fylkeskommunen",
        "Statsforvalteren",
    }
    assert all(k.get("niva") in gyldige for k in konfig["kilder"])
