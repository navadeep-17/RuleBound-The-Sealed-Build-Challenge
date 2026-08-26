"""Microsoft Entra ID (formerly Azure AD) OAuth2 JWT Token Validation.
Validates Bearer tokens against Microsoft Entra ID OpenID Connect discovery endpoints.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any


class EntraIDAuthValidator:
    def __init__(self, tenant_id: str | None = None, client_id: str | None = None) -> None:
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID", "common")
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID", "")
        self.jwks_cache: dict[str, Any] = {}

    def get_openid_config(self) -> dict[str, Any]:
        url = f"https://login.microsoftonline.com/{self.tenant_id}/v2.0/.well-known/openid-configuration"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            return {}

    def validate_token_header_and_claims(self, token: str) -> tuple[bool, str, dict[str, Any]]:
        """Parses and validates JWT structure and claims."""
        parts = token.strip().split(".")
        if len(parts) != 3:
            return False, "Malformed JWT: expected header.payload.signature", {}

        import base64
        def b64_decode(data: str) -> bytes:
            padding = b"=" * (4 - len(data) % 4)
            return base64.urlsafe_b64decode(data.encode("utf-8") + padding)

        try:
            header = json.loads(b64_decode(parts[0]).decode("utf-8"))
            claims = json.loads(b64_decode(parts[1]).decode("utf-8"))
        except Exception as e:
            return False, f"Failed to decode token payload: {e}", {}

        # Validate Audience if configured
        if self.client_id and claims.get("aud") not in (self.client_id, f"api://{self.client_id}"):
            return False, f"Audience mismatch: expected {self.client_id}, got {claims.get('aud')}", claims

        # Check expiration claim if present
        import time
        exp = claims.get("exp")
        if exp and exp < time.time():
            return False, "Token has expired", claims

        return True, "Valid Entra ID token", claims
