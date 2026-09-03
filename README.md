# RuleBound — Final Submission (Round 3)

**Northwind Furnishings Commercial Fit-Out & Deterministic Pricing Engine**  
*LV8 Tech Sealed Build Challenge — Final Submission (Round 3)*  
**Author**: Navadeep ([navadeepthota17@gmail.com](mailto:navadeepthota17@gmail.com))  
**Repository**: [https://github.com/navadeep-17/RuleBound-The-Sealed-Build-Challenge](https://github.com/navadeep-17/RuleBound-The-Sealed-Build-Challenge)

---

## 🎥 Demonstration Video

> 📺 **Watch the 5-Minute Technical Demonstration Video**:  
> **[Google Drive Video Link](https://drive.google.com/file/d/1sQc1XkfnCOp7_p-EhqP3ZcSq-8P5Df82/view?usp=sharing)**  
> *(Covers boundary seam architecture, vector relaxation descent, Question 4 escalation on ROOM-03, deterministic pricing math, CAD DXF floorplans, and Azure/Entra ID bonus tracks)*

---

## 📋 Executive Summary & Architectural Deliverables

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Runnable Solution** | [`run.py`](run.py), [`rulebound/`](rulebound/) | Python 3.10+ zero-dependency fit-out & pricing engine. |
| **Revised Architecture** | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Boundary contracts, vector relaxation, $K_{\max}=6$ termination proof, and pricing math. |
| **Iterative Changelog** | [`CHANGELOG.md`](CHANGELOG.md) | Comprehensive engineering changelog from Round 1 baseline through Round 3 final. |
| **Committed Outputs** | [`OUTPUT/`](OUTPUT/) | Pre-generated, schema-validated, byte-deterministic outputs for all 5 released rooms. |
| **CAD Floorplans & DXF Ingest** | [`rulebound/dxf_ingester.py`](rulebound/dxf_ingester.py) | 1:1 scale DXF export, interactive SVG floorplans, and ASCII DXF ingestion via `--ingest-dxf`. |
| **Azure + Entra ID Deployment** | [`azure/`](azure/) | Production Dockerfile, Bicep infrastructure template, FastAPI service, and Entra ID JWT verification. |
| **Test & Verification Suite** | [`tests/`](tests/), [`tools/`](tools/) | 17 unit tests verifying all 14 rules, schema validator, pack verifier, and determinism checker. |

---

## 🗂️ Repository Architecture & Directory Layout

```text
├── run.py                    # Master CLI runner & entrypoint
├── rulebound/                # Core Fit-Out & Pricing Engine (100% pure Python standard library)
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

### 1. Master Output Generation
Run the master engine across all rooms in the dataset:
```bash
python run.py --input data --output OUTPUT
```

### 2. Comprehensive Test Suite (All 14 Rules Verified)
Run the 17-test verification suite:
```bash
python run.py --check
```

### 3. Official JSON Schema Validation
Validate all generated `layout.json` and `quote.json` files against the schemas:
```bash
python tools/validate_output.py OUTPUT
```

### 4. Byte-for-Byte Multi-Run Determinism Verification
Verify 100% byte-identical outputs across repeated execution:
```bash
python tools/check_determinism.py --command "python run.py --input {input} --output {output}" --input data --work-dir .determinism-check
```

### 5. Interactive Technical Demonstration CLI
Run the automated step-by-step terminal showcase:
```bash
python tools/demo.py
```

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

