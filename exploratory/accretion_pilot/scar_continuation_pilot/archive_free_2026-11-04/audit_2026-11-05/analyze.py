"""Independent comparisons of fresh traces and pinned artifacts. No reader search."""
import json,math,time,subprocess,hashlib,inspect,platform,sys,os
from pathlib import Path
import observe as O
HERE=Path(__file__).resolve().parent
OUT=HERE/'results';OUT.mkdir(exist_ok=True)
PIN='e4a7503b5273dbc1fa72232de5c29b7048672b0d'
PREFIX='exploratory/accretion_pilot/scar_continuation_pilot/archive_free_2026-11-04/'
def git(*args):return subprocess.check_output(['git',*args],cwd=O.REPO)
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2,default=str)+'\n',encoding='utf-8')
def keys(ts):return [repr(O.AF.dk(t)) for t in ts]
def coords(a,b):
    am={O.AF.dk(t):t for t in a};bm={O.AF.dk(t):t for t in b}
    assert len(am)==len(a) and len(bm)==len(b)
    equal=am.keys()==bm.keys()
    delta=max((abs(x-y) for k in am.keys()&bm.keys() for x,y in zip(am[k][1:],bm[k][1:])),default=0.)
    return dict(decorated_key_sets_equal=equal,max_coordinate_difference=delta,
                raw_tiles_equal_by_key=equal and all(am[k]==bm[k] for k in am),ordered_raw_tiles_equal=a==b)
def stars(ts):
    p=O.AF.L.Patch(ts)
    bad=[k for k in list(p.V) if not p.vertex_ok(k,[])]
    complete=O.VS.complete_star_check(p)
    return dict(vertices=len(p.V),all_complete_and_partial_vertices_valid=not bad,bad=bad,**complete)
def normalized(ts):
    anchor=min((z for t in ts for z in t[1:]),key=lambda z:(z.real,z.imag))
    return tuple(sorted((t[0],*((round((z-anchor).real,6),round((z-anchor).imag,6)) for z in t[1:])) for t in ts))

def main():
    exports=json.loads(git('show',PIN+':'+PREFIX+'input/worker_band_exports.json'))
    records=[];groups_raw={};groups_key={};groups_translation={}
    for w,si in O.AF.B_JAMS:
        tag=f'{w}-{si}';case=f'w{w}-B-s{si}'
        while not (O.CACHE/f'spawn-messages-{tag}.pkl').exists():time.sleep(2)
        print('[analyze]',case,flush=True)
        trace=O.load(f'trace-{tag}.pkl');rec,pre=O.load(f'verify-{tag}.pkl')
        full=[r for r in trace['calls'] if not r['skin']];worker=[r for r in trace['calls'] if r['skin']]
        assert len(full)==len(worker)==44
        step_rows=[]
        for s,(f,b) in enumerate(zip(full,worker),1):
            sf,sb=O.signature(f),O.signature(b)
            checks={k:sf[k]==sb[k] for k in sf}
            step_rows.append(dict(step=s,checks=checks,placed=len(b['added']),status=b['result'][0],
                                  full_signature=sf,worker_signature=sb))
        spawned=[json.loads(x) for x in (O.CACHE/f'spawn-{tag}.jsonl').read_text().splitlines()]
        spawned_checks=[]
        jam=rec['jam_step']
        for s,r in enumerate(spawned,jam):
            expected=O.signature(worker[s-1]);actual=r['signature']
            spawned_checks.append(dict(step=s,checks={k:actual[k]==expected[k] for k in expected},signature=actual,prune=r['prune']))
        bfinal=[O.IW.dtile(t) for t in trace['final_state']['tiles']]
        bjam=[O.IW.dtile(t) for t in pre['tiles']]
        bspawn=[O.IW.dtile(t) for t in O.load(f'spawn-state-{tag}.pkl')['tiles']]
        original=exports[f'w{w}-s{si}']
        raw=dict(jam=coords(bjam,[O.IW.dtile(t) for t in original['jam']]),
                 final=coords(bfinal,[O.IW.dtile(t) for t in original['final']]),spawn_final=coords(bspawn,bfinal))
        jp=O.cached_jam(w,si)
        # Compare to the earlier independently audited full-patch replay if available.
        previous=O.CACHE.parent/'scar-cache'/f'trace-{w}-{si}.pkl'
        prior={}
        if previous.exists():
            import pickle
            old=pickle.loads(previous.read_bytes())
            prior=dict(ordered_geometry=all(f['post']==r['post'] for f,r in zip(full,old)),
                       prng_before=all(f['rng_before']==r['rng_before'] for f,r in zip(full,old)),
                       prng_after=all(f['rng_after']==r['rng_after'] for f,r in zip(full,old)),
                       same_length=len(full)==len(old))
        p=O.AF.L.Patch(bfinal)
        local_front={O.AF.frontier_id(e) for e in p.frontier()}
        true_front={O.AF.frontier_id(e) for e in worker[-1]['frontier_after']}
        prunes=trace['prunes'][1:] # constructor clears its seed additions after initial prune
        payload=O.AF.RD.build_payload(jp['Sstar'],jp['cs'],bfinal)
        metadata={k:v for k,v in payload.items() if k!='tiles'}
        write(f'readout_metadata_{tag}.json',metadata)
        accesses=json.loads((O.CACHE/f'spawn-access-{tag}.json').read_text())
        # Keep filesystem provenance inspectable; bytecode, rule catalogue and source
        # imports are not mistaken for trajectory reads.
        data_access=[p for p in accesses if p.lower().endswith(('.json','.pkl','.csv','.txt','.npy','.npz'))]
        entry=dict(case=case,jam_step=jam,steps=step_rows,spawned_steps=spawned_checks,
                   all_steps_progress=all(r['placed']>0 and r['status']=='ok' for r in step_rows),
                   prior_audited_full_patch=prior,raw_geometry=raw,prune_observations=prunes,
                   initial_B_legal=O.AF.L.Patch(jp['Sstar']).legal(jp['B']),
                   endpoint_full_stars=stars(full[-1]['post']),endpoint_band_stars=stars(bfinal),
                   cavity_edges_in_local_index=len(local_front-true_front),true_front_missing_from_local_index=len(true_front-local_front),
                   cumulative_labels=rec['cumulative_scar_labels'],currently_blocked=rec['current_blocked_edges'],
                   n_full=len(full[-1]['post']),n_band=len(bfinal),spawn_data_file_access=data_access)
        records.append(entry)
        groups_raw.setdefault(repr(sorted(bjam,key=lambda t:repr(O.AF.dk(t)))),[]).append(case)
        groups_key.setdefault(repr(sorted(keys(bjam))),[]).append(case)
        groups_translation.setdefault(repr(normalized(bjam)),[]).append(case)
        write('execution_checks.json',records)
    write('case_equivalence.json',dict(
        absolute_raw_coordinate_groups=list(groups_raw.values()),absolute_decorated_key_groups=list(groups_key.values()),
        translation_normalized_6_decimal_groups=list(groups_translation.values()),
        definition='Translation normalization subtracts lexicographically smallest raw vertex; preserves decoration and A/B/C vertex order, rounds relative coordinates to 6 decimal places. No rotations/reflections normalized; no statistical independence inferred.'))
    # Provenance of loaded dependency modules, with actual paths and content hashes.
    mods={}
    frozen=Path(os.environ['EFP_SNAPSHOT']).resolve().parents[2]
    for name,m in sorted(sys.modules.items()):
        f=getattr(m,'__file__',None)
        if not f:continue
        path=Path(f).resolve()
        if path.is_file() and (path.is_relative_to(frozen) or path.is_relative_to(O.REPO)):
            mods[name]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    import numpy,scipy,matplotlib
    write('environment.json',dict(python=sys.version,executable=sys.executable,platform=platform.platform(),
          numpy=numpy.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,modules=mods,
          pinned_commit=PIN,frozen_commit=git('-C',str(frozen),'rev-parse','HEAD').decode().strip(),
          fork_cache_sha256=hashlib.sha256((O.REPO/'exploratory/accretion_pilot/jam_repair_pilot/results/baseline/forks.pkl').read_bytes()).hexdigest()))
    print('Independent trace analysis complete.',flush=True)

if __name__=='__main__':
    import os
    main()
