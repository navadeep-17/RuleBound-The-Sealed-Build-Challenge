"""ANSI Terminal 2D Floorplan & Heatmap Visualizer for RuleBound.
Renders high-contrast, scaled ASCII/ANSI floorplans directly inside the terminal.
"""
from __future__ import annotations

import math
from typing import Sequence

from rulebound.models import CatalogItem, Placement, RoomSpec, Violation
from rulebound.geometry import point_to_segment_distance, point_in_polygon


def render_terminal_floorplan(
    room: RoomSpec,
    placements: list[Placement],
    catalog: dict[str, CatalogItem],
    violations: list[Violation] | None = None,
    cols: int = 70,
    rows: int = 26,
) -> str:
    """Renders an ANSI color 2D top-down floorplan to a string for terminal display."""
    min_x = min(pt[0] for pt in room.boundary_mm)
    max_x = max(pt[0] for pt in room.boundary_mm)
    min_y = min(pt[1] for pt in room.boundary_mm)
    max_y = max(pt[1] for pt in room.boundary_mm)

    w_room = max(1, max_x - min_x)
    h_room = max(1, max_y - min_y)

    grid = [["  " for _ in range(cols)] for _ in range(rows)]

    # Coordinate mapping: mm -> (c, r)
    def to_grid(x: float, y: float) -> tuple[int, int]:
        c = int((x - min_x) / w_room * (cols - 1))
        r = rows - 1 - int((y - min_y) / h_room * (rows - 1))
        return (max(0, min(cols - 1, c)), max(0, min(rows - 1, r)))

    # 1. Draw Egress Corridor
    if room.doors:
        door = next((d for d in room.doors if d.door_id == room.egress.from_door_id), room.doors[0])
        # Door center
        d_x = door.offset_mm + door.width_mm / 2.0
        p1 = (d_x, 0.0) if door.wall == "south" else (d_x, float(h_room))
        p2 = (float(room.egress.to_point_mm[0]), float(room.egress.to_point_mm[1]))
        half_w = room.egress.min_width_mm / 2.0

        for r in range(rows):
            for c in range(cols):
                gx = min_x + (c / (cols - 1)) * w_room
                gy = min_y + ((rows - 1 - r) / (rows - 1)) * h_room
                if point_to_segment_distance((gx, gy), p1, p2) <= half_w:
                    grid[r][c] = "\033[90m..\033[0m"

    # 2. Draw Room Boundary
    b_pts = list(room.boundary_mm)
    for i in range(len(b_pts)):
        p_start = b_pts[i]
        p_end = b_pts[(i + 1) % len(b_pts)]
        steps = 50
        for s in range(steps + 1):
            t = s / steps
            bx = p_start[0] + t * (p_end[0] - p_start[0])
            by = p_start[1] + t * (p_end[1] - p_start[1])
            gc, gr = to_grid(bx, by)
            grid[gr][gc] = "\033[96m##\033[0m"

    # 3. Draw Doors
    for door in room.doors:
        d_center = door.offset_mm + door.width_mm / 2.0
        dc, dr = to_grid(d_center, 0 if door.wall == "south" else h_room)
        grid[dr][dc] = "\033[93mDD\033[0m"

    # 4. Draw Furniture Placements
    viol_pids = {pid for v in (violations or []) for pid in v.affected_placement_ids}

    for p in placements:
        item = catalog.get(p.sku)
        fam = item.family if item else "unknown"
        gc, gr = to_grid(p.x_mm, p.y_mm)

        if p.placement_id in viol_pids:
            symbol = "\033[91;1mXX\033[0m"
        elif fam == "desk":
            symbol = "\033[94m[]\033[0m"
        elif fam == "chair":
            symbol = "\033[33moo\033[0m"
        elif fam == "collaboration":
            symbol = "\033[92m<>\033[0m"
        elif fam == "storage":
            symbol = "\033[95m$$\033[0m"
        else:
            symbol = "\033[36m**\033[0m"

        grid[gr][gc] = symbol

    # Build Output String
    border_horiz = "-" * (cols * 2 + 2)
    lines = [
        f"\n\033[1m+{border_horiz}+\033[0m",
        f"\033[1m| {room.name} ({room.room_id}) - Scaled 2D Top-Down View".ljust(cols * 2 + 3) + "|\033[0m",
        f"\033[1m+{border_horiz}+\033[0m",
    ]
    for row in grid:
        lines.append("| " + "".join(row) + " |")
    lines.append(f"\033[1m+{border_horiz}+\033[0m")
    lines.append(
        " \033[96m##\033[0m Wall   \033[93mDD\033[0m Door   \033[90m..\033[0m Egress   \033[94m[]\033[0m Desk   \033[33moo\033[0m Chair   \033[92m<>\033[0m Collab   \033[95m$$\033[0m Storage   \033[91;1mXX\033[0m Violation\n"
    )
    return "\n".join(lines)
