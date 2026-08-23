#!/usr/bin/env python3
"""
Secondary metric v2 (repaired), frozen in PREREG_degree_controlled_address.md
Amendment 1, run on fresh offsets not used in the diagnostic.

Address reconstruction from the VERTEX TYPE (canonical cyclic sequence of incident
edge directions), by a type -> mean-address lookup, validated HELD-OUT-OFFSET: train
the lookup on some window offsets, test on a fresh unseen offset. Target is the
current-state, offset-free true address a . perp4. Guards against the spatial
autocorrelation that inflates a random vertex split (reported alongside for contrast).

Outputs per family:
  - R^2_type (held-out-offset) vs damage, and its decay Delta R^2;
  - R^2_deg  (held-out-offset) and the clean type-over-degree increment
    R^2_type - R^2_deg  (the "vertex type conditional on degree" decomposition);
  - R^2_type random-split at clean (inflation check).

Decision rule (amended): clean level need NOT match the primary ordering; agreement =
the family with the largest unique address channel (primary: golden) shows a
correspondingly measurable loss of reconstructible address (largest decay).
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, generate, structure
from audit_with_nulls import adjacency
from phason_energy import vertex_types
from rank4_headline import ACTIVE, EXTENT

NAME = {8: "silver", 10: "golden", 12: "platinum"}
# Fresh offsets, distinct from the diagnostic default (0.1123, 0.0847).
OFFSETS = [(0.31, 0.19), (0.07, 0.41), (0.23, 0.05), (0.44, 0.28)]
AMPS = [0.0, 0.06, 0.12, 0.20, 0.25]


def lookup_r2(tr_keys, tr_addr, te_keys, te_addr):
    """R^2 of a key -> mean-address lookup trained on (tr) and tested on (te)."""
    sums, cnts = {}, {}
    for k, a in zip(tr_keys, tr_addr):
        if k in sums:
            sums[k] += a
            cnts[k] += 1
        else:
            sums[k] = a.astype(float).copy()
            cnts[k] = 1
    grand = tr_addr.mean(0)
    means = {k: sums[k] / cnts[k] for k in sums}
    pred = np.array([means.get(k, grand) for k in te_keys])
    ss_res = ((te_addr - pred) ** 2).sum(0)
    ss_tot = ((te_addr - te_addr.mean(0)) ** 2).sum(0)
    return 1.0 - float(np.mean(ss_res / np.where(ss_tot > 0, ss_tot, 1.0)))


def heldout_offset_r2(data):
    """data: list of (keys_list, addr_array), one per offset. Rotate held-out offset."""
    scores = []
    for i in range(len(data)):
        tr_keys, tr_addr = [], []
        for j in range(len(data)):
            if j != i:
                tr_keys += data[j][0]
                tr_addr.append(data[j][1])
        scores.append(lookup_r2(tr_keys, np.vstack(tr_addr), data[i][0], data[i][1]))
    return float(np.mean(scores))


def random_split_r2(data, seed=0, folds=4):
    keys = [k for d in data for k in d[0]]
    addr = np.vstack([d[1] for d in data])
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(keys))
    scores = []
    for f in np.array_split(idx, folds):
        te = set(f.tolist())
        tr_i = [i for i in range(len(keys)) if i not in te]
        scores.append(lookup_r2([keys[i] for i in tr_i], addr[tr_i],
                                [keys[i] for i in f], addr[f]))
    return float(np.mean(scores))


def collect(N, amp):
    st = structure(N)
    star, K, par4, perp4 = st["star"], st["K"], st["par4"], st["perp4"]
    tdata, ddata = [], []
    for i, o in enumerate(OFFSETS):
        lifts, par, _, ustar = generate(N, EXTENT[N], offset=np.array(o),
                                        disorder=amp, seed=i)
        E = build_edges(lifts, N, ustar)
        n = len(par)
        adj = adjacency(n, E)
        deg = [len(adj[k]) for k in range(n)]
        rad = np.linalg.norm(par - par.mean(0), axis=1)
        act = np.sort(np.argsort(rad)[:ACTIVE])
        addr = (lifts @ perp4)[act]
        vt = vertex_types(lifts, ustar, star, K, par4)
        tdata.append(([vt[a] for a in act], addr))
        ddata.append(([deg[a] for a in act], addr))
    return tdata, ddata


def main():
    print("Secondary v2: held-out-offset address reconstruction from vertex type\n")
    for N in (8, 10, 12):
        print(f"=== {NAME[N]} ({N}-fold) ===")
        print(f"{'damage(amp)':>11} {'R2_type(HO)':>12} {'R2_deg(HO)':>11} "
              f"{'type|deg':>9} {'R2_type(rand)':>14}")
        clean_type = None
        for amp in AMPS:
            td, dd = collect(N, amp)
            r2t = heldout_offset_r2(td)
            r2d = heldout_offset_r2(dd)
            rand = random_split_r2(td) if amp == 0.0 else np.nan
            if amp == 0.0:
                clean_type = r2t
            inc = r2t - r2d
            print(f"{amp:>11.2f} {r2t:>12.3f} {r2d:>11.3f} {inc:>9.3f} "
                  f"{rand:>14.3f}", flush=True)
        # decay
        td, _ = collect(N, AMPS[-1])
        print(f"   clean R2_type(HO) = {clean_type:.3f}; "
              f"decay to amp {AMPS[-1]} = {clean_type - heldout_offset_r2(td):+.3f}\n")


if __name__ == "__main__":
    main()
