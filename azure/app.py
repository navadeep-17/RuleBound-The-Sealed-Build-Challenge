"""RuleBound Fit-Out Engine — Cloud API Service.
Deployable to Azure Container Apps or Azure App Service with Entra ID Authentication.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from azure.entra_auth import EntraIDAuthValidator
from rulebound.loader import load_asset_pack
from rulebound.generator import generate_layout_for_room
from rulebound.pricing_engine import aggregate_placements_to_lines, price_room_layout

# Initialize pack
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
pack = load_asset_pack(DATA_DIR)
auth_validator = EntraIDAuthValidator()


def handle_request(method: str, path: str, headers: dict[str, str], body: bytes) -> tuple[int, dict[str, str], dict[str, Any]]:
    """Lightweight WSGI/ASGI/HTTP handler without requiring heavy third-party web frameworks."""
    # Health check is public
    if path == "/health":
        return 200, {"Content-Type": "application/json"}, {"status": "healthy", "service": "rulebound-engine"}

    # Validate Entra ID token
    auth_header = headers.get("Authorization", headers.get("authorization", ""))
    if not auth_header.startswith("Bearer "):
        return 401, {"Content-Type": "application/json"}, {"error": "Missing or invalid Bearer token (Entra ID required)"}

    token = auth_header.split(" ", 1)[1]
    is_valid, msg, claims = auth_validator.validate_token_header_and_claims(token)
    if not is_valid:
        return 403, {"Content-Type": "application/json"}, {"error": f"Forbidden: {msg}"}

    # Authenticated Routes
    if path.startswith("/api/v1/quote/"):
        room_id = path.split("/")[-1]
        room = pack.rooms_by_id.get(room_id)
        if not room:
            return 404, {"Content-Type": "application/json"}, {"error": f"Room {room_id} not found"}

        layout = generate_layout_for_room(room, pack)
        if layout.status == "valid":
            lines = aggregate_placements_to_lines(layout.placements)
            quote = price_room_layout(room_id, lines, pack)
        else:
            quote = price_room_layout(room_id, [], pack)
            quote.blocking_reasons.extend([v.message for v in layout.violations])

        return 200, {"Content-Type": "application/json"}, {
            "layout": layout.to_dict(),
            "quote": quote.to_dict(),
            "authenticated_user": claims.get("preferred_username", claims.get("sub", "authorized_user")),
        }

    return 404, {"Content-Type": "application/json"}, {"error": "Endpoint not found"}
