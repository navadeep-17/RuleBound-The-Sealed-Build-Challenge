from __future__ import annotations

import unittest
from pathlib import Path

from rulebound.geometry import (
    get_rectangle_vertices,
    min_distance_to_boundary,
    polygon_inside_boundary,
    polygons_overlap_sat,
)
from rulebound.loader import load_asset_pack
from rulebound.models import Placement, RoomSpec
from rulebound.spatial_engine import validate_spatial_rules


class TestGeometryAndSpatialEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.pack = load_asset_pack(cls.root / "data")

    def test_rectangle_vertices_rotation(self):
        # 1000x500 at (0,0) unrotated
        rect = get_rectangle_vertices(0, 0, 1000, 500, 0)
        self.assertEqual(len(rect), 4)
        xs = [p[0] for p in rect]
        ys = [p[1] for p in rect]
        self.assertEqual(min(xs), -500)
        self.assertEqual(max(xs), 500)
        self.assertEqual(min(ys), -250)
        self.assertEqual(max(ys), 250)

        # Rotated 90 deg -> width along Y, depth along X
        rect90 = get_rectangle_vertices(0, 0, 1000, 500, 90)
        xs90 = [round(p[0]) for p in rect90]
        ys90 = [round(p[1]) for p in rect90]
        self.assertEqual(min(xs90), -250)
        self.assertEqual(max(xs90), 250)
        self.assertEqual(min(ys90), -500)
        self.assertEqual(max(ys90), 500)

    def test_overlap_sat(self):
        poly1 = get_rectangle_vertices(0, 0, 100, 100, 0)
        poly2 = get_rectangle_vertices(50, 0, 100, 100, 0)
        poly3 = get_rectangle_vertices(200, 0, 100, 100, 0)

        self.assertTrue(polygons_overlap_sat(poly1, poly2))
        self.assertFalse(polygons_overlap_sat(poly1, poly3))

    def test_room_boundary_containment(self):
        boundary = ((0, 0), (5000, 0), (5000, 5000), (0, 5000))
        inside = get_rectangle_vertices(2500, 2500, 1000, 1000, 0)
        outside = get_rectangle_vertices(5000, 2500, 1000, 1000, 0)

        self.assertTrue(polygon_inside_boundary(inside, boundary))
        self.assertFalse(polygon_inside_boundary(outside, boundary))

    def test_spatial_rule_violations(self):
        room = self.pack.rooms_by_id["ROOM-01"]
        # Placement overlapping wall (<100mm) and overlapping door swing
        p_bad = Placement(
            placement_id="P_BAD",
            sku="NW-DES-001",
            finish_id="F01",
            x_mm=500,  # right on top of door D1 (offset 500, width 1000)
            y_mm=200,  # too close to wall (<100mm wall offset)
            rotation_deg=0,
        )
        violations, energy = validate_spatial_rules(room, [p_bad], self.pack.catalog_by_sku)
        self.assertGreater(len(violations), 0)
        self.assertGreater(energy, 0.0)
        rule_ids = {v.rule_id for v in violations}
        self.assertTrue("RB-GEO-003" in rule_ids or "RB-GEO-005" in rule_ids)


if __name__ == "__main__":
    unittest.main()
