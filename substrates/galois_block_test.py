#!/usr/bin/env python3
"""
Gate test: is the address carried only by the Galois-conjugate plane?

The cyclotomic Z^4 family matched perpendicular dimension but broke the tiling
(see TILING_CONFOUND.md). The Z^n family tiles properly at all three folds but
appears to vary perpendicular dimension: 2, 3, 4 for 8-, 10-, 12-fold.

That appearance may be misleading. Diagonalising the negacyclic shift (rotation
by pi/n in parallel space) shows perpendicular space is never a single block:

    n = 4   8-fold    perp = <zeta_8^3,  zeta_8^5>                     2D, all primitive
    n = 5  10-fold    perp = <zeta_10^3, zeta_10^7>  (+) <zeta_10^5>   2D primitive + 1D
    n = 6  12-fold    perp = <zeta_12^5, zeta_12^7>  (+) <zeta_12^3,9> 2D primitive + 2D

In each case the primitive eigenvalues form a 2-dimensional Galois-conjugate
plane, and the remainder is non-primitive: zeta_10^5 = -1, and zeta_12^{3,9} =
+-i, a four-fold symmetry sitting inside the twelve-fold one.

The remainder is the analogue of Penrose's lift-sum grading, already measured
inert (AUC 0.5398 at zero disorder, 0.5696 at disorder 0.20). If it is inert
here too, then all three substrates carry a 2-dimensional Galois address, the
Z^n family is matched on the quantity that matters, and it is a proper rhombus
tiling family with complete stars - strictly better than the Z^4 construction.

If the remainder is NOT inert, perpendicular dimension genuinely differs and the
tiling confound and the dimension confound cannot both be removed at once.

Substrates are matched by active-set count, not by extent.
"""

import argparse
import sys
from math import gcd

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KDTree

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from audit_with_nulls import adjacency
from generate_nfold import build_edges, generate, projections
from matched_labels import matched_rate_labels

EXTENT = {4: 12, 5: 8, 6: 6}
NAME = {4: "8-fold silver", 5: "10-fold golden", 6: "12-fold platinum"}


def perp_blocks(n):
    """Split perpendicular space into the Galois-conjugate plane and the rest.

    The negacyclic shift C (e_k -> e_{k+1}, e_{n-1} -> -e_0) realises rotation by
    pi/n. Its eigenvalues are the primitive and imprimitive 2n-th roots of unity;
    the parallel plane is the zeta^1 eigenspace, and what remains splits by
    whether the eigenvalue is a primitive 2n-th root.
    """
    N = 2 * n
    C = np.zeros((n, n))
    for k in range(n - 1):
        C[k + 1, k] = 1.0
    C[0, n - 1] = -1.0
    par, _ = projections(n)
    Pperp = np.eye(n) - par @ par.T

    w, V = np.linalg.eig(C)
    gal, extra = [], []
    for j in range(n):
        v = V[:, j]
        if np.linalg.norm(Pperp @ v) / np.linalg.norm(v) < 0.5:
            continue                                    # parallel plane
        p = round(float(np.angle(w[j])) / (2 * np.pi) * N) % N
        (gal if gcd(p, N) == 1 else extra).append(v)

    def real_basis(vecs):
        if not vecs:
            return np.zeros((n, 0))
        M = np.column_stack([f(v) for v in vecs for f in (np.real, np.imag)])
        q, r = np.linalg.qr(M)
        return q[:, np.abs(np.diag(r)) > 1e-8]

    G, X = real_basis(gal), real_basis(extra)
    assert G.shape[1] == 2, (n, G.shape)
    assert G.shape[1] + X.shape[1] == n - 2, (n, G.shape, X.shape)
    return G, X


def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if X.shape[1] == 0 or y.sum() < 8 or (1 - y).sum() < 8:
        return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed)
    p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, p))


def one(n, amp, seed, active_n, baseline):
    lifts, par, _ = generate(n, EXTENT[n], disorder=amp, seed=seed)
    E = build_edges(lifts)
    N = len(par)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    act = np.sort(np.argsort(rad)[:active_n]).tolist()

    med = float(np.median(np.linalg.norm(par[[u for u, _ in E]]
                                         - par[[v for _, v in E]], axis=1)))
    q = KDTree(par).query_radius(par[act], r=3.0 * med)
    seeds = {act[k]: q[k].tolist() for k in range(len(act))}
    y, _ = matched_rate_labels(adjacency(N, E), act, seeds, fraction=0.05)

    G, X = perp_blocks(n)
    g = lifts @ G
    x = lifts @ X
    feat_g = np.column_stack([g, np.linalg.norm(g, axis=1)])
    feat_a = np.column_stack([feat_g, x]) if X.shape[1] else feat_g

    rng = np.random.default_rng(900 + seed)
    V = {tuple(r) for r in lifts}
    dmg = len(baseline ^ V) / len(baseline | V)
    return (dmg,
            auc(feat_g[act], y, seed),
            auc(x[act], y, seed) if X.shape[1] else float("nan"),
            auc(feat_a[act], y, seed),
            auc(feat_g[rng.permutation(N)][act], y, seed))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--active", type=int, default=700)
    args = ap.parse_args()

    amps = [0.00, 0.05, 0.10, 0.20]
    for n in (4, 5, 6):
        G, X = perp_blocks(n)
        base, _, _ = generate(n, EXTENT[n], disorder=0.0, seed=0)
        baseline = {tuple(r) for r in base}
        print(f"\n{'='*78}")
        print(f"{NAME[n]}  (Z^{n}, perp dim {n-2} = 2 Galois + {X.shape[1]} non-primitive)")
        print(f"patch {len(base)} vertices, active set {args.active}, "
              f"{args.seeds} seeds")
        print(f"{'='*78}")
        print(f"{'disorder':>9} {'damage':>8} {'GALOIS 2D':>11} {'remainder':>11} "
              f"{'both':>8} {'shuffle':>9}", flush=True)
        for a in amps:
            r = np.array([one(n, a, s, args.active, baseline)
                          for s in range(args.seeds)])
            m = np.nanmean(r, axis=0)
            print(f"{a:9.2f} {m[0]:8.4f} {m[1]:11.4f} {m[2]:11.4f} "
                  f"{m[3]:8.4f} {m[4]:9.4f}", flush=True)

    print("\nInert remainder: column 'remainder' near 0.5 and flat across disorder,")
    print("and 'both' no better than 'GALOIS 2D'. That would mean all three")
    print("substrates carry a 2-dimensional address and the family is matched.")


if __name__ == "__main__":
    main()
