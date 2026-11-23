"""Frozen A/B labels, exact archive coordinates, and immutable input provenance."""
import hashlib,json,sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ROLE=ROOT.parent/'role_reversal_omission_2026-11-22'
sys.path.insert(0,str(ROLE))
import run_role_reversal as E
BASE='6236920f087a223ca3c0d701640afbe2a89ce5e7'
OLD='1922a7b7ff7e30f0ead0781ac6aaf3b924038783'
CONFIG=[('AB_1',14,'Z3','hallway','Z6','corner ear'),('AB_bal',14,'Z3','middle yard','Z6','middle yard'),
        ('Penrose_1',14,'Z7','middle yard','Z1','middle yard'),('Penrose_2',4,'Z1','middle yard','Z4','middle yard'),
        ('Penrose_ear',13,'Z7','hallway','Z6','corner ear')]
def patch_path(name):
    return (ROLE/'results' if name in ('AB_bal','Penrose_ear') else ROOT.parent/'aperiodic_predict_2026-11-20/results')/(name+'.json')
def prepare():
    sites=[]
    for name,edge,A,arole,B,brole in CONFIG:
        code=E.CorrectedPatchCode(patch_path(name));d=code.json;e=next(e for e in d['eligible'] if e['edge']==edge)
        nx,nz=len(d['HX']),len(d['HZ']);idx=lambda c:E.check_index(c,nx,nz)
        endpoints=[c for c in e['checks'] if c.startswith('X')]
        assert set(e['checks'])==set(endpoints+[A,B]) and len(endpoints)==2
        mapping={'AB':endpoints+[A,B],'A':endpoints+[A],'B':endpoints+[B],'0':endpoints}
        arms={k:dict(checks=v,indices=sorted(map(idx,v)),coordinates=[[c,t] for c in v for t in (1,2)]) for k,v in mapping.items()}
        assert arms['AB']['indices']==code.STAR[e['qubit']]
        assert all({tuple(x) for x in a['coordinates']}<={tuple(x) for x in e['query']} for a in arms.values())
        old=name not in ('AB_bal','Penrose_ear')
        sites.append(dict(name=name,edge=edge,qubit=e['qubit'],A=A,A_role=arole,B=B,B_role=brole,endpoints=endpoints,
            nx=nx,nz=nz,arms=arms,scored_logical_Z=d['logical_Z'],patch_lf_sha256=hashlib.sha256(patch_path(name).read_text().encode()).hexdigest(),
            baseline_mode='sealed per-configuration reuse plus deterministic replay' if old else 'full baseline replay',
            baseline_commit=OLD if old else BASE))
    result=dict(starting_sha=BASE,sites=sites,p=.001,caps=[3,3],histories_per_site=385648,
        directional_prediction=None,interaction='G_A + G_B - G_AB - G_0',
        interpretation='Positive interaction: losing either face costs more when its partner is absent, on decoder truth credit only.')
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/arms.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':print(json.dumps(prepare(),indent=2))
