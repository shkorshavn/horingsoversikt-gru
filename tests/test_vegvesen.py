from datetime import date
from pathlib import Path

import yaml

from horinger.geografi import GeografiFilter
from horinger.kilder.vegvesen import Vegvesen, tolk_prosjekter, tolk_regelverk

FIXTURES = Path(__file__).parent / "fixtures"
REGELVERK = "https://www.vegvesen.no/fag/publikasjoner/hoeringer/"
PROSJEKTER = "https://www.vegvesen.no/vegprosjekter/hoeringer-vegprosjekter/"
GEOGRAFI = yaml.safe_load(
    (Path(__file__).parent.parent / "sources.yaml").read_text(encoding="utf-8")
)["felles"]["geografi"]


def _les(navn):
    return (FIXTURES / navn).read_text(encoding="utf-8")


def test_regelverk_tolkes():
    rader = tolk_regelverk(_les("vegvesen_regelverk.html"), REGELVERK)
    assert len(rader) > 400  # hele historikken ligger på én side
    forste = rader[0]
    assert forste["tittel"] == "Høring – endring i vegtrafikkloven"
    assert forste["lenke"] == (
        "https://www.vegvesen.no/fag/publikasjoner/hoeringer/"
        "horing--endring-i-vegtrafikkloven-20-38820/"
    )
    assert forste["frist"] == date(2027, 1, 9)
    assert forste["frist_tekst"] == "Høringsfrist: 09.01.2027"
    assert "Referanse: 20-38820." in forste["ingress"]


def test_regelverk_alle_har_frist():
    rader = tolk_regelverk(_les("vegvesen_regelverk.html"), REGELVERK)
    uten = [r["tittel"] for r in rader if r["frist"] is None]
    assert len(uten) <= 5, uten


def test_prosjekter_tolkes():
    rader = tolk_prosjekter(_les("vegvesen_prosjekter.html"), PROSJEKTER)
    assert len(rader) == 7
    forste = rader[0]
    assert forste["tittel"] == "Rv. 13 Førland bru: Reguleringsplan leggast på offentleg ettersyn"
    assert forste["frist"] == date(2026, 11, 16)
    assert forste["publisert"] == date(2026, 10, 1)
    # «Publisert 24.09.2026» uten kolon
    assert rader[1]["publisert"] == date(2026, 9, 24)


def test_prosjekter_i_fixture_er_ikke_relevante():
    filter_ = GeografiFilter(GEOGRAFI)
    rader = tolk_prosjekter(_les("vegvesen_prosjekter.html"), PROSJEKTER)
    assert not any(filter_.vurder(f"{r['tittel']} {r['lenke']}").relevant for r in rader)


class FalskNett:
    def __init__(self, sider):
        self.sider = sider
        self.kall = []

    def hent(self, url, **_):
        self.kall.append(url)

        class Svar:
            text = self.sider.get(url, "<main>Ingen treff</main>")

        return Svar()


def test_hent_filtrerer_prosjekter_geografisk():
    prosjekt_html = """<main><div class="editorial">
      <h2>Rv. 4 Lygna sør</h2><p>Publisert: 01.10.2026<br>Merknadsfrist: 20.11.2026</p>
      <p><a href="/vegprosjekter/riksveg/rv4/varsel">Varsel om oppstart</a></p>
      <h2>E39 Grungen bru</h2><p>Publisert: 24.09.2026<br>Merknadsfrist: 02.11.2026</p>
      <p><a href="/vegprosjekter/e39/grungen">Varsel om oppstart</a></p>
      <h2>E6 Moelv</h2><p>Publisert: 20.09.2026<br>Merknadsfrist: 01.12.2026</p>
      <p><a href="/vegprosjekter/e6/moelv">Offentlig ettersyn</a></p>
    </div></main>"""
    nett = FalskNett(
        {
            REGELVERK: "<html></html>",
            PROSJEKTER: prosjekt_html,
            "https://www.vegvesen.no/vegprosjekter/e6/moelv": (
                "<main>Planen ligger i Ringsaker kommune.</main>"
            ),
        }
    )
    konfig = {"navn": "Statens vegvesen", "url": REGELVERK, "prosjekt_url": PROSJEKTER}
    kilde = Vegvesen(konfig, nett, {"geografi": GEOGRAFI})
    titler = [h.tittel for h in kilde.hent()]
    assert titler == ["Rv. 4 Lygna sør: Varsel om oppstart", "E6 Moelv: Offentlig ettersyn"]
    # Detaljsiden hentes bare når listen ikke gir treff
    assert "https://www.vegvesen.no/vegprosjekter/riksveg/rv4/varsel" not in nett.kall
