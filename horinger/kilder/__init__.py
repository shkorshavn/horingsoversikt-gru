"""Register over kildemodulene. Nøkkelen er feltet `modul` i sources.yaml."""

from __future__ import annotations

from horinger.kilder.bane_nor import BaneNor
from horinger.kilder.base import Kilde
from horinger.kilder.digdir import Digdir
from horinger.kilder.dsb import Dsb
from horinger.kilder.enkle_lister import EnkelListe
from horinger.kilder.etater import (
    Arbeidstilsynet,
    Dmp,
    EnkeltSide,
    Landbruksdirektoratet,
    Mattilsynet,
    Nasjonalarkivet,
    Nkom,
    Politiet,
    Riksantikvaren,
    Skatteetaten,
)
from horinger.kilder.innlandet_fk import InnlandetFylkeskommune
from horinger.kilder.jernbanedirektoratet import Jernbanedirektoratet
from horinger.kilder.miljodirektoratet import Miljodirektoratet
from horinger.kilder.nve import Nve
from horinger.kilder.nye_veier import NyeVeier
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
    # Sprint 4: direktorater og etater med prioritet 1
    "miljodirektoratet": Miljodirektoratet,
    "nve": Nve,
    "dsb": Dsb,
    "helsedirektoratet": EnkelListe,
    "bufdir": EnkelListe,
    "dibk": EnkelListe,
    "digdir": Digdir,
    "nye_veier": NyeVeier,
    "jernbanedirektoratet": Jernbanedirektoratet,
    "bane_nor": BaneNor,
    # Sprint 5: prioritet 2 og 3, og etater som bare tas med når det er aktuelt for regionen
    "nkom": Nkom,
    "landbruksdirektoratet": Landbruksdirektoratet,
    "riksantikvaren": Riksantikvaren,
    "nasjonalarkivet": Nasjonalarkivet,
    "dmp": Dmp,
    "mattilsynet": Mattilsynet,
    "arbeidstilsynet": Arbeidstilsynet,
    "politiet": Politiet,
    "skatteetaten": Skatteetaten,
    "enkeltside": EnkeltSide,
}
