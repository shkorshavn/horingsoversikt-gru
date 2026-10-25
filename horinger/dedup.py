"""Deduplisering av høringer som publiseres av flere kilder.

Mange direktoratshøringer ligger både på etatens side og på regjeringen.no (f.eks. DiBK på
oppdrag fra KDD). To høringer regnes som den samme når

- fristen er lik (og ikke mangler), og
- titlene er nesten like: minst 80 % av de meningsbærende ordene er felles (Jaccard), etter
  at ord som «høring», «forslag» og «endringer» er fjernet.

Da beholdes etatens versjon, fordi den har etaten som høringsinstans og ofte flere detaljer,
og den andre lenken lagres i feltet `ogsa`. Mellom to etater beholdes den som står først i
sources.yaml.
"""

from __future__ import annotations

import re

LIKHET = 0.8
_STOPPORD = {
    "høring",
    "høyring",
    "høringsnotat",
    "forslag",
    "til",
    "om",
    "av",
    "i",
    "og",
    "på",
    "for",
    "med",
    "endring",
    "endringer",
    "endringar",
    "ny",
    "nye",
    "the",
    "en",
    "et",
    "ei",
    "frå",
    "fra",
    "sendes",
    "sendt",
    "ut",
    "er",
    "vedrørende",
    "knyttet",
}
_ORD = re.compile(r"[a-zæøå0-9]+")
REGJERINGEN = "Regjeringen.no"


def nokkelord(tittel: str) -> set[str]:
    """De meningsbærende ordene i en tittel, med små bokstaver."""
    return {o for o in _ORD.findall((tittel or "").lower()) if o not in _STOPPORD and len(o) > 1}


def like(a: dict, b: dict) -> bool:
    """Om to høringer er den samme, etter reglene over."""
    if not a.get("frist") or a.get("frist") != b.get("frist"):
        return False
    x, y = nokkelord(a.get("tittel", "")), nokkelord(b.get("tittel", ""))
    if not x or not y:
        return False
    return len(x & y) / len(x | y) >= LIKHET


def dedupliser(horinger: list[dict]) -> list[dict]:
    """Slår sammen like høringer. Rekkefølgen i listen avgjør hvem som vinner mellom etater."""
    beholdt: list[dict] = []
    for h in horinger:
        treff = next((b for b in beholdt if b["kilde"] != h["kilde"] and like(b, h)), None)
        if treff is None:
            beholdt.append(dict(h))
            continue
        if treff["kilde"] == REGJERINGEN and h["kilde"] != REGJERINGEN:
            # Etatens versjon tar plassen, regjeringen.no blir «også publisert».
            ny = dict(h)
            ny["ogsa"] = [
                *treff.get("ogsa", []),
                {"kilde": treff["kilde"], "lenke": treff["lenke"]},
            ]
            beholdt[beholdt.index(treff)] = ny
        else:
            treff.setdefault("ogsa", []).append({"kilde": h["kilde"], "lenke": h["lenke"]})
    return beholdt
