"""Tester av kildene fra sprint 5, mot lagrede kopier av sidene (hentet 25.10.2026)."""

from datetime import date
from pathlib import Path

import pytest
import yaml

from horinger.kilder import bane_nor
from horinger.kilder.base import Kilde
from horinger.kilder.etater import (
    Riksantikvaren,
    detalj,
    er_fredningssak,
    tas_med,
    tolk_arbeidstilsynet,
    tolk_dmp,
    tolk_landbruk,
    tolk_mattilsynet,
    tolk_nasjonalarkivet,
    tolk_nkom,
    tolk_politiet,
    tolk_riksantikvaren,
    tolk_skatteetaten,
)
from horinger.sokeord import Sokeord

F = Path(__file__).parent / "fixtures"
KONFIG = yaml.safe_load((Path(__file__).parent.parent / "sources.yaml").read_text("utf-8"))
KILDER = {k["navn"]: k for k in KONFIG["kilder"]}


def _les(navn: str) -> str:
    return (F / navn).read_text(encoding="utf-8")


def test_nkom_liste_og_detalj():
    (h,) = tolk_nkom(_les("nkom.html"), "https://nkom.no/hoeringer")
    assert h["tittel"] == "Høring av utlysningsvilkår og tildelingsregler for lokale FM-sendernett"
    d = detalj(_les("nkom_detalj.html"))
    assert d["frist"] == date(2026, 11, 13)


def test_landbruk_bare_pa_horing_na():
    (h,) = tolk_landbruk(
        _les("landbruksdirektoratet.html"), "https://www.landbruksdirektoratet.no/nb/x"
    )
    assert h["frist"] == date(2026, 10, 16)  # «fredag 16. oktober 2026»
    assert h["tittel"].startswith("Høring - Forslag til omregningsfaktor")
    assert "/nb/om-direktoratet/horinger/horing-forslag" in h["lenke"]


def test_riksantikvaren():
    liste = tolk_riksantikvaren(_les("riksantikvaren.html"), "https://riksantikvaren.no/")
    assert len(liste) == 10
    halden = liste[0]
    assert halden["tittel"] == "Foreslår å frede deler av Haldenkanalen"
    assert halden["frist"] == date(2026, 9, 30)  # «30.september 2026» uten mellomrom
    assert halden["publisert"] == date(2026, 5, 7)
    assert er_fredningssak(halden["tittel"])
    uttalelse = next(h for h in liste if "Bygnings" in h["tittel"])
    assert uttalelse["frist"] is None  # egen uttalelse, ikke høring


def _kilde(klasse, navn):
    return klasse(KILDER[navn], nett=None, felles=KONFIG["felles"])


def test_riksantikvaren_fredning_bare_i_regionen():
    ra = _kilde(Riksantikvaren, "Riksantikvaren")
    assert not ra.godta({"tittel": "Foreslår å frede deler av Haldenkanalen", "ingress": ""})
    assert ra.godta({"tittel": "Foreslår å frede Hunn gravfelt", "ingress": "Gjøvik kommune"})
    # Saker som gjelder fylkeskommunene tas med selv om de handler om fredet eiendom.
    assert ra.godta(
        {
            "tittel": "Høring: Overføring av forvaltningsansvar for fredet eiendom",
            "ingress": "fra Riksantikvaren til fylkeskommunen",
        }
    )
    assert ra.godta({"tittel": "Ny forskrift om kulturminnesøk", "ingress": ""})
    # Sprint 5 v2: hele Innlandet fylke, ikke bare regionen.
    assert ra.godta(
        {"tittel": "Forslag om freding av Kvikne kirke", "ingress": "i Nord-Fron kommune"}
    )
    assert ra.godta({"tittel": "Oppstart av fredning av Trysil-gården", "ingress": ""})
    assert not ra.godta(
        {"tittel": "Forslag om freding av sjøhuset Slinningsbua", "ingress": "Ålesund"}
    )


def test_nasjonalarkivet():
    liste = tolk_nasjonalarkivet(_les("nasjonalarkivet.html"), "https://www.nasjonalarkivet.no/")
    assert [h["tittel"] for h in liste][:2] == [
        "Arbeidet med ny strategi for privatarkiv 2026",
        "Høring: ny arkivforskrift 2025",
    ]
    assert not any(h["lenke"].endswith(".pdf") for h in liste)


def test_dmp_liste_og_detalj():
    liste = tolk_dmp(_les("dmp.html"), "https://www.dmp.no/om-oss/horinger")
    assert liste[0]["tittel"].startswith("Høring om endringer i forskrift for medisinsk utstyr")
    assert "Publisert" not in liste[0]["tittel"]
    assert liste[0]["publisert"] == date(2026, 10, 13)
    assert detalj(_les("dmp_detalj.html"))["frist"] == date(2026, 12, 9)


def test_mattilsynet():
    liste = tolk_mattilsynet(
        _les("mattilsynet.html"), "https://www.mattilsynet.no/regelverksutvikling"
    )
    assert not any(h["tittel"].lower().startswith("bestilling") for h in liste)
    drikkevann = next(h for h in liste if "kontakt med drikkevann" in h["tittel"])
    assert drikkevann["frist"] == date(2026, 10, 20)
    assert drikkevann["lenke"].startswith("https://www.mattilsynet.no/regelverksutvikling?bId=")


def test_arbeidstilsynet_bare_pagaende():
    (h,) = tolk_arbeidstilsynet(
        _les("arbeidstilsynet.html"), "https://www.arbeidstilsynet.no/regelverk/horinger/"
    )
    assert h["frist"] == date(2027, 1, 31)
    assert h["tittel"] == "Høring - Fjerne kravet til røntgenundersøkelse ved bergarbeid"


def test_politiet_slaar_sammen_dokumenter():
    (h,) = tolk_politiet(_les("politiet_pod.html"))  # 3 dokumenter fra samme høring + 1 svar
    assert h["tittel"] == "Høring – Nasjonal retningslinje for utgivelse av navn"
    assert h["frist"] == date(2026, 9, 11)
    assert h["instans"] == "Politidirektoratet"
    assert tolk_politiet(_les("politiet_innlandet.html")) == []  # bare et høringssvar fra 2020


def test_skatteetaten():
    liste = tolk_skatteetaten(
        _les("skatteetaten.html"), "https://www.skatteetaten.no/rettskilder/type/horinger/"
    )
    assert len(liste) == 118
    assert detalj(_les("skatteetaten_detalj.html"))["frist"] == date(2026, 11, 11)
    assert detalj(_les("skatteetaten_uten_frist.html"))["frist"] is None


def test_ssb_utlopt_hoering_tas_ikke_med():
    d = detalj(_les("ssb.html"))
    assert d["frist"] == date(2026, 6, 4)  # «Høringsfristen var 4. juni 2026»
    assert d["publisert"] == date(2026, 4, 8)  # «Publisert : 8. april 2026»


def test_konkurransetilsynet_sitemap():
    k = KILDER["Konkurransetilsynet"]
    adresser = bane_nor.tolk_sitemap(
        _les("konkurransetilsynet_sitemap.xml"),
        Sokeord(k["sokeord"], k["utelat_ord"]),
        date(2026, 6, 1),
    )
    assert adresser == [
        "https://konkurransetilsynet.no/horing-revisjon-av-retningslinjer-for-fusjoner-og-oppkjop/"
    ]


def test_tas_med(monkeypatch):
    monkeypatch.setattr("horinger.kilder.etater.i_dag", lambda: date(2026, 10, 25))
    assert tas_med(date(2026, 1, 1), None)
    assert tas_med(None, date(2026, 8, 1))
    assert not tas_med(None, date(2026, 7, 1))
    assert not tas_med(None, None)


class _Dummy(Kilde):
    def hent(self):
        return []


@pytest.mark.parametrize(
    "tekst, aktuell",
    [
        ("Forslag som gir kommunene nye oppgaver", True),
        ("Ny ordning i Innlandet", True),
        ("Endring i regler for drosjer i Raufoss", True),
        ("Forslag om fusjonskontroll i bankmarkedet", False),
    ],
)
def test_aktuell_for_regionen(tekst, aktuell):
    k = _Dummy({"navn": "X", "krav": "aktuell_for_regionen"}, nett=None, felles=KONFIG["felles"])
    assert k.krav_oppfylt(tekst) is aktuell
    assert _Dummy({"navn": "Y"}, nett=None, felles=KONFIG["felles"]).krav_oppfylt(tekst)


def test_alle_etater_i_avsnitt_2_har_oppforing():
    """Kriterium 1: alle prioritet 2- og 3-kilder er aktive eller har begrunnelse."""
    for k in KONFIG["kilder"]:
        if k.get("prioritet") in (2, 3) and not k.get("aktiv") and k["navn"] != "Regjeringen.no":
            assert k.get("merknad"), k["navn"]
        if k.get("aktiv"):
            from horinger.kilder import KILDER as MODULER

            assert k.get("modul") in MODULER, k["navn"]
