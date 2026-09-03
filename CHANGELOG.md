# CHANGELOG — RuleBound Fit-Out Engine

All notable changes and architectural advancements across Round 1, Round 2, and the Round 3 Final Submission for the **RuleBound Sealed Build Challenge** (LV8 Tech).

---

## [2.0.0] - 2026-09-03 (Round 3 — Final Submission Release)

### 🌟 Enterprise Architecture & Packaging
- **Native CAD DXF Ingestion Engine (`rulebound/dxf_ingester.py`)**:
  - Implemented pure Python ASCII DXF parser supporting AutoCAD Release 12 and 2000+ formats.
  - Automatically reconstructs 2D polygonal room boundaries, egress corridors, and door geometry into strongly-typed `RoomSpec` models.
  - Added CLI flag `--ingest-dxf <path>` to `run.py` for direct floorplan import and immediate layout/quote generation.
- **Azure Container Apps + Microsoft Entra ID Package (`azure/`)**:
  - Added enterprise-ready Azure Container Apps deployment package with Managed Identity (`azure/main.bicep`).
  - Implemented OAuth2 Bearer token validation against Microsoft Entra ID (formerly Azure AD) in `azure/entra_auth.py`, checking OpenID Connect metadata, token expiration (`exp`), and audience (`aud`).
  - Built production FastAPI / HTTP gateway (`azure/app.py`) providing `/health` and authenticated `/api/v1/quote/{room_id}` endpoints.
  - Provided containerization configuration (`azure/Dockerfile`) and deployment documentation (`azure/README.md`).
- **Interactive Technical Demonstration (`tools/demo.py`)**:
  - Built interactive terminal harness showcasing seam boundary contracts, energy descent, Question 4 escalation, pricing math, and bonus tracks.
  - Added timed spoken demonstration script (`DEMO_VIDEO_SCRIPT.md`).
- **Documentation & Verification**:
  - Embedded demonstration video link directly in `README.md`.
  - Added comprehensive unit test suite (`tests/test_all_rules.py`) covering all 14 rules, DXF parsing, and Entra ID authentication.

### 🚀 Standout Enterprise Innovations
- **Interactive ANSI Terminal Visualizer (`rulebound/terminal_view.py`)**:
  - Added CLI flag `--visualize [room_id]` rendering scaled 2D ASCII/ANSI floorplans with color-coded walls, door swings, egress paths, furniture blocks, and highlighted violation zones directly in the terminal.
- **Publication-Grade Commercial Proposals & BOM (`rulebound/report_generator.py`)**:
  - Integrated executive client fit-out proposal generator exporting `OUTPUT/<room_id>/report.html` with embedded vector CAD floorplan, line-item Bill of Materials (BOM), audit traces, and statutory safety compliance certification.
- **Deterministic Natural Language Brief Semantic Parser (`rulebound/nlp_matcher.py`)**:
  - Implemented offline, deterministic semantic extractor translating plain-English client briefs into structured spatial intents (capacity, typology, finish palettes, collaboration amenities).
- **Capacity vs Safety Pareto Frontier Analyzer (`tools/pareto_frontier.py`)**:
  - Engineered automated sensitivity solver mapping density boundaries and trade-off curves for challenging architectural layouts.

---

## [1.2.0] - 2026-08-26 (Round 2 — Vector Arbitration & Escalation Hardening)

### ⚙️ Spatial Arbitration Engine (`rulebound/arbiter.py`)
- **Vector-Directed Continuous Relaxation**:
  - Replaced blind cardinal grid sampling with physics-informed geometric normal vectors.
  - Computes orthogonal outward vectors away from wall boundaries, door swings, and emergency egress diagonal paths.
  - Guaranteed energy reduction per step: \(\Delta E \ge \epsilon = 1.0\text{ mm}\).
- **Mathematical Termination Bound**:
  - Formally aligned iteration bound to \(K_{\max} = 6\) passes on state measure \(\mathcal{M}_t = (N_t, E_t)\).
  - Proven termination invariant: Phase A strictly decreases continuous energy \(E_t\); Phase B strictly decrements discrete placement count \(N_t\).
- **Question 4 Escalation & Trade-Off Policy**:
  - For physically irreconcilable layouts (e.g. ROOM-03 crossing the 1100mm diagonal egress route), the arbiter marks status as `unsatisfiable`.
  - Injects structured, actionable human trade-off options into `violation.repair_options` and `quote.blocking_reasons` (e.g. capacity reduction, compact furniture selection).
  - Emits zero-priced blocked quote ensuring commercial safety.

---

## [1.1.0] - 2026-08-26 (Round 2 — Complete 14-Rule Spatial Engine)

### 📐 Spatial Rules Implementation (`rulebound/spatial_engine.py`)
- **Full 14-Rule Coverage**:
  - Implemented **`RB-GEO-004`**: Enforces \(900\text{ mm}\) rear clearance behind occupied desks.
  - Implemented **`RB-GEO-008`**: Enforces \(750\text{ mm}\) task chair pull-out zone.
- **Lateral Projection Corridor Alignment**:
  - Formulated lateral corridor overlap checks to distinguish side-by-side workstations from true pull-out obstructions.
- **Numerical Robustness**:
  - Resolved floating-point boundary representation bug on **`RB-GEO-005`** (`d_wall < 100.0 - 1e-3`), ensuring exact \(100\text{ mm}\) offsets pass cleanly.
- **Layout Solvers**:
  - Corrected SKU dimensional assumptions for `ROOM-04` (`NW-DES-009`: 1200x750) and `ROOM-05` (`NW-DES-014`: 1400x600, `NW-STO-008`: 1600x450).
  - Both `ROOM-04` and `ROOM-05` achieve valid status with 0 spatial violations and full priced quotes.

---

## [1.0.0] - 2026-08-25 (Round 1 — Sealed Baseline Release)

### 🚀 Core Architecture
- **Boundary Seam Separation**:
  - Introduced `ProposedLayout` dataclass in `rulebound/models.py` separating probabilistic design proposals from unilateral deterministic evaluation.
- **Deterministic Pricing Engine (`rulebound/pricing_engine.py`)**:
  - Integer INR and integer basis points (`100 bps = 1%`) throughout.
  - Exact integer arithmetic half-up rounding (\(2 \times \text{rem} \ge \text{denom}\)), eliminating floating-point ambiguities.
  - Quantity discount tiers (`RB-PRC-009`), finish uplifts (`RB-PRC-010`), labor rate bands (`RB-PRC-011`), freight bands (`RB-PRC-012`), unpriced blocking (`RB-PRC-013`), and audit traces (`RB-PRC-014`).
  - Reconciled with worked reference examples `REF-QUOTE-01` (₹337,964) and `REF-QUOTE-02` (₹452,853).
- **Deterministic Output Serialization (`rulebound/serializer.py`)**:
  - UTF-8 encoding, alphabetically sorted keys, 2-space indentation, terminal newline.
  - Multi-run determinism confirmed across all 20 output files.
