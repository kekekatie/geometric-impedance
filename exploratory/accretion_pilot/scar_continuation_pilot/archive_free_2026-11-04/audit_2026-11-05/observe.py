"""Read-only observations around the pinned scheduler and prune; no decision changes."""
import sys, os, pickle, json, random, hashlib
from pathlib import Path
REPO = Path(os.environ['AF_REPRO']).resolve()
EXP = REPO/'exploratory/accretion_pilot/scar_continuation_pilot/archive_free_2026-11-04'
sys.path.insert(0, str(EXP/'src'))
sys.path.insert(0, str(EXP/'supplement_2026-11-04'))
import af_common as AF
import isolated_worker as IW
import scar_continuation as SCN
import verify_supplement as VS
CACHE = Path(os.environ['AF_CACHE']).resolve()
CACHE.mkdir(parents=True, exist_ok=True)

def save(name, x):
    (CACHE/name).write_bytes(pickle.dumps(x, protocol=5))
def load(name):
    return pickle.loads((CACHE/name).read_bytes())
def digest(x):
    return hashlib.sha256(pickle.dumps(x, protocol=5)).hexdigest()

def signature(row):
    def h(x):return hashlib.sha256(repr(x).encode()).hexdigest()
    def scars(x):return sorted(tuple(sorted(e)) for e in x)
    return dict(candidate_enumeration=h([(e,[AF.dk(t) for t in ts]) for e,ts in row['candidates']]),
                legal_checks=h(row['legal_checks']), placements=h([AF.dk(t) for t in row['added']]),
                frontier_before=h([AF.frontier_id(e) for e in row['frontier_before']]),
                frontier_after=h([AF.frontier_id(e) for e in row['frontier_after']]),
                rng_before=h(row['rng_before']),rng_after=h(row['rng_after']),
                scars_before=h(scars(row['scars_before'])),scars_after=h(scars(row['scars_after'])),
                outcome=[row['result'][0],row['result'][1],row['result'][2]],n_added=len(row['added']))

class Observer:
    def __init__(self):
        self.calls=[]; self.prunes=[]
        self.patient=SCN.patient_scar; self.prune=AF.E.ActiveSkin.prune
    def install(self):
        obs=self
        def patient(P, rng, scars, *args, **kw):
            row=dict(skin=isinstance(P, AF.E.ActiveSkin), pre=list(P.tris), rng_before=rng.getstate(), scars_before=set(scars),
                     frontier_before=list(P.frontier()), candidates=[], legal_checks=[], added=[])
            old_candidates=AF.D.candidates; old_legal=P.legal; old_add=P.add
            def candidates(Q,*e):
                cs=old_candidates(Q,*e)
                if Q is P: row['candidates'].append((AF.frontier_id(e),list(cs)))
                return cs
            def legal(t):
                v=old_legal(t); row['legal_checks'].append((AF.dk(t),v)); return v
            def add(t):
                row['added'].append(t); return old_add(t)
            AF.D.candidates=candidates; P.legal=legal; P.add=add
            try: result=obs.patient(P,rng,scars,*args,**kw)
            finally:
                AF.D.candidates=old_candidates; del P.legal; del P.add
            row.update(result=result,post=list(P.tris),rng_after=rng.getstate(),scars_after=set(scars),frontier_after=list(P.frontier()))
            obs.calls.append(row)
            return result
        def prune(P):
            result=obs.prune(P)
            fresh=AF.L.Patch(list(P.tris)); keys={AF.dk(t) for t in P.tris}
            # The instance dict has precisely the frozen state fields. Temporary observer
            # methods are removed before prune; retained V/edges equal fresh retained indexes.
            row=dict(n=len(P.tris),dropped=result, additions=len(P.additions), fields=sorted(vars(P)),
                     edges_match=P.edges==fresh.edges, vertices_match=P.V==fresh.V,
                     owners_retained=all(o is None or AF.dk(o) in keys for p,q,r,o in P.boundary.values()),
                     boundary_vertices_retained=all(AF.L.key(z) in fresh.V for e in P.boundary.values() for z in e[:3]))
            obs.prunes.append(row)
            self.final_state=IW.serialize_state(P, random.Random(0), set())
            return result
        SCN.patient_scar=patient; AF.E.ActiveSkin.prune=prune
    def restore(self):
        SCN.patient_scar=self.patient; AF.E.ActiveSkin.prune=self.prune

ORIGINAL_JAM=AF.jam_prep
def cached_jam(w,si):
    name=f'jam-{w}-{si}.pkl'
    if (CACHE/name).exists():return load(name)
    v=ORIGINAL_JAM(w,si);save(name,v);return v
AF.jam_prep=cached_jam

ORIGINAL_VERIFY=VS.verify_case
def cached_verify(w,si):
    name=f'verify-{w}-{si}.pkl'
    if (CACHE/name).exists(): return load(name)
    obs=Observer();obs.install()
    try: result=ORIGINAL_VERIFY(w,si)
    finally: obs.restore()
    save(f'trace-{w}-{si}.pkl',dict(calls=obs.calls,prunes=obs.prunes,final_state=obs.final_state))
    save(name,result)
    return result

def reproduce():
    print('Setup: w7-B-s0',flush=True)
    r,_=cached_verify(7,0)
    print(json.dumps(r),flush=True)
    VS.verify_case=cached_verify
    VS.main()

if __name__=='__main__': reproduce()
