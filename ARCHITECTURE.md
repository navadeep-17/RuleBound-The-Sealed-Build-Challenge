# System Architecture — RuleBound

**Northwind Furnishings Fit-Out & Commercial Pricing Engine**  
*LV8 Tech Sealed Build Challenge — Round 3 Revised Architecture*  
**Author**: Navadeep ([navadeepthota17@gmail.com](mailto:navadeepthota17@gmail.com))

---

## 1. Architectural Overview & Boundary Design

RuleBound resolves the conflict between creative AI exploration and strict commercial/regulatory constraints through a **strict, unidirectional boundary architecture**:

```text
  [ Client Brief & RoomSpec JSON ]
                 │
                 ▼
  Generative Layer (Design Intent & Heuristic Proposals)
                 │
                 │  ProposedLayout (Strongly-Typed Forward Contract)
                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   DETERMINISTIC SEAM BOUNDARY                          │
├────────────────────────────────────────────────────────────────────────┤
│  1. Spatial Rules Engine (RB-GEO-001 .. RB-GEO-008)                    │
│     - SAT Polygon Intersections, Egress Corridors, Pull-out Zones      │
│     │                                                                  │
│     ▼                                                                  │
│  2. Arbitration Engine (Bounded Vector-Directed Repair Loop)           │
│     - Normal-Vector Relaxation & Discrete Priority Pruning (K_max = 6) │
│     │                                                                  │
│     ▼                                                                  │
│  3. Deterministic Pricing Engine (RB-PRC-009 .. RB-PRC-014)            │
│     - Integer Arithmetic, Half-Up Rounding, Full Line Audit Traces     │
└────────────────────────────────────────────────────────────────────────┘
                 │
                 ├────────────────────────┬────────────────────────┐
                 ▼                        ▼                        ▼
           `layout.json`            `quote.json`              `plan.dxf`
        (Validated/Escalated)     (Priced / Blocked)       (1:1 CAD Floorplan)
```

The system is implemented in modular Python 3 with **zero external dependencies**, guaranteeing immediate execution and cross-platform byte-for-byte determinism on clean judging environments.

---

## 2. Arbitration Mechanics & Boundary Contracts

### Question 1: What object crosses the boundary in each direction? Show the contract.

At the seam between generative proposals and deterministic evaluation, two strongly-typed JSON Schema-compliant objects cross the boundary:

**Forward Boundary (Generative Layer $\to$ Deterministic Arbiter):**
```json
{
  "room_id": "ROOM-01",
  "placements": [
    {
      "placement_id": "P001",
      "sku": "NW-DES-003",
      "finish_id": "F03",
      "x_mm": 1200,
      "y_mm": 4400,
      "rotation_deg": 0
    }
  ]
}
```

**Reverse Boundary (Spatial Engine $\to$ Arbiter / Repair Action):**
```json
{
  "status": "invalid",
  "violations": [
    {
      "violation_id": "V001",
      "rule_id": "RB-GEO-002",
      "message": "Placement P012 encroaches into egress path by 87.9 mm.",
      "affected_placement_ids": ["P012"],
      "measured": {"clearance_from_centerline_mm": 462.1},
      "required": {"min_half_width_mm": 550.0},
      "repair_options": [
        {"action": "translate", "placement_id": "P012", "strategy": "clear_egress"},
        {"action": "remove", "placement_id": "P012"}
      ]
    }
  ]
}
```

---

### Question 2: What may the model decide, and when does control pass irreversibly to deterministic code?

- **Generative Scope**: The model or generative layer interprets client briefs, selects candidate product SKUs, selects valid finish IDs from `finishes.json`, and proposes initial spatial cluster centroids $(x, y, \theta)$.
- **Irreversible Hand-off**: Control passes **irreversibly** to deterministic code the instant `ProposedLayout` is ingested by `arbitrate_layout()`. No LLM, stochastic sampling, or external network call operates downstream of this seam. All adjustments, pruning, and financial calculations are executed by deterministic code.

---

### Question 3: How does the loop terminate? State the bound and what strictly decreases on each pass.

- **Hard Iteration Bound**: The arbitration loop is strictly bounded to $K_{\max} = 6$ passes.
- **State Measure**: State at iteration $t$ is defined by the well-founded lexicographic measure $\mathcal{M}_t = (N_t, E_t) \in \mathbb{N} \times \mathbb{R}_{\ge 0}$, where:
  - $N_t$ is the placement count ($N_t \le N_0$).
  - $E_t = \sum \text{penalty}_i$ is the scalar geometric energy (sum of overlap areas, egress shortfalls, and clearance shortfalls).
- **Strictly Decreasing Invariant**:
  - **Phase A (Vector-Directed Relaxation)**: The arbiter computes outward normal vectors from wall boundaries, door swings, and egress corridors. A nudge is accepted if and only if $E_{t+1} \le E_t - \epsilon$ where $\epsilon = 1.0\text{ mm}$.
  - **Phase B (Discrete Pruning)**: If no continuous nudge reduces energy by $\epsilon$, the arbiter prunes the placement with the highest conflict score and lowest functional priority (accessories first, then storage, then chairs), strictly decrementing $N_{t+1} = N_t - 1$.
  - Because $N_t \ge 0$ is a non-negative integer and $K_{\max}$ is finite, the loop is well-founded and **provably terminates**.

---

### Question 4: When no valid layout exists, what is produced and what does a human see?

When physical geometry or mandatory emergency egress corridors mathematically prevent satisfying the target capacity (e.g. `ROOM-03`):
1. **Machine Artifacts**:
   - `layout.json`: Emitted with `"status": "unsatisfiable"`, residual energy, and structured violations conforming to `schemas/violation.schema.json`.
   - `quote.json`: Emitted with `"status": "blocked"`, `"summary": {"grand_total_inr": 0}`, and `"blocking_reasons"` citing spatial constraint failures (`RB-PRC-013`).
2. **Human Operator Escalation Report**:
   ```json
   {
     "escalation": "UNSATISFIABLE_LAYOUT",
     "room_id": "ROOM-03",
     "required_capacity": 10,
     "residual_energy": 121704.3,
     "tradeoff_recommendations": [
       "Reduce target capacity from 10 to 8 to preserve the 1100mm egress diagonal corridor.",
       "Select compact 1200mm desks (NW-DES-001) instead of 1400mm.",
       "Reroute presentation point or egress corridor to free up perimeter floor area."
     ]
   }
   ```

---

## 3. Deterministic Pricing Math & Arithmetic Integrity

All financial arithmetic is computed in integer INR and integer basis points (`100 bps = 1%`). Fractional rupees use exact **round half-up** via integer division:
$$\text{round\_half\_up}(N, D) = \lfloor (2N + D) / (2D) \rfloor$$

1. **Base Amount**: $\text{base} = \text{unit\_price} \times \text{quantity}$ (`CATALOG`).
2. **Finish Uplift**: $\text{round\_half\_up}(\text{base} \times \text{bps} / 10000)$ (`RB-PRC-010`).
3. **Quantity Discount**: Tiered on base amount ($5\text{--}9: 300\text{ bps}$, $10\text{--}19: 700\text{ bps}$, $20+: 1000\text{ bps}$) (`RB-PRC-009`).
4. **Labour Fee**: Banded on total assembly minutes ($\le 240\text{ min}: ₹900/\text{hr}$; $241\text{--}480\text{ min}: ₹800/\text{hr}$; $>480\text{ min}: ₹750/\text{hr}$) (`RB-PRC-011`).
5. **Freight Fee**: Banded on net goods ($\le ₹100\text{k}: ₹5\text{k}$; $₹100\text{k}\text{--}₹250\text{k}: ₹9\text{k}$; $>₹250\text{k}: 4\%$) (`RB-PRC-012`).
6. **Immutable Trace**: Every quote line includes an input/output calculation trace (`RB-PRC-014`).

---

## 4. Enterprise Bonus Architecture

### 4.1 Native CAD DXF Ingest Engine (`rulebound/dxf_ingester.py`)
- Direct ASCII DXF parsing without third-party libraries.
- Reconstructs polygonal room boundaries, doors, and egress paths into `RoomSpec`.
- Ingest via CLI: `python run.py --ingest-dxf <path>`.

### 4.2 Azure Container Apps + Microsoft Entra ID Authentication (`azure/`)
- Declarative infrastructure via Azure Bicep (`azure/main.bicep`).
- OIDC token verification against Entra ID metadata (`azure/entra_auth.py`).
- Production FastAPI endpoint (`azure/app.py`).
