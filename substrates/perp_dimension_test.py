#!/usr/bin/env python3
"""
Does address-channel fragility scale with perpendicular-space dimension?

The projection reading of the framework says the address channel is how much of
the higher-dimensional structure stays readable from inside the shadow. If so,
how much got projected away should matter. Z^n -> 2D gives perpendicular
dimension n-2, so this is directly testable.

    n = 4   8-fold   perp dim 2
    n = 5  10-fold   perp dim 3
    n = 6  12-fold   perp dim 4

Extents chosen so all three substrates carry ~5,600 vertices, matched positive
rate, bulk crop, shuffle null beside every point.

Feature-count control: higher n gives more perpendicular coordinates, hence more
address features, hence more model capacity. So the sweep is also run with the
perpendicular RADIUS ALONE - one feature for every n - which removes that
difference entirely.
"""
import sys, argparse, numpy as np
sys.path.insert(0, __file__.rsplit("/",1)[0])
import generate_nfold as GN
from audit_with_nulls import adjacency
from matched_labels import matched_rate_labels
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KDTree

EXTENT = {4: 18, 5: 15, 6: 12}          # matched to ~5,600 vertices

def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if y.sum() < 8 or (1-y).sum() < 8: return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed); p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr]); p[te] = m.predict_proba(X[te])[:,1]
    return float(roc_auc_score(y, p))

def one(n, amp, seed, interior=0.50, frac=0.05):
    lifts, par, perp = GN.generate(n, EXTENT[n], disorder=amp, seed=seed)
    E = GN.build_edges(lifts); N = len(par)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    active = np.sort(np.argsort(rad)[:int(round(interior*N))]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u,_ in E]] - par[[v for _,v in E]], axis=1)))
    q = KDTree(par).query_radius(par[active], r=3.0*med)
    seeds = {active[k]: q[k].tolist() for k in range(len(active))}
    y, _ = matched_rate_labels(adjacency(N, E), active, seeds, fraction=frac)
    pr = np.linalg.norm(perp, axis=1)[:, None]
    full = np.column_stack([perp, pr])
    rng = np.random.default_rng(900+seed)
    sh = full[rng.permutation(N)]
    return (N, int(y.sum()),
            auc(full[active], y, seed),          # all perp coords + radius
            auc(pr[active], y, seed),            # radius alone: 1 feature for every n
            auc(sh[active], y, seed))            # shuffle null

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    amps = [0.0, 0.05, 0.10, 0.20, 0.30, 0.40]
    res = {}
    for n in (4, 5, 6):
        print(f"\nn = {n}   {2*n}-fold   perpendicular dimension {n-2}", flush=True)
        print(f"{'disorder':>9} {'verts':>7} {'pos':>5} {'full address':>16} "
              f"{'radius only':>16} {'shuffle':>9}", flush=True)
        for a in amps:
            r = [one(n, a, s) for s in range(args.seeds)]
            v  = np.mean([x[0] for x in r]); p = np.mean([x[1] for x in r])
            f  = np.array([x[2] for x in r]); o = np.array([x[3] for x in r])
            s_ = np.mean([x[4] for x in r])
            res[(n,a)] = (f.mean(), o.mean())
            print(f"{a:9.2f} {int(v):7d} {int(p):5d} {f.mean():9.4f} +-{f.std(ddof=1):.4f} "
                  f"{o.mean():9.4f} +-{o.std(ddof=1):.4f} {s_:9.4f}", flush=True)

    for label, idx in (("FULL ADDRESS", 0), ("RADIUS ONLY", 1)):
        print(f"\n{'='*64}\n{label}: address AUC by perpendicular dimension\n{'='*64}")
        print(f"{'disorder':>9} {'perp 2':>9} {'perp 3':>9} {'perp 4':>9}")
        for a in amps:
            print(f"{a:9.2f} " + " ".join(f"{res[(n,a)][idx]:9.4f}" for n in (4,5,6)))
        print(f"{'loss 0->0.4':>9} " +
              " ".join(f"{res[(n,0.0)][idx]-res[(n,0.40)][idx]:9.4f}" for n in (4,5,6)))

if __name__ == "__main__":
    main()
