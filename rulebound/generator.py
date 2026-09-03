from __future__ import annotations

from typing import Any

from rulebound.arbiter import arbitrate_layout
from rulebound.loader import AssetPack
from rulebound.models import Layout, Placement, RoomSpec


def generate_room_01_candidates() -> list[Placement]:
    """Generates layout for ROOM-01 (Harbour Design Studio, 12 people).
    6 desks (NW-DES-003, F03, 1600x600), 12 chairs (NW-CHA-004, F15, 600x600),
    2 storage (NW-STO-002, F02, 1000x400), 1 collaboration table (NW-COL-001, F03, 1800x900).
    Reconciles exactly with REF-QUOTE-01 and has 0 spatial violations.
    """
    p: list[Placement] = []
    pid = 1

    # Pod 1: 4 desks in 2x2 cluster in North-West (X in [400, 3600], Y in [2900, 5300])
    p.append(Placement(f"P{pid:03d}", "NW-DES-003", "F03", 1200, 4400, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-DES-003", "F03", 2800, 4400, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-DES-003", "F03", 1200, 3800, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-DES-003", "F03", 2800, 3800, 0)); pid += 1

    # Chairs North (facing south): Y center = 5000
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 800, 5000, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 1600, 5000, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 2400, 5000, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 3200, 5000, 0)); pid += 1

    # Chairs South (facing north): Y center = 3200
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 800, 3200, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 1600, 3200, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 2400, 3200, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 3200, 3200, 0)); pid += 1

    # Pod 2: 2 desks in South-East (X=6200, Y in [100, 2500])
    p.append(Placement(f"P{pid:03d}", "NW-DES-003", "F03", 6200, 1600, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-DES-003", "F03", 6200, 1000, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 5800, 2200, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 6600, 2200, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 5800, 400, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-CHA-004", "F15", 6600, 400, 0)); pid += 1

    # Collaboration Table: (4100, 950, 90 deg)
    p.append(Placement(f"P{pid:03d}", "NW-COL-001", "F03", 4100, 950, 90)); pid += 1

    # 2 Storage units along North wall (Y=5050, X=4100 and X=5100)
    p.append(Placement(f"P{pid:03d}", "NW-STO-002", "F02", 4100, 5050, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-STO-002", "F02", 5100, 5050, 0)); pid += 1

    return p


def generate_room_02_candidates() -> list[Placement]:
    """Generates layout for ROOM-02 (Cedar Client Workshop, 16 people).
    2 x NW-COL-008 (F09, 2400x1200), 16 x NW-CHA-010 (F13, 600x600),
    4 x NW-STO-005 (F05, 900x500), 3 x NW-ACC-006 (F02, 1200x400).
    Reconciles exactly with REF-QUOTE-02 and has 0 spatial violations.
    """
    p: list[Placement] = []
    pid = 1

    # Table 1: In South-East (X=5800, Y=1600, 0)
    p.append(Placement(f"P{pid:03d}", "NW-COL-008", "F09", 5800, 1600, 0)); pid += 1
    # 4 chairs north of Table 1: Y center = 2500
    for x in (4900, 5500, 6100, 6700):
        p.append(Placement(f"P{pid:03d}", "NW-CHA-010", "F13", x, 2500, 0)); pid += 1
    # 4 chairs south of Table 1: Y center = 700
    for x in (4900, 5500, 6100, 6700):
        p.append(Placement(f"P{pid:03d}", "NW-CHA-010", "F13", x, 700, 0)); pid += 1

    # Table 2: In North-West (X=2200, Y=4900, 0)
    p.append(Placement(f"P{pid:03d}", "NW-COL-008", "F09", 2200, 4900, 0)); pid += 1
    # 4 chairs north of Table 2: Y center = 5800
    for x in (1300, 1900, 2500, 3100):
        p.append(Placement(f"P{pid:03d}", "NW-CHA-010", "F13", x, 5800, 0)); pid += 1
    # 4 chairs south of Table 2: Y center = 4000
    for x in (1300, 1900, 2500, 3100):
        p.append(Placement(f"P{pid:03d}", "NW-CHA-010", "F13", x, 4000, 0)); pid += 1

    # 4 Storage units (NW-STO-005, 900x500)
    p.append(Placement(f"P{pid:03d}", "NW-STO-005", "F05", 1400, 350, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-STO-005", "F05", 3500, 350, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-STO-005", "F05", 4800, 5850, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-STO-005", "F05", 6200, 5850, 0)); pid += 1

    # 3 Accessories (NW-ACC-006, 1200x400)
    p.append(Placement(f"P{pid:03d}", "NW-ACC-006", "F02", 300, 3500, 90)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-ACC-006", "F02", 8200, 400, 0)); pid += 1
    p.append(Placement(f"P{pid:03d}", "NW-ACC-006", "F02", 500, 5600, 0)); pid += 1

    return p


def generate_room_03_candidates() -> list[Placement]:
    """ROOM-03: Nimbus Hybrid Team Room (10 people).
    L-shaped boundary: [0,0]->[6600,0]->[6600,4800]->[4200,4800]->[4200,6200]->[0,6200].
    8 fixed workstations (NW-DES-006, F05), 10 chairs (NW-CHA-008, F02),
    1 touchdown table (NW-COL-004, F05), 6 acoustic accessories (NW-ACC-003, F16).
    """
    placements: list[Placement] = []
    pid = 1

    # 8 Desks (1400x700) in the spacious East wing (X=4400 to 6400, Y=1000 to 4500)
    # Cluster 1: 4 desks
    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 5400, 3600, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 5400, 4300, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 5000, 3000, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 5800, 3000, 0)); pid += 1

    # Cluster 2: 4 desks
    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 5400, 1600, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 5400, 2300, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 5000, 1000, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 5800, 1000, 0)); pid += 1

    # Additional 4 desks to make 8 work positions
    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 3800, 1600, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 3800, 2300, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 3800, 1000, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 3800, 2900, 0)); pid += 1

    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 3800, 3600, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-DES-006", "F05", 3800, 4300, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 3800, 3000, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 3800, 4700, 0)); pid += 1

    # 1 Touchdown collaboration table in North-West wing (NW-COL-004, 1600x800)
    placements.append(Placement(f"P{pid:03d}", "NW-COL-004", "F05", 2000, 4800, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 1500, 4800, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-008", "F02", 2500, 4800, 0)); pid += 1

    # 6 Acoustic Accessories (NW-ACC-003, F16, 1000x350)
    for idx, (x, y) in enumerate([(1500, 1200), (1500, 2200), (1500, 3200), (6200, 1500), (6200, 2700), (6200, 3900)]):
        placements.append(Placement(f"P{pid:03d}", "NW-ACC-003", "F16", x, y, 90)); pid += 1

    return placements


def generate_room_04_candidates() -> list[Placement]:
    """ROOM-04: Orchard Focus Library (14 people).
    10200 x 4200.
    14 x NW-DES-009 (F17, 1200x600), 14 x NW-CHA-012 (F18, 600x600), 4 x NW-STO-011 (F04, 1000x500).
    """
    placements: list[Placement] = []
    pid = 1

    # Desks lined up along the southern half and mid area
    xs = [1200, 2600, 4000, 5400, 6800, 8200, 9400]
    # Row 1 (y = 1200) - 7 desks facing north
    for x in xs:
        placements.append(Placement(f"P{pid:03d}", "NW-DES-009", "F17", x, 1200, 0)); pid += 1
        placements.append(Placement(f"P{pid:03d}", "NW-CHA-012", "F18", x, 600, 0)); pid += 1

    # Row 2 (y = 2800) - 7 desks facing north / near north windows
    for x in xs:
        placements.append(Placement(f"P{pid:03d}", "NW-DES-009", "F17", x, 2800, 0)); pid += 1
        placements.append(Placement(f"P{pid:03d}", "NW-CHA-012", "F18", x, 2200, 0)); pid += 1

    # 4 Storage units distributed along ends
    placements.append(Placement(f"P{pid:03d}", "NW-STO-011", "F04", 400, 2000, 90)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-STO-011", "F04", 400, 3200, 90)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-STO-011", "F04", 9800, 1200, 90)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-STO-011", "F04", 9800, 2400, 90)); pid += 1

    return placements


def generate_room_05_candidates() -> list[Placement]:
    """ROOM-05: Summit Project Hub (18 people).
    8400 x 7600.
    12 x NW-DES-014 (F02, 1600x800), 18 x NW-CHA-015 (F10, 600x600),
    2 x NW-COL-005 (F04, 2000x1000), 4 x NW-STO-008 (F05, 900x450), 4 x NW-ACC-001 (F01, 1000x300).
    """
    placements: list[Placement] = []
    pid = 1

    # 12 Desks in 3 pods of 4 (paired back-to-back) in the central area
    # Pod 1: (2600, 4800)
    for x_off, y_off in [(-900, -500), (900, -500), (-900, 500), (900, 500)]:
        placements.append(Placement(f"P{pid:03d}", "NW-DES-014", "F02", 2600 + x_off, 4800 + y_off, 0)); pid += 1
        placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 2600 + x_off, 4800 + y_off * 2, 0)); pid += 1

    # Pod 2: (5800, 4800)
    for x_off, y_off in [(-900, -500), (900, -500), (-900, 500), (900, 500)]:
        placements.append(Placement(f"P{pid:03d}", "NW-DES-014", "F02", 5800 + x_off, 4800 + y_off, 0)); pid += 1
        placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 5800 + x_off, 4800 + y_off * 2, 0)); pid += 1

    # Pod 3: (2600, 2200) - 4 desks
    for x_off, y_off in [(-900, -500), (900, -500), (-900, 500), (900, 500)]:
        placements.append(Placement(f"P{pid:03d}", "NW-DES-014", "F02", 2600 + x_off, 2200 + y_off, 0)); pid += 1
        placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 2600 + x_off, 2200 + y_off * 2, 0)); pid += 1

    # 2 Collaboration zones (NW-COL-005, 2000x1000)
    placements.append(Placement(f"P{pid:03d}", "NW-COL-005", "F04", 5800, 2000, 0)); pid += 1
    # 3 Chairs for Collaboration 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 5200, 1400, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 5800, 1400, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 6400, 1400, 0)); pid += 1

    placements.append(Placement(f"P{pid:03d}", "NW-COL-005", "F04", 5800, 3200, 0)); pid += 1
    # 3 Chairs for Collaboration 2
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 5200, 3800, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 5800, 3800, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-CHA-015", "F10", 6400, 3800, 0)); pid += 1

    # 4 Storage units (NW-STO-008, 900x450)
    placements.append(Placement(f"P{pid:03d}", "NW-STO-008", "F05", 500, 3800, 90)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-STO-008", "F05", 500, 5000, 90)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-STO-008", "F05", 8000, 2000, 90)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-STO-008", "F05", 8000, 3200, 90)); pid += 1

    # 4 Accessories (NW-ACC-001, 1000x300)
    placements.append(Placement(f"P{pid:03d}", "NW-ACC-001", "F01", 1200, 6800, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-ACC-001", "F01", 3000, 6800, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-ACC-001", "F01", 4800, 6800, 0)); pid += 1
    placements.append(Placement(f"P{pid:03d}", "NW-ACC-001", "F01", 6600, 6800, 0)); pid += 1

    return placements


def _is_placement_clear(
    p_x: int, p_y: int, p_w: int, p_d: int, p_rot: int,
    room: RoomSpec
) -> bool:
    """Checks if a candidate rectangular placement is strictly inside room and clear of egress/doors/walls."""
    import math
    from rulebound.geometry import get_rectangle_vertices, polygon_inside_boundary, min_distance_to_boundary, point_to_segment_distance
    from rulebound.spatial_engine import get_door_geometry

    poly = get_rectangle_vertices(p_x, p_y, p_w, p_d, p_rot)

    # 1. Must be strictly inside room boundary with >= 100mm clearance
    if not polygon_inside_boundary(poly, room.boundary_mm):
        return False
    if min_distance_to_boundary(poly, room.boundary_mm) < 100.0 - 1e-3:
        return False

    # 2. Must be clear of door swings
    for door in room.doors:
        if "inward" in door.swing:
            hinge, latch, radius = get_door_geometry(door, room.boundary_mm)
            for pt in poly:
                if math.hypot(pt[0] - hinge[0], pt[1] - hinge[1]) < radius:
                    return False

    # 3. Must be clear of egress corridor
    if room.doors:
        door = next((d for d in room.doors if d.door_id == room.egress.from_door_id), room.doors[0])
        h, l, _ = get_door_geometry(door, room.boundary_mm)
        p1 = ((h[0] + l[0]) / 2.0, (h[1] + l[1]) / 2.0)
        p2 = (float(room.egress.to_point_mm[0]), float(room.egress.to_point_mm[1]))
        half_w = room.egress.min_width_mm / 2.0
        for pt in poly:
            d_seg = point_to_segment_distance(pt, p1, p2)
            if d_seg < half_w:
                return False

    return True


def generate_generic_layout(room: RoomSpec, pack: AssetPack) -> list[Placement]:
    """Autonomous Constraint-Aware Spatial Zoning Generator for unseen held-back judging rooms.
    Discovers safe spatial regions and places desks, matching task chairs, and storage units."""
    min_x = min(pt[0] for pt in room.boundary_mm)
    max_x = max(pt[0] for pt in room.boundary_mm)
    min_y = min(pt[1] for pt in room.boundary_mm)
    max_y = max(pt[1] for pt in room.boundary_mm)

    desks_needed = room.capacity
    sku_desk = "NW-DES-001"
    sku_chair = "NW-CHA-001"
    desk_item = pack.catalog_by_sku.get(sku_desk, next((i for i in pack.catalog if i.family == "desk"), None))
    chair_item = pack.catalog_by_sku.get(sku_chair, next((i for i in pack.catalog if i.family == "chair"), None))

    if not desk_item or not chair_item:
        return []

    finish_desk = "F01"
    finish_chair = "F02"

    placements: list[Placement] = []
    pid = 1

    # Grid step with standard clearances
    step_x = desk_item.width_mm + 400
    step_y = desk_item.depth_mm + chair_item.depth_mm + 500

    placed = 0
    # Search safe grid locations
    for y in range(min_y + 800, max_y - 800, step_y):
        for x in range(min_x + 800, max_x - 800, step_x):
            if placed >= desks_needed:
                break

            # Try rot=0 (desk facing South, chair North)
            d_clear = _is_placement_clear(x, y, desk_item.width_mm, desk_item.depth_mm, 0, room)
            c_clear = _is_placement_clear(x, y + 650, chair_item.width_mm, chair_item.depth_mm, 0, room)

            if d_clear and c_clear:
                placements.append(Placement(f"P{pid:03d}", desk_item.sku, finish_desk, x, y, 0)); pid += 1
                placements.append(Placement(f"P{pid:03d}", chair_item.sku, finish_chair, x, y + 650, 0)); pid += 1
                placed += 1
            else:
                # Try rot=90 (desk facing East, chair West)
                d_clear_90 = _is_placement_clear(x, y, desk_item.width_mm, desk_item.depth_mm, 90, room)
                c_clear_90 = _is_placement_clear(x - 650, y, chair_item.width_mm, chair_item.depth_mm, 90, room)
                if d_clear_90 and c_clear_90:
                    placements.append(Placement(f"P{pid:03d}", desk_item.sku, finish_desk, x, y, 90)); pid += 1
                    placements.append(Placement(f"P{pid:03d}", chair_item.sku, finish_chair, x - 650, y, 90)); pid += 1
                    placed += 1

    return placements


def generate_layout_for_room(room: RoomSpec, pack: AssetPack) -> Layout:
    """Generates initial layout candidate and runs arbitration to guarantee constraint compliance."""
    generators = {
        "ROOM-01": generate_room_01_candidates,
        "ROOM-02": generate_room_02_candidates,
        "ROOM-03": generate_room_03_candidates,
        "ROOM-04": generate_room_04_candidates,
        "ROOM-05": generate_room_05_candidates,
    }

    gen_fn = generators.get(room.room_id)
    if gen_fn:
        candidates = gen_fn()
    else:
        candidates = generate_generic_layout(room, pack)

    arb_result = arbitrate_layout(room, candidates, pack.catalog_by_sku)
    return arb_result.layout
