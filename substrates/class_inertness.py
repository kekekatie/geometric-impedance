#!/usr/bin/env python3
"""
Is the congruence class inert? Re-testing a claim this project has been leaning on.

`discrete_vs_continuous.py` concluded that Penrose's discrete address component -
the lift-sum index selecting one of four pentagons - carries almost no address
information: AUC 0.5398 at zero disorder, rising only to 0.5696 at disorder 0.20.
That finding was used to justify treating the rank-4 reinterpretation as safe,
on the grounds that the congruence label was a dead coordinate.

The rank-4 headline run contradicts it. The 10-fold congruence class reads AUC
0.823 at zero disorder under the headline protocol.

Both cannot be right about the same thing, so this separates the candidates:

  1. The substrates differ. The old test used *singular* Penrose, whose class 0 is
     empty and which has four pentagons. The new one uses the *generic* 10-fold
     member, with all five classes occupied. Genuinely different point sets.
  2. The old test was underpowered. It used a different active-set size and crop
     and a smaller patch, so a real signal may have been lost in noise.

Measured here under one protocol, held identical across substrates: active set of
matched size, `matched_rate_labels` at fraction 0.05, gradient boosting, 3-fold CV.

Also reports how vertex degree varies by class, since a mechanical explanation is
available and should be checked before anything subtler is entertained: if classes
carry systematically different local environments, the class predicts degree, and
degree predicts retention.
"""

import argparse
import sys
from collections import Counter

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KDTree

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import generate_penrose as GP
import generate_rank4 as R4
from audit_with_nulls import adjacency
from matched_labels import matched_rate_labels


def auc(X, y, seed=0):
    y = np.asarray(y, int)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    if y.sum() < 8 or (1 - y).sum() < 8:
        return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed)
    p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, p))


def assess(name, par, perp, cls, E, active, seed):
    n = len(par)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    act = np.sort(np.argsort(rad)[:active]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u, _ in E]]
                                         - par[[v for _, v in E]], axis=1)))
    q = KDTree(par).query_radius(par[act], r=3.0 * med)
    seeds = {act[k]: q[k].tolist() for k in range(len(act))}
    y, _ = matched_rate_labels(adjacency(n, E), act, seeds, fraction=0.05)

    deg = np.zeros(n, int)
    for u, v in E:
        deg[u] += 1
        deg[v] += 1

    X = np.column_stack([perp, np.linalg.norm(perp, axis=1)])
    a_cls = auc(cls[act].astype(float), y, seed)
    a_perp = auc(X[act], y, seed)
    a_both = auc(np.column_stack([X, cls.astype(float)])[act], y, seed)

    # Mechanical check: does the class carry a different local environment?
    by = {}
    for c in sorted(set(cls.tolist())):
        m = cls == c
        by[c] = (int(m.sum()), float(deg[m].mean()))
    return a_cls, a_perp, a_both, by, len(act)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--active", type=int, default=1200)
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()

    print(f"active set {args.active}, {args.seeds} seeds, fraction 0.05\n")
    print(f"{'substrate':<28} {'verts':>6} {'CLASS':>8} {'perp 2D':>9} "
          f"{'both':>8}")
    print("-" * 64)

    rows = {}
    for label, build in (
        ("Penrose (singular, Z^5)",
         lambda: (lambda L: (L[1], L[2][:, :2], L[0].sum(1) % 5,
                             GP.build_edges(L[0])))(
             GP.generate(16, np.array([0.1237, 0.0891])))),
        ("rank-4 10-fold (generic)",
         lambda: (lambda L: (L[1], L[2], R4.classes_of(L[0], 10),
                             R4.build_edges(L[0], 10, L[3])))(
             R4.generate(10, 16))),
        ("rank-4 12-fold (generic)",
         lambda: (lambda L: (L[1], L[2], R4.classes_of(L[0], 12),
                             R4.build_edges(L[0], 12, L[3])))(
             R4.generate(12, 16))),
    ):
        par, perp, cls, E = build()
        r = [assess(label, par, perp, cls, E, args.active, s)
             for s in range(args.seeds)]
        ac = np.mean([x[0] for x in r])
        ap_ = np.mean([x[1] for x in r])
        ab = np.mean([x[2] for x in r])
        rows[label] = (ac, r[0][3])
        print(f"{label:<28} {len(par):>6} {ac:>8.4f} {ap_:>9.4f} {ab:>8.4f}")

    print("\nclass occupancy and mean degree (mechanical explanation check)")
    print("-" * 64)
    for label, (ac, by) in rows.items():
        parts = "  ".join(f"c{c}:n={n},deg={d:.2f}" for c, (n, d) in by.items())
        print(f"{label}\n    {parts}")

    print("\nOld claim: Penrose discrete component inert at 0.5398.")
    print("If Penrose now reads high too, that finding was underpowered and")
    print("everything resting on it needs revisiting. If Penrose stays low while")
    print("the generic 10-fold reads high, singular and generic members differ.")


if __name__ == "__main__":
    main()
