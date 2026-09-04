from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rulebound.arbiter import arbitrate_layout
from rulebound.loader import load_asset_pack
from rulebound.models import Placement


class TestArbitration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.pack = load_asset_pack(cls.root / "data")

    def test_arbitration_repairs_nudgeable_violation(self):
        room = self.pack.rooms_by_id["ROOM-01"]
        # Placement placed at 80mm from south wall (needs 100mm)
        p = Placement(
            placement_id="P001",
            sku="NW-DES-001",  # 1200 x 600
            finish_id="F01",
            x_mm=3000,
            y_mm=380,  # bottom edge is at 380 - 300 = 80mm from wall (violation: <100mm)
            rotation_deg=0,
        )
        res = arbitrate_layout(room, [p], self.pack.catalog_by_sku, max_iterations=5)
        self.assertEqual(res.layout.status, "valid")
        self.assertEqual(res.final_energy, 0.0)
        self.assertLess(res.final_energy, res.initial_energy)
        self.assertGreaterEqual(res.iterations_run, 1)

    def test_arbitration_escalates_on_unsatisfiable_layout(self):
        room = self.pack.rooms_by_id["ROOM-01"]
        # Place 2 huge overlapping tables that cannot be moved or pruned within 1 iteration
        p1 = Placement("P001", "NW-COL-001", "F03", 3000, 3000, 0)
        p2 = Placement("P002", "NW-COL-001", "F03", 3000, 3000, 0)
        # With max_iterations=0, it cannot repair and must terminate immediately with unsatisfiable
        res = arbitrate_layout(room, [p1, p2], self.pack.catalog_by_sku, max_iterations=0)
        self.assertEqual(res.layout.status, "unsatisfiable")
        self.assertIsNotNone(res.escalation_report)
        self.assertIn("human_tradeoff_options", res.escalation_report)


if __name__ == "__main__":
    unittest.main()
