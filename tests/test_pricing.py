from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rulebound.loader import load_asset_pack
from rulebound.pricing_engine import price_room_layout


class TestPricingEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.pack = load_asset_pack(cls.root / "data")

    def test_reconcile_ref_quote_01(self):
        ref_path = self.root / "data/reference_quotes/REF-QUOTE-01.json"
        ref_data = json.loads(ref_path.read_text(encoding="utf-8"))

        specs = [(line["sku"], line["finish_id"], line["quantity"]) for line in ref_data["lines"]]
        calculated = price_room_layout("ROOM-01", specs, self.pack, quote_id="REF-QUOTE-01")
        calc_dict = calculated.to_dict()

        self.assertEqual(calc_dict["status"], "priced")
        self.assertEqual(calc_dict["summary"]["grand_total_inr"], ref_data["summary"]["grand_total_inr"])
        self.assertEqual(calc_dict["summary"]["goods_after_adjustments_inr"], ref_data["summary"]["goods_after_adjustments_inr"])
        self.assertEqual(calc_dict["summary"]["labour_inr"], ref_data["summary"]["labour_inr"])
        self.assertEqual(calc_dict["summary"]["freight_inr"], ref_data["summary"]["freight_inr"])

        for ref_line, calc_line in zip(ref_data["lines"], calc_dict["lines"]):
            self.assertEqual(calc_line["sku"], ref_line["sku"])
            self.assertEqual(calc_line["unit_list_price_inr"], ref_line["unit_list_price_inr"])
            self.assertEqual(calc_line["base_amount_inr"], ref_line["base_amount_inr"])
            self.assertEqual(calc_line["finish_uplift_inr"], ref_line["finish_uplift_inr"])
            self.assertEqual(calc_line["quantity_discount_inr"], ref_line["quantity_discount_inr"])
            self.assertEqual(calc_line["net_goods_inr"], ref_line["net_goods_inr"])
            self.assertEqual(calc_line["trace"], ref_line["trace"])

    def test_reconcile_ref_quote_02(self):
        ref_path = self.root / "data/reference_quotes/REF-QUOTE-02.json"
        ref_data = json.loads(ref_path.read_text(encoding="utf-8"))

        specs = [(line["sku"], line["finish_id"], line["quantity"]) for line in ref_data["lines"]]
        calculated = price_room_layout("ROOM-02", specs, self.pack, quote_id="REF-QUOTE-02")
        calc_dict = calculated.to_dict()

        self.assertEqual(calc_dict["status"], "priced")
        self.assertEqual(calc_dict["summary"]["grand_total_inr"], ref_data["summary"]["grand_total_inr"])
        self.assertEqual(calc_dict["summary"]["goods_after_adjustments_inr"], ref_data["summary"]["goods_after_adjustments_inr"])
        self.assertEqual(calc_dict["summary"]["labour_inr"], ref_data["summary"]["labour_inr"])
        self.assertEqual(calc_dict["summary"]["freight_inr"], ref_data["summary"]["freight_inr"])

        for ref_line, calc_line in zip(ref_data["lines"], calc_dict["lines"]):
            self.assertEqual(calc_line["sku"], ref_line["sku"])
            self.assertEqual(calc_line["unit_list_price_inr"], ref_line["unit_list_price_inr"])
            self.assertEqual(calc_line["base_amount_inr"], ref_line["base_amount_inr"])
            self.assertEqual(calc_line["finish_uplift_inr"], ref_line["finish_uplift_inr"])
            self.assertEqual(calc_line["quantity_discount_inr"], ref_line["quantity_discount_inr"])
            self.assertEqual(calc_line["net_goods_inr"], ref_line["net_goods_inr"])
            self.assertEqual(calc_line["trace"], ref_line["trace"])

    def test_blocking_on_incompatible_finish(self):
        # Chair finish F18 (Leather) applied to desk NW-DES-001
        specs = [("NW-DES-001", "F18", 1)]
        quote = price_room_layout("ROOM-TEST", specs, self.pack)
        self.assertEqual(quote.status, "blocked")
        self.assertTrue(any("incompatible" in r for r in quote.blocking_reasons))
        self.assertEqual(quote.summary["grand_total_inr"], 0)

    def test_blocking_on_unknown_sku(self):
        specs = [("NON-EXISTENT-SKU", "F01", 1)]
        quote = price_room_layout("ROOM-TEST", specs, self.pack)
        self.assertEqual(quote.status, "blocked")
        self.assertTrue(any("not present in catalog" in r for r in quote.blocking_reasons))


if __name__ == "__main__":
    unittest.main()
