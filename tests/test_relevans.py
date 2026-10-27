"""Tester av relevansvurderingen (sprint 8 v2). API-et er erstattet med en falsk klient."""

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from horinger import relevans as rv
from horinger import sammendrag as sm
from horinger.bygg import bygg
from horinger.filer import les_json
from horinger.lager import lagre_kilde

ROT = Path(__file__).parent.parent
KONFIG = yaml.safe_load((ROT / "sources.yaml").read_text("utf-8"))
REGJ = next(k for k in KONFIG["kilder"] if k["navn"] == "Regjeringen.no")
DAG = date(2026, 10, 27)
IKKE = '{"relevant": false, "hvorfor": "Gjelder bare kysten i Nord-Norge."}'
JA = '{"relevant": true, "hvorfor": "Kommunene må planlegge tilfluktsrom."}'


class _Klient:
    """Svarer ut fra tittelen: titler med «kystruten» er ikke relevante."""

    def __init__(self, feil=()):
        self.kall: list[dict] = []
        self.feil = set(feil)
        self.messages = SimpleNamespace(create=self.create)

    def create(self, **kw):
        self.kall.append(kw)
        tekst = kw["messages"][0]["content"]
        if any(f in tekst for f in self.feil):
            raise TimeoutError("tidsavbrudd")
        svar = IKKE if "kystruten" in tekst else JA
        if kw["system"] == sm.INSTRUKS:
            svar = "Et sammendrag."
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=svar)])


def _h(id_, tittel="Høring av forskrift om tilfluktssteder", **ekstra):
    return {
        "id": id_,
        "kilde": "Regjeringen.no",
        "instans": "Justis- og beredskapsdepartementet",
        "tittel": tittel,
        "lenke": f"https://www.regjeringen.no/{id_}",
        "frist": "2026-12-01",
        "ingress": "Forslag til forskrift.",
        **ekstra,
    }


def _kilde(tmp_path, horinger):
    mappe = tmp_path / "kilder"
    lagre_kilde(
        mappe,
        {
            "kilde": "Regjeringen.no",
            "status": "ok",
            "hentet": "2026-10-27T10:00:00+01:00",
            "horinger": horinger,
        },
    )
    return mappe


def _konfig():
    k = {**KONFIG, "kilder": [REGJ]}
    k["felles"] = {
        **KONFIG["felles"],
        "sammendrag": {**KONFIG["felles"]["sammendrag"], "pause_sekunder": 0},
    }
    return k


def test_instruksen_har_region_og_svein_sine_eksempler():
    tekst = rv.instruks(KONFIG["felles"]["relevans"])
    assert "Gjøvik, Østre Toten, Vestre Toten, Søndre Land og Nordre Land" in tekst
    for eksempel in ("kystruten Bergen–Kirkenes", "skip", "Svalbard", "fiskeflåten", "Nord-Norge"):
        assert eksempel in tekst
    assert '{"relevant": true eller false, "hvorfor": "..."}' in tekst


def test_tolk_svar():
    assert rv.tolk_svar(IKKE) == {"relevant": False, "hvorfor": "Gjelder bare kysten i Nord-Norge."}
    # Tekst rundt JSON-en og linjeskift tåles.
    assert rv.tolk_svar('Svar:\n```json\n{"relevant": true,\n "hvorfor": " A\\nB "}\n```') == {
        "relevant": True,
        "hvorfor": "A B",
    }
    assert rv.tolk_svar('{"relevant": true}')["hvorfor"] == ""
    for ugyldig in ("ja", '{"relevant": "ja", "hvorfor": ""}', '{"hvorfor": "x"}'):
        with pytest.raises(ValueError):
            rv.tolk_svar(ugyldig)


def test_vurderer_og_bufrer(tmp_path):
    mappe = _kilde(tmp_path, [_h("a"), _h("b", tittel="Ny ruteplan for kystruten")])
    klient = _Klient()
    teller = rv.kjor(_konfig(), mappe, tmp_path, klient, DAG)
    assert teller["nye"] == 2
    data = les_json(tmp_path / "relevans.json")["relevans"]
    assert data["a"]["relevant"] is True
    assert data["a"]["hvorfor"] == "Kommunene må planlegge tilfluktsrom."
    assert data["b"] == {**data["b"], "relevant": False, "versjon": rv.VERSJON}
    assert klient.kall[0]["system"] == rv.instruks(KONFIG["felles"]["relevans"])
    assert klient.kall[0]["model"] == KONFIG["felles"]["sammendrag"]["modell"]
    # Andre kjøring bruker bufferen.
    assert rv.kjor(_konfig(), mappe, tmp_path, klient, DAG)["gjenbrukt"] == 2
    assert len(klient.kall) == 2


def test_nye_eksempler_gir_ny_vurdering(tmp_path):
    mappe = _kilde(tmp_path, [_h("a")])
    rv.kjor(_konfig(), mappe, tmp_path, _Klient(), DAG)
    konfig = _konfig()
    konfig["felles"]["relevans"] = {
        **konfig["felles"]["relevans"],
        "ikke_relevant_eksempler": ["Noe helt annet"],
    }
    assert rv.kjor(konfig, mappe, tmp_path, _Klient(), DAG)["nye"] == 1


def test_ugyldig_svar_er_feil_og_prøves_igjen(tmp_path):
    class _Rot(_Klient):
        def create(self, **kw):
            return SimpleNamespace(content=[SimpleNamespace(type="text", text="Kanskje.")])

    teller = rv.kjor(_konfig(), _kilde(tmp_path, [_h("a")]), tmp_path, _Rot(), DAG)
    assert teller["feil"] == 1
    assert les_json(tmp_path / "relevans.json")["relevans"] == {}


def test_uten_nokkel_feiler_ikke(tmp_path):
    teller = rv.kjor(_konfig(), _kilde(tmp_path, [_h("a")]), tmp_path, None, DAG)
    assert teller["uten_nokkel"] == 1


@pytest.mark.parametrize(
    ("ekstra", "relevant"),
    [
        ({}, False),
        ({"regionflagg": ["Alle kommuner"]}, True),
        ({"postliste": [{"niva": "mulig"}]}, True),
        ({"niva": "Fylkeskommunen"}, True),
        ({"niva": "Statsforvalteren"}, True),
        ({"niva": "Regjeringen"}, False),
    ],
)
def test_vern_mot_aa_utelate(ekstra, relevant):
    svar = {"relevant": False, "hvorfor": "Gjelder bare Svalbard."}
    resultat = rv.vurder(_h("a", **ekstra), svar, KONFIG["felles"]["relevans"])
    assert resultat["relevant"] is relevant
    # Når høringen vises likevel, vises ikke begrunnelsen for å utelate den.
    assert resultat["hvorfor_relevant"] == ("" if relevant else "Gjelder bare Svalbard.")


def test_uten_vurdering_er_hoeringen_med():
    assert rv.vurder(_h("a"), None, {}) == {"relevant": True, "hvorfor_relevant": ""}


def test_bygg_legger_inn_relevans(tmp_path):
    mappe = _kilde(tmp_path, [_h("a"), _h("b", tittel="Ny ruteplan for kystruten")])
    rv.kjor(_konfig(), mappe, tmp_path, _Klient(), DAG)
    bygg(_konfig(), mappe, tmp_path)
    hs = {h["id"]: h for h in les_json(tmp_path / "horinger.json")["horinger"]}
    assert hs["a"]["relevant"] is True
    assert hs["a"]["hvorfor_relevant"] == "Kommunene må planlegge tilfluktsrom."
    assert hs["b"]["relevant"] is False
    assert hs["b"]["hvorfor_relevant"] == "Gjelder bare kysten i Nord-Norge."


def test_main_lager_begge_og_det_ene_stopper_ikke_det_andre(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-hemmelig-test")
    monkeypatch.setattr(sm, "lag_klient", lambda nokkel: _Klient())
    _kilde(tmp_path, [_h("a")])
    monkeypatch.setattr(sm, "kjor", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("brudd")))
    assert sm.main(["--utdata", str(tmp_path)]) == 0
    assert "Sammendragene kunne ikke oppdateres: brudd" in caplog.text
    assert les_json(tmp_path / "relevans.json")["relevans"]["a"]["relevant"] is True
    assert "sk-ant-hemmelig-test" not in caplog.text
