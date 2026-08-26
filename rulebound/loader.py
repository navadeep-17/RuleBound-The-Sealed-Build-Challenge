from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rulebound.models import CatalogItem, Finish, RoomSpec


@dataclass(frozen=True)
class AssetPack:
    catalog: list[CatalogItem]
    catalog_by_sku: dict[str, CatalogItem]
    finishes: list[Finish]
    finishes_by_id: dict[str, Finish]
    rules: dict[str, Any]
    rooms: list[RoomSpec]
    rooms_by_id: dict[str, RoomSpec]
    briefs: dict[str, str]
    historical_jobs: list[dict[str, Any]]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_asset_pack(input_dir: str | Path) -> AssetPack:
    root = Path(input_dir)
    raw_catalog = read_json(root / "catalog.json")
    catalog = [CatalogItem.from_dict(item) for item in raw_catalog]
    catalog_by_sku = {item.sku: item for item in catalog}

    raw_finishes = read_json(root / "finishes.json")
    finishes = [Finish.from_dict(f) for f in raw_finishes]
    finishes_by_id = {f.finish_id: f for f in finishes}

    rules = read_json(root / "rules.json")

    rooms_dir = root / "rooms"
    room_files = sorted(rooms_dir.glob("*.json"))
    rooms = [RoomSpec.from_dict(read_json(p)) for p in room_files]
    rooms_by_id = {r.room_id: r for r in rooms}

    briefs_dir = root / "briefs"
    briefs: dict[str, str] = {}
    if briefs_dir.exists():
        for path in sorted(briefs_dir.glob("*.txt")):
            briefs[path.stem] = path.read_text(encoding="utf-8").strip()

    historical_jobs: list[dict[str, Any]] = []
    hist_file = root / "historical_jobs.json"
    if hist_file.exists():
        historical_jobs = read_json(hist_file)

    return AssetPack(
        catalog=catalog,
        catalog_by_sku=catalog_by_sku,
        finishes=finishes,
        finishes_by_id=finishes_by_id,
        rules=rules,
        rooms=rooms,
        rooms_by_id=rooms_by_id,
        briefs=briefs,
        historical_jobs=historical_jobs,
    )
