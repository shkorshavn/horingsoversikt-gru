"""Tester av deduplisering og foreslått prioritet (sprint 4)."""

from datetime import date
from pathlib import Path

import yaml

from horinger.datoer import frist_etter_ord, fristtekst, setning_med_frist
from horinger.dedup import dedupliser, like, nokkelord
from horinger.prioritet import Prioritet

KONFIG = yaml.safe_load((Path(__file__).parent.parent / "sources.yaml").read_text("utf-8"))
REGJ = next(k for k in KONFIG["kilder"] if k["navn"] == "Regjeringen.no")


def _h(kilde, tittel, frist, lenke=None):
    return {
        "id": lenke or tittel,
        "kilde": kilde,
        "tittel": tittel,
        "frist": frist,
        "lenke": lenke or f"https://example.no/{kilde}/{abs(hash(tittel))}",
    }


# ---------- Deduplisering ----------
# I dataene 25.10.2026 fantes ingen høring både hos en ny etat og på regjeringen.no. Eksemplene
# under bruker ekte titler fra DiBK og Miljødirektoratet, med titlene slik regjeringen.no
# typisk skriver dem («Høring – …», «Høyring av …»). Se rapporten for sprint 4.


def test_eksempel_1_dibk_og_regjeringen():
    dibk = _h("DiBK", "Forslag til endringer i klimakrav i byggteknisk forskrift", "2026-05-05")
    regj = _h(
        "Regjeringen.no", "Høring – endringer i klimakrav i byggteknisk forskrift", "2026-05-05"
    )
    (h,) = dedupliser([regj, dibk])
    assert h["kilde"] == "DiBK"
    assert h["ogsa"] == [{"kilde": "Regjeringen.no", "lenke": regj["lenke"]}]


def test_eksempel_2_miljodirektoratet_og_regjeringen():
    miljo = _h(
        "Miljødirektoratet",
        "Høring av forslag til endringer i forurensningsforskriften kapittel 10. "
        "Utslipp fra krematorier",
        "2026-12-31",
    )
    regj = _h(
        "Regjeringen.no",
        "Høyring av forslag til endringar i forurensningsforskriften kapittel 10 – "
        "utslipp frå krematorier",
        "2026-12-31",
    )
    (h,) = dedupliser([miljo, regj])
    assert h["kilde"] == "Miljødirektoratet"
    assert h["ogsa"][0]["kilde"] == "Regjeringen.no"


def test_ulik_frist_slaas_ikke_sammen():
    a = _h("DiBK", "Forslag til endringer i energikrav i byggteknisk forskrift", "2026-05-05")
    b = _h(
        "Regjeringen.no", "Forslag til endringer i energikrav i byggteknisk forskrift", "2026-06-05"
    )
    assert len(dedupliser([a, b])) == 2


def test_lignende_titler_slaas_ikke_sammen():
    """Klimakrav og energikrav har samme frist og nesten samme tittel, men er to høringer."""
    a = _h("DiBK", "Forslag til endringer i klimakrav i byggteknisk forskrift", "2026-05-05")
    b = _h("DiBK", "Forslag til endringer i energikrav i byggteknisk forskrift", "2026-05-05")
    c = _h(
        "Regjeringen.no", "Høring – endringer i energikrav i byggteknisk forskrift", "2026-05-05"
    )
    resultat = dedupliser([a, b, c])
    assert len(resultat) == 2
    assert not like(a, b)


def test_uten_frist_slaas_ikke_sammen():
    a = _h("NVE", "Forslag til endringer i økodesignforskriften", None)
    b = _h("Regjeringen.no", "Forslag til endringer i økodesignforskriften", None)
    assert len(dedupliser([a, b])) == 2


def test_nokkelord():
    assert nokkelord("Høring – forslag til endringer i TEK17 kapittel 14") == {
        "tek17",
        "kapittel",
        "14",
    }


# ---------- Prioritet ----------


def test_departement_med_hoy_prioritet():
    p = Prioritet(KONFIG["felles"])
    h = {"instans": "Kunnskapsdepartementet", "tittel": "Høring om studiestøtte", "ingress": ""}
    assert p.vurder(h, REGJ) == (1, "")


def test_departement_med_middels_prioritet():
    p = Prioritet(KONFIG["felles"])
    h = {"instans": "Forsvarsdepartementet", "tittel": "Høring om etterretning", "ingress": ""}
    assert p.vurder(h, REGJ) == (2, "")


def test_lofting_naar_det_gjelder_kommunene():
    p = Prioritet(KONFIG["felles"])
    h = {
        "instans": "Justis- og beredskapsdepartementet",
        "tittel": "Høring av forskrift om tilfluktssteder",
        "ingress": "Forslaget gir kommunene ansvar for å kartlegge tilfluktsrom.",
    }
    assert p.vurder(h, REGJ) == (1, "gjelder kommunene")


def test_lofting_naar_det_gjelder_regionen():
    p = Prioritet(KONFIG["felles"])
    h = {
        "instans": "Samferdselsdepartementet",
        "tittel": "Høring om ny bru ved Raufoss",
        "ingress": "",
    }
    assert p.vurder(h, REGJ) == (1, "gjelder regionen")


def test_kilde_uten_instansliste():
    p = Prioritet(KONFIG["felles"])
    assert p.vurder({"instans": "NVE", "tittel": "x"}, {"prioritet": 1}) == (1, "")


# ---------- Datohjelpere for detaljsider ----------


def test_frist_etter_ord_tar_ikke_forste_dato():
    tekst = "Publisert 05.10.2026. Forskrift av 23.2.2011 nr. 190. Høringsfrist er 15. mars 2026."
    assert frist_etter_ord(tekst) == date(2026, 3, 15)


def test_frist_etter_ord_innenfor_teller_ikke():
    assert frist_etter_ord("Områdene innenfor 1. mai 2026 berøres.") is None


def test_setning_med_frist_deler_ikke_ved_dato():
    tekst = "Bakgrunn. Høringsfrist er 15. mars 2026. Svar sendes til NVE."
    assert setning_med_frist(tekst) == "Høringsfrist er 15. mars 2026"


def test_fristtekst():
    assert (
        fristtekst(date(2026, 7, 3), "Kort setning innen 3. juli 2026")
        == "Kort setning innen 3. juli 2026"
    )
    assert fristtekst(date(2026, 7, 3), "x" * 200) == "Frist: 03.07.2026"
    assert (
        fristtekst(None, "innen høringsfristen desember 2026")
        == "innen høringsfristen desember 2026"
    )


# ---------- Sprint 5: månedsfrist og ingress ----------


def test_frist_med_bare_maned():
    from horinger.datoer import finn_frist_maned

    assert finn_frist_maned("innen høringsfristen desember 2026") == (2026, 12)
    assert finn_frist_maned("Frist for innspill: mars 2027.") == (2027, 3)
    assert finn_frist_maned("Høringsfrist er 15. desember 2026") is None
    assert finn_frist_maned("fra midten av april til midten av juni") is None


def test_lag_hoering_med_maanedsfrist():
    from horinger.kilder.base import Kilde

    class K(Kilde):
        def hent(self):
            return []

    h = K({"navn": "NVE"}, nett=None).lag_hoering(
        instans="NVE",
        tittel="Økodesign",
        lenke="https://x",
        frist=None,
        frist_tekst="…innspill innen høringsfristen desember 2026…",
    )
    assert h.frist == date(2026, 12, 1)  # første dag i måneden (Svein 25.10.2026)
    assert h.frist_maned == "2026-12"
    assert h.frist_tekst == "Høringsfrist: desember 2026"


def test_ingress_kuttes_ved_helt_ord():
    from horinger.datoer import kort_ingress

    tekst = "energimerkeforskriften " * 30
    kort = kort_ingress(tekst, maks=100)
    assert kort.endswith("energimerkeforskriften…")
    assert len(kort) <= 101
    assert kort_ingress("kort tekst") == "kort tekst"


def test_innenriks_er_ikke_fristord():
    """Skatteetaten 25.10.2026: «innenriks kvotepliktig sjøfart» ble tatt for en frist."""
    assert frist_etter_ord("gjelder innenriks sjøfart fra 1. januar 2027") is None
    assert setning_med_frist("Dette gjelder innenriks sjøfart fra 1. januar.") == ""
