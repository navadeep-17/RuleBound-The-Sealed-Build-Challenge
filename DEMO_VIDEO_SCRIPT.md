# RuleBound Fit-Out Engine — 5-Minute Technical Demonstration Script

> **Candidate**: Navadeep (`navadeepthota17@gmail.com`)  
> **Challenge**: LV8 Tech Sealed Build Challenge — Round 1  
> **Duration**: ~4 to 5 Minutes  
> **Recording Tool**: Loom, OBS Studio, or QuickTime (Screen + Audio + Webcam)

---

## Video Timeline & Spoken Script

### 0:00 – 0:45 | Introduction & System Architecture
- **Action**: Open terminal with `python tools/demo.py` ready and VS Code open showing `ARCHITECTURE.md` and `rulebound/models.py`.
- **Spoken**:
  > "Hello evaluation committee! My name is Navadeep, and this is my Round 1 submission for the RuleBound fit-out design and pricing engine challenge.
  > 
  > At Northwind Furnishings, architectural compliance and commercial integrity are non-negotiable. To satisfy the prompt's core mandate, our system enforces a strict **boundary architecture**:
  > - On the left side of the seam, the generative design layer proposes furniture arrangements via a strongly-typed `ProposedLayout` contract.
  > - Across the boundary seam, the deterministic spatial arbiter and pricing engine have unilateral authority to validate, relax, prune, or block layouts. No LLM or generative heuristic is ever allowed inside the pricing or arbitration loop."

---

### 0:45 – 1:45 | Spatial Arbitration & Mathematical Termination Proof
- **Action**: Switch to terminal and run `python tools/demo.py`. Pause at Section 2.
- **Spoken**:
  > "Let’s look at Question 1 and 2: Spatial Arbitration and Termination.
  > 
  > The arbiter operates on a well-founded state measure \(M_t = (N_t, E_t)\), where \(N_t\) is the placement count and \(E_t\) is the continuous constraint energy.
  > 
  > In Phase A, the arbiter uses **vector-directed continuous relaxation**. Rather than random grid sampling, it computes physical normal vectors away from wall boundaries, door swings, and egress corridors. If a nudge strictly reduces constraint energy by at least \(\epsilon = 1.0\), it is accepted.
  > 
  > In Phase B, if no continuous displacement can relieve the conflict, the arbiter performs **discrete pruning**, strictly decrementing \(N_t\).
  > 
  > Because \(N_t\) is non-negative and bounded by \(N_0\), and the iteration count is bounded by \(K_{\max} = 6\), the algorithm is provably well-founded and guaranteed to terminate in finite steps."

---

### 1:45 – 2:45 | Handling Unsatisfiable Briefs & Question 4 Escalation
- **Action**: Highlight Section 3 in terminal output showing ROOM-03. Open `OUTPUT/ROOM-03/quote.json`.
- **Spoken**:
  > "A critical commercial requirement of the prompt is handling briefs where room geometry, egress routes, and capacity requirements are mathematically irreconcilable.
  > 
  > In ROOM-03—the Nimbus Hybrid Team Room—the 10-person capacity requirement directly crosses the 1100 mm emergency egress diagonal corridor.
  > 
  > When the arbiter reaches \(K_{\max} = 6\) with residual energy \(E_t > 0\), it immediately flags the layout as `unsatisfiable`.
  > Crucially, our pricing engine blocks the quote: zero line items are priced, and zero currency amount is emitted.
  > 
  > In addition, the engine produces structured human trade-off recommendations in the quote’s blocking reasons and violation repair options—recommending reducing capacity from 10 to 8, or selecting smaller footprint furniture."

---

### 2:45 – 3:45 | Pricing Engine Determinism & Arithmetic Integrity
- **Action**: Highlight Section 4 in terminal. Open `PRICING_SPEC.md` and `rulebound/pricing_engine.py`.
- **Spoken**:
  > "Now let's examine commercial integrity. In fit-out contracts, rounding discrepancies lead to invoice disputes and legal exposure.
  > 
  > Our pricing engine follows strict determinism:
  > - Calculations use integer basis points (where 100 bps = 1%) and integer INR throughout.
  > - Half-up rounding is implemented with exact integer arithmetic \((2 \times \text{rem} \ge \text{denom})\), eliminating Python’s floating-point banker's rounding.
  > - We enforce all 5 pricing rules: quantity discounts, finish uplifts, labor bands, freight bands, and mandatory audit traces.
  > - Every single quote line contains an immutable, reproducible audit trace showing the exact rule, input parameters, and INR adjustment."

---

### 3:45 – 4:45 | Enterprise Bonus Tracks & Quality Verification
- **Action**: Highlight Section 5 in terminal. Show `azure/main.bicep`, `rulebound/dxf_ingester.py`, and run `python run.py --check`.
- **Spoken**:
  > "Finally, we implemented both enterprise bonus tracks:
  > 1. **CAD DXF Floorplans & DXF Ingest**: We generate 1:1 scale DXF floorplans with standardized AutoCAD layers (`ROOM_BOUNDARY`, `DOORS_SWING`, `EGRESS`, `FURNITURE`). Furthermore, we built a native ASCII DXF ingester allowing clients to import 2D floorplans with `run.py --ingest-dxf`.
  > 2. **Azure Deployment with Microsoft Entra ID**: In the `azure/` package, we provide production Dockerfiles, FastAPI endpoints, Bicep infrastructure-as-code, and OAuth2 JWT authentication against Microsoft Entra ID.
  > 
  > Running `python tools/check_determinism.py` confirms that across multiple runs and environments, 20 generated files remain 100% byte-for-byte identical."

---

### 4:45 – 5:00 | Conclusion
- **Spoken**:
  > "RuleBound delivers complete spatial safety, robust arbitration, and airtight commercial pricing. Thank you for your time, and I look forward to defending this codebase in Round 2!"
