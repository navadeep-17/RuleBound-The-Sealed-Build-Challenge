# System Guide — RuleBound Fit-Out Engine

This document provides a comprehensive module-by-module reference explaining **what each component does, how it works, and how data flows through the architecture**.

---

## 1. High-Level Data Flow

```text
[ Input JSON & Brief ] 
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ 1. INGESTION & INTENT EXTRACTION                       │
│    - loader.py: Strongly-typed AssetPack & RoomSpec     │
│    - nlp_matcher.py: Deterministic brief intent parser │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ 2. GENERATIVE LAYER (Heuristic Seam Boundary)          │
│    - generator.py: Autonomous spatial zoning generator │
│    - Yields ProposedLayout dataclass                   │
└────────────────────────────────────────────────────────┘
          │
          ▼ (IRREVERSIBLE SEAM HANDOFF)
┌────────────────────────────────────────────────────────┐
│ 3. DETERMINISTIC SPATIAL ARBITRATION                   │
│    - spatial_engine.py: 14-rule constraint validation   │
│    - geometry.py: SAT collision & vector geometry      │
│    - arbiter.py: Vector relaxation & pruning (K_max=6) │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ 4. DETERMINISTIC PRICING ENGINE                        │
│    - pricing_engine.py: Integer INR, exact half-up     │
│    - Full arithmetic audit trace citations             │
└────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ 5. MULTI-MODAL EXPORT & VISUALIZATION                  │
│    - serializer.py: Deterministic sorted JSON          │
│    - dxf_exporter.py: 1:1 AutoCAD DXF CAD file         │
│    - svg_exporter.py: Interactive scaled browser SVG   │
│    - report_generator.py: Print-ready client proposal  │
│    - terminal_view.py: ANSI 2D terminal floorplan      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Core Package (`rulebound/`) Reference

### 2.1 Domain Models (`rulebound/models.py`)
- **Purpose**: Defines strongly-typed domain primitives using Python `dataclasses`.
- **Key Types**:
  - `RoomSpec`: Immutable definition of room boundaries, door offsets, swing types, egress corridors, and target capacity.
  - `Placement`: Spatial coordinate tuple `(placement_id, sku, finish_id, x_mm, y_mm, rotation_deg)`.
  - `ProposedLayout`: The formal forward boundary contract carrying candidate placements from the generative layer into the deterministic engine.
  - `Violation`: Structured constraint failure conforming strictly to `schemas/violation.schema.json`.
  - `Quote` & `QuoteLine`: Commercial quotation entities with integer amounts and arithmetic traces.

### 2.2 Ingestion & Pack Loader (`rulebound/loader.py`)
- **Purpose**: Dependency-free JSON loader parsing `catalog.json`, `finishes.json`, `rules.json`, `rooms/`, `briefs/`, and `historical_jobs.json`.
- **Validation**: Indexes items by SKU, finishes by ID, and rules by rule ID for $O(1)$ constant-time lookup.

### 2.3 Vector & Computational Geometry (`rulebound/geometry.py`)
- **Purpose**: Low-level 2D Euclidean geometry operations.
- **Key Algorithms**:
  - `get_rectangle_vertices(cx, cy, w, d, rot)`: Computes rotated 4-corner coordinate polygons.
  - `polygons_overlap_sat(p1, p2)`: **Separating Axis Theorem (SAT)** implementation for detecting arbitrary convex polygon intersections in 2D.
  - `point_to_segment_distance(pt, a, b)`: Orthogonal distance from coordinate point to line segment (used for emergency egress corridors).
  - `polygon_inside_boundary(poly, boundary)`: Ray-casting point-in-polygon containment test.
  - `min_distance_to_boundary(poly, boundary)`: Minimum clearance from furniture bounding boxes to exterior walls.

### 2.4 Spatial Constraint Engine (`rulebound/spatial_engine.py`)
- **Purpose**: Evaluates candidate placements against all 14 mandatory fit-out rules.
- **Rules Evaluated**:
  - `RB-GEO-001`: Minimum 900 mm walkway between adjacent furniture items.
  - `RB-GEO-002`: Emergency egress path clearance (half-width 550 mm along centerline).
  - `RB-GEO-003`: Inward door swing arc clearance (circular sector exclusion).
  - `RB-GEO-004`: Desk rear clearance (minimum 900 mm behind occupied desks).
  - `RB-GEO-005`: Perimeter wall clearance (minimum 100 mm buffer).
  - `RB-GEO-006`: Footprint non-overlap (SAT polygon collision check).
  - `RB-GEO-007`: Room boundary containment (all vertices strictly inside).
  - `RB-GEO-008`: Task chair pull-out zone (750 mm clearance behind chairs; permits paired orthogonal seating).
- **Energy Metric**: Returns a scalar violation energy $E \in \mathbb{R}_{\ge 0}$ representing total penalty magnitude.

### 2.5 Multi-Modal Arbitration Engine (`rulebound/arbiter.py`)
- **Purpose**: Resolves spatial violations through a bounded, provably terminating repair loop ($K_{\max}=6$).
- **Repair Mechanics**:
  - **Phase A1 (Continuous Vector Relaxation)**: Computes outward normal vectors away from wall boundaries, door swing arcs, and egress segments, nudging placements along energy gradient vectors.
  - **Phase A2 (Orthogonal Rotation Relaxation)**: Rotates tight placements ($90^\circ, 180^\circ, 270^\circ$) to clear narrow corridors without dropping items.
  - **Phase B (Discrete Priority Pruning)**: If continuous relaxation cannot reduce energy by $\epsilon \ge 1.0\text{ mm}$, prunes the placement with the highest conflict score and lowest functional utility (accessories $\to$ storage $\to$ chairs).
  - **Question 4 Escalation**: For unsatisfiable rooms, marks status as `unsatisfiable`, generates blocked zero-price quotes, and provides human operator trade-off recommendations.

### 2.6 Deterministic Pricing Engine (`rulebound/pricing_engine.py`)
- **Purpose**: Generates byte-identical, line-traceable commercial quotations.
- **Arithmetic Integrity**:
  - Strict integer INR and basis points (`100 bps = 1%`).
  - Exact integer half-up rounding: $\lfloor (2N + D) / (2D) \rfloor$.
  - Line-level calculations: Base Amount, Finish Uplift (`RB-PRC-010`), Quantity Discount (`RB-PRC-009`), Net Goods.
  - Summary-level calculations: Assembly Labour (`RB-PRC-011`), Regional Freight (`RB-PRC-012`), Grand Total.
  - Blocking under `RB-PRC-013`: Unknown SKUs, incompatible finishes, or unsatisfiable layouts immediately block quote generation.
  - Audit Trail (`RB-PRC-014`): Every line and summary item includes an arithmetic input/output trace.

### 2.7 Natural Language Brief Parser (`rulebound/nlp_matcher.py`)
- **Purpose**: Offline, deterministic extraction of client intent from plain-English briefs (`data/briefs/*.txt`).
- **Extracted Fields**: Target capacity, layout typology (paired pods, focus carrels, open workshop), finish preferences, and requested amenity counts.

### 2.8 Deterministic Serializer (`rulebound/serializer.py`)
- **Purpose**: Serializes output objects into byte-identical JSON.
- **Invariants**: UTF-8 encoding, alphabetically sorted keys, 2-space indentation, trailing newline. Zero timestamps or random UUIDs.

---

## 3. Benchmarking & Verification Tools (`tools/`)

| Tool | Purpose | How It Works |
| :--- | :--- | :--- |
| **`check_determinism.py`** | Multi-Run Determinism Proof | Executes runner twice in isolated directories and compares every file byte-for-byte using SHA-256 hashes. |
| **`validate_output.py`** | JSON Schema Validator | Validates all output files against the official JSON schemas. |
| **`verify_pack.py`** | Integrity & Reconciled Quotes | Verifies the 120 SKUs, 18 finishes, 14 rules, and reconciles quotes against worked examples. |
| **`stress_test.py`** | 50-Room Procedural Benchmark | Synthesizes 50 edge-case room geometries (L-shaped, corridor-style, wide open, compact studio) to stress-test arbitration and pricing. |
| **`pareto_frontier.py`** | Question 4 Decision Support | Evaluates capacity density limits and trade-off curves for challenging rooms. |
| **`demo.py`** | Interactive Showcase | Automated terminal presentation demonstrating seam boundaries, energy descent, and pricing traces. |
| **`viewer.html`** | HTML5 Canvas Visualizer | Zero-dependency browser floorplan viewer with real-time CAD layers and price drawer. |
