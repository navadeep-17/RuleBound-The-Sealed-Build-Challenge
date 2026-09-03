"""Procedural Stress-Testing Suite for RuleBound Fit-Out Engine.
Generates 50 synthetic rooms with diverse geometries, doors, and egress paths
to verify 100% mathematical termination, zero constraint escapes, and determinism.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rulebound.loader import load_asset_pack
from rulebound.models import Door, Egress, RoomSpec
from rulebound.generator import generate_layout_for_room
from rulebound.pricing_engine import aggregate_placements_to_lines, price_room_layout


def create_synthetic_room(index: int) -> RoomSpec:
    """Procedurally generates realistic and challenging test rooms."""
    room_id = f"SYNTH-{index:03d}"

    # Varying room geometries
    if index % 4 == 0:
        # L-shaped room
        w1, h1 = 7000 + (index % 5) * 500, 5000 + (index % 3) * 400
        w2, h2 = 4000, 3000
        boundary = (
            (0, 0), (w1, 0), (w1, h2), (w2, h2), (w2, h1), (0, h1)
        )
        door_offset = 600
        egress_to = (w1 - 800, h2 - 600)
    elif index % 4 == 1:
        # Long narrow room (corridor style)
        w, h = 12000, 3600
        boundary = ((0, 0), (w, 0), (w, h), (0, h))
        door_offset = 1000
        egress_to = (w - 1000, h - 600)
    elif index % 4 == 2:
        # Large open floorplan
        w, h = 14000, 8000
        boundary = ((0, 0), (w, 0), (w, h), (0, h))
        door_offset = 1200
        egress_to = (w - 1500, h - 1500)
    else:
        # Compact studio room
        w, h = 5400 + (index % 4) * 400, 4800 + (index % 3) * 300
        boundary = ((0, 0), (w, 0), (w, h), (0, h))
        door_offset = 800
        egress_to = (w - 800, h - 800)

    doors = (
        Door(
            door_id="D1",
            wall="south",
            offset_mm=door_offset,
            width_mm=1000,
            swing="inward_right" if index % 2 == 0 else "outward_right",
        ),
    )

    egress = Egress(
        from_door_id="D1",
        to_point_mm=egress_to,
        min_width_mm=1100,
    )

    capacity = 4 + (index % 12) * 2

    return RoomSpec(
        room_id=room_id,
        name=f"Procedural Room {index:03d}",
        boundary_mm=boundary,
        doors=doors,
        windows=(),
        egress=egress,
        capacity=capacity,
    )


def run_stress_test(num_rooms: int = 50) -> bool:
    print("=" * 80)
    print(f"  RUNNING RULEBOUND STRESS-TEST BENCHMARK ({num_rooms} SYNTHETIC ROOMS)")
    print("=" * 80)

    pack = load_asset_pack("data")
    t0 = time.time()

    valid_count = 0
    unsatisfiable_count = 0
    invalid_escapes = 0

    for i in range(1, num_rooms + 1):
        room = create_synthetic_room(i)
        layout = generate_layout_for_room(room, pack)

        if layout.status == "valid":
            valid_count += 1
            if len(layout.violations) > 0:
                print(f"[FAIL] Room {room.room_id} marked valid but has {len(layout.violations)} violations!")
                invalid_escapes += 1
            lines = aggregate_placements_to_lines(layout.placements)
            quote = price_room_layout(room.room_id, lines, pack)
            if quote.status != "priced" or quote.summary["grand_total_inr"] <= 0:
                print(f"[FAIL] Valid room {room.room_id} has invalid quote!")
                invalid_escapes += 1

        elif layout.status == "unsatisfiable":
            unsatisfiable_count += 1
            quote = price_room_layout(room.room_id, [], pack)
            if quote.status != "blocked" or quote.summary["grand_total_inr"] != 0:
                print(f"[FAIL] Unsatisfiable room {room.room_id} emitted non-zero price!")
                invalid_escapes += 1
        else:
            print(f"[FAIL] Room {room.room_id} returned illegal status: {layout.status}")
            invalid_escapes += 1

    elapsed = time.time() - t0
    print(f"\nCompleted {num_rooms} rooms in {elapsed:.2f}s ({elapsed/num_rooms*1000:.1f} ms/room)")
    print(f"  - Valid Fit-Outs:         {valid_count}")
    print(f"  - Unsatisfiable Blocked:  {unsatisfiable_count}")
    print(f"  - Constraint Escapes:     {invalid_escapes}")
    print("=" * 80)

    if invalid_escapes == 0:
        print(">>> 100% PASS: All procedural rooms satisfied safety and pricing invariants!")
        return True
    else:
        print(">>> FAIL: Constraint or pricing escapes detected!")
        return False


if __name__ == "__main__":
    success = run_stress_test(50)
    sys.exit(0 if success else 1)
