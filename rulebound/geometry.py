from __future__ import annotations

import math
from typing import Sequence

Point = tuple[float, float]
Polygon = list[Point]


def rotate_point(x: float, y: float, rad: float) -> Point:
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)


def get_rectangle_vertices(
    center_x: float,
    center_y: float,
    width: float,
    depth: float,
    rotation_deg: float = 0.0,
) -> Polygon:
    """Returns 4 vertices of a rectangle centered at (center_x, center_y),
    rotated clockwise/counter-clockwise by rotation_deg."""
    rad = math.radians(rotation_deg)
    hw, hd = width / 2.0, depth / 2.0
    corners = [
        (-hw, -hd),
        (hw, -hd),
        (hw, hd),
        (-hw, hd),
    ]
    vertices: Polygon = []
    for cx, cy in corners:
        rx, ry = rotate_point(cx, cy, rad)
        vertices.append((center_x + rx, center_y + ry))
    return vertices


def dot_product(p1: Point, p2: Point) -> float:
    return p1[0] * p2[0] + p1[1] * p2[1]


def distance_sq(p1: Point, p2: Point) -> float:
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return dx * dx + dy * dy


def distance(p1: Point, p2: Point) -> float:
    return math.sqrt(distance_sq(p1, p2))


def point_to_segment_distance(p: Point, a: Point, b: Point) -> float:
    """Computes minimum distance from point p to segment [a, b]."""
    ab_x = b[0] - a[0]
    ab_y = b[1] - a[1]
    ab_len_sq = ab_x * ab_x + ab_y * ab_y
    if ab_len_sq == 0.0:
        return distance(p, a)

    ap_x = p[0] - a[0]
    ap_y = p[1] - a[1]
    t = (ap_x * ab_x + ap_y * ab_y) / ab_len_sq
    t = max(0.0, min(1.0, t))

    closest = (a[0] + t * ab_x, a[1] + t * ab_y)
    return distance(p, closest)


def segments_intersect(a1: Point, a2: Point, b1: Point, b2: Point) -> bool:
    """Checks if line segments [a1, a2] and [b1, b2] intersect."""
    def ccw(p1: Point, p2: Point, p3: Point) -> float:
        return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

    d1 = ccw(a1, a2, b1)
    d2 = ccw(a1, a2, b2)
    d3 = ccw(b1, b2, a1)
    d4 = ccw(b1, b2, a2)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    # Check collinear cases
    for p, q, r in [(a1, a2, b1), (a1, a2, b2), (b1, b2, a1), (b1, b2, a2)]:
        if abs(ccw(p, q, r)) < 1e-7:
            if min(p[0], q[0]) - 1e-7 <= r[0] <= max(p[0], q[0]) + 1e-7 and \
               min(p[1], q[1]) - 1e-7 <= r[1] <= max(p[1], q[1]) + 1e-7:
                return True
    return False


def segment_to_segment_distance(a1: Point, a2: Point, b1: Point, b2: Point) -> float:
    """Computes minimum distance between two line segments."""
    if segments_intersect(a1, a2, b1, b2):
        return 0.0
    d1 = point_to_segment_distance(a1, b1, b2)
    d2 = point_to_segment_distance(a2, b1, b2)
    d3 = point_to_segment_distance(b1, a1, a2)
    d4 = point_to_segment_distance(b2, a1, a2)
    return min(d1, d2, d3, d4)


def polygon_edges(poly: Polygon) -> list[tuple[Point, Point]]:
    n = len(poly)
    return [(poly[i], poly[(i + 1) % n]) for i in range(n)]


def polygon_to_segment_distance(poly: Polygon, a: Point, b: Point) -> float:
    """Computes minimum distance from a polygon to line segment [a, b].
    Returns 0.0 if segment intersects or is inside polygon."""
    if point_in_polygon(a, poly) or point_in_polygon(b, poly):
        return 0.0
    min_dist = float("inf")
    for e1, e2 in polygon_edges(poly):
        d = segment_to_segment_distance(e1, e2, a, b)
        if d < min_dist:
            min_dist = d
            if min_dist == 0.0:
                return 0.0
    return min_dist


def point_in_polygon(point: Point, poly: Sequence[Point]) -> bool:
    """Ray casting algorithm for point-in-polygon test."""
    x, y = point
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def polygon_inside_boundary(inner: Polygon, boundary: Sequence[Point]) -> bool:
    """Checks if inner polygon is completely inside boundary polygon."""
    # All vertices of inner must be inside boundary
    for pt in inner:
        if not point_in_polygon(pt, boundary):
            return False
    # No edges may intersect boundary edges
    for ie1, ie2 in polygon_edges(inner):
        for be1, be2 in polygon_edges(list(boundary)):
            if segments_intersect(ie1, ie2, be1, be2):
                return False
    return True


def polygon_bbox(poly: Sequence[Point]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_overlap(b1: tuple[float, float, float, float], b2: tuple[float, float, float, float]) -> bool:
    return not (b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1])


def bbox_distance(b1: tuple[float, float, float, float], b2: tuple[float, float, float, float]) -> float:
    dx = max(0.0, max(b1[0] - b2[2], b2[0] - b1[2]))
    dy = max(0.0, max(b1[1] - b2[3], b2[1] - b1[3]))
    return math.hypot(dx, dy)


def polygons_overlap_sat(poly1: Polygon, poly2: Polygon) -> bool:
    """Separating Axis Theorem (SAT) collision check for two convex polygons."""
    b1 = polygon_bbox(poly1)
    b2 = polygon_bbox(poly2)
    if not bbox_overlap(b1, b2):
        return False

    for poly in (poly1, poly2):
        edges = polygon_edges(poly)
        for p1, p2 in edges:
            edge_x = p2[0] - p1[0]
            edge_y = p2[1] - p1[1]
            normal = (-edge_y, edge_x)
            length = math.hypot(normal[0], normal[1])
            if length == 0:
                continue
            axis = (normal[0] / length, normal[1] / length)

            min1 = float("inf")
            max1 = float("-inf")
            for pt in poly1:
                proj = pt[0] * axis[0] + pt[1] * axis[1]
                if proj < min1: min1 = proj
                if proj > max1: max1 = proj

            min2 = float("inf")
            max2 = float("-inf")
            for pt in poly2:
                proj = pt[0] * axis[0] + pt[1] * axis[1]
                if proj < min2: min2 = proj
                if proj > max2: max2 = proj
             # If there is a gap along this axis, or touching on edge, they do NOT overlap
            if max1 <= min2 + 1e-3 or max2 <= min1 + 1e-3:
                return False
    return True


def polygon_to_polygon_distance(poly1: Polygon, poly2: Polygon) -> float:
    """Returns 0.0 if overlapping, otherwise minimum Euclidean distance between boundaries."""
    b1 = polygon_bbox(poly1)
    b2 = polygon_bbox(poly2)
    b_dist = bbox_distance(b1, b2)
    if b_dist > 1000.0:
        return b_dist

    if polygons_overlap_sat(poly1, poly2):
        return 0.0
    min_dist = float("inf")
    for e1_a, e1_b in polygon_edges(poly1):
        for e2_a, e2_b in polygon_edges(poly2):
            d = segment_to_segment_distance(e1_a, e1_b, e2_a, e2_b)
            if d < min_dist:
                min_dist = d
                if min_dist == 0.0:
                    return 0.0
    return min_dist


def min_distance_to_boundary(poly: Polygon, boundary: Sequence[Point]) -> float:
    """Minimum distance from polygon edges to boundary walls."""
    min_dist = float("inf")
    for pe1, pe2 in polygon_edges(poly):
        for be1, be2 in polygon_edges(list(boundary)):
            d = segment_to_segment_distance(pe1, pe2, be1, be2)
            if d < min_dist:
                min_dist = d
    return min_dist
