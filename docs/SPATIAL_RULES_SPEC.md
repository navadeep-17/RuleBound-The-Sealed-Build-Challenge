# Spatial & Pricing Rules Specification

This document provides the definitive technical specification for all 14 rules implemented in the **RuleBound Fit-Out Engine**.

---

## Part 1: Spatial & Geometric Rules (`RB-GEO-001` .. `RB-GEO-008`)

### `RB-GEO-001`: Minimum Walkway Clearance
- **Threshold**: $\ge 900\text{ mm}$ between adjacent furniture items.
- **Evaluation**: For every distinct pair of placements $(P_1, P_2)$, compute the minimum Euclidean distance between their convex polygons:
  $$d(P_1, P_2) = \min_{\vec{x} \in P_1, \vec{y} \in P_2} \|\vec{x} - \vec{y}\|$$
- **Exception**: Designated clusters (e.g. back-to-back desks or desks paired with their task chairs) where lateral gap $\le 50\text{ mm}$.
- **Penalty Energy**: If $50 < d < 900$, $\text{penalty} = (900 - d) \times 2.0$.

### `RB-GEO-002`: Emergency Egress Corridor Clearance
- **Threshold**: $\ge 1100\text{ mm}$ corridor (minimum half-width $R = 550\text{ mm}$ from centerline).
- **Evaluation**: The egress route is defined as a line segment $S = [P_{\text{door}}, P_{\text{exit}}]$. For each placement vertex $\vec{v} \in P$, compute the orthogonal distance to segment $S$:
  $$d_{\text{egress}}(\vec{v}, S) \ge 550.0\text{ mm}$$
- **Penalty Energy**: If $d_{\text{egress}} < 550$, $\text{penalty} = (550 - d_{\text{egress}}) \times 10.0$.

### `RB-GEO-003`: Door Swing Arc Clearance
- **Threshold**: Zero furniture intersection with the door swing radial sweep sector.
- **Evaluation**: For doors with `"inward"` swing, let $\vec{H}$ be the hinge coordinate and $R = \text{door-width-mm}$. For each placement vertex $\vec{v} \in P$:
  $$\|\vec{v} - \vec{H}\| \ge R$$
- **Penalty Energy**: If $\|\vec{v} - \vec{H}\| < R$, $\text{penalty} = (R - \|\vec{v} - \vec{H}\|) \times 8.0$.

### `RB-GEO-004`: Desk Rear Clearance
- **Threshold**: $\ge 900\text{ mm}$ behind occupied desks.
- **Evaluation**: Evaluates the rear boundary of desks facing user workstations to ensure adequate circulation behind seated workers.
- **Penalty Energy**: If rear clearance $d_{\text{rear}} < 900$, $\text{penalty} = (900 - d_{\text{rear}}) \times 4.0$.

### `RB-GEO-005`: Perimeter Wall Clearance
- **Threshold**: $\ge 100\text{ mm}$ from all room boundary walls.
- **Evaluation**: For each edge segment of the exterior room boundary polygon, compute minimum distance to the placement bounding box:
  $$d_{\text{wall}}(P, \partial \Omega) \ge 100.0 - 10^{-3}\text{ mm}$$
- **Penalty Energy**: If $d_{\text{wall}} < 100$, $\text{penalty} = (100 - d_{\text{wall}}) \times 5.0$.

### `RB-GEO-006`: Footprint Non-Overlap
- **Threshold**: Zero intersection between any two furniture items ($P_1 \cap P_2 = \emptyset$).
- **Evaluation**: Evaluated via the **Separating Axis Theorem (SAT)**.
- **Penalty Energy**: Overlap area $\times 50.0$.

### `RB-GEO-007`: Room Boundary Containment
- **Threshold**: All placement vertices must lie strictly within the interior of the room polygon ($P \subset \Omega$).
- **Evaluation**: Evaluated via standard 2D ray-casting point-in-polygon containment.

### `RB-GEO-008`: Task Chair Pull-Out Zone
- **Threshold**: $\ge 750\text{ mm}$ pull-out clearance behind task chairs.
- **Evaluation**: Verifies space behind task chairs in the direction of seat egress. Paired side-by-side chairs in the same row ($\Delta y \le 100\text{ mm}$ or $\Delta x \le 100\text{ mm}$) are exempt as paired seating.
- **Penalty Energy**: If $50 < d < 750$, $\text{penalty} = (750 - d) \times 8.0$.

---

## Part 2: Pricing & Determinism Rules (`RB-PRC-009` .. `RB-PRC-014`)

### `RB-PRC-009`: Tiered Quantity Discounts
Computed exclusively on Base Amount:
- **1–4 units**: $0\text{ bps}$ ($0\%$)
- **5–9 units**: $300\text{ bps}$ ($3.0\%$)
- **10–19 units**: $700\text{ bps}$ ($7.0\%$)
- **20+ units**: $1000\text{ bps}$ ($10.0\%$)

### `RB-PRC-010`: Finish Uplift Calculation
Applied on line Base Amount using basis points from `finishes.json`:
$$\text{finish-uplift} = \text{round-half-up}\left(\frac{\text{base-amount} \times \text{uplift-bps}}{10000}\right)$$

### `RB-PRC-011`: Assembly Labour Fee
Banded on total assembly minutes across all catalog items:
- $\le 240\text{ min}$: ₹900 / hour
- $241\text{--}480\text{ min}$: ₹800 / hour
- $> 480\text{ min}$: ₹750 / hour
$$\text{labour-fee} = \text{round-half-up}\left(\frac{\text{total-minutes} \times \text{rate-per-hour}}{60}\right)$$

### `RB-PRC-012`: Regional Freight Delivery Fee
Banded on total Net Goods:
- $\le ₹100,000$: ₹5,000 flat
- $₹100,001\text{--}₹250,000$: ₹9,000 flat
- $> ₹250,000$: $400\text{ bps}$ ($4.0\%$) of Net Goods, round half-up.

### `RB-PRC-013`: Commercial Integrity Blocking
If any item SKU is missing from catalog, any finish is incompatible with the item's family, or the room layout is unsatisfiable:
- `quote.status` is set to `"blocked"`.
- `grand_total_inr` is set to `0`.
- Explicit `blocking_reasons` cite the exact constraint or catalog failures.

### `RB-PRC-014`: Full Line-Level & Summary Arithmetic Trace
Every quote line includes an immutable `trace` array recording:
- `rule_id`: Rule identifier (`CATALOG`, `RB-PRC-009`, `RB-PRC-010`, etc.).
- `inputs`: Dictionary of exact mathematical inputs.
- `amount_inr`: Exact integer rupee impact.
