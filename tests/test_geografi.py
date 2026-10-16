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
    ],
)
def test_ikke_relevant(filter_, tekst):
    assert not filter_.vurder(tekst).relevant, tekst


def test_grunn_oppgis(filter_):
    assert filter_.vurder("Rv. 4 Lygna").grunn == "rv. 4"
    assert filter_.vurder("E6 ved Eidsvoll").grunn == "E6 og Eidsvoll"
