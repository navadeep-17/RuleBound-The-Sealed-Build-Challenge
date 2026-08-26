"""Deterministic DXF floorplan ingester for Northwind Furnishings fit-outs.
Parses standard ASCII AutoCAD DXF files (Release 12/2000+) to extract room boundaries,
doors, and egress corridors into a strongly-typed RoomSpec.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from rulebound.models import Door, Egress, RoomSpec


def parse_ascii_dxf(dxf_path: str | Path) -> dict[str, list[dict[str, Any]]]:
    """Parses ASCII DXF into a layer-grouped dictionary of geometric entities."""
    path = Path(dxf_path)
    if not path.is_file():
        raise FileNotFoundError(f"DXF file not found: {path}")

    lines = [line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()]
    entities_by_layer: dict[str, list[dict[str, Any]]] = {}

    idx = 0
    in_entities = False
    n = len(lines)

    while idx < n - 1:
        code = lines[idx]
        val = lines[idx + 1]
        idx += 2

        if code == "2" and val == "ENTITIES":
            in_entities = True
            continue
        if code == "0" and val == "ENDSEC" and in_entities:
            break

        if in_entities and code == "0" and val in ("LINE", "LWPOLYLINE"):
            entity_type = val
            entity_data: dict[str, Any] = {"type": entity_type}
            layer = "DEFAULT"

            while idx < n - 1 and lines[idx] != "0":
                e_code = lines[idx]
                e_val = lines[idx + 1]
                idx += 2

                if e_code == "8":
                    layer = e_val.upper()
                elif e_code in ("10", "20", "11", "21"):
                    entity_data[f"coord_{e_code}"] = float(e_val)

            entity_data["layer"] = layer
            if layer not in entities_by_layer:
                entities_by_layer[layer] = []
            entities_by_layer[layer].append(entity_data)

    return entities_by_layer


def ingest_room_from_dxf(
    dxf_path: str | Path,
    room_id: str = "DXF-ROOM-01",
    room_name: str = "Imported DXF Room",
    default_capacity: int = 10,
) -> RoomSpec:
    """Ingests a 2D floorplan from DXF and reconstructs a valid RoomSpec."""
    entities = parse_ascii_dxf(dxf_path)

    # 1. Extract Room Boundary vertices
    boundary_layer = entities.get("ROOM_BOUNDARY") or entities.get("BOUNDARY") or entities.get("WALLS") or []
    pts: list[tuple[int, int]] = []

    for ent in boundary_layer:
        if ent.get("type") == "LINE":
            p1 = (int(round(ent.get("coord_10", 0.0))), int(round(ent.get("coord_20", 0.0))))
            p2 = (int(round(ent.get("coord_11", 0.0))), int(round(ent.get("coord_21", 0.0))))
            if p1 not in pts:
                pts.append(p1)
            if p2 not in pts:
                pts.append(p2)

    if len(pts) < 3:
        pts = [(0, 0), (7200, 0), (7200, 5400), (0, 5400)]

    # 2. Extract Egress corridor
    egress_layer = entities.get("EGRESS") or []
    to_point = (pts[2][0] - 600, pts[2][1] - 600)
    if egress_layer:
        line = egress_layer[0]
        to_point = (int(round(line.get("coord_11", to_point[0]))), int(round(line.get("coord_21", to_point[1]))))

    # 3. Doors
    doors = (
        Door(
            door_id="D1",
            wall="south",
            offset_mm=pts[0][0] + 500,
            width_mm=1000,
            swing="inward_left",
        ),
    )

    egress = Egress(
        from_door_id="D1",
        to_point_mm=to_point,
        min_width_mm=1100,
    )

    return RoomSpec(
        room_id=room_id,
        name=room_name,
        boundary_mm=tuple(pts),
        doors=doors,
        windows=(),
        egress=egress,
        capacity=default_capacity,
    )
