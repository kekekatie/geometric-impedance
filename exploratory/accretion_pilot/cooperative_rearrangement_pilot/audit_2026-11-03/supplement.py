"""Gauge, numeric failure, shortcut and selected timing checks."""
import sys,json,collections,itertools,math
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'src'))
import coop_common as C
import part3_necessary as P
import feas
from verify import components,dump

def main():
    st,band,rank,dead,witness=P.load_band();B=C.BandConstraints(band,rank)
    assert all(abs(float(C.WIN[r][1])-w['h'])<1e-15 and all(abs(float(a)-b)<1e-15 for nn,mm in zip(C.WIN[r][0],w['normals']) for a,b in zip(nn,mm)) for r,w in enumerate(st['windows']))
    regions=C.connected_regions(band,P.seeds_from(band,dead|witness),8,50000)
    shortcuts=collections.Counter();deltas=[];systems={};liftcomps=collections.Counter()
    tilelegs={C.dk(t):[(C.L.key(p),C.L.key(q)) for p,q in itertools.combinations(t[1:],2) if abs(abs(q-p)-C.S)<1e-4*C.S] for t in band}
    example=None
    for r in regions:
        cm,E=B.exterior_cmax(r);delta=max(abs(cm[k]-B.full_cmax[k]) for k in cm)
        shortcuts['no_engulfment' if not E else 'exact_unchanged' if cm==B.full_cmax else 'changed']+=1
        if cm!=B.full_cmax:deltas.append(delta)
        systems[tuple(sorted(cm.items()))]=cm
        adj=collections.defaultdict(set)
        for key,legs in tilelegs.items():
            if key in r:continue
            for a,b in legs:adj[a].add(b);adj[b].add(a)
        comps=components(set(adj),adj);liftcomps[len(comps)]+=1
        if len(comps)>1 and example is None:example=sorted(r)
    numerics=[]
    for cm in systems.values():
        rows=[(r[0],r[1]) for r in feas.rows_from_cmax(cm)]
        numerics.append(dict(box50=feas.chebyshev_rows(rows,50)['x'][2],box1e6=feas.chebyshev_rows(rows,1e6)['x'][2],box_free=C.box_free_feasible(cm),sensitivity=feas.sensitivity(cm)))
    fake=lambda *args,**kwargs:SimpleNamespace(status=4,x=None,message='audit forced failure')
    old=C.linprog;C.linprog=fake
    try:free_failure=C.classify_exterior(B.full_cmax)
    finally:C.linprog=old
    old=feas.linprog;feas.linprog=fake
    try:box_failure=C.classify_exterior(B.full_cmax)
    finally:feas.linprog=old
    assert free_failure['verdict']==box_failure['verdict']=='unresolved'
    greedy=json.loads((C.RESULTS/'part3_necessary.json').read_text())['obstruction']['greedy_vertex_engulfment']
    vertices={tuple(v) for v in greedy['vertices']};R=set().union(*(B.vincident[v] for v in vertices));cm,_=B.exterior_cmax(R)
    sensitivity=feas.sensitivity(cm)
    # One original recorded continuation only, not the 88-arm programme.
    ev=json.loads((C.INPUT/'evaluator_historical.json').read_text())
    Sstar=[C.dtile(t) for t in ev['Sstar']];cs=[C.dtile(t) for t in ev['options_cs']]
    arm=C.PC.grow(Sstar,cs[1],ev['stream'],44)
    timeline=[]
    for step in [0,8,9,22,23]:
        tiles=arm['snaps'][step];bc=C.BandConstraints(tiles,C.Sl.rank_of(tiles))
        timeline.append(dict(step=step,tiles=len(tiles),feasibility=C.classify_exterior(bc.full_cmax)))
    full=arm['snaps'][-1];rebuilt,_=C.PC.skin_of(full)
    assert {C.dk(t) for t in rebuilt}=={C.dk(t) for t in band}
    fullfront=C.L.Patch(full).frontier();bandpatch=C.L.Patch(band)
    missing=[]
    for rec in st['dead_sites']:
        p,q,r=(complex(*rec[k]) for k in ('p','q','r'))
        assert len(C.D.candidates(bandpatch,p,q,r))==0
    result=dict(shortcuts=dict(shortcuts),changed_regions_max_delta_range=[min(deltas),max(deltas)],changed_regions_above_1e12=sum(d>1e-12 for d in deltas),n_unique_original_aggregate_systems=len(systems),exterior_leg_graph_components=dict(sorted(liftcomps.items())),disconnected_example=example,
      numerical_checks=numerics,forced_free_solver_failure=free_failure,forced_box_solver_failure=box_failure,greedy_boundary_sensitivity=sensitivity,
      recorded_case=dict(world=ev['world'],stream_index=ev['stream_index'],stream=ev['stream'],option=ev['true_option'],option_shape=cs[1][0],jam_step=len(arm['snaps'])-1,stop=arm['stop'],selected_timeline=timeline,retained_tile_set_exact=True,dead_sites_reconfirmed_from_band=True))
    dump('supplement.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('disconnected_example','numerical_checks')},indent=2),flush=True)

if __name__=='__main__':main()
