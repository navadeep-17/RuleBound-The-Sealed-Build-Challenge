#!/usr/bin/env python3
"""RuleBound Round 1 Master Runner & Explainability Engine.

Satisfies RUNNER_CONTRACT.md:
    python run.py --input <dir> --output <dir>

Bonus Track Capabilities:
    --explain <quote_path_or_room_id> [--line <line_id>]
    --check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from rulebound.dxf_exporter import export_layout_to_dxf
from rulebound.svg_exporter import export_room_svg
from rulebound.generator import generate_layout_for_room
from rulebound.loader import load_asset_pack
from rulebound.pricing_engine import aggregate_placements_to_lines, price_room_layout
from rulebound.serializer import write_deterministic_json


def process_rooms(input_dir: str | Path, output_dir: str | Path, export_dxf: bool = True) -> int:
    pack = load_asset_pack(input_dir)
    out_root = Path(output_dir)

    print("\n" + "=" * 70)
    print("  RULEBOUND FIT-OUT ENGINE  --  Processing All Rooms")
    print("=" * 70)

    for room in sorted(pack.rooms, key=lambda r: r.room_id):
        room_id = room.room_id
        room_out = out_root / room_id

        print(f"\n  [{room_id}] {room.name}")
        print(f"  {'-' * 48}")

        # 1. Generate & Arbitrate Layout
        layout = generate_layout_for_room(room, pack)

        # 2. Price Layout
        if layout.status == "valid":
            line_specs = aggregate_placements_to_lines(layout.placements)
            quote = price_room_layout(room_id, line_specs, pack)
            total = quote.summary.get("grand_total_inr", 0)
            print(f"  [OK] Layout  : valid  ({len(layout.placements)} placements, {len(layout.violations)} violations)")
            print(f"  [OK] Quote   : INR {total:>10,}")
        else:
            # Blocked quote for invalid or unsatisfiable layout under RB-PRC-013
            quote = price_room_layout(room_id, [], pack)
            quote.blocking_reasons.extend([v.message for v in layout.violations])
            print(f"  [!!] Layout  : {layout.status}")
            print(f"  [XX] Quote   : BLOCKED (INR 0)  -- RB-PRC-013 escalation triggered")

        # 3. Serialize Deterministic JSON
        write_deterministic_json(room_out / "layout.json", layout.to_dict())
        write_deterministic_json(room_out / "quote.json", quote.to_dict())
        print(f"  [OK] Written : layout.json, quote.json")

        # 4. Bonus Track: CAD DXF Floorplan Export
        if export_dxf:
            export_layout_to_dxf(room, layout, pack.catalog_by_sku, room_out / "plan.dxf")
            print(f"  [OK] Written : plan.dxf  (AutoCAD R12 1:1 scale)")

        # 5. Bonus Track: Scaled SVG Floorplan (viewable in browser)
        svg_path = room_out / "plan.svg"
        export_room_svg(room, layout, pack.catalog_by_sku, str(svg_path))
        print(f"  [OK] Written : plan.svg  (browser-viewable)")

        # 6. Standout Feature: Executive Commercial Fit-Out Proposal & BOM Report
        from rulebound.report_generator import generate_html_proposal
        svg_content = svg_path.read_text(encoding="utf-8") if svg_path.exists() else None
        html_report = generate_html_proposal(room, layout, quote, pack, svg_content)
        (room_out / "report.html").write_text(html_report, encoding="utf-8")
        print(f"  [OK] Written : report.html  (executive proposal & BOM)")

    print("\n" + "=" * 70)
    print("  ALL ROOMS COMPLETE  --  Outputs written to:  " + str(out_root))
    print("=" * 70 + "\n")
    return 0



def process_dxf_input(dxf_path: str | Path, output_dir: str | Path, data_dir: str = "data") -> int:
    """Bonus Track: Ingest a 2D CAD DXF floorplan file and generate layout and quote."""
    from rulebound.dxf_ingester import ingest_room_from_dxf
    pack = load_asset_pack(data_dir)
    room = ingest_room_from_dxf(dxf_path)
    out_root = Path(output_dir) / room.room_id

    layout = generate_layout_for_room(room, pack)
    if layout.status == "valid":
        line_specs = aggregate_placements_to_lines(layout.placements)
        quote = price_room_layout(room.room_id, line_specs, pack)
    else:
        quote = price_room_layout(room.room_id, [], pack)
        quote.blocking_reasons.extend([v.message for v in layout.violations])

    write_deterministic_json(out_root / "layout.json", layout.to_dict())
    write_deterministic_json(out_root / "quote.json", quote.to_dict())
    svg_path = out_root / "plan.svg"
    export_room_svg(room, layout, pack.catalog_by_sku, str(svg_path))
    from rulebound.report_generator import generate_html_proposal
    svg_content = svg_path.read_text(encoding="utf-8") if svg_path.exists() else None
    (out_root / "report.html").write_text(generate_html_proposal(room, layout, quote, pack, svg_content), encoding="utf-8")
    print(f"DXF Ingest Complete: Room {room.room_id} parsed -> Output written to {out_root}")
    return 0


def explain_price_trace(quote_path: Path | str, line_id: str | None = None) -> int:
    """Bonus Track: Explain any price line or quote summary by retrieving its trace."""
    path = Path(quote_path)
    if not path.is_file():
        # Check if room id was provided e.g. "ROOM-01"
        candidate = Path("OUTPUT") / str(quote_path) / "quote.json"
        if candidate.is_file():
            path = candidate
        else:
            print(f"Error: Quote file not found at {quote_path}", file=sys.stderr)
            return 1

    with open(path, encoding="utf-8") as f:
        quote = json.load(f)

    room_id = quote.get("room_id", "Unknown")
    status = quote.get("status", "unknown")
    currency = quote.get("currency", "INR")

    print("=" * 80)
    print("NORTHWIND FURNISHINGS -- PRICING EXPLANABILITY ENGINE")
    print(f"Quote: {quote.get('quote_id', 'N/A')} | Room: {room_id} | Status: {status.upper()}")
    print("=" * 80)

    if status == "blocked":
        print("\n[STATUS: BLOCKED QUOTE]")
        print("This quote was blocked under rule RB-PRC-013 due to spatial / specification violations:\n")
        for idx, reason in enumerate(quote.get("blocking_reasons", []), 1):
            print(f"  {idx}. {reason}")
        print("=" * 80)
        return 0

    lines = quote.get("lines", [])
    if line_id:
        target_line = next((l for l in lines if l.get("line_id") == line_id), None)
        if not target_line:
            print(f"Error: Line '{line_id}' not found in quote. Available lines: {[l['line_id'] for l in lines]}")
            return 1
        lines_to_show = [target_line]
    else:
        lines_to_show = lines

    for line in lines_to_show:
        lid = line["line_id"]
        sku = line["sku"]
        qty = line["quantity"]
        ulp = line["unit_list_price_inr"]
        base = line["base_amount_inr"]
        fin_id = line["finish_id"]
        fin_up = line["finish_uplift_inr"]
        q_disc = line["quantity_discount_inr"]
        net = line["net_goods_inr"]

        print(f"\n--- Line Item: {lid} | SKU: {sku} | Finish: {fin_id} | Quantity: {qty} units ---")
        print(f"  * Catalog Unit List Price:     {currency} {ulp:>8,}")
        print(f"  * Base Amount (qty x unit):    {currency} {base:>8,}   [CATALOG]")
        print(f"  * Finish Uplift:              +{currency} {fin_up:>8,}   [RB-PRC-010]")
        print(f"  * Quantity Discount:          -{currency} {q_disc:>8,}   [RB-PRC-009]")
        print(f"  -------------------------------------------------------------")
        print(f"  * Net Goods for Line:          {currency} {net:>8,}")
        print("\n  Arithmetic Audit Trace:")
        for t in line.get("trace", []):
            rule = t.get("rule_id", "TRACE")
            amt = t.get("amount_inr", 0)
            inputs = ", ".join(f"{k}={v}" for k, v in sorted(t.get("inputs", {}).items()))
            print(f"    - [{rule:<10}] Amount: {currency} {amt:>8,} | Inputs: ({inputs})")

    # Summary breakdown
    summary = quote.get("summary", {})
    print("\n" + "=" * 80)
    print("FINANCIAL SUMMARY & LOGISTICS BREAKDOWN")
    print("-" * 80)
    print(f"  Net Goods (Total):             {currency} {summary.get('goods_after_adjustments_inr', 0):>8,}")
    print(f"  Labour Charge:                +{currency} {summary.get('labour_inr', 0):>8,}   [RB-PRC-011: {summary.get('labour_minutes', 0)} min @ INR {summary.get('labour_rate_inr_per_hour', 0)}/hr]")
    print(f"  Freight Charge:               +{currency} {summary.get('freight_inr', 0):>8,}   [RB-PRC-012]")
    print(f"  -------------------------------------------------------------")
    print(f"  GRAND TOTAL:                   {currency} {summary.get('grand_total_inr', 0):>8,}")
    print("=" * 80)
    return 0


def main() -> None:
    if len(sys.argv) == 1:
        print("""
================================================================================
  RULEBOUND FIT-OUT & DETERMINISTIC PRICING ENGINE
  Author: Navadeep (navadeepthota17@gmail.com)
================================================================================
  Usage Quickstart:
    1. Generate All Room Outputs & Proposals:
       python run.py --input data --output OUTPUT

    2. Master Full System Audit Scorecard:
       python run.py --verify-all

    3. 17-Test Automated Verification Suite:
       python run.py --check

    4. Interactive Terminal 2D Floorplan Visualizer:
       python run.py --visualize ROOM-01
       python run.py --visualize ROOM-03

    5. Explain Line-Level Arithmetic Traces:
       python run.py --explain ROOM-01 --line L001

    6. Ingest External CAD DXF Floorplan:
       python run.py --ingest-dxf OUTPUT/ROOM-01/plan.dxf --output OUTPUT
================================================================================
""")
        sys.exit(0)

    parser = argparse.ArgumentParser(description="RuleBound Master Runner & Explainability Engine")
    parser.add_argument("--input", help="Path to input data directory")
    parser.add_argument("--output", help="Path to output directory")
    parser.add_argument("--no-dxf", action="store_true", help="Disable CAD DXF floorplan generation")
    parser.add_argument("--explain", help="Retrieve and explain price trace for a quote file or room ID")
    parser.add_argument("--line", help="Line ID to explain (optional, used with --explain)")
    parser.add_argument("--check", action="store_true", help="Run comprehensive verification test suite")
    parser.add_argument("--verify-all", action="store_true", help="Run master 5-part full system audit and verification scorecard")
    parser.add_argument("--visualize", help="Render ANSI 2D top-down floorplan directly in the terminal for a room ID")
    parser.add_argument("--ingest-dxf", help="Bonus Track: Ingest a 2D CAD DXF floorplan file and generate layout and quote")
    args = parser.parse_args()

    if args.verify_all:
        from rulebound.verifier import run_full_system_verification
        sys.exit(run_full_system_verification(args.input or "data", args.output or "OUTPUT"))

    if args.ingest_dxf:
        out_dir = args.output or "OUTPUT"
        in_dir = args.input or "data"
        sys.exit(process_dxf_input(args.ingest_dxf, out_dir, in_dir))

    if args.explain:
        sys.exit(explain_price_trace(args.explain, args.line))

    if args.visualize:
        from rulebound.loader import load_asset_pack
        from rulebound.terminal_view import render_terminal_floorplan
        pack = load_asset_pack(args.input or "data")
        room_id = args.visualize
        if room_id not in pack.rooms_by_id:
            print(f"Error: Room {room_id} not found in {args.input or 'data'}")
            sys.exit(1)
        room = pack.rooms_by_id[room_id]
        out_layout_path = Path(args.output or "OUTPUT") / room_id / "layout.json"
        if out_layout_path.exists():
            import json
            from rulebound.models import Placement, Violation
            data = json.loads(out_layout_path.read_text(encoding="utf-8"))
            placements = [Placement(**p) for p in data["placements"]]
            violations = [Violation(**v) for v in data["violations"]]
        else:
            from rulebound.generator import generate_layout_for_room
            layout = generate_layout_for_room(room, pack)
            placements = layout.placements
            violations = layout.violations

        print(render_terminal_floorplan(room, placements, pack.catalog_by_sku, violations))
        sys.exit(0)

    if args.check:
        import unittest
        suite = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        res = runner.run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)

    if not args.input or not args.output:
        parser.error("--input and --output are required when running layout and pricing generation.")

    exit_code = process_rooms(args.input, args.output, export_dxf=not args.no_dxf)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
