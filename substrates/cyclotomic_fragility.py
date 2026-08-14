#!/usr/bin/env python3
"""Address fragility across the Z^4 cyclotomic family: 8-, 10- and 12-fold.

All three at matched perpendicular dimension (2), matched lattice rank (4),
identical window construction and edge rule. Only the cyclotomic field varies.
Reports AUC against nominal amplitude and against measured damage.
"""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import generate_cyclotomic as GC
from audit_with_nulls import adjacency
from matched_labels import matched_rate_labels
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KDTree

EXTENT, AMPS, SEEDS = 16, (0.0, 0.05, 0.10, 0.20, 0.30), 3

def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if y.sum() < 8 or (1-y).sum() < 8: return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed); p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr]); p[te] = m.predict_proba(X[te])[:,1]
    return float(roc_auc_score(y, p))

def one(N, amp, seed, base):
    lf, par, perp = GC.generate(N, EXTENT, disorder=amp, seed=seed)
    E = GC.build_edges(lf); n = len(par)
    r = np.linalg.norm(par - par.mean(0), axis=1)
    act = np.sort(np.argsort(r)[:int(round(0.5*n))]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u,_ in E]] - par[[v for _,v in E]], axis=1)))
    q = KDTree(par).query_radius(par[act], r=3.0*med)
    seeds = {act[k]: q[k].tolist() for k in range(len(act))}
    y, _ = matched_rate_labels(adjacency(n, E), act, seeds, fraction=0.05)
    rng = np.random.default_rng(400+seed)
    V = {tuple(x) for x in lf}
    dmg = len(base ^ V)/len(base | V) if base else 0.0
    return dmg, auc(perp[act], y, seed), auc(perp[rng.permutation(n)][act], y, seed), int(y.sum())

res = {}
for N, nm in ((8,"silver"),(10,"golden"),(12,"platinum")):
    print(f"\n{N}-fold  ({nm} ratio)", flush=True)
    print(f"{'disorder':>9} {'damage':>8} {'pos':>5} {'address AUC':>20} {'shuffle':>9}", flush=True)
    base = {tuple(x) for x in GC.generate(N, EXTENT)[0]}
    res[N] = []
    for a in AMPS:
        r = [one(N, a, s, base) for s in range(SEEDS)]
        d = np.mean([x[0] for x in r]); v = np.array([x[1] for x in r])
        sh = np.mean([x[2] for x in r]); p = int(np.mean([x[3] for x in r]))
        res[N].append((a, d, v.mean()))
        print(f"{a:9.2f} {d:8.4f} {p:5d} {v.mean():11.4f} +-{v.std(ddof=1):.4f} {sh:9.4f}", flush=True)

print("\n" + "="*66)
print("AUC at MATCHED DAMAGE (interpolated)")
print("="*66)
print(f"{'damage':>8} {'8-fold':>10} {'10-fold':>10} {'12-fold':>10}")
for d in (0.10, 0.20, 0.30, 0.40):
    row = []
    for N in (8,10,12):
        dd = [x[1] for x in res[N]]; aa = [x[2] for x in res[N]]
        row.append(np.interp(d, dd, aa) if d <= max(dd) else np.nan)
    print(f"{d:8.2f} " + " ".join(f"{v:10.4f}" for v in row))
