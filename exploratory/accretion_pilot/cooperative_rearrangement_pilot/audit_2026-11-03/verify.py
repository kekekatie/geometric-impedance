"""Independent bounded checks. Run with EFP_SNAPSHOT set; no historical writes."""
import sys, json, math, cmath, itertools, collections, hashlib, platform
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import linprog
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'src'))
import coop_common as C
import part3_necessary as P3
import part4_search as P4
import hexflip as H

def dump(name, obj):
    (HERE / 'results').mkdir(exist_ok=True)
    (HERE / 'results' / name).write_text(json.dumps(obj, indent=2, default=lambda x: x.item() if hasattr(x,'item') else str(x)))

def components(nodes, adj):
    unseen=set(nodes); out=[]
    while unseen:
        todo=[min(unseen)]; co=set()
        while todo:
            u=todo.pop()
            if u not in unseen: continue
            unseen.remove(u); co.add(u); todo.extend(adj[u] & unseen)
        out.append(co)
    return out

def enum_dfs(adj,seeds,k):
    """Include/exclude frontier DFS, roots partitioned by least contained seed."""
    out=set(); earlier=set()
    def visit(cur,front,excluded):
        out.add(frozenset(cur))
        if len(cur)==k: return
        front=set(front); excluded=set(excluded)
        while front:
            v=min(front); front.remove(v)
            visit(cur|{v},front | (adj[v]-cur-excluded-{v}),excluded)
            excluded.add(v)
    for root in sorted(seeds):
        visit({root},adj[root]-earlier,earlier)
        earlier.add(root)
    return out

def synthetic():
    cases=0
    original=C.edge_adjacency
    try:
        for n in range(1,6):
            edges=list(itertools.combinations(range(n),2))
            for mask in range(1<<len(edges)):
                adj={i:set() for i in range(n)}
                for j,(u,v) in enumerate(edges):
                    if mask>>j&1: adj[u].add(v);adj[v].add(u)
                for seeds in ({0},set(range(n)),{0,n-1}):
                    expected=set()
                    for size in range(1,min(n,4)+1):
                        for seq in itertools.combinations(range(n),size):
                            ss=set(seq)
                            if ss&seeds and len(components(ss,adj))==1: expected.add(frozenset(ss))
                    C.edge_adjacency=lambda _:adj
                    assert set(C.connected_regions([],seeds,4,10000))==expected
                    assert enum_dfs(adj,seeds,4)==expected
                    cases+=1
    finally: C.edge_adjacency=original
    return cases

def phase(rows):
    if not rows: return dict(status=0,margin=None)
    a=np.array([[-nx,-ny,1] for nx,ny,c in rows]); b=-np.array([c for nx,ny,c in rows])
    r=linprog([0,0,-1],A_ub=a,b_ub=b,bounds=[(None,None)]*3,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    return dict(status=int(r.status),margin=float(r.x[2]) if r.status==0 else None)

def main():
    st,band,rank,dead,witness=P3.load_band(); B=C.BandConstraints(band,rank)
    tiles=sorted(band,key=C.dk); keys=[C.dk(t) for t in tiles]; ids={d:i for i,d in enumerate(keys)}
    # Adjacency constructed pairwise from vertex intersections, independently of edge index.
    vs=[set(C.L.key(z) for z in t[1:]) for t in tiles]
    adj={i:set() for i in range(len(tiles))}
    for i in range(len(tiles)):
        for j in range(i):
            if len(vs[i]&vs[j])==2: adj[i].add(j);adj[j].add(i)
    seeds={i for i,v in enumerate(vs) if v & (dead|witness)}
    hist=C.connected_regions(band,P3.seeds_from(band,dead|witness),8,50000)
    expected=enum_dfs(adj,seeds,8)
    encoded={frozenset(ids[d] for d in r) for r in hist}
    assert encoded==expected and len(hist)==len(encoded)
    synthetic_cases=synthetic()
    # Independent lift: nearest of ten physical unit directions, different traversal.
    directions=[C.S*cmath.exp(1j*(math.pi/10+2*math.pi*j/5)) for j in range(5)]
    legadj=collections.defaultdict(list); pos={}
    for t in band:
        for p,q in itertools.combinations(t[1:],2):
            if abs(abs(q-p)-C.S)>1e-4*C.S: continue
            v,w=C.L.key(p),C.L.key(q);pos[v]=p;pos[w]=q
            err,j,sg=min((abs(q-p-sg*d),j,sg) for j,d in enumerate(directions) for sg in [-1,1])
            assert err<1e-8
            dv=np.zeros(5,dtype=int);dv[j]=sg
            legadj[v].append((w,dv));legadj[w].append((v,-dv))
    root=min(pos); K={root:np.zeros(5,dtype=int)}; stack=[root]; conflicts=0
    while stack:
        v=stack.pop()
        for w,dv in legadj[v]:
            nxt=K[v]+dv
            if w in K: conflicts+=int(not np.array_equal(K[w],nxt))
            else: K[w]=nxt;stack.append(w)
    assert len(K)==len(pos) and conflicts==0
    shift=B.K[root]
    assert all(np.array_equal(K[v]+shift,B.K[v]) for v in K)
    # Windows come from the exported current state, not the imported WIN.
    rows_by_v={}; contrib={}
    for v,k in K.items():
        k=k+shift;rk=rank[int(sum(k))]
        z=sum(int(k[j])*cmath.exp(4j*math.pi*j/5) for j in range(5))
        win=st['windows'][rk]; cr={};rr=[]
        for i,(nx,ny) in enumerate(win['normals']):
            val=nx*z.real+ny*z.imag-win['h'];norm=math.hypot(nx,ny)
            cr[(rk,i)]=val;rr.append((nx/norm,ny/norm,val/norm))
        contrib[v]=cr;rows_by_v[v]=rr
    unique={}; maxdiff=0.; engulf_count=collections.Counter();comp_counts=collections.Counter();row_mismatch=0
    allv=set(K);worst=None
    for r in sorted(expected,key=lambda r:(len(r),sorted(r))):
        outside=set(range(len(tiles)))-set(r)
        surviving=set().union(*(vs[i] for i in outside))
        cm={}
        for v in surviving:
            for key,val in contrib[v].items(): cm[key]=max(cm.get(key,-math.inf),val)
        old,E=B.exterior_cmax({keys[i] for i in r})
        assert E==allv-surviving and set(cm)==set(old)
        diff=max(abs(cm[k]-old[k]) for k in cm);maxdiff=max(maxdiff,diff)
        assert diff<1e-12
        signature=tuple(sorted(cm.items()))
        if signature not in unique:
            raw=[row for v in surviving for row in rows_by_v[v]]
            result=phase(raw)
            assert result['status']==0 and result['margin'] < -1e-6
            unique[signature]=result
        engulf_count[len(E)]+=1
        comp_counts[len(components(outside,adj))]+=1
    # Exhaustive abstract deletion minimum, including all lower cardinalities.
    ks=sorted(B.full_cmax); facet=[]; feasible4=[]
    for size in range(5):
        counts=collections.Counter();margins=[]
        for drop in itertools.combinations(ks,size):
            rows=[]
            for key in ks:
                if key in drop:continue
                nx,ny=C.WIN[key[0]][0][key[1]];norm=math.hypot(nx,ny)
                rows.append((nx/norm,ny/norm,B.full_cmax[key]/norm))
            rr=phase(rows)
            verdict='feasible' if rr['status']==3 or (rr['status']==0 and rr['margin']>=-1e-9) else 'infeasible' if rr['status']==0 else 'unresolved'
            counts[verdict]+=1
            if rr['margin'] is not None:margins.append(rr['margin'])
            if size==4 and verdict=='feasible': feasible4.append(drop)
        facet.append(dict(size=size,counts=dict(counts),largest_margin=max(margins,default=None)))
    saved=json.loads((C.RESULTS/'part3_necessary.json').read_text())
    selected={tuple(v) for v in saved['obstruction']['greedy_vertex_engulfment']['vertices']}
    footprint={i for i,v in enumerate(vs) if v&selected};surv=set().union(*(vs[i] for i in set(adj)-footprint))
    engulfed=allv-surv
    raw=[row for v in surv for row in rows_by_v[v]]
    cm,E=B.exterior_cmax({keys[i] for i in footprint})
    boundary_ids=lambda records:{frozenset((C.L.key(complex(*d['p'])),C.L.key(complex(*d['q'])))) for d in records}
    true_edges=boundary_ids(st['true_frontier']);inner_edges=boundary_ids(st['inner_boundary'])
    rempatch=C.L.Patch([tiles[i] for i in set(adj)-footprint])
    remainder_edges={C.ekey(e[0],e[1]) for e in rempatch.frontier()}
    all_foot_vs=set().union(*(vs[i] for i in footprint))
    span=lambda verts:max((abs(complex(*a)-complex(*b))/C.S for a in verts for b in verts),default=0)
    pat=C.L.Patch(band);front={C.ekey(e[0],e[1]):e for e in pat.frontier()}
    def frontier_counts(ekeys):
        cc=collections.Counter(len(C.D.candidates(pat,*front[e][:3])) for e in ekeys)
        return dict(n_edges=len(ekeys),histogram=dict(sorted(cc.items())))
    result=dict(environment=dict(python=sys.version,platform=platform.platform(),numpy=np.__version__,scipy=scipy.__version__),
        input_provenance=st['provenance'],n_tiles=len(band),n_vertices=len(K),rank=rank,independent_lift_conflicts=conflicts,
        enumeration=dict(n_seeds=len(seeds),n_regions=len(expected),by_size=dict(sorted(collections.Counter(map(len,expected)).items())),exact_set_agreement=True,synthetic_graph_seed_cases=synthetic_cases,exterior_tile_components=dict(sorted(comp_counts.items())),engulfed_vertex_counts=dict(sorted(engulf_count.items())),lexicographic_order_matches=hist==sorted(hist,key=lambda r:(len(r),sorted(r)))),
        constraints=dict(max_coefficient_difference=maxdiff,n_unique_aggregated_systems=len(unique),all_unaggregated_box_free_margins_negative=True,margin_range=[min(x['margin'] for x in unique.values()),max(x['margin'] for x in unique.values())]),
        facet_deletion=dict(exhaustive_by_cardinality=facet,n_feasible_size4=len(feasible4),example=feasible4[0]),
        greedy=dict(selected_vertices=len(selected),union_tiles=len(footprint),components=len(components(footprint,adj)),actual_removed_vertices=len(engulfed),collateral_vertices=sorted(engulfed-selected),selected_vertex_span_S=span(selected),whole_footprint_span_S=span(all_foot_vs),actual_exterior_raw_LP=phase(raw),aggregate_verdict=C.classify_exterior(cm),true_boundary_edges_lost=len(true_edges-remainder_edges),inner_boundary_edges_lost=len(inner_edges-remainder_edges),is_fixed_boundary_replacement=False),
        baseline_frontiers=dict(true=frontier_counts(true_edges),inner=frontier_counts(inner_edges),all=frontier_counts(set(front))))
    dump('independent.json',result);print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
