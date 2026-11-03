#!/usr/bin/env python3
"""
arc_tools.py -- deterministic, geometry-based arc decomposition of the retained
boundary band (active ring), and the frozen-reader scoring of connected sub-arcs.

Only CONNECTED sub-arcs are scored, so the 5D lift is single-valued and
path-independent (the frozen reader raises lift_cycle_conflict otherwise). The
notch anchor theta0 is the band-centroid angle of the midpoint between the two
dead frontier sites.
"""
from __future__ import annotations
import cmath, collections
import scar_common as SC
from scar_common import L, dk, ekey


def centroid(tiles):
    zs = [z for t in tiles for z in t[1:]]
    return sum(zs) / len(zs)


def tile_angle(t, c):
    return cmath.phase(sum(t[1:]) / 3 - c)


def notch_theta0(state):
    """band-centroid angle of the midpoint between the two dead frontier sites."""
    c = centroid(state["band"])
    mids = [(e[0] + e[1]) / 2 for e in state["dead"]]
    m = sum(mids) / len(mids)
    return cmath.phase(m - c), c


def edge_adjacency(tiles):
    by_edge = collections.defaultdict(list)
    for t in tiles:
        a, b, cc = t[1], t[2], t[3]
        for p, q in ((a, b), (b, cc), (cc, a)):
            by_edge[ekey(p, q)].append(dk(t))
    adj = collections.defaultdict(set)
    for _, ts in by_edge.items():
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                adj[ts[i]].add(ts[j]); adj[ts[j]].add(ts[i])
    return adj


def connected_components(tiles):
    adj = edge_adjacency(tiles)
    tmap = {dk(t): t for t in tiles}
    seen = set(); comps = []
    for start in sorted(tmap):
        if start in seen:
            continue
        comp = set(); stack = [start]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u); comp.add(u)
            stack.extend(adj[u] - seen)
        comps.append([tmap[d] for d in comp])
    return comps


def largest_component(tiles):
    comps = connected_components(tiles)
    return max(comps, key=len) if comps else []


def angular_window(tiles, c, center, half_width):
    """tiles whose centroid angle lies within +/- half_width of `center` (wrapped)."""
    import math
    out = []
    for t in tiles:
        a = tile_angle(t, c)
        d = abs(((a - center + math.pi) % (2 * math.pi)) - math.pi)
        if d <= half_width + 1e-12:
            out.append(t)
    return out


def score_arc(state, arc_tiles):
    """Score a connected sub-arc with the frozen reader (direct call) under the
    fork gauge + A/B hypotheses. Returns a dict with verdict, F-area, intersections
    and choice-tile retention. Non-connected inputs are reduced to their largest
    connected component first (single-valued lift)."""
    comp = largest_component(arc_tiles)
    payload = SC.RD.build_payload(state["Sstar"], state["cs"], comp)
    raw = SC.SR.read(payload)
    outcome, detail = SC.RD.classify(raw)
    bkey = dk(state["B"])
    band_keys = {dk(t) for t in state["band"]}
    comp_keys = {dk(t) for t in comp}
    if bkey in comp_keys:
        retention = "retained_in_arc"
    elif bkey in band_keys:
        retention = "retained_outside_arc"
    else:
        retention = "departed"
    return dict(n_tiles=len(comp), n_tiles_requested=len(arc_tiles),
                connected=len(comp) == len(arc_tiles),
                reader_status=raw.get("status"),
                F_area=raw.get("area"), intersections=raw.get("intersections"),
                selected=raw.get("selected"), outcome=outcome, detail=detail,
                choice_tile_retention=retention)
