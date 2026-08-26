#!/usr/bin/env python3
"""RuleBound Round 1 Master Runner.

Accepts --input <dir> and --output <dir>, satisfying the RUNNER_CONTRACT.md specification.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from rulebound.dxf_exporter import export_layout_to_dxf
from rulebound.generator import generate_layout_for_room
from rulebound.loader import load_asset_pack
from rulebound.pricing_engine import aggregate_placements_to_lines, price_room_layout
from rulebound.serializer import write_deterministic_json


def process_rooms(input_dir: str | Path, output_dir: str | Path, export_dxf: bool = True) -> int:
    pack = load_asset_pack(input_dir)
    out_root = Path(output_dir)

    for room in sorted(pack.rooms, key=lambda r: r.room_id):
        room_id = room.room_id
        room_out = out_root / room_id

        # 1. Generate & Arbitrate Layout
        layout = generate_layout_for_room(room, pack)

        # 2. Price Layout
        if layout.status == "valid":
            line_specs = aggregate_placements_to_lines(layout.placements)
            quote = price_room_layout(room_id, line_specs, pack)
        else:
            # Blocked quote for invalid or unsatisfiable layout under RB-PRC-013
            quote = price_room_layout(room_id, [], pack)
            quote.blocking_reasons.extend([v.message for v in layout.violations])

        # 3. Serialize Deterministic JSON
        write_deterministic_json(room_out / "layout.json", layout.to_dict())
        write_deterministic_json(room_out / "quote.json", quote.to_dict())

        # 4. Optional / Bonus DXF CAD Floorplan Export
        if export_dxf:
            export_layout_to_dxf(room, layout, pack.catalog_by_sku, room_out / "plan.dxf")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="RuleBound Round 1 One-Command Runner")
    parser.add_argument("--input", required=True, help="Path to input data directory")
    parser.add_argument("--output", required=True, help="Path to output directory")
    parser.add_argument("--no-dxf", action="store_true", help="Disable CAD DXF floorplan generation")
    args = parser.parse_args()

    exit_code = process_rooms(args.input, args.output, export_dxf=not args.no_dxf)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
