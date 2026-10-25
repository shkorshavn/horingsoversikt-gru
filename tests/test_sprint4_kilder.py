"""Tester av kildene fra sprint 4, mot lagrede kopier av kildesidene (hentet 25.10.2026)."""

import json
from datetime import date
from pathlib import Path

import pytest
import yaml

from horinger.geografi import GeografiFilter
from horinger.kilder import bane_nor, digdir, dsb, jernbanedirektoratet, nve, nye_veier
from horinger.kilder.enkle_lister import tolk_bufdir, tolk_dibk, tolk_helsedirektoratet
from horinger.kilder.miljodirektoratet import tolk as tolk_miljo
from horinger.sokeord import Sokeord

F = Path(__file__).parent / "fixtures"
KONFIG = yaml.safe_load((Path(__file__).parent.parent / "sources.yaml").read_text("utf-8"))
GEOGRAFI = GeografiFilter(KONFIG["felles"]["geografi"])
KILDER = {k["navn"]: k for k in KONFIG["kilder"]}


def _les(navn: str) -> str:
    return (F / navn).read_text(encoding="utf-8")


def _sokeord(kilde: str) -> Sokeord:
    k = KILDER[kilde]
    return Sokeord(k.get("sokeord", []), k.get("utelat_ord", []))


# ---------- Miljødirektoratet ----------


def test_miljo_utelater_olje_og_gass():
    data = json.loads(_les("miljodirektoratet.json"))
    alle = tolk_miljo(data, set())
    uten = tolk_miljo(data, {"olje og gass"})
    assert len(alle) == 18
    assert len(uten) == 11  # 7 høringer har temaet «Olje og gass»
    assert not any("Equinor" in h["tittel"] for h in uten)


def test_miljo_felt():
    (h,) = [
        h
        for h in tolk_miljo(json.loads(_les("miljodirektoratet.json")), set())
        if "Solør" in h["tittel"]
    ]
    assert h["frist"] == date(2026, 11, 24)
    assert h["publisert"] == date(2026, 10, 20)
    assert h["lenke"].startswith("https://www.miljodirektoratet.no/hoeringer/2026/oktober-2026/")
    assert "Innlandet" in h["ingress"] and "2026/2029" in h["ingress"]


# ---------- NVE ----------


def test_nve_forskriftsliste_uten_avsluttede():
    liste = nve.tolk_forskriftsliste(_les("nve_forskrifter.html"))
    assert liste[0]["publisert"] == date(2026, 10, 5)
    assert not any("avsluttet" in h["tittel"].lower() for h in liste)
    assert len(liste) == 5


def test_nve_detalj_med_frist():
    frist, setning, ingress = nve.tolk_forskriftsdetalj(_les("nve_detalj.html"), date(2025, 12, 19))
    assert frist == date(2026, 3, 15)
    assert setning == "Høringsfrist: Høringsfrist er 15. mars 2026"
    assert ingress.startswith("Norges vassdrags- og energidirektorat (NVE) har sendt på høring")


def test_nve_detalj_med_vag_frist():
    """«innen høringsfristen desember 2026»: ingen dato, men setningen vises (Svein 25.10)."""
    frist, setning, _ = nve.tolk_forskriftsdetalj(
        _les("nve_detalj_vag_frist.html"), date(2026, 10, 5)
    )
    assert frist is None
    assert "høringsfristen desember 2026" in setning


def test_nve_konsesjoner_geografi():
    data = json.loads(_les("nve_konsesjoner.json"))
    assert nve.tolk_konsesjoner(data, GEOGRAFI) == []  # ingen i området 25.10.2026
    trysil = nve.tolk_konsesjoner(data, GeografiFilter({"kommuner": ["Trysil"]}))
    assert [h["tittel"] for h in trysil] == ["Granåsen vindkraftverk", "Borveggen vindkraftverk"]
    assert trysil[0]["frist"] == date(2026, 11, 6)
    assert trysil[0]["lenke"].endswith("konsesjonssak?id=26175&type=A-6")


def test_nve_konsesjon_uten_frist():
    data = {
        "Licenses": [
            {
                "Tittel": "Lillehammer kraftlinje",
                "Kommune": "Lillehammer",
                "Hoeringsfrist": "0001-01-01T00:00:00",
                "SoknadId": 1,
                "Type": "A-1",
            }
        ]
    }
    (h,) = nve.tolk_konsesjoner(data, GEOGRAFI)
    assert h["frist"] is None


# ---------- DSB ----------


def test_dsb_rss():
    rss = dsb.tolk_rss(_les("dsb_rss.xml"))
    assert len(rss) == 25
    assert rss[0]["tittel"] == "Endringer i sivilforsvarsforskriften"
    assert rss[0]["publisert"] == date(2026, 10, 16)
    assert not rss[0]["samtykke"] and rss[1]["samtykke"]


def test_dsb_detalj():
    frist, tekst, ingress = dsb.tolk_detalj(_les("dsb_detalj.html"), date(2026, 10, 16))
    assert frist == date(2026, 11, 27)
    assert tekst == "Høringsfrist: 27.11.2026"
    assert ingress.startswith("Direktoratet for samfunnssikkerhet og beredskap (DSB) sender")


def test_dsb_samtykke_uten_geografi_tas_ikke_med():
    assert not GEOGRAFI.vurder("Bygging av tankanlegg i Avaldsnes i Karmøy kommune").relevant


# ---------- Helsedirektoratet, Bufdir, DiBK ----------


def test_helsedirektoratet_bare_ute_pa_horing():
    liste = tolk_helsedirektoratet(
        _les("helsedirektoratet.html"), "https://www.helsedirektoratet.no/horinger"
    )
    assert [h["frist"] for h in liste] == [date(2026, 12, 3), date(2027, 2, 1)]
    assert (
        liste[0]["tittel"]
        == "Retningslinje for mat, måltider og ernæring i helse- og omsorgstjenesten"
    )
    assert not any("Fontenehus" in h["tittel"] for h in liste)  # under behandling


def test_bufdir_ingen_apne(monkeypatch):
    assert tolk_bufdir(_les("bufdir.html"), "https://www.bufdir.no/om/hoeringer/") == []


def test_bufdir_med_frist_fram_i_tid(monkeypatch):
    monkeypatch.setattr("horinger.kilder.enkle_lister.i_dag", lambda: date(2026, 7, 1))
    (h,) = tolk_bufdir(_les("bufdir.html"), "https://www.bufdir.no/om/hoeringer/")
    assert h["frist"] == date(2026, 8, 3)
    assert h["tittel"].startswith("Forslag til endring av forskrift om tilskudd")


def test_dibk():
    liste = tolk_dibk(_les("dibk.html"), "https://www.dibk.no/regelverk/horinger/hoyringar")
    assert len(liste) == 28
    assert liste[0]["frist"] == date(2026, 6, 16)
    assert (
        liste[0]["tittel"]
        == "Forslag til endringer i veiledningen til kapittel 2 i byggteknisk forskrift"
    )
    assert all(h["tittel"] and h["lenke"].startswith("https://www.dibk.no/") for h in liste)


# ---------- Digdir ----------


def test_digdir_liste_og_ar():
    liste = digdir.tolk_liste(
        _les("digdir.html"), "https://www.digdir.no/standarder/hoyringar/1502"
    )
    assert len(liste) == 10
    assert not digdir.har_ar(liste[0]["frist_tekst"])  # «Høyringsfrist 1. oktober.»
    assert digdir.har_ar(liste[3]["frist_tekst"])  # «Høyringsfrist 01.09.2020»


def test_digdir_detalj():
    laga, status = digdir.tolk_detalj(_les("digdir_detalj.html"))
    assert laga == date(2022, 9, 12)
    assert status == "Ferdig behandla"


# ---------- Nye Veier ----------


def test_nye_veier_sokeord():
    liste = nye_veier.tolk_liste(_les("nye_veier.html"), KILDER["Nye Veier"]["url"])
    assert len(liste) == 65
    s = _sokeord("Nye Veier")
    treff = {h["tittel"] for h in liste if s.treff(f"{h['tittel']} {h['prosjekt']} {h['ingress']}")}
    assert "Varsel om utvidet varslingsområde for E6-strekningen fra Elstad til Fryasletta" in treff
    assert "Befaring langs rv. 4" not in treff


def test_nye_veier_detalj():
    frist, setning = nye_veier.tolk_detalj(_les("nye_veier_detalj.html"), date(2026, 6, 8))
    assert frist == date(2026, 7, 3)
    assert setning.endswith("innen 3. juli 2026")


def test_nye_veier_uten_frist_tas_ikke_med():
    """«Utsatt høring …» har ingen frist og skal ikke vises som en åpen høring."""
    frist, _ = nye_veier.tolk_detalj(_les("nye_veier_uten_frist.html"), date(2026, 4, 8))
    assert frist is None


# ---------- Jernbanedirektoratet ----------


def test_jernbanedirektoratet_bare_nye():
    data = json.loads(_les("jernbanedirektoratet.json"))
    assert (
        jernbanedirektoratet.tolk(data, _sokeord("Jernbanedirektoratet"), date(2026, 6, 27)) == []
    )


def test_jernbanedirektoratet_vag_frist():
    data = json.loads(_les("jernbanedirektoratet.json"))
    funnet = jernbanedirektoratet.tolk(data, _sokeord("Jernbanedirektoratet"), date(2026, 1, 1))
    assert [h["tittel"] for h in funnet] == [
        "Tre nye utredninger: – Vi løser ikke utfordringene uten jernbanen"
    ]
    assert funnet[0]["frist"] is None  # «midten av juni»
    assert "høring" in funnet[0]["frist_tekst"].lower() or funnet[0]["frist_tekst"] == ""


# ---------- Bane NOR ----------


def test_bane_nor_sitemap():
    adresser = bane_nor.tolk_sitemap(
        _les("bane_nor_sitemap.xml"), _sokeord("Bane NOR"), date(2026, 6, 20)
    )
    assert any("sorli-flerbruksterminal" in a for a in adresser)
    assert not any("innkomne-merknader" in a for a in adresser)


@pytest.mark.parametrize(
    "fil, frist, relevant",
    [
        ("bane_nor_sorli.html", date(2026, 8, 13), True),  # Stange
        ("bane_nor_moelv.html", date(2025, 6, 23), True),  # Ringsaker
        ("bane_nor_oslo.html", date(2026, 5, 12), False),  # Oslo uten rv. 4
    ],
)
def test_bane_nor_detalj(fil, frist, relevant):
    d = bane_nor.tolk_detalj(_les(fil))
    assert d["frist"] == frist
    assert GEOGRAFI.vurder(d["tekst"]).relevant is relevant
    assert d["tittel"] and d["publisert"]
