#!/usr/bin/env python3
"""
v13_lib.py -- replay v11 worlds to t=2000, aligned snapshots, FrozenWorld, and the
passive tagged local visitor. Imports v11's substrate_lib (no new substrate code).
"""
from __future__ import annotations
import json, math, os, sys
from collections import defaultdict, deque
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V11 = os.path.join(os.path.dirname(_HERE), "v11_substrate_pilot")
_V2 = os.path.join(os.path.dirname(_HERE), "v2_saturation")
sys.path.insert(0, _V11); sys.path.insert(0, _V2)
import substrate_lib as sl          # noqa: E402
import accretion_pilot_v2 as v2     # noqa: E402

BASE_SEED = v2.BASE_SEED
RADIUS = 10.0; JITTER = 0.30; HIST_LEN = 6; N_PAIRS = 3
CHECKPOINT = 2000
VISIT_BASE = 900000
BUDGETS = [100, 300, 1000]


def ekey(u, v):
    return (u, v) if u < v else (v, u)


def qround(w):
    return math.floor(w + 0.5)


def frozen_setup():
    """Rebuild the six v11 patches + histories + coefficients from the frozen manifest."""
    man = json.load(open(os.path.join(_V11, "results", "frozen_manifest.json")))
    offsets = man["offsets"]
    patches, hists, coeffs = {}, {}, {}
    for i, off in enumerate(offsets):
        patches[("regular", i)] = sl.Substrate.pentagrid(RADIUS, off)
        patches[("perturbed", i)] = sl.Substrate.pentagrid(RADIUS, off,
                                                           jitter_amp=JITTER, seed=i)
    for key, sub in patches.items():
        hp = sl.make_history_pairs(sub, k=N_PAIRS, length=HIST_LEN)
        hists[key] = hp
        coeffs[key] = [sl.reader_coefficients(sub, h) for h in hp]
    return offsets, patches, hists, coeffs


def replay(sub, path, seed, checkpoint=CHECKPOINT):
    """Reproduce a v11 world to `checkpoint` (history 3 passes, then weighted walk)."""
    w = sl.SubstrateWorld(sub)
    for _ in range(3):
        for a, b in zip(path[:-1], path[1:]):
            w.reinforce(a, b); w.grow_from_edge(a, b)
    rng = np.random.default_rng(BASE_SEED + seed)
    v = path[0]
    for step in range(1, checkpoint + 1):
        nxt = w.weighted_step(v, rng)
        w.reinforce(v, nxt); w.grow_from_edge(v, nxt); v = nxt
    return w


def replay_nohistory(sub, S, seed, checkpoint=CHECKPOINT):
    w = sl.SubstrateWorld(sub)
    rng = np.random.default_rng(BASE_SEED + seed)
    v = S
    for step in range(1, checkpoint + 1):
        nxt = w.weighted_step(v, rng)
        w.reinforce(v, nxt); w.grow_from_edge(v, nxt); v = nxt
    return w


def scalars(w, coeff, S):
    return {"S_high": w.s_high(coeff), "n_active": w.n_activations,
            "frac_active": w.frac_active(), "headroom": w.headroom(),
            "total_weight": w.total_weight(), "struct_access": w.structural_access(S),
            "eff_alt": w.effective_alternatives(S)}


# ---------------------------------------------------------------------------
# Aligned snapshot: weight vector over [orig_edges ; cand_edges]
# ---------------------------------------------------------------------------
def patch_edge_index(sub):
    orig = sorted(sub.base_edges)
    cand = sorted(set(sub.all_diagonals()))
    idx = {e: i for i, e in enumerate(orig)}
    for j, e in enumerate(cand):
        idx[e] = len(orig) + j
    return orig, cand, idx


def weight_vector(w, orig, cand, idx):
    vec = np.zeros(len(orig) + len(cand))
    for i, e in enumerate(orig):
        vec[i] = w.weight[e]
    for j, e in enumerate(cand):
        vec[len(orig) + j] = w.weight.get(e, 0.0)   # 0 = absent
    return vec


# ---------------------------------------------------------------------------
# FrozenWorld reconstructed from an aligned weight vector (read-only)
# ---------------------------------------------------------------------------
class FrozenWorld:
    def __init__(self, orig, cand, vec, coeff):
        self.w = {}
        self.adj = defaultdict(list)
        self.is_diag = set()
        self.coeff = {}
        E = len(orig)
        for i, e in enumerate(orig):
            self.w[e] = vec[i]
            self.adj[e[0]].append(e[1]); self.adj[e[1]].append(e[0])
        for j, e in enumerate(cand):
            wv = vec[E + j]
            if wv > 0:                       # present diagonal
                self.w[e] = wv
                self.adj[e[0]].append(e[1]); self.adj[e[1]].append(e[0])
                self.is_diag.add(e)
                self.coeff[e] = coeff[j]
        for v in self.adj:
            self.adj[v] = sorted(self.adj[v])

    def global_s_high(self):
        return float(sum(self.coeff[d] for d in self.is_diag if qround(self.w[d]) == 6))

    def n_present_diag(self):
        return len(self.is_diag)

    def n_high_diag(self):
        return sum(1 for d in self.is_diag if qround(self.w[d]) == 6)


# ---------------------------------------------------------------------------
# Passive tagged visitor
# ---------------------------------------------------------------------------
def visit_encounters(frozen, S, budgets, rng):
    """Read-only walk; return encountered diagonal-key sets at each budget + coverage.
    Movement/encounter are reader-independent (used to score with multiple coeffs)."""
    encountered = set(); verts = set()
    enc_at = {}; cover = {}
    bset = set(budgets); Bmax = max(budgets)

    def observe(v):
        verts.add(v)
        for u in frozen.adj[v]:
            e = ekey(v, u)
            if e in frozen.is_diag:
                encountered.add(e)
    v = S; observe(v)
    for step in range(1, Bmax + 1):
        nb = frozen.adj[v]
        qw = np.array([qround(frozen.w[ekey(v, u)]) for u in nb], float)
        v = nb[rng.choice(len(nb), p=qw / qw.sum())]
        observe(v)
        if step in bset:
            enc_at[step] = frozenset(encountered)
            npd = frozen.n_present_diag(); nhd = frozen.n_high_diag()
            nh_seen = sum(1 for d in encountered if qround(frozen.w[d]) == 6)
            cover[step] = {"verts": len(verts), "diags": len(encountered),
                           "frac_present": len(encountered) / npd if npd else 0.0,
                           "frac_high_seen": nh_seen / nhd if nhd else 0.0}
    return enc_at, cover


def score_enc(enc, coeff_by_key, frozen):
    return float(sum(coeff_by_key.get(d, 0.0) for d in enc
                     if qround(frozen.w[d]) == 6))


def visit(frozen, S, budgets, rng):
    """Read-only weighted walk on rounded weights; encounter = observe at a vertex.
    Returns scores[b], coverage[b]. Does not mutate frozen."""
    encountered = set(); verts = set()
    scores = {}; cover = {}
    bset = set(budgets); Bmax = max(budgets)

    def observe(v):
        verts.add(v)
        for u in frozen.adj[v]:
            e = ekey(v, u)
            if e in frozen.is_diag:
                encountered.add(e)

    def score():
        return float(sum(frozen.coeff[d] for d in encountered if qround(frozen.w[d]) == 6))

    v = S; observe(v)
    if 0 in bset:
        scores[0] = score()
    for step in range(1, Bmax + 1):
        nb = frozen.adj[v]
        qw = np.array([qround(frozen.w[ekey(v, u)]) for u in nb], float)
        v = nb[rng.choice(len(nb), p=qw / qw.sum())]
        observe(v)
        if step in bset:
            npd = frozen.n_present_diag(); nhd = frozen.n_high_diag()
            scores[step] = score()
            cover[step] = {"verts": len(verts), "diags": len(encountered),
                           "frac_present": len(encountered) / npd if npd else 0.0,
                           "frac_high_seen": (sum(1 for d in encountered
                                                  if qround(frozen.w[d]) == 6) /
                                              nhd if nhd else 0.0)}
    return scores, cover
