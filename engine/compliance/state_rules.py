"""
state_rules.py — State-specific building regulation loader and hierarchy resolver.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

REG_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "regulations"


def load_central_codes() -> List[Dict[str, Any]]:
    """Loads national central codes: ENS 2021, ECBC 2017, NBC 2016."""
    central_dir = REG_DIR / "central"
    codes = []
    if central_dir.exists():
        for f in central_dir.glob("*.json"):
            with open(f, "r", encoding="utf-8") as fp:
                codes.append(json.load(fp))
    return codes


def load_state_code(state_name_or_code: str) -> Optional[Dict[str, Any]]:
    """Loads state-specific building rules if verified."""
    states_dir = REG_DIR / "states"
    if not states_dir.exists():
        return None

    clean_query = state_name_or_code.lower().replace(" ", "_")

    for f in states_dir.glob("*.json"):
        if f.stem.lower() == clean_query:
            with open(f, "r", encoding="utf-8") as fp:
                return json.load(fp)

    # Search inside state files for matching name or code
    for f in states_dir.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            if data.get("state_name", "").lower() == state_name_or_code.lower() or \
               data.get("state_code", "").lower() == state_name_or_code.lower():
                return data

    return None
