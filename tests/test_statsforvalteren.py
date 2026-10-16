from datetime import date
from pathlib import Path

from horinger.kilder.statsforvalteren import referansedato, tolk_liste

FIXTURES = Path(__file__).parent / "fixtures"
URL = "https://www.statsforvalteren.no/innlandet/horinger/"


def test_liste_tolkes():
    (rad,) = tolk_liste((FIXTURES / "statsforvalteren.html").read_text(encoding="utf-8"), URL)
    assert rad["tittel"] == "Oppstart av verneprosess - Frivillig vern av skog - Syv områder"
    assert rad["lenke"] == (
        "https://www.statsforvalteren.no/nb/innlandet/horinger/2026/10/"
        "oppstart-av-verneprosess---frivillig-vern-av-skog---syv-omrader/"
    )
    assert rad["frist"] == date(2026, 10, 16)
    assert rad["frist_tekst"] == "Høringsfrist: 16. oktober kl. 23:59"
    assert rad["ingress"].startswith("Statsforvalteren har startet opp verneprosess")
    assert rad["instans"] == "Statsforvalteren i Innlandet"


def test_frist_over_arsskiftet():
    html = """<a class="ds-card" href="/nb/innlandet/horinger/2026/11/plan/">
      <h2 class="ds-card-title">Plan</h2>
      <div><span class="ds-font-weight-bold">Høringsfrist:</span> 15. januar kl. 12:00</div></a>"""
    (rad,) = tolk_liste(html, URL)
    assert rad["frist"] == date(2027, 1, 15)


def test_referansedato_uten_ar_i_adressen_bruker_i_dag():
    assert referansedato("https://www.statsforvalteren.no/innlandet/horinger/x/") <= date.today()
