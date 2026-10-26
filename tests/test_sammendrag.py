"""Tester av KI-sammendragene (sprint 8). API-et er erstattet med en falsk klient."""

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import yaml

from horinger import sammendrag as sm
from horinger.bygg import bygg
from horinger.filer import les_json
from horinger.lager import lagre_kilde

ROT = Path(__file__).parent.parent
KONFIG = yaml.safe_load((ROT / "sources.yaml").read_text("utf-8"))
REGJ = next(k for k in KONFIG["kilder"] if k["navn"] == "Regjeringen.no")
DAG = date(2026, 10, 27)


class _Klient:
    """Gir faste svar. `feil` er id-er (via tittelen) som skal gi unntak."""

    def __init__(self, svar="Endringer i tilfluktsforskriften for kommunene.", feil=()):
        self.kall: list[dict] = []
        self.svar = svar
        self.feil = set(feil)
        self.messages = SimpleNamespace(create=self.create)

    def create(self, **kw):
        self.kall.append(kw)
        if any(f in kw["messages"][0]["content"] for f in self.feil):
            raise TimeoutError("tidsavbrudd")
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.svar)])


def _h(id_, tittel="Høring av forskrift om tilfluktssteder", frist="2026-12-01", **ekstra):
    return {
        "id": id_,
        "kilde": "Regjeringen.no",
        "instans": "Justis- og beredskapsdepartementet",
        "tittel": tittel,
        "lenke": f"https://www.regjeringen.no/{id_}",
        "frist": frist,
        "ingress": "Departementet sender på høring forslag til forskrift om tilfluktssteder.",
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


def test_lager_og_bufrer_sammendrag(tmp_path):
    mappe = _kilde(tmp_path, [_h("a", detaljtekst="Forslaget gjelder kommunenes ansvar.")])
    klient = _Klient()
    teller = sm.kjor(_konfig(), mappe, tmp_path, klient, DAG)
    assert teller["nye"] == 1
    kall = klient.kall[0]
    assert kall["model"] == "claude-sonnet-5-5"
    assert kall["max_tokens"] == 200
    assert "Bruk bare opplysninger som står i teksten" in kall["system"]
    innhold = kall["messages"][0]["content"]
    assert "Tittel: Høring av forskrift om tilfluktssteder" in innhold
    assert "Tekst fra høringssiden: Forslaget gjelder kommunenes ansvar." in innhold
    lagret = les_json(tmp_path / "sammendrag.json")["sammendrag"]["a"]
    assert lagret["tekst"] == "Endringer i tilfluktsforskriften for kommunene."
    assert lagret["modell"] == "claude-sonnet-5-5"
    # Neste kjøring: samme grunnlag gir ingen nye kall.
    teller = sm.kjor(_konfig(), mappe, tmp_path, klient, DAG)
    assert teller == {"nye": 0, "gjenbrukt": 1, "feil": 0, "uten_nokkel": 0, "utsatt": 0}
    assert len(klient.kall) == 1


def test_endret_tekst_gir_nytt_sammendrag(tmp_path):
    klient = _Klient()
    sm.kjor(_konfig(), _kilde(tmp_path, [_h("a")]), tmp_path, klient, DAG)
    mappe = _kilde(tmp_path, [_h("a", ingress="Ny ingress etter endring.")])
    assert sm.kjor(_konfig(), mappe, tmp_path, klient, DAG)["nye"] == 1


def test_uten_nokkel_feiler_ikke(tmp_path):
    teller = sm.kjor(_konfig(), _kilde(tmp_path, [_h("a")]), tmp_path, None, DAG)
    assert teller["uten_nokkel"] == 1 and teller["nye"] == 0
    assert les_json(tmp_path / "sammendrag.json")["sammendrag"] == {}


def test_main_uten_nokkel_gir_0(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    (tmp_path / "kilder").mkdir()
    assert sm.main(["--utdata", str(tmp_path)]) == 0


def test_feil_for_en_hoering_stopper_ikke_resten(tmp_path):
    mappe = _kilde(tmp_path, [_h("a", tittel="Feiler"), _h("b")])
    teller = sm.kjor(_konfig(), mappe, tmp_path, _Klient(feil={"Feiler"}), DAG)
    assert teller["feil"] == 1 and teller["nye"] == 1
    assert set(les_json(tmp_path / "sammendrag.json")["sammendrag"]) == {"b"}


def test_mangler_gir_ingressen(tmp_path):
    sm.kjor(_konfig(), _kilde(tmp_path, [_h("a")]), tmp_path, _Klient(svar="MANGLER"), DAG)
    assert les_json(tmp_path / "sammendrag.json")["sammendrag"]["a"]["tekst"] == ""


def test_utlopte_hoeringer_oppsummeres_ikke_og_borte_slettes(tmp_path):
    klient = _Klient()
    sm.kjor(
        _konfig(),
        _kilde(tmp_path, [_h("a"), _h("gammel", frist="2026-10-01")]),
        tmp_path,
        klient,
        DAG,
    )
    assert len(klient.kall) == 1
    sm.kjor(_konfig(), _kilde(tmp_path, [_h("b")]), tmp_path, klient, DAG)
    assert set(les_json(tmp_path / "sammendrag.json")["sammendrag"]) == {"b"}


def test_rens_svar():
    assert sm.rens_svar(" «Forslag om nye regler.» ") == "Forslag om nye regler."
    assert sm.rens_svar("MANGLER") == ""
    assert sm.rens_svar("Mangler.") == ""
    assert sm.rens_svar("To\nlinjer.") == "To linjer."


def test_maks_per_kjoring(tmp_path):
    konfig = _konfig()
    konfig["felles"]["sammendrag"]["maks_per_kjoring"] = 2
    mappe = _kilde(tmp_path, [_h(x) for x in "abc"])
    teller = sm.kjor(konfig, mappe, tmp_path, _Klient(), DAG)
    assert teller["nye"] == 2 and teller["utsatt"] == 1


def test_bygg_legger_inn_sammendrag_og_skjuler_detaljteksten(tmp_path):
    mappe = _kilde(tmp_path, [_h("a", detaljtekst="Lang tekst fra siden."), _h("b")])
    sm.kjor(_konfig(), mappe, tmp_path, _Klient(), DAG)
    bygg(_konfig(), mappe, tmp_path)
    hs = {h["id"]: h for h in les_json(tmp_path / "horinger.json")["horinger"]}
    assert hs["a"]["sammendrag"] == "Endringer i tilfluktsforskriften for kommunene."
    assert "detaljtekst" not in hs["a"]
    tekst = (tmp_path / "horinger.json").read_text("utf-8")
    assert "Lang tekst fra siden." not in tekst


def test_nokkelen_skrives_aldri_til_loggen(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-hemmelig-test")
    monkeypatch.setattr(sm, "lag_klient", lambda nokkel: _Klient(feil={"tilfluktssteder"}))
    _kilde(tmp_path, [_h("a")])
    sm.main(["--utdata", str(tmp_path)])
    assert "sk-ant-hemmelig-test" not in caplog.text


def test_detaljteksten_lagres_fra_siden():
    from bs4 import BeautifulSoup

    from horinger.kilder.base import sidetekst

    html = (ROT / "tests/fixtures/horingsparter/regj_tilfluktssteder.html").read_text("utf-8")
    tekst = sidetekst(BeautifulSoup(html, "html.parser"))
    assert "tilfluktssteder" in tekst
    assert len(tekst) <= 6000
    assert "<" not in tekst and "function(" not in tekst
