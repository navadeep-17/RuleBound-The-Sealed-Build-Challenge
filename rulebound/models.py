from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class CatalogItem:
    sku: str
    family: str
    name: str
    width_mm: int
    depth_mm: int
    height_mm: int
    list_price_inr: int
    labour_minutes: int
    lead_time_days: int
    compatible_finish_ids: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CatalogItem:
        dims = data.get("dimensions_mm", {})
        return cls(
            sku=data["sku"],
            family=data["family"],
            name=data.get("name", data["sku"]),
            width_mm=int(dims.get("width", 0)),
            depth_mm=int(dims.get("depth", 0)),
            height_mm=int(dims.get("height", 0)),
            list_price_inr=int(data["list_price_inr"]),
            labour_minutes=int(data["labour_minutes"]),
            lead_time_days=int(data.get("lead_time_days", 0)),
            compatible_finish_ids=tuple(data.get("compatible_finish_ids", [])),
        )


@dataclass(frozen=True)
class Finish:
    finish_id: str
    name: str
    uplift_bps: int
    compatible_families: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Finish:
        return cls(
            finish_id=data["finish_id"],
            name=data["name"],
            uplift_bps=int(data["uplift_bps"]),
            compatible_families=tuple(data.get("compatible_families", [])),
        )


@dataclass(frozen=True)
class Door:
    door_id: str
    wall: str  # "north" | "south" | "east" | "west"
    offset_mm: int
    width_mm: int
    swing: str  # "inward_left" | "inward_right" | "outward_left" | "outward_right"


@dataclass(frozen=True)
class Window:
    wall: str
    offset_mm: int
    width_mm: int


@dataclass(frozen=True)
class Egress:
    from_door_id: str
    to_point_mm: tuple[int, int]
    min_width_mm: int


@dataclass(frozen=True)
class RoomSpec:
    room_id: str
    name: str
    boundary_mm: tuple[tuple[int, int], ...]
    doors: tuple[Door, ...]
    windows: tuple[Window, ...]
    egress: Egress
    capacity: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RoomSpec:
        doors = tuple(
            Door(
                door_id=d["door_id"],
                wall=d["wall"],
                offset_mm=int(d["offset_mm"]),
                width_mm=int(d["width_mm"]),
                swing=d["swing"],
            )
            for d in data.get("doors", [])
        )
        windows = tuple(
            Window(
                wall=w["wall"],
                offset_mm=int(w["offset_mm"]),
                width_mm=int(w["width_mm"]),
            )
            for w in data.get("windows", [])
        )
        egress_data = data["egress"]
        egress = Egress(
            from_door_id=egress_data["from_door_id"],
            to_point_mm=(int(egress_data["to_point_mm"][0]), int(egress_data["to_point_mm"][1])),
            min_width_mm=int(egress_data.get("min_width_mm", 1100)),
        )
        boundary = tuple((int(pt[0]), int(pt[1])) for pt in data["boundary_mm"])
        return cls(
            room_id=data["room_id"],
            name=data.get("name", data["room_id"]),
            boundary_mm=boundary,
            doors=doors,
            windows=windows,
            egress=egress,
            capacity=int(data["capacity"]),
        )


@dataclass
class Placement:
    placement_id: str
    sku: str
    finish_id: str
    x_mm: int
    y_mm: int
    rotation_deg: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "placement_id": self.placement_id,
            "sku": self.sku,
            "finish_id": self.finish_id,
            "x_mm": self.x_mm,
            "y_mm": self.y_mm,
            "rotation_deg": self.rotation_deg,
        }


@dataclass
class ProposedLayout:
    """Strongly-typed forward contract crossing the seam: Generative Layer -> Deterministic Arbiter."""
    room_id: str
    placements: list[Placement]

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "placements": [p.to_dict() for p in self.placements],
        }


@dataclass
class Violation:
    violation_id: str
    rule_id: str
    message: str
    affected_placement_ids: list[str]
    measured: dict[str, Any] = field(default_factory=dict)
    required: dict[str, Any] = field(default_factory=dict)
    repair_options: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "message": self.message,
            "affected_placement_ids": list(self.affected_placement_ids),
            "repair_options": self.repair_options,
        }
        if self.measured:
            res["measured"] = self.measured
        if self.required:
            res["required"] = self.required
        return res


@dataclass
class Layout:
    room_id: str
    placements: list[Placement]
    violations: list[Violation]
    status: Literal["valid", "invalid", "unsatisfiable"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "placements": [p.to_dict() for p in self.placements],
            "violations": [v.to_dict() for v in self.violations],
            "status": self.status,
        }


@dataclass
class QuoteLineTrace:
    rule_id: str
    inputs: dict[str, Any]
    amount_inr: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "inputs": self.inputs,
            "amount_inr": self.amount_inr,
        }


@dataclass
class QuoteLine:
    line_id: str
    sku: str
    finish_id: str
    quantity: int
    unit_list_price_inr: int
    base_amount_inr: int
    finish_uplift_inr: int
    quantity_discount_inr: int
    net_goods_inr: int
    trace: list[QuoteLineTrace]

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_id": self.line_id,
            "sku": self.sku,
            "finish_id": self.finish_id,
            "quantity": self.quantity,
            "unit_list_price_inr": self.unit_list_price_inr,
            "base_amount_inr": self.base_amount_inr,
            "finish_uplift_inr": self.finish_uplift_inr,
            "quantity_discount_inr": self.quantity_discount_inr,
            "net_goods_inr": self.net_goods_inr,
            "trace": [t.to_dict() for t in self.trace],
        }


@dataclass
class SummaryTrace:
    rule_id: str
    inputs: dict[str, Any]
    amount_inr: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "inputs": self.inputs,
            "amount_inr": self.amount_inr,
        }


@dataclass
class Quote:
    quote_id: str
    room_id: str
    currency: str
    lines: list[QuoteLine]
    summary: dict[str, Any]
    summary_trace: list[SummaryTrace]
    status: Literal["priced", "blocked"]
    blocking_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = {
            "quote_id": self.quote_id,
            "room_id": self.room_id,
            "currency": self.currency,
            "lines": [l.to_dict() for l in self.lines],
            "summary": self.summary,
            "summary_trace": [t.to_dict() for t in self.summary_trace],
            "status": self.status,
        }
        if self.blocking_reasons:
            res["blocking_reasons"] = list(self.blocking_reasons)
        return res
