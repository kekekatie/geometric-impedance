#!/usr/bin/env python3
"""
Is Penrose's address carried by its discrete component?

Penrose's window is four pentagons indexed by lift sum, so its address splits
into a continuous part (position within a pentagon) and a discrete part (which
pentagon). Ammann-Beenker's window is one octagon; its lift sum exists but does
not index disjoint pieces.

Hypothesis: Penrose's readability leans on the discrete index, and a discrete
index does not degrade gracefully under jitter - it flips. That would give a
cliff rather than a gradient, and would explain why Penrose is fragile without
appealing to fragmentation as such.

Fits three feature sets per substrate per disorder level, and reports which
carries the signal and which collapses.
"""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import generate_nfold as GN, generate_penrose as GP
from audit_with_nulls import adjacency
from matched_labels import matched_rate_labels
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KDTree

def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if y.sum() < 8 or (1-y).sum() < 8: return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed); p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr]); p[te] = m.predict_proba(X[te])[:,1]
    return float(roc_auc_score(y, p))

def measure(lifts, par, perp, E, seed=0, interior=0.5, frac=0.05):
    n = len(par)
    r = np.linalg.norm(par - par.mean(0), axis=1)
    act = np.sort(np.argsort(r)[:int(round(interior*n))]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u,_ in E]] - par[[v for _,v in E]], axis=1)))
    q = KDTree(par).query_radius(par[act], r=3.0*med)
    seeds = {act[k]: q[k].tolist() for k in range(len(act))}
    y, _ = matched_rate_labels(adjacency(n, E), act, seeds, fraction=frac)
    ksum = lifts.sum(1)[:, None].astype(float)
    cont = perp                                   # continuous position only
    both = np.column_stack([perp, ksum])
    return (auc(cont[act], y, seed), auc(ksum[act], y, seed), auc(both[act], y, seed),
            int(len(set(ksum.ravel().tolist()))))

print(f"{'substrate':<10} {'disorder':>9} {'continuous':>11} {'DISCRETE':>9} {'both':>7} {'k values':>9}")
print("-"*62)
for name, make in (("AB", lambda a,s: (lambda L: (L[0],L[1],L[2],GN.build_edges(L[0])))(GN.generate(4,18,disorder=a,seed=s))),
                   ("Penrose", lambda a,s: (lambda L: (L[0],L[1],L[2],GP.build_edges(L[0])))(GP.generate(20,np.array([0.1237,0.0891]),disorder=a,seed=s)))):
    for amp in (0.0, 0.05, 0.10, 0.20):
        c, k, b, nk = [], [], [], 0
        for s in range(2):
            lf, par, perp, E = make(amp, s)
            cc, kk, bb, nk = measure(lf, par, perp, E, seed=s)
            c.append(cc); k.append(kk); b.append(bb)
        print(f"{name:<10} {amp:9.2f} {np.mean(c):11.4f} {np.mean(k):9.4f} "
              f"{np.mean(b):7.4f} {nk:9d}")
    print()
