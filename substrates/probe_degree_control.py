import sys, numpy as np
sys.path.insert(0, "/home/user/geometric-impedance/substrates")
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KDTree
from audit_with_nulls import adjacency
from generate_rank4 import build_edges, classes_of, generate, structure
from matched_labels import matched_rate_labels

EXT={8:14,10:16,12:16}; NAME={8:"silver",10:"golden",12:"platinum"}; ACTIVE=1200

def auc(X,y,seed=0):
    y=np.asarray(y,int); X=np.asarray(X,float)
    if X.ndim==1: X=X[:,None]
    if X.shape[1]==0 or y.sum()<8 or (1-y).sum()<8: return float("nan")
    cv=StratifiedKFold(3,shuffle=True,random_state=seed); p=np.zeros(len(y))
    for tr,te in cv.split(X,y):
        m=HistGradientBoostingClassifier(max_iter=200,random_state=0); m.fit(X[tr],y[tr])
        p[te]=m.predict_proba(X[te])[:,1]
    return float(roc_auc_score(y,p))

print(f"{'':9} {'deg':>6} {'perp':>6} {'d+perp':>7} {'class':>6} {'d+cls':>6} {'d+p+cls':>8}  increments: perp|deg  cls|d+p")
for N in (8,10,12):
    accum={}
    for seed in range(2):
        lifts,par,perp,ustar=generate(N,EXT[N],seed=seed)
        E=build_edges(lifts,N,ustar); n=len(par)
        rad=np.linalg.norm(par-par.mean(0),axis=1); act=np.sort(np.argsort(rad)[:ACTIVE]).tolist()
        med=float(np.median(np.linalg.norm(par[[u for u,_ in E]]-par[[v for _,v in E]],axis=1)))
        q=KDTree(par).query_radius(par[act],r=3.0*med); seeds={act[k]:q[k].tolist() for k in range(len(act))}
        y,_=matched_rate_labels(adjacency(n,E),act,seeds,fraction=0.05)
        deg=np.zeros(n)
        for u,v in E: deg[u]+=1; deg[v]+=1
        d=deg[act][:,None]; pp=np.column_stack([perp,np.linalg.norm(perp,axis=1)])[act]
        cl=classes_of(lifts,N).astype(float)[act][:,None]
        multi = structure(N)["classes"]>1
        res={"deg":auc(d,y,seed),"perp":auc(pp,y,seed),"dperp":auc(np.column_stack([d,pp]),y,seed),
             "cls":auc(cl,y,seed) if multi else float("nan"),
             "dcls":auc(np.column_stack([d,cl]),y,seed) if multi else float("nan"),
             "dpc":auc(np.column_stack([d,pp,cl]),y,seed) if multi else auc(np.column_stack([d,pp]),y,seed)}
        for k,val in res.items(): accum.setdefault(k,[]).append(val)
    m={k:np.nanmean(v) for k,v in accum.items()}
    perp_gain=m["dperp"]-m["deg"]; cls_gain=m["dpc"]-m["dperp"]
    print(f"{NAME[N]:9} {m['deg']:6.3f} {m['perp']:6.3f} {m['dperp']:7.3f} {m['cls']:6.3f} {m['dcls']:6.3f} {m['dpc']:8.3f}   {perp_gain:+.3f}      {cls_gain:+.3f}")
