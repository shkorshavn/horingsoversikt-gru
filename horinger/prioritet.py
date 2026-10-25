"""Foreslått prioritet per høring.

Reglene (Svein 25.10.2026):
1. Utgangspunktet er kildens `prioritet` i sources.yaml.
2. En kilde kan gi enkelte høringsinstanser egen prioritet (`prioritet_instans`). For
   regjeringen.no har KDD, KD, HOD, AID, DFD og FIN prioritet 1 (høy), de andre departementene
   prioritet 2 (middels), slik spesifikasjonen sier.
3. En høring med prioritet 2 eller 3 løftes til 1 når tittel eller ingress klart gjelder
   kommunene eller regionen: ordene i `felles.prioritet_loft.ord` (kommunene, fylkeskommunen,
   plan- og bygningsloven …) eller en kommune i geografien.

Grunnen lagres i `prioritet_grunn`, slik at siden kan vise hvorfor en høring er løftet.
"""

from __future__ import annotations

from horinger.geografi import GeografiFilter
from horinger.sokeord import Sokeord


class Prioritet:
    """Beregner foreslått prioritet ut fra kildens oppsett og teksten i høringen."""

    def __init__(self, felles: dict) -> None:
        loft = felles.get("prioritet_loft", {})
        self.kommuneord = Sokeord(loft.get("ord", []))
        self.geografi = GeografiFilter(felles.get("geografi", {}))

    def vurder(self, hoering: dict, kilde_konfig: dict) -> tuple[int, str]:
        """Gir (prioritet, grunn). Grunnen er tom når prioriteten er kildens vanlige."""
        prioritet = int(kilde_konfig.get("prioritet", 3))
        instans = hoering.get("instans", "")
        for verdi, instanser in (kilde_konfig.get("prioritet_instans") or {}).items():
            if any(instans.startswith(i) for i in instanser):
                prioritet = int(verdi)
                break
        if prioritet == 1:
            return 1, ""
        tekst = f"{hoering.get('tittel', '')} {hoering.get('ingress', '')}"
        if self.kommuneord.treff(tekst):
            return 1, "gjelder kommunene"
        if self.geografi.vurder(tekst).relevant:
            return 1, "gjelder regionen"
        return prioritet, ""
