import multiprocessing as mp,json,copy,hashlib,subprocess,sys
import common as C
from common import AF,IW,L,D,E,dk,VS
from worker import LiveSkin,constructor

def prepare(w,si,radius,collar):
    rec,state=C.old(f'verify-{w}-{si}.pkl');state=copy.deepcopy(state)
    trace=C.old(f'trace-{w}-{si}.pkl');full=[r for r in trace['calls'] if not r['skin']]
    jam=rec['jam_step'];base=full[jam-1]
    if radius==3:state['tiles']=[IW.etile(t) for t in base['pre']]
    P=IW.rebuild_skin(state);P.__class__=LiveSkin;P.radius=radius
    pinned={AF.edge_id(*e[:2]) for e in P.frontier() if not D.candidates(P,*e[:3])}
    assert pinned==set(base['result'][3]),'Initial reconnaissance must match original first scar scan'
    meta=P.thin(pinned,collar)
    rng=IW.rebuild_rng(state)
    return IW.serialize_state(P,rng,pinned),full,jam,meta

def local_witness(P,tiles,edge,expected):
    """Evaluator-only query diagnostic; never restores a running constructor."""
    have={dk(t) for t in tiles};missing=[t for t in P.tris if dk(t) not in have]
    def answer(extra):return C.keys(D.candidates(L.Patch(list(tiles)+extra),*edge[:3]))
    radii=[];good=None
    for rho in (0,.5,1,1.5,2):
        extra=[t for t in missing if any(abs(z-v)<=rho*C.S+1e-12 for z in t[1:] for v in edge[:2])]
        ok=answer(extra)==expected;radii.append(dict(radius=rho,added_tiles=len(extra),matches=ok))
        if ok and good is None:good=extra
    minimal=None;checks=0
    if good is not None and len(good)<=64:
        keep=sorted(good,key=lambda t:repr(dk(t)))
        for t in list(keep):
            if checks>=128:break
            trial=[u for u in keep if u is not t];checks+=1
            if answer(trial)==expected:keep=trial
        minimal=dict(n_tiles=len(keep),tiles=[IW.etile(t) for t in keep],subset_checks=checks,
                     scope='one-pass deletion-minimal for this single observed query; not cardinality-minimal or a global continuation guarantee')
    return dict(edge=repr(AF.edge_id(*edge[:2])),expected=expected,without_restoration=answer([]),radii=radii,minimal=minimal)

def run(w,si,radius=2,collar=0):
    name=f'w{w}-s{si}-r{radius}-c{collar:g}';path=C.RESULTS/(name+'.json')
    if path.exists():return json.loads(path.read_text())
    state,baseline,jam,initial=prepare(w,si,radius,collar)
    C.save(name+'-input.pkl',state)
    history=L.Patch(baseline[jam-1]['pre']);rows=[];first={};witness=None;failed=None;actual=[]
    ctx=mp.get_context('spawn');parent,child=ctx.Pipe();p=ctx.Process(target=constructor,args=(child,state,collar));p.start();child.close()
    try:
        ready=parent.recv();assert ready['kind']=='ready',ready
        final=ready['tiles'];snapshots={'jam':list(final)}
        for step in range(jam,45):
            parent.send('STEP');m=parent.recv();assert m['kind']=='step',m
            b=baseline[step-1]
            expected_live=[(edge,C.keys(ts)) for edge,ts in b['candidates'] if ts]
            live=[(edge,ts) for edge,ts in m['candidates'] if ts]
            checks=dict(live_candidate_enumeration=live==expected_live,
                        outcome=m['result'][:3]==b['result'][:3],ordered_placements=m['placed']==b['added'],
                        frontier_before=m['frontier_before']==[AF.frontier_id(e) for e in b['frontier_before']],
                        frontier_after=m['frontier_after']==[AF.frontier_id(e) for e in b['frontier_after']],
                        rng_before=m['rng_before']==b['rng_before'],rng_after=m['rng_after']==b['rng_after'],
                        scars=m['scars']==C.scars(b['scars_after']))
            for k,v in checks.items():
                if not v and k not in first:first[k]=step
            if not checks['live_candidate_enumeration'] and 'live_query' not in first:
                em=dict(expected_live);wm=dict(live)
                edgekey=next(k for k in list(em)+list(wm) if em.get(k)!=wm.get(k))
                first['live_query']=dict(step=step,edge=edgekey,baseline=em.get(edgekey),worker=wm.get(edgekey))
            for i,t in enumerate(m['placed']):
                if not history.legal(t):failed=dict(step=step,batch_position=i,tile=IW.etile(t));break
                history.add(t)
            mon=[]
            for eid,got in m['monitors']:
                e=next((e for e in history.frontier() if AF.frontier_id(e)==eid),None)
                want=C.keys(D.candidates(history,*e[:3])) if e else None
                if got!=want:
                    mon.append(dict(edge=eid,worker=got,evaluator=want))
                    if witness is None and e is not None:witness=dict(step=step,**local_witness(history,m['tiles'],e,want))
            if mon and 'scar_monitor' not in first:first['scar_monitor']=dict(step=step,queries=mon)
            final=m['tiles'];actual.append(m)
            if step in (23,44):snapshots[str(step)]=list(final)
            rows.append(dict(step=step,checks=checks,placed=len(m['placed']),status=m['result'][0],
                             n_full=len(history.tris),retained=len(final),fraction=len(final)/len(history.tris),
                             retention=m['retention'],scar_labels=len(m['scars']),monitor_mismatches=len(mon)))
            if failed or m['result'][0]=='total_arrest':break
    finally:
        if p.is_alive():parent.send('STOP')
        p.join(30)
        if p.is_alive():p.terminate();p.join();raise RuntimeError('worker did not exit')
    fullstars=VS.complete_star_check(history)
    partial_bad=sum(not history.vertex_ok(k,[]) for k in list(history.V) if history.V[k])
    overlaps=VS.overlap_check(history.tris)
    construction_fields=['live_candidate_enumeration','outcome','ordered_placements','frontier_before','frontier_after','rng_before','rng_after','scars']
    fullband=AF.PC.skin_of(baseline[-1]['post'])[0]
    b23=AF.PC.skin_of(baseline[22]['post'])[0]
    rec=dict(case=f'w{w}-B-s{si}',world=w,si=si,radius=radius,collar=collar,jam_step=jam,
             initial_retention=initial,initial_full=len(baseline[jam-1]['pre']),initial_full_band=len(C.old(f'verify-{w}-{si}.pkl')[1]['tiles']),
             completed=rows[-1]['step']==44 and not failed and all(r['status']=='ok' and r['placed']>0 for r in rows),
             equivalent=not any(k in first for k in construction_fields),first_differences=first,validation_failure=failed,
             endpoint_complete_stars=fullstars,endpoint_invalid_partial_or_complete=partial_bad,overlaps=overlaps,
             full_band_step44=len(fullband),full_patch_step44=len(baseline[-1]['post']),full_band_step23=len(b23),
             full_patch_step23=len(baseline[22]['post']),step23_intervention_started=jam<=23,
             monitor_witness=witness,rows=rows)
    C.save(name+'-states.pkl',dict(snapshots=snapshots,actual=actual,history=list(history.tris)))
    C.dump(path,rec);print(name,'complete',rec['completed'],'equivalent',rec['equivalent'],'tiles',len(final),'first',list(first),flush=True)
    return rec

def main():
    cases=[(7,0)]+[c for c in AF.B_JAMS if c!=(7,0)]
    primary=[run(w,si,2) for w,si in cases]
    for radius in (1,3):
        for w,si in cases:run(w,si,radius)
    if any(not r['equivalent'] or not r['completed'] for r in primary):
        for collar in (.5,1,1.5,2):
            restored=[run(w,si,2,collar) for w,si in cases]
            if all(r['equivalent'] and r['completed'] for r in restored):break
    print('Bounded continuation trials complete.',flush=True)
if __name__=='__main__':main()
