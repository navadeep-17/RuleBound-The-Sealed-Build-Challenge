from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from rulebound.models import CatalogItem, Layout, Placement, RoomSpec, Violation
from rulebound.spatial_engine import validate_spatial_rules


@dataclass
class ArbitrationResult:
    layout: Layout
    iterations_run: int
    initial_energy: float
    final_energy: float
    escalation_report: dict[str, Any] | None = None


def arbitrate_layout(
    room: RoomSpec,
    initial_placements: list[Placement],
    catalog_by_sku: dict[str, CatalogItem],
    max_iterations: int = 10,
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

    # 4 cardinal nudges for fast, targeted continuous relaxation
    step_deltas = [
        (100, 0), (-100, 0), (0, 100), (0, -100),
        (200, 0), (-200, 0), (0, 200), (0, -200),
    ]

    while iteration < max_iterations and current_energy > 0.0:
        iteration += 1
        best_nudge_energy = current_energy
        best_p_idx = -1
        best_new_x = 0
        best_new_y = 0

        # Phase A: Targeted Continuous Relaxation on worst violation
        target_v = current_violations[0]
        candidate_ids = set(target_v.affected_placement_ids)

        for idx, p in enumerate(placements):
            if p.placement_id not in candidate_ids:
                continue

            orig_x, orig_y = p.x_mm, p.y_mm
            for dx, dy in step_deltas:
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

        if best_p_idx >= 0 and best_nudge_energy < current_energy - eps:
            # Accept continuous relaxation step (strictly decreasing energy E)
            placements[best_p_idx].x_mm = best_new_x
            placements[best_p_idx].y_mm = best_new_y
            current_violations, current_energy = validate_spatial_rules(room, placements, catalog_by_sku)
            continue

        # Phase B: Discrete Pruning (strictly decreasing N)
        # Find the placement involved in the most / highest-energy violations
        conflicted_ids = {pid for v in current_violations for pid in v.affected_placement_ids}
        conflict_scores: dict[str, float] = {}
        for v in current_violations:
            for pid in v.affected_placement_ids:
                conflict_scores[pid] = conflict_scores.get(pid, 0.0) + 1.0

        # Lower priority to accessories, higher to desks/chairs
        def prune_priority(p: Placement) -> tuple[int, float]:
            item = catalog_by_sku.get(p.sku)
            fam = item.family if item else "unknown"
            fam_score = {"accessory": 0, "storage": 1, "collaboration": 2, "desk": 3, "chair": 4}.get(fam, 5)
            # We want to prune accessories first, then storage, then most-conflicted
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
        escalation_report = {
            "room_id": room.room_id,
            "required_capacity": room.capacity,
            "achieved_placements": len(placements),
            "residual_energy": current_energy,
            "surviving_violations": [v.to_dict() for v in current_violations],
            "human_tradeoff_options": [
                f"Reduce target capacity from {room.capacity} to {max(1, len(placements))}.",
                "Select smaller footprint desks (e.g. 1200 mm width) to satisfy clearance corridors.",
                "Reroute presentation point or egress corridor to free up perimeter floor area.",
            ],
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
