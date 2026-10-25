from pathlib import Path

import pytest
import yaml

from horinger.geografi import GeografiFilter

KONFIG = yaml.safe_load(
    (Path(__file__).resolve().parent.parent / "sources.yaml").read_text(encoding="utf-8")
)["felles"]["geografi"]


@pytest.fixture
def filter_():
    return GeografiFilter(KONFIG)


@pytest.mark.parametrize(
    "tekst",
    [
        "Reguleringsplan for gang- og sykkelveg i Gjøvik",
        "Varsel om oppstart – Fv. 33 Østre Toten",
        "Ny bru i Gran sentrum",
        "Kryssutbedring i Sør-Aurdal",
        "Rv. 4 Roa–Gran grense, offentlig ettersyn",
        "rv4 Nittedal, varsel om oppstart",
        "Riksveg 4 gjennom Oslo",
        "E6 Gardermoen–Eidsvoll, ny reguleringsplan",
        "E 6 ved Ullensaker",
        "Høringsfrist 11. november 2026 Gjøvik kommune er berørt",
    ],
)
def test_relevant(filter_, tekst):
    assert filter_.vurder(tekst).relevant, tekst


@pytest.mark.parametrize(
    "tekst",
    [
        "Granåsen vindkraftverk",
        "E39 Grungen bru",
        "E6 Ranheim–Værnes",
        "Ny sykkelveg i Oslo sentrum",
        "Nittedal sentrum, kollektivfelt",
        "Rv. 40 Kongsberg",
        "E16 Sandvika–Wøyen",
        "stangenes lengde og gran-trær",
        "Merknader sendes til Statens vegvesen, postboks 1010 Nordre Ål, 2605 Lillehammer "
        "innan 30. oktober 2026.",
        "Kontakt: Statens vegvesen, Postboks 1010, 2815 Gjøvik",
    ],
)
def test_ikke_relevant(filter_, tekst):
    assert not filter_.vurder(tekst).relevant, tekst


def test_grunn_oppgis(filter_):
    assert filter_.vurder("Rv. 4 Lygna").grunn == "rv. 4"
    assert filter_.vurder("E6 ved Eidsvoll").grunn == "E6 og Eidsvoll"


def test_kommune_i_tekst_teller_selv_om_adresse_fjernes(filter_):
    tekst = "Planen gjelder Hunndalen i Gjøvik. Postboks 1010 Nordre Ål, 2605 Lillehammer."
    assert filter_.vurder(tekst).grunn == "kommune: Gjøvik"


def test_tettsted_gir_treff():
    filter_ = GeografiFilter({"kommuner": ["Ringsaker"], "steder": ["Moelv"]})
    assert filter_.vurder("Starter reguleringsarbeid i Moelv").grunn == "sted: Moelv"
    assert not filter_.vurder("Starter reguleringsarbeid i Moss").relevant
