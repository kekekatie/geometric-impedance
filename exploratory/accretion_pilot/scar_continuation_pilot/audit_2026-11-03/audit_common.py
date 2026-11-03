import sys,os,json,pickle,hashlib,collections,math,functools
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'src'))
import scar_common as S
import arc_tools as A
import scar_continuation as G
import phase3_post_readout as P3
CACHE=Path(os.environ['SCAR_AUDIT_CACHE'])
RESULTS=HERE/'results';RESULTS.mkdir(exist_ok=True)
def load(name):return pickle.loads((CACHE/name).read_bytes())
def dump(name,value):
    (RESULTS/name).write_text(json.dumps(value,indent=2,default=lambda x: x.item() if hasattr(x,'item') else str(x)),encoding='utf-8')
def tilehash(tiles):return hashlib.sha256(repr(sorted(S.dk(t) for t in tiles)).encode()).hexdigest()
def exacthash(tiles):return hashlib.sha256(repr(tiles).encode()).hexdigest()
def components(tiles):
    return sorted([sorted(c,key=S.dk) for c in A.connected_components(tiles)],key=lambda c:(-len(c),tuple(S.dk(t) for t in c)))
def largest(tiles):return components(tiles)[0] if tiles else []
def outcome(raw):
    if raw.get('status')!='reconstructed':return 'reconstruction_failure'
    return {0:'A',1:'B'}.get(raw['selected'],'ambiguous' if S.RD.classify(raw)[0]=='ambiguous' else 'empty_incompatible')
def margin(raw,payload,hypothesis=None):
    if raw.get('status')!='reconstructed':return dict(status='unresolved')
    rows=[];cm={(r,i):c for r,i,c in raw['constraints']}
    if hypothesis is not None:
        for r,i,c in hypothesis:cm[(r,i)]=max(cm.get((r,i),-math.inf),c)
    for (r,i),c in sorted(cm.items()):
        nx,ny=payload['windows'][r]['normals'][i];n=math.hypot(nx,ny)
        rows.append((-nx/n,-ny/n,1,c/n))
    if not rows:return dict(status='unbounded',margin=None)
    arr=np.array(rows)
    rr=linprog([0,0,-1],A_ub=arr[:,:3],b_ub=-arr[:,3],bounds=[(None,None)]*3,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    return dict(status=int(rr.status),margin=float(rr.x[2]) if rr.status==0 else None)
def area(poly):
    return abs(sum((a.conjugate()*b).imag for a,b in zip(poly,poly[1:]+poly[:1])))/2 if len(poly)>2 else 0.
def intersection(a,b):
    out=list(a);sign=1 if sum((p.conjugate()*q).imag for p,q in zip(b,b[1:]+b[:1]))>0 else -1
    for p,q in zip(b,b[1:]+b[:1]):
        old=out;out=[]
        if not old:break
        f=lambda z:sign*((q-p).conjugate()*(z-p)).imag
        for u,v in zip(old,old[1:]+old[:1]):
            fu,fv=f(u),f(v)
            if fu>=-1e-15:out.append(u)
            if (fu>=-1e-15)!=(fv>=-1e-15):out.append(u+(v-u)*fu/(fu-fv))
    return out
def overlap_check(tiles):
    boxes=[(min(z.real for z in t[1:]),max(z.real for z in t[1:]),min(z.imag for z in t[1:]),max(z.imag for z in t[1:])) for t in tiles]
    pairs=0;bad=[];maxarea=0.
    for i,a in enumerate(boxes):
        for j in range(i):
            b=boxes[j]
            if min(a[1],b[1])-max(a[0],b[0])<=1e-12 or min(a[3],b[3])-max(a[2],b[2])<=1e-12:continue
            pairs+=1;value=area(intersection(list(tiles[i][1:]),list(tiles[j][1:])));maxarea=max(value,maxarea)
            if value>1e-12:bad.append([i,j,value])
    return dict(test_pairs=pairs,max_intersection_area=maxarea,positive_area_overlaps=bad,area_tolerance=1e-12)
def edge_stats(edges,band):
    adj=collections.defaultdict(set)
    for ek in edges:
        a,b=tuple(ek);adj[a].add(b);adj[b].add(a)
    unseen=set(adj);n=0
    while unseen:
        n+=1;stack=[min(unseen)]
        while stack:
            a=stack.pop()
            if a not in unseen:continue
            unseen.remove(a);stack.extend(adj[a]&unseen)
    c=A.centroid(band);angles=sorted(math.atan2((sum(complex(*v) for v in e)/2-c).imag,(sum(complex(*v) for v in e)/2-c).real) for e in edges)
    gaps=[b-a for a,b in zip(angles,angles[1:])]+([2*math.pi+angles[0]-angles[-1]] if angles else [])
    return dict(edges=len(edges),vertex_connected_components=n,span_radians=2*math.pi-max(gaps) if gaps else 0.)

class Reader:
    """Cache exact read payloads and inverse arguments; thresholds are untouched."""
    def __init__(self):
        self.cache={};self.inverse_original=S.SR.inverse
        S.SR.inverse=functools.lru_cache(maxsize=None)(S.SR.inverse)
        self.align_checks=0;self.metadata={};self.globallifts={}
    def payload(self,st,tiles):
        key=exacthash(st['Sstar'])+repr(st['cs'])
        if key not in self.metadata:self.metadata[key]=S.RD.build_payload(st['Sstar'],st['cs'],[])
        p=dict(self.metadata[key]);p['tiles']=[[t[0]]+[[z.real,z.imag] for z in t[1:]] for t in tiles]
        return p
    def score(self,st,tiles):
        comp=largest(tiles);payload=self.payload(st,comp);key=json.dumps(payload,sort_keys=True)
        if key not in self.cache:
            try:raw=S.SR.read(payload)
            except S.SR.ReconstructionError as exc:raw=dict(status='unreconstructible',reason=str(exc))
            self.cache[key]=raw
        raw=self.cache[key]
        if raw.get('status')=='reconstructed':
            full=st['full'];fkey=exacthash(full)+str(payload['origin'])
            if fkey not in self.globallifts:
                K,_,conf=S.EB.M.lift(full);assert not conf
                root=S.L.key(complex(*payload['origin']));shift=K[root]
                self.globallifts[fkey]={v:(k-shift).tolist() for v,k in K.items()}
            K=self.globallifts[fkey]
            assert all(K[tuple(v)]==k for v,k in raw['lift']),'absolute historical gauge mismatch'
            self.align_checks+=1
        bkey=S.dk(st['B']);ck={S.dk(t) for t in comp};bk={S.dk(t) for t in st['band']}
        rec=dict(n_requested=len(tiles),component_sizes=[len(c) for c in components(tiles)],n_tiles=len(comp),fraction=len(comp)/len(st['band']),subset_hash=tilehash(comp),reader_status=raw['status'],outcome=outcome(raw),area=raw.get('area'),intersections=raw.get('intersections'),selected=raw.get('selected'),feasibility=margin(raw,payload),hypothesis_feasibility=[margin(raw,payload,h) for h in payload['hypotheses']],B_in_subset=bkey in ck,B_in_band=bkey in bk,B_in_archive=any(S.dk(t)==bkey for t in st['full']))
        return rec,comp,raw,payload
