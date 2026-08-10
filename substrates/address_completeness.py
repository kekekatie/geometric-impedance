import sys, csv, math, numpy as np
sys.path.insert(0,"/home/user/geometric-impedance/substrates")
from nonlinear import load          # reuse loader
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

# AB lifts Z^4 -> 2 parallel + 2 perpendicular. perp_x, perp_y is COMPLETE.
# Penrose lifts Z^5 -> 2 parallel + 2 perpendicular + 1 along (1,1,1,1,1).
# So a Penrose vertex needs THREE numbers to be fully addressed. The published
# feature set uses perp_x, perp_y, perp_r, k_sum_mod5 - is that complete?
B="/home/user/geometric-impedance/substrates/"
rows=list(csv.DictReader(open(B+"real_penrose_lift.csv",encoding="utf-8-sig")))
K=np.array([[int(r[f"K{i}"]) for i in range(5)] for r in rows],float)
perp_given=np.array([[float(r["perp_x"]),float(r["perp_y"])] for r in rows])
ks=K.sum(1)
PERP=np.array([[math.cos(4*math.pi*k/5), math.sin(4*math.pi*k/5)] for k in range(5)])
perp_calc=K@PERP
print("recomputed perp vs supplied perp : max abs diff %.4f" % np.abs(perp_calc-perp_given).max())
print("k_sum distinct values            :", sorted(set(ks.astype(int)))[:12], "...")
print("k_sum_mod5 distinct              :", sorted(set((ks%5).astype(int))))
print("=> k_sum is NOT confined to a few hyperplanes; mod-5 discards its magnitude\n")

def auc(X,y,seed=0):
    cv=StratifiedKFold(3,shuffle=True,random_state=seed); p=np.zeros(len(y))
    for tr,te in cv.split(X,y):
        m=HistGradientBoostingClassifier(max_iter=300,random_state=0)
        m.fit(X[tr],y[tr]); p[te]=m.predict_proba(X[te])[:,1]
    return roc_auc_score(y,p)

_, y_p = load(B+"real_penrose_lift.csv", B+"real_penrose_edges.csv",
              ["perp_x","perp_y","perp_r","k_sum_mod5"])
import numpy as _np
pts=_np.array([[float(r["x"]),float(r["y"])] for r in rows]); n=len(rows)
rad=_np.linalg.norm(pts-pts.mean(0),axis=1)
act=_np.sort(_np.argsort(rad)[:int(round(0.75*n))])

feats={
 "published (perp_x,perp_y,perp_r,k_sum_mod5)": np.column_stack(
     [perp_calc, np.linalg.norm(perp_calc,axis=1), ks%5])[act],
 "+ continuous k_sum instead of mod5":          np.column_stack(
     [perp_calc, np.linalg.norm(perp_calc,axis=1), ks])[act],
 "complete perp address (perp_x,perp_y,k_sum)": np.column_stack([perp_calc, ks])[act],
}
print(f"{'Penrose address feature set':<46} {'AUC':>7}")
for k,X in feats.items(): print(f"{k:<46} {auc(X,y_p):7.4f}")

_, y_a = load(B+"real_ab_lift.csv", B+"real_ab_edges.csv",
              ["perp_x","perp_y","perp_r","k_sum_mod4"])
ra=list(csv.DictReader(open(B+"real_ab_lift.csv",encoding="utf-8-sig")))
Ka=np.array([[int(r[f"K{i}"]) for i in range(4)] for r in ra],float)
pa=np.array([[float(r["perp_x"]),float(r["perp_y"])] for r in ra])
pts_a=np.array([[float(r["x"]),float(r["y"])] for r in ra]); na=len(ra)
rada=np.linalg.norm(pts_a-pts_a.mean(0),axis=1)
acta=np.sort(np.argsort(rada)[:int(round(0.75*na))])
print(f"\n{'AB complete perp address (perp_x,perp_y)':<46} {auc(pa[acta],y_a):7.4f}")
