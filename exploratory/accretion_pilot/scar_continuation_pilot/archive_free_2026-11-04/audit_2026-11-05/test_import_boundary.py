"""Bounded w7 restart control: unrelated import summary blanked, history APIs denied.

Imports still use exact frozen source. This is a disclosed negative-access control,
separate from the unmodified scientific reproduction, not a filesystem sandbox.
"""
import sys,os,json,multiprocessing as mp,io,builtins
from pathlib import Path

def child(conn,state):
    old_open=io.open;old_builtin=builtins.open;intercepted=[]
    def opened(file,*args,**kw):
        path=str(file).replace('\\','/')
        if path.endswith('corner-response-catalogue/results/summary.json'):
            intercepted.append(path)
            return io.StringIO('{"stiffness":{}}')
        return old_open(file,*args,**kw)
    io.open=opened;builtins.open=opened
    import observe as O
    io.open=old_open;builtins.open=old_builtin
    def denied(*a,**k):raise AssertionError('Historical replay/cache API accessed by constructor')
    class Forbidden(dict):
        __getitem__=get=__iter__=__contains__=__len__=keys=values=items=denied
    modules=[]
    for name,m in list(sys.modules.items()):
        for field in ('STIFF','_STIFF'):
            if hasattr(m,field):
                setattr(m,field,Forbidden());modules.append(name+'.'+field)
    assert modules, 'The historical summary consumer must be instrumented'
    O.AF.RD.load_forks=denied;O.AF.PC.grow=denied;O.AF.jam_prep=denied
    (O.CACHE/'import_control_details.json').write_text(json.dumps(dict(summary_reads_replaced=intercepted,forbidden_stiffness_modules=modules),indent=2))
    O.IW._worker_proc(conn,state)

def main():
    import observe as O
    rec,state=O.load('verify-7-0.pkl')
    ctx=mp.get_context('spawn');parent,endpoint=ctx.Pipe()
    p=ctx.Process(target=child,args=(endpoint,state));p.start();endpoint.close()
    out=[]
    try:
        r=parent.recv();assert r['kind']=='ready',r;out.append(r)
        for _ in range(44-rec['jam_step']+1):
            parent.send('STEP');r=parent.recv();assert r['kind']=='step',r;out.append(r)
    finally:
        if p.is_alive():parent.send('STOP')
        p.join(30)
        if p.is_alive():p.terminate();p.join();raise AssertionError('worker did not exit')
    expected=O.load('spawn-messages-7-0.pkl')
    assert out==expected
    details=json.loads((O.CACHE/'import_control_details.json').read_text())
    details.update(all_original_worker_messages_exact=True,steps=len(out)-1,
                   scope='w7-B-s0 pre-scar restart only; original worker target, summary replaced only at import and lookup subsequently forbidden; no historical replay/fork API calls permitted')
    (O.CACHE/'import_boundary_control.json').write_text(json.dumps(details,indent=2))
    print(json.dumps(details),flush=True)
if __name__=='__main__':main()
