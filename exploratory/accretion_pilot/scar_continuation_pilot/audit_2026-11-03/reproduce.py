"""Execute original modules in a disposable checkout; instrument, do not alter decisions."""
import sys,os,json,pickle,functools,hashlib,time,subprocess,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=Path(sys.argv[1]).resolve();CACHE=Path(sys.argv[2]).resolve();CACHE.mkdir(parents=True,exist_ok=True)
SRC=REPO/'exploratory/accretion_pilot/scar_continuation_pilot/src'
sys.path.insert(0,str(SRC))
import scar_common as S
import scar_continuation as G
import arc_tools as A
import phase1_arc_readout as P1
import phase3_post_readout as P3

original_jam=S.jam_state;original_grow=G.scar_grow;original_patient=G.patient_scar;original_baseline=S.PC.grow
active=None;traces={};baselines={};reader_calls=[]
def save(name,value):
    (CACHE/name).write_bytes(pickle.dumps(value,protocol=5))
def baseline(*args,**kw):
    original=S.SN.patient;trace=[]
    def observe(P,rng):
        before=rng.getstate();r=original(P,rng)
        trace.append(dict(rng_before=before,rng_after=rng.getstate(),result=r))
        return r
    S.SN.patient=observe
    try:result=original_baseline(*args,**kw)
    finally:S.SN.patient=original
    result['_audit_rng_trace']=trace
    baselines[args[2]]=result
    return result
S.PC.grow=baseline
def jam(w,si):
    path=CACHE/f'jam-{w}-{si}.pkl'
    if path.exists():return pickle.loads(path.read_bytes())
    value=original_jam(w,si);save(path.name,value)
    save(f'baseline-{w}-{si}.pkl',baselines[value['stream']])
    return value
S.jam_state=jam

def patient(P,rng,scars,verify_legal=True):
    pre=list(P.tris);rng_before=rng.getstate();added=[];original_add=P.add
    def add(t):
        legal=P.legal(t)
        if not legal:raise AssertionError('actual addition violates frozen pre-add legality')
        added.append(t);return original_add(t)
    P.add=add
    try:result=original_patient(P,rng,scars,verify_legal)
    finally:del P.add
    traces[active].append(dict(pre=pre,post=list(P.tris),added=added,scars=set(scars),rng_before=rng_before,rng_after=rng.getstate(),result=result))
    return result
G.patient_scar=patient
def grow(w,si,steps=44,record_illegal=False):
    global active
    path=CACHE/f'growth-{w}-{si}.pkl'
    if path.exists():return pickle.loads(path.read_bytes())
    active=(w,si);traces[active]=[]
    # Extra legal checks are observational: every actual placement independently checked above.
    value=original_grow(w,si,steps=steps,record_illegal=True)
    assert value['illegal_placements']==0
    save(path.name,value);save(f'trace-{w}-{si}.pkl',traces[active]);return value
G.scar_grow=grow

# inverse is deterministic on its exact complex argument. Memoization leaves results unchanged.
S.SR.inverse=functools.lru_cache(maxsize=None)(S.SR.inverse)
original_read=S.SR.read
def read(payload):
    result=original_read(payload)
    reader_calls.append(dict(payload=payload,result=result))
    return result
S.SR.read=read

def figures():
    import importlib.util
    spec=importlib.util.spec_from_file_location('original_scar_figures',SRC/'make_figures.py')
    F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F);F.main()

if '--figures-only' in sys.argv:
    figures();save('reader-figures.pkl',reader_calls);raise SystemExit(0)

if '--growth-only' in sys.argv:
    G.main(cases=S.B_JAMS)
    print('Original growth cache complete.',flush=True)
    raise SystemExit(0)

print('Setup case w7/B/s0',flush=True)
setup1=P1.analyse(7,0,with_witness=True);setup2=grow(7,0);setup3,_=P3.analyse(7,0)
save('setup.pkl',(setup1,setup2,setup3))
print('Setup complete:',setup1['maximal_compatible_connected_arc']['n_tiles'],len(setup2['full']),setup3['maximal_compatible_arc'],flush=True)
save('reader-setup.pkl',reader_calls);reader_calls.clear()
P1.main(cases=S.B_JAMS)
save('reader-phase1.pkl',reader_calls);reader_calls.clear()
G.main(cases=S.B_JAMS)
P3.main(cases=S.B_JAMS)
save('reader-phase3.pkl',reader_calls);reader_calls.clear()
figures()
save('reader-figures.pkl',reader_calls)
print('Original outputs complete; cached original states, exact payloads and per-add legality traces.',flush=True)
