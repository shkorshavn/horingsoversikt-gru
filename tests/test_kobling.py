"""Tester av koblingen mellom postlista og høringene (sprint 7).

Fasiten er satt for hånd 26.10.2026: 48 ekte høringsbrev fra Gjøviks postliste (06.08–21.10)
mot de 202 høringene i oversikten og arkivet. Se sprintrapport 7 for tabellen.
"""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

from horinger.kobling import (
    MULIG,
    SIKKER,
    Kobling,
    koble_postlister,
    lik_avsender,
    referanser,
    rens_avsender,
    rens_tittel,
)
from horinger.postliste import lagre_postliste

ROT = Path(__file__).parent.parent
FIX = Path(__file__).parent / "fixtures" / "postliste"
KONFIG = yaml.safe_load((ROT / "sources.yaml").read_text("utf-8"))
OPPSETT = KONFIG["felles"]["postliste"]
POSTER = {
    p["dokument_id"]: p
    for p in json.loads((FIX / "gjovik_journalposter.json").read_text("utf-8"))["journalposter"]
}
HORINGER = json.loads((FIX / "horinger_26_10.json").read_text("utf-8"))["horinger"]
KOBLING = Kobling(OPPSETT)

# Riktig høring for høringsbrev som finnes i oversikten (kontrollert mot tittel og avsender).
FASIT = {
    "2026/86270": "5a4d402d9439",  # NFD: Europakommisjonens anskaffelsesforordning
    "2026/86288": "d6878ef0e7f4",  # KD: saksbehandlings- og klageregler i opplæringsloven
    "2026/85652": "e4f7f112e5d1",  # HOD: fylkeskommunale tannhelsetjenester
    "2026/85572": "10f5a678155b",  # Vegvesenet: indeksregulering i parkeringsforskriften
    "2026/84085": "b5d10c057333",  # Skatteetaten: skatteregnskapsområdet
    "2026/83309": "7bdc37294b5b",  # Vegvesenet: vegtrafikkloven, unntak fra forvaltningsloven
    "2026/83115": "2f947152205b",  # AID: integreringsloven
    "2026/82854": "9d8000136a3b",  # KD: smågruppeundervisning og leksehjelp
    "2026/81286": "defdb6b438fe",  # Innlandet fylkeskommune: nettinfrastruktur, planprogram
    "2026/81203": "868dbad65877",  # KD: gudstjenester og seremonier
    "2026/79934": "0fac555760ba",  # AID: trygderettsloven
    "2026/79578": "387a95279af5",  # HOD: sykepleieres og farmasøyters rett til å rekvirere
    "2026/78463": "ab01fdcf2eec",  # KD: NOU 2026: 10 Fellesskolen
    "2026/78166": "17796e18616d",  # AID: særordning for fordrevne fra Ukraina
    "2026/76896": "defdb6b438fe",  # Innlandet fylkeskommune: varsel om oppstart, samme plan
    "2026/76586": "f84de76c0415",  # Helsedirektoratet: mat, måltider og ernæring
    "2026/76628": "929e7e070e99",  # HOD: nasjonale e-helseløsninger
    "2026/76559": "db984834479b",  # HOD: kartleggingssystem for selvmord
    "2026/74153": "87b13fc8a9cd",  # Miljødirektoratet: karbonpris ved import (CBAM)
    "2026/73852": "c51b51b3b5cc",  # JD: tilfluktssteder (utsatt frist)
    "2026/68202": "ce28d7268a81",  # JD: Ø-kriminformasjonsforskriften
    "2026/69933": "a1692dc49017",  # Vegvesenet: hest i trafikken
    "2026/65424": "a707facb1eff",  # KLD: ekspertutvalget om klimatilpasning
}
# Kan ikke avgjøres: «Revisjon av regelverket om vekter og dimensjoner» (Vegvesenet, 02.10) kom
# etter fristen for høringen om ny forskrift om vekter og dimensjoner (30.09). Kan være samme sak.
UAVKLART = {"2026/81758"}


@pytest.mark.parametrize("dokument_id, hoering_id", sorted(FASIT.items()))
def test_kjente_hoeringsbrev_kobles_sikkert(dokument_id, hoering_id):
    treff = KOBLING.beste(POSTER[dokument_id], HORINGER)
    assert treff.hoering_id == hoering_id
    assert treff.niva == SIKKER


def test_hoeringsbrev_uten_hoering_i_oversikten_kobles_ikke():
    """De andre 24 har ingen riktig høring i oversikten. Ingen av dem skal få treff."""
    uten = [d for d in POSTER if d not in FASIT and d not in UAVKLART]
    assert len(uten) == 24
    feil = {d: KOBLING.beste(POSTER[d], HORINGER) for d in uten}
    assert {d: t.poeng for d, t in feil.items() if t.niva} == {}


def test_tersklene_har_god_margin():
    """Laveste riktige og høyeste feil poengsum (grunnlaget for tersklene i rapporten)."""
    riktige = [
        KOBLING.poeng(POSTER[d], next(h for h in HORINGER if h["id"] == i))
        for d, i in FASIT.items()
    ]
    feil = [
        KOBLING.beste(POSTER[d], HORINGER).poeng
        for d in POSTER
        if d not in FASIT and d not in UAVKLART
    ]
    assert min(riktige) >= OPPSETT["sikker_terskel"] + 2
    assert max(feil) < OPPSETT["mulig_terskel"] - 5


def test_mulig_treff_mellom_tersklene():
    k = Kobling({**OPPSETT, "sikker_terskel": 99, "mulig_terskel": 85})
    treff = k.beste(POSTER["2026/69933"], HORINGER)  # hest i trafikken: 87,3
    assert treff.niva == MULIG


def test_rens_tittel():
    assert (
        rens_tittel("Høring - Endring i vegtrafikkloven (20-38820)") == "endring i vegtrafikkloven"
    )
    assert rens_tittel("Kopi - Høringsbrev - Skiltplan") == "skiltplan"
    assert rens_tittel("Høyring av forslag til lov") == "forslag til lov"
    assert rens_tittel("Høring NOU 2026: 10 Fellesskolen") == "nou 2026 10 fellesskolen"


def test_referanser():
    assert referanser("Høring om parkeringsforskriften (21-219359)") == {"21/219359"}
    assert referanser("Vår ref.: 26/4010") == {"26/4010"}
    assert referanser("Høring om hest") == set()


def test_avkortede_avsendernavn():
    alias = OPPSETT["avsender_alias"]
    a = rens_avsender("Arbeids- Og Inkluderingsdepart", alias)
    assert lik_avsender(a, rens_avsender("Arbeids- og inkluderingsdepartementet", alias))
    assert lik_avsender(rens_avsender("KDD", alias), "kommunal- og distriktsdepartementet")
    assert not lik_avsender("statens vegvesen", "statens kartverk")
    assert not lik_avsender("kd", "kdd")  # korte navn må være like


def test_samme_referanse_er_sikkert_treff():
    jp = {"tittel": "Høring – ny forskrift (21-219359)", "avsender": "Statens vegvesen"}
    h = {"id": "x", "tittel": "Høring om noe helt annet (21-219359)", "instans": "Statens vegvesen"}
    assert KOBLING.poeng(jp, h) == 100.0


# ---------- Bygging: merker, persistens og seksjonen «uten treff» ----------


def _jp(dok, dato):
    return {**POSTER[dok], "id": dok, "dato": dato}


def _koble(tmp_path, poster, apne, forrige=None, dag=date(2026, 10, 26), status="ok"):
    lagre_postliste(
        tmp_path,
        {
            "kilde": KONFIG["postlister"][0]["navn"],
            "status": status,
            "hentet": "2026-10-26T10:00",
            "antall": len(poster),
            "journalposter": poster,
        },
    )
    return koble_postlister(KONFIG, tmp_path, apne, {}, forrige, dag)


def test_merke_paa_hoeringen_og_status(tmp_path):
    tann = dict(next(h for h in HORINGER if h["id"] == "e4f7f112e5d1"))
    treff, status = _koble(tmp_path, [_jp("2026/85652", "2026-10-20")], [tann])
    assert tann["postliste"] == [
        {
            "kommune": "Gjøvik",
            "dato": "2026-10-20",
            "tittel": POSTER["2026/85652"]["tittel"],
            "lenke": POSTER["2026/85652"]["lenke"],
            "niva": SIKKER,
        }
    ]
    assert treff["journalposter"][0]["hoering_id"] == "e4f7f112e5d1"
    assert status[0]["kilde"] == "Gjøvik kommunes postliste"
    assert status[0]["status"] == "ok" and status[0]["type"] == "postliste"


def test_merket_blir_staaende_etter_14_dager(tmp_path):
    tann = dict(next(h for h in HORINGER if h["id"] == "e4f7f112e5d1"))
    forrige, _ = _koble(tmp_path, [_jp("2026/85652", "2026-10-20")], [dict(tann)])
    # Tre uker senere er journalposten ute av vinduet, men merket står.
    _, _ = _koble(tmp_path, [], [tann], forrige, dag=date(2026, 11, 16))
    assert tann["postliste"][0]["dato"] == "2026-10-20"


def test_uten_treff_vises_i_60_dager(tmp_path):
    sameting = _jp("2026/84341", "2026-10-14")
    treff, _ = _koble(tmp_path, [sameting], [])
    assert [j["id"] for j in treff["journalposter"]] == ["2026/84341"]
    assert treff["journalposter"][0]["niva"] == ""
    senere, _ = _koble(tmp_path, [], [], treff, dag=date(2026, 10, 14) + timedelta(days=61))
    assert senere["journalposter"] == []


def test_feil_i_postlista_beholder_treffene(tmp_path):
    tann = dict(next(h for h in HORINGER if h["id"] == "e4f7f112e5d1"))
    _koble(tmp_path, [_jp("2026/85652", "2026-10-20")], [dict(tann)])
    _, status = _koble(tmp_path, [], [tann], status="feil")
    assert status[0]["status"] == "feil"
    assert tann["postliste"][0]["niva"] == SIKKER  # forrige journalposter er beholdt


def test_uavklart_faar_ikke_sikkert_treff():
    treff = KOBLING.beste(POSTER["2026/81758"], HORINGER)
    assert treff.niva != SIKKER
