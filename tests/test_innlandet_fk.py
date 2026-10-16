from datetime import date
from pathlib import Path

from horinger.kilder.innlandet_fk import InnlandetFylkeskommune, tolk_liste

FIXTURES = Path(__file__).parent / "fixtures"
URL = "https://innlandetfylke.no/politikk/horinger/"


def test_liste_tolkes():
    rader = tolk_liste((FIXTURES / "innlandet_fk.html").read_text(encoding="utf-8"), URL)
    assert [r["tittel"] for r in rader] == [
        "Oppstart av reguleringsplanarbeid for fv. 213 Skog bru i Ringsaker kommune",
        "Planprogram på høring: Regional plan for nettinfrastrukturen for energi",
    ]
    skog, nett = rader
    assert skog["frist"] == date(2026, 11, 13)
    assert skog["frist_tekst"] == "Frist for innspill til planarbeidet er 13. november 2026."
    assert skog["lenke"] == (
        "https://innlandetfylke.no/politikk/horinger/"
        "oppstart-av-reguleringsplanarbeid-for-fv-213-skog-bru-i-ringsaker-kommune.82328.aspx"
    )
    assert nett["frist"] == date(2026, 11, 11)
    assert nett["frist_tekst"] == "Høringsfrist er 11. november 2026."
    assert skog["instans"] == "Innlandet fylkeskommune"


def test_detaljside_brukes_uten_frist_i_ingressen():
    liste = """<div class="article-preview"><h3 class="article-preview-title">
      <a href="/politikk/horinger/x.1.aspx">Regional plan</a></h3>
      <div class="article-preview-excerpt"><p>Planen er lagt ut.</p></div></div>"""
    detalj = "<main><p>Frist for å sende innspill er 3. desember 2026.</p></main>"

    class Nett:
        def hent(self, url, **_):
            class Svar:
                text = liste if url == URL else detalj

            return Svar()

    kilde = InnlandetFylkeskommune({"navn": "Innlandet fylkeskommune", "url": URL}, Nett())
    (h,) = kilde.hent()
    assert h.frist == date(2026, 12, 3)
    assert h.frist_tekst == "Frist for å sende innspill er 3. desember 2026."
