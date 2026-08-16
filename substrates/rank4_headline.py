#!/usr/bin/env python3
"""
The headline re-run, on the rank-4 congruence family.

Protocol fixed in advance in PREDICTION_rank4_headline.md. Nothing here departs
from it. The hypotheses:

    H1  field          silver > platinum > golden   (previous ordering replicates)
    H2  fragmentation  silver > golden > platinum   (perimeter/area 1.657/1.789/1.856)
    H0  null           no ordering survives damage-matching

Both agree silver leads, so only the golden/platinum contrast discriminates. Under
H2 that gap should be about half the silver/golden gap, since the covariate is
unevenly spaced.

Two damage models are run. The primary is the pre-registered one: jitter the two
Galois perpendicular coordinates before the acceptance test. The secondary also
jitters the extra coordinate, which lets a point be accepted through a different
preimage - a congruence-class flip. The asymmetry matters because 8-fold has no
extra coordinate at all, so under the primary model its whole perpendicular space
is perturbed while the fragmented members have only part of theirs perturbed.
Damage-matching absorbs the difference in amount but not necessarily in kind, so
both are reported and labelled.
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
from generate_rank4 import build_edges, classes_of, generate, structure
from matched_labels import matched_rate_labels

EXTENT = {8: 14, 10: 16, 12: 16}
NAME = {8: "silver (8-fold)", 10: "golden (10-fold)", 12: "platinum (12-fold)"}
ACTIVE = 1200
AMPS = [0.00, 0.03, 0.06, 0.09, 0.12, 0.16, 0.20, 0.25]


def auc(X, y, seed=0):
    y = np.asarray(y, int)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    if X.shape[1] == 0 or y.sum() < 8 or (1 - y).sum() < 8:
        return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed)
    p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, p))


def one(N, amp, seed, baseline, full_perp):
    lifts, par, perp, ustar = generate(N, EXTENT[N], disorder=amp, seed=seed,
                                       disorder_extra=full_perp)
    E = build_edges(lifts, N, ustar)
    n = len(par)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    act = np.sort(np.argsort(rad)[:ACTIVE]).tolist()

    med = float(np.median(np.linalg.norm(par[[u for u, _ in E]]
                                         - par[[v for _, v in E]], axis=1)))
    q = KDTree(par).query_radius(par[act], r=3.0 * med)
    seeds = {act[k]: q[k].tolist() for k in range(len(act))}
    y, _ = matched_rate_labels(adjacency(n, E), act, seeds, fraction=0.05)

    X = np.column_stack([perp, np.linalg.norm(perp, axis=1)])
    cls = classes_of(lifts, N).astype(float)[:, None]
    rng = np.random.default_rng(1300 + seed)
    V = {tuple(r) for r in lifts}
    dmg = len(baseline ^ V) / len(baseline | V)
    return (dmg, n,
            auc(X[act], y, seed),
            auc(X[rng.permutation(n)][act], y, seed),
            auc(cls[act], y, seed) if structure(N)["classes"] > 1 else float("nan"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--full-perp", action="store_true",
                    help="secondary model: also jitter the extra coordinate")
    args = ap.parse_args()

    tag = "SECONDARY (full perpendicular jitter)" if args.full_perp \
        else "PRIMARY (pre-registered: Galois-plane jitter)"
    print(f"### {tag}")
    print(f"active set {ACTIVE}, {args.seeds} seeds, "
          f"extents {EXTENT}\n", flush=True)

    curves = {}
    for N in (8, 10, 12):
        base, bpar, _, _ = generate(N, EXTENT[N])
        baseline = {tuple(r) for r in base}
        print(f"{NAME[N]}   patch {len(base)} vertices, "
              f"active {ACTIVE} = {ACTIVE/len(base):.1%}", flush=True)
        print(f"{'amp':>6} {'damage':>8} {'ADDRESS AUC':>16} {'shuffle':>9} "
              f"{'class':>8}", flush=True)
        rows = []
        for a in AMPS:
            r = np.array([one(N, a, s, baseline, args.full_perp)
                          for s in range(args.seeds)])
            m, sd = np.nanmean(r, axis=0), np.nanstd(r, axis=0, ddof=1)
            rows.append((m[0], m[2], sd[2]))
            print(f"{a:6.2f} {m[0]:8.4f} {m[2]:10.4f} +-{sd[2]:.4f} "
                  f"{m[3]:9.4f} {m[4]:8.4f}", flush=True)
        curves[N] = np.array(rows)
        print(flush=True)

    print("=" * 72)
    print("AUC interpolated at matched measured damage")
    print("=" * 72)
    print(f"{'damage':>8} {'silver':>10} {'golden':>10} {'platinum':>10} "
          f"{'s-g gap':>9} {'g-p gap':>9}", flush=True)
    for d in (0.05, 0.10, 0.15, 0.20, 0.25):
        v = {}
        for N in (8, 10, 12):
            c = curves[N]
            v[N] = float(np.interp(d, c[:, 0], c[:, 1])) if d <= c[:, 0].max() \
                else float("nan")
        sg, gp = v[8] - v[10], v[10] - v[12]
        print(f"{d:8.2f} {v[8]:10.4f} {v[10]:10.4f} {v[12]:10.4f} "
              f"{sg:9.4f} {gp:9.4f}", flush=True)

    print("\nH1 field         predicts silver > platinum > golden")
    print("H2 fragmentation predicts silver > golden > platinum, "
          "with g-p gap about half s-g")
    print("H0 null          predicts no stable ordering")


if __name__ == "__main__":
    main()
