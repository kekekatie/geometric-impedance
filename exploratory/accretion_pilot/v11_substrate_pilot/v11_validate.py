#!/usr/bin/env python3
"""
v11_validate.py -- run ALL construction & engine gates before the experiment.

Gates:
  G1 geometry validation (incl. real overlap/gap checks) on all 6 production patches
  G2 invalid-fixture rejection (proves the overlap/gap checks bite)
  G3 robust construction: zero degeneracies; discarded components reported
  G4 candidate diagonals unique & distinct from original edges
  G5 engine equivalence: substrate-general engine == v2 square engine, event-by-event
  G6 patch distinctness: chosen regular patches are not rigid-motion duplicates
  G7 history freezing: 3 eligible length-6 pairs per patch (else that patch FAILS)

Writes results/gate_report.txt and results/frozen_manifest.json. Exit status in the
report; the experiment script refuses to run unless all gates pass.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

import substrate_lib as sl

_HERE = os.path.dirname(os.path.abspath(__file__))
_V2DIR = os.path.join(os.path.dirname(_HERE), "v2_saturation")
sys.path.insert(0, _V2DIR)
import accretion_pilot_v2 as v2   # noqa: E402

RES = os.path.join(_HERE, "results")
os.makedirs(RES, exist_ok=True)

RADIUS = 10.0
JITTER = 0.30
OFFSET_CANDIDATES = [
    [0.30, 0.10, -0.25, -0.25, 0.10],
    [0.12, 0.31, -0.08, -0.20, -0.15],
    [-0.05, 0.22, 0.17, -0.29, -0.05],
    [0.20, -0.10, 0.05, 0.15, -0.30],
    [0.08, 0.19, -0.27, 0.11, -0.11],
    [-0.18, 0.24, -0.06, 0.09, -0.09],
]
HIST_LEN = 6
N_HIST_PAIRS = 3


# ---------------------------------------------------------------------------
def rigid_duplicate(subA, subB, tol=1e-3):
    """True if subB's vertex point-set == subA's under some D10 rigid motion +
    centroid translation."""
    A = np.array([subA.pos[v] for v in sorted(subA.pos)])
    B = np.array([subB.pos[v] for v in sorted(subB.pos)])
    if len(A) != len(B):
        return False
    A = A - A.mean(0); B = B - B.mean(0)
    Bset = set((round(x, 3), round(y, 3)) for x, y in B)
    for reflect in (1, -1):
        for kk in range(10):
            th = 2 * np.pi * kk / 10
            R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
            At = A.copy(); At[:, 0] *= reflect
            At = At @ R.T
            Aset = set((round(x, 3), round(y, 3)) for x, y in At)
            if len(Aset & Bset) >= len(Bset) - 2:     # allow tiny rounding slack
                return True
    return False


def gate_engine_equivalence():
    """G5: generalised engine == v2 square engine, event by event (canonical order)."""
    n = v2.GRID_N
    sub = sl.square_substrate(n)
    sw = sl.SubstrateWorld(sub)
    vw = v2.World()

    def sort_v2_adj():
        for k in list(vw.adj):
            vw.adj[k] = sorted(vw.adj[k])

    sort_v2_adj()

    def weights_equal():
        if set(sw.weight) != set(vw.weight):
            return False
        return all(abs(sw.weight[e] - vw.weight[e]) < 1e-12 for e in sw.weight)

    def active_equal():
        return set(sw.active) == set(vw.active)

    ok = True; detail = []
    # imposed history: v2's grid-edge staircase (guaranteed to use base edges)
    path = v2.staircase("upper")
    path_edges = list(zip(path[:-1], path[1:]))
    for _ in range(3):
        for u, v in path_edges:
            sw.reinforce(u, v); sw.grow_from_edge(u, v)
            vw.reinforce(u, v); vw.grow_from_edge(u, v)
            sort_v2_adj()
    if not (weights_equal() and active_equal()):
        ok = False; detail.append("history-phase mismatch")
    # subsequent walk: matched RNG, canonical order, compare chosen step each time
    rng_s = np.random.default_rng(12345)
    rng_v = np.random.default_rng(12345)
    vs = v2.vid(*v2.PROBE); vv = v2.vid(*v2.PROBE)
    for step in range(300):
        ns = sw.weighted_step(vs, rng_s)
        nv = vw.adj[vv][rng_v.choice(
            len(vw.adj[vv]),
            p=np.array([vw.weight[v2.ekey(vv, u)] for u in vw.adj[vv]]) /
            sum(vw.weight[v2.ekey(vv, u)] for u in vw.adj[vv]))]
        if ns != nv:
            ok = False; detail.append(f"step {step}: chose {ns} vs {nv}"); break
        sw.reinforce(vs, ns); sw.grow_from_edge(vs, ns)
        vw.reinforce(vv, nv); vw.grow_from_edge(vv, nv); sort_v2_adj()
        vs = ns; vv = nv
        if not (weights_equal() and active_equal()):
            ok = False; detail.append(f"step {step}: state mismatch"); break
    return ok, (detail or ["event-by-event identical over history + 300 steps"])


def main():
    lines = ["# v11 GATE REPORT", ""]
    gate_pass = {}

    # select 3 distinct regular offsets
    chosen = []
    subs_reg = []
    for off in OFFSET_CANDIDATES:
        sub = sl.Substrate.pentagrid(RADIUS, off)
        if any(rigid_duplicate(sub, s) for s in subs_reg):
            lines.append(f"# offset {off} -> rigid-duplicate of an earlier patch; skip")
            continue
        chosen.append(off); subs_reg.append(sub)
        if len(chosen) == 3:
            break
    gate_pass["G6_distinct_regular_patches"] = (len(chosen) == 3)
    lines.append(f"[G6] distinct regular offsets chosen: {len(chosen)}/3 "
                 f"-> {'PASS' if len(chosen)==3 else 'FAIL'}")

    # build all 6 patches (matched regular/perturbed pairs share offset)
    patches = {}
    for i, off in enumerate(chosen):
        patches[("regular", i)] = subs_reg[i]
        patches[("perturbed", i)] = sl.Substrate.pentagrid(RADIUS, off,
                                                           jitter_amp=JITTER, seed=i)

    # G1/G3/G4 validation on all 6
    g1 = g3 = g4 = True
    for (arm, i), sub in patches.items():
        ok, ch = sl.validate(sub)
        g1 &= ok
        g3 &= (sub.degeneracies == 0)
        g4 &= ch["diagonals_unique"][0] and ch["diagonals_not_original"][0]
        fails = [k for k, (p, v) in ch.items() if not p]
        lines.append(f"[G1] {arm}#{i}: V={sub.V} E={sub.Ecount} F={sub.F} "
                     f"degen={sub.degeneracies} discarded={sub.discarded_components} "
                     f"-> {'PASS' if ok else 'FAIL ' + str(fails)}")
    gate_pass["G1_geometry_valid"] = g1
    gate_pass["G3_zero_degeneracies"] = g3
    gate_pass["G4_diagonals_unique_distinct"] = g4

    # G2 invalid-fixture rejection (two fixtures)
    e0, e1 = sl.E[0], sl.E[1]
    r1 = [np.array([0., 0.]), e0, e0 + e1, e1]
    r2 = [p + 0.3 * e0 for p in r1]
    fx1 = sl.Substrate.from_faces(list(r1) + list(r2),
                                  [((0, 1, 2, 3), "thick"), ((4, 5, 6, 7), "thick")])
    ok1, _ = sl.validate(fx1)
    fx2 = sl.Substrate.pentagrid(3.0, sl.DEFAULT_OFFSETS)
    biv = max(fx2.boundary_distance(), key=lambda v: fx2.boundary_distance()[v])
    fx2.pos[biv] = fx2.pos[biv] + np.array([0.9, 0.6])
    ok2, _ = sl.validate(fx2)
    gate_pass["G2_invalid_fixtures_rejected"] = (not ok1) and (not ok2)
    lines.append(f"[G2] invalid fixtures rejected: overlap={not ok1}, "
                 f"corrupt={not ok2} -> "
                 f"{'PASS' if (not ok1 and not ok2) else 'FAIL'}")

    # G5 engine equivalence
    okE, detE = gate_engine_equivalence()
    gate_pass["G5_engine_equivalence"] = okE
    lines.append(f"[G5] engine equivalence vs v2 square: "
                 f"{'PASS' if okE else 'FAIL'} ({detE[0]})")

    # G7 history freezing
    g7 = True
    manifest = {"radius": RADIUS, "jitter": JITTER, "hist_len": HIST_LEN,
                "offsets": chosen, "patches": {}}
    for (arm, i), sub in patches.items():
        pairs = sl.make_history_pairs(sub, k=N_HIST_PAIRS, length=HIST_LEN)
        ok = (len(pairs) == N_HIST_PAIRS)
        g7 &= ok
        manifest["patches"][f"{arm}_{i}"] = {
            "V": sub.V, "E": sub.Ecount, "F": sub.F,
            "shape_counts": sub.shape_counts(),
            "n_history_pairs": len(pairs),
            "history": [{"S": p["S"], "E": p["E"], "len": p["len"],
                         "shared_edges": p["shared_edges"],
                         "shared_internal_vertices": p["shared_internal_vertices"]}
                        for p in pairs]}
        lines.append(f"[G7] {arm}#{i}: {len(pairs)}/{N_HIST_PAIRS} history pairs "
                     f"(shared_edges={[p['shared_edges'] for p in pairs]}) "
                     f"-> {'PASS' if ok else 'FAIL'}")
    gate_pass["G7_histories_frozen"] = g7

    all_pass = all(gate_pass.values())
    lines += ["", "# SUMMARY"]
    for k, v in gate_pass.items():
        lines.append(f"  {k}: {'PASS' if v else 'FAIL'}")
    lines.append(f"\nALL GATES: {'PASS' if all_pass else 'FAIL'}")
    with open(os.path.join(RES, "gate_report.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    manifest["all_gates_pass"] = all_pass
    with open(os.path.join(RES, "frozen_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("\n".join(lines))
    print("\nWrote results/gate_report.txt and results/frozen_manifest.json")
    return all_pass


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
