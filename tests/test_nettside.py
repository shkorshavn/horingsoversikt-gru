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
    "antall": 9,
    "horinger": [
        _h(
            "d31",
            "2026-11-17",
            tittel="Høring om barnehageloven",
            kategori="Oppvekst",
            niva="Regjeringen",
            instans="Kunnskapsdepartementet",
            kilde="Regjeringen.no",
        ),
        _h("d13", "2026-10-30", tittel='Høring om æ, ø og å; «sitat» og "anførsel"'),
        _h("d14", "2026-10-31", tittel="Fjorten dager"),
        _h("d30", "2026-11-16", tittel="Tretti dager", ingress="Gjelder rv. 4 ved Gjøvik."),
        _h(
            "d0",
            "2026-10-17",
            tittel="Frist i dag",
            instans="Stortinget, Justiskomiteen",
            kilde="Stortinget",
            niva="Stortinget",
            kategori="Regjeringen og Stortinget",
        ),
        _h("utlopt", "2026-10-16", tittel="Utløpt i går"),
        _h("prio3", "2026-10-25", tittel="Lav prioritet", prioritet=3),
        _h("ukjent", None, tittel="Uten frist"),
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

STATUS = {
    "generert": "2026-10-17T10:05:00+02:00",
    "antall_kall": 20,
    "kilder": [
        {"kilde": "Stortinget", "status": "ok", "antall": 64},
        {
            "kilde": "Regjeringen.no",
            "status": "feil",
            "antall": 0,
            "feil": "HTTPError: 403 Client Error: Forbidden for url: https://x",
        },
        {"kilde": "Statens vegvesen", "status": "ok", "antall": 448},
        {"kilde": "Innlandet fylkeskommune", "status": "ok", "antall": 1},
        {"kilde": "NVE", "status": "ikke overvåket", "antall": 0},
        {"kilde": "DSB", "status": "ikke overvåket", "antall": 0},
    ],
}


def _lag_nettsted(mappe: Path, horinger=HORINGER, status=STATUS) -> Path:
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
    return side.locator("#liste .hoering h2").all_inner_texts()


# ---------- Sortering og standardvisning ----------


def test_sortert_pa_frist_uten_utlopte_og_prio3(side):
    assert _titler(side) == [
        "Frist i dag",
        'Høring om æ, ø og å; «sitat» og "anførsel"',
        "Fjorten dager",
        "Regional plan",
        "Tretti dager",
        "Høring om barnehageloven",
        "Uten frist",
    ]
    assert side.inner_text("#antall") == "Viser 7 høringer (8 åpne totalt)"


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


def test_utlopte_kan_vises(side):
    side.check("#utlopte")
    assert "Utløpt i går" in _titler(side)
    frist = side.locator('.hoering[data-id="utlopt"] .frist')
    assert "utlopt" in frist.get_attribute("class")
    assert frist.locator(".igjen").inner_text() == "Fristen er ute"


def test_prioritet_3(side):
    side.check('input[name="prio"][value="3"]')
    assert "Lav prioritet" in _titler(side)
    side.uncheck('input[name="prio"][value="1"]')
    assert _titler(side) == ["Lav prioritet"]


def test_kategori(side):
    side.select_option("#kategori", "Oppvekst")
    assert _titler(side) == ["Høring om barnehageloven"]


def test_niva(side):
    side.select_option("#niva", "Fylkeskommunen")
    assert _titler(side) == ["Regional plan"]


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
    assert len(_titler(side)) == 7
    assert side.is_hidden("#tom")


def test_filtre_skrives_til_adressen(side):
    side.fill("#sok", "plan")
    side.select_option("#niva", "Fylkeskommunen")
    side.check('input[name="prio"][value="3"]')
    assert side.url.endswith("?q=plan&niva=Fylkeskommunen&prio=1%2C2%2C3")


def test_filtre_leses_fra_adressen(nettleser, server, tmp_path):
    url = server(_lag_nettsted(tmp_path))
    side = _apne(nettleser, url, sti="/index.html?q=lav&prio=3&utlopte=1")
    assert _titler(side) == ["Lav prioritet"]
    assert side.is_checked("#utlopte")
    assert not side.is_checked('input[name="prio"][value="1"]')
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
        "Høringsfrist: 2026-10-30;https://example.no/d13"
    )
    assert linjer[2] == ""


# ---------- Status ----------


def test_statusoversikt(side):
    rader = side.locator("#status-tabell tbody tr")
    assert rader.count() == 4
    regj = rader.nth(1)
    assert regj.locator("th").inner_text() == "Regjeringen.no"
    assert "Nettstedet avviste innhentingen (feilkode 403)." in regj.inner_text()
    assert regj.locator("td").nth(1).inner_text() == "–"
    vegvesen = rader.nth(2)
    # Åpne høringer fra kilden (5 i testdataene), ikke antall hentet (448)
    assert vegvesen.locator("td").nth(1).inner_text() == "5"
    assert side.inner_text("#antall-inaktive") == "2"
    assert "1 kilde kunne ikke hentes" in side.inner_text("#status-ingress")
    assert "17. oktober 2026 kl. 10.05" in side.inner_text("#oppdatert")


def test_feilforklaringer(side):
    f = "window.Horinger.feilforklaring"
    assert side.evaluate(f"{f}('ReadTimeout: timed out')") == "Nettstedet svarte ikke i tide."
    assert side.evaluate(f"{f}('SperretAvRobots: x er sperret i robots.txt')").startswith(
        "Nettstedet tillater ikke"
    )
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
    assert len(_titler(side)) == 7
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
    side = _apne(nettleser, server(_lag_nettsted(tmp_path)), bredde=bredde)
    if not side.locator("#filtre-boks").evaluate("d => d.open"):
        side.click("#filtre-boks summary")  # åpne filtrene på mobil, så de også kontrolleres
    side.check("#utlopte")  # vis alle fristtyper
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
