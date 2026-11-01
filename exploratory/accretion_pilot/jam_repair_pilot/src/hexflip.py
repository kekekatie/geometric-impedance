#!/usr/bin/env python3
"""
hexflip.py -- three-rhombus hexagon rearrangement (the Penrose simpleton/phason
flip) on decorated half-tiles, built on the FROZEN engine's own legality.

No matching rule is relaxed. Legality of any placed half-tile is decided ONLY
by the frozen engine: a tile is legal iff it does not overlap, is not a
duplicate, and every touched vertex is a contiguous atlas star or a complete
atlas star (laying_the_tiling.Patch.legal / vertex_ok, via D.candidates).

Representation facts used (verified against the templates):
  - a half-tile is (c, A, B, C); c in {0,1}; vertices complex.
  - legs have length S; the single non-leg edge is the BASE.
      type 0 (36-72-72): base length S/tau   -> thin rhombus
      type 1 (108-36-36): base length tau*S  -> thick rhombus
  - a RHOMBUS is two SAME-type half-tiles sharing their base edge.

A flip hexagon is 3 rhombi meeting at one interior vertex v (degree 3), whose
union is a convex hexagon with v as the only strictly-interior vertex. The flip
re-tiles that hexagon the other way (moving v), keeping the 6 outer edges fixed.
"""
from __future__ import annotations
import math, cmath, collections, itertools
import engine_bridge as EB

L, D, S = EB.L, EB.D, EB.S
key = L.key
orient = L.orient
TAU = (1 + 5 ** 0.5) / 2
EPS = 1e-6


def _elen(p, q):
    return abs(q - p)


def is_leg(p, q):
    return abs(_elen(p, q) - S) < 1e-4 * S


def base_edge(t):
    """Return the (unordered) base edge of a half-tile as a frozenset of keys,
    plus the two endpoints. The base is the unique non-leg edge."""
    c, A, B, C = t
    for p, q in ((A, B), (B, C), (C, A)):
        if not is_leg(p, q):
            return frozenset((key(p), key(q))), (p, q)
    raise ValueError("no base edge (degenerate tile)")


def tile_vertices(t):
    return t[1], t[2], t[3]


def tile_centroid(t):
    return sum(t[1:]) / 3


def tile_area(t):
    return abs(orient(*t[1:])) / 2


def dkey(t):
    return D.dkey(t)


# ----------------------------------------------------------------- rhombi
def rhombi(tiles):
    """Pair half-tiles into rhombi by shared base edge (same type). Returns a
    list of rhombi; each rhombus is a frozenset of the two tiles' dkeys, with
    helper maps. Half-tiles whose base partner is absent (e.g. on the frontier)
    are left unpaired and excluded."""
    by_base = collections.defaultdict(list)
    tmap = {}
    for t in tiles:
        tmap[dkey(t)] = t
        b, _ = base_edge(t)
        by_base[(t[0], b)].append(t)
    rh = []
    for (c, b), ts in by_base.items():
        if len(ts) == 2:
            rh.append(tuple(sorted((dkey(ts[0]), dkey(ts[1])))))
        # len 1 -> frontier half-rhombus; len>2 impossible for a base edge
    return rh, tmap


def rhombus_vertices(rh, tmap):
    vs = set()
    for dk in rh:
        for z in tile_vertices(tmap[dk]):
            vs.add(key(z))
    return vs


# ----------------------------------------------------------- flip detection
def interior_vertices(patch):
    """Vertices with a complete atlas star (angle sum 2pi)."""
    out = []
    for k, lst in patch.V.items():
        tot = sum(d for _, d, _ in lst)
        if abs(tot - 2 * math.pi) < 1e-6:
            out.append(k)
    return out


def _hexagon_boundary(cluster_tiles):
    """Outer boundary edges of a tile cluster (edges owned by exactly one tile
    of the cluster). Returns list of frozenset-edge-keys, and the ordered
    boundary vertex cycle if it is a simple polygon, else None."""
    edgecount = collections.defaultdict(int)
    edgepts = {}
    for t in cluster_tiles:
        c, A, B, C = t
        for p, q in ((A, B), (B, C), (C, A)):
            ek = frozenset((key(p), key(q)))
            edgecount[ek] += 1
            edgepts[ek] = (p, q)
    boundary = [ek for ek, n in edgecount.items() if n == 1]
    # try to order into a cycle
    adj = collections.defaultdict(list)
    for ek in boundary:
        p, q = edgepts[ek]
        adj[key(p)].append(key(q))
        adj[key(q)].append(key(p))
    if any(len(v) != 2 for v in adj.values()):
        return boundary, None
    start = next(iter(adj))
    cycle = [start]
    prev, cur = None, start
    while True:
        nxts = [w for w in adj[cur] if w != prev]
        if not nxts:
            break
        nxt = nxts[0]
        if nxt == start:
            break
        cycle.append(nxt)
        prev, cur = cur, nxt
        if len(cycle) > len(boundary) + 1:
            return boundary, None
    return boundary, cycle


def find_flip_hexagons(tiles):
    """Return a list of flip-hexagon clusters. Each is a dict with:
      vertex   : key of the interior flip vertex v
      tiles    : the 6 decorated half-tiles forming the hexagon
      boundary : the 6 outer boundary edge-keys
      bverts   : the 6 boundary vertex keys (ordered cycle)
    Strictly geometric detection; legality of the ALTERNATIVE filling is tested
    later by the frozen engine."""
    patch = L.Patch(list(tiles))
    rh, tmap = rhombi(tiles)
    # map: vertex-key -> set of rhombus indices incident to it
    v_rh = collections.defaultdict(set)
    rverts = []
    for i, r in enumerate(rh):
        vs = rhombus_vertices(r, tmap)
        rverts.append(vs)
        for vk in vs:
            v_rh[vk].add(i)
    out = []
    inter = set(interior_vertices(patch))
    for vk in inter:
        inc = v_rh.get(vk, set())
        if len(inc) != 3:
            continue
        cluster_dks = set()
        for i in inc:
            cluster_dks |= set(rh[i])
        cluster = [tmap[dk] for dk in cluster_dks]
        if len(cluster) != 6:
            continue
        boundary, cycle = _hexagon_boundary(cluster)
        if cycle is None or len(cycle) != 6:
            continue
        # v must be strictly interior: not on the boundary cycle
        if vk in set(cycle):
            continue
        # every boundary vertex is a corner shared with the rest of the patch:
        # the flip must keep them; v is the only vertex that can move.
        out.append(dict(vertex=vk, tiles=cluster, boundary=boundary, bverts=cycle))
    return out


# --------------------------------------------- geometric refilling of a hexagon
def _poly_of(cycle):
    return [complex(*k) for k in cycle]


_GTOL = 1e-4 * S          # geometric tolerance, matched to the engine's is_leg tol (~2e-6)


def _on_segment(z, a, b, tol=_GTOL):
    lab = abs(b - a)
    if lab < 1e-12:
        return abs(z - a) < tol
    t = ((z - a).real * (b - a).real + (z - a).imag * (b - a).imag) / lab ** 2
    tt = tol / lab                      # absolute tol -> parametric tol
    if t < -tt or t > 1 + tt:
        return False
    proj = a + t * (b - a)
    return abs(z - proj) < tol


def _in_poly(z, poly, tol=_GTOL):
    """Return 'in' (strictly inside), 'on' (on boundary) or 'out'."""
    n = len(poly)
    for i in range(n):
        if _on_segment(z, poly[i], poly[(i + 1) % n], tol):
            return "on"
    inside = False
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if (a.imag > z.imag) != (b.imag > z.imag):
            xint = (b.real - a.real) * (z.imag - a.imag) / (b.imag - a.imag) + a.real
            if z.real < xint:
                inside = not inside
    return "in" if inside else "out"


def _point_in_hexagon(z, poly):
    return _in_poly(z, poly) in ("in", "on")


def _point_strictly_in_hexagon(z, poly):
    return _in_poly(z, poly) == "in"


def _template_placements(p, q):
    """All decorated half-tiles having an edge exactly (p,q) (either as a leg or
    base), both third-vertex sides. Geometry only (no legality, no atlas)."""
    out = {}
    for (c, o), (tc, A, B, C) in L.TEMPL.items():
        P = {"A": A, "B": B, "C": C}
        for X, Y, Z in (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"),
                        ("B", "A", "C"), ("C", "B", "A"), ("A", "C", "B")):
            x, y, z = P[X], P[Y], P[Z]
            if abs(_elen(x, y) - _elen(p, q)) > 1e-6:
                continue
            a = (q - p) / (y - x)
            zz = p + a * (z - x)
            img = {X: p, Y: q, Z: zz}
            nt = (tc, img["A"], img["B"], img["C"])
            out[dkey(nt)] = nt
    return list(out.values())


def _legal_no_atlas(P, t):
    """L.Patch.legal minus the vertex-star atlas test: overlap-free + not a
    duplicate across the base edge. Used only to COUNT geometric candidates."""
    cen = tile_centroid(t)
    SL = L.SCALE_LEN
    for u in P.tris:
        if abs(u[1] - cen) < 3 * SL and (L.inside(cen, *u[1:]) or any(L.inside(z, *u[1:]) for z in t[1:])):
            return False
    if L.canon(t) in {L.canon(u) for u in P.edges.get(frozenset((key(t[1]), key(t[2]))), [])}:
        return False
    return True


def _placements_across(p, q, poly, interior_only=True):
    """Decorated half-tiles having an edge exactly (p,q), whose centroid lies
    strictly inside the hexagon poly (so they fill inward). Geometry only; both
    third-vertex sides considered, kept if the centroid is inside."""
    out = {}
    for (c, o), (tc, A, B, C) in L.TEMPL.items():
        Pp = {"A": A, "B": B, "C": C}
        for X, Y, Z in (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"),
                        ("B", "A", "C"), ("C", "B", "A"), ("A", "C", "B")):
            x, y, z = Pp[X], Pp[Y], Pp[Z]
            if abs(_elen(x, y) - _elen(p, q)) > 1e-6:
                continue
            a = (q - p) / (y - x)
            zz = p + a * (z - x)
            img = {X: p, Y: q, Z: zz}
            nt = (tc, img["A"], img["B"], img["C"])
            if interior_only and not _point_strictly_in_hexagon(tile_centroid(nt), poly):
                continue
            out[dkey(nt)] = nt
    return list(out.values())


def enumerate_hexagon_fillings(hex_tiles, surround_tiles, legality="engine", max_solutions=32):
    """All complete tilings of the hexagon H (= union of hex_tiles) under the
    chosen legality, filling strictly inside H. The hole frontier is tracked
    explicitly (independent of which tiles the surround owns), so this works
    with a full, reduced or empty surround. Returns (solutions, lookup): each
    solution a sorted tuple of dkeys; lookup maps dkey -> tile.

    legality='engine' -> frozen P.legal (full atlas, overlap, duplicate);
    legality='geom'   -> overlap + duplicate only (no vertex-star atlas).
    The original dissection is always among the 'engine' solutions."""
    boundary, cycle = _hexagon_boundary(hex_tiles)
    poly = _poly_of(cycle)
    hexarea = sum(tile_area(t) for t in hex_tiles)
    bpts = {}
    for t in hex_tiles:
        c, A, B, C = t
        for p, qq in ((A, B), (B, C), (C, A)):
            bpts.setdefault(frozenset((key(p), key(qq))), (p, qq))
    boundary_set = set(boundary)

    solutions = []
    lookup = {}

    def open_edges(placed):
        """Edges on the hole frontier: hexagon boundary edges not yet covered by
        a placed tile, plus placed-tile edges used an odd number of times that
        are not hexagon boundary edges (interior seams still open)."""
        used = collections.Counter()
        pts = dict(bpts)
        for t in placed:
            c, A, B, C = t
            for p, qq in ((A, B), (B, C), (C, A)):
                ek = frozenset((key(p), key(qq)))
                used[ek] += 1
                pts[ek] = (p, qq)
        oe = []
        for ek in boundary_set:
            if used[ek] == 0:
                oe.append(ek)
        for ek, n in used.items():
            if ek in boundary_set:
                continue
            if n % 2 == 1:        # interior seam with one side filled
                oe.append(ek)
        return [(ek, pts[ek]) for ek in oe]

    def legal_add(P, t):
        return P.legal(t) if legality == "engine" else _legal_no_atlas(P, t)

    def rec(placed, area, depth):
        if len(solutions) >= max_solutions or depth > 8:
            return
        if abs(area - hexarea) < 1e-9:
            solutions.append(tuple(sorted(dkey(t) for t in placed)))
            return
        oe = open_edges(placed)
        if not oe:
            return
        oe.sort(key=lambda it: sorted(it[0]))
        ek, (p, q) = oe[0]
        P = L.Patch(list(surround_tiles) + list(placed))
        placed_dks = {dkey(t) for t in placed}
        for nt in _placements_across(p, q, poly):
            if dkey(nt) in placed_dks:
                continue
            # vertices must stay within the closed hexagon
            if not all(_point_in_hexagon(v, poly) for v in tile_vertices(nt)):
                continue
            if not legal_add(P, nt):
                continue
            lookup[dkey(nt)] = nt
            rec(list(placed) + [nt], area + tile_area(nt), depth + 1)

    rec([], 0.0, 0)
    return sorted(set(solutions)), lookup


# ------------------------------------------------- legality against the engine
def filling_is_legal(solution_tiles, surround_tiles):
    """True iff placing all solution tiles into the surround yields only legal
    tiles (frozen engine legal()). We rebuild the surround and add tiles in a
    geometry order, checking legal() at each add against the growing patch."""
    P = L.Patch(list(surround_tiles))
    for t in sorted(solution_tiles, key=lambda u: (u[0], key(u[1]), key(u[2]), key(u[3]))):
        if not P.legal(t):
            return False, dkey(t)
        P.add(t)
    return True, None


def solution_tiles_from_dkeys(dks, lookup):
    return [lookup[dk] for dk in dks]
