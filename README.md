# RuleBound Round 1 Release Pack

This archive is the official candidate pack for **RuleBound: The Sealed Build Challenge**. Every record is synthetic and belongs to the fictional manufacturer **Northwind Furnishings**. It contains no real client, employee or customer data.

## Start here

1. Read `PROBLEM.md`.
2. Read `RUNNER_CONTRACT.md` and `PRICING_SPEC.md`.
3. Inspect `data/`, `schemas/`, and `worked_examples/`.
4. Choose either `starter/python/` or `starter/typescript/`.
5. Run `python3 tools/verify_pack.py` from the archive root.
6. Implement the required one-command runner and create `OUTPUT/<room_id>/layout.json` and `quote.json`.
7. Run `python3 tools/validate_output.py OUTPUT`.
8. Run `python3 tools/check_determinism.py --command '<your command>' --input data --work-dir .determinism-check`.

## Released contents

- 120 catalog SKUs across five families
- 18 finishes with basis-point uplifts and family compatibility
- 14 spatial and pricing rules in YAML plus an exact JSON mirror
- Five room specifications and five matching plain-English briefs
- Six synthetic historical jobs
- Two arithmetically reconciled worked reference quotes
- Seven JSON Schemas
- Python and TypeScript typed loaders and runner stubs
- Output validator, pack verifier and determinism checker

## Important boundaries

- `data/rules.json` and `data/rules.yaml` contain identical rules; JSON is provided to keep both starter loaders dependency-free.
- Integer INR and basis points are used everywhere. Round half-up only where a fractional rupee is unavoidable.
- The held-back judging set and Round 3 curveball pack are intentionally **not included**.
- Questions about an ambiguity or pack defect must go to the common participant channel so every candidate receives the same clarification.

---

## Solution Execution & Determinism Statement

### Prerequisites
- Python 3.10+ (Standard Library only, **zero external dependencies** required)

### Run Command
To generate layouts, quotes, and DXF floorplans for any input directory:
```bash
python run.py --input data --output OUTPUT
```
*(Alternatively, via starter stub: `python starter/python/runner.py --input data --output OUTPUT`)*

### Output Validation
To validate output schemas and business contracts against the official validator:
```bash
python tools/validate_output.py OUTPUT
```

### Determinism Verification
To verify 100% byte-identical outputs across repeated runs:
```bash
python tools/check_determinism.py --command "python run.py --input {input} --output {output}" --input data --work-dir .determinism-check
```

### Run Automated Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Optional Bonus Features

#### 1. Explain Any Price Line by Retrieving Its Trace
Retrieve full arithmetic citations and rule breakdowns directly from the CLI:
```bash
# Explain an individual line item's calculations and rules
python run.py --explain ROOM-01 --line L001

# Explain complete quote and financial breakdown for a room
python run.py --explain ROOM-01

# Inspect a blocked quote's explicit constraint violation reasons
python run.py --explain ROOM-03
```

#### 2. Vector CAD Floorplans (DXF & Browser SVG)
For every room, the runner generates both:
- `plan.dxf`: Industry-standard AutoCAD Release 12 / 2000 ASCII DXF file.
- `plan.svg`: Interactive scaled vector floorplan viewable directly in any web browser (Chrome, Edge, Safari) showing room boundary, egress corridor, doors with swing arcs, windows, and categorized furniture items.
