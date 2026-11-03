"""Regelen «alltid med» for Mjøsa og vann (sprint 12, Svein 03.11.2026).

Høringer som gjelder Mjøsa, vannkvalitet, overvåking av innsjøer, fartsgrenser og båttrafikk
på innsjøer og elver, utslipp og avrenning til vann, ammunisjon i Mjøsa, drikkevann, vannverk,
flom eller vassdragsregulering skal alltid være med. Ordene står i
`felles.relevans.alltid_med` i sources.yaml: `ord` treffer i tittel, ingress og teksten fra
høringssiden, og `ord_tittel` bare i tittel og ingress (vanlige ord som ellers gir falske treff).

Store og små bokstaver spiller ingen rolle. Et ord med * treffer ord som begynner slik
(«innsjø*» treffer «innsjøer»), og et ord uten * må stå som helt ord («Mjøsa»). Et oppslag med
« + » krever at alle delene står i teksten, f.eks. «ammunisjon* + Mjøsa».
"""

from __future__ import annotations

import re


def _monster(ord_: str) -> re.Pattern[str]:
    """«innsjø*» treffer ord som begynner slik («innsjøer»). Uten * må hele ordet stemme, slik at
    «Mjøsa» ikke treffer firmanavn som «Mjøsanlegget» i lister over høringsparter."""
    ord_ = ord_.strip()
    if ord_.endswith("*"):
        return re.compile(rf"(?<![\wæøå]){re.escape(ord_[:-1])}", re.IGNORECASE)
    return re.compile(rf"(?<![\wæøå]){re.escape(ord_)}(?![\wæøå])", re.IGNORECASE)


class AlltidMed:
    """Avgjør om en tekst treffer regelen «alltid med»."""

    def __init__(self, konfig: dict | None) -> None:
        konfig = konfig or {}
        self.grunn = str(konfig.get("grunn") or "gjelder Mjøsa og vann")
        self._overalt = _regler(konfig.get("ord"))
        self._tittel = _regler(konfig.get("ord_tittel"))

    def treff(self, tekst: str | None, detaljtekst: str | None = None) -> str:
        """Første oppslag som treffer, eller tom tekst.

        `tekst` er tittel og ingress. `detaljtekst` er teksten fra høringssiden, der bare `ord`
        (ikke `ord_tittel`) vurderes.
        """
        tekst = tekst or ""
        hele = f"{tekst} {detaljtekst or ''}"
        for regler, mot in ((self._overalt, hele), (self._tittel, tekst)):
            for oppslag, monstre in regler:
                if all(m.search(mot) for m in monstre):
                    return oppslag
        return ""

    def treff_hoering(self, h: dict) -> str:
        """Treff for en høring (ordbok med tittel, ingress og ev. detaljtekst)."""
        return self.treff(f"{h.get('tittel') or ''} {h.get('ingress') or ''}", h.get("detaljtekst"))


def _regler(oppslag: list | None) -> list[tuple[str, list[re.Pattern[str]]]]:
    resultat = []
    for o in oppslag or []:
        deler = [d for d in str(o).split(" + ") if d.strip()]
        if deler:
            resultat.append((str(o), [_monster(d) for d in deler]))
    return resultat


def fra_felles(felles: dict) -> AlltidMed:
    """Regelen fra de felles innstillingene i sources.yaml."""
    return AlltidMed((felles.get("relevans") or {}).get("alltid_med"))
