#!/usr/bin/env python3
"""
coop_common.py -- shared wiring for the cooperative-rearrangement pilot
(2026-11-02, branch claude/cooperative-rearrangement-pilot).

Read-only with respect to the frozen engine, the frozen reader, the pilot, the
jam-compatibility diagnostic, and that study's audit. We reuse the AUDITED tools:
  * feas.py (box certifier) + a box-free Phase-I feasibility check (audit Part 2);
  * part4_iis.constraints_with_origin (provenance; a vertex constraint is supplied
    by the vertex, i.e. survives if ANY incident tile remains);
and the frozen engine via study_common / engine_bridge (needs EFP_SNAPSHOT).

Terminology: "retained boundary band" is the study's "active skin". Existing
identifiers are preserved.
"""
from __future__ import annotations
import os, sys, collections
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

# audited study src: feas.py, part4_iis.py, study_common.py
AUDIT_STUDY_SRC = (Path(__file__).resolve().parents[2] / "jam_compatibility_diagnostic" / "src")
if str(AUDIT_STUDY_SRC) not in sys.path:
    sys.path.insert(0, str(AUDIT_STUDY_SRC))

import study_common as SC                      # noqa: E402  frozen engine (EFP_SNAPSHOT)
from study_common import Sl, PC, L, D, M, S, WIN  # noqa: E402
import feas                                    # noqa: E402
import part4_iis as P4                         # noqa: E402

HERE = Path(__file__).resolve().parents[1]     # cooperative_rearrangement_pilot
INPUT = HERE / "input"
RESULTS = HERE / "results"
FIGURES = HERE / "figures"


# ----------------------------- serialization -----------------------------
def ez(z):
    return [z.real, z.imag]


def etile(t):
    return [int(t[0])] + [ez(z) for z in t[1:]]


def dtile(rec):
    return (int(rec[0]),) + tuple(complex(x, y) for x, y in rec[1:])


def ekey(p, q):
    return frozenset((L.key(p), L.key(q)))


def dk(t):
    return PC.dk(t)


# ----------------------------- adjacency -----------------------------
def edge_adjacency(tiles):
    """dkey -> set(dkey) for half-tiles sharing a full edge (both own it)."""
    by_edge = collections.defaultdict(list)
    for t in tiles:
        c, A, B, C = t
        for p, q in ((A, B), (B, C), (C, A)):
            by_edge[ekey(p, q)].append(dk(t))
    adj = collections.defaultdict(set)
    for _, ts in by_edge.items():
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                adj[ts[i]].add(ts[j]); adj[ts[j]].add(ts[i])
    return adj


def connected_components(tiles):
    adj = edge_adjacency(tiles)
    dks = {dk(t) for t in tiles}
    seen = set(); comps = []
    for start in sorted(dks):
        if start in seen:
            continue
        comp = set(); stack = [start]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u); comp.add(u)
            stack.extend(adj[u] - seen)
        comps.append(comp)
    return comps


def connected_regions(tiles, seeds, max_size, cap):
    """Deterministically enumerate connected tile-dkey subsets (edge-adjacency) of
    size 1..max_size that contain at least one seed dkey. BFS by size (small
    first); dedup by frozenset; stop after `cap` distinct regions. Yields
    frozensets of dkeys."""
    adj = edge_adjacency(tiles)
    seen = set()
    frontier = []
    for s in sorted(seeds):
        fs = frozenset((s,))
        if fs not in seen:
            seen.add(fs); frontier.append(fs)
    out = []
    i = 0
    while i < len(frontier) and len(out) < cap:
        cur = frontier[i]; i += 1
        out.append(cur)
        if len(cur) >= max_size:
            continue
        nbrs = set()
        for u in cur:
            nbrs |= adj[u]
        nbrs -= cur
        for v in sorted(nbrs):
            nf = frozenset(cur | {v})
            if nf not in seen:
                seen.add(nf); frontier.append(nf)
    return out[:cap]


# ------------- vertex contributions under a consistent gauge -------------
class BandConstraints:
    """Precompute every vertex's per-(rank,facet) constraint contribution under a
    FIXED gauge (rank map taken once from the full band). The exterior constraint
    system for a region R is then obtained by dropping ONLY the vertices fully
    engulfed by R (all incident tiles in R); a vertex whose star is partly outside
    R still supplies its constraint. This matches slack.constraints exactly."""

    def __init__(self, band_tiles, rank=None):
        self.band = list(band_tiles)
        self.rank = rank if rank is not None else Sl.rank_of(self.band)
        K, pos, conf = M.lift(self.band)
        self.K = K; self.pos = pos
        # per vertex: (rk, {(rk,i): c_v})
        self.vcontrib = {}
        self.vincident = collections.defaultdict(set)   # vkey -> set(dkey) incident tiles
        for v, k in K.items():
            rk = self.rank[int(k.sum())]
            z = M.perp(k)
            n, h = WIN[rk]
            cs = {}
            for i, (nx, ny) in enumerate(n):
                cs[(rk, i)] = float(nx) * z.real + float(ny) * z.imag - float(h)
            self.vcontrib[v] = cs
        for t in self.band:
            for zz in t[1:]:
                vk = L.key(zz)
                if vk in self.vcontrib:
                    self.vincident[vk].add(dk(t))
        # per (rk,i): sorted (contribution desc, vkey) for fast max under removal
        self.by_key = collections.defaultdict(list)
        for v, cs in self.vcontrib.items():
            for key, c in cs.items():
                self.by_key[key].append((c, v))
        for key in self.by_key:
            self.by_key[key].sort(key=lambda t: -t[0])
        self.full_cmax = {key: lst[0][0] for key, lst in self.by_key.items()}

    def engulfed_vertices(self, region_dks):
        """Vertices all of whose incident band tiles lie in region_dks."""
        R = set(region_dks)
        E = set()
        # candidate vertices: those on region tiles
        cand = set()
        tiles_by_dk = {dk(t): t for t in self.band}
        for d in R:
            for zz in tiles_by_dk[d][1:]:
                cand.add(L.key(zz))
        for vk in cand:
            inc = self.vincident.get(vk)
            if inc and inc <= R:
                E.add(vk)
        return E

    def exterior_cmax(self, region_dks):
        """cmax of the constraints supplied by tiles OUTSIDE region_dks (consistent
        gauge). Drops only fully-engulfed vertices."""
        E = self.engulfed_vertices(region_dks)
        cmax = {}
        for key, lst in self.by_key.items():
            for c, v in lst:           # sorted desc; first surviving vertex is the max
                if v not in E:
                    cmax[key] = c
                    break
            # if every supplier is engulfed, that (rk,i) constraint vanishes entirely
        return cmax, E


# ----------------------------- feasibility -----------------------------
def box_free_feasible(cmax):
    """Box-INDEPENDENT feasibility of { n_i.t >= c_i } (unit normals), via a
    Phase-I LP with free t (no position box) and a deepest-margin LP. Returns
    (verdict, margin): verdict in {feasible, infeasible, unresolved}."""
    rows = [(r[0], r[1]) for r in feas.rows_from_cmax(cmax)]
    if not rows:
        return "feasible", float("inf")
    ur = feas._unit(rows)
    N = np.array([[nx, ny] for (nx, ny), c in ur], float)
    cc = np.array([c for (nx, ny), c in ur], float)
    r1 = linprog(c=[0.0, 0.0], A_ub=-N, b_ub=-cc, bounds=[(None, None)] * 2, method="highs")
    if r1.status == 2:
        base = "infeasible"
    elif r1.status == 0:
        base = "feasible"
    else:
        return "unresolved", None
    # deepest signed margin (box-free in position)
    A_ub = np.hstack([-N, np.ones((len(ur), 1))])    # unit normals => ||n||=1
    r2 = linprog(c=[0, 0, -1.0], A_ub=A_ub, b_ub=-cc,
                 bounds=[(None, None), (None, None), (-1e3, 1e3)], method="highs")
    margin = float(r2.x[2]) if r2.status == 0 and r2.x is not None else None
    return base, margin


def classify_exterior(cmax):
    """Combine the box-50 certifier with the box-free check; agree => that verdict,
    disagree => unresolved (reported, never silently 'infeasible')."""
    box = feas.classify(cmax)                      # positive_area / lower_dimensional / infeasible / unresolved
    bf, margin = box_free_feasible(cmax)
    box_feasible = box["cls"] in ("positive_area", "lower_dimensional")
    if bf == "feasible" and box_feasible:
        verdict = "feasible"
    elif bf == "infeasible" and box["cls"] == "infeasible":
        verdict = "infeasible"
    else:
        verdict = "unresolved"
    return dict(verdict=verdict, box_cls=box["cls"], box_r=box["r"],
                box_free=bf, box_free_margin=margin, n_constraints=len(cmax))


# ------- order-independent completed-replacement legality (audited approach) -------
import math as _math


def vertex_star_ok(V_at_k):
    """Mirror of laying_the_tiling.Patch.vertex_ok(k, []) on a FINISHED corner list:
    complete atlas star (2pi, in STARS) or contiguous arcs (each in ARCS)."""
    lst = sorted(V_at_k); n = len(lst)
    if n == 0:
        return True
    tot = sum(d for _, d, _ in lst)
    if tot > 2 * _math.pi + 1e-6:
        return False
    if abs(tot - 2 * _math.pi) < 1e-6:
        return L.star(lst) in L.STARS
    wrap = lambda x: (x + _math.pi) % (2 * _math.pi) - _math.pi
    start = next((i for i in range(n)
                  if abs(wrap(lst[i - 1][0] + lst[i - 1][1] - lst[i][0])) > 1e-6), None)
    if start is None:
        return False
    seq = lst[start:] + lst[:start]; arcs = [[seq[0]]]
    for i in range(1, n):
        pa, pd, _ = seq[i - 1]; a = seq[i][0]
        g = wrap(a - (pa + pd))
        if abs(g) < 1e-6:
            arcs[-1].append(seq[i])
        elif g < 0:
            return False
        else:
            arcs.append([seq[i]])
    return all(tuple(l for _, _, l in arc) in L.ARCS for arc in arcs)


def overlap_or_dupe(exterior_local, fill_tiles):
    """True if any fill tile overlaps the exterior or duplicates an edge-mate."""
    P = L.Patch(list(exterior_local)); placed = []
    for t in fill_tiles:
        cen = sum(t[1:]) / 3
        for u in list(P.tris) + placed:
            if abs(u[1] - cen) < 3 * L.SCALE_LEN and (L.inside(cen, *u[1:]) or any(L.inside(z, *u[1:]) for z in t[1:])):
                return True
        ekset = P.edges.get(frozenset((L.key(t[1]), L.key(t[2]))), [])
        if L.canon(t) in {L.canon(u) for u in ekset}:
            return True
        placed.append(t)
    return False


def completed_replacement_legal(exterior_local, region_tiles, fill_tiles):
    """Order-independent frozen legality of replacing region_tiles by fill_tiles,
    against the local exterior: no overlap/dup, and every touched vertex is a
    complete/contiguous atlas star in the assembled patch."""
    if overlap_or_dupe(exterior_local, fill_tiles):
        return False
    touch = {L.key(z) for t in fill_tiles for z in t[1:]}
    P = L.Patch(list(exterior_local) + list(fill_tiles))
    return all(vertex_star_ok(P.V.get(vk, [])) for vk in touch)
