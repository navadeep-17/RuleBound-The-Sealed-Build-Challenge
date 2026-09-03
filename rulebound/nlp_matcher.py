"""Deterministic Natural Language Brief Semantic Parser for RuleBound.
Extracts structured design intent from plain-English client briefs without external LLM calls.
Guarantees 100% offline, deterministic translation from natural language to spatial constraints.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from rulebound.models import CatalogItem, Finish


@dataclass(frozen=True)
class BriefIntent:
    target_capacity: int | None
    typology: str  # "paired_pods", "perimeter_carrels", "hybrid_zones", "open_workshop"
    preferred_finishes: tuple[str, ...]
    collaboration_tables: int
    storage_units: int
    acoustic_accessories: int
    preserve_daylight: bool
    prioritize_egress: bool


WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twelve": 12, "fourteen": 14, "sixteen": 16, "eighteen": 18, "twenty": 20
}

FINISH_KEYWORDS = {
    "natural oak": "F01",
    "oak": "F01",
    "graphite": "F03",
    "walnut": "F05",
    "matte black": "F02",
    "black": "F02",
    "neutral": "F04",
    "birch": "F06",
    "charcoal": "F13",
    "grey": "F14",
    "gray": "F14",
    "acoustic felt": "F16",
    "felt": "F16",
    "sage": "F17",
    "olive": "F18",
}


def parse_brief_text(brief_text: str) -> BriefIntent:
    """Parses a plain-English client brief into strongly-typed BriefIntent."""
    text_lower = brief_text.lower()

    # 1. Extract Target Capacity
    cap = None
    team_match = re.search(r"team\s+of\s+(\d+)", text_lower)
    if team_match:
        cap = int(team_match.group(1))
    else:
        cap_match = re.search(r"(\d+)\s*[-]?\s*(?:person|people)", text_lower)
        if cap_match:
            cap = int(cap_match.group(1))
        else:
            # Check word numbers like "twelve-person"
            for word, val in WORD_TO_NUM.items():
                if re.search(rf"\b{word}\s*[-]?\s*(?:person|people)\b", text_lower):
                    cap = val
                    break

    # 2. Extract Typology
    if "paired" in text_lower or "pod" in text_lower:
        typology = "paired_pods"
    elif "focus" in text_lower or "carrel" in text_lower or "library" in text_lower:
        typology = "perimeter_carrels"
    elif "hybrid" in text_lower or "touchdown" in text_lower:
        typology = "hybrid_zones"
    elif "workshop" in text_lower or "flexible" in text_lower:
        typology = "open_workshop"
    else:
        typology = "paired_pods"

    # 3. Extract Preferred Finishes
    found_finishes: list[str] = []
    for kw, f_id in FINISH_KEYWORDS.items():
        if kw in text_lower and f_id not in found_finishes:
            found_finishes.append(f_id)

    # 4. Extract Collaboration Tables
    collab_count = 0
    if "collaboration" in text_lower or "touchdown" in text_lower:
        # Check explicit count e.g. "two collaboration tables", "one compact collaboration table"
        count_match = re.search(r"(\w+)\s+(?:compact\s+)?(?:collaboration|touchdown)\s+(?:table|zone)", text_lower)
        if count_match:
            word = count_match.group(1)
            collab_count = WORD_TO_NUM.get(word, int(word) if word.isdigit() else 1)
        else:
            collab_count = 1

    # 5. Extract Storage Units
    storage_count = 0
    if "storage" in text_lower:
        count_match = re.search(r"(\w+)\s+(?:lockable\s+|accessible\s+|distributed\s+)?storage", text_lower)
        if count_match:
            word = count_match.group(1)
            storage_count = WORD_TO_NUM.get(word, int(word) if word.isdigit() else 2)
        else:
            storage_count = 2

    # 6. Extract Acoustic Accessories
    acc_count = 0
    if "acoustic" in text_lower or "accessories" in text_lower or "writable" in text_lower:
        count_match = re.search(r"(\w+)\s+(?:acoustic\s+)?accessories", text_lower)
        if count_match:
            word = count_match.group(1)
            acc_count = WORD_TO_NUM.get(word, int(word) if word.isdigit() else 4)
        else:
            acc_count = 4

    # 7. Constraint Flags
    preserve_daylight = "daylight" in text_lower or "windows" in text_lower
    prioritize_egress = "egress" in text_lower or "circulation" in text_lower

    return BriefIntent(
        target_capacity=cap,
        typology=typology,
        preferred_finishes=tuple(found_finishes),
        collaboration_tables=collab_count,
        storage_units=storage_count,
        acoustic_accessories=acc_count,
        preserve_daylight=preserve_daylight,
        prioritize_egress=prioritize_egress,
    )
