from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from rulebound.loader import AssetPack
from rulebound.models import (
    CatalogItem,
    Finish,
    Placement,
    Quote,
    QuoteLine,
    QuoteLineTrace,
    SummaryTrace,
)


def round_half_up(value: Decimal | int | float) -> int:
    """Rounds half up to the nearest integer as specified in PRICING_SPEC.md."""
    d = Decimal(str(value)) if not isinstance(value, Decimal) else value
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def get_quantity_discount_bps(quantity: int) -> int:
    """Rule RB-PRC-009: Quantity discount tiers.
    1-4: 0 bps
    5-9: 300 bps
    10-19: 700 bps
    20+: 1000 bps
    """
    if quantity >= 20:
        return 1000
    if quantity >= 10:
        return 700
    if quantity >= 5:
        return 300
    return 0


def get_labour_rate_per_hour(minutes: int) -> int:
    """Rule RB-PRC-011: Labour bands.
    Up to 240 minutes: 900 INR/hour
    241 - 480 minutes: 800 INR/hour
    Above 480 minutes: 750 INR/hour
    """
    if minutes <= 240:
        return 900
    if minutes <= 480:
        return 800
    return 750


def calculate_freight(net_goods_inr: int) -> tuple[int, dict[str, Any]]:
    """Rule RB-PRC-012: Freight band on net goods.
    Up to 100,000 INR: flat 5,000 INR
    100,001 - 250,000 INR: flat 9,000 INR
    Above 250,000 INR: 4% of net goods (400 bps), round half up
    """
    if net_goods_inr <= 100000:
        return 5000, {"band": "up_to_100000", "flat_inr": 5000, "goods_inr": net_goods_inr}
    if net_goods_inr <= 250000:
        return 9000, {"band": "100001_to_250000", "flat_inr": 9000, "goods_inr": net_goods_inr}

    amount = round_half_up(Decimal(net_goods_inr) * Decimal(400) / Decimal(10000))
    return amount, {
        "band": "above_250000",
        "percent_bps": 400,
        "goods_inr": net_goods_inr,
    }


def aggregate_placements_to_lines(placements: list[Placement]) -> list[tuple[str, str, int]]:
    """Aggregates individual placements into unique (sku, finish_id, quantity) tuples,
    sorted deterministically by SKU then finish_id."""
    counts: dict[tuple[str, str], int] = {}
    for p in placements:
        key = (p.sku, p.finish_id)
        counts[key] = counts.get(key, 0) + 1

    return [(sku, finish_id, count) for (sku, finish_id), count in sorted(counts.items())]


def price_room_layout(
    room_id: str,
    line_specs: list[tuple[str, str, int]],
    pack: AssetPack,
    quote_id: str | None = None,
) -> Quote:
    """Calculates a fully deterministic, line-traceable quote.
    
    If any SKU is uncatalogued or any finish is incompatible, blocks the quote under RB-PRC-013.
    """
    q_id = quote_id or f"QUOTE-{room_id}"
    lines: list[QuoteLine] = []
    blocking_reasons: list[str] = []
    total_labour_minutes = 0

    for idx, (sku, finish_id, quantity) in enumerate(line_specs, start=1):
        line_id = f"L{idx:03d}"
        item: CatalogItem | None = pack.catalog_by_sku.get(sku)
        finish: Finish | None = pack.finishes_by_id.get(finish_id)

        if not item:
            blocking_reasons.append(f"SKU {sku} on line {line_id} is not present in catalog (RB-PRC-013).")
            continue

        if not finish:
            blocking_reasons.append(f"Finish {finish_id} on line {line_id} is not present in finishes (RB-PRC-013).")
            continue

        # Check finish compatibility both ways
        if finish_id not in item.compatible_finish_ids or item.family not in finish.compatible_families:
            blocking_reasons.append(
                f"Finish {finish_id} is incompatible with SKU {sku} ({item.family}) on line {line_id} (RB-PRC-013)."
            )

        unit_list_price = item.list_price_inr
        base_amount = unit_list_price * quantity
        uplift_bps = finish.uplift_bps
        finish_uplift = round_half_up(Decimal(base_amount) * Decimal(uplift_bps) / Decimal(10000))

        discount_bps = get_quantity_discount_bps(quantity)
        quantity_discount = round_half_up(Decimal(base_amount) * Decimal(discount_bps) / Decimal(10000))

        net_goods = base_amount + finish_uplift - quantity_discount

        total_labour_minutes += item.labour_minutes * quantity

        trace = [
            QuoteLineTrace(
                rule_id="CATALOG",
                inputs={"unit_price": unit_list_price, "quantity": quantity},
                amount_inr=base_amount,
            ),
            QuoteLineTrace(
                rule_id="RB-PRC-010",
                inputs={"uplift_bps": uplift_bps, "base_amount_inr": base_amount},
                amount_inr=finish_uplift,
            ),
            QuoteLineTrace(
                rule_id="RB-PRC-009",
                inputs={"discount_bps": discount_bps, "base_amount_inr": base_amount},
                amount_inr=-quantity_discount,
            ),
        ]

        lines.append(
            QuoteLine(
                line_id=line_id,
                sku=sku,
                finish_id=finish_id,
                quantity=quantity,
                unit_list_price_inr=unit_list_price,
                base_amount_inr=base_amount,
                finish_uplift_inr=finish_uplift,
                quantity_discount_inr=quantity_discount,
                net_goods_inr=net_goods,
                trace=trace,
            )
        )

    if blocking_reasons or not lines:
        if not lines and not blocking_reasons:
            blocking_reasons.append("Layout contains zero valid furniture placements.")
        return Quote(
            quote_id=q_id,
            room_id=room_id,
            currency="INR",
            lines=lines,
            summary={"grand_total_inr": 0},
            summary_trace=[],
            status="blocked",
            blocking_reasons=blocking_reasons,
        )

    goods_after_adjustments = sum(l.net_goods_inr for l in lines)
    labour_rate_per_hour = get_labour_rate_per_hour(total_labour_minutes)
    labour_inr = round_half_up(Decimal(total_labour_minutes) * Decimal(labour_rate_per_hour) / Decimal(60))

    freight_inr, freight_inputs = calculate_freight(goods_after_adjustments)
    grand_total_inr = goods_after_adjustments + labour_inr + freight_inr

    summary = {
        "goods_after_adjustments_inr": goods_after_adjustments,
        "labour_minutes": total_labour_minutes,
        "labour_rate_inr_per_hour": labour_rate_per_hour,
        "labour_inr": labour_inr,
        "freight_inr": freight_inr,
        "grand_total_inr": grand_total_inr,
    }

    summary_trace = [
        SummaryTrace(
            rule_id="RB-PRC-011",
            inputs={"total_labour_minutes": total_labour_minutes, "rate_inr_per_hour": labour_rate_per_hour},
            amount_inr=labour_inr,
        ),
        SummaryTrace(
            rule_id="RB-PRC-012",
            inputs=freight_inputs,
            amount_inr=freight_inr,
        ),
    ]

    return Quote(
        quote_id=q_id,
        room_id=room_id,
        currency="INR",
        lines=lines,
        summary=summary,
        summary_trace=summary_trace,
        status="priced",
        blocking_reasons=[],
    )
