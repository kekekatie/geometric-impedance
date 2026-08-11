#!/usr/bin/env python3
"""Address AUC vs how much of the patch boundary is trimmed, both substrates."""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit("/",1)[0])
from audit_with_nulls import read_csv_rows, read_edges, adjacency
from matched_labels import matched_rate_labels
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KDTree

def auc(X, y, seed=0):
    y = np.asarray(y, int)
    if y.sum() < 8: return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed); p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr]); p[te] = m.predict_proba(X[te])[:,1]
    return float(roc_auc_score(y, p))

def load(lift, edges, addr):
    rows = read_csv_rows(lift); E = read_edges(edges); n = len(rows)
    pts = np.array([[float(r["x"]), float(r["y"])] for r in rows])
    A = np.array([[float(r[c]) for c in addr] for r in rows])
    med = float(np.median(np.linalg.norm(pts[[u for u,_ in E]] - pts[[v for _,v in E]], axis=1)))
    return adjacency(n,E), pts, A, med, n

SUBS = [("AB","real_ab_lift.csv","real_ab_edges.csv",["perp_x","perp_y","perp_r","k_sum_mod4"]),
        ("Penrose","real_penrose_lift.csv","real_penrose_edges.csv",["perp_x","perp_y","perp_r","k_sum_mod5"])]
FRACS = [0.90, 0.75, 0.60, 0.50, 0.40, 0.30]

out={}
for name, lf, ef, addr in SUBS:
    adj, pts, A, med, n = load(lf, ef, addr)
    rad = np.linalg.norm(pts - pts.mean(0), axis=1); order = np.argsort(rad)
    tree = KDTree(pts)
    print(f"\n{name}  ({n} vertices total)")
    print(f"{'interior':>9} {'active':>8} {'pos':>6} {'AUC':>8} {'shuffle':>8}")
    out[name]={}
    for f in FRACS:
        active = np.sort(order[:int(round(f*n))]).tolist()
        q = tree.query_radius(pts[active], r=3.0*med)
        seeds = {active[k]: q[k].tolist() for k in range(len(active))}
        y,_ = matched_rate_labels(adj, active, seeds, fraction=0.03)
        rng = np.random.default_rng(5)
        a = auc(A[active], y); s = auc(A[rng.permutation(len(A))][active], y)
        out[name][f]=a
        print(f"{f:9.0%} {len(active):8d} {int(y.sum()):6d} {a:8.4f} {s:8.4f}")

print(f"\n{'interior':>9} {'AB':>9} {'Penrose':>9} {'gap':>9}")
for f in FRACS:
    print(f"{f:9.0%} {out['AB'][f]:9.4f} {out['Penrose'][f]:9.4f} {out['AB'][f]-out['Penrose'][f]:+9.4f}")
