from __future__ import annotations

from pathlib import Path
from typing import Sequence

from rulebound.geometry import get_rectangle_vertices
from rulebound.models import CatalogItem, Layout, RoomSpec


def export_layout_to_dxf(
    room: RoomSpec,
    layout: Layout,
    catalog_by_sku: dict[str, CatalogItem],
    output_path: str | Path,
) -> None:
    """Exports a 2D floorplan to a standard ASCII AutoCAD DXF (Release 12/2000 compatible).
    
    Generates layers:
    - ROOM_BOUNDARY (Color 4: Cyan)
    - DOORS_SWING (Color 2: Yellow)
    - EGRESS (Color 6: Magenta)
    - FURNITURE (Color 3: Green)
    - LABELS (Color 7: White)
    """
    lines: list[str] = [
        "0", "SECTION",
        "2", "HEADER",
        "9", "$ACADVER",
        "1", "AC1009",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "TABLES",
        "0", "TABLE",
        "2", "LAYER",
        "70", "5",
        # Layer 1: ROOM_BOUNDARY
        "0", "LAYER",
        "2", "ROOM_BOUNDARY",
        "70", "0",
        "62", "4",  # Cyan
        "6", "CONTINUOUS",
        # Layer 2: DOORS_SWING
        "0", "LAYER",
        "2", "DOORS_SWING",
        "70", "0",
        "62", "2",  # Yellow
        "6", "CONTINUOUS",
        # Layer 3: EGRESS
        "0", "LAYER",
        "2", "EGRESS",
        "70", "0",
        "62", "6",  # Magenta
        "6", "DASHED",
        # Layer 4: FURNITURE
        "0", "LAYER",
        "2", "FURNITURE",
        "70", "0",
        "62", "3",  # Green
        "6", "CONTINUOUS",
        # Layer 5: LABELS
        "0", "LAYER",
        "2", "LABELS",
        "70", "0",
        "62", "7",  # White
        "6", "CONTINUOUS",
        "0", "ENDTAB",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "ENTITIES",
    ]

    # 1. Room boundary polygon
    b_pts = list(room.boundary_mm)
    n_b = len(b_pts)
    for i in range(n_b):
        p1 = b_pts[i]
        p2 = b_pts[(i + 1) % n_b]
        lines.extend([
            "0", "LINE",
            "8", "ROOM_BOUNDARY",
            "10", str(float(p1[0])),
            "20", str(float(p1[1])),
            "30", "0.0",
            "11", str(float(p2[0])),
            "21", str(float(p2[1])),
            "31", "0.0",
        ])

    # 2. Egress line
    egress_start = (float(room.boundary_mm[0][0]), float(room.boundary_mm[0][1]))
    if room.doors:
        off = room.doors[0].offset_mm
        w = room.doors[0].width_mm
        egress_start = (float(off + w / 2), 0.0)

    lines.extend([
        "0", "LINE",
        "8", "EGRESS",
        "10", str(egress_start[0]),
        "20", str(egress_start[1]),
        "30", "0.0",
        "11", str(float(room.egress.to_point_mm[0])),
        "21", str(float(room.egress.to_point_mm[1])),
        "31", "0.0",
    ])

    # 3. Furniture placements
    for p in layout.placements:
        item = catalog_by_sku.get(p.sku)
        if not item:
            continue
        poly = get_rectangle_vertices(
            center_x=float(p.x_mm),
            center_y=float(p.y_mm),
            width=float(item.width_mm),
            depth=float(item.depth_mm),
            rotation_deg=float(p.rotation_deg),
        )
        for i in range(4):
            v1 = poly[i]
            v2 = poly[(i + 1) % 4]
            lines.extend([
                "0", "LINE",
                "8", "FURNITURE",
                "10", str(v1[0]),
                "20", str(v1[1]),
                "30", "0.0",
                "11", str(v2[0]),
                "21", str(v2[1]),
                "31", "0.0",
            ])

        # Text label inside furniture
        lines.extend([
            "0", "TEXT",
            "8", "LABELS",
            "10", str(float(p.x_mm) - 200.0),
            "20", str(float(p.y_mm)),
            "30", "0.0",
            "40", "120.0",  # Text height in mm
            "1", f"{p.placement_id}: {p.sku}",
        ])

    lines.extend([
        "0", "ENDSEC",
        "0", "EOF",
    ])

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
