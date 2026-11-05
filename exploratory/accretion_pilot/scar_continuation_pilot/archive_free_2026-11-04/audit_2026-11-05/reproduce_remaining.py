"""Execute original report/test entry points, reusing this audit's deterministic traces.

Spawned restart still executes the ORIGINAL _worker_proc. Its observational wrapper
writes reduced step signatures and overwrites one current retained-state snapshot;
it receives no evaluator state and retains no cumulative geometry trace.
"""
import os, sys, json, time, multiprocessing as mp
from pathlib import Path

def traced_worker(conn,state,tag):
    accessed=[]
    def audit(event,args):
        if event=='open':
            p=args[0]
            if isinstance(p,(str,bytes)):accessed.append(str(p))
    sys.addaudithook(audit)
    import observe as O
    obs=O.Observer();obs.install()
    wrapped_prune=O.AF.E.ActiveSkin.prune
    target=O.CACHE/f'spawn-{tag}.jsonl'
    target.write_text('')
    def prune(P):
        n=wrapped_prune(P)
        if obs.calls:
            record=dict(signature=O.signature(obs.calls[-1]),prune=obs.prunes[-1])
            with target.open('a') as f:f.write(json.dumps(record)+'\n')
        # Diagnostic records are exported, never supplied as constructor input.
        obs.calls.clear();obs.prunes.clear()
        O.save(f'spawn-state-{tag}.pkl',obs.final_state)
        return n
    O.AF.E.ActiveSkin.prune=prune
    try:O.IW._worker_proc(conn,state)
    finally:
        obs.restore()
        (O.CACHE/f'spawn-access-{tag}.json').write_text(json.dumps(sorted(set(accessed)),indent=2))

def main():
    import observe as O
    import restart_prescar as RP
    import endpoint_geom as EG
    import test_supplement as TS
    import test_failstop as TF
    original_spawn=O.IW.run_spawned
    current=['test']
    def spawn(state,n_steps):
        tag=current[0]
        path=O.CACHE/f'spawn-messages-{tag}.pkl'
        if path.exists():return O.load(path.name)
        ctx=mp.get_context('spawn'); parent,child=ctx.Pipe()
        proc=ctx.Process(target=traced_worker,args=(child,state,tag));proc.start();child.close()
        out=[]
        try:
            msg=parent.recv();assert msg['kind']=='ready',msg;out.append(msg)
            for _ in range(n_steps):
                parent.send('STEP');msg=parent.recv()
                assert msg['kind']=='step',msg
                out.append(msg)
                if msg['status']=='total_arrest':break
        finally:
            if proc.is_alive():parent.send('STOP')
            proc.join(30)
            if proc.is_alive():proc.terminate();proc.join();raise RuntimeError('worker failed to terminate')
            parent.close()
        O.save(path.name,out);return out
    def full(w,si):
        current[0]=f'{w}-{si}'
        trace=O.load(f'trace-{w}-{si}.pkl')
        calls=[r for r in trace['calls'] if not r['skin']]
        return [(s,[repr(O.AF.dk(t)) for t in row['added']]) for s,row in enumerate(calls,1)],O.cached_jam(w,si)['jam_step']
    def worker(w,si):
        trace=O.load(f'trace-{w}-{si}.pkl')
        calls=[r for r in trace['calls'] if r['skin']]
        return [(s,[repr(O.AF.dk(t)) for t in row['added']]) for s,row in enumerate(calls,1)],[O.IW.dtile(t) for t in trace['final_state']['tiles']]
    # Wait for each freshly computed verification cache; never consume historical outputs.
    cases=[(7,0)]+[c for c in O.AF.B_JAMS if c!=(7,0)]
    original_cases=O.AF.B_JAMS
    restarts=[]
    for w,si in cases:
        while not (O.CACHE/f'verify-{w}-{si}.pkl').exists():time.sleep(2)
        print(f'[spawn setup/run] w{w}-s{si}',flush=True)
        rec,pre=O.load(f'verify-{w}-{si}.pkl')
        O.VS.INPUT.mkdir(exist_ok=True)
        # Run original main on one fresh state, accumulate the exact output records.
        (RP.INPUT/'prescar_states.json').write_text(json.dumps({f'w{w}-s{si}':pre}))
        RP.full_patch_placements=full;RP.uninterrupted_worker_placements=worker
        O.IW.run_spawned=spawn;O.AF.B_JAMS=[(w,si)]
        RP.main()
        restarts.extend(json.loads((RP.RESULTS/'prescar_restart.json').read_text()))
    O.AF.B_JAMS=original_cases
    prestates={f'w{w}-s{si}':O.load(f'verify-{w}-{si}.pkl')[1] for w,si in original_cases}
    (RP.INPUT/'prescar_states.json').write_text(json.dumps(prestates,default=float))
    bycase={r['case']:r for r in restarts}
    (RP.RESULTS/'prescar_restart.json').write_text(json.dumps([bycase[f'w{w}-B-s{si}'] for w,si in original_cases],indent=2))
    EG.worker_final_band=lambda w,si:worker(w,si)[1]
    EG.main()
    O.VS.verify_case=O.cached_verify
    current[0]='7-0'
    TS.main()
    # Failure fixture must execute real verifier with the injection, not a cached success.
    O.VS.verify_case=O.ORIGINAL_VERIFY
    TF.main()
    print('Original restart, endpoint and focused tests completed.',flush=True)

if __name__=='__main__':main()
