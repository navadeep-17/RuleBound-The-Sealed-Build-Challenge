"""Deterministic SVG floorplan exporter for Northwind Furnishings fit-outs.
Generates an interactive, beautiful 2D vector CAD preview viewable in any modern web browser.
"""

from __future__ import annotations

import math
from rulebound.models import CatalogItem, Layout, RoomSpec
from rulebound.geometry import get_rectangle_vertices


def export_room_svg(
    room: RoomSpec,
    layout: Layout,
    catalog_by_sku: dict[str, CatalogItem],
    target_path: str,
) -> None:
    """Exports a deterministic SVG floorplan for the given room and layout."""
    # Find bounding box of room to compute SVG viewBox
    min_x = min(pt[0] for pt in room.boundary_mm)
    max_x = max(pt[0] for pt in room.boundary_mm)
    min_y = min(pt[1] for pt in room.boundary_mm)
    max_y = max(pt[1] for pt in room.boundary_mm)

    pad = 600
    vb_x = min_x - pad
    vb_y = min_y - pad
    vb_w = (max_x - min_x) + 2 * pad
    vb_h = (max_y - min_y) + 2 * pad

    # We use Cartesian coordinates: flip Y so +Y is up
    # In SVG, Y is down, so we use a transform: translate(0, max_y + min_y) scale(1, -1)
    svg_lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x} {vb_y} {vb_w} {vb_h}" width="100%" height="100%" style="background:#0f172a; font-family:system-ui, -apple-system, sans-serif;">',
        '  <defs>',
        '    <pattern id="grid" width="500" height="500" patternUnits="userSpaceOnUse">',
        '      <path d="M 500 0 L 0 0 0 500" fill="none" stroke="#1e293b" stroke-width="15"/>',
        '    </pattern>',
        '    <linearGradient id="egressGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#10b981" stop-opacity="0.25"/>',
        '      <stop offset="100%" stop-color="#059669" stop-opacity="0.15"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect x="{vb_x}" y="{vb_y}" width="{vb_w}" height="{vb_h}" fill="url(#grid)"/>',
    ]

    # Helper to flip Y coordinate for standard CAD view (Y=0 at bottom)
    def svg_y(y: float) -> float:
        return max_y - y + min_y

    # 1. Draw Egress Corridor
    if room.egress:
        eg = room.egress
        door = next((d for d in room.doors if d.door_id == eg.from_door_id), None)
        if door:
            if door.wall == "south":
                sx, sy = (door.offset_mm + door.width_mm / 2.0, float(min_y))
            elif door.wall == "north":
                sx, sy = (door.offset_mm + door.width_mm / 2.0, float(max_y))
            elif door.wall == "west":
                sx, sy = (float(min_x), door.offset_mm + door.width_mm / 2.0)
            else:
                sx, sy = (float(max_x), door.offset_mm + door.width_mm / 2.0)

            gx, gy = float(eg.to_point_mm[0]), float(eg.to_point_mm[1])
            hw = eg.min_width_mm / 2.0
            dx = gx - sx
            dy = gy - sy
            dist = math.hypot(dx, dy)
            if dist > 0:
                nx = -dy / dist * hw
                ny = dx / dist * hw
                p1 = (sx + nx, svg_y(sy + ny))
                p2 = (gx + nx, svg_y(gy + ny))
                p3 = (gx - nx, svg_y(gy - ny))
                p4 = (sx - nx, svg_y(sy - ny))
                poly_pts = f"{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f} {p4[0]:.1f},{p4[1]:.1f}"
                svg_lines.append('  <!-- Egress Path -->')
                svg_lines.append(f'  <polygon points="{poly_pts}" fill="url(#egressGrad)" stroke="#10b981" stroke-width="20" stroke-dasharray="100,50"/>')
                svg_lines.append(f'  <line x1="{sx:.1f}" y1="{svg_y(sy):.1f}" x2="{gx:.1f}" y2="{svg_y(gy):.1f}" stroke="#34d399" stroke-width="25" stroke-dasharray="80,40"/>')

    # 2. Draw Room Boundary
    b_pts = " ".join(f"{pt[0]:.1f},{svg_y(pt[1]):.1f}" for pt in room.boundary_mm)
    svg_lines.append('  <!-- Room Boundary -->')
    svg_lines.append(f'  <polygon points="{b_pts}" fill="#1e293b" fill-opacity="0.5" stroke="#94a3b8" stroke-width="80" stroke-linejoin="round"/>')

    # 3. Draw Windows
    for win in room.windows:
        wall = win.wall.lower()
        if wall == "north":
            y = svg_y(max_y)
            svg_lines.append(f'  <line x1="{win.offset_mm:.1f}" y1="{y:.1f}" x2="{(win.offset_mm + win.width_mm):.1f}" y2="{y:.1f}" stroke="#38bdf8" stroke-width="120" stroke-linecap="square"/>')
        elif wall == "south":
            y = svg_y(min_y)
            svg_lines.append(f'  <line x1="{win.offset_mm:.1f}" y1="{y:.1f}" x2="{(win.offset_mm + win.width_mm):.1f}" y2="{y:.1f}" stroke="#38bdf8" stroke-width="120" stroke-linecap="square"/>')
        elif wall == "east":
            x = max_x
            svg_lines.append(f'  <line x1="{x:.1f}" y1="{svg_y(win.offset_mm):.1f}" x2="{x:.1f}" y2="{svg_y(win.offset_mm + win.width_mm):.1f}" stroke="#38bdf8" stroke-width="120" stroke-linecap="square"/>')
        elif wall == "west":
            x = min_x
            svg_lines.append(f'  <line x1="{x:.1f}" y1="{svg_y(win.offset_mm):.1f}" x2="{x:.1f}" y2="{svg_y(win.offset_mm + win.width_mm):.1f}" stroke="#38bdf8" stroke-width="120" stroke-linecap="square"/>')

    # 4. Draw Doors
    for door in room.doors:
        wall = door.wall.lower()
        if wall == "south":
            y = svg_y(min_y)
            svg_lines.append(f'  <line x1="{door.offset_mm:.1f}" y1="{y:.1f}" x2="{(door.offset_mm + door.width_mm):.1f}" y2="{y:.1f}" stroke="#f59e0b" stroke-width="140" stroke-linecap="round"/>')
        elif wall == "north":
            y = svg_y(max_y)
            svg_lines.append(f'  <line x1="{door.offset_mm:.1f}" y1="{y:.1f}" x2="{(door.offset_mm + door.width_mm):.1f}" y2="{y:.1f}" stroke="#f59e0b" stroke-width="140" stroke-linecap="round"/>')
        elif wall == "west":
            x = min_x
            svg_lines.append(f'  <line x1="{x:.1f}" y1="{svg_y(door.offset_mm):.1f}" x2="{x:.1f}" y2="{svg_y(door.offset_mm + door.width_mm):.1f}" stroke="#f59e0b" stroke-width="140" stroke-linecap="round"/>')
        elif wall == "east":
            x = max_x
            svg_lines.append(f'  <line x1="{x:.1f}" y1="{svg_y(door.offset_mm):.1f}" x2="{x:.1f}" y2="{svg_y(door.offset_mm + door.width_mm):.1f}" stroke="#f59e0b" stroke-width="140" stroke-linecap="round"/>')

    # 5. Draw Furniture Placements
    color_map = {
        "desk": ("#3b82f6", "#1d4ed8"),
        "chair": ("#f97316", "#c2410c"),
        "storage": ("#8b5cf6", "#6d28d9"),
        "collaboration": ("#10b981", "#047857"),
        "accessory": ("#ec4899", "#be185d"),
    }

    svg_lines.append('  <!-- Furniture Placements -->')
    for p in layout.placements:
        item = catalog_by_sku.get(p.sku)
        w = item.width_mm if item else 600
        d = item.depth_mm if item else 600
        fam = item.family if item else "desk"
        fill_col, stroke_col = color_map.get(fam, ("#64748b", "#475569"))

        corners = get_rectangle_vertices(p.x_mm, p.y_mm, w, d, p.rotation_deg)
        f_pts = " ".join(f"{pt[0]:.1f},{svg_y(pt[1]):.1f}" for pt in corners)

        svg_lines.append(f'  <g id="{p.placement_id}">')
        svg_lines.append(f'    <polygon points="{f_pts}" fill="{fill_col}" fill-opacity="0.8" stroke="{stroke_col}" stroke-width="25" rx="20"/>')
        # Centered label
        c_y = svg_y(p.y_mm)
        font_size = 140 if fam in ("desk", "collaboration") else 100
        svg_lines.append(f'    <text x="{p.x_mm:.1f}" y="{(c_y + font_size / 3):.1f}" fill="#ffffff" font-size="{font_size}" font-weight="bold" text-anchor="middle">{p.placement_id}</text>')
        svg_lines.append(f'  </g>')

    # Title & Room Info
    svg_lines.append('  <!-- Room Title -->')
    svg_lines.append(f'  <text x="{min_x + 100}" y="{svg_y(max_y - 250)}" fill="#f8fafc" font-size="280" font-weight="bold">{room.name} ({room.room_id})</text>')
    svg_lines.append(f'  <text x="{min_x + 100}" y="{svg_y(max_y - 550)}" fill="#94a3b8" font-size="160">Status: {layout.status.upper()} | Placements: {len(layout.placements)} | Violations: {len(layout.violations)}</text>')

    svg_lines.append('</svg>\n')

    with open(target_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
