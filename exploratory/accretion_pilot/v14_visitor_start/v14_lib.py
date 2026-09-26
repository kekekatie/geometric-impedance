#!/usr/bin/env python3
"""
v14_lib.py -- bounded visitor-start intervention on the RETAINED v13 frozen worlds.

No evolution replay, no new substrate family: frozen evolved WEIGHTS are read from the
v13 snapshots; static geometry/topology (boundary, faces, adjacency, histories,
coefficients) is reconstructed deterministically via v11's frozen_setup and verified to
match the snapshots. The visitor movement reproduces v13 exactly (same rounded-weight
policy, same encounter/coverage bookkeeping) and additionally records arrival at the
imposed paths. The only intervention is the visitor START vertex.
"""
from __future__ import annotations
import os, sys
from collections import deque
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V13 = os.path.join(os.path.dirname(_HERE), "v13_local_reader")
sys.path.insert(0, _V13)
import v13_lib as L                      # noqa: E402  (also puts v11/v2 on the path)
import substrate_lib as sl               # noqa: E402

SNAP13 = os.path.join(_V13, "results", "snapshots")
BUDGETS = L.BUDGETS                       # [100, 300, 1000]
PRIMARY = 300
VISIT_BASE = L.VISIT_BASE                 # matched visitor streams vs v13
NSEED = 50
REPLICATES = 5
N_PAIRS = L.N_PAIRS
qround = L.qround
ekey = L.ekey


# ---------------------------------------------------------------------------
# Distant-start selection -- FROM ORIGINAL GEOMETRY ONLY (frozen before outcomes)
# ---------------------------------------------------------------------------
def select_distant_start(sub, pathA, pathB, min_boundary=2):
    """Choose the visitor 'distant start' for one (patch, history-pair).

    Rule (fixed before any visitor outcome):
      * union U = vertices of pathA and pathB.
      * d_U(v) = original-graph (base-edge) hop distance from v to the nearest vertex
        of U; d_bd(v) = original-graph hop distance to the nearest boundary vertex.
      * Eligible: d_bd(v) >= min_boundary AND d_U(v) > 0 (strictly off the union).
      * Choose the eligible vertex maximising d_U(v).
      * Canonical tie-break (specified in advance): smallest rounded coordinate
        (x, then y) lexicographically -- i.e. min over (round(x,6), round(y,6), v).
    Returns (vertex, info) or (None, info) if no eligible vertex exists (reported, not
    substituted).
    """
    U = set(int(x) for x in pathA) | set(int(x) for x in pathB)
    dA = sl._dist_to_pathset(sub, set(int(x) for x in pathA))
    dB = sl._dist_to_pathset(sub, set(int(x) for x in pathB))
    dU = sl._dist_to_pathset(sub, U)
    dbd = sub.boundary_distance()
    S = int(pathA[0])
    dS = sub.graph_bfs_dist(S)

    eligible = [v for v in sub.pos
                if dbd.get(v, 0) >= min_boundary and dU.get(v, 0) > 0]
    info = {"n_eligible": len(eligible), "S": S,
            "max_dU": (max((dU[v] for v in eligible), default=0))}
    if not eligible:
        info["eligible"] = False
        return None, info

    def keyfn(v):
        p = sub.pos[v]
        return (-dU[v], round(float(p[0]), 6), round(float(p[1]), 6), v)

    v = sorted(eligible, key=keyfn)[0]
    info.update({"eligible": True, "vertex": int(v),
                 "dist_pathA": int(dA[v]), "dist_pathB": int(dB[v]),
                 "dist_union": int(dU[v]), "dist_S": int(dS[v]),
                 "boundary_dist": int(dbd[v]), "degree": len(sub.adj[v]),
                 "x": round(float(sub.pos[v][0]), 6),
                 "y": round(float(sub.pos[v][1]), 6)})
    return int(v), info


# ---------------------------------------------------------------------------
# Snapshot loading -- frozen evolved weights (no replay) + geometry alignment
# ---------------------------------------------------------------------------
def load_patch_snapshot(arm, i):
    return np.load(os.path.join(SNAP13, f"{arm}_{i}.npz"))


def snapshot_edges(d):
    orig = [(int(u), int(v)) for u, v in zip(d["orig_u"], d["orig_v"])]
    cand = [(int(u), int(v)) for u, v in zip(d["cand_u"], d["cand_v"])]
    return orig, cand


def verify_geometry(sub, d):
    """Snapshot geometry/edges/paths/coeffs must equal the deterministic reconstruction.
    Returns (ok, maxdev). Guards that reconstruction is the frozen v13 substrate."""
    orig, cand, idx = L.patch_edge_index(sub)
    s_orig, s_cand = snapshot_edges(d)
    if orig != s_orig or cand != s_cand:
        return False, float("inf")
    dev = 0.0
    for v in range(sub.V):
        dev = max(dev, abs(sub.pos[v][0] - d["pos_x"][v]),
                  abs(sub.pos[v][1] - d["pos_y"][v]))
    return dev < 1e-9, dev


def frozen_from_snapshot(d, orig, cand, j, hk_or_null, seed):
    """Rebuild the exact v13 FrozenWorld for a (pair j, history hk|null, seed)."""
    if hk_or_null == "null":
        vec = d[f"nw_{seed}"]
    else:
        vec = d[f"w_{j}_{hk_or_null}_{seed}"]
    return L.FrozenWorld(orig, cand, vec, d[f"coeff_{j}"])


# ---------------------------------------------------------------------------
# Visitor: reproduces v13 movement/encounter EXACTLY, plus arrival tracking.
# (When start == v13 start and rng seeded identically, enc/cover/score match v13.)
# ---------------------------------------------------------------------------
def visit_track(frozen, start, budgets, rng, path_union):
    encountered = set(); verts = set()
    enc_at = {}; cover = {}; arrival = {}
    bset = set(budgets); Bmax = max(budgets)
    arrival_step = None

    def observe(v):
        verts.add(v)
        for u in frozen.adj[v]:
            e = ekey(v, u)
            if e in frozen.is_diag:
                encountered.add(e)

    v = start; observe(v)
    if v in path_union:
        arrival_step = 0
    for step in range(1, Bmax + 1):
        nb = frozen.adj[v]
        qw = np.array([qround(frozen.w[ekey(v, u)]) for u in nb], float)
        v = nb[rng.choice(len(nb), p=qw / qw.sum())]
        observe(v)
        if arrival_step is None and v in path_union:
            arrival_step = step
        if step in bset:
            enc_at[step] = frozenset(encountered)
            npd = frozen.n_present_diag(); nhd = frozen.n_high_diag()
            nh_seen = sum(1 for dd in encountered if qround(frozen.w[dd]) == 6)
            cover[step] = {"verts": len(verts), "diags": len(encountered),
                           "frac_present": len(encountered) / npd if npd else 0.0,
                           "frac_high_seen": nh_seen / nhd if nhd else 0.0}
            arrival[step] = (arrival_step is not None and arrival_step <= step)
    return enc_at, cover, arrival, arrival_step


def score_enc(enc, coeff_by_key, frozen):
    return L.score_enc(enc, coeff_by_key, frozen)
