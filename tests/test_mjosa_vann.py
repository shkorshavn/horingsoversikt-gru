"""Tester av «alltid med» for Mjøsa og vann, departementene og Kystverket (sprint 12)."""

from datetime import date
from pathlib import Path

import pytest
import yaml

from horinger.geografi import GeografiFilter
from horinger.kilder.base import Kilde
from horinger.kilder.etater import Kystverket, detalj, tolk_kystverket
from horinger.kilder.miljodirektoratet import tolk as tolk_miljodir
from horinger.kilder.nve import tolk_konsesjoner
from horinger.kilder.regjeringen import velg
from horinger.prioritet import Prioritet
from horinger.relevans import instruks, vurder
from horinger.tema import AlltidMed, fra_felles

ROT = Path(__file__).parent.parent
F = Path(__file__).parent / "fixtures" / "kystverket"
KONFIG = yaml.safe_load((ROT / "sources.yaml").read_text("utf-8"))
FELLES = KONFIG["felles"]
REL = FELLES["relevans"]
AM = fra_felles(FELLES)


# ---------- Regelen ----------


@pytest.mark.parametrize(
    ("tittel", "detaljtekst", "treff"),
    [
        ("Tiltak mot dumpet ammunisjon i Mjøsa", "", "Mjøsa"),
        ("Mjøsas vannkvalitet", "", "Mjøsas"),
        ("Overvåking av innsjøer i Innlandet", "", "innsjø*"),
        ("Endringer i vannforskriften", "", "vannforskrift*"),
        ("Lokal fartsforskrift for Randsfjorden", "", "fartsforskrift*"),
        ("Nye regler for fritidsbåter", "", "fritidsbåt*"),
        ("Fartsgrense for båter på elva", "", "fartsgrense* + båt*"),
        ("Grenseverdi for PFAS i drikkevannsforskriften", "", "drikkevann*"),
        ("Revisjon av vilkår for vassdragsregulering i Lågen", "", "vassdragsregulering*"),
        ("Sikringstiltak for flom og skred", "", "flom*"),
        ("Overtredelsesgebyr for avrenning", "", "avrenning*"),
        # Detaljteksten: bare `ord`, ikke `ord_tittel`.
        ("Karbonfangstanlegg på Trehørningen", "Kondensat slippes ut til Mjøsa.", "Mjøsa"),
        ("Næringsmiddelforskrifter for Svalbard", "Gjelder også drikkevann.", ""),
        ("Fv. 33 Skreia–Bilitt", "Planen tar hensyn til flom.", ""),
        # Vanlige høringer uten vann.
        ("Klimakvoteforskriften – utslipp fra industri", "", ""),
        ("Endringer i CO2-avgiften", "Utslipp av CO2.", ""),
        ("Ammunisjon til Forsvaret", "", ""),
        ("Fartsgrense på vei ved Gjøvik", "", ""),
        ("Flomberegning", "", "flom*"),
        # Hele ord uten *: firmanavn i lister over høringsparter treffer ikke.
        ("Opprinnelsesgarantier", "Høringsparter: Mjøsanlegget, Lyse", ""),
    ],
)
def test_alltid_med_ordene(tittel, detaljtekst, treff):
    assert AM.treff(tittel, detaljtekst) == treff


def test_alltid_med_krever_alle_deler():
    am = AlltidMed({"ord": ["ammunisjon* + Mjøsa"]})
    assert am.treff("Ammunisjonen i Mjøsa") == "ammunisjon* + Mjøsa"
    assert am.treff("Ammunisjon") == ""
    assert am.treff("Mjøsa") == ""
    assert AlltidMed(None).treff("Mjøsa") == ""
    assert AM.grunn == "gjelder Mjøsa og vann"


# ---------- Rekkefølgen i relevansvurderingen ----------


def test_alltid_med_gaar_foran_representantforslag_og_ki():
    h = {"tittel": "Representantforslag om opprydding av ammunisjon i Mjøsa", "kilde": "Stortinget"}
    nei = {"relevant": False, "hvorfor": "Gjelder statlig opprydding."}
    assert vurder(h, nei, REL) == {"relevant": True, "hvorfor_relevant": ""}
    ja = {"relevant": True, "hvorfor": "Gjelder Mjøsa, som regionen grenser til."}
    assert vurder(h, ja, REL)["hvorfor_relevant"] == "Gjelder Mjøsa, som regionen grenser til."
    # Treffet fra byggingen (med detaljtekst) brukes også.
    h2 = {"tittel": "Karbonfangstanlegg", "alltid_med": "Mjøsa"}
    assert vurder(h2, nei, REL)["relevant"] is True
    # Uten treff gjelder de andre reglene som før.
    assert vurder({"tittel": "Representantforslag om noe annet"}, None, REL)["relevant"] is False


def test_ki_instruksen_har_temaene():
    tekst = instruks(REL)
    assert "ALLTID relevante" in tekst
    for tema in ("Mjøsa", "båttrafikk", "avrenning", "ammunisjon", "drikkevann", "flom"):
        assert tema in tekst


def test_relevans_sendes_til_ki_selv_for_representantforslag_om_mjosa():
    from horinger.relevans import Relevans

    r = Relevans(FELLES["sammendrag"], REL, None)
    assert not r.hopp_over({"tittel": "Representantforslag om vannkvaliteten i Mjøsa"})
    assert r.hopp_over({"tittel": "Representantforslag om noe annet"})


# ---------- Prioritet ----------


def test_hoy_prioritet_med_grunn():
    p = Prioritet(FELLES)
    assert p.vurder({"tittel": "Vannkvalitet i Mjøsa"}, {"prioritet": 3}) == (
        1,
        "gjelder Mjøsa og vann",
    )
    # Også når kildens prioritet allerede er høy, slik at grunnen vises.
    assert p.vurder({"tittel": "Drikkevann"}, {"prioritet": 1}) == (1, "gjelder Mjøsa og vann")
    assert p.vurder({"tittel": "Ingenting"}, {"prioritet": 3}) == (3, "")


# ---------- Filtrene i kildene ----------


def test_departementene_er_tatt_inn_igjen():
    assert FELLES["ekskluder_departementer"] == ["Utenriksdepartementet"]


UD = "Utenriksdepartementet"


def test_regjeringen_ekskludert_departement_slipper_gjennom_mjosa():
    rader = [
        {
            "instans": "Utenriksdepartementet",
            "tittel": "Avtale om handel",
            "status": "Status: På høring",
        },
        {
            "instans": "Utenriksdepartementet",
            "tittel": "Grenseelver og innsjøer",
            "status": "Status: På høring",
        },
    ]
    am = lambda t: AM.treff(t)  # noqa: E731
    valgt = velg(rader, {"Utenriksdepartementet"}, am)
    assert [r["tittel"] for r in valgt] == ["Grenseelver og innsjøer"]
    assert velg(rader, {"Utenriksdepartementet"}) == []


def test_miljodirektoratet_utelatt_tema_slipper_gjennom_mjosa():
    data = {
        "hearings": [
            {
                "title": "Utslippstillatelse for felt i Nordsjøen",
                "subjects": ["Olje og gass"],
                "url": "/a",
            },
            {"title": "Drikkevann ved oljeanlegg", "subjects": ["Olje og gass"], "url": "/b"},
            {"title": "Naturvern", "subjects": ["Natur"], "url": "/c"},
        ]
    }
    titler = [h["tittel"] for h in tolk_miljodir(data, {"olje og gass"}, AM.treff)]
    assert titler == ["Drikkevann ved oljeanlegg", "Naturvern"]


def test_nve_konsesjon_utenfor_geografien_med_mjosa():
    data = {
        "Licenses": [
            {"Kommune": "Bergen", "Tittel": "Ny kraftlinje", "SoknadId": 1, "Type": "x"},
            {
                "Kommune": "Eidsvoll",
                "Tittel": "Manøvreringsreglement for Mjøsa",
                "SoknadId": 2,
                "Type": "x",
            },
        ]
    }
    geo = GeografiFilter(FELLES["geografi"])
    titler = [s["tittel"] for s in tolk_konsesjoner(data, geo, AM.treff)]
    assert titler == ["Manøvreringsreglement for Mjøsa"]


def test_aktuell_for_regionen_gjelder_ogsa_mjosa():
    class _K(Kilde):
        def hent(self):
            return []

    k = _K({"navn": "X"}, None, FELLES)
    assert k.aktuell_for_regionen("Tiltak mot avrenning til Mjøsa")
    assert not k.aktuell_for_regionen("Ny forskrift om fiskeflåten")
    k2 = _K({"navn": "X", "krav": "alltid_med"}, None, FELLES)
    assert k2.krav_oppfylt("Fritidsbåter")
    assert not k2.krav_oppfylt("Kommunene i Innlandet")


# ---------- Kystverket ----------


def test_kystverket_liste():
    liste = tolk_kystverket(
        (F / "liste.html").read_text("utf-8"), "https://www.kystverket.no/regelverk/horinger/"
    )
    assert len(liste) == 38
    forste = liste[0]
    assert forste["tittel"] == "Forslag til nye avgiftssatser for 2027 på høring"
    assert forste["lenke"] == (
        "https://www.kystverket.no/regelverk/horinger/forslag-til-nye-avgiftssatser-for-2027-pa-horing/"
    )
    assert forste["publisert"] == date(2026, 10, 15)


def test_kystverket_detalj_frist():
    d = detalj((F / "kyst_d1.html").read_text("utf-8"))
    assert d["frist"] == date(2026, 11, 24)
    d = detalj((F / "kyst_d3.html").read_text("utf-8"))
    assert d["frist"] == date(2026, 7, 17)


def test_kystverket_tar_bare_med_mjosa_og_regionen():
    k = Kystverket({"navn": "Kystverket"}, None, FELLES)
    for navn in ("kyst_d1", "kyst_d2", "kyst_d3"):
        d = detalj((F / f"{navn}.html").read_text("utf-8"))
        assert not k.godta({"tittel": d["tittel"], "ingress": d["ingress"], "_tekst": d["tekst"]})
    assert k.godta({"tittel": "Statlige fartsgrenser", "ingress": "", "_tekst": "Gjelder Mjøsa."})
    assert k.godta({"tittel": "Ny farled", "ingress": "i Gjøvik kommune", "_tekst": ""})
    assert not k.godta({"tittel": "Ny farled i Kristiansund", "ingress": "", "_tekst": ""})


def test_nye_kilder_i_sources_yaml():
    kilder = {k["navn"]: k for k in KONFIG["kilder"]}
    assert kilder["Kystverket"]["aktiv"] is True and kilder["Kystverket"]["modul"] == "kystverket"
    for navn in ("Sjøfartsdirektoratet", "Forsvarsbygg", "Vannportalen", "Folkehelseinstituttet"):
        assert kilder[navn]["aktiv"] is False
        assert "03.11.2026" in kilder[navn]["merknad"]


def test_tolk_svar_taaler_tekst_og_klammer_etter_json():
    from horinger.relevans import tolk_svar

    svar = '{"relevant": true, "hvorfor": "Gjelder nettleien."}\n\nMerk: {usikker} vurdering.'
    assert tolk_svar(svar) == {"relevant": True, "hvorfor": "Gjelder nettleien."}
    assert (
        tolk_svar('Forklaring {x} så {"relevant": false, "hvorfor": "Bare havet."}')["relevant"]
        is False
    )
