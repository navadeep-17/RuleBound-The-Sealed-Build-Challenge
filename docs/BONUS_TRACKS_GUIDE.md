# Bonus Tracks Guide: CAD DXF & Azure Entra ID

This document details the architecture, implementation, and verification of the two official bonus tracks (+10 total bonus points).

---

## Bonus Track 1: Native CAD DXF Ingest & Export (+5 Bonus)

### 1.1 Pure Python ASCII DXF Parser (`rulebound/dxf_ingester.py`)
- **Philosophy**: Zero external libraries (no `ezdxf` or C-bindings required). Directly parses standard AutoCAD Release 12 and 2000+ ASCII group codes.
- **Group Code Processing**:
  - Code `0`: Entity type (`LWPOLYLINE`, `POLYLINE`, `LINE`, `ARC`, `CIRCLE`).
  - Codes `10, 20`: Vertex $X$ and $Y$ coordinates.
  - Codes `8`: Layer names (`WALLS`, `DOORS`, `EGRESS`).
- **Entity Reconstruction**:
  - Reconstructs closed room boundary polygons from `LWPOLYLINE` on layer `WALLS`.
  - Reconstructs door frames and calculates hinge positions from `LINE` or `ARC` on layer `DOORS`.
  - Extracts egress path vectors from `LINE` on layer `EGRESS`.
- **Command-Line Interface**:
  ```bash
  python run.py --ingest-dxf OUTPUT/ROOM-01/plan.dxf --output OUTPUT
  ```

### 1.2 1:1 Scale DXF CAD Exporter (`rulebound/dxf_exporter.py`)
- Exports exact 1:1 scale drawings in millimeters.
- Organizes geometry across standardized CAD layers:
  - `ROOM_BOUNDARY`: Exterior room walls.
  - `DOORS`: Door openings and swing arcs.
  - `EGRESS_PATH`: Centerline and corridor safety envelope.
  - `FURNITURE_DESK`, `FURNITURE_CHAIR`, `FURNITURE_STORAGE`, `FURNITURE_COLLAB`: Footprint blocks.

---

## Bonus Track 2: Azure Container Apps & Microsoft Entra ID (+5 Bonus)

### 2.1 Cloud Architecture (`azure/main.bicep`)
- Declarative infrastructure-as-code written in Azure Bicep.
- Provisions:
  - Azure Container Registry (ACR) with Admin access.
  - Azure Container Apps Environment (Log Analytics workspace integration).
  - Azure Container App hosting the containerized RuleBound API with Managed Identity.

### 2.2 Microsoft Entra ID (Azure AD) Authentication (`azure/entra_auth.py`)
- Standard OAuth2 Bearer token authentication.
- Retrieves OpenID Connect metadata:
  `https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration`
- Validates JWT claims:
  - `iss`: Issuer matches Microsoft Entra ID tenant.
  - `aud`: Audience matches registered Application ID.
  - `exp`: Token is not expired.
  - `nbf`: Token is currently valid.

### 2.3 Production HTTP Service (`azure/app.py`)
- FastAPI REST service providing:
  - `GET /health`: Public liveness/readiness probe.
  - `GET /api/v1/quote/{room_id}`: Authenticated endpoint returning layout, quote, and traces.
  - `POST /api/v1/fitout`: Authenticated endpoint ingesting custom floorplans and briefs.
