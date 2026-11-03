"""Small scheduler-policy and selection controls; no new growth experiment."""
import random,math
from audit_common import *

def main():
    class Patch:
        def __init__(self):self.tris=[]
        def frontier(self):return [(0j,1+0j,1j,None)]
        def legal(self,t):return True
        def add(self,t):self.tris.append(t)
    t=next(iter(S.L.TEMPL.values()));old=S.D.candidates
    try:
        S.D.candidates=lambda *args:[t]
        p=Patch();scars={S.ekey(0j,1+0j)}
        status,n,kind,new,illegal=G.patient_scar(p,random.Random(3),scars)
        assert status=='total_arrest' and n==0 and not p.tris
        # This is scheduler arrest despite an extendable pinned edge, by policy.
        p=Patch();q=Patch();r1=random.Random(3);r2=random.Random(3)
        a=G.patient_scar(p,r1,set());b=S.SN.patient(q,r2)
        assert a[:3]==b and p.tris==q.tris and r1.getstate()==r2.getstate()
    finally:S.D.candidates=old
    # Geometric overlap component control: crossing strips with no vertex containment requirement.
    p=[-2-.3j,2-.3j,.3j];q=[-.3-2j,-.3+2j,.3+0j]
    assert area(intersection(p,q))>1e-3
    assert area(intersection(p,[z+10 for z in q]))==0
    # Area alone cannot establish emptiness: x>=0, -x>=0, -1<=y<=1.
    payload={'windows':[{'normals':[[1,0],[-1,0],[0,1],[0,-1]],'h':1}]}
    raw={'status':'reconstructed','constraints':[[0,0,0],[0,1,0],[0,2,-1],[0,3,-1]]}
    m=margin(raw,payload);assert m['status']==0 and abs(m['margin'])<1e-12
    dump('regression_tests.json',dict(permanent_pin_can_cause_scheduler_arrest=True,no_scar_forced_step_matches_baseline=True,crossing_overlap_detected=True,disjoint_overlap_rejected=True,zero_area_segment_not_infeasible=True))
    print('PASS scheduler pin semantics, baseline forced-step control, overlap controls, zero-area feasible segment',flush=True)

if __name__=='__main__':main()
