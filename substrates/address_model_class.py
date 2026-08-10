import sys, numpy as np
sys.path.insert(0,"/home/user/geometric-impedance/substrates")
from audit_with_nulls import (read_csv_rows, read_edges, adjacency, shared_core_labels, cv_auc)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier, KDTree
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

def cv_auc_model(X, y, make_model, seed=0):
    y=np.asarray(y,int)
    cv=StratifiedKFold(3, shuffle=True, random_state=seed); p=np.zeros(len(y))
    for tr,te in cv.split(X,y):
        m=make_model(); m.fit(X[tr],y[tr]); p[te]=m.predict_proba(X[te])[:,1]
    return float(roc_auc_score(y,p))

def load(lift, edges, addr):
    rows=read_csv_rows(lift); E=read_edges(edges); n=len(rows)
    pts=np.array([[float(r["x"]),float(r["y"])] for r in rows])
    A=np.array([[float(r[c]) for c in addr] for r in rows])
    rad=np.linalg.norm(pts-pts.mean(0),axis=1)
    active=np.sort(np.argsort(rad)[:int(round(0.75*n))]).tolist()
    med=float(np.median([np.linalg.norm(pts[u]-pts[v]) for u,v in E]))
    q=KDTree(pts).query_radius(pts[active], r=3.0*med)
    seeds={active[k]:q[k].tolist() for k in range(len(active))}
    adj=adjacency(n,E)
    y,_,_,_ = shared_core_labels(adj, active, seeds)
    return A[active], y

subs=[("AB",      "real_ab_lift.csv","real_ab_edges.csv",
       ["perp_x","perp_y","perp_r","k_sum_mod4"]),
      ("Penrose", "real_penrose_lift.csv","real_penrose_edges.csv",
       ["perp_x","perp_y","perp_r","k_sum_mod5"])]

models={
 "logistic (as published)": lambda: make_pipeline(StandardScaler(),
        __import__("sklearn.linear_model",fromlist=["LogisticRegression"]).LogisticRegression(
            max_iter=700, class_weight="balanced", solver="liblinear")),
 "k-NN (k=25)":            lambda: make_pipeline(StandardScaler(), KNeighborsClassifier(25)),
 "gradient boosting":      lambda: HistGradientBoostingClassifier(max_iter=200, random_state=0),
}

print(f"{'substrate':<10} {'model':<26} {'address AUC':>12}")
print("-"*50)
res={}
for name, lf, ef, addr in subs:
    X,y = load(f"/home/user/geometric-impedance/substrates/{lf}",
               f"/home/user/geometric-impedance/substrates/{ef}", addr)
    for mname, mk in models.items():
        a=cv_auc_model(X,y,mk)
        res[(name,mname)]=a
        print(f"{name:<10} {mname:<26} {a:12.4f}")
    print()
print("gap AB - Penrose, by model:")
for mname in models:
    print(f"  {mname:<26} {res[('AB',mname)]-res[('Penrose',mname)]:+.4f}")
