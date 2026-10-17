import json
from datetime import timedelta

import requests
import yaml

from horinger import kilder
from horinger.datoer import i_dag
from horinger.kilder.base import Kilde
from horinger.kjor import kjor_kilder, main, velg_kilder


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
    resultater = kjor_kilder(_konfig(), nett=None)
    per_kilde = {r["kilde"]: r for r in resultater}
    assert set(per_kilde) == {"Feiler", "God"}  # inaktive kilder hentes ikke
    assert per_kilde["Feiler"]["status"] == "feil"
    assert "Timeout" in per_kilde["Feiler"]["feil"]
    assert per_kilde["God"]["status"] == "ok"
    assert per_kilde["God"]["horinger"][0]["tittel"] == "Høring om æ, ø og å"


def test_simulert_feil(monkeypatch):
    monkeypatch.setitem(kilder.KILDER, "god", GodKilde)
    monkeypatch.setitem(kilder.KILDER, "feil", FeilendeKilde)
    resultater = kjor_kilder(_konfig(), nett=None, utvalg=["God"], simuler_feil="God")
    assert resultater[0]["status"] == "feil"
    assert "SimulertFeil" in resultater[0]["feil"]


def test_velg_kilder_etter_maskin():
    konfig = {
        "kilder": [
            {"navn": "A", "modul": "stortinget", "aktiv": True},
            {"navn": "B", "modul": "regjeringen", "aktiv": True, "kjoring": "pc"},
        ]
    }
    assert [k["navn"] for k in velg_kilder(konfig, maskin="github")] == ["A"]
    assert [k["navn"] for k in velg_kilder(konfig, maskin="pc")] == ["B"]
    assert [k["navn"] for k in velg_kilder(konfig, maskin="alle")] == ["A", "B"]


def test_main_skriver_kildefil_og_bygger(monkeypatch, tmp_path):
    monkeypatch.setitem(kilder.KILDER, "god", GodKilde)
    monkeypatch.setitem(kilder.KILDER, "feil", FeilendeKilde)
    konfig = tmp_path / "k.yaml"
    konfig.write_text(
        yaml.safe_dump({**_konfig(), "felles": {"user_agent": "test", "pause_sekunder": 0}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("HORINGER_SIMULER_FEIL", "")
    assert main(["--konfig", str(konfig), "--utdata", str(tmp_path)]) == 0
    god = json.loads((tmp_path / "kilder" / "god.json").read_text(encoding="utf-8"))
    assert god["status"] == "ok" and god["sist_ok"] == god["hentet"]
    assert (tmp_path / "kilder" / "feiler.json").is_file()
    data = json.loads((tmp_path / "horinger.json").read_text(encoding="utf-8"))
    assert data["antall"] == 1
    status = {s["kilde"]: s for s in json.loads((tmp_path / "status.json").read_text())["kilder"]}
    assert status["Feiler"]["status"] == "feil"
    assert status["God"]["antall"] == 1


def test_main_bare_kilder_bygger_ikke(monkeypatch, tmp_path):
    monkeypatch.setitem(kilder.KILDER, "god", GodKilde)
    monkeypatch.setitem(kilder.KILDER, "feil", FeilendeKilde)
    konfig = tmp_path / "k.yaml"
    konfig.write_text(
        yaml.safe_dump({**_konfig(), "felles": {"user_agent": "test", "pause_sekunder": 0}}),
        encoding="utf-8",
    )
    main(["--konfig", str(konfig), "--utdata", str(tmp_path), "--bare-kilder"])
    assert (tmp_path / "kilder" / "god.json").is_file()
    assert not (tmp_path / "horinger.json").exists()


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
