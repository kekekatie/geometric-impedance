#!/usr/bin/env python3
"""
Secondary metric for the sealed static test (PREREG_degree_controlled_address.md,
section 2): direct address reconstruction.

Predict each vertex's TRUE perpendicular coordinates (the noise-free projection
lifts @ perp4) from tiling-LOCAL structural features -- degree, the neighbour-degree
multiset, and a small graph ball -- and measure reconstruction R^2 by CV, watched as
it degrades under damage. This conditions on nothing downstream of the address (it
predicts the address FROM structure), so it does not share the mediator profile of
the primary AUC-increment metric. Per the sealed decision rule, an ordering is claimed
only if this secondary and the primary AGREE on the fragility (decay) ordering.

Reported: R^2 clean and under damage, per family, 8 seeds, so both the level and the
decay can be compared with the primary's honest-channel curve. No claim here; this is
the confirmer, run exactly as written.
"""

import argparse
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, generate, structure
from audit_with_nulls import adjacency
from rank4_headline import ACTIVE, EXTENT

NAME = {8: "silver", 10: "golden", 12: "platinum"}
AMPS = [0.0, 0.06, 0.12, 0.20, 0.25]
NBR = 8                                   # neighbour-degree slots


def local_features(adj, deg):
    n = len(adj)
    X = np.zeros((n, 1 + NBR + 1))
    for i in range(n):
        X[i, 0] = deg[i]
        nd = sorted((deg[j] for j in adj[i]), reverse=True)[:NBR]
        X[i, 1:1 + len(nd)] = nd
        ball = set(adj[i])
        for j in adj[i]:
            ball |= adj[j]
        X[i, -1] = len(ball)
    return X


def cv_r2(X, Y, seed):
    """Mean CV R^2 over the two perpendicular coordinates."""
    kf = KFold(3, shuffle=True, random_state=seed)
    scores = []
    for c in range(Y.shape[1]):
        pred = np.zeros(len(Y))
        for tr, te in kf.split(X):
            m = HistGradientBoostingRegressor(max_iter=200, random_state=0)
            m.fit(X[tr], Y[tr, c])
            pred[te] = m.predict(X[te])
        scores.append(r2_score(Y[:, c], pred))
    return float(np.mean(scores))


def one(N, amp, seed, baseline):
    st = structure(N)
    lifts, par, perp, ustar = generate(N, EXTENT[N], disorder=amp, seed=seed)
    E = build_edges(lifts, N, ustar)
    n = len(par)
    adj = adjacency(n, E)
    deg = np.array([len(adj[i]) for i in range(n)], float)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    act = np.sort(np.argsort(rad)[:ACTIVE])
    X = local_features(adj, deg)[act]
    Y = (lifts @ st["perp4"])[act]                       # true, noise-free address
    r2 = cv_r2(X, Y, seed)
    V = {tuple(r) for r in lifts}
    dmg = len(baseline ^ V) / len(baseline | V)
    return dmg, r2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    args = ap.parse_args()
    print(f"Secondary: address reconstruction R^2 from local structure, "
          f"{args.seeds} seeds\n")
    for N in (8, 10, 12):
        base, _, _, _ = generate(N, EXTENT[N])
        baseline = {tuple(r) for r in base}
        print(f"=== {NAME[N]} ({N}-fold) ===")
        print(f"{'damage':>7} {'recon R^2':>12}")
        clean_r2 = None
        for amp in AMPS:
            rows = np.array([one(N, amp, s, baseline) for s in range(args.seeds)])
            m = rows.mean(0)
            e = rows.std(0, ddof=1) / np.sqrt(args.seeds)
            if amp == 0.0:
                clean_r2 = m[1]
            print(f"{m[0]:>7.3f} {m[1]:>8.3f}±{e[1]:.3f}", flush=True)
        print(f"   clean R^2 = {clean_r2:.3f}\n")


if __name__ == "__main__":
    main()
