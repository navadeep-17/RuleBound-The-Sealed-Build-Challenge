# RuleBound — Final Submission (Round 3)

**Northwind Furnishings Commercial Fit-Out & Deterministic Pricing Engine**  
*LV8 Tech Sealed Build Challenge — Final Submission (Round 3)*  
**Author**: Navadeep ([navadeepthota17@gmail.com](mailto:navadeepthota17@gmail.com))  
**Repository**: [https://github.com/navadeep-17/RuleBound-The-Sealed-Build-Challenge](https://github.com/navadeep-17/RuleBound-The-Sealed-Build-Challenge)

[![RuleBound CI Verification Suite](https://github.com/navadeep-17/RuleBound-The-Sealed-Build-Challenge/actions/workflows/ci.yml/badge.svg)](https://github.com/navadeep-17/RuleBound-The-Sealed-Build-Challenge/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Dependencies: Zero](https://img.shields.io/badge/dependencies-zero%20(stdlib)-brightgreen.svg)
![Determinism: 100%](https://img.shields.io/badge/determinism-100%25%20byte--identical-success.svg)
![Tests: 17/17](https://img.shields.io/badge/tests-17%2F17%20passing-success.svg)

---

## 🎥 Technical Demonstration Video

A comprehensive technical walkthrough (< 5 minutes) covering end-to-end execution from one documented command, boundary seam enforcement, automated constraint violation repair, Question 4 escalation, deterministic pricing traces, and enterprise bonus tracks:

🔗 **Watch Demonstration Video**: [**Google Drive Link (Click Here to View)**](https://drive.google.com/file/d/1IscQXa4xYL_y87sdL4Pcm_dueWJeUDt0/view?usp=sharing)

### Video Walkthrough Highlights
- **0:00 – 0:45**: Problem overview, zero-dependency architecture, and master verification scorecard (`python run.py --verify-all`).
- **0:45 – 1:30**: End-to-end generation (`python run.py --input data --output OUTPUT`) & JSON schema validation.
- **1:30 – 2:30**: Boundary seam contract (`ProposedLayout`), SAT collision detection, and bounded vector relaxation repair ($K_{\max}=6$).
- **2:30 – 3:30**: Interactive ANSI 2D terminal visualizer (`--visualize`) and Question 4 escalation on unsatisfiable room (`ROOM-03`).
- **3:30 – 4:15**: Deterministic integer INR pricing arithmetic and line-level audit traces (`--explain`).
- **4:15 – 4:50**: Native CAD DXF export/ingest, executive HTML commercial proposals (`report.html`), and Azure Entra ID OAuth2 package.

---

## 📋 Executive Summary & Architectural Deliverables

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Runnable Solution** | [`run.py`](run.py), [`rulebound/`](rulebound/) | Python 3.10+ zero-dependency fit-out & pricing engine. |
| **Revised Architecture** | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Boundary contracts, vector relaxation, $K_{\max}=6$ termination proof, and pricing math. |
| **Iterative Changelog** | [`CHANGELOG.md`](CHANGELOG.md) | Comprehensive engineering changelog from Round 1 baseline through Round 3 final. |
| **Committed Outputs** | [`OUTPUT/`](OUTPUT/) | Pre-generated, schema-validated, byte-deterministic outputs for all 5 released rooms. |
| **Technical Documentation** | [`docs/`](docs/) | Deep mathematical proofs, spatial rules specs, and system guides. |
| **CAD Floorplans & DXF Ingest** | [`rulebound/dxf_ingester.py`](rulebound/dxf_ingester.py) | 1:1 scale DXF export, interactive SVG floorplans, and ASCII DXF ingestion via `--ingest-dxf`. |
| **Azure + Entra ID Deployment** | [`azure/`](azure/) | Production Dockerfile, Bicep infrastructure template, FastAPI service, and Entra ID JWT verification. |
| **Test & Verification Suite** | [`tests/`](tests/), [`tools/`](tools/) | 17 unit tests verifying all 14 rules, schema validator, pack verifier, and determinism checker. |
| **Technical Demo Video** | [Google Drive Link](https://drive.google.com/file/d/1IscQXa4xYL_y87sdL4Pcm_dueWJeUDt0/view?usp=sharing) | Complete 5-minute technical walkthrough: end-to-end execution, violation repair, Question 4 escalation, pricing traces, and bonus tracks. |

---

## 🗂️ Repository Architecture & Directory Layout

```text
├── .github/workflows/ci.yml  # Multi-OS (Ubuntu, Windows) Python (3.10-3.13) CI matrix
├── run.py                    # Master CLI runner & entrypoint
├── docs/                     # Deep-dive technical documentation
│   ├── SYSTEM_GUIDE.md       # Module-by-module reference & architecture dataflow
│   ├── MATHEMATICAL_PROOFS.md# SAT collision, K_max=6 termination, and rounding proofs
│   ├── SPATIAL_RULES_SPEC.md # Exhaustive 14-rule geometric and pricing specification
│   └── BONUS_TRACKS_GUIDE.md # CAD DXF and Azure Entra ID architecture guide
├── rulebound/                # Core Fit-Out & Pricing Engine (100% pure Python standard library)
│   ├── verifier.py           # Master 5-part full system audit scorecard (--verify-all)
│   ├── arbiter.py            # Multi-modal relaxation arbiter (Vector normal translation, rotation, K_max=6)
│   ├── geometry.py           # 2D SAT collision detection, boundary containment, distances
│   ├── generator.py          # Autonomous constraint-aware spatial zoning generator
│   ├── nlp_matcher.py        # Deterministic semantic brief intent parser
│   ├── spatial_engine.py     # Complete 14-rule constraint validation engine
│   ├── pricing_engine.py     # Integer commercial pricing math with line traces
│   ├── serializer.py         # Deterministic UTF-8 sorted JSON writer
│   ├── dxf_ingester.py       # Pure-Python ASCII DXF CAD floorplan parser
│   ├── dxf_exporter.py       # 1:1 AutoCAD R12/2000 DXF floorplan exporter
│   ├── svg_exporter.py       # Scaled browser-viewable SVG floorplan exporter
│   ├── terminal_view.py      # ANSI 2D terminal floorplan visualizer (--visualize)
│   └── report_generator.py   # Publication-grade commercial proposal & BOM exporter
├── azure/                    # Enterprise Bonus: Azure Container Apps + Entra ID OAuth2 package
│   ├── Dockerfile            # Container configuration
│   ├── main.bicep            # Declarative Bicep infrastructure-as-code
│   ├── app.py                # FastAPI HTTP service
│   ├── entra_auth.py         # Microsoft Entra ID JWT Bearer token validator
│   └── README.md             # Azure CLI deployment instructions
├── data/                     # Released synthetic asset pack (catalog, finishes, rules, rooms, briefs)
├── schemas/                  # Official JSON Schemas for validation
├── starter/                  # Official Python & TypeScript stubs
├── tests/                    # 17 automated unit tests covering all 14 rules
├── tools/                    # Benchmarking & verification tools
│   ├── demo.py               # Interactive terminal showcase demo
│   ├── stress_test.py        # 50-room synthetic benchmark
│   ├── pareto_frontier.py    # Capacity vs safety Pareto frontier analyzer
│   ├── viewer.html           # Interactive HTML5 Canvas floorplan & pricing viewer
│   ├── check_determinism.py  # Multi-run byte-for-byte determinism checker
│   ├── validate_output.py    # Official JSON schema validator
│   └── verify_pack.py        # Pack integrity verifier
├── OUTPUT/                   # Validated, byte-identical outputs for all 5 rooms
└── worked_examples/          # Reconciled reference quotes (REF-QUOTE-01 & 02)
```

---

## 🚀 Quickstart & One-Command Execution

### Prerequisites
- **Python 3.10+** (Standard Library only — **zero external dependencies required**)

### 1. Master System Audit & Verification Scorecard
Run the full 5-part system verification suite in one command:
```bash
python run.py --verify-all
```

### 2. Master Output Generation
Run the master engine across all rooms in the dataset:
```bash
python run.py --input data --output OUTPUT
```

### 3. Comprehensive Test Suite (All 14 Rules Verified)
Run the 17-test verification suite:
```bash
python run.py --check
```

### 4. Official JSON Schema Validation
Validate all generated `layout.json` and `quote.json` files against the schemas:
```bash
python tools/validate_output.py OUTPUT
```

### 5. Byte-for-Byte Multi-Run Determinism Verification
Verify 100% byte-identical outputs across repeated execution:
```bash
python tools/check_determinism.py --command "python run.py --input {input} --output {output}" --input data --work-dir .determinism-check
```

### 6. Interactive Technical Demonstration CLI
Run the automated step-by-step terminal showcase:
```bash
python tools/demo.py
```

---

## 🔒 Determinism Statement

As required by the **Runner Contract** and **Submission Checklist**, judges can verify 100% byte-identical output across repeat runs on any clean machine by executing:

```bash
# Automated verification across two isolated runs:
python tools/check_determinism.py --command "python run.py --input {input} --output {output}" --input data --work-dir .determinism-check
```

Or manually:
```bash
# Run 1:
python run.py --input data --output OUTPUT_RUN1

# Run 2:
python run.py --input data --output OUTPUT_RUN2

# Compare byte-for-byte hashes:
git diff --no-index OUTPUT_RUN1 OUTPUT_RUN2
```

**Determinism Guarantees**:
- **Zero Entropy**: No timestamps, machine paths, random seeds, or pseudo-random UUIDs.
- **Canonical Serialization**: UTF-8 encoding, alphabetically sorted keys, two-space indentation, and trailing newline.
- **Integer Arithmetic**: Exact integer INR, basis points (`100 bps = 1%`), and half-up rounding eliminate IEEE 754 floating-point platform drift.
- **Pure-Code Downstream**: Zero LLMs, stochastic heuristics, or network calls downstream of the generative boundary seam.

---

## 📊 Released Rooms & Verified Commercial Outputs

| Room ID | Room Name | Target Cap. | Status | Grand Total (INR) | Reconciled Reference | Generated Files |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`ROOM-01`** | Harbour Design Studio | 12 | **VALID** | **₹337,964** | Exactly matches `REF-QUOTE-01` | `layout.json`, `quote.json`, `plan.dxf`, `plan.svg`, `report.html` |
| **`ROOM-02`** | Verdant Study Carrels | 18 | **VALID** | **₹452,853** | Exactly matches `REF-QUOTE-02` | `layout.json`, `quote.json`, `plan.dxf`, `plan.svg`, `report.html` |
| **`ROOM-03`** | Nimbus Hybrid Team Room | 10 | **UNSATISFIABLE** | **BLOCKED (₹0)** | Question 4 Escalation (Diagonal Egress) | `layout.json`, `quote.json`, `plan.dxf`, `plan.svg`, `report.html` |
| **`ROOM-04`** | Orchard Focus Library | 14 | **UNSATISFIABLE** | **BLOCKED (₹0)** | Question 4 Escalation (Perimeter Clearances) | `layout.json`, `quote.json`, `plan.dxf`, `plan.svg`, `report.html` |
| **`ROOM-05`** | Apex Project Hub | 18 | **UNSATISFIABLE** | **BLOCKED (₹0)** | Question 4 Escalation (Density vs Egress) | `layout.json`, `quote.json`, `plan.dxf`, `plan.svg`, `report.html` |

---

## 💎 Bonus Tracks & Enterprise Features

### Bonus Track 1: Native CAD DXF Ingest & Export
- **Export**: Automatically generates 1:1 scale AutoCAD R12/2000 compatible `plan.dxf` and browser-viewable `plan.svg` for every room.
- **Ingest**: Import external 2D DXF floorplans directly to generate compliant layouts and pricing:
  ```bash
  python run.py --ingest-dxf OUTPUT/ROOM-01/plan.dxf --output OUTPUT
  ```

### Bonus Track 2: Azure Container Apps & Microsoft Entra ID Authentication
- Located in the [`azure/`](azure/) directory:
  - **`azure/main.bicep`**: Declarative Azure Container Apps infrastructure with Managed Identity.
  - **`azure/entra_auth.py`**: OAuth2 Bearer token verification against Microsoft Entra ID OpenID Connect metadata.
  - **`azure/app.py`**: Authenticated API service with `/health` and `/api/v1/quote/{room_id}` endpoints.
  - **`azure/Dockerfile`**: Production container configuration.
  - **`azure/README.md`**: Step-by-step Azure CLI deployment & authentication guide.

### Bonus Track 3: Price Trace & Violation Explainability CLI
Inspect line-level arithmetic traces and escalation blocking reasons from the terminal:
```bash
# Explain arithmetic breakdown for an individual line item
python run.py --explain ROOM-01 --line L001

# Explain complete quote and financial summary for a room
python run.py --explain ROOM-01

# Explain reasons and trade-offs for an unsatisfiable layout
python run.py --explain ROOM-03
```

---

## 🌟 Standout Enterprise Innovations (Round 3 Final)

### 1. Interactive ANSI Terminal Floorplan Visualizer (`--visualize`)
Render scaled, color-coded 2D floorplans and collision heatmaps directly in the terminal:
```bash
# View valid layout for ROOM-01
python run.py --visualize ROOM-01

# View highlighted constraint violations for unsatisfiable ROOM-03
python run.py --visualize ROOM-03
```

### 2. Publication-Grade Commercial Proposals & BOM (`report.html`)
For every room, the runner exports an official, print-ready executive fit-out proposal at `OUTPUT/<room_id>/report.html` featuring:
- Official Northwind Furnishings corporate letterhead and project metadata.
- Embedded 1:1 scale vector CAD floorplan drawing.
- Itemized Bill of Materials (BOM) with unit rates, finish uplifts, and quantity breaks.
- Statutory regulatory safety certification (zero SAT overlaps, 1100mm egress clearance).

### 3. Capacity vs Safety Pareto Frontier Analyzer
Evaluate density boundaries and trade-offs for challenging architectural layouts:
```bash
python tools/pareto_frontier.py ROOM-03
```

### 4. Deterministic Natural Language Brief Semantic Parser (`rulebound/nlp_matcher.py`)
Automatically translates plain-English client briefs into structured spatial intents (capacity, typology, finish palettes, collaboration amenities) without probabilistic external API calls.

