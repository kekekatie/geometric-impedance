#!/usr/bin/env python3
"""
Is the fragility curve a threshold or a knee?

The coarse sweep showed the 8-fold address channel flat within noise from
disorder 0.00 to 0.10 (0.979, 0.983, 0.974) and then falling sharply. That shape
is consistent with a pinning threshold — the address channel holding until a
critical disorder and then giving way — but the grid was far too coarse to tell a
sharp transition from a gentle knee.

This samples finely through the suspect region, with enough seeds to separate
structure from noise, and records the flipped-vertex fraction alongside so the
curve can be plotted against actual damage rather than nominal amplitude.

A threshold has a location, which is a number that can be predicted and checked.
A knee is what everything does.
"""

import argparse
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KDTree

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from audit_with_nulls import adjacency
from matched_labels import matched_rate_labels
from multiplex_ab import substrate_disordered

EXTENT = 18


def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if y.sum() < 8 or (1 - y).sum() < 8:
        return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed)
    p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, p))


def one(amp, seed, baseline, interior=0.50, frac=0.05):
    lifts, par, perp, E = substrate_disordered(amp, EXTENT, seed=seed)
    n = len(par)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    active = np.sort(np.argsort(rad)[:int(round(interior * n))]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u, _ in E]]
                                         - par[[v for _, v in E]], axis=1)))
    q = KDTree(par).query_radius(par[active], r=3.0 * med)
    seeds = {active[k]: q[k].tolist() for k in range(len(active))}
    y, _ = matched_rate_labels(adjacency(n, E), active, seeds, fraction=frac)

    X = np.column_stack([perp, np.linalg.norm(perp, axis=1)])
    rng = np.random.default_rng(700 + seed)
    V = {tuple(r) for r in lifts}
    damage = len(baseline ^ V) / len(baseline | V)
    return damage, auc(X[active], y, seed), auc(X[rng.permutation(n)][active], y, seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args()

    amps = [0.00, 0.05, 0.08, 0.11, 0.14, 0.17, 0.20, 0.23, 0.26]
    base_lifts, _, _, _ = substrate_disordered(0.0, EXTENT, seed=0)
    baseline = {tuple(r) for r in base_lifts}

    print(f"8-fold (perpendicular dimension 2), {len(base_lifts)} vertices, "
          f"{args.seeds} seeds per point", flush=True)
    print(f"{'disorder':>9} {'damage':>9} {'address AUC':>20} {'shuffle':>9}", flush=True)

    rows = []
    for a in amps:
        r = [one(a, s, baseline) for s in range(args.seeds)]
        d = np.mean([x[0] for x in r])
        v = np.array([x[1] for x in r])
        s_ = np.mean([x[2] for x in r])
        rows.append((a, d, v.mean(), v.std(ddof=1)))
        print(f"{a:9.2f} {d:9.4f} {v.mean():11.4f} +-{v.std(ddof=1):.4f} {s_:9.4f}",
              flush=True)

    print(f"\n{'='*56}\nstep-to-step change in AUC\n{'='*56}", flush=True)
    print(f"{'from':>6} {'to':>6} {'d(AUC)':>10} {'d(damage)':>11} {'slope':>10}", flush=True)
    for i in range(1, len(rows)):
        a0, d0, m0, _ = rows[i - 1]
        a1, d1, m1, _ = rows[i]
        slope = (m1 - m0) / (d1 - d0) if d1 != d0 else float("nan")
        print(f"{a0:6.2f} {a1:6.2f} {m1-m0:10.4f} {d1-d0:11.4f} {slope:10.3f}", flush=True)

    print("\nA threshold shows a flat run of near-zero slopes then an abrupt jump.", flush=True)
    print("A knee shows slopes growing steadily from the start.", flush=True)


if __name__ == "__main__":
    main()
