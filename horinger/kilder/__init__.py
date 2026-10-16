"""Register over kildemodulene. Nøkkelen er feltet `modul` i sources.yaml."""

from __future__ import annotations

from horinger.kilder.base import Kilde
from horinger.kilder.innlandet_fk import InnlandetFylkeskommune
from horinger.kilder.regjeringen import Regjeringen
from horinger.kilder.statsforvalteren import Statsforvalteren
from horinger.kilder.stortinget import Stortinget
from horinger.kilder.vegvesen import Vegvesen

KILDER: dict[str, type[Kilde]] = {
    "stortinget": Stortinget,
    "regjeringen": Regjeringen,
    "vegvesen": Vegvesen,
    "innlandet_fk": InnlandetFylkeskommune,
    "statsforvalteren": Statsforvalteren,
}
