#!/usr/bin/env python3
"""
v11_experiment.py -- the bounded substrate memory experiment (runs only if gates
passed; this script re-checks the frozen manifest exists).

Design (frozen; see DESIGN_NOTE_v11.md):
  * 2 arms (regular / perturbed) x 3 patches x 3 history pairs = 18 cells.
  * Per cell: Growing with imposed histories A and B, 200 paired seeds (common
    random numbers), 10,000 steps, 8 checkpoints. 3 history passes; reset to S.
  * No-imposed-history Growing null per patch (labels assigned independently of
    dynamics in analysis).
  * Frozen reader S_high (v5 one-bit added-diagonal, proximity sign). Checkpoint
    reads do not alter trajectories.
Outputs scalar readings only (full-snapshot size is large -- see verdict); a small
subsample of full snapshots is retained compressed.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

import substrate_lib as sl

_HERE = os.path.dirname(os.path.abspath(__file__))
_V2DIR = os.path.join(os.path.dirname(_HERE), "v2_saturation")
sys.path.insert(0, _V2DIR)
import accretion_pilot_v2 as v2   # noqa: E402

RES = os.path.join(_HERE, "results")
BASE_SEED = v2.BASE_SEED
RADIUS = 10.0; JITTER = 0.30; HIST_LEN = 6; N_PAIRS = 3
NSEED = 200; NSTEPS = 10000
CPS = [0, 100, 200, 400, 1000, 2000, 5000, 10000]
COLS = ["S_high", "n_high", "n_active", "frac_active", "headroom",
        "total_weight", "struct_access", "eff_alt", "bvisit_frac"]


def build_world_and_impose(sub, path):
    w = sl.SubstrateWorld(sub)
    for _ in range(3):
        for a, b in zip(path[:-1], path[1:]):
            w.reinforce(a, b); w.grow_from_edge(a, b)
    return w


def snap(w, coeff, S):
    return [w.s_high(coeff), w.n_high(), w.n_activations, w.frac_active(),
            w.headroom(), w.total_weight(), w.structural_access(S),
            w.effective_alternatives(S),
            (w.boundary_visits / w.total_steps if w.total_steps else 0.0)]


def evolve(sub, path, coeff, S, seed):
    w = build_world_and_impose(sub, path)
    rng = np.random.default_rng(BASE_SEED + seed)
    out = {0: snap(w, coeff, S)}
    v = S
    for step in range(1, NSTEPS + 1):
        nxt = w.weighted_step(v, rng)
        w.reinforce(v, nxt); w.grow_from_edge(v, nxt); v = nxt
        if step in CPS:
            out[step] = snap(w, coeff, S)
    return out, w


def evolve_null(sub, S, coeffs, seed):
    """No imposed history; record all 3 pair readers' S_high + shared opportunity."""
    w = sl.SubstrateWorld(sub)
    rng = np.random.default_rng(BASE_SEED + seed)
    rec = {}

    def snap_null():
        base = [w.n_active, w.frac_active(), w.headroom(), w.total_weight(),
                w.structural_access(S), w.effective_alternatives(S),
                (w.boundary_visits / w.total_steps if w.total_steps else 0.0)]
        highs = [w.s_high(c) for c in coeffs]
        return highs, base
    rec[0] = snap_null()
    v = S
    for step in range(1, NSTEPS + 1):
        nxt = w.weighted_step(v, rng)
        w.reinforce(v, nxt); w.grow_from_edge(v, nxt); v = nxt
        if step in CPS:
            rec[step] = snap_null()
    return rec


def main():
    if not os.path.exists(os.path.join(RES, "frozen_manifest.json")):
        print("frozen_manifest.json missing -- run v11_validate.py first."); return
    man = json.load(open(os.path.join(RES, "frozen_manifest.json")))
    if not man.get("all_gates_pass"):
        print("gates did not pass -- refusing to run."); return
    offsets = man["offsets"]

    patches = {}
    hists = {}
    coeffs = {}
    for i, off in enumerate(offsets):
        patches[("regular", i)] = sl.Substrate.pentagrid(RADIUS, off)
        patches[("perturbed", i)] = sl.Substrate.pentagrid(RADIUS, off,
                                                           jitter_amp=JITTER, seed=i)
    for key, sub in patches.items():
        hp = sl.make_history_pairs(sub, k=N_PAIRS, length=HIST_LEN)
        hists[key] = hp
        coeffs[key] = [sl.reader_coefficients(sub, h) for h in hp]

    fmain = open(os.path.join(RES, "raw_main.csv"), "w")
    fmain.write("arm,patch,pair,history,seed,checkpoint," + ",".join(COLS) + "\n")
    fnull = open(os.path.join(RES, "raw_null.csv"), "w")
    fnull.write("arm,patch,seed,checkpoint,pair,S_high,n_active,frac_active,"
                "headroom,total_weight,struct_access,eff_alt,bvisit_frac\n")
    sub_snaps = {}                     # small subsample of full snapshots

    t0 = time.time(); done_cells = 0; total_cells = len(patches) * N_PAIRS
    for key, sub in patches.items():
        arm, i = key
        for j, h in enumerate(hists[key]):
            coeff = coeffs[key][j]; S = h["S"]
            for seed in range(NSEED):
                for hk, path in (("A", h["pathA"]), ("B", h["pathB"])):
                    out, w = evolve(sub, path, coeff, S, seed)
                    for cp, vals in out.items():
                        fmain.write(f"{arm},{i},{j},{hk},{seed},{cp}," +
                                    ",".join(f"{x:.5f}" for x in vals) + "\n")
                    if seed < 2 and j == 0:      # subsample full snapshots
                        sub_snaps[f"{arm}_{i}_{hk}_{seed}"] = np.array(
                            [w.weight.get(e, 0.0) for e in sorted(w.weight)])
            done_cells += 1
            print(f"  cell {done_cells}/{total_cells} [{arm}#{i} pair{j}] "
                  f"elapsed {(time.time()-t0)/60:.1f} min", flush=True)
        # null per patch (reset to pair-0 S)
        S0 = hists[key][0]["S"]
        for seed in range(NSEED):
            rec = evolve_null(sub, S0, coeffs[key], seed)
            for cp, (highs, base) in rec.items():
                for j in range(N_PAIRS):
                    fnull.write(f"{arm},{i},{seed},{cp},{j},{highs[j]:.5f}," +
                                ",".join(f"{x:.5f}" for x in base) + "\n")
    fmain.close(); fnull.close()
    np.savez_compressed(os.path.join(RES, "subsample_snapshots.npz"), **sub_snaps)

    with open(os.path.join(RES, "experiment_config.json"), "w") as f:
        json.dump({"radius": RADIUS, "jitter": JITTER, "hist_len": HIST_LEN,
                   "n_pairs": N_PAIRS, "n_seeds": NSEED, "n_steps": NSTEPS,
                   "checkpoints": CPS, "base_seed": BASE_SEED, "offsets": offsets,
                   "primary_checkpoint": 2000,
                   "reader": "S_high one-bit added-diagonal proximity sign (frozen)",
                   "runtime_min": round((time.time() - t0) / 60, 1),
                   "env": {"numpy": np.__version__}}, f, indent=2)
    with open(os.path.join(RES, "EXPERIMENT_DONE"), "w") as f:
        f.write(f"done in {(time.time()-t0)/60:.1f} min\n")
    print(f"EXPERIMENT DONE in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
