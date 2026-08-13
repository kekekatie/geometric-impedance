#!/usr/bin/env python3
"""
Does partition granularity predict address fragility across a substrate family?

Three or four substrates cannot discriminate: any quantity that happens to order
them will "predict" fragility perfectly. This builds a family by varying window
scale at fixed n — holding lattice, dimension and window connectivity constant
while moving granularity — so the relation can be fitted and its residuals
inspected.

Fragility is measured per unit of MEASURED damage, not nominal amplitude, since
calibration showed amplitude is not comparable across substrates.
"""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import generate_nfold as GN, generate_penrose as GP
from granularity import purity
from audit_with_nulls import adjacency
from matched_labels import matched_rate_labels
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KDTree

AMP = 0.10

def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if y.sum() < 8 or (1 - y).sum() < 8: return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed); p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr]); p[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, p))

def score(lifts, par, perp, E, interior=0.5, frac=0.05, seed=0):
    n = len(par)
    r = np.linalg.norm(par - par.mean(0), axis=1)
    active = np.sort(np.argsort(r)[:int(round(interior * n))]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u,_ in E]] - par[[v for _,v in E]], axis=1)))
    q = KDTree(par).query_radius(par[active], r=3.0 * med)
    seeds = {active[k]: q[k].tolist() for k in range(len(active))}
    y, _ = matched_rate_labels(adjacency(n, E), active, seeds, fraction=frac)
    X = np.column_stack([perp, np.linalg.norm(perp, axis=1)])
    return auc(X[active], y, seed), int(y.sum())

def run(label, make):
    lf0, par0, perp0 = make(0.0, 0)
    E0 = GN.build_edges(lf0) if label != "Penrose" else GP.build_edges(lf0)
    a0, npos = score(lf0, par0, perp0, E0)
    pur = purity(perp0, E0, par0, mode="degree")
    base = {tuple(r) for r in lf0}
    a1s, dmgs = [], []
    for s in range(2):
        lf, par, perp = make(AMP, s)
        E = GN.build_edges(lf) if label != "Penrose" else GP.build_edges(lf)
        a1s.append(score(lf, par, perp, E, seed=s)[0])
        V = {tuple(r) for r in lf}
        dmgs.append(len(base ^ V) / len(base | V))
    a1, dmg = float(np.mean(a1s)), float(np.mean(dmgs))
    frag = (a0 - a1) / dmg if dmg > 0 else float("nan")
    print(f"{label:<26} {len(par0):7d} {npos:5d} {pur['purity_excess_k8']:+8.3f} "
          f"{a0:8.4f} {a1:8.4f} {dmg:8.4f} {frag:9.3f}", flush=True)
    return pur["purity_excess_k8"], frag

print(f"{'substrate':<26} {'verts':>7} {'pos':>5} {'purity':>8} "
      f"{'AUC(0)':>8} {'AUC(a)':>8} {'damage':>8} {'FRAGILITY':>9}", flush=True)
rows = []
for n, ext in ((4, 16), (5, 13)):
    for ws in (0.70, 0.85, 1.00, 1.15, 1.30):
        rows.append(run(f"Z{n} zonotope ws={ws:.2f}",
                        lambda a, s, n=n, ext=ext, ws=ws: GN.generate(n, ext, disorder=a, seed=s, window_scale=ws)))
rows.append(run("Z6 zonotope ws=1.00",
                lambda a, s: GN.generate(6, 11, disorder=a, seed=s)))
rows.append(run("Penrose",
                lambda a, s: GP.generate(20, np.array([0.1237, 0.0891]), disorder=a, seed=s)))

x = np.array([r[0] for r in rows]); y = np.array([r[1] for r in rows])
ok = ~np.isnan(x) & ~np.isnan(y)
r = np.corrcoef(x[ok], y[ok])[0, 1]
b, a = np.polyfit(x[ok], y[ok], 1)
print(f"\nn = {ok.sum()} substrates")
print(f"correlation(purity excess, fragility) = {r:+.3f}   (r^2 = {r*r:.3f})")
print(f"fit: fragility = {a:.3f} {b:+.3f} * purity_excess")
print(f"residual sd = {np.std(y[ok] - (a + b*x[ok]), ddof=2):.3f}")
