from horinger.filer import les_json
from horinger.lager import filnavn, lagre_kilde


def test_filnavn():
    assert filnavn("Regjeringen.no") == "regjeringen-no.json"
    assert filnavn("Statsforvalteren i Innlandet") == "statsforvalteren-i-innlandet.json"
    assert (
        filnavn("Direktoratet for byggkvalitet (DiBK)") == "direktoratet-for-byggkvalitet-dibk.json"
    )
    assert filnavn("Miljødirektoratet – Høring") == "miljodirektoratet-horing.json"
    assert filnavn("Kartverket Århus") == "kartverket-arhus.json"


def test_feil_beholder_forrige_horinger(tmp_path):
    ok = {
        "kilde": "K",
        "status": "ok",
        "hentet": "2026-10-12T10:00:00+02:00",
        "horinger": [{"id": "a"}],
    }
    lagre_kilde(tmp_path, ok)
    feil = {
        "kilde": "K",
        "status": "feil",
        "hentet": "2026-10-19T10:00:00+02:00",
        "feil": "Timeout",
        "horinger": [],
    }
    lagret = lagre_kilde(tmp_path, feil)
    assert lagret["horinger"] == [{"id": "a"}]
    assert lagret["sist_ok"] == "2026-10-12T10:00:00+02:00"
    assert les_json(tmp_path / "k.json")["status"] == "feil"


def test_feil_uten_forrige(tmp_path):
    lagret = lagre_kilde(tmp_path, {"kilde": "K", "status": "feil", "hentet": "x", "horinger": []})
    assert lagret["horinger"] == [] and lagret["sist_ok"] is None


def test_filene_har_lf_og_utf8(tmp_path):
    lagre_kilde(
        tmp_path,
        {
            "kilde": "K",
            "status": "ok",
            "hentet": "x",
            "horinger": [{"tittel": "Høring – Østre Toten"}],
        },
    )
    raa = (tmp_path / "k.json").read_bytes()
    assert b"\r\n" not in raa
    assert "Høring – Østre Toten".encode() in raa
