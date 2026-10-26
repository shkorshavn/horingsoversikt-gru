from horinger.nett import Robots, robots_tekst

AGENT = "HoringsoversiktGRU/0.1 (+mailto:test@example.no)"


def test_robots_bare_page_tillatt():
    tekst = """
User-agent: *
Disallow: /*?ownerid
Disallow: /*?documenttype
Disallow: /Utilities/RSSEngine/
Crawl-delay: 2
"""
    r = Robots.tolk(tekst, AGENT)
    assert r.tillatt("/no/dokument/hoyringar/id1763/?page=2")
    assert not r.tillatt("/no/dokument/hoyringar/id1763/?ownerid=123")
    assert not r.tillatt("/Utilities/RSSEngine/x")
    assert r.crawl_delay == 2


def test_robots_lengste_regel_vinner():
    tekst = "User-agent: *\nDisallow: /innsyn\nAllow: /innsyn/offentlig\n"
    r = Robots.tolk(tekst, AGENT)
    assert not r.tillatt("/innsyn/x")
    assert r.tillatt("/innsyn/offentlig/side")


def test_robots_egen_gruppe_for_agent():
    tekst = "User-agent: *\nDisallow: /\n\nUser-agent: HoringsoversiktGRU\nAllow: /\n"
    assert Robots.tolk(tekst, AGENT).tillatt("/hva/som/helst")


def test_robots_dollartegn():
    r = Robots.tolk("User-agent: *\nDisallow: /*.pdf$\n", AGENT)
    assert not r.tillatt("/globalassets/fil.pdf")
    assert r.tillatt("/side.pdf.html")


def test_robots_tom_er_alt_tillatt():
    assert Robots.tolk("", AGENT).tillatt("/")


def test_robots_flere_agenter_i_samme_gruppe():
    tekst = "User-agent: googlebot\nUser-agent: *\nDisallow: /sok/\n"
    assert not Robots.tolk(tekst, AGENT).tillatt("/sok/x")


def test_nettverksfeil_ved_robots_er_ikke_sperre(monkeypatch):
    import pytest
    import requests

    from horinger.nett import Nett, RobotsUtilgjengelig, SperretAvRobots

    nett = Nett(user_agent="test", pause=0, tidsavbrudd=1)

    def feiler(*_a, **_k):
        raise requests.ConnectionError("[Errno 101] Network is unreachable")

    monkeypatch.setattr(nett.okt, "get", feiler)
    with pytest.raises(RobotsUtilgjengelig) as feil:
        nett.hent("https://www.vegvesen.no/x")
    assert not isinstance(feil.value, SperretAvRobots)
    assert nett.antall_kall == 0


def test_utf8_naar_tegnsett_mangler():
    import requests

    from horinger.nett import _rett_tegnsett

    svar = requests.Response()
    svar._content = "Ute på høring".encode()
    svar.headers["Content-Type"] = "text/html"
    svar.encoding = "ISO-8859-1"
    _rett_tegnsett(svar)
    assert svar.text == "Ute på høring"
    svar.headers["Content-Type"] = "text/html; charset=windows-1252"
    svar.encoding = "windows-1252"
    _rett_tegnsett(svar)
    assert svar.encoding == "windows-1252"


def test_robots_med_byte_order_mark():
    """Skatteetatens robots.txt begynner med BOM. Reglene for «*» skal likevel gjelde."""
    tekst = "﻿User-agent: *\nDisallow: /contentassets\nDisallow: /sok\n"
    robots = Robots.tolk(tekst, "HoringsoversiktGRU/0.1")
    assert not robots.tillatt("/contentassets/9f72203550404410b5da06ef31d929cb/liste.pdf")
    assert robots.tillatt("/rettskilder/type/horinger/")


def test_robots_tekst_med_bom_uten_tegnsett():
    """Slik Skatteetaten svarer: BOM først og ingen charset i Content-Type."""
    innhold = "\ufeffUser-agent: *\nDisallow: /contentassets\n".encode()
    robots = Robots.tolk(robots_tekst(innhold), "HoringsoversiktGRU/0.1")
    assert not robots.tillatt(
        "/contentassets/25088935421644869d69846ca51862c2/2026-10-horingsliste.pdf"
    )
