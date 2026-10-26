"""Tester av Gjøvik kommunes postliste (sprint 7).

`tests/fixtures/postliste/` har ekte svar fra postlistens endepunkt, hentet fra GitHub 26.10.2026.
"""

import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import yaml

from horinger.postliste import Postliste, hent_postliste, lagre_postliste

ROT = Path(__file__).parent.parent
FIX = Path(__file__).parent / "fixtures" / "postliste"
KONFIG = yaml.safe_load((ROT / "sources.yaml").read_text("utf-8"))
GJOVIK = KONFIG["postlister"][0]
FELLES = KONFIG["felles"]["postliste"]
SVAR = json.loads((FIX / "gjovik_hoering_s1.json").read_text("utf-8"))


class _Nett:
    """Gir samme ekte svar for første side og en tom side etter det."""

    def __init__(self, feil: Exception | None = None):
        self.kall: list[dict] = []
        self.feil = feil

    def hent(self, url, metode="GET", json=None, headers=None):
        self.kall.append({"url": url, "metode": metode, "json": json, "headers": headers})
        if self.feil:
            raise self.feil
        side = next(k["value"] for k in json["keyValues"] if k["key"] == "page")
        data = SVAR if side == "1" else {"content": {"searchItems": {"items": []}}}
        return SimpleNamespace(json=lambda: data)


def _poster(dag=date(2026, 10, 26)):
    nett = _Nett()
    return Postliste(GJOVIK, nett, {**FELLES, "sokeord": ["høring"]}).hent(dag), nett


def test_henter_hoeringsbrev_og_utelater_svar():
    poster, _ = _poster()
    titler = [p["tittel"] for p in poster]
    assert "Høring – Forslag til ny lov om fylkeskommunale tannhelsetjenester mv." in titler
    assert (
        "Høring om forslag til endringer i enkelte saksbehandlings- og klageregler i "
        "opplæringsloven og opplæringsforskriften mv." in titler
    )
    # Svar og kopier av høringssvar til kommunens egne planer er ikke høringsbrev.
    assert not any(t.startswith(("Kopi - Høringssvar", "Kopi - Høringsuttalelse")) for t in titler)
    assert "Svar på forespørsel om høringsuttalelse" not in titler
    assert not any("Innspill til varsel" in t for t in titler)
    assert len(poster) == 5


def test_felt_og_lenke():
    poster, _ = _poster()
    tann = next(p for p in poster if "tannhelsetjenester" in p["tittel"])
    assert tann["dato"] == "2026-10-20"
    assert tann["dokument_id"] == "2026/85652"
    assert tann["avsender"] == "Helse- Og Omsorgsdepartementet"
    assert tann["kommune"] == "Gjøvik"
    assert tann["lenke"] == (
        "https://www.gjovik.kommune.no/politikk-planer-og-organisasjon/postliste-dokumenter-og-"
        "vedtak/sok-i-postliste/#/details/a-ee0f97cc__bfb2__4549__9555__c2dcc5131630-"
        "2021031723!H4Ot3W/d-ee0f97cc__bfb2__4549__9555__c2dcc5131630-2021586173!4OjK9p"
    )


def test_14_dagers_vindu():
    # 3.11: vinduet starter 20.10, så journalpostene fra 14.10 og 19.10 faller ut.
    poster, _ = _poster(date(2026, 11, 3))
    assert {p["dato"] for p in poster} <= {"2026-10-20", "2026-10-21"}
    assert poster


def test_blar_ikke_forbi_vinduet():
    # Eldste treff på side 1 er 14.10, eldre enn vinduet (12.10–26.10)? Nei: da blas det videre.
    _, nett = _poster(date(2026, 10, 26))
    assert len(nett.kall) == 2  # side 2 er tom
    _, nett = _poster(date(2026, 11, 3))  # vinduet starter 20.10: side 1 holder
    assert len(nett.kall) == 1


def test_foresporsel_bare_inngaaende_og_hoder():
    _, nett = _poster()
    k = nett.kall[0]
    assert k["metode"] == "POST"
    assert k["url"] == "https://www.gjovik.kommune.no/api/presentation/v2/nye-innsyn/overview"
    verdier = {v["key"]: v["value"] for v in k["json"]["keyValues"]}
    assert verdier["Type"] == GJOVIK["dokumenttype_inngaaende"]
    assert verdier["searchTerm"] == "høring"
    assert k["headers"]["Origin"] == "https://www.gjovik.kommune.no"


def test_personvern_avsender_bare_for_virksomheter():
    p = Postliste(GJOVIK, _Nett(), FELLES)
    for navn in [
        "Statens vegvesen",
        "Helse- Og Omsorgsdepartementet",
        "Innlandet Fylkeskommune",
        "Statsforvalteren I Innlandet",
        "Samediggi  Sametinget",
        "Norges Vassdrags- Og Energidir",
        "Bane NOR SF",
    ]:
        assert p.er_virksomhet(navn), navn
    for navn in ["Ola Nordmann", "Kari Hansen", ""]:
        assert not p.er_virksomhet(navn), navn
    post = {
        "identifier": "d-1",
        "parentIdentifier": "a-1",
        "title": "Høring om noe",
        "type": "Inngående dokument",
        "properties": {"dato": "21.10.2026", "avsender": "Ola Nordmann", "dokumentID": "x"},
    }
    assert p.tolk(post, date(2026, 10, 1))["avsender"] == ""


def test_er_svar():
    p = Postliste(GJOVIK, _Nett(), FELLES)
    assert p.er_svar("Kopi - Høringssvar - Detaljplan for dam Beritknappen")
    assert p.er_svar("Innspill til varsel om oppstart av detaljregulering")
    assert p.er_svar("Svar på forespørsel om høringsuttatelse")
    # Høringsbrev som nevner høringssvar senere i tittelen, tas med.
    assert not p.er_svar("Høring – endringer i forskriften – frist for høringssvar 1. desember")
    assert not p.er_svar("Varsel om oppstart av planarbeid – mulighet for innspill")


def test_feil_gir_status_og_resten_fortsetter(tmp_path):
    forrige = hent_postliste(GJOVIK, _Nett(), {**FELLES, "sokeord": ["høring"]})
    lagre_postliste(tmp_path, forrige)
    feil = hent_postliste(GJOVIK, _Nett(TimeoutError("tidsavbrudd")), FELLES)
    assert feil["status"] == "feil"
    assert "TimeoutError" in feil["feil"]
    lagret = lagre_postliste(tmp_path, feil)
    # Forrige journalposter beholdes, slik at merkene ikke forsvinner.
    assert lagret["journalposter"] == forrige["journalposter"]
    assert lagret["sist_ok"] == forrige["hentet"]


def test_simulert_feil():
    r = hent_postliste(GJOVIK, _Nett(), FELLES, simuler_feil=GJOVIK["navn"])
    assert r["status"] == "feil" and "Simulert" in r["feil"]
