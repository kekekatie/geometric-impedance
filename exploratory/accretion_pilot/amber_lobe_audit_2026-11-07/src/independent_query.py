"""Separate diagnostic: no call to original local_witness or summarize."""
import math, copy, json, collections
import run as R
from run import C, HERE, ORIGINAL
L,D,IW,AF=C.L,C.D,C.IW,C.AF

def main():
    states=C.load('w7-s0-r2-c0-states.pkl')
    baseline=[r for r in C.old('trace-7-0.pkl')['calls'] if not r['skin']]
    history=L.Patch(baseline[22]['pre']);first=None;checked=0
    for step,m in enumerate(states['actual'],23):
        for t in m['placed']:history.add(t)
        band=L.Patch(m['tiles'])
        pinned={frozenset(tuple(v) for v in ek) for ek in m['scars']}
        mismatches=[]
        for e in history.frontier():
            if AF.edge_id(*e[:2]) not in pinned:continue
            got=C.keys(D.candidates(band,*e[:3]));want=C.keys(D.candidates(history,*e[:3]));checked+=1
            if got!=want:mismatches.append((e,got,want))
        if mismatches:
            first=(step,m,history,band,pinned,mismatches);break
    assert first and first[0]==35
    step,m,history,band,pinned,mismatches=first
    edge,got,want=mismatches[0]
    assert got and want==[]
    diagnostics=json.loads((ORIGINAL/'results/query_diagnostics.json').read_text())
    witness=next(x for x in diagnostics if x['case']=='w7-B-s0' and x['radius']==2)
    extra=[IW.dtile(t) for t in witness['witness']['minimal']['tiles']]
    assert len(extra)==1 and C.dk(extra[0]) in {C.dk(t) for t in history.tris}
    assert C.dk(extra[0]) not in {C.dk(t) for t in band.tris}
    restored=C.keys(D.candidates(L.Patch(band.tris+extra),*edge[:3]))
    assert restored==want
    # Build the reported one-vertex corner record independently from its tile.
    summary=witness['vertex_summary'];assert len(summary)==1
    vertex=tuple(summary[0]['vertex']);t=extra[0];pts=dict(zip('ABC',t[1:]));records=[]
    orientation=((t[2]-t[1]).real*(t[3]-t[1]).imag-(t[2]-t[1]).imag*(t[3]-t[1]).real)>0
    for name,others in (('A','BC'),('B','CA'),('C','AB')):
        v=pts[name]
        if L.key(v)!=vertex:continue
        p,q=(pts[x] for x in others)
        a=math.atan2((p-v).imag,(p-v).real);b=math.atan2((q-v).imag,(q-v).real)
        angle=(b-a)%(2*math.pi)
        if angle>math.pi:a,b,angle=b,a,2*math.pi-angle
        records.append((a%(2*math.pi),angle,(t[0],name,orientation)))
    assert json.loads(json.dumps(records))==summary[0]['arcs']
    summarized=L.Patch(band.tris)
    summarized.V[vertex]+=records
    summarized_menu=C.keys(D.candidates(summarized,*edge[:3]))
    assert summarized_menu==want and summarized.tris==band.tris
    assert dict(summarized.edges)==dict(band.edges)
    # Diagnostic-only reconstruction of the already verified true-boundary state.
    # Full-history boundary is used here, never passed back to a scientific worker.
    from worker import LiveSkin
    state=C.load('w7-s0-r2-c0-input.pkl')
    state=copy.deepcopy(state);state['tiles']=[IW.etile(t) for t in band.tris]
    state['boundary']=[dict(p=IW.ez(e[0]),q=IW.ez(e[1]),r=IW.ez(e[2]),owner=None) for e in history.frontier()]
    state['scars']=m['scars'];state['rng_state']=list(m['rng_after'])
    P=IW.rebuild_skin(state);P.__class__=LiveSkin
    assert C.front(P)==m['frontier_after']
    before_pin=set(pinned);queried=[];original=D.candidates
    def guard(Q,*e):
        key=AF.edge_id(*e[:2]);assert key not in before_pin,'Scheduler reconsidered a pinned edge'
        queried.append(AF.frontier_id(e));return original(Q,*e)
    D.candidates=guard
    try:result=C.SCN.patient_scar(P,IW.rebuild_rng(state),set(pinned),verify_legal=True)
    finally:D.candidates=original
    assert P.additions==baseline[35]['added'] and result[:3]==baseline[35]['result'][:3]
    out=dict(first_mismatch_step=step,queries_checked_through_first_mismatch=checked,edge=AF.frontier_id(edge),
        reduced_menu=got,full_history_menu=want,one_tile_restored_menu=restored,
        no_context_fails=True,one_tile_is_deleted_full_history_tile=True,one_tile_count_minimal_for_this_query=True,
        independently_derived_corner=summary,vertex_only_menu=summarized_menu,vertex_only_preserves_tiles_and_edges=True,
        diagnostic_next_step=36,scheduler_calls=len(queried),pinned_edges_queried=0,next_step_placements_equal=True,
        constructor_received_no_restoration=True,scope='First primary w7-s0 scar query only; no global or future minimality assertion.',all_passed=True)
    C.dump(HERE/'independent_query.json',out)
    print(json.dumps(out,indent=2),flush=True)

if __name__=='__main__':main()
