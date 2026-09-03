import math
from dataclasses import dataclass
from typing import Any, Literal

from rulebound.models import CatalogItem, Layout, Placement, RoomSpec, Violation
from rulebound.spatial_engine import get_door_geometry, validate_spatial_rules


@dataclass
class ArbitrationResult:
    layout: Layout
    iterations_run: int
    initial_energy: float
    final_energy: float
    escalation_report: dict[str, Any] | None = None


def compute_relaxation_vectors(
    room: RoomSpec,
    target_v: Violation,
    placement: Placement,
    catalog_by_sku: dict[str, CatalogItem],
) -> list[tuple[int, int]]:
    """Calculates vector-directed physical relaxation nudges tailored to the specific geometric rule violation."""
    vectors: list[tuple[int, int]] = []
    rule_id = target_v.rule_id

    if rule_id == "RB-GEO-005":
        # Wall encroachment: push toward center of the room
        cx = sum(pt[0] for pt in room.boundary_mm) / len(room.boundary_mm)
        cy = sum(pt[1] for pt in room.boundary_mm) / len(room.boundary_mm)
        dx = cx - placement.x_mm
        dy = cy - placement.y_mm
        d = math.hypot(dx, dy)
        if d > 0:
            for step in (120, 200, 300):
                vectors.append((int(round(dx / d * step)), int(round(dy / d * step))))

    elif rule_id == "RB-GEO-002":
        # Egress corridor: push along the perpendicular normal away from the corridor
        egress_door = next((dr for dr in room.doors if dr.door_id == room.egress.from_door_id), room.doors[0] if room.doors else None)
        if egress_door:
            h, l, _ = get_door_geometry(egress_door, room.boundary_mm)
            p1 = ((h[0] + l[0]) / 2.0, (h[1] + l[1]) / 2.0)
            p2 = (float(room.egress.to_point_mm[0]), float(room.egress.to_point_mm[1]))
            seg_dx = p2[0] - p1[0]
            seg_dy = p2[1] - p1[1]
            seg_len = math.hypot(seg_dx, seg_dy)
            if seg_len > 0:
                nx = -seg_dy / seg_len
                ny = seg_dx / seg_len
                side = (placement.x_mm - p1[0]) * nx + (placement.y_mm - p1[1]) * ny
                sign = 1.0 if side >= 0 else -1.0
                for step in (150, 250, 400):
                    vectors.append((int(round(sign * nx * step)), int(round(sign * ny * step))))
                    vectors.append((int(round(-sign * nx * step)), int(round(-sign * ny * step))))

    elif rule_id == "RB-GEO-003":
        # Door swing: push radially outward from door hinge
        for door in room.doors:
            hinge, latch, _ = get_door_geometry(door, room.boundary_mm)
            dx = placement.x_mm - hinge[0]
            dy = placement.y_mm - hinge[1]
            d = math.hypot(dx, dy)
            if d > 0:
                for step in (150, 300, 450):
                    vectors.append((int(round(dx / d * step)), int(round(dy / d * step))))

    # Standard orthogonal and diagonal exploration vectors
    for dist in (100, 200, 300):
        vectors.extend([
            (dist, 0), (-dist, 0), (0, dist), (0, -dist),
            (dist, dist), (-dist, dist), (dist, -dist), (-dist, -dist),
        ])

    return vectors


def arbitrate_layout(
    room: RoomSpec,
    initial_placements: list[Placement],
    catalog_by_sku: dict[str, CatalogItem],
    max_iterations: int = 6,
) -> ArbitrationResult:
    """Bounded, provably terminating arbitration loop for spatial layout repair.
    
    Termination Proof:
    - State is defined by measure M_t = (N_t, E_t) where N_t is placement count and E_t is constraint energy.
    - On each pass, the arbiter first attempts continuous relaxation (nudging positions).
      If energy decreases by at least eps (E_{t+1} <= E_t - eps), the nudge is accepted.
    - If continuous nudges cannot decrease energy, the arbiter prunes the placement causing the largest conflict,
      strictly decrementing N_t (N_{t+1} = N_t - 1).
    - With N_t in [0, N_0] and hard iteration bound K_max = max_iterations, the loop is strictly well-founded
      and terminates in finite steps.
    """
    placements = [
        Placement(
            placement_id=p.placement_id,
            sku=p.sku,
            finish_id=p.finish_id,
            x_mm=p.x_mm,
            y_mm=p.y_mm,
            rotation_deg=p.rotation_deg,
        )
        for p in initial_placements
    ]

    initial_violations, initial_energy = validate_spatial_rules(room, placements, catalog_by_sku)
    if initial_energy == 0.0:
        layout = Layout(
            room_id=room.room_id,
            placements=placements,
            violations=[],
            status="valid",
        )
        return ArbitrationResult(layout, 0, 0.0, 0.0, None)

    current_violations = initial_violations
    current_energy = initial_energy
    iteration = 0
    eps = 1.0

    while iteration < max_iterations and current_energy > 0.0:
        iteration += 1
        best_nudge_energy = current_energy
        best_p_idx = -1
        best_new_x = 0
        best_new_y = 0

        # Phase A: Vector-Directed Continuous Relaxation on worst violation
        target_v = current_violations[0]
        candidate_ids = set(target_v.affected_placement_ids)

        for idx, p in enumerate(placements):
            if p.placement_id not in candidate_ids:
                continue

            vectors = compute_relaxation_vectors(room, target_v, p, catalog_by_sku)
            orig_x, orig_y = p.x_mm, p.y_mm
            for dx, dy in vectors:
                p.x_mm = orig_x + dx
                p.y_mm = orig_y + dy
                _, e_test = validate_spatial_rules(room, placements, catalog_by_sku)
                if e_test < best_nudge_energy - eps:
                    best_nudge_energy = e_test
                    best_p_idx = idx
                    best_new_x = p.x_mm
                    best_new_y = p.y_mm
                p.x_mm = orig_x
                p.y_mm = orig_y

        best_new_rot = None

        if best_p_idx >= 0 and best_nudge_energy < current_energy - eps:
            # Accept continuous relaxation step (strictly decreasing energy E)
            placements[best_p_idx].x_mm = best_new_x
            placements[best_p_idx].y_mm = best_new_y
            current_violations, current_energy = validate_spatial_rules(room, placements, catalog_by_sku)
            continue

        # Phase A2: Orthogonal Rotation Relaxation (0, 90, 180, 270 degrees)
        for idx, p in enumerate(placements):
            if p.placement_id not in candidate_ids:
                continue

            orig_rot = p.rotation_deg
            for rot_delta in (90, 180, 270):
                p.rotation_deg = (orig_rot + rot_delta) % 360
                _, e_test = validate_spatial_rules(room, placements, catalog_by_sku)
                if e_test < best_nudge_energy - eps:
                    best_nudge_energy = e_test
                    best_p_idx = idx
                    best_new_rot = p.rotation_deg
                p.rotation_deg = orig_rot

        if best_p_idx >= 0 and best_new_rot is not None and best_nudge_energy < current_energy - eps:
            placements[best_p_idx].rotation_deg = best_new_rot
            current_violations, current_energy = validate_spatial_rules(room, placements, catalog_by_sku)
            continue

        # Phase B: Discrete Pruning (strictly decreasing N)
        conflicted_ids = {pid for v in current_violations for pid in v.affected_placement_ids}
        conflict_scores: dict[str, float] = {}
        for v in current_violations:
            for pid in v.affected_placement_ids:
                conflict_scores[pid] = conflict_scores.get(pid, 0.0) + 1.0

        def prune_priority(p: Placement) -> tuple[int, float]:
            item = catalog_by_sku.get(p.sku)
            fam = item.family if item else "unknown"
            fam_score = {"accessory": 0, "storage": 1, "collaboration": 2, "chair": 3, "desk": 4}.get(fam, 5)
            return (fam_score, -conflict_scores.get(p.placement_id, 0.0))

        prune_candidate = min(
            (p for p in placements if p.placement_id in conflicted_ids),
            key=prune_priority,
            default=None,
        )

        if prune_candidate:
            placements = [p for p in placements if p.placement_id != prune_candidate.placement_id]
            current_violations, current_energy = validate_spatial_rules(room, placements, catalog_by_sku)
        else:
            break

    final_status: Literal["valid", "invalid", "unsatisfiable"]
    escalation_report = None

    if current_energy == 0.0:
        final_status = "valid"
    else:
        final_status = "unsatisfiable"
        desks_remaining = len([p for p in placements if catalog_by_sku.get(p.sku, None) and catalog_by_sku[p.sku].family == "desk"])
        tradeoff_recommendations = [
            f"Reduce target capacity from {room.capacity} to {max(1, desks_remaining)} to preserve the egress diagonal corridor.",
            "Select compact footprint furniture (e.g. 1200 mm width) to satisfy clearance corridors.",
            "Reroute presentation point or egress corridor to free up perimeter floor area.",
        ]

        # Enrich surviving violations with structured tradeoff repair options conforming to violation schema
        for v in current_violations:
            v.repair_options.append({
                "action": "escalate_tradeoff",
                "strategy": "capacity_reduction",
                "recommendation": tradeoff_recommendations[0],
            })

        escalation_report = {
            "escalation": "UNSATISFIABLE_LAYOUT",
            "room_id": room.room_id,
            "required_capacity": room.capacity,
            "achieved_placements": len(placements),
            "residual_energy": round(current_energy, 1),
            "surviving_violations": [v.to_dict() for v in current_violations],
            "tradeoff_recommendations": tradeoff_recommendations,
            "human_tradeoff_options": tradeoff_recommendations,
        }

    layout = Layout(
        room_id=room.room_id,
        placements=placements,
        violations=current_violations,
        status=final_status,
    )

    return ArbitrationResult(
        layout=layout,
        iterations_run=iteration,
        initial_energy=initial_energy,
        final_energy=current_energy,
        escalation_report=escalation_report,
    )
