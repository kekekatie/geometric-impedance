#!/usr/bin/env python3
"""
Confirmatory run for the sealed static test (PREREG_degree_controlled_address.md).

Primary metric, per family per measured-damage level, over >=8 seeds:

    S_N = AUC(degree (+) address) - AUC(degree)

the address's readability of privileged sites BEYOND what scalar degree already
gives. address = the two Galois perpendicular coords + radius; degree recomputed on
the damaged tiling. Reports the absolute AUCs alongside so a ceiling-compressed
S_N ~ 0 (address redundant with degree) is not confused with an empty channel.

Degree-stratified null: permute the address rows within degree deciles, preserving
the degree-address coupling and breaking only within-stratum address signal; S_null
must sit at ~0. At zero damage the discrete-class increment over degree+address is
also reported (prereg P2).

Damage is Galois-plane jitter, read as measured flipped-vertex fraction against the
clean patch. The secondary reconstruction metric and the decision rule (primary and
secondary must agree) come in a second script once this shows its ordering.
"""

import argparse
import sys

import numpy as np
from sklearn.neighbors import KDTree

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, classes_of, generate, structure
from audit_with_nulls import adjacency
from matched_labels import matched_rate_labels
from rank4_headline import ACTIVE, EXTENT, auc

NAME = {8: "silver", 10: "golden", 12: "platinum"}
AMPS = [0.0, 0.06, 0.12, 0.20, 0.25]


def stratified_permute(addr, deg, rng, nbins=10):
    """Permute address rows within degree deciles (breaks address, keeps degree)."""
    out = addr.copy()
    for b in np.array_split(np.argsort(deg), nbins):
        if len(b) > 1:
            out[b] = addr[b][rng.permutation(len(b))]
    return out


def one(N, amp, seed, baseline):
    st = structure(N)
    lifts, par, perp, ustar = generate(N, EXTENT[N], disorder=amp, seed=seed)
    E = build_edges(lifts, N, ustar)
    n = len(par)
    adj = adjacency(n, E)
    deg = np.array([len(adj[i]) for i in range(n)], float)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    act = np.sort(np.argsort(rad)[:ACTIVE]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u, _ in E]]
                                         - par[[v for _, v in E]], axis=1)))
    q = KDTree(par).query_radius(par[act], r=3.0 * med)
    seeds = {act[k]: q[k].tolist() for k in range(len(act))}
    y, _ = matched_rate_labels(adj, act, seeds, fraction=0.05)

    addr = np.column_stack([perp, np.linalg.norm(perp, axis=1)])
    D = deg[:, None]
    a_deg = auc(D[act], y, seed)
    a_addr = auc(addr[act], y, seed)
    a_dp = auc(np.column_stack([D, addr])[act], y, seed)
    rng = np.random.default_rng(5000 + seed)
    a_dp_null = auc(np.column_stack([D, stratified_permute(addr, deg, rng)])[act], y, seed)

    cls_inc = np.nan
    if amp == 0.0 and st["classes"] > 1:
        cl = classes_of(lifts, N).astype(float)[:, None]
        a_dpc = auc(np.column_stack([D, addr, cl])[act], y, seed)
        cls_inc = a_dpc - a_dp

    V = {tuple(r) for r in lifts}
    dmg = len(baseline ^ V) / len(baseline | V)
    return dmg, a_deg, a_addr, a_dp, a_dp - a_deg, a_dp_null - a_deg, cls_inc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    args = ap.parse_args()

    print(f"Degree-controlled static address channel, {args.seeds} seeds\n")
    for N in (8, 10, 12):
        base, _, _, _ = generate(N, EXTENT[N])
        baseline = {tuple(r) for r in base}
        print(f"=== {NAME[N]} ({N}-fold) ===")
        print(f"{'damage':>7} {'AUC_deg':>8} {'AUC_addr':>9} {'AUC_d+a':>8} "
              f"{'S (a|d)':>9} {'S_null':>8}")
        cls_incs = []
        for amp in AMPS:
            rows = np.array([one(N, amp, s, baseline) for s in range(args.seeds)])
            m = np.nanmean(rows, axis=0)
            e = np.nanstd(rows, axis=0, ddof=1) / np.sqrt(args.seeds)
            print(f"{m[0]:>7.3f} {m[1]:>8.3f} {m[2]:>9.3f} {m[3]:>8.3f} "
                  f"{m[4]:>6.3f}±{e[4]:.3f} {m[5]:>8.3f}", flush=True)
            if amp == 0.0:
                cls_incs = rows[:, 6]
        ci = cls_incs[~np.isnan(cls_incs)]
        if len(ci):
            print(f"   zero-damage class increment over degree+address: "
                  f"{ci.mean():+.3f} ± {ci.std(ddof=1)/np.sqrt(len(ci)):.3f}")
        print()


if __name__ == "__main__":
    main()
