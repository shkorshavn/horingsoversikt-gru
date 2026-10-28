"""Tester av nettsiden i Chromium (Playwright), med egne testdata og fast dato.

Krever Playwright med Chromium og axe-core (se README, «Tester og kodekvalitet»).
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from playwright.sync_api import Page, sync_playwright

ROT = Path(__file__).resolve().parent.parent
I_DAG = "2026-10-17"


def _h(id_, frist, **ekstra):
    data = {
        "id": id_,
        "kilde": "Statens vegvesen",
        "kategori": "Transport, samferdsel og infrastruktur",
        "niva": "Direktorater og etater",
        "prioritet": 1,
        "instans": "Statens vegvesen",
        "tittel": f"Høring {id_}",
        "lenke": f"https://example.no/{id_}",
        "frist": frist,
        "frist_tekst": f"Høringsfrist: {frist}" if frist else "",
        "publisert": None,
        "ingress": "",
        "hentet": "2026-10-17T10:00:00+02:00",
    }
    data.update(ekstra)
    return data


HORINGER = {
    "generert": "2026-10-17T10:05:00+02:00",
    "antall": 10,
    "horinger": [
        _h(
            "d31",
            "2026-11-17",
            tittel="Høring om barnehageloven",
            kategori="Oppvekst",
            niva="Regjeringen",
            instans="Kunnskapsdepartementet",
            kilde="Regjeringen.no",
            prioritet_grunn="regionen er høringspart",
            horingsparter=["Alle kommuner", "KS", "Utdanningsdirektoratet", "Utdanningsforbundet"],
            partkategorier={
                "Alle kommuner": 1,
                "Kommuner og fylkeskommuner": 1,
                "Departementer og direktorater": 1,
                "Organisasjoner": 1,
            },
            regionflagg=["Alle kommuner", "KS"],
            saksfelt=["Barnehager"],
        ),
        _h("d13", "2026-10-30", tittel='Høring om æ, ø og å; «sitat» og "anførsel"'),
        _h(
            "d14",
            "2026-10-31",
            tittel="Fjorten dager",
            ny=True,
            forst_sett="2026-10-15",
            horingsparter_merknad="Åpen for alle",
        ),
        _h(
            "d30",
            "2026-11-16",
            tittel="Tretti dager",
            ingress="Gjelder rv. 4 ved Gjøvik.",
            prioritet_grunn="gjelder regionen",
            horingsparter_merknad="Ikke tilgjengelig",
            horingsparter_lenke="https://example.no/liste.pdf",
            ogsa=[
                {"kilde": "Regjeringen.no", "lenke": "https://www.regjeringen.no/x"},
                {"kilde": "Farlig", "lenke": "javascript:alert(1)"},
            ],
        ),
        _h(
            "d0",
            "2026-10-17",
            tittel="Frist i dag",
            instans="Stortinget, Justiskomiteen",
            kilde="Stortinget",
            niva="Stortinget",
            kategori="Stortinget",
        ),
        _h("prio3", "2026-10-25", tittel="Lav prioritet", prioritet=3),
        _h("ukjent", None, tittel="Uten frist"),
        _h(
            "maned",
            "2026-12-01",
            tittel="Frist bare med måned",
            frist_maned="2026-12",
            frist_tekst="Høringsfrist: desember 2026",
            kilde="NVE",
            instans="NVE",
        ),
        _h("farlig", "2026-11-12", tittel="Lenke uten http", lenke="javascript:alert(1)"),
        _h(
            "fylke",
            "2026-11-11",
            tittel="Regional plan",
            niva="Fylkeskommunen",
            kategori="Regionale ledd",
            instans="Innlandet fylkeskommune",
            kilde="Innlandet fylkeskommune",
        ),
    ],
}

ARKIV = {
    "generert": "2026-10-17T10:05:00+02:00",
    "antall": 3,
    "horinger": [
        _h("utlopt", "2026-10-16", tittel="Utløpt i går", utlopt="2026-10-16"),
        _h("d-30", "2026-09-17", tittel="Utløpt for 30 dager siden", utlopt="2026-09-17"),
        _h("gammel", "2026-09-16", tittel="Utløpt for 31 dager siden", utlopt="2026-09-16"),
    ],
}

OK = "2026-10-17T10:01:00+02:00"
STATUS = {
    "generert": "2026-10-17T10:05:00+02:00",
    "kilder": [
        {"kilde": "Stortinget", "status": "ok", "hentet": OK, "sist_ok": OK, "antall": 1},
        {
            "kilde": "Regjeringen.no",
            "kjoring": "pc",
            "status": "feil",
            "hentet": OK,
            "sist_ok": "2026-10-12T10:02:00+02:00",
            "antall": 1,
            "feil": "HTTPError: 403 Client Error: Forbidden for url: https://x",
        },
        {"kilde": "Statens vegvesen", "status": "ok", "hentet": OK, "sist_ok": OK, "antall": 6},
        {"kilde": "Innlandet fylkeskommune", "status": "ok", "hentet": OK, "sist_ok": OK},
        {
            "kilde": "Statsforvalteren i Innlandet",
            "status": "feil",
            "hentet": OK,
            "sist_ok": None,
            "feil": "ReadTimeout: timed out",
        },
        {
            "kilde": "Miljødirektoratet",
            "status": "utdatert",
            "hentet": "2026-10-05T10:01:00+02:00",
            "sist_ok": "2026-10-05T10:01:00+02:00",
        },
        {"kilde": "NVE", "status": "ikke hentet", "antall": 0},
        {"kilde": "DSB", "status": "ikke overvåket", "antall": 0},
        {"kilde": "Udir", "status": "ikke overvåket", "antall": 0},
    ],
}


def _lag_nettsted(
    mappe: Path, horinger=HORINGER, status=STATUS, arkiv=ARKIV, postliste=None
) -> Path:
    shutil.copy(ROT / "index.html", mappe / "index.html")
    shutil.copytree(ROT / "side", mappe / "side")
    (mappe / "data").mkdir()
    if horinger is not None:
        (mappe / "data" / "horinger.json").write_text(
            json.dumps(horinger, ensure_ascii=False), encoding="utf-8"
        )
    if status is not None:
        (mappe / "data" / "status.json").write_text(
            json.dumps(status, ensure_ascii=False), encoding="utf-8"
        )
    if arkiv is not None:
        (mappe / "data" / "arkiv.json").write_text(
            json.dumps(arkiv, ensure_ascii=False), encoding="utf-8"
        )
    if postliste is not None:
        (mappe / "data" / "postliste_treff.json").write_text(
            json.dumps(postliste, ensure_ascii=False), encoding="utf-8"
        )
    return mappe


class _StilleHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


@pytest.fixture(scope="module")
def nettleser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def server():
    """Starter en lokal webserver for en mappe og gir tilbake adressen."""
    servere = []

    def start(mappe: Path) -> str:
        handler = functools.partial(_StilleHandler, directory=str(mappe))
        s = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=s.serve_forever, daemon=True).start()
        servere.append(s)
        return f"http://127.0.0.1:{s.server_port}"

    yield start
    for s in servere:
        s.shutdown()


def _apne(nettleser, url: str, bredde: int = 1280, sti: str = "/index.html") -> Page:
    side = nettleser.new_page(viewport={"width": bredde, "height": 900}, accept_downloads=True)
    side.add_init_script(f"window.HORINGER_I_DAG = '{I_DAG}';")
    side.feil = []
    side.on("pageerror", lambda e: side.feil.append(str(e)))
    side.goto(url + sti)
    side.wait_for_selector("html[data-klar]")
    return side


@pytest.fixture
def side(nettleser, server, tmp_path):
    s = _apne(nettleser, server(_lag_nettsted(tmp_path)))
    yield s
    assert s.feil == [], s.feil
    s.close()


def _titler(side: Page) -> list[str]:
    return side.locator("#liste .hoering h2 > :first-child").all_inner_texts()


# ---------- Sortering og standardvisning ----------


def test_sortert_pa_frist_uten_utlopte_og_prio3(side):
    assert _titler(side) == [
        "Frist i dag",
        'Høring om æ, ø og å; «sitat» og "anførsel"',
        "Fjorten dager",
        "Regional plan",
        "Lenke uten http",
        "Tretti dager",
        "Høring om barnehageloven",
        "Frist bare med måned",
        "Uten frist",
    ]
    assert side.inner_text("#antall") == "Viser 9 høringer (10 åpne totalt, 1 ny siste uke)"


@pytest.mark.parametrize(
    "id_, klasse, tekst",
    [
        ("d0", "snart", "Frist i dag"),
        ("d13", "snart", "13 dager igjen"),
        ("d14", "middels", "14 dager igjen"),
        ("d30", "middels", "30 dager igjen"),
        ("d31", "godtid", "31 dager igjen"),
        ("ukjent", "ukjent", "Frist ikke oppgitt"),
    ],
)
def test_fargeklasse_og_tekst(side, id_, klasse, tekst):
    frist = side.locator(f'.hoering[data-id="{id_}"] .frist')
    assert klasse in frist.get_attribute("class").split()
    assert frist.locator(".igjen").inner_text() == tekst


def test_dato_vises_i_norsk_format(side):
    rad = side.locator('.hoering[data-id="d31"] .frist')
    assert rad.locator(".dag").inner_text() == "17"
    assert rad.locator(".maned").inner_text() == "nov."
    assert rad.locator(".skjult").inner_text().startswith("Frist 17. november 2026")


def test_lenke_til_kilden(side):
    lenke = side.locator('.hoering[data-id="d31"] h2 a')
    assert lenke.get_attribute("href") == "https://example.no/d31"


# ---------- Filtre ----------


def _vis_utlopte(side):
    side.check("#utlopte")
    side.wait_for_selector("html[data-arkiv]")


def test_utlopte_kan_vises(side):
    _vis_utlopte(side)
    titler = _titler(side)
    assert titler[:2] == ["Utløpt for 30 dager siden", "Utløpt i går"]
    assert "Utløpt for 31 dager siden" not in titler
    frist = side.locator('.hoering[data-id="utlopt"] .frist')
    assert "utlopt" in frist.get_attribute("class")
    assert frist.locator(".igjen").inner_text() == "Fristen er ute"


def test_prioritet_3(side):
    side.check('input[name="prio"][value="3"]')
    assert "Lav prioritet" in _titler(side)
    side.uncheck('input[name="prio"][value="1"]')
    assert _titler(side) == ["Lav prioritet"]


def _kryss(side, gruppe, verdi):
    side.check(f'#{gruppe} input[value="{verdi}"]')


def test_kategori(side):
    _kryss(side, "kategori", "Oppvekst")
    assert _titler(side) == ["Høring om barnehageloven"]


def test_niva(side):
    _kryss(side, "niva", "Fylkeskommunen")
    assert _titler(side) == ["Regional plan"]


def test_flere_temaer_og_avsendere(side):
    """Svein 25.10.2026: Tema og Avsender skal kunne ha ett eller flere valg."""
    _kryss(side, "kategori", "Oppvekst")
    _kryss(side, "kategori", "Regionale ledd")
    assert sorted(_titler(side)) == ["Høring om barnehageloven", "Regional plan"]
    assert "kategori=Oppvekst&kategori=Regionale+ledd" in side.url
    side.click("#nullstill")
    _kryss(side, "niva", "Fylkeskommunen")
    _kryss(side, "niva", "Stortinget")
    assert sorted(_titler(side)) == ["Frist i dag", "Regional plan"]
    info = side.inner_text("#utskrift-info")
    assert (
        "avsender Stortinget og Fylkeskommunen" in info
        or "avsender Fylkeskommunen og Stortinget" in info
    )


def test_flere_valg_leses_fra_adressen(nettleser, server, tmp_path):
    url = server(_lag_nettsted(tmp_path))
    sti = "/index.html?kategori=Oppvekst&kategori=Regionale+ledd"
    side = _apne(nettleser, url, sti=sti)
    assert side.is_checked('#kategori input[value="Oppvekst"]')
    assert side.is_checked('#kategori input[value="Regionale ledd"]')
    assert len(_titler(side)) == 2
    side.close()


def test_fritekst_flere_ord_og_store_bokstaver(side):
    side.fill("#sok", "RV. 4 gjøvik")
    assert _titler(side) == ["Tretti dager"]
    side.fill("#sok", "justiskomiteen")
    assert _titler(side) == ["Frist i dag"]


def test_tom_visning_og_nullstill(side):
    side.fill("#sok", "finnes ikke")
    assert _titler(side) == []
    assert side.is_visible("#tom")
    assert side.is_disabled("#eksport")
    side.click("#nullstill-tom")
    assert len(_titler(side)) == 9
    assert side.is_hidden("#tom")


def test_filtre_skrives_til_adressen(side):
    side.fill("#sok", "plan")
    _kryss(side, "niva", "Fylkeskommunen")
    side.check('input[name="prio"][value="3"]')
    assert side.url.endswith("?q=plan&niva=Fylkeskommunen&prio=1%2C2%2C3")


def test_filtre_leses_fra_adressen(nettleser, server, tmp_path):
    url = server(_lag_nettsted(tmp_path))
    side = _apne(nettleser, url, sti="/index.html?q=i+går&prio=1&utlopte=1")
    assert _titler(side) == ["Utløpt i går"]
    assert side.is_checked("#utlopte")
    assert not side.is_checked('input[name="prio"][value="2"]')
    side.close()


# ---------- CSV ----------


def test_csv_eksport(side):
    side.fill("#sok", "sitat")
    with side.expect_download() as nedlasting:
        side.click("#eksport")
    fil = nedlasting.value
    assert fil.suggested_filename == f"horinger-gjovikregionen-{I_DAG}.csv"
    innhold = Path(fil.path()).read_bytes()
    assert innhold.startswith(b"\xef\xbb\xbf")
    tekst = innhold.decode("utf-8-sig")
    linjer = tekst.split("\r\n")
    assert linjer[0].startswith("Frist;Dager igjen;Høringsinstans;Tittel;")
    assert linjer[1] == (
        "30. oktober 2026;13;Statens vegvesen;"
        '"Høring om æ, ø og å; «sitat» og ""anførsel""";'
        "Transport, samferdsel og infrastruktur;Direktorater og etater;1;"
        "Høringsfrist: 2026-10-30;;;;;;;;https://example.no/d13"
    )
    assert linjer[2] == ""


# ---------- Status ----------


def _rad(side, kilde):
    return side.locator("#status-tabell tbody tr").filter(has=side.locator("th", has_text=kilde))


def test_statusoversikt(side):
    assert side.locator("#status-tabell tbody tr").count() == 7
    assert side.locator("#status-tabell thead th").all_inner_texts() == [
        "Kilde",
        "Status",
        "Sist hentet",
        "Åpne høringer",
    ]
    vegvesen = _rad(side, "Statens vegvesen").locator("td")
    assert vegvesen.nth(0).inner_text() == "Hentet"
    assert vegvesen.nth(1).inner_text() == "17. oktober 2026 kl. 10.01"
    assert vegvesen.nth(2).inner_text() == "6"
    assert side.inner_text("#antall-inaktive") == "2"
    assert "3 kilder kunne ikke hentes" in side.inner_text("#status-ingress")
    assert "17. oktober 2026 kl. 10.05" in side.inner_text("#oppdatert")


def test_status_feil_med_tidligere_data(side):
    regj = _rad(side, "Regjeringen.no").locator("td")
    tekst = regj.nth(0).inner_text()
    assert "Feil" in tekst
    assert "Nettstedet avviste innhentingen (feilkode 403)." in tekst
    assert "Viser høringene fra 12. oktober 2026 kl. 10.02." in tekst
    assert "PC hos Gjøvikregionen Utvikling" in tekst
    assert regj.nth(1).inner_text() == "12. oktober 2026 kl. 10.02"
    assert regj.nth(2).inner_text() == "1"


def test_status_feil_uten_data_utdatert_og_ikke_hentet(side):
    sf = _rad(side, "Statsforvalteren i Innlandet").locator("td")
    assert "Høringene herfra mangler i listen." in sf.nth(0).inner_text()
    assert sf.nth(1).inner_text() == "–" and sf.nth(2).inner_text() == "–"
    miljo = _rad(side, "Miljødirektoratet").locator("td")
    assert miljo.nth(0).inner_text().startswith("Utdatert")
    assert miljo.nth(1).inner_text() == "5. oktober 2026 kl. 10.01"
    nve = _rad(side, "NVE").locator("td")
    assert nve.nth(0).inner_text() == "Ikke hentet ennå"
    assert nve.nth(2).inner_text() == "–"


def test_ny_merke(side):
    assert side.locator(".hoering .ny-merke").count() == 1
    assert side.locator('.hoering[data-id="d14"] h2').inner_text() == "Fjorten dager Ny"
    assert side.locator('.hoering[data-id="d14"] h2 a').inner_text() == "Fjorten dager"


def test_ingen_advarsel_naar_ferske_data(side):
    assert side.is_hidden("#advarsel")


def test_advarsel_naar_data_er_gamle(nettleser, server, tmp_path):
    gamle = {**HORINGER, "generert": "2026-10-06T10:05:00+02:00"}
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=gamle)))
    assert side.is_visible("#advarsel")
    assert side.inner_text("#advarsel").startswith("Oversikten er ikke oppdatert på 11 dager.")
    side.close()


def test_ingen_advarsel_etter_ti_dager(nettleser, server, tmp_path):
    # Generert sent 7. oktober norsk tid (som er 7. oktober også i UTC-tid før midnatt).
    data = {**HORINGER, "generert": "2026-10-07T23:30:00+02:00"}
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=data)))
    assert side.is_hidden("#advarsel")
    side.close()


def test_arkiv_mangler(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, arkiv=None)))
    _vis_utlopte(side)
    assert "Høringer med utløpt frist kunne ikke hentes." in side.inner_text("#antall")
    assert len(_titler(side)) == 9
    side.close()


def test_arkiv_hentes_bare_ved_behov(nettleser, server, tmp_path):
    url = server(_lag_nettsted(tmp_path))
    side = nettleser.new_page()
    side.add_init_script(f"window.HORINGER_I_DAG = '{I_DAG}';")
    adresser = []
    side.on("request", lambda r: adresser.append(r.url))
    side.goto(url + "/index.html")
    side.wait_for_selector("html[data-klar]")
    assert not any(a.endswith("arkiv.json") for a in adresser)
    _vis_utlopte(side)
    assert any(a.endswith("arkiv.json") for a in adresser)
    side.close()


def test_feilforklaringer(side):
    f = "window.Horinger.feilforklaring"
    assert side.evaluate(f"{f}('ReadTimeout: timed out')") == "Nettstedet svarte ikke i tide."
    assert side.evaluate(f"{f}('SperretAvRobots: x er sperret i robots.txt')").startswith(
        "Nettstedet tillater ikke"
    )
    # Nettverksfeil ved henting av robots.txt (Vegvesenet 23.10.2026) er ikke en sperre.
    nettverk = (
        "RobotsUtilgjengelig: Kunne ikke hente https://www.vegvesen.no/robots.txt: "
        "HTTPSConnectionPool(host='www.vegvesen.no', port=443): Max retries exceeded "
        "(Caused by NewConnectionError('[Errno 101] Network is unreachable'))"
    )
    assert side.evaluate(f"{f}({nettverk!r})") == "Fikk ikke kontakt med nettstedet."
    assert side.evaluate(f"{f}('HTTPError: 500 Server Error')") == (
        "Nettstedet svarte med en feil (feilkode 500)."
    )


# ---------- Feil i datafilene ----------


def test_mangler_horinger(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=None)))
    assert side.is_visible("#feil")
    assert "Klarte ikke å hente høringene" in side.inner_text("#feil")
    assert side.is_disabled("#eksport")
    side.close()


def test_mangler_status(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, status=None)))
    assert len(_titler(side)) == 9
    assert side.inner_text("#status-ingress") == "Status for kildene er ikke tilgjengelig."
    assert side.is_hidden("#status-tabell")
    side.close()


# ---------- Mobil og tilgjengelighet ----------


def _axe_sti() -> Path:
    sti = Path(os.environ.get("AXE_STI", ROT / "node_modules" / "axe-core" / "axe.min.js"))
    if not sti.is_file():
        raise FileNotFoundError(
            f"axe-core mangler ({sti}). Installer med `npm install --no-save axe-core@4.10.2` "
            "eller sett AXE_STI."
        )
    return sti


@pytest.mark.parametrize("bredde", [375, 1280])
def test_tilgjengelighet_axe(nettleser, server, tmp_path, bredde):
    # Med «Hvorfor relevant» og «Utelatte høringer» (sprint 8 v2), så de også kontrolleres.
    side = _apne(
        nettleser, server(_lag_nettsted(tmp_path, horinger=_med_relevans())), bredde=bredde
    )
    if not side.locator("#filtre-boks").evaluate("d => d.open"):
        side.click("#filtre-boks summary")  # åpne filtrene på mobil, så de også kontrolleres
    _vis_utlopte(side)  # vis alle fristtyper
    side.click("#utelatte summary")
    side.add_script_tag(path=str(_axe_sti()))
    resultat = side.evaluate(
        "axe.run(document, {runOnly: {type: 'tag', "
        "values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']}})"
    )
    alvorlige = [
        (v["id"], v["impact"], [n["target"] for n in v["nodes"]][:3])
        for v in resultat["violations"]
        if v["impact"] in ("serious", "critical")
    ]
    assert alvorlige == []
    side.close()


def test_mobil_uten_vannrett_rulling(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path)), bredde=375)
    assert side.evaluate("document.documentElement.scrollWidth") <= 375
    assert not side.locator("#filtre-boks").evaluate("d => d.open")  # filtre lukket på mobil
    side.click("#filtre-boks summary")
    side.fill("#sok", "barnehage")
    assert _titler(side) == ["Høring om barnehageloven"]
    # «Sist hentet» flyttes inn i statuskolonnen på smal skjerm.
    assert side.locator("#status-tabell thead .kol-tid").is_hidden()
    vegvesen = _rad(side, "Statens vegvesen").locator("td").nth(0)
    assert "Sist hentet 17. oktober 2026 kl. 10.01" in vegvesen.inner_text()
    side.close()


def test_tastatur_kommer_til_sok_og_listen(side):
    side.keyboard.press("Tab")
    assert side.evaluate("document.activeElement.className") == "hopp"
    side.keyboard.press("Enter")
    assert side.evaluate("document.activeElement.id") == "liste"


def test_ingen_eksterne_foresporsler(nettleser, server, tmp_path):
    url = server(_lag_nettsted(tmp_path))
    side = nettleser.new_page()
    side.add_init_script(f"window.HORINGER_I_DAG = '{I_DAG}';")
    adresser = []
    side.on("request", lambda r: adresser.append(r.url))
    side.goto(url + "/index.html")
    side.wait_for_selector("html[data-klar]")
    eksterne = [a for a in adresser if not a.startswith(url)]
    assert eksterne == []
    assert {a.rsplit("/", 1)[-1] for a in adresser} >= {
        "index.html",
        "stil.css",
        "app.js",
        "logo.svg",
        "horinger.json",
        "status.json",
    }
    side.close()


def test_filtre_kan_ikke_foldes_sammen_pa_pc(side):
    side.click("#filtre-boks summary")
    assert side.locator("#filtre-boks").evaluate("d => d.open")


def test_lenker_som_ikke_er_nettadresser_blir_tekst(side):
    rad = side.locator('.hoering[data-id="farlig"] h2')
    assert rad.locator("a").count() == 0
    assert rad.inner_text() == "Lenke uten http"


def test_foreslatt_prioritet_vises(side):
    flagg = side.locator('.hoering[data-id="d13"] .prio')
    assert flagg.inner_text() == "Foreslått prioritet: høy"
    assert "prio-1" in flagg.get_attribute("class")
    side.check('input[name="prio"][value="3"]')
    lav = side.locator('.hoering[data-id="prio3"] .prio')
    assert lav.inner_text() == "Foreslått prioritet: lav"
    assert side.locator("#liste .hoering").count() == side.locator("#liste .prio").count()


# ---------- Sortering og utskrift ----------


def test_sortering(side):
    side.select_option("#sortering", "avsender")
    instanser = side.locator("#liste .instans").all_inner_texts()
    assert instanser == sorted(instanser, key=str.lower)
    assert side.url.endswith("?sort=avsender")
    side.select_option("#sortering", "nye")
    assert _titler(side)[0] == "Fjorten dager"  # nyeste forst_sett i testdataene
    side.select_option("#sortering", "tema")
    tema = side.locator("#liste .tema").all_inner_texts()
    assert tema == sorted(tema)
    side.select_option("#sortering", "frist")
    assert _titler(side)[0] == "Frist i dag"
    assert "sort=" not in side.url


def test_sortering_prioritet(side):
    side.check('input[name="prio"][value="3"]')
    side.select_option("#sortering", "prioritet")
    assert _titler(side)[-1] == "Lav prioritet"


def test_sortering_leses_fra_adressen(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path)), sti="/index.html?sort=avsender")
    assert side.input_value("#sortering") == "avsender"
    side.close()


def test_nullstill_setter_sortering_tilbake(side):
    side.select_option("#sortering", "tema")
    side.click("#nullstill")
    assert side.input_value("#sortering") == "frist"


def test_utskrift(side):
    side.fill("#sok", "dager")
    side.select_option("#sortering", "avsender")
    side.emulate_media(media="print")
    assert side.is_hidden(".filtre")
    assert side.is_hidden(".status")
    assert side.is_hidden("#skriv-ut")
    info = side.inner_text("#utskrift-info")
    assert info.startswith("Utvalg: 2 høringer, søk «dager»")
    assert "Sortert etter høringsinstans A–Å. Skrevet ut 17. oktober 2026." in info
    # Samme høringer på papiret som på skjermen, og fargene skrives ut.
    assert _titler(side) == ["Fjorten dager", "Tretti dager"]
    farge = side.locator('.hoering[data-id="d14"] .frist').evaluate(
        "e => getComputedStyle(e).printColorAdjust"
    )
    assert farge == "exact"


def test_utskrift_er_kompakt(nettleser, server, tmp_path):
    """60 høringer skal få plass på høyst fem A4-sider (minst 12 per side). Sprint 10 ga mer
    luft og større skrift (Svein 28.10.2026), derfor fem og ikke tre."""
    mange = {
        **HORINGER,
        "horinger": [
            _h(f"m{i}", f"2026-11-{1 + i % 28:02d}", ingress="Kort beskrivelse av høringen.")
            for i in range(60)
        ],
    }
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=mange)))
    pdf = side.pdf(format="A4", print_background=True, prefer_css_page_size=True)
    sider = pdf.count(b"/Type /Page") - pdf.count(b"/Type /Pages")
    assert 1 <= sider <= 5, sider
    side.close()


# ---------- Sprint 4: grunn for prioritet og «Også på» ----------


def test_grunn_for_prioritet(side):
    flagg = side.locator('.hoering[data-id="d30"] .prio')
    assert flagg.inner_text() == "Foreslått prioritet: høy (gjelder regionen)"


def test_ogsa_publisert(side):
    ogsa = side.locator('.hoering[data-id="d30"] .ogsa')
    assert ogsa.inner_text() == "Også på Regjeringen.no"
    assert ogsa.locator("a").count() == 1  # lenken som ikke er en nettadresse, er tatt bort
    assert ogsa.locator("a").get_attribute("href") == "https://www.regjeringen.no/x"
    assert side.locator(".ogsa").count() == 1


# ---------- Sprint 5: månedsfrist og filtre ----------


def test_maanedsfrist_vises_som_maaned(side):
    frist = side.locator('.hoering[data-id="maned"] .frist')
    assert frist.locator(".dag").inner_text() == "des."
    assert frist.locator(".maned").inner_text() == "2026"
    assert frist.locator(".igjen").inner_text() == "Frist i desember"
    assert "Høringsfrist: desember 2026" in side.inner_text('.hoering[data-id="maned"]')
    titler = _titler(side)
    # Sorteres som 1. desember: etter 17. november, før høringen uten frist.
    assert titler.index("Frist bare med måned") == titler.index("Høring om barnehageloven") + 1
    assert titler[-1] == "Uten frist"


def test_maanedsfrist_er_aapen_ut_maaneden(nettleser, server, tmp_path):
    url = server(_lag_nettsted(tmp_path))
    side = nettleser.new_page()
    side.add_init_script("window.HORINGER_I_DAG = '2026-12-20';")
    side.goto(url + "/index.html")
    side.wait_for_selector("html[data-klar]")
    rad = side.locator('.hoering[data-id="maned"]')
    assert rad.count() == 1
    assert rad.locator(".igjen").inner_text() == "Frist denne måneden"
    side.close()


def test_temafilter_har_alle_temaer(side):
    valg = side.locator('#kategori input[name="kategori"]').evaluate_all(
        "els => els.map(e => e.value)"
    )
    temaer = sorted({h["kategori"] for h in HORINGER["horinger"]})
    assert sorted(valg) == temaer
    for tema in temaer:
        _kryss(side, "kategori", tema)
        assert all(t == tema for t in side.locator("#liste .tema").all_inner_texts())
        side.uncheck(f'#kategori input[value="{tema}"]')


def test_prioritetsfilter_skiller(side):
    side.uncheck('input[name="prio"][value="1"]')
    side.uncheck('input[name="prio"][value="2"]')
    side.check('input[name="prio"][value="3"]')
    assert _titler(side) == ["Lav prioritet"]


# ---------- Sprint 6: høringsparter og regionflagg ----------


def test_regionflagg_vises_ved_tittelen(side):
    rad = side.locator('.hoering[data-id="d31"]')
    assert rad.locator(".regionflagg").inner_text() == "Regionen er høringspart: Alle kommuner, KS"
    assert "Foreslått prioritet: høy (regionen er høringspart)" in rad.locator(".prio").inner_text()
    assert side.locator('.hoering[data-id="d13"] .regionflagg').count() == 0


def test_kategorier_og_utfoldbar_liste(side):
    rad = side.locator('.hoering[data-id="d31"]')
    assert rad.locator(".parter-kort").inner_text() == (
        "Høringsparter: Alle kommuner, Kommuner og fylkeskommuner (1), "
        "Departementer og direktorater (1), Organisasjoner (1)"
    )
    oppsummering = rad.locator(".parter summary")
    assert oppsummering.inner_text() == "Vis alle høringsparter (4)"
    assert not rad.locator(".parter-liste").is_visible()
    # Kan foldes ut med tastaturet.
    oppsummering.focus()
    side.keyboard.press("Enter")
    assert rad.locator(".parter-liste").is_visible()
    assert rad.locator(".parter-liste li").all_inner_texts() == [
        "Alle kommuner",
        "KS",
        "Utdanningsdirektoratet",
        "Utdanningsforbundet",
    ]
    assert "Saksfelt: Barnehager" in rad.locator(".detaljer").inner_text()


def test_merknad_og_lenke_uten_liste(side):
    rad = side.locator('.hoering[data-id="d30"]')
    assert rad.locator(".parter-kort").inner_text() == (
        "Høringsparter: Ikke tilgjengelig – se høringslisten"
    )
    assert rad.locator(".parter-kort a").get_attribute("href") == "https://example.no/liste.pdf"
    assert rad.locator(".parter").count() == 0
    apen = side.locator('.hoering[data-id="d14"] .parter-kort').inner_text()
    assert apen == "Høringsparter: Åpen for alle"


def test_filter_bare_regionen_som_hoeringspart(side):
    side.check("#regionpart")
    assert _titler(side) == ["Høring om barnehageloven"]
    assert "regionpart=1" in side.url
    assert "bare der regionen er høringspart" in side.inner_text("#utskrift-info")
    side.click("#nullstill")
    assert not side.is_checked("#regionpart")


def test_filter_regionpart_leses_fra_adressen(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path)), sti="/index.html?regionpart=1")
    assert side.is_checked("#regionpart")
    assert _titler(side) == ["Høring om barnehageloven"]
    side.close()


def test_sok_i_hoeringsparter(side):
    side.fill("#sok", "utdanningsforbundet")
    assert _titler(side) == ["Høring om barnehageloven"]


def test_csv_har_flagg_og_kategorier(side):
    side.fill("#sok", "barnehageloven")
    with side.expect_download() as nedlasting:
        side.click("#eksport")
    linjer = Path(nedlasting.value.path()).read_bytes().decode("utf-8-sig").split("\r\n")
    assert linjer[0].endswith(
        ";Regionen er høringspart;Høringsparter;Saksfelt;Mottatt av Gjøvik kommune;KI-sammendrag;"
        "Hvorfor relevant (KI);Ingress;Lenke"
    )
    assert linjer[1].endswith(
        ";Alle kommuner, KS;Alle kommuner, Kommuner og fylkeskommuner (1), "
        "Departementer og direktorater (1), Organisasjoner (1);Barnehager;;;;;https://example.no/d31"
    )


def test_utskrift_viser_flagg_og_kategorier_men_ikke_listen(side):
    side.emulate_media(media="print")
    rad = side.locator('.hoering[data-id="d31"]')
    assert rad.locator(".regionflagg").is_visible()
    assert rad.locator(".parter-kort").is_visible()
    assert not rad.locator(".parter").is_visible()


def test_utskrift_med_hoeringsparter(nettleser, server, tmp_path):
    """Med flagg og kategorier får hver høring én linje til: 60 høringer på høyst åtte sider
    (sprint 10: mer luft og større skrift). Lokalt blir det 6 sider og på GitHub 7, fordi
    skriftene på maskinene er ulike."""
    mange = {
        **HORINGER,
        "horinger": [
            _h(
                f"m{i}",
                f"2026-11-{1 + i % 28:02d}",
                ingress="Kort beskrivelse av høringen.",
                horingsparter=[f"Part {n}" for n in range(40)],
                partkategorier={"Alle kommuner": 1, "Organisasjoner": 20, "Andre": 19},
                regionflagg=["Alle kommuner"],
            )
            for i in range(60)
        ],
    }
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=mange)))
    pdf = side.pdf(format="A4", print_background=True, prefer_css_page_size=True)
    sider = pdf.count(b"/Type /Page") - pdf.count(b"/Type /Pages")
    assert 1 <= sider <= 8, sider
    side.close()


# ---------- Sprint 7: Gjøviks postliste ----------

PL = "https://www.gjovik.kommune.no/sok-i-postliste/#/details/"


def _med_postliste():
    hs = []
    for h in HORINGER["horinger"]:
        h = dict(h)
        if h["id"] == "d31":
            h["postliste"] = [
                {
                    "kommune": "Gjøvik",
                    "dato": "2026-10-12",
                    "tittel": "Høring om barnehageloven",
                    "lenke": PL + "a/1",
                    "niva": "sikker",
                }
            ]
        if h["id"] == "d13":
            h["postliste"] = [
                {
                    "kommune": "Gjøvik",
                    "dato": "2026-10-14",
                    "tittel": "Høring om æ",
                    "lenke": PL + "a/2",
                    "niva": "mulig",
                }
            ]
        hs.append(h)
    status = {
        **STATUS,
        "kilder": [
            *STATUS["kilder"],
            {
                "kilde": "Gjøviks postliste",
                "type": "postliste",
                "status": "ok",
                "hentet": OK,
                "sist_ok": OK,
                "antall": 7,
            },
        ],
    }
    postliste = {
        "generert": OK,
        "journalposter": [
            {
                "id": "s",
                "kommune": "Gjøvik",
                "dato": "2026-10-14",
                "avsender": "Samediggi Sametinget",
                "tittel": "Høring - Behov for samisk tilbud",
                "lenke": PL + "b/3",
                "niva": "",
            },
            {
                "id": "p",
                "kommune": "Gjøvik",
                "dato": "2026-10-10",
                "avsender": "",
                "tittel": "Høring om noe",
                "lenke": PL + "b/4",
                "niva": "",
            },
            {
                "id": "k",
                "kommune": "Gjøvik",
                "dato": "2026-10-12",
                "avsender": "KD",
                "tittel": "Høring om barnehageloven",
                "lenke": PL + "a/1",
                "niva": "sikker",
            },
        ],
    }
    return {**HORINGER, "horinger": hs}, status, postliste


@pytest.fixture
def side_pl(nettleser, server, tmp_path):
    hs, status, postliste = _med_postliste()
    s = _apne(nettleser, server(_lag_nettsted(tmp_path, hs, status, postliste=postliste)))
    yield s
    assert s.feil == [], s.feil
    s.close()


def test_merke_mottatt_og_mulig(side_pl):
    sikker = side_pl.locator('.hoering[data-id="d31"] .mottatt')
    assert sikker.inner_text() == "Mottatt av Gjøvik kommune 12. oktober 2026"
    assert sikker.locator("a").get_attribute("href") == PL + "a/1"
    mulig = side_pl.locator('.hoering[data-id="d13"] .mottatt')
    assert mulig.inner_text() == "Mulig treff i Gjøvik kommunes postliste 14. oktober 2026"
    assert "mottatt-mulig" in mulig.get_attribute("class")
    assert side_pl.locator('.hoering[data-id="d14"] .mottatt').count() == 0


def test_filter_bare_mottatt(side_pl):
    side_pl.check("#mottatt")
    assert _titler(side_pl) == ["Høring om barnehageloven"]  # bare sikre treff
    assert "mottatt=1" in side_pl.url
    assert "bare mottatt av Gjøvik kommune" in side_pl.inner_text("#utskrift-info")
    side_pl.click("#nullstill")
    assert not side_pl.is_checked("#mottatt")


def test_seksjon_uten_treff(side_pl):
    assert side_pl.is_visible("#postliste")
    rader = side_pl.locator("#postliste-liste li")
    assert rader.count() == 2  # det koblede brevet vises ikke her
    assert rader.nth(0).inner_text().split("\n") == [
        "14. oktober 2026",
        "Samediggi Sametinget",
        "Høring - Behov for samisk tilbud",
    ]
    assert "Avsender ikke vist" in rader.nth(1).inner_text()


def test_status_for_postlista(side_pl):
    rad = _rad(side_pl, "Gjøviks postliste")
    assert rad.locator("td.tall").inner_text() == "7 brev"
    ingress = side_pl.inner_text("#status-ingress")
    assert ingress.startswith("7 kilder overvåkes automatisk.")  # postlista telles ikke
    assert "Gjøviks postliste ble sist sjekket 17. oktober 2026 kl. 10.01." in ingress


def test_csv_har_mottatt(side_pl):
    side_pl.fill("#sok", "barnehageloven")
    with side_pl.expect_download() as nedlasting:
        side_pl.click("#eksport")
    linjer = Path(nedlasting.value.path()).read_bytes().decode("utf-8-sig").split("\r\n")
    assert linjer[1].endswith(";12. oktober 2026;;;;https://example.no/d31")


def test_seksjonen_skjules_uten_data(side):
    assert side.is_hidden("#postliste")


# ---------- Sprint 8: delt visning (Svein 27.10.2026) ----------


def _mange(n=60):
    return {
        **HORINGER,
        "horinger": [
            _h(f"m{i}", f"2026-11-{1 + i % 28:02d}", ingress="Kort beskrivelse av høringen.")
            for i in range(n)
        ],
    }


def _rull(side, x, y, dy):
    side.mouse.move(x, y)
    side.mouse.wheel(0, dy)
    side.wait_for_timeout(250)


def _topp(side, sel):
    return side.evaluate(f"document.querySelector('{sel}').scrollTop")


def test_filtre_og_liste_ruller_hver_for_seg(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_mange())), bredde=1280)
    side.set_viewport_size({"width": 1280, "height": 600})
    # Listen rulles: filtrene står i ro, og selve siden ruller ikke (toppen står fast).
    _rull(side, 900, 450, 1200)
    assert _topp(side, "#hoved") > 0
    assert _topp(side, ".filtre") == 0
    assert side.evaluate("scrollY") == 0
    liste_for = _topp(side, "#hoved")
    # Filtrene rulles: listen står i ro. Musen nederst i venstre kolonne, under verktøylinjen
    # (sprint 11).
    _rull(side, 150, 570, 600)
    assert _topp(side, ".filtre") > 0
    assert _topp(side, "#hoved") == liste_for
    assert side.is_visible("h1")
    side.close()


def test_hopp_til_listen_flytter_ikke_toppen(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_mange())), bredde=1280)
    side.keyboard.press("Tab")
    side.keyboard.press("Enter")
    assert side.evaluate("document.activeElement.id") == "liste"
    assert side.evaluate("scrollY") == 0
    side.close()


def test_mobil_ruller_som_en_side(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_mange())), bredde=390)
    assert (
        side.evaluate("getComputedStyle(document.querySelector('#hoved')).overflowY") == "visible"
    )
    _rull(side, 200, 400, 1500)
    assert side.evaluate("scrollY") > 0
    side.close()


# ---------- Sprint 8: KI-sammendrag ----------


def test_ki_sammendrag_med_merke_og_ingress(nettleser, server, tmp_path):
    hs = {**HORINGER, "horinger": [dict(h) for h in HORINGER["horinger"]]}
    d30 = next(h for h in hs["horinger"] if h["id"] == "d30")
    d30["sammendrag"] = "Forslag om ny fartsgrense på rv. 4 ved Gjøvik."
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=hs)))
    rad = side.locator('.hoering[data-id="d30"]')
    assert rad.locator(".sammendrag").inner_text() == (
        "KI-sammendrag Forslag om ny fartsgrense på rv. 4 ved Gjøvik."
    )
    assert not rad.locator(".ingress-kilde .beskrivelse").is_visible()
    rad.locator(".ingress-kilde summary").click()
    assert rad.locator(".ingress-kilde .beskrivelse").inner_text() == "Gjelder rv. 4 ved Gjøvik."
    # Uten sammendrag vises ingressen som før.
    assert side.locator('.hoering[data-id="d13"] .ki-merke').count() == 0
    side.fill("#sok", "fartsgrense")
    assert _titler(side) == ["Tretti dager"]
    with side.expect_download() as nedlasting:
        side.click("#eksport")
    linje = Path(nedlasting.value.path()).read_bytes().decode("utf-8-sig").split("\r\n")[1]
    assert ";Forslag om ny fartsgrense på rv. 4 ved Gjøvik.;;Gjelder rv. 4 ved Gjøvik.;" in linje
    assert side.feil == []
    side.close()


# ---------- Sprint 8 v2: relevans for regionen og utelatte høringer ----------


def _med_relevans():
    hs = {**HORINGER, "horinger": [dict(h) for h in HORINGER["horinger"]]}
    for h in hs["horinger"]:
        h["relevant"] = True
        h["hvorfor_relevant"] = ""
    d30 = next(h for h in hs["horinger"] if h["id"] == "d30")
    d30["hvorfor_relevant"] = "Fartsgrensen gjelder rv. 4 gjennom Gjøvik."
    d13 = next(h for h in hs["horinger"] if h["id"] == "d13")
    d13.update(
        relevant=False,
        tittel="Ny ruteplan for kystruten Bergen–Kirkenes",
        hvorfor_relevant="Gjelder bare kysten fra Bergen til Kirkenes.",
    )
    return hs


def test_hvorfor_relevant_vises_under_sammendraget(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_med_relevans())))
    rad = side.locator('.hoering[data-id="d30"]')
    assert rad.locator(".relevans").inner_text() == (
        "KI: Hvorfor relevant Fartsgrensen gjelder rv. 4 gjennom Gjøvik."
    )
    assert side.locator('.hoering[data-id="d31"] .relevans').count() == 0
    side.fill("#sok", "gjennom gjøvik")
    assert _titler(side) == ["Tretti dager"]
    assert side.feil == []
    side.close()


def test_utelatte_hoeringer_er_samlet_nederst(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_med_relevans())))
    assert "Ny ruteplan for kystruten Bergen–Kirkenes" not in _titler(side)
    assert side.inner_text("#antall") == "Viser 8 høringer (9 åpne totalt, 1 ny siste uke)"
    boks = side.locator("#utelatte")
    assert boks.is_visible() and boks.get_attribute("open") is None
    assert side.inner_text("#antall-utelatte") == "1"
    assert not side.locator("#utelatte-liste li").first.is_visible()
    boks.locator("summary").click()
    rad = side.locator("#utelatte-liste li")
    assert rad.locator("a").inner_text() == "Ny ruteplan for kystruten Bergen–Kirkenes"
    assert rad.locator("a").get_attribute("href") == "https://example.no/d13"
    assert rad.locator(".utelatt-grunn").inner_text() == (
        "Utelatt: Gjelder bare kysten fra Bergen til Kirkenes."
    )
    # Filtrene gjelder også de utelatte. Ingen treff skjuler seksjonen.
    side.fill("#sok", "barnehageloven")
    assert side.locator("#utelatte").is_hidden()
    # CSV tar bare med hovedlisten.
    side.fill("#sok", "")
    with side.expect_download() as nedlasting:
        side.click("#eksport")
    tekst = Path(nedlasting.value.path()).read_bytes().decode("utf-8-sig")
    assert "kystruten" not in tekst and "Fartsgrensen gjelder rv. 4 gjennom Gjøvik." in tekst
    assert side.feil == []
    side.close()


def test_uten_utelatte_vises_ikke_seksjonen(side):
    assert side.locator("#utelatte").is_hidden()


def test_utelatte_vises_ikke_paa_utskrift(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_med_relevans())))
    side.emulate_media(media="print")
    assert side.locator("#utelatte").is_hidden()
    side.close()


# ---------- Sprint 10: brukervennlighet ----------


def _med_veger():
    hs = {**HORINGER, "horinger": [dict(h) for h in HORINGER["horinger"]]}
    hs["horinger"] += [
        _h("v1", "2026-11-20", tittel="Utbedring av Rv. 4 ved Gjøvik"),
        _h("v2", "2026-11-21", tittel="Reguleringsplan rv. 40 Hunndalen"),
        _h("v3", "2026-11-22", tittel="Fv. 33 Skreia–Bilitt"),
    ]
    return hs


@pytest.mark.parametrize("sok", ["rv4", "Rv.4", "rv. 4", "rv 4", "RV-4", "rv.  4"])
def test_sok_tåler_skrivemaater_for_vegnummer(nettleser, server, tmp_path, sok):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_med_veger())))
    side.fill("#sok", sok)
    # «rv4» skal ikke finne «rv. 40». «Tretti dager» har «rv. 4» i ingressen.
    assert _titler(side) == ["Tretti dager", "Utbedring av Rv. 4 ved Gjøvik"]
    side.close()


@pytest.mark.parametrize(
    "sok", ["barnehage", "Barnehave", "barnehahgre", "barnhage", "barnehagelovn"]
)
def test_sok_taaler_smaa_skrivefeil(side, sok):
    side.fill("#sok", sok)
    assert _titler(side) == ["Høring om barnehageloven"]


@pytest.mark.parametrize("sok", ["sitat", "fv33", "fv. 33"])
def test_sok_uten_falske_treff(nettleser, server, tmp_path, sok):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_med_veger())))
    side.fill("#sok", sok)
    forventet = {
        "sitat": ['Høring om æ, ø og å; «sitat» og "anførsel"'],
        "fv33": ["Fv. 33 Skreia–Bilitt"],
        "fv. 33": ["Fv. 33 Skreia–Bilitt"],
    }[sok]
    assert _titler(side) == forventet
    side.close()


def test_korte_ord_maa_stemme(side):
    # «hør» finnes som starten av «høring», men «hxr» (3 tegn) skal ikke gi treff med feil.
    side.fill("#sok", "hxr")
    assert _titler(side) == []


def test_lenker_aapnes_i_ny_fane(nettleser, server, tmp_path):
    hs = _med_relevans()
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=hs, postliste=None)))
    lenker = side.locator("#liste a[href^='http'], #utelatte-liste a")
    assert lenker.count() > 5
    for i in range(lenker.count()):
        a = lenker.nth(i)
        assert a.get_attribute("target") == "_blank"
        assert a.get_attribute("rel") == "noopener"
        assert a.get_attribute("aria-describedby") == "ny-fane"
    assert side.locator("#ny-fane").text_content() == "Åpnes i ny fane"
    side.close()


def test_verktoylinjen_staar_fast_over_filtrene(nettleser, server, tmp_path):
    """Sprint 11 (Svein 28.10.2026): verktøylinjen står fast i venstre kolonne, over filtrene."""
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_mange())), bredde=1280)
    side.set_viewport_size({"width": 1280, "height": 700})
    for sel in ("#antall", "#sortering", "#skriv-ut", "#eksport", ".forklaring"):
        assert side.locator(f".venstre .verktoy-boks {sel}").count() == 1, sel
        assert side.locator(f"header.topp {sel}").count() == 0, sel
    boks = side.locator(".verktoy-boks").bounding_box()
    filtre = side.locator("#filtre-tittel").bounding_box()
    assert boks["y"] + boks["height"] <= filtre["y"]
    assert boks["x"] + boks["width"] <= side.locator("#hoved").bounding_box()["x"]
    # Står i ro når filtrene og listen rulles.
    for_ = side.locator("#eksport").bounding_box()["y"]
    _rull(side, 150, 600, 600)
    assert _topp(side, ".filtre") > 0
    _rull(side, 900, 450, 900)
    assert _topp(side, "#hoved") > 0
    assert side.locator("#eksport").bounding_box()["y"] == for_
    assert side.evaluate("scrollY") == 0
    side.close()


def test_verktoylinjen_over_filtrene_paa_mobil(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path)), bredde=375)
    assert (
        side.locator(".verktoy-boks").bounding_box()["y"]
        < side.locator("#filtre-boks").bounding_box()["y"]
    )
    assert side.evaluate("document.documentElement.scrollWidth") <= 375
    side.close()


def test_filtrene_uten_fet_og_prioritet_uten_tall(side):
    vekt = side.locator("label.valg").first.evaluate("e => getComputedStyle(e).fontWeight")
    assert vekt == "400"
    assert side.locator("legend", has_text="Øvrige valg").count() == 1
    prio = [t.strip() for t in side.locator('input[name="prio"] >> xpath=..').all_inner_texts()]
    assert prio == ["Høy", "Middels", "Lav"]
    tekst = side.inner_text("fieldset:has(legend:text('Øvrige valg'))")
    assert "regionen er høringspart" in tekst and "utløpt frist" in tekst


def test_utskrift_har_hvorfor_relevant(nettleser, server, tmp_path):
    side = _apne(nettleser, server(_lag_nettsted(tmp_path, horinger=_med_relevans())))
    side.emulate_media(media="print")
    assert side.locator('.hoering[data-id="d30"] .relevans').is_visible()
    assert not side.locator("#eksport").is_visible()
    assert side.locator("#antall").is_visible()
    side.close()


def test_avkrysningsboksene_krymper_ikke_ved_lange_valg(side):
    bredder = side.locator("#kategori input").evaluate_all(
        "l => l.map(e => Math.round(e.getBoundingClientRect().width))"
    )
    assert len(set(bredder)) == 1, bredder
