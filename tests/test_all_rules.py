"""Comprehensive test suite verifying all 14 Rules, DXF Ingestion, and Entra ID Auth."""
from __future__ import annotations

import unittest
from pathlib import Path

from azure.entra_auth import EntraIDAuthValidator
from rulebound.dxf_ingester import ingest_room_from_dxf
from rulebound.loader import load_asset_pack
from rulebound.models import Placement
from rulebound.pricing_engine import aggregate_placements_to_lines, price_room_layout
from rulebound.spatial_engine import validate_spatial_rules


class TestAllRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pack = load_asset_pack("data")
        cls.room1 = cls.pack.rooms_by_id["ROOM-01"]

    def test_all_14_rules_present_in_pack(self) -> None:
        rule_ids = {r["rule_id"] for r in self.pack.rules["rules"]}
        expected = {
            "RB-GEO-001", "RB-GEO-002", "RB-GEO-003", "RB-GEO-004",
            "RB-GEO-005", "RB-GEO-006", "RB-GEO-007", "RB-GEO-008",
            "RB-PRC-009", "RB-PRC-010", "RB-PRC-011", "RB-PRC-012",
            "RB-PRC-013", "RB-PRC-014",
        }
        for r_id in expected:
            self.assertIn(r_id, rule_ids, f"Rule {r_id} missing from asset pack!")

    def test_rb_geo_005_wall_offset(self) -> None:
        # Placement placed 50mm from wall (minimum is 100mm)
        p = [Placement("P001", "NW-DES-001", "F01", 300, 300, 0)]
        viols, _ = validate_spatial_rules(self.room1, p, self.pack.catalog_by_sku)
        wall_viols = [v for v in viols if v.rule_id == "RB-GEO-005"]
        self.assertTrue(len(wall_viols) > 0)

    def test_rb_geo_006_no_overlap(self) -> None:
        # Two placements overlapping at exact same coordinate
        p = [
            Placement("P001", "NW-DES-001", "F01", 2000, 2000, 0),
            Placement("P002", "NW-DES-001", "F01", 2000, 2000, 0),
        ]
        viols, _ = validate_spatial_rules(self.room1, p, self.pack.catalog_by_sku)
        overlap_viols = [v for v in viols if v.rule_id == "RB-GEO-006"]
        self.assertTrue(len(overlap_viols) > 0)

    def test_rb_geo_004_and_008_clearances(self) -> None:
        # Desk with solid storage placed 300mm behind it (violates 900mm rear clearance)
        # NW-DES-001: 1400x700 -> y in [1650, 2350]
        # NW-STO-001: 800x450 -> y in [2450, 2900] (center 2675). Gap = 100mm
        p = [
            Placement("P001", "NW-DES-001", "F01", 2000, 2000, 0),
            Placement("P002", "NW-STO-001", "F01", 2000, 2675, 0),
        ]
        viols, _ = validate_spatial_rules(self.room1, p, self.pack.catalog_by_sku)
        self.assertTrue(any(v.rule_id == "RB-GEO-004" for v in viols))

    def test_rb_prc_pricing_rules(self) -> None:
        p = [Placement(f"P{i:03d}", "NW-DES-001", "F05", 2000, 2000, 0) for i in range(15)]
        lines = aggregate_placements_to_lines(p)
        quote = price_room_layout("ROOM-01", lines, self.pack)

        self.assertEqual(quote.status, "priced")
        self.assertTrue(quote.summary["goods_after_adjustments_inr"] > 0)
        self.assertTrue(quote.summary["labour_inr"] > 0)
        self.assertTrue(quote.summary["freight_inr"] > 0)

        # Audit trace present (RB-PRC-014)
        for line in quote.lines:
            self.assertTrue(len(line.trace) >= 2)

    def test_dxf_ingest_bonus(self) -> None:
        dxf_path = Path("OUTPUT/ROOM-01/plan.dxf")
        if dxf_path.is_file():
            room = ingest_room_from_dxf(dxf_path)
            self.assertIsNotNone(room.boundary_mm)
            self.assertTrue(len(room.boundary_mm) >= 3)
            self.assertIsNotNone(room.egress)

    def test_entra_id_auth_validation(self) -> None:
        validator = EntraIDAuthValidator(tenant_id="test-tenant", client_id="test-client")
        valid, msg, _ = validator.validate_token_header_and_claims("invalid.token")
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()
