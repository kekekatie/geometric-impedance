"""Focused controls for dormant-edge guards, deletion and serialization."""
import sys,copy,random,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import common as C
from common import IW,AF,L,D,SCN
from worker import LiveSkin

def main():
    _,state=C.old('verify-7-0.pkl');P=IW.rebuild_skin(copy.deepcopy(state));P.__class__=LiveSkin
    original=C.front(P);all_edges={AF.edge_id(*e[:2]) for e in P.frontier()}
    # All edges dormant: no centres, no retained tile/edge/vertex archive, but the
    # declared edge guards survive and the scheduler must arrest without reattempts.
    P.thin(all_edges)
    assert not P.tris and not P.edges and not P.V and not P.additions
    assert C.front(P)==original and all(o is None for p,q,r,o in P.boundary.values())
    q=IW.rebuild_skin(IW.serialize_state(P,random.Random(7),all_edges));q.__class__=LiveSkin
    original_candidates=D.candidates
    def forbidden(*args):raise AssertionError('pinned edge queried by scheduler')
    D.candidates=forbidden
    try:result=SCN.patient_scar(q,random.Random(7),set(all_edges))
    finally:D.candidates=original_candidates
    assert result[0]=='total_arrest' and result[1]==0 and not q.tris
    # The real pre-scar band contains cavity edges. Cold restore must not promote
    # them to true frontier, even though legal() uses its local retained index.
    p=IW.rebuild_skin(state)
    local=set(C.front(L.Patch(p.tris)));declared=set(C.front(p))
    assert local-declared and declared<=local
    assert all(v is None for v in [o for p,q,r,o in P.boundary.values()])
    C.dump(C.RESULTS/'policy_tests.json',dict(all_dormant_deletes_all_tiles=True,pinned_edges_never_queried=True,
           cold_restore_preserves_true_frontier=True,cavity_edges_not_promoted=len(local-declared),all_passed=True))
    print('Policy controls passed.',flush=True)
if __name__=='__main__':main()
