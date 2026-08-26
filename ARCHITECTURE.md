# System Architecture — RuleBound

**Northwind Furnishings Fit-Out Engine**  
*Round 1 Sealed Build Solution*

---

## 1. Architectural Overview

RuleBound bridges generative design and deterministic manufacturing rules through a strict, unidirectional execution pipeline:

```text
  [ Brief & RoomSpec ]
          │
          ▼
   Generative Layer (Design Intent & Initial Placement Proposals)
          │  ProposedLayout (Contract Inward)
          ▼
┌──────────────────────────────────────────────────────────────┐
│                  DETERMINISTIC SEAM                          │
├──────────────────────────────────────────────────────────────┤
│  Spatial Constraint Engine (RB-GEO-001 .. RB-GEO-008)         │
│         │                                                    │
│         ▼                                                    │
│  Arbitration Engine (Bounded Repair Loop: Relaxation/Prune)  │
│         │                                                    │
│         ▼                                                    │
│  Deterministic Pricing Engine (RB-PRC-009 .. RB-PRC-014)     │
└──────────────────────────────────────────────────────────────┘
          │
          ├────────────────────────┬────────────────────────┐
          ▼                        ▼                        ▼
    `layout.json`            `quote.json`              `plan.dxf`
 (Validated / Escalated)   (Priced / Blocked)       (CAD Bonus Track)
```

The system is implemented in modular Python 3 with **zero external dependencies**, ensuring instant execution and cross-platform byte determinism on clean judging machines.

---

## 2. Arbitration

### Question 1: What object crosses the boundary in each direction? Show the contract.

At the seam between generative proposals and deterministic evaluation, two strongly-typed JSON Schema-compliant objects cross the boundary:

**Forward Boundary (Generative $\to$ Deterministic Arbiter):**
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

### Question 2: What may the model decide, and when does control pass irreversibly to deterministic code?

- **Generative Scope**: The model/generative layer interprets the natural language brief, selects product families, picks compatible finishes from `finishes.json`, and proposes initial spatial cluster anchors $(x, y, \theta)$.
- **Irreversible Hand-off**: Control passes **irreversibly** to deterministic code the instant `ProposedLayout` is ingested by `arbitrate_layout()`. No probabilistic inference, external API call, or stochastic sampling is permitted beyond this seam. All downstream adjustments, pruning, and pricing are strictly rule-based and deterministic.

### Question 3: How does the loop terminate? State the bound and what strictly decreases on each pass.

- **Hard Bound**: The arbitration loop is strictly bounded to $K_{\max} = 6$ iterations.
- **State Measure**: The state at iteration $t$ is evaluated by the lexicographic measure $\mathcal{M}_t = (N_t, E_t) \in \mathbb{N} \times \mathbb{R}_{\ge 0}$, where:
  - $N_t$ is the active placement count ($N_t \le N_0$).
  - $E_t = \sum \text{penalty}_i$ is the scalar geometric violation energy (sum of overlap areas, clearance shortfalls, and wall encroachments).
- **Strictly Decreasing Invariant**:
  - **Phase A (Continuous Relaxation)**: The arbiter attempts cardinal spatial nudges on the worst-offending placement. A nudge is accepted if and only if $E_{t+1} \le E_t - \epsilon$ ($\epsilon = 1.0\text{ mm}$).
  - **Phase B (Discrete Pruning)**: If no continuous nudge reduces energy by $\epsilon$, the arbiter prunes the placement with the highest violation degree and lowest functional priority (accessories first, then storage, then chairs), strictly decrementing $N_{t+1} = N_t - 1$.
  - Because $N_t \ge 0$ is a non-negative integer and $K_{\max}$ is finite, the loop is well-founded and **provably terminates**.

### Question 4: When no valid layout exists, what is produced and what does a human see?

When a room cannot be satisfied (e.g. physical area or diagonal egress corridor mathematically prevents required capacity without violating clearance rules):
1. **Machine Artifacts**:
   - `layout.json`: Written with `"status": "unsatisfiable"` and surviving structured violations conforming to `schemas/violation.schema.json`.
   - `quote.json`: Written with `"status": "blocked"`, `"summary": {"grand_total_inr": 0}`, and `"blocking_reasons"` citing `RB-PRC-013` and the specific spatial shortfalls.
2. **Human Operator Escalation Report**:
   ```json
   {
     "escalation": "UNSATISFIABLE_LAYOUT",
     "room_id": "ROOM-03",
     "required_capacity": 10,
     "residual_energy": 121704.3,
     "tradeoff_recommendations": [
       "Reduce target capacity from 10 to 6 to preserve the 1100mm egress diagonal.",
       "Select compact 1200mm desks (NW-DES-001) instead of 1400mm.",
       "Omit secondary acoustic accessories to relieve walkway pinch points."
     ]
   }
   ```

---

## 3. Deterministic Pricing Math

All calculations use integer INR. Basis point adjustments (`100 bps = 1%`) and fractional rupees use **round half up** via Python's `decimal` module (`ROUND_HALF_UP`).
- **Base**: $\text{base} = \text{unit\_price} \times \text{quantity}$ (`CATALOG`).
- **Finish Uplift**: $\text{round\_half\_up}(\text{base} \times \text{bps} / 10000)$ (`RB-PRC-010`).
- **Quantity Discount**: Tiered on base amount ($5\text{--}9: 300\text{ bps}$, $10\text{--}19: 700\text{ bps}$, $20+: 1000\text{ bps}$) (`RB-PRC-009`).
- **Labour Band**: Banded on total minutes ($\le 240\text{ min}: ₹900/\text{hr}$; $241\text{--}480\text{ min}: ₹800/\text{hr}$; $>480\text{ min}: ₹750/\text{hr}$) (`RB-PRC-011`).
- **Freight Band**: On net goods ($\le ₹100\text{k}: ₹5\text{k}$; $₹100\text{k}\text{--}₹250\text{k}: ₹9\text{k}$; $>₹250\text{k}: 4\%$) (`RB-PRC-012`).
- **Trace Citation**: Every line and summary item includes an arithmetic input/output trace (`RB-PRC-014`).

---

## 4. Determinism Statement & Execution

Judges verify 100% byte-identical repeat output via:
```bash
python tools/check_determinism.py --command "python run.py --input {input} --output {output}" --input data --work-dir .determinism-check
```
Output serialization guarantees UTF-8, keys sorted alphabetically, 2-space indentation, and terminal newline. Zero runtime timestamps, UUIDs, or random seeds are permitted in outputs.
