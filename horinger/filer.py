"""Lesing og skriving av JSON-filer.

Filene skrives alltid i UTF-8 med linjeskift «\\n», også på Windows (Sveins PC), slik at git
ikke ser endringer bare på grunn av linjeskift.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml


def les_konfig(sti: Path) -> dict:
    """Leser sources.yaml."""
    with open(sti, encoding="utf-8") as fil:
        return yaml.safe_load(fil)


def les_json(sti: Path) -> dict | None:
    """Leser en JSON-fil, eller gir None hvis den ikke finnes."""
    if not sti.is_file():
        return None
    with open(sti, encoding="utf-8") as fil:
        return json.load(fil)


def skriv_json(sti: Path, data: dict) -> None:
    """Skriver JSON i UTF-8 med «\\n» som linjeskift."""
    sti.parent.mkdir(parents=True, exist_ok=True)
    with open(sti, "w", encoding="utf-8", newline="\n") as fil:
        json.dump(data, fil, ensure_ascii=False, indent=2)
        fil.write("\n")
