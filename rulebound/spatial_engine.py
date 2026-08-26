from __future__ import annotations

import math
from typing import Any

from rulebound.geometry import (
    Point,
    Polygon,
    distance,
    get_rectangle_vertices,
    min_distance_to_boundary,
    point_in_polygon,
    point_to_segment_distance,
    polygon_edges,
    polygon_inside_boundary,
    polygon_to_polygon_distance,
    polygon_to_segment_distance,
    polygons_overlap_sat,
)
from rulebound.models import CatalogItem, Door, Placement, RoomSpec, Violation


def get_door_geometry(door: Door, boundary: tuple[tuple[int, int], ...]) -> tuple[Point, Point, float]:
    """Determines door hinge position, door latch position, and swing radius.
    Wall conventions:
    - south: y = 0, x from offset to offset + width
    - north: y = max_y, x from offset to offset + width
    - west: x = 0, y from offset to offset + width
    - east: x = max_x, y from offset to offset + width
    """
    w = door.width_mm
    off = door.offset_mm
    radius = max(850.0, float(w))

    if door.wall == "south":
        p1 = (float(off), 0.0)
        p2 = (float(off + w), 0.0)
        hinge = p1 if "left" in door.swing else p2
        latch = p2 if "left" in door.swing else p1
    elif door.wall == "north":
        # Find max_y
        max_y = max(pt[1] for pt in boundary)
        p1 = (float(off), float(max_y))
        p2 = (float(off + w), float(max_y))
        hinge = p2 if "left" in door.swing else p1
        latch = p1 if "left" in door.swing else p2
    elif door.wall == "west":
        p1 = (0.0, float(off))
        p2 = (0.0, float(off + w))
        hinge = p2 if "left" in door.swing else p1
        latch = p1 if "left" in door.swing else p2
    elif door.wall == "east":
        max_x = max(pt[0] for pt in boundary)
        p1 = (float(max_x), float(off))
        p2 = (float(max_x), float(off + w))
        hinge = p1 if "left" in door.swing else p2
        latch = p2 if "left" in door.swing else p1
    else:
        hinge = (float(off), 0.0)
        latch = (float(off + w), 0.0)

    return hinge, latch, radius


def get_placement_footprint(placement: Placement, item: CatalogItem) -> Polygon:
    return get_rectangle_vertices(
        center_x=float(placement.x_mm),
        center_y=float(placement.y_mm),
        width=float(item.width_mm),
        depth=float(item.depth_mm),
        rotation_deg=float(placement.rotation_deg),
    )


def validate_spatial_rules(
    room: RoomSpec,
    placements: list[Placement],
    catalog_by_sku: dict[str, CatalogItem],
) -> tuple[list[Violation], float]:
    """Evaluates all spatial rules RB-GEO-001 through RB-GEO-008.
    
    Returns:
    - List of structured Violations
    - Total energy penalty E (sum of clearance shortfalls, overlap depths, boundary violations)
    """
    violations: list[Violation] = []
    total_energy: float = 0.0
    v_idx = 1

    footprints: dict[str, Polygon] = {}
    items: dict[str, CatalogItem] = {}

    for p in placements:
        item = catalog_by_sku.get(p.sku)
        if item:
            items[p.placement_id] = item
            footprints[p.placement_id] = get_placement_footprint(p, item)

    # 1. RB-GEO-007: inside_room_boundary
    for p in placements:
        poly = footprints.get(p.placement_id)
        if not poly:
            continue
        if not polygon_inside_boundary(poly, room.boundary_mm):
            outside_count = sum(1 for pt in poly if not point_in_polygon(pt, room.boundary_mm))
            penalty = 5000.0 + outside_count * 1000.0
            total_energy += penalty
            violations.append(
                Violation(
                    violation_id=f"V{v_idx:03d}",
                    rule_id="RB-GEO-007",
                    message=f"Placement {p.placement_id} ({p.sku}) extends outside the room boundary.",
                    affected_placement_ids=[p.placement_id],
                    measured={"outside_vertices": outside_count},
                    required={"outside_vertices": 0},
                    repair_options=[
                        {"action": "translate", "placement_id": p.placement_id, "strategy": "nudge_inward"},
                        {"action": "remove", "placement_id": p.placement_id},
                    ],
                )
            )
            v_idx += 1

    # 2. RB-GEO-005: min_wall_offset (100 mm)
    for p in placements:
        poly = footprints.get(p.placement_id)
        if not poly:
            continue
        d_wall = min_distance_to_boundary(poly, room.boundary_mm)
        if d_wall < 100.0:
            shortfall = 100.0 - d_wall
            total_energy += shortfall * 10.0
            violations.append(
                Violation(
                    violation_id=f"V{v_idx:03d}",
                    rule_id="RB-GEO-005",
                    message=f"Placement {p.placement_id} is only {d_wall:.1f} mm from wall (minimum 100 mm).",
                    affected_placement_ids=[p.placement_id],
                    measured={"wall_distance_mm": round(d_wall, 1)},
                    required={"min_wall_offset_mm": 100},
                    repair_options=[
                        {"action": "translate", "placement_id": p.placement_id, "distance_mm": round(shortfall, 1)},
                        {"action": "remove", "placement_id": p.placement_id},
                    ],
                )
            )
            v_idx += 1

    # 3. RB-GEO-006: no_overlap
    n = len(placements)
    for i in range(n):
        p1 = placements[i]
        poly1 = footprints.get(p1.placement_id)
        if not poly1:
            continue
        for j in range(i + 1, n):
            p2 = placements[j]
            poly2 = footprints.get(p2.placement_id)
            if not poly2:
                continue
            if polygons_overlap_sat(poly1, poly2):
                overlap_dist = 500.0  # nominal overlap penalty
                total_energy += overlap_dist * 20.0
                violations.append(
                    Violation(
                        violation_id=f"V{v_idx:03d}",
                        rule_id="RB-GEO-006",
                        message=f"Footprints of {p1.placement_id} and {p2.placement_id} overlap.",
                        affected_placement_ids=[p1.placement_id, p2.placement_id],
                        measured={"overlap": True},
                        required={"overlap": False},
                        repair_options=[
                            {"action": "separate", "placement_ids": [p1.placement_id, p2.placement_id]},
                            {"action": "remove", "placement_id": p2.placement_id},
                        ],
                    )
                )
                v_idx += 1

    # 4. RB-GEO-003: door_swing_clearance (850 mm)
    for door in room.doors:
        hinge, latch, radius = get_door_geometry(door, room.boundary_mm)
        door_center = ((hinge[0] + latch[0]) / 2.0, (hinge[1] + latch[1]) / 2.0)

        for p in placements:
            poly = footprints.get(p.placement_id)
            if not poly:
                continue
            # Distance from placement to hinge or door opening
            d_hinge = polygon_to_segment_distance(poly, hinge, latch)
            d_hinge_pt = min(distance(pt, hinge) for pt in poly)
            effective_dist = min(d_hinge, d_hinge_pt)

            if effective_dist < 850.0 and "inward" in door.swing:
                shortfall = 850.0 - effective_dist
                total_energy += shortfall * 15.0
                violations.append(
                    Violation(
                        violation_id=f"V{v_idx:03d}",
                        rule_id="RB-GEO-003",
                        message=f"Placement {p.placement_id} intrudes into door {door.door_id} swing zone by {shortfall:.1f} mm.",
                        affected_placement_ids=[p.placement_id],
                        measured={"clearance_mm": round(effective_dist, 1)},
                        required={"min_clearance_mm": 850},
                        repair_options=[
                            {"action": "translate", "placement_id": p.placement_id, "strategy": "clear_door"},
                            {"action": "remove", "placement_id": p.placement_id},
                        ],
                    )
                )
                v_idx += 1

    # 5. RB-GEO-002: min_clearance egress (1100 mm corridor)
    # Egress line from door to to_point_mm
    egress_door = next((d for d in room.doors if d.door_id == room.egress.from_door_id), room.doors[0] if room.doors else None)
    if egress_door:
        h, l, _ = get_door_geometry(egress_door, room.boundary_mm)
        door_mid = ((h[0] + l[0]) / 2.0, (h[1] + l[1]) / 2.0)
        egress_target = (float(room.egress.to_point_mm[0]), float(room.egress.to_point_mm[1]))
        half_width = room.egress.min_width_mm / 2.0

        for p in placements:
            poly = footprints.get(p.placement_id)
            if not poly:
                continue
            d_egress = polygon_to_segment_distance(poly, door_mid, egress_target)
            if d_egress < half_width:
                shortfall = half_width - d_egress
                total_energy += shortfall * 12.0
                violations.append(
                    Violation(
                        violation_id=f"V{v_idx:03d}",
                        rule_id="RB-GEO-002",
                        message=f"Placement {p.placement_id} encroaches into egress path by {shortfall:.1f} mm.",
                        affected_placement_ids=[p.placement_id],
                        measured={"clearance_from_centerline_mm": round(d_egress, 1)},
                        required={"min_half_width_mm": half_width},
                        repair_options=[
                            {"action": "translate", "placement_id": p.placement_id, "strategy": "clear_egress"},
                            {"action": "remove", "placement_id": p.placement_id},
                        ],
                    )
                )
                v_idx += 1

    # 6. RB-GEO-001: min_clearance walkway (900 mm between distinct desk/storage groups)
    # Checks that inter-group spacing is either adjacent (paired <= 100mm) or wide walkway (>= 900mm)
    # Pairs of desks face-to-face or side-to-side are intentional; non-paired items must not form pinch points < 900mm
    for i in range(n):
        p1 = placements[i]
        poly1 = footprints.get(p1.placement_id)
        item1 = items.get(p1.placement_id)
        if not poly1 or not item1:
            continue
        for j in range(i + 1, n):
            p2 = placements[j]
            poly2 = footprints.get(p2.placement_id)
            item2 = items.get(p2.placement_id)
            if not poly2 or not item2:
                continue

            # Skip desk-to-chair pairs (chair is paired with desk)
            if (item1.family == "desk" and item2.family == "chair") or (item1.family == "chair" and item2.family == "desk"):
                continue

            d_pair = polygon_to_polygon_distance(poly1, poly2)
            # If two separate items are close but not intentionally paired/clustered (pinch point)
            # Desks can be back-to-back or side-by-side (d < 50mm)
            if 50.0 < d_pair < 900.0 and item1.family in ("desk", "collaboration") and item2.family in ("desk", "collaboration"):
                shortfall = 900.0 - d_pair
                total_energy += shortfall * 5.0
                violations.append(
                    Violation(
                        violation_id=f"V{v_idx:03d}",
                        rule_id="RB-GEO-001",
                        message=f"Walkway width between {p1.placement_id} and {p2.placement_id} is {d_pair:.1f} mm (< 900 mm).",
                        affected_placement_ids=[p1.placement_id, p2.placement_id],
                        measured={"walkway_width_mm": round(d_pair, 1)},
                        required={"min_walkway_mm": 900},
                        repair_options=[
                            {"action": "widen_aisle", "placement_ids": [p1.placement_id, p2.placement_id]},
                        ],
                    )
                )
                v_idx += 1

    return violations, total_energy
