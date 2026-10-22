"""Cold restart at 60 from worker-produced skin state; no archived geometry supplied."""
from pathlib import Path
import pickle,json,random,multiprocessing as mp,hashlib
import active_skin_engine as E
import figures as F
H=Path(__file__).resolve().parent; O=H/'skin-restart'

def checkpoint(P,rng,s,swap):
    return dict(version=1,tiles=list(P.tris),boundary=list(P.boundary.values()),radius=P.radius,rng=rng.getstate(),slice=s,swap29=swap)

def restore(c):
    assert set(c)=={'version','tiles','boundary','radius','rng','slice','swap29'} and c['version']==1
    P=E.ActiveSkin.__new__(E.ActiveSkin)
    index=F.L.Patch(c['tiles']); P.tris,P.edges,P.V=index.tris,index.edges,index.V
    P.boundary={E.edge_id(e[0],e[1]):e for e in c['boundary']}
    assert {E.tile_id(e[3]) for e in c['boundary']}<={E.tile_id(t) for t in P.tris}
    P.radius=c['radius']; P.additions=[]
    rng=random.Random(); rng.setstate(c['rng'])
    return P,rng

def make_checkpoint(conn,seed,stream,swap):
    try:
        P=E.ActiveSkin(seed,2); seed.clear(); del seed
        rng=random.Random(stream)
        for s in range(1,61):
            P.additions=[]; status,_,_=E.step(P,rng,s,swap); assert status=='ok'
            P.additions=[]; P.prune()
        conn.send(dict(kind='checkpoint',payload=checkpoint(P,rng,60,swap)))
    except Exception:
        import traceback
        conn.send(dict(kind='error',traceback=traceback.format_exc()))
    finally: conn.close()

def resumed_worker(conn,blob):
    try:
        c=pickle.loads(blob); P,rng=restore(c); s=c['slice']; swap=c['swap29']; del c,blob
        conn.send(dict(kind='ready',pid=__import__('os').getpid(),frontier=[E.frontier_id(e) for e in P.frontier()]))
        while True:
            cmd=conn.recv()
            if cmd=='STOP': break
            assert cmd=='STEP'; s+=1; inv=E.inventory(P); P.additions=[]
            status,n,mode=E.step(P,rng,s,swap); added=P.additions; P.additions=[]; P.prune()
            conn.send(dict(kind='step',slice=s,before=inv,status=status,n=n,mode=mode,added=added,frontier=[E.frontier_id(e) for e in P.frontier()],skin=[E.tile_id(t) for t in P.tris],rng=rng.getstate()))
    except Exception:
        import traceback
        conn.send(dict(kind='error',traceback=traceback.format_exc()))
    finally: conn.close()

def recv(conn):
    # Parent logging remains responsive; no geometry sent back to either worker.
    while not conn.poll(10): print('Waiting for worker...',flush=True)
    x=conn.recv()
    if x['kind']=='error': raise RuntimeError(x['traceback'])
    return x

def main():
    O.mkdir(exist_ok=True)
    _,e=pickle.loads((H/'results/geometry.pkl').read_bytes())
    previous=json.loads((H/'active-skin/results.json').read_text())
    observations=pickle.loads((H/'active-skin/observer-frames.pkl').read_bytes())
    inventories=json.loads((H/'choice-tracking/inventory.json').read_text())
    ctx=mp.get_context('spawn'); reports=[]
    for case,idx,swap in [('continuation-1',0,False),('continuation-3',2,False),('alternative-29',0,True)]:
        print('Creating worker checkpoint:',case,flush=True)
        a,b=ctx.Pipe(); first=ctx.Process(target=make_checkpoint,args=(b,e['base']+[e['cs'][1]],e['streams'][idx],swap)); first.start(); b.close()
        c=recv(a)['payload']; first.join(10); assert not first.is_alive() and first.exitcode==0; a.close()
        blob=pickle.dumps(c); (O/(case+'-skin-only.pkl')).write_bytes(blob)
        # Independent archived observation is available only to the controller.
        fr=next(f for r in observations if r['case']==case for f in r['frames'] if f['slice']==60)
        assert [E.tile_id(t) for t in c['tiles']]==[E.tile_id(t) for t in fr['skin']]
        assert [E.frontier_id(ed) for ed in sorted(c['boundary'],key=lambda ed:(abs((ed[0]+ed[1])/2),F.L.key((ed[0]+ed[1])/2)))]==[E.frontier_id(ed) for ed in fr['frontier']]
        ref_rng=random.Random(e['streams'][idx]); old=next(r for r in previous if r['case']==case)
        for row in old['rows'][:60]:
            if row['mode']=='guess':
                if swap: count=2
                else: count=next(r for r in inventories if r['continuation']==idx+1)['records'][row['slice']-1]['selected']['count']
                ref_rng.choice(range(count))
        assert ref_rng.getstate()==c['rng']
        Q=F.L.Patch(fr['archive']); a,b=ctx.Pipe(); second=ctx.Process(target=resumed_worker,args=(b,blob)); second.start(); b.close(); ready=recv(a)
        assert ready['frontier']==[E.frontier_id(ed) for ed in Q.frontier()]
        rows=[]
        try:
            for s in range(61,121):
                a.send('STEP'); inv=E.inventory(Q); n0=len(Q.tris); status,n,mode=E.step(Q,ref_rng,s,swap); msg=recv(a)
                assert msg['before']==inv and msg['slice']==s
                assert (status,n,mode)==(msg['status'],msg['n'],msg['mode'])
                assert [E.tile_id(t) for t in Q.tris[n0:]]==[E.tile_id(t) for t in msg['added']]
                assert msg['frontier']==[E.frontier_id(ed) for ed in Q.frontier()]
                assert msg['rng']==ref_rng.getstate()
                recorded=old['rows'][s-1]
                assert (status,n,mode,len(msg['skin']))==(recorded['status'],recorded['placed'],recorded['mode'],recorded['retained'])
                rows.append(dict(slice=s,status=status,edge_queries=len(inv),placed=n,retained=len(msg['skin'])))
                if status=='JAM': break
        finally:
            if second.is_alive(): a.send('STOP')
            second.join(10)
            if second.is_alive(): second.terminate(); second.join()
            a.close()
        reports.append(dict(case=case,checkpoint_slice=60,checkpoint_tiles=len(c['tiles']),archive_tiles=len(fr['archive']),checkpoint_bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),original_process_exited=True,first_pid=first.pid,restarted_pid=second.pid,verified=True,rows=rows))
        (O/'results.json').write_text(json.dumps(reports,indent=2)); print(case,'passed through',rows[-1]['slice'],rows[-1]['status'],flush=True)
    print('All restart checks passed.',flush=True)

if __name__=='__main__': mp.freeze_support(); main()
