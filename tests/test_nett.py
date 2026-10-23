from horinger.nett import Robots

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
