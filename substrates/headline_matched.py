#!/usr/bin/env python3
"""Headline AB vs Penrose address comparison under matched positive rates."""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit("/",1)[0])
from audit_with_nulls import read_csv_rows, read_edges, adjacency
from matched_labels import matched_rate_labels, intersection_labels
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KDTree

def prep(lift, edges, addr):
    rows = read_csv_rows(lift); E = read_edges(edges); n = len(rows)
    pts = np.array([[float(r["x"]), float(r["y"])] for r in rows])
    A = np.array([[float(r[c]) for c in addr] for r in rows])
    rad = np.linalg.norm(pts - pts.mean(0), axis=1)
    active = np.sort(np.argsort(rad)[:int(round(0.75*n))]).tolist()
    med = float(np.median(np.linalg.norm(pts[[u for u,_ in E]] - pts[[v for _,v in E]], axis=1)))
    q = KDTree(pts).query_radius(pts[active], r=3.0*med)
    seeds = {active[k]: q[k].tolist() for k in range(len(active))}
    return adjacency(n, E), active, seeds, A

def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if y.sum() < 8: return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed); p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr]); p[te] = m.predict_proba(X[te])[:,1]
    return float(roc_auc_score(y, p))

SUBS = [("AB", "real_ab_lift.csv", "real_ab_edges.csv", ["perp_x","perp_y","perp_r","k_sum_mod4"]),
        ("Penrose", "real_penrose_lift.csv", "real_penrose_edges.csv", ["perp_x","perp_y","perp_r","k_sum_mod5"])]

print(f"{'substrate':<9} {'label':<22} {'active':>8} {'pos':>6} {'rate':>7} {'AUC':>8} {'shuffle':>8}")
print("-"*72)
res={}
for name, lf, ef, addr in SUBS:
    adj, active, seeds, A = prep(lf, ef, addr)
    X = A[active]
    rng = np.random.default_rng(3)
    Xs = A[rng.permutation(len(A))][active]
    yi = intersection_labels(adj, active, seeds)
    print(f"{name:<9} {'v3 intersection':<22} {len(active):8d} {int(yi.sum()):6d} "
          f"{yi.mean():7.3%} {auc(X,yi):8.4f} {auc(Xs,yi):8.4f}")
    for frac in (0.03,):
        ym, _ = matched_rate_labels(adj, active, seeds, fraction=frac)
        a = auc(X, ym); res[name]=a
        print(f"{name:<9} {'matched rate '+f'{frac:.0%}':<22} {len(active):8d} {int(ym.sum()):6d} "
              f"{ym.mean():7.3%} {a:8.4f} {auc(Xs,ym):8.4f}")
    print()
print(f"matched-rate gap  AB - Penrose = {res['AB']-res['Penrose']:+.4f}")
