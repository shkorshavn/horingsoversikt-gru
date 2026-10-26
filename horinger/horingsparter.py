"""Høringsparter: tolking av lister (HTML og PDF), kategorisering og regionflagg (sprint 6).

Kildene lagrer høringspartene slik de står hos kilden (`horingsparter`), og eventuelt en merknad
som «Åpen for alle» (`horingsparter_merknad`). Kategorier og regionflagg beregnes i bygg.py med
`Partvurdering`, ut fra `felles.horingsparter` i sources.yaml. Da slår endringer i ordlistene inn
ved neste bygging uten ny henting.

Regionflagget settes bare ut fra listen over høringsparter, ikke ut fra teksten ellers, og hver
part vurderes for seg. Slik gir «Sykehuset Innlandet, Gjøvik» eller en postadresse i Lillehammer
ikke flagg, mens «Gjøvik kommune» og «Alle landets kommuner» gjør det.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup, NavigableString, Tag

# Merknader når det ikke finnes en liste.
APEN_FOR_ALLE = "Åpen for alle"
IKKE_TILGJENGELIG = "Ikke tilgjengelig"
IKKE_OPPGITT = "Ikke oppgitt"

# Overskrifter og lenketekster som innleder en liste over høringsparter.
_LISTEORD = re.compile(
    r"h[øo]y?rings(?:instans(?:er|ar)?|liste|parter|mottakarar|mottakere)|adressat(?:er|liste)?"
    r"|mottak(?:er|ar)liste|adresseliste",
    re.IGNORECASE,
)
# Tekst som sier at alle kan svare.
_APEN = re.compile(
    r"alle (?:er velkomne|er velkommen|kan (?:gi|sende|komme)|som ønsker,? kan)"
    r"|offentlig (?:høring|innspillsrunde)|åpen høring|alle kan uttale seg",
    re.IGNORECASE,
)
# Linjer i en liste som ikke er høringsparter.
_IKKE_PART = re.compile(
    r"^(?:h[øo]y?rings(?:instans(?:er|ar)?|liste)|mottak(?:er|ar)liste|adresseliste|adressater"
    r"|side \d+(?: av \d+)?|\d+|vedlegg.*|liste over h[øo]y?ringsinstans\w*)[:.]?$",
    re.IGNORECASE,
)
# Adresser som står etter navnet i PDF-lister (Landbruksdirektoratet, Digdir m.fl.).
_ADRESSE = [
    re.compile(r"\s+(?:Postboks|Pb\.?|Boks|Postb\.)\s.*$", re.IGNORECASE),
    re.compile(r"\s+\d{4}\s+[A-ZÆØÅ][\wæøåÆØÅ .-]*$"),
    re.compile(r"\s+[A-ZÆØÅ][\wæøå.-]*(?:veien|vegen|gata|gate|vei|veg|stranda|plass)\s+\d+\w?$"),
    re.compile(r"\s+(?:Fylkeshuset|Statens hus)\b.*$", re.IGNORECASE),
]
# Linjer i PDF-tabeller som bare er en del av en adresse.
_ADRESSELINJE = re.compile(
    r"^(?:(?:Postboks|Pb\.?|Boks|Postb\.)\b|\d|(?:Fylkeshuset|Statens hus|Rådhuset)\b"
    r"|\S+(?:veien|vegen|gata|gate|vei|veg)\s+\d)",
    re.IGNORECASE,
)
# Poststed med store bokstaver på egen linje («BRØNNØYSUND», «MO I RANA»), men ikke firmanavn
# som «DNV AS».
_POSTSTED = re.compile(
    r"^(?!.*\b(?:AS|ASA|SA|SF|HF|IKS|KF|BA|DA|ANS)$)[A-ZÆØÅ-]{3,}(?: [A-ZÆØÅ-]+)*$"
)
_MELLOMROM = re.compile(r"\s+")
# Markerer en overskrift i linjene fra _linjer().
OVERSKRIFT = "\x01"


def _rens(linje: str) -> str:
    linje = _MELLOMROM.sub(" ", linje.replace("\xa0", " ")).strip(" \t•·–-;,")
    for monster in _ADRESSE:
        linje = monster.sub("", linje)
    return linje.strip(" ,;.")


def rens_liste(linjer: list[str], sla_sammen: bool = True) -> list[str]:
    """Renser linjer til høringsparter: fjerner overskrifter, adresser og doble oppføringer.

    Linjer som er brutt i PDF-en («Møre og Romsdal» + «fylkeskommune»), slås sammen når neste
    linje begynner med liten bokstav, eller linjen slutter med bindestrek eller «og».
    """
    samlet: list[str] = []
    for ra in linjer:
        linje = _MELLOMROM.sub(" ", ra.replace("\xa0", " ")).strip()
        if not linje:
            continue
        if (
            sla_sammen
            and samlet
            and (
                linje[0].islower()
                or samlet[-1].endswith(("-", " og", ",", " i", " for", " av"))
                and not _IKKE_PART.match(linje)
            )
        ):
            skille = "" if samlet[-1].endswith("-") else " "
            samlet[-1] = f"{samlet[-1]}{skille}{linje}"
            continue
        samlet.append(linje)
    parter: list[str] = []
    sett: set[str] = set()
    for linje in samlet:
        navn = _rens(linje)
        if len(navn) < 2 or _IKKE_PART.match(navn):
            continue
        if navn.casefold() not in sett:
            sett.add(navn.casefold())
            parter.append(navn)
    return parter


def er_apen(tekst: str) -> bool:
    """Om teksten sier at alle kan gi høringssvar."""
    return bool(_APEN.search(tekst or ""))


def _linjer(element: Tag) -> list[str]:
    """Tekstlinjer i et element: hvert listepunkt, avsnitt og hver <br> gir en ny linje."""
    linjer: list[str] = []
    gjeldende: list[str] = []

    def bryt() -> None:
        if gjeldende:
            linjer.append("".join(gjeldende))
            gjeldende.clear()

    def gaa(node: Tag) -> None:
        for barn in node.children:
            if isinstance(barn, NavigableString):
                gjeldende.append(str(barn))
            elif isinstance(barn, Tag):
                if barn.name == "br":
                    bryt()
                elif barn.name in ("h2", "h3", "h4", "h5", "h6"):
                    # Gruppeoverskrifter i listen («Universitet og høgskoler») er ikke parter.
                    bryt()
                    linjer.append(OVERSKRIFT + barn.get_text(" ", strip=True))
                elif barn.name in ("li", "p", "div", "tr", "dt", "dd"):
                    bryt()
                    gaa(barn)
                    bryt()
                else:
                    gaa(barn)

    gaa(element)
    bryt()
    return linjer


@dataclass
class Liste:
    """Det som ble funnet om høringspartene på en side."""

    parter: list[str] = field(default_factory=list)
    apen: bool = False
    # Lenke til en liste i PDF når siden ikke har listen selv.
    pdf: str = ""


def fra_html(html: str | BeautifulSoup, lenke: str = "") -> Liste:
    """Finner høringspartene på en detaljside.

    Leter etter en overskrift som «Høringsinstanser» og tar med teksten fram til neste
    overskrift på samme eller høyere nivå. Finnes ikke listen på siden, men en lenke til den
    (f.eks. «Høringsliste (PDF)»), returneres lenken i `pdf`.
    """
    suppe = html if isinstance(html, BeautifulSoup) else BeautifulSoup(html, "html.parser")
    resultat = Liste(apen=er_apen(suppe.get_text(" ")))
    for overskrift in suppe.find_all(["h2", "h3", "h4", "strong", "button", "summary"]):
        tittel = overskrift.get_text(" ", strip=True)
        if not (_LISTEORD.search(tittel) and len(tittel) < 60):
            continue
        # På nettsider er hver part en egen linje («proLAR» skal ikke slås sammen med linjen
        # over). Bare PDF-er bryter lange navn over flere linjer.
        parter = rens_liste(_bare_listen(_innhold_etter(overskrift)), sla_sammen=False)
        # Korte avsnitt som bare viser til et vedlegg, er ikke en liste.
        if len(parter) >= 2:
            resultat.parter = parter
            return resultat
    for a in suppe.find_all("a", href=True):
        tekst = f"{a.get_text(' ', strip=True)} {a['href']}"
        if _LISTEORD.search(tekst) and not a["href"].startswith("mailto:"):
            resultat.pdf = urljoin(lenke, a["href"])
            break
    return resultat


# Overskrifter som betyr at listen over høringsparter er slutt.
_NESTE_AVSNITT = re.compile(
    r"^(?:kontakt(?:person|personer)?|høringsbrev|høringsnotat|bakgrunn|vedlegg|dokumenter"
    r"|høringsdokument(?:er)?|høringssvar|høringsuttalelser|høringsinnspill|frist|spørsmål.*"
    r"|send(?: inn)? (?:høringssvar|innspill).*|om høringen)[:.]?$",
    re.IGNORECASE,
)
# Linjer som innleder en underliste («Referansegruppens medlemmer, herunder representanter fra»).
_INNLEDNING = re.compile(r"(?:\bfra|\bherunder|\bbl\.a\.|\bblant annet|:)$", re.IGNORECASE)


def _er_prosa(linje: str) -> bool:
    """Om linjen er løpende tekst og ikke navnet på en høringspart."""
    ord_ = linje.split()
    return (
        len(ord_) > 14
        or (linje.endswith(".") and len(ord_) >= 6)
        or (linje.endswith(":") and len(ord_) >= 3)
        or er_apen(linje)
    )


def _bare_listen(linjer: list[str]) -> list[str]:
    """Linjene som er høringsparter: innledende tekst hoppes over, og listen slutter ved første
    avsnitt med løpende tekst etter at den har begynt (sider limt inn fra Word mangler ofte
    overskrifter som avgrenser listen)."""
    liste: list[str] = []
    for linje in linjer:
        linje = _MELLOMROM.sub(" ", linje.replace("\xa0", " ")).strip()
        if not linje:
            continue
        if _NESTE_AVSNITT.match(linje.lstrip(OVERSKRIFT)):
            if liste:
                break  # «Kontakt», «Høringsbrev» o.l.: listen er slutt
            continue
        if linje.startswith(OVERSKRIFT) or _INNLEDNING.search(linje):
            continue
        if _er_prosa(linje):
            if len(liste) >= 2:
                break
            continue
        liste.append(linje)
    return liste


_NIVA = {"h1": 1, "h2": 2, "h3": 3, "h4": 4}


def _innhold_etter(overskrift: Tag) -> list[str]:
    """Linjene etter en overskrift, fram til neste overskrift på samme eller høyere nivå."""
    niva = _NIVA.get(overskrift.name, 5)
    # En overskrift inne i en knapp eller <summary> (trekkspill): innholdet står i neste element.
    start = overskrift
    while start.parent is not None and start.parent.name in ("button", "summary", "span"):
        start = start.parent
    linjer: list[str] = []
    for sosken in start.find_next_siblings():
        if not isinstance(sosken, Tag):
            continue
        if sosken.name in _NIVA and _NIVA[sosken.name] <= niva:
            break
        if sosken.name in _NIVA:
            linjer.append(OVERSKRIFT + sosken.get_text(" ", strip=True))
            continue
        linjer.extend(_linjer(sosken))
    if not linjer and start.parent is not None:
        # Trekkspill: overskriften står i en egen beholder, og listen i neste.
        neste = start.parent.find_next_sibling()
        if isinstance(neste, Tag):
            linjer = _linjer(neste)
    return linjer


def fra_pdf(innhold: bytes) -> list[str]:
    """Leser høringspartene fra en PDF. Gir tom liste når PDF-en ikke har tekst (skannet)."""
    from pypdf import PdfReader  # importeres her: bare kildene med PDF-lister trenger pypdf

    leser = PdfReader(io.BytesIO(innhold))
    tekst = "\n".join(side.extract_text() or "" for side in leser.pages)
    # Kolonner i tabeller (navn og adresse) skilles med mange mellomrom. Ta bare navnet.
    linjer = [re.split(r"\s{4,}", linje.strip())[0] for linje in tekst.splitlines()]
    return rens_liste(
        [
            linje
            for linje in linjer
            if not _ADRESSELINJE.match(linje.strip()) and not _POSTSTED.match(linje.strip())
        ]
    )


# ---------------------------------------------------------------------------------------------
# Kategorisering og regionflagg


def _norm(tekst: str) -> str:
    return _MELLOMROM.sub(" ", tekst.casefold().replace("\xa0", " ")).strip(" .,;:")


@dataclass
class Regel:
    """Én regel for regionflagg eller kategori, fra sources.yaml."""

    navn: str
    # Treffer bare når parten er nøyaktig lik en av frasene (f.eks. «KS»).
    eksakt: list[str] = field(default_factory=list)
    # Treffer når en part er lik, eller begynner med, en av frasene (hele ord).
    start: list[str] = field(default_factory=list)
    # Treffer når en av frasene står som hele ord hvor som helst i parten.
    inneholder: list[str] = field(default_factory=list)
    # Treffer når et ord i parten slutter på frasen («Kommunal- og distriktsdepartementet»).
    ordslutt: list[str] = field(default_factory=list)
    # Parter med disse frasene treffer aldri regelen.
    utelat: list[str] = field(default_factory=list)

    @classmethod
    def fra_konfig(cls, data: dict) -> Regel:
        """Lager en regel fra en oppføring i sources.yaml."""
        return cls(
            navn=data["navn"],
            eksakt=[_norm(o) for o in data.get("eksakt", [])],
            start=[_norm(o) for o in data.get("start", [])],
            inneholder=[_norm(o) for o in data.get("inneholder", [])],
            ordslutt=[_norm(o) for o in data.get("ordslutt", [])],
            utelat=[_norm(o) for o in data.get("utelat", [])],
        )

    def treff(self, part: str, omrader: tuple[str, ...]) -> bool:
        """Om høringsparten treffer regelen."""
        p = _norm(part)
        if any(_ord_i(o, p) for o in self.utelat):
            return False
        if p in self.eksakt:
            return True
        for frase in self.start:
            if p == frase:
                return True
            if p.startswith(frase) and not p[len(frase)].isalnum():
                rest = p[len(frase) :]
                # «Kommunene i Troms» er ikke alle kommuner, «alle kommuner i Innlandet» er det.
                if m := re.match(r"\s+i\s+(\S+)", rest):
                    return m.group(1) in omrader
                return True
        if any(re.search(rf"{re.escape(o)}(?![\wæøå])", p) for o in self.ordslutt):
            return True
        return any(_ord_i(o, p) for o in self.inneholder)


def _ord_i(frase: str, tekst: str) -> bool:
    return re.search(rf"(?<![\wæøå]){re.escape(frase)}(?![\wæøå])", tekst) is not None


class Partvurdering:
    """Kategoriserer høringsparter og avgjør regionflagget, ut fra `felles.horingsparter`."""

    def __init__(self, konfig: dict) -> None:
        self.omrader = tuple(_norm(o) for o in konfig.get("omrader", ["landet", "norge"]))
        flagg = konfig.get("regionflagg", {})
        self.flaggregler = [Regel.fra_konfig(r) for r in flagg.get("regler", [])]
        for kommune in flagg.get("kommuner", []):
            # Bare «Gjøvik kommune». Navnet alene kan være poststedet i en adresse i en PDF-liste
            # («Postboks 987, 2626 Lillehammer»), og «Gjøvik tingrett» er ikke kommunen.
            self.flaggregler.append(
                Regel(navn=f"{kommune} kommune", start=[_norm(f"{kommune} kommune")])
            )
        self.kategorier = [Regel.fra_konfig(r) for r in konfig.get("kategorier", [])]
        self.annet = konfig.get("annet", "Andre")

    def regionflagg(self, parter: list[str]) -> list[str]:
        """Grunnene til regionflagget, f.eks. ["Alle kommuner", "KS"]. Tom liste: ingen flagg."""
        grunner: list[str] = []
        for regel in self.flaggregler:
            if regel.navn in grunner:
                continue
            if any(regel.treff(p, self.omrader) for p in parter):
                grunner.append(regel.navn)
        return grunner

    def kategoriser(self, parter: list[str]) -> dict[str, int]:
        """Antall parter per kategori, i rekkefølgen fra sources.yaml. «Andre» til slutt."""
        antall: dict[str, int] = {}
        for part in parter:
            navn = next(
                (k.navn for k in self.kategorier if k.treff(part, self.omrader)), self.annet
            )
            antall[navn] = antall.get(navn, 0) + 1
        rekkefolge = [k.navn for k in self.kategorier] + [self.annet]
        return {n: antall[n] for n in rekkefolge if n in antall}

    def vurder(self, hoering: dict) -> dict:
        """Feltene bygg.py legger til: `partkategorier` og `regionflagg`."""
        parter = hoering.get("horingsparter") or []
        return {
            "partkategorier": self.kategoriser(parter),
            "regionflagg": self.regionflagg(parter),
        }
