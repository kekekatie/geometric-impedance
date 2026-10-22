"""Archive-owning independent process controller; never sends geometry after init."""
from pathlib import Path
import multiprocessing as mp
import pickle,json,random
import figures as F
import active_skin_engine as E
H=Path(__file__).resolve().parent; OUT=H/'active-skin'; OUT.mkdir(exist_ok=True)

def receive(pipe):
    if not pipe.poll(120): raise RuntimeError('Worker timed out')
    msg=pipe.recv()
    if msg['kind']=='error': raise RuntimeError(msg['traceback'])
    return msg

def main():
    _,e=pickle.loads((H/'results/geometry.pkl').read_bytes())
    cases=[('continuation-1',0,False),('continuation-3',2,False),('alternative-29',0,True)]
    report=[]; film=[]
    for name,idx,swap in cases:
        seed=e['base']+[e['cs'][1]]; Q=F.L.Patch(seed); rng=random.Random(e['streams'][idx])
        parent,child=mp.get_context('spawn').Pipe()
        proc=mp.get_context('spawn').Process(target=E.worker,args=(child,seed,e['streams'][idx],2,swap)); proc.start(); child.close()
        rows=[]; frames=[]; initial=None
        try:
            initial=receive(parent)
            assert initial['frontier']==[E.frontier_id(ed) for ed in Q.frontier()]
            for s in range(1,121):
                parent.send('STEP')
                expected=E.inventory(Q); n0=len(Q.tris)
                status,n,kind=E.step(Q,rng,s,swap)
                msg=receive(parent)
                assert msg['before']==expected, f'{name} slice {s}: candidate/frontier mismatch'
                assert (msg['status'],msg['n'],msg['mode'])==(status,n,kind), f'{name} slice {s}: outcome mismatch'
                assert [E.tile_id(t) for t in msg['placed']]==[E.tile_id(t) for t in Q.tris[n0:]],f'{name} slice {s}: placement mismatch'
                assert msg['frontier']==[E.frontier_id(ed) for ed in Q.frontier()],f'{name} slice {s}: frontier mismatch'
                fullkeys={E.tile_id(t) for t in Q.tris}; retained={E.tile_id(t) for t in msg['tiles']}
                assert retained<=fullkeys
                if not swap and s<=20:
                    assert fullkeys=={E.tile_id(t) for t in e['tr'][idx]['snapshots'][s]}
                rows.append(dict(slice=s,status=status,mode=kind,placed=n,edge_queries=len(expected),retained=len(retained),archive=len(fullkeys),dropped=msg['dropped'],frontier=len(msg['frontier'])))
                if s in [1,12,29,44,60,90,120]: frames.append(dict(slice=s,archive=list(Q.tris),skin=msg['tiles'],frontier=Q.frontier()))
                if s%20==0: print(name,s,'skin',len(retained),'full',len(fullkeys),flush=True)
                if status=='JAM': break
            report.append(dict(case=name,radius=2,initial_retained=len(initial['tiles']),initial_full=len(seed),rows=rows,verified=True))
            film.append(dict(case=name,frames=frames))
        except Exception as exc:
            report.append(dict(case=name,verified=False,error=str(exc),rows=rows))
            (OUT/'results.json').write_text(json.dumps(report,indent=2)); raise
        finally:
            if proc.is_alive(): parent.send('STOP')
            proc.join(timeout=10)
            if proc.is_alive(): proc.terminate(); proc.join()
            parent.close()
    (OUT/'results.json').write_text(json.dumps(report,indent=2))
    with (OUT/'observer-frames.pkl').open('wb') as f: pickle.dump(film,f)
    print('All comparisons passed.',flush=True)

if __name__=='__main__': mp.freeze_support(); main()
