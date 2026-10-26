"""Tester av høringsparter, kategorier og regionflagg (sprint 6).

Sidene og PDF-ene i tests/fixtures/horingsparter/ er hentet fra kildene 26.10.2026.
"""

from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from horinger.bygg import bygg
from horinger.dedup import dedupliser
from horinger.horingsparter import (
    APEN_FOR_ALLE,
    IKKE_OPPGITT,
    IKKE_TILGJENGELIG,
    Partvurdering,
    fra_html,
    fra_pdf,
    rens_liste,
)
from horinger.kilder.base import Kilde
from horinger.lager import lagre_kilde
from horinger.modell import Hoering
from horinger.nett import SperretAvRobots
from horinger.prioritet import Prioritet

ROT = Path(__file__).parent.parent
FIX = Path(__file__).parent / "fixtures" / "horingsparter"
KONFIG = yaml.safe_load((ROT / "sources.yaml").read_text("utf-8"))
VURDERING = Partvurdering(KONFIG["felles"]["horingsparter"])


def _html(navn: str) -> str:
    return (FIX / navn).read_text("utf-8")


def _pdf(navn: str) -> list[str]:
    return fra_pdf((FIX / navn).read_bytes())


# ---------- Regionflagg: hver part vurderes for seg ----------


@pytest.mark.parametrize(
    "part, flagg",
    [
        ("Gjøvik kommune", ["Gjøvik kommune"]),
        ("Østre Toten kommune", ["Østre Toten kommune"]),
        ("Vestre Toten kommune", ["Vestre Toten kommune"]),
        ("Søndre Land kommune", ["Søndre Land kommune"]),
        ("Nordre Land kommune", ["Nordre Land kommune"]),
        ("Ringsaker kommune", ["Ringsaker kommune"]),
        ("Lillehammer kommune", ["Lillehammer kommune"]),
        ("Alle kommuner", ["Alle kommuner"]),
        ("Alle landets kommuner", ["Alle kommuner"]),
        ("Kommunene", ["Alle kommuner"]),
        ("Alle kommuner i Innlandet", ["Alle kommuner"]),
        ("Alle fylkeskommuner", ["Alle fylkeskommuner"]),
        ("Fylkeskommunene", ["Alle fylkeskommuner"]),
        ("KS", ["KS"]),
        ("KS – Kommunesektorens organisasjon", ["KS"]),
        ("Kommunesektorens organisasjon (KS)", ["KS"]),
        ("Innlandet fylkeskommune", ["Innlandet fylkeskommune"]),
        ("Gjøvikregionen IPR", ["Gjøvikregionen"]),
        ("Interkommunale politiske råd", ["Regionrådene"]),
        ("Alle regionråd", ["Regionrådene"]),
    ],
)
def test_regionflagg_treff(part, flagg):
    assert VURDERING.regionflagg([part]) == flagg


@pytest.mark.parametrize(
    "part",
    [
        "Gjøvik tingrett",
        "Sykehuset Innlandet, Gjøvik",
        "Gjøvik",  # navnet alene kan være poststedet i en adresse
        "Statsforvalteren i Innlandet",  # ikke med (Svein 26.10.2026)
        "Hamar kommune",  # nabokommune som ikke er med
        "Oslo kommune",
        "Universitetet i Innlandet",
        "Kommunene i Troms",
        "KS Bedrift",
        "KS2-sertifiserte",
        "Norsk kommunerevisorforening",
        "Kommunal- og distriktsdepartementet",
        "Fylkesmannen i Oppland",
        "Statens vegvesen",
    ],
)
def test_regionflagg_ingen_falske_treff(part):
    assert VURDERING.regionflagg([part]) == []


def test_flere_grunner_og_rekkefolge():
    parter = ["Direktoratet for byggkvalitet", "KS", "Alle kommuner", "Gjøvik kommune"]
    assert VURDERING.regionflagg(parter) == ["Alle kommuner", "KS", "Gjøvik kommune"]


def test_kategorier():
    parter = [
        "Alle landets kommuner",
        "Alle fylkeskommuner",
        "Oslo kommune",
        "KS",
        "Statsforvalteren i Innlandet",
        "Kommunal- og distriktsdepartementet",
        "Helsedirektoratet",
        "Norges Bondelag",
        "Den norske legeforening",
        "Felleskjøpet Agri SA",
    ]
    assert VURDERING.kategoriser(parter) == {
        "Alle kommuner": 1,
        "Alle fylkeskommuner": 1,
        "Statsforvaltere": 1,
        "Kommuner og fylkeskommuner": 2,
        "Departementer og direktorater": 2,
        "Organisasjoner": 2,
        "Andre": 1,
    }


# ---------- Rensing av lister ----------


def test_rens_liste_slaar_sammen_brutte_linjer_og_fjerner_adresser():
    linjer = [
        "Høringsinstanser",
        "Møre og Romsdal",
        "fylkeskommune",
        "Fylkesmannen i Nord-",
        "Trøndelag",
        "Strand Unikorn AS Postboks 103 2391 Moelv",
        "Fiskå Mølle AS Fiskåvegen 1010 4121 Tau",
        "Side 1 av 2",
        "KS",
        "KS",
    ]
    assert rens_liste(linjer) == [
        "Møre og Romsdal fylkeskommune",
        "Fylkesmannen i Nord-Trøndelag",
        "Strand Unikorn AS",
        "Fiskå Mølle AS",
        "KS",
    ]


# ---------- Ekte sider og PDF-er ----------


def test_helsedirektoratet_liste_pa_siden_med_kommunene():
    """Kriterium 3: «Alle landets kommuner» og KS står i listen (mat og måltider)."""
    funnet = fra_html(_html("helsedirektoratet_mat.html"))
    assert funnet.apen
    assert "Alle landets kommuner" in funnet.parter
    assert "KS – Kommunesektorens organisasjon" in funnet.parter
    # Gruppeoverskrifter og innledende tekst er ikke parter.
    assert "Universitet og høgskoler" not in funnet.parter
    assert not any(p.startswith("Nedenfor listes") for p in funnet.parter)
    assert VURDERING.regionflagg(funnet.parter) == ["Alle kommuner", "KS"]


def test_helsedirektoratet_uten_kommunene():
    """Kriterium 4: breddekompetanse i legers spesialistutdanning er ikke sendt regionen."""
    funnet = fra_html(_html("helsedirektoratet_bredde.html"))
    assert funnet.apen
    assert "Alle regionale helseforetak" in funnet.parter
    assert 5 < len(funnet.parter) < 30  # listen stopper før resten av høringsteksten
    assert VURDERING.regionflagg(funnet.parter) == []


def test_dmp_lenke_til_pdf_og_ks_i_listen():
    funnet = fra_html(_html("dmp_medisinsk_utstyr.html"), "https://www.dmp.no/nyheter/x")
    assert funnet.parter == []
    assert funnet.pdf.startswith("https://www.dmp.no/contentassets/")
    assert funnet.pdf.endswith(".pdf")
    parter = _pdf("dmp_medisinsk_utstyr_liste.pdf")
    assert len(parter) > 80
    assert "KS" in parter
    assert "Helse Sør-Øst RHF" in parter
    assert VURDERING.regionflagg(parter) == ["KS"]


def test_dmp_grossist_uten_regionen():
    parter = _pdf("dmp_grossist_liste.pdf")
    assert "Legemiddelgrossistforeningen" in parter
    assert VURDERING.regionflagg(parter) == []


def test_landbruksdirektoratet_pdf_med_adresser():
    funnet = fra_html(_html("landbruk.html"), "https://www.landbruksdirektoratet.no/nb/x/")
    assert "H%C3%B8ringsinstanser.pdf" in funnet.pdf
    parter = _pdf("landbruk_liste.pdf")
    assert parter[0] == "Felleskjøpet Agri SA"
    assert "Strand Unikorn AS" in parter  # adressen i Moelv er fjernet
    assert len(parter) == 11
    assert VURDERING.regionflagg(parter) == []


def test_digdir_tabell_med_adresser_gir_ikke_falskt_flagg():
    parter = _pdf("digdir_mottakerliste.pdf")
    assert "Fylkesmannen i Oppland" in parter
    assert "Møre og Romsdal fylkeskommune" in parter
    assert not any(p.startswith("Postboks") for p in parter)
    assert VURDERING.regionflagg(parter) == []  # «2626 Lillehammer» er en adresse


def test_skatteetaten_lenke_til_liste():
    funnet = fra_html(_html("skatteetaten.html"), "https://www.skatteetaten.no/rettskilder/x/")
    assert funnet.pdf.startswith("https://www.skatteetaten.no/contentassets/")


def test_dibk_apen_uten_liste():
    funnet = fra_html(_html("dibk.html"), "https://www.dibk.no/x")
    assert funnet.apen
    assert funnet.parter == []  # lenkene på siden er høringssvar, ikke høringsparter


# ---------- Innhenting med gjenbruk og robots.txt ----------


class _Nett:
    def __init__(self, sider: dict, sperret: set[str] = frozenset()):
        self.sider = sider
        self.sperret = sperret
        self.kall: list[str] = []

    def hent(self, url, **_):
        self.kall.append(url)
        if url in self.sperret:
            raise SperretAvRobots(url)
        innhold = self.sider[url]
        if isinstance(innhold, Exception):
            raise innhold
        if isinstance(innhold, bytes):
            return SimpleNamespace(content=innhold, text="", headers={"Content-Type": "pdf"})
        return SimpleNamespace(content=innhold.encode(), text=innhold, headers={})


class _Kilde(Kilde):
    def hent(self):
        return []


def _hoering(lenke: str, frist: date | None = None) -> Hoering:
    return Hoering(
        kilde="Test",
        kategori="",
        prioritet=2,
        instans="Test",
        tittel="Test",
        lenke=lenke,
        frist=frist or date.today() + timedelta(days=30),
    )


def test_fyll_leser_pdf_og_gjenbruker_forrige():
    side = "https://www.dmp.no/nyheter/x"
    pdf = "https://www.dmp.no/contentassets/3bc4c24576214eb3bcd8502d8f84c810/26_22268-4-horingsliste-40178854_1_1.pdf"
    nett = _Nett(
        {
            side: _html("dmp_medisinsk_utstyr.html"),
            pdf: (FIX / "dmp_medisinsk_utstyr_liste.pdf").read_bytes(),
        }
    )
    kilde = _Kilde({"navn": "Test", "horingsparter": {"detalj": True, "pdf": True}}, nett)
    h = _hoering(side)
    assert kilde.fyll_horingsparter([h]) == 2
    assert "KS" in h.horingsparter
    assert h.horingsparter_lenke == pdf
    # Neste kjøring: ingen nye kall, listen brukes om igjen.
    nett.kall.clear()
    h2 = _hoering(side)
    assert kilde.fyll_horingsparter([h2], {h.id: h.til_dict()}) == 0
    assert nett.kall == []
    assert h2.horingsparter == h.horingsparter


def test_fyll_pdf_sperret_i_robots():
    side = "https://www.skatteetaten.no/rettskilder/x/"
    funnet = fra_html(_html("skatteetaten.html"), side)
    nett = _Nett({side: _html("skatteetaten.html")}, sperret={funnet.pdf})
    kilde = _Kilde({"navn": "Test", "horingsparter": {"detalj": True, "pdf": True}}, nett)
    h = _hoering(side)
    kilde.fyll_horingsparter([h])
    assert h.horingsparter == []
    assert h.horingsparter_merknad == IKKE_TILGJENGELIG
    assert h.horingsparter_lenke == funnet.pdf


def test_fyll_feil_for_en_hoering_stopper_ikke_resten():
    a, b = "https://x.no/a", "https://x.no/b"
    nett = _Nett({a: TimeoutError("tidsavbrudd"), b: _html("helsedirektoratet_mat.html")})
    kilde = _Kilde({"navn": "Test", "horingsparter": {"detalj": True}}, nett)
    ha, hb = _hoering(a), _hoering(b)
    kilde.fyll_horingsparter([ha, hb])
    assert ha.horingsparter == [] and ha.horingsparter_merknad == ""  # prøves igjen neste gang
    assert "Alle landets kommuner" in hb.horingsparter
    assert hb.horingsparter_merknad == APEN_FOR_ALLE


def test_fyll_utlopte_og_kilder_uten_detalj():
    nett = _Nett({})
    utlopt = _hoering("https://x.no/gammel", date.today() - timedelta(days=1))
    _Kilde({"navn": "Test", "horingsparter": {"detalj": True}}, nett).fyll_horingsparter([utlopt])
    assert nett.kall == []
    storting = _hoering("https://x.no/storting")
    oppsett = {"navn": "Stortinget", "horingsparter": {"merknad": APEN_FOR_ALLE}}
    _Kilde(oppsett, nett).fyll_horingsparter([storting])
    assert storting.horingsparter_merknad == APEN_FOR_ALLE


def test_fyll_side_uten_liste_gir_ikke_oppgitt():
    side = "https://nkom.no/x"
    kilde = _Kilde(
        {"navn": "Test", "horingsparter": {"detalj": True}}, _Nett({side: _html("nkom.html")})
    )
    h = _hoering(side)
    kilde.fyll_horingsparter([h])
    assert h.horingsparter_merknad == IKKE_OPPGITT


def test_fyll_hoyst_maks_per_kjoring():
    sider = {f"https://x.no/{i}": "<html></html>" for i in range(5)}
    nett = _Nett(sider)
    kilde = _Kilde({"navn": "T", "horingsparter": {"detalj": True, "maks_per_kjoring": 2}}, nett)
    kilde.fyll_horingsparter([_hoering(u) for u in sider])
    assert len(nett.kall) == 2


# ---------- Prioritet, bygging og deduplisering ----------


def test_flagg_lofter_til_hoy_prioritet():
    p = Prioritet(KONFIG["felles"])
    h = {"tittel": "Forskrift om medisinsk utstyr", "ingress": "", "regionflagg": ["KS"]}
    assert p.vurder(h, {"prioritet": 3}) == (1, "regionen er høringspart")
    assert p.vurder({**h, "regionflagg": []}, {"prioritet": 3}) == (3, "")


def test_bygg_setter_kategorier_flagg_og_prioritet(tmp_path):
    kilder = tmp_path / "kilder"
    frist = (date.today() + timedelta(days=20)).isoformat()
    dmp = next(k for k in KONFIG["kilder"] if k["navn"] == "Direktoratet for medisinske produkter")
    lagre_kilde(
        kilder,
        {
            "kilde": dmp["navn"],
            "status": "ok",
            "hentet": "2026-10-26T10:00:00+01:00",
            "horinger": [
                {
                    "id": "a1",
                    "kilde": dmp["navn"],
                    "instans": "DMP",
                    "tittel": "Høring om endringer i forskrift for medisinsk utstyr",
                    "lenke": "https://www.dmp.no/x",
                    "frist": frist,
                    "ingress": "",
                    "horingsparter": _pdf("dmp_medisinsk_utstyr_liste.pdf"),
                }
            ],
        },
    )
    bygg({**KONFIG, "kilder": [dmp]}, kilder, tmp_path)
    (h,) = yaml.safe_load((tmp_path / "horinger.json").read_text("utf-8"))["horinger"]
    assert h["regionflagg"] == ["KS"]
    assert h["prioritet"] == 1
    assert h["prioritet_grunn"] == "regionen er høringspart"
    assert h["partkategorier"]["Kommuner og fylkeskommuner"] == 1


def test_dedup_tar_med_listen_fra_den_andre_versjonen():
    etat = {
        "id": "e",
        "kilde": "DiBK",
        "tittel": "Forslag til endringer i klimakrav i byggteknisk forskrift",
        "frist": "2026-05-05",
        "lenke": "https://dibk.no/x",
        "prioritet": 2,
        "horingsparter": [],
    }
    regj = {
        "id": "r",
        "kilde": "Regjeringen.no",
        "tittel": "Høring – endringer i klimakrav i byggteknisk forskrift",
        "frist": "2026-05-05",
        "lenke": "https://regjeringen.no/x",
        "prioritet": 1,
        "prioritet_grunn": "regionen er høringspart",
        "horingsparter": ["Alle kommuner", "KS"],
        "partkategorier": {"Alle kommuner": 1, "Kommuner og fylkeskommuner": 1},
        "regionflagg": ["Alle kommuner", "KS"],
    }
    (h,) = dedupliser([regj, etat])
    assert h["kilde"] == "DiBK"
    assert h["horingsparter"] == ["Alle kommuner", "KS"]
    assert h["regionflagg"] == ["Alle kommuner", "KS"]
    assert h["prioritet"] == 1
