"""Kobling av høringsbrev i postlista mot høringene i oversikten (sprint 7).

Hver journalpost sammenlignes med hver høring. Poengsummen (0–100) bygger på:
- **Tittel:** likhet med rapidfuzz etter at ord som «Høring –», «Høyring av» og
  referansenumre er tatt bort.
- **Avsender:** normalisert navn. Store og små bokstaver ignoreres, avkortede navn håndteres
  («Arbeids- Og Inkluderingsdepart»), og forkortelser står i `felles.postliste.avsender_alias`.
  Ulik avsender trekker ned.
- **Referansenummer:** står samme saksnummer (f.eks. «20-38820», «26/4010») i begge, er det et
  sikkert treff.

`sikker_terskel` og `mulig_terskel` i sources.yaml avgjør nivået: «sikker» gir merket «Mottatt
av Gjøvik kommune», «mulig» gir «Mulig treff». Grensene er begrunnet i sprintrapport 7.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from rapidfuzz import fuzz

from horinger.filer import les_json
from horinger.postliste import postlistefil

SIKKER = "sikker"
MULIG = "mulig"

# Ord i starten av titler som ikke sier noe om innholdet.
_INNLEDNING = re.compile(
    r"^(?:(?:kopi|vs|sv)\s*[-:–]\s*)?"
    r"(?:(?:h[øo]y?ring(?:sbrev|snotat|sinvitasjon)?|invitasjon til h[øo]y?ring|offentlig "
    r"h[øo]y?ring)\s*(?:[-–:]\s*|om\s+|av\s+|på\s+|til\s+)?)+",
    re.IGNORECASE,
)
_REFERANSE = re.compile(r"\b(\d{2,4})\s*[/-]\s*(\d{3,7})\b")
_IKKE_ORD = re.compile(r"[^\wæøå]+", re.IGNORECASE)

# Trekk i poengsum når avsenderen er kjent og ulik høringens instans.
ULIK_AVSENDER = 15
# Tillegg når avsenderen er den samme.
LIK_AVSENDER = 5
# Avkortede navn i postlista (ca. 30 tegn): så mange tegn må stemme fra starten.
MIN_PREFIKS = 12


def rens_tittel(tittel: str) -> str:
    """Tittel uten «Høring –»-innledning, referansenumre og tegnsetting, med små bokstaver."""
    t = _INNLEDNING.sub("", (tittel or "").strip())
    t = _REFERANSE.sub(" ", t)
    t = t.replace("(", " ").replace(")", " ")
    return " ".join(_IKKE_ORD.sub(" ", t.casefold()).split())


def referanser(tekst: str) -> set[str]:
    """Saksnumre som «20-38820» og «26/4010», normalisert til «20/38820»."""
    return {f"{int(a) % 100:02d}/{int(b)}" for a, b in _REFERANSE.findall(tekst or "")}


def rens_avsender(navn: str, alias: dict[str, str]) -> str:
    """Normalisert avsendernavn: små bokstaver, ett mellomrom og forkortelser slått opp."""
    n = " ".join((navn or "").casefold().split())
    oppslag = {k.casefold(): v.casefold() for k, v in alias.items()}
    return oppslag.get(n, n)


def lik_avsender(a: str, b: str) -> bool:
    """Om to normaliserte avsendernavn er det samme. Tåler avkorting i postlista."""
    if not a or not b:
        return False
    if a == b:
        return True
    kort, lang = sorted((a, b), key=len)
    return len(kort) >= MIN_PREFIKS and lang.startswith(kort)


@dataclass
class Treff:
    """Beste høring for én journalpost."""

    hoering_id: str
    poeng: float
    niva: str  # SIKKER, MULIG eller ""


class Kobling:
    """Kobler journalposter mot høringer ut fra `felles.postliste` i sources.yaml."""

    def __init__(self, konfig: dict) -> None:
        self.alias = dict(konfig.get("avsender_alias", {}))
        self.sikker = float(konfig.get("sikker_terskel", 85))
        self.mulig = float(konfig.get("mulig_terskel", 70))

    def avsendere(self, hoering: dict) -> list[str]:
        """Navnene en høring kan komme fra: instans, kilde og kildene i «Også på»."""
        navn = [hoering.get("instans", ""), hoering.get("kilde", "")]
        navn += [o.get("kilde", "") for o in hoering.get("ogsa") or []]
        return [rens_avsender(n, self.alias) for n in navn if n]

    def poeng(self, journalpost: dict, hoering: dict) -> float:
        """Poengsum 0–100 for at journalposten er høringsbrevet for denne høringen."""
        ref_jp = referanser(journalpost.get("tittel", ""))
        ref_h = referanser(f"{hoering.get('tittel', '')} {hoering.get('lenke', '')}")
        if ref_jp and ref_jp & ref_h:
            return 100.0
        a, b = rens_tittel(journalpost.get("tittel", "")), rens_tittel(hoering.get("tittel", ""))
        if not a or not b:
            return 0.0
        # token_sort_ratio er streng på ordrekkefølge og lengde. token_set_ratio tåler at den ene
        # tittelen er kortere, men gir lett 100 for korte titler, så den teller litt mindre.
        tittel = max(fuzz.token_sort_ratio(a, b), 0.9 * fuzz.token_set_ratio(a, b))
        avsender = rens_avsender(journalpost.get("avsender", ""), self.alias)
        if avsender:
            if any(lik_avsender(avsender, h) for h in self.avsendere(hoering)):
                tittel += LIK_AVSENDER
            else:
                tittel -= ULIK_AVSENDER
        return round(max(0.0, min(100.0, tittel)), 1)

    def beste(self, journalpost: dict, hoeringer: list[dict]) -> Treff:
        """Høringen med høyest poengsum, med nivå etter tersklene."""
        best = Treff("", 0.0, "")
        for h in hoeringer:
            p = self.poeng(journalpost, h)
            if p > best.poeng:
                best = Treff(h["id"], p, "")
        if best.poeng >= self.sikker:
            best.niva = SIKKER
        elif best.poeng >= self.mulig:
            best.niva = MULIG
        return best


def koble_postlister(
    konfig: dict,
    kildemappe: Path,
    apne: list[dict],
    arkiv: dict[str, dict],
    forrige: dict | None,
    i_dag_: date,
) -> tuple[dict, list[dict]]:
    """Kobler journalpostene i postlistene mot høringene, og merker høringene.

    Gir tilbake innholdet til data/postliste_treff.json og statuslinjer for postlistene.
    Journalposter fra forrige bygging beholdes, slik at et merke blir stående etter at
    journalposten har falt ut av 14-dagersvinduet. Et sikkert treff fra før holdes fast så lenge
    høringen finnes. Journalposter uten treff vises i `vis_dager` dager.
    """
    oppsett = konfig.get("felles", {}).get("postliste", {})
    vis_dager = int(oppsett.get("vis_dager", 60))
    grense = i_dag_ - timedelta(days=vis_dager)
    kobling = Kobling(oppsett)
    kandidater = apne + [
        h for h in arkiv.values() if date.fromisoformat(h["utlopt"][:10]) >= grense
    ]
    alle_hoeringer = {h["id"]: h for h in [*apne, *arkiv.values()]}

    journalposter: dict[str, dict] = {j["id"]: j for j in (forrige or {}).get("journalposter", [])}
    status: list[dict] = []
    for p in konfig.get("postlister", []):
        lagret = les_json(postlistefil(kildemappe, p["navn"])) if p.get("aktiv") else None
        linje = {"kilde": p["navn"], "kjoring": p.get("kjoring", "github"), "type": "postliste"}
        if not p.get("aktiv"):
            status.append({**linje, "status": "ikke overvåket", "antall": 0})
            continue
        if lagret is None:
            status.append({**linje, "status": "ikke hentet", "antall": 0})
            continue
        status.append(
            {
                **linje,
                **{
                    k: lagret.get(k)
                    for k in ("status", "hentet", "sist_ok", "antall", "sekunder", "feil")
                    if lagret.get(k) is not None
                },
            }
        )
        for j in lagret.get("journalposter", []):
            journalposter[j["id"]] = {**journalposter.get(j["id"], {}), **j}

    beholdt: list[dict] = []
    for j in journalposter.values():
        gammel_id = j.get("hoering_id")
        if j.get("niva") == SIKKER and gammel_id in alle_hoeringer:
            pass  # sikre treff holdes fast
        else:
            treff = kobling.beste(j, kandidater)
            j["hoering_id"], j["poeng"], j["niva"] = (
                (treff.hoering_id, treff.poeng, treff.niva) if treff.niva else ("", treff.poeng, "")
            )
        koblet = j["niva"] and j["hoering_id"] in alle_hoeringer
        if not koblet and date.fromisoformat(j["dato"]) < grense:
            continue  # uten treff og eldre enn visningsperioden
        beholdt.append(j)
        if koblet:
            h = alle_hoeringer[j["hoering_id"]]
            h.setdefault("postliste", []).append(
                {
                    "kommune": j["kommune"],
                    "dato": j["dato"],
                    "tittel": j["tittel"],
                    "lenke": j["lenke"],
                    "niva": j["niva"],
                }
            )
    for h in alle_hoeringer.values():
        if h.get("postliste"):
            # Sikre treff først, deretter eldste journaldato (når kommunen mottok høringen).
            h["postliste"].sort(key=lambda x: (x["niva"] != SIKKER, x["dato"]))
    beholdt.sort(key=lambda j: (j["dato"], j["id"]), reverse=True)
    return {"journalposter": beholdt}, status
