"""Register over kildemodulene. Nøkkelen er feltet `modul` i sources.yaml."""

from __future__ import annotations

from horinger.kilder.base import Kilde

KILDER: dict[str, type[Kilde]] = {}
