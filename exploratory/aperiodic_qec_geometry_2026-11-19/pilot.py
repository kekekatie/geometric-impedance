"""Deterministic whole-tile edge-qubit pilot. Run: python pilot.py --out results."""
import argparse, collections as C, hashlib, importlib.util, itertools as I, json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
AB=load('ab_vendor',ROOT/'vendor/generate_ab.py')
P=load('penrose_addresses',ROOT.parent/'accretion_pilot/penrose_address_environment/penrose_address.py')
def edge(a,b): return tuple(sorted((a,b)))
def area(vs,pos): return sum(pos[a][0]*pos[b][1]-pos[b][0]*pos[a][1] for a,b in zip(vs,vs[1:]+vs[:1]))/2
def canon(vs,pos):
    vs=tuple(vs)
    if area(vs,pos)<0: vs=tuple(reversed(vs))
    j=vs.index(min(vs)); return vs[j:]+vs[:j]
def parent(family,large=False):
    meta={'family':family}; pos={}; perp={}; faces=[]
    if family=='square':
        r=15 if large else 12
        pos={(x,y):(float(x),float(y)) for x in range(-r,r+1) for y in range(-r,r+1)}
        faces=[((x,y),(x+1,y),(x+1,y+1),(x,y+1)) for x in range(-r,r) for y in range(-r,r)]
        meta.update(extent=r,lift_dimension=2,window=None)
    elif family=='AB':
        r=11 if large else 9; offset=np.array([.1381,.0927])
        lifts,xy,pp=AB.generate(r,offset)
        pos={tuple(map(int,k)):tuple(map(float,v)) for k,v in zip(lifts,xy)}
        perp={tuple(map(int,k)):tuple(map(float,v)) for k,v in zip(lifts,pp)}
        for k in pos:
            for a,b in I.combinations(range(4),2):
                ka=list(k); ka[a]+=1; kb=list(k); kb[b]+=1; kab=list(ka); kab[b]+=1
                vs=(k,tuple(ka),tuple(kab),tuple(kb))
                if all(v in pos for v in vs): faces.append(vs)
        meta.update(extent=r,lift_dimension=4,offset=offset.tolist(),parallel_basis=AB.PAR.tolist(),
                    perp_basis=AB.PERP.tolist(),window=AB.octagon_window().tolist(),window_rule='K@PERP + offset inside actual CCW polygon; tolerance 1e-9',
                    layer_convention='No Penrose-style layer; sum(K) and source sum(K)%5 retained only as integer labels.')
    else:
        r=15 if large else 12
        fs,vs,es=P.build(r); pos={k:P.par(k) for k in vs}; perp={k:P.perp(k) for k in vs}; faces=[f[0] for f in fs]
        meta.update(radius=r,lift_dimension=5,gamma=list(P.GAMMA),parallel_basis=P.EV,
                    perp_basis=[P.EV[(2*j)%5] for j in range(5)],layer_convention='sum(K), pentagrid ceil-strip indices',
                    window_rule='Dual pentagrid e_j dot x = n + gamma_j; unshifted K@PERP stored; gamma and projected gamma retained.',
                    gamma_perp=[sum(P.GAMMA[j]*P.EV[(2*j)%5][i] for j in range(5)) for i in range(2)])
    faces=sorted({canon(v,pos) for v in faces},key=lambda v:tuple(sorted(v)))
    ef=C.defaultdict(list); ve=C.defaultdict(set)
    for f,vs in enumerate(faces):
        assert len(vs)==4 and area(vs,pos)>1e-9
        for a,b in zip(vs,vs[1:]+vs[:1]):
            e=edge(a,b); ef[e].append(f); ve[a].add(e); ve[b].add(e)
            assert abs(math.dist(pos[a],pos[b])-1)<1e-8
    assert all(len(fs) in (1,2) for fs in ef.values())
    return dict(meta=meta,pos=pos,perp=perp,faces=faces,ef=ef,ve=ve)

def disk(p,ids):
    ids=tuple(sorted(ids)); es=C.defaultdict(list); vs=set()
    for f in ids:
        poly=p['faces'][f]; vs.update(poly)
        for a,b in zip(poly,poly[1:]+poly[:1]): es[edge(a,b)].append(f)
    if len(vs)-len(es)+len(ids)!=1: return None
    adj=C.defaultdict(set)
    for e,fs in es.items():
        if len(fs)==1: a,b=e; adj[a].add(b); adj[b].add(a)
    if not adj or any(len(n)!=2 for n in adj.values()): return None
    start=min(adj); cycle=[start]; prev=None; cur=start
    while True:
        nxt=min(adj[cur]-({prev} if prev is not None else set()))
        if nxt==start: break
        if nxt in cycle: return None
        cycle.append(nxt); prev,cur=cur,nxt
    if len(cycle)!=len(adj): return None
    if area(tuple(cycle),p['pos'])<0: cycle=[cycle[0]]+list(reversed(cycle[1:]))
    fa=C.defaultdict(set)
    for fs in es.values():
        if len(fs)==2: a,b=fs; fa[a].add(b); fa[b].add(a)
    seen={ids[0]}; todo=[ids[0]]
    for f in todo:
        for g in fa[f]-seen: seen.add(g); todo.append(g)
    if len(seen)!=len(ids): return None
    # Each vertex link is a single path (rim) or cycle (interior).
    for v in vs:
        link=C.defaultdict(set)
        for f in ids:
            poly=p['faces'][f]
            if v not in poly: continue
            j=poly.index(v); a,b=poly[j-1],poly[(j+1)%4]; link[a].add(b); link[b].add(a)
        seen={min(link)}; todo=list(seen)
        for a in todo:
            for b in link[a]-seen: seen.add(b); todo.append(b)
        if len(seen)!=len(link) or any(len(z)>2 for z in link.values()): return None
    return dict(ids=ids,edges=es,vertices=vs,cycle=cycle)

def path(adj,starts,targets):
    seen={v:None for v in starts}; todo=C.deque(sorted(starts)); targets=set(targets)
    while todo:
        v=todo.popleft()
        if v in targets:
            result=[]
            while seen[v] is not None: v,e=seen[v]; result.append(e)
            return list(reversed(result))
        for w,e in sorted(adj[v],key=lambda x:(str(x[0]),x[1])):
            if w not in seen: seen[w]=(v,e); todo.append(w)
    return None

def cut(p,d,corners):
    cyc=d['cycle']; L=len(cyc); s,a,b,c=corners; bounds=(s,a,b,c,s+L)
    arcs=[[edge(cyc[i%L],cyc[(i+1)%L]) for i in range(lo,hi)] for lo,hi in zip(bounds,bounds[1:])]
    rough=set(arcs[0]+arcs[2]); rv={v for e in rough for v in e}
    data=sorted(set(d['edges'])-rough); q={e:i for i,e in enumerate(data)}
    xv=sorted(d['vertices']-rv); xs={v:i for i,v in enumerate(xv)}
    elig=[]
    for e in data:
        a,b=e; fs=d['edges'][e]
        if len(fs)!=2 or a not in xs or b not in xs: continue
        if any(not p['ve'][v].issubset(q) for v in e): continue
        if any(any(edge(v,w) not in q for v,w in zip(p['faces'][f],p['faces'][f][1:]+p['faces'][f][:1])) for f in fs): continue
        elig.append(e)
    return dict(arcs=arcs,rough=rough,rough_vertices=rv,data=data,xv=xv,eligible=elig,corners=corners)

def distances(d,c):
    pa=C.defaultdict(list); da=C.defaultdict(list)
    sm={e:-(j+1) for j,arc in enumerate((c['arcs'][1],c['arcs'][3])) for e in arc}
    for e in c['data']:
        a,b=e; pa[a].append((b,e)); pa[b].append((a,e))
        fs=d['edges'][e]
        if len(fs)==2: a,b=fs
        else: a,b=fs[0],sm[e]
        da[a].append((b,e)); da[b].append((a,e))
    rz=[{v for e in c['arcs'][j] for v in e} for j in (0,2)]
    z=path(pa,rz[0],rz[1]); x=path(da,{-1},{-2})
    return x,z

def search(p):
    centres=sorted((v for v in p['pos'] if sum(t*t for t in p['pos'][v])<=16),key=lambda v:(round(sum(t*t for t in p['pos'][v]),10),v))[:24]
    patches={}; facecentres={i:np.mean([p['pos'][v] for v in vs],axis=0) for i,vs in enumerate(p['faces'])}
    for ci,v in enumerate(centres):
        for ai,aspect in enumerate((1.,1.25,.8)):
            for oi,angle in enumerate((0.,math.pi/8,math.pi/4,3*math.pi/8)):
                def score(f):
                    dx,dy=facecentres[f]-p['pos'][v]; x=dx*math.cos(angle)+dy*math.sin(angle); y=-dx*math.sin(angle)+dy*math.cos(angle)
                    return (round((x/aspect)**2+(y*aspect)**2,10),tuple(sorted(p['faces'][f])))
                order=sorted(facecentres,key=score)
                for m in range(6,25):
                    ids=tuple(sorted(order[:m])); spec=(ci,ai,oi,m)
                    if ids not in patches:
                        d=disk(p,ids)
                        if d: patches[ids]=(spec,d,v,aspect,angle)
    print(p['meta']['family'],'disk cuts',len(patches),flush=True)
    stats=dict(disks=len(patches),checked=0,targets=0); seen=set()
    # Qualifier preference is fixed before search. Search complete n shells in ranking order.
    for minimum in (2,1,0):
        for band in (range(15,31),range(31,43)):
            for delta in sorted({abs(n-21) for n in band}):
                best=None
                for spec,d,centre,aspect,angle in patches.values():
                    L=len(d['cycle']); E=len(d['edges'])
                    for s in range(L):
                        for shifts in I.product((-1,0,1),repeat=3):
                            corners=(s,)+(tuple(s+j*L//4+t for j,t in zip((1,2,3),shifts)))
                            if not all(a<b for a,b in zip(corners,corners[1:]+(s+L,))): continue
                            n=E-((corners[1]-s)+(corners[3]-corners[2]))
                            if n not in band or abs(n-21)!=delta: continue
                            key=(d['ids'],tuple(sorted((i%L) for a,b in ((s,corners[1]),(corners[2],corners[3])) for i in range(a,b))),minimum)
                            if key in seen: continue
                            seen.add(key); c=cut(p,d,corners)
                            if len(c['eligible'])<minimum: continue
                            stats['checked']+=1
                            x,z=distances(d,c)
                            if x is None or z is None or len(x)!=3 or len(z)!=3: continue
                            stats['targets']+=1
                            pairs=sorted({tuple(sorted(len(p['ve'][v]) for v in e)) for e in c['eligible']})
                            rank=(delta,-len(c['eligible']),-len(pairs),spec,corners)
                            if best is None or rank<best[0]: best=(rank,d,c,dict(centre=centre,aspect=aspect,angle=angle,spec=spec,corners=corners),x,z)
                if best:
                    print(p['meta']['family'],'selected',best[0],'stats',stats,flush=True)
                    return best,dict(stats,minimum_eligible=minimum,expanded=(band.start==31))
    raise RuntimeError('No distance-three cut under frozen search; inspect search obstruction before any extension.')

def basis(rows):
    out={}
    for r in rows:
        while r:
            j=r.bit_length()-1
            if j in out: r^=out[j]
            else: out[j]=r; break
    return out
def member(x,b):
    while x:
        j=x.bit_length()-1
        if j not in b: return False
        x^=b[j]
    return True
def bits(row): return sum(int(x)<<i for i,x in enumerate(row))

def export(p,chosen,stats):
    rank,d,c,spec,x,z=chosen; allvs=sorted(d['vertices']); vid={v:i for i,v in enumerate(allvs)}
    alledges=sorted(d['edges']); eid={e:i for i,e in enumerate(alledges)}; qid={e:i for i,e in enumerate(c['data'])}; fid={f:i for i,f in enumerate(d['ids'])}; xid={v:i for i,v in enumerate(c['xv'])}
    hx=[[int(v in e) for e in c['data']] for v in c['xv']]
    hz=[[int(e in {edge(a,b) for a,b in zip(p['faces'][f],p['faces'][f][1:]+p['faces'][f][:1])}) for e in c['data']] for f in d['ids']]
    elig=[]
    for e in c['eligible']:
        checks=[f'X{xid[v]}' for v in e]+[f'Z{fid[f]}' for f in sorted(d['edges'][e])]
        weights=[len(p['ve'][v]) for v in e]+[4,4]
        elig.append(dict(edge=eid[e],qubit=qid[e],checks=checks,weights=weights,endpoint_degrees=sorted(weights[:2]),query=[[a,t] for a in checks for t in (1,2)]))
    vertices=[]
    for v in allvs:
        vertices.append(dict(id=vid[v],lift=v,xy=p['pos'][v],perp=p['perp'].get(v),layer=sum(v) if p['meta']['family']=='Penrose' else None,
                             integer_sum=sum(v),source_mod5=sum(v)%5 if p['meta']['family']=='AB' else None,
                             rough=v in c['rough_vertices'],xcheck=f'X{xid[v]}' if v in xid else None,
                             parent_neighbours=sorted([list(b if a==v else a) for a,b in p['ve'][v]])))
    return dict(family=p['meta']['family'],parent=p['meta'],selection=spec,search=stats,vertices=vertices,
        edges=[dict(id=eid[e],vertices=[vid[v] for v in e],qubit=qid.get(e),incident_faces=[fid[f] for f in d['edges'][e]],parent_face_lifts=[p['faces'][f] for f in p['ef'][e]]) for e in alledges],
        faces=[dict(id=fid[f],zcheck=f'Z{fid[f]}',vertices=[vid[v] for v in p['faces'][f]]) for f in d['ids']],
        boundary_cycle=[vid[v] for v in d['cycle']],arcs=[dict(label='rough' if j%2==0 else 'smooth',edges=[eid[e] for e in arc]) for j,arc in enumerate(c['arcs'])],
        HX=hx,HZ=hz,eligible=elig,logical_X=[qid[e] for e in x],logical_Z=[qid[e] for e in z],n=len(qid))

def save(path,obj): path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default=str(ROOT/'results')); args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    for family in ('square','AB','Penrose'):
        p=parent(family); chosen,stats=search(p); obj=export(p,chosen,stats); save(out/(family+'.json'),obj)
    import certify, draw
    certify.run(out); draw.run(out)
if __name__=='__main__': main()
