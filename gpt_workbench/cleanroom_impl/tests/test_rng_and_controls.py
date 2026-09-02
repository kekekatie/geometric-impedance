import hashlib, json
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.constants import CAPACITY_PATCH_AXIS
from gpt_workbench.cleanroom_impl.controls import *
from gpt_workbench.cleanroom_impl.errors import ConformanceError
from gpt_workbench.cleanroom_impl.seed_registry import *


def independent_digest(fields,person):
    raw=json.dumps(OrderedDict(fields),ensure_ascii=True,allow_nan=False,separators=(",",":"),sort_keys=False).encode()
    d=hashlib.blake2b(raw,digest_size=8,person=person).digest()
    return raw,d,int.from_bytes(d[:4],"big"),int.from_bytes(d[4:],"big")


def test_tp_amd_007_shuffle_canonical_independent():
    fields=(("family","silver"),("tier","small"),("extent",14),("offset_index",0))
    raw,d,u0,u1=independent_digest(fields,b"GIV-SHUFFLE-v1")
    assert raw==shuffle_key("silver","small",14,0)
    assert (d.hex(),u0,u1)==("ed9ec0e3c61e6fec",3986604259,3323883500)


def test_tp_amd_013_address_canonical_independent():
    fields=(("family","golden"),("tier","large"),("extent",22),("offset_index",5),("motif",[[0,1],[3,-1]]))
    raw,d,u0,u1=independent_digest(fields,b"GIV-ADDRPERM-v1")
    assert raw==address_key("golden","large",22,5,((0,1),(3,-1)))
    assert (d.hex(),u0,u1)==("9d70af0b3b41cf37",2641407755,994168631)
    with pytest.raises(ConformanceError): address_key("golden","large",22,5,((0,1.0),))


@pytest.mark.parametrize("b,expected",[
 (0,[0.8826497560738871,0.38985455656051815]),
 (1,[0.08641531257431889,0.5763533629808645]),
 (999,[0.8346469226889753,0.32584218102241924])])
def test_tp_rng_001_amd_014_address_stream_golden(b,expected):
    rng=address_rng("golden","large",22,5,((0,1),(3,-1)),b)
    assert rng.random(2).tolist()==expected


def test_tp_amd_017_018_capacity_tree_axis():
    c=CapacityRegistry(); assert len(c.axis)==54 and c.axis==CAPACITY_PATCH_AXIS
    assert [c.axis[i][0].family for i in (0,18,36)]==["silver","golden","platinum"]
    hashes={c.field(d,p,3).sha256 for d,p in ((0,0),(0,53),(199,0),(199,53))}
    assert len(hashes)==4


def test_tp_amd_019_capacity_independent_replay_and_reuse():
    c=CapacityRegistry(); one=c.field(0,0,3); two=c.field(0,0,3)
    draw=np.random.SeedSequence(20260830).spawn(200)[0]
    patch=draw.spawn(54)[0]
    direct=np.random.Generator(np.random.PCG64(patch)).standard_normal((3,11),dtype=np.float64)
    assert one is two and one.values.flags.c_contiguous and np.array_equal(one.values,direct)
    assert one.sha256=="9566b3f8f33fa404b42fc71442c287713b43dde44f48b12183ca6ed89592e8c8"


def test_tp_amd_golden_file_matches_production():
    path=Path(__file__).parents[1]/"golden_vectors.json"; frozen=json.loads(path.read_text())
    assert frozen["numpy_version"]==np.__version__
    assert frozen["shuffle"]["digest_hex"]==golden_vectors()["shuffle"]["digest_hex"]
    assert frozen["address"]["uniform_b999"]==golden_vectors()["address_uniform_b"]["999"]


def test_tp_rng_002_roots_separate():
    addr=address_rng("silver","small",14,0,((0,1),),0).random(8)
    cap=CapacityRegistry().field(0,0,1).values.ravel()[:8]
    assert not np.array_equal(addr,cap)


def test_tp_amd_008_shuffle_replay_and_consumption(grid_patch):
    motifs=[((0,1),) if i%2 else ((1,-1),) for i in range(len(grid_patch.lifts))]
    registry=tuple(sorted(set(motifs)))
    a,pa=stratified_shuffle(grid_patch,grid_patch.perp,motifs,registry,"silver","small",14)
    b,pb=stratified_shuffle(grid_patch,grid_patch.perp,motifs,registry,"silver","small",14)
    assert np.array_equal(a,b) and np.array_equal(pa,pb)
    assert sorted(pa.tolist())==list(range(len(pa)))


def test_tp_rng_004_singleton_boundary():
    common=((0,1),)
    motifs=[common]*19+[((9,1),)]
    assert local_null_available(motifs) # exactly 5%
    motifs=[common]*18+[((9,1),),((8,1),)]
    assert not local_null_available(motifs)


def test_tp_rng_003_assignment_distance_plus_u_and_derangement():
    n=5; x=np.arange(n,dtype=float)[:,None]; lifts=tuple((i,) for i in range(n))
    result=local_assignment(x,lifts,"silver","small",14,0,((0,1),),0,candidate_sizes=("full",))
    assert sorted(result.destination_by_source)==list(range(n))
    assert all(i!=j for i,j in enumerate(result.destination_by_source))


def test_tp_amd_014_source_candidate_consumption_reversed_and_concurrent():
    n=6; x=np.array([[0.],[3.],[1.],[5.],[2.],[4.]])
    lifts=((30,),(10,),(60,),(20,),(50,),(40,)); motif=((0,1),)
    def run(values,ids): return local_assignment(values,ids,"silver","small",14,0,motif,7,candidate_sizes=("full",))
    normal=run(x,lifts)
    order=np.arange(n)[::-1]; reversed_result=run(x[order],tuple(lifts[i] for i in order))
    by_lift={lifts[i]:lifts[j] for i,j in enumerate(normal.destination_by_source)}
    reversed_by_lift={lifts[order[i]]:lifts[order[j]] for i,j in enumerate(reversed_result.destination_by_source)}
    assert by_lift==reversed_by_lift
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:run(x,lifts),range(2)))
    assert results[0]==results[1]==normal
    # Independent row-major stream reconstruction for the one full-candidate attempt.
    source_order=sorted(range(n),key=lambda i:lifts[i]); distances=np.abs(x-x.T)
    U=address_rng("silver","small",14,0,motif,7).random((n,n-1),dtype=np.float64)
    cost=np.full((n,n),np.inf)
    for rank,i in enumerate(source_order):
        candidates=sorted((j for j in range(n) if j!=i),key=lambda j:(distances[i,j],lifts[j]))
        cost[i,candidates]=distances[i,candidates]+U[rank]
    rows,cols=__import__('scipy').optimize.linear_sum_assignment(cost)
    mapping=np.empty(n,dtype=int); mapping[rows]=cols
    assert tuple(mapping)==normal.destination_by_source
