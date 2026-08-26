from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def dump_json_str(value: Any) -> str:
    """Serializes data to a deterministic JSON string.
    
    Guarantees:
    - Sorted keys (determinism across Python dict ordering)
    - 2-space indentation
    - Trailing newline
    - UTF-8 compatible ASCII/Unicode handling
    """
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_deterministic_json(path: str | Path, value: Any) -> None:
    """Writes deterministic JSON to disk, ensuring parent directories exist."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(dump_json_str(value), encoding="utf-8")
