"""Capacity vs Safety Pareto Frontier Analyzer for RuleBound.
Evaluates physical density limits and trade-off curves for challenging/unsatisfiable rooms.
Elevates Question 4 escalation into a mathematical decision-support engine.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rulebound.loader import load_asset_pack
from rulebound.models import Placement, RoomSpec
from rulebound.generator import generate_generic_layout
from rulebound.arbiter import arbitrate_layout
from rulebound.pricing_engine import aggregate_placements_to_lines, price_room_layout


def analyze_pareto_frontier(room_id: str, data_dir: str = "data") -> None:
    pack = load_asset_pack(data_dir)
    if room_id not in pack.rooms_by_id:
        print(f"Error: Room {room_id} not found in {data_dir}")
        sys.exit(1)

    base_room = pack.rooms_by_id[room_id]
    target_cap = base_room.capacity

    print("\n" + "=" * 80)
    print(f"  PARETO CAPACITY & SAFETY FRONTIER ANALYSIS: {base_room.name} ({room_id})")
    print(f"  Target Requested Capacity: {target_cap} people | Egress Width: {base_room.egress.min_width_mm} mm")
    print("=" * 80)

    # Test capacities down from target
    test_capacities = sorted(list({target_cap, max(1, target_cap - 2), max(1, target_cap - 4), max(1, target_cap - 6), 2}), reverse=True)

    results = []
    optimal_compliant_cap = None

    for cap in test_capacities:
        # Create virtual room with altered capacity
        test_room = RoomSpec(
            room_id=base_room.room_id,
            name=base_room.name,
            boundary_mm=base_room.boundary_mm,
            doors=base_room.doors,
            windows=base_room.windows,
            egress=base_room.egress,
            capacity=cap,
        )

        candidates = generate_generic_layout(test_room, pack)
        arb_res = arbitrate_layout(test_room, candidates, pack.catalog_by_sku)

        status = arb_res.layout.status
        energy = arb_res.final_energy
        viols = len(arb_res.layout.violations)

        if status == "valid":
            lines = aggregate_placements_to_lines(arb_res.layout.placements)
            quote = price_room_layout(room_id, lines, pack)
            quote_display = f"INR {quote.summary['grand_total_inr']:,}"
            if optimal_compliant_cap is None:
                optimal_compliant_cap = cap
        else:
            quote_display = "BLOCKED (INR 0)"

        results.append((cap, status, energy, viols, quote_display))

    # Print Table
    print(f"\n{'Capacity':<10} | {'Status':<14} | {'Residual Energy':<16} | {'Violations':<10} | {'Commercial Quote'}")
    print("-" * 80)
    for cap, status, energy, viols, q_disp in results:
        status_color = "\033[92mVALID\033[0m" if status == "valid" else "\033[91mUNSATISFIABLE\033[0m"
        req_mark = " (Target)" if cap == target_cap else ""
        print(f"{str(cap) + req_mark:<10} | {status_color:<23} | {energy:>13.1f} mm | {viols:>10} | {q_disp}")
    print("-" * 80)

    if optimal_compliant_cap:
        print(f"\n\033[1;92m>>> MATHEMATICAL PARETO CONCLUSION:\033[0m")
        print(f"    Maximum Compliant Capacity: {optimal_compliant_cap} people.")
        print(f"    Preserves 100% of the {base_room.egress.min_width_mm} mm emergency corridor with zero code violations.")
    else:
        print(f"\n\033[1;91m>>> CONCLUSION: Room cannot be satisfied under current egress constraints.\033[0m")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RuleBound Pareto Frontier Analyzer")
    parser.add_argument("room_id", nargs="?", default="ROOM-03", help="Room ID to evaluate (default: ROOM-03)")
    parser.add_argument("--input", default="data", help="Input data directory")
    args = parser.parse_args()
    analyze_pareto_frontier(args.room_id, args.input)
