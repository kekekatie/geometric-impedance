"""Independent matrix/incidence verifier for the saved patches; nonzero on failure."""
import itertools, json, math
from pathlib import Path
import numpy as np

def rank(rows,n):
    a=np.array(rows,dtype=np.uint8).reshape((-1,n)).copy(); r=0
    for c in range(n):
        found=next((i for i in range(r,len(a)) if a[i,c]),None)
        if found is None: continue
        a[[r,found]]=a[[found,r]]
        for i in range(r+1,len(a)):
            if a[i,c]: a[i]^=a[r]
        r+=1
    return r
def verify(obj,large):
    vs=obj['vertices']; es=obj['edges']; fs=obj['faces']; n=obj['n']; qes=sorted((e for e in es if e['qubit'] is not None),key=lambda e:e['qubit'])
    assert [e['qubit'] for e in qes]==list(range(n))
    rough={i for a in obj['arcs'] if a['label']=='rough' for i in a['edges']}
    rv={v for i in rough for v in es[i]['vertices']}
    assert all(v['rough']==(v['id'] in rv) for v in vs)
    assert {e['id'] for e in es if e['qubit'] is None}==rough
    edgeid={tuple(sorted(e['vertices'])):e['id'] for e in es}
    incidence={e['id']:[] for e in es}; fedge={}
    for f in fs:
        v=f['vertices']; assert len(set(v))==4
        fedge[f['id']]=[edgeid[tuple(sorted((a,b)))] for a,b in zip(v,v[1:]+v[:1])]
        for i in fedge[f['id']]: incidence[i].append(f['id'])
    assert all(sorted(e['incident_faces'])==sorted(incidence[e['id']]) for e in es)
    assert len(vs)-len(es)+len(fs)==1
    def connected(adj):
        seen={min(adj)}; todo=list(seen)
        for a in todo:
            for b in adj[a]-seen: seen.add(b); todo.append(b)
        return len(seen)==len(adj)
    fa={f['id']:set() for f in fs}
    for e in es:
        if len(e['incident_faces'])==2:
            a,b=e['incident_faces']; fa[a].add(b); fa[b].add(a)
    assert connected(fa)
    for v in vs:
        link={}
        for f in fs:
            poly=f['vertices']
            if v['id'] not in poly: continue
            j=poly.index(v['id']); a,b=poly[j-1],poly[(j+1)%4]
            link.setdefault(a,set()).add(b); link.setdefault(b,set()).add(a)
        assert connected(link) and all(len(z)<=2 for z in link.values())
    cycle=obj['boundary_cycle']; bedges=[edgeid[tuple(sorted((a,b)))] for a,b in zip(cycle,cycle[1:]+cycle[:1])]
    assert len(set(cycle))==len(cycle)
    assert set(bedges)=={e['id'] for e in es if len(e['incident_faces'])==1}
    arcs=obj['arcs']; assert [a['label'] for a in arcs]==['rough','smooth','rough','smooth'] and all(a['edges'] for a in arcs)
    seq=sum((a['edges'] for a in arcs),[]); assert len(seq)==len(set(seq))==len(bedges)
    j=bedges.index(seq[0]); assert seq==bedges[j:]+bedges[:j]
    xv=sorted((v for v in vs if v['xcheck'] is not None),key=lambda v:int(v['xcheck'][1:]))
    assert {v['id'] for v in xv}==set(range(len(vs)))-rv
    hx=[[int(v['id'] in e['vertices']) for e in qes] for v in xv]
    hz=[[int(e['id'] in fedge[f['id']]) for e in qes] for f in fs]
    assert hx==obj['HX'] and hz==obj['HZ']
    A=np.array(hx,dtype=np.uint8); B=np.array(hz,dtype=np.uint8)
    assert not np.any((A@B.T)%2)
    rx,rz=rank(hx,n),rank(hz,n); assert n-rx-rz==1
    tests={}; logicals={}
    for name,comm,stabs,r in (('X',B,hx,rx),('Z',A,hz,rz)):
        counts={}
        for w in (1,2):
            count=0
            for inds in itertools.combinations(range(n),w):
                vec=np.zeros(n,dtype=np.uint8); vec[list(inds)]=1
                if not np.any((comm@vec)%2):
                    assert rank(stabs+[vec.tolist()],n)==r,('short logical',name,inds)
                count+=1
            counts[str(w)]=count
        support=obj['logical_'+name]; assert len(set(support))==3
        vec=np.zeros(n,dtype=np.uint8); vec[support]=1
        assert not np.any((comm@vec)%2) and rank(stabs+[vec.tolist()],n)==r+1
        logicals[name]=vec; tests[name]=counts
    assert int(logicals['X']@logicals['Z'])%2==1
    # Geometry: unit rhombi, oriented disks, no overlapping face interiors.
    polys=[np.array([vs[i]['xy'] for i in f['vertices']]) for f in fs]
    areas=[]
    for poly in polys:
        d=np.roll(poly,-1,axis=0)-poly
        assert np.max(np.abs(np.linalg.norm(d,axis=1)-1))<1e-8
        a=float(sum(poly[i,0]*poly[(i+1)%4,1]-poly[i,1]*poly[(i+1)%4,0] for i in range(4))/2); assert a>1e-9; areas.append(a)
        allowed={'square':[1.],'AB':[1.,2**-.5],'Penrose':[math.sin(math.pi/5),math.sin(2*math.pi/5)]}[obj['family']]
        assert min(abs(a-v) for v in allowed)<1e-8
    for a,b in itertools.combinations(polys,2):
        axes=[np.array([-v[1],v[0]]) for poly in (a,b) for v in np.roll(poly,-1,axis=0)-poly]
        assert any(min(max(a@u),max(b@u))-max(min(a@u),min(b@u))<=1e-8 for u in axes), 'overlap'
    boundary=np.array([vs[i]['xy'] for i in cycle]); ba=sum(boundary[i,0]*boundary[(i+1)%len(boundary),1]-boundary[i,1]*boundary[(i+1)%len(boundary),0] for i in range(len(boundary)))/2
    assert abs(ba-sum(areas))<1e-8
    # Check full stars and incident faces using a separately regenerated larger parent.
    for v in vs:
        k=tuple(v['lift']); neighbours={tuple(t) for t in v['parent_neighbours']}
        actual={b if a==k else a for a,b in large['ve'][k]}
        assert neighbours==actual
        if obj['family']=='AB':
            source_neighbours=set()
            for axis in range(4):
                for sign in (-1,1):
                    other=list(k); other[axis]+=sign; other=tuple(other)
                    if other in large['pos']: source_neighbours.add(other)
            assert actual==source_neighbours, 'face extraction lost a source unit-lift edge'
        assert math.dist(v['xy'],large['pos'][k])<1e-10
        if obj['family']!='square': assert math.dist(v['perp'],large['perp'][k])<1e-10
        if obj['family']=='Penrose': assert v['layer']==sum(k) and math.hypot(*v['xy'])<obj['parent']['radius']-3
        else: assert max(abs(z) for z in k)<=obj['parent']['extent']-2
    recomputed=[]
    for e in qes:
        a,b=[vs[i] for i in e['vertices']]; lift=tuple(sorted((tuple(a['lift']),tuple(b['lift']))))
        parentfaces={frozenset(poly) for poly in (large['faces'][f] for f in large['ef'][lift])}
        assert parentfaces=={frozenset(tuple(k) for k in f) for f in e['parent_face_lifts']}
        intact=(a['xcheck'] is not None and b['xcheck'] is not None and len(e['incident_faces'])==2)
        for v in (a,b):
            kept={tuple(vs[w]['lift']) for ee in qes if v['id'] in ee['vertices'] for w in ee['vertices'] if w!=v['id']}
            intact &= kept=={tuple(k) for k in v['parent_neighbours']}
        intact &= all(all(es[i]['qubit'] is not None for i in fedge[f]) for f in e['incident_faces'])
        if intact: recomputed.append(e['id'])
    assert recomputed==[v['edge'] for v in obj['eligible']]
    for e in obj['eligible']:
        ee=es[e['edge']]; vertices=[vs[v] for v in ee['vertices']]
        checks=[v['xcheck'] for v in vertices]+[fs[f]['zcheck'] for f in sorted(ee['incident_faces'])]
        assert checks==e['checks'] and len(set(checks))==4
        weights=[sum(hx[int(c[1:])]) if c[0]=='X' else sum(hz[int(c[1:])]) for c in checks]
        assert weights==e['weights'] and weights[2:]==[4,4]
        assert e['endpoint_degrees']==sorted(weights[:2])
        assert e['query']==[[c,t] for c in checks for t in (1,2)] and len({tuple(x) for x in e['query']})==8
    return dict(family=obj['family'],n=n,rank_X=rx,rank_Z=rz,k=1,dX=3,dZ=3,eligible_edges=len(recomputed),
                endpoint_degree_pairs=sorted({tuple(e['endpoint_degrees']) for e in obj['eligible']}),
                checks=dict(commutation=True,relative_boundary=True,disk=True,unit_rhombi=True,no_overlap=True,area_matches=True,
                            larger_parent_stars_and_faces=True,exhaustive_short_supports=tests,weight_three_witnesses=True,anticommutation=1,eight_coordinates=True),
                logical_X=obj['logical_X'],logical_Z=obj['logical_Z'])
def run(out):
    import pilot
    certs=[]
    for family in ('square','AB','Penrose'):
        obj=json.loads((out/(family+'.json')).read_text(encoding='utf-8')); cert=verify(obj,pilot.parent(family,True)); pilot.save(out/(family+'_certificate.json'),cert); certs.append(cert)
        print('CERTIFIED',family,cert['n'],cert['eligible_edges'],cert['endpoint_degree_pairs'],flush=True)
    pilot.save(out/'comparison.json',certs)
if __name__=='__main__':
    import sys
    run(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'results')
