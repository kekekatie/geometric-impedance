"""One-way snapshot export. Tracker runs only after all growth workers exit."""
import multiprocessing as mp,pickle,json
from pathlib import Path
import skin_restart as R
import active_skin_engine as E
H=Path(__file__).resolve().parent; O=H/'endurance'
def producer(conn,blob):
    try:
        c=pickle.loads(blob); P,rng=R.restore(c); swap=c['swap29']; del c,blob
        conn.send(dict(slice=60,skin=list(P.tris),frontier=P.frontier(),added=[],status='initial',mode=None))
        for s in range(61,121):
            P.additions=[]; status,n,mode=E.step(P,rng,s,swap); added=P.additions; P.additions=[]; P.prune()
            conn.send(dict(slice=s,skin=list(P.tris),frontier=P.frontier(),added=added,status=status,mode=mode))
            if status=='JAM': break
        conn.send(None)
    except Exception:
        import traceback
        conn.send({'error':traceback.format_exc()})
    finally: conn.close()
def main():
    O.mkdir(exist_ok=True); prior=json.loads((H/'active-skin/results.json').read_text()); runs=[]
    for case in ['continuation-1','continuation-3','alternative-29']:
        a,b=mp.get_context('spawn').Pipe(duplex=False); blob=(H/'skin-restart'/f'{case}-skin-only.pkl').read_bytes()
        p=mp.get_context('spawn').Process(target=producer,args=(b,blob)); p.start(); b.close(); frames=[]
        old=next(r for r in prior if r['case']==case)
        while True:
            if not a.poll(10): print(case,'exporting...',flush=True); continue
            fr=a.recv()
            if fr is None: break
            assert 'error' not in fr,fr.get('error')
            if fr['slice']>60:
                row=old['rows'][fr['slice']-1]
                assert (fr['status'],fr['mode'],len(fr['added']),len(fr['skin']))==(row['status'],row['mode'],row['placed'],row['retained'])
            frames.append(fr)
        p.join(10); assert p.exitcode==0; a.close()
        runs.append(dict(case=case,frames=frames)); print(case,'saved',len(frames),'snapshots',flush=True)
    with (O/'skin-snapshots.pkl').open('wb') as f: pickle.dump(runs,f)
    print('All growth processes exited. Observer may now analyse.',flush=True)
if __name__=='__main__': mp.freeze_support(); main()
