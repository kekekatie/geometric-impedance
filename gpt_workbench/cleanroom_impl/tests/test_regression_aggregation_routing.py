import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.aggregation import *
from gpt_workbench.cleanroom_impl.constants import CONFIGS, PERMUTATION_CONFIGS
from gpt_workbench.cleanroom_impl.errors import ConformanceError, LeakageError
from gpt_workbench.cleanroom_impl.gates import *
from gpt_workbench.cleanroom_impl.identity import *
from gpt_workbench.cleanroom_impl.regression import *
from gpt_workbench.cleanroom_impl.routing import *


def labels(nc): return (tuple(range(nc)),tuple(range(6)))


def test_tp_reg_002_wire_006_m9_axis_and_order_refusal():
    x=np.arange(54,dtype=float).reshape(9,6); d=LabelledArray(x,("config","offset"),labels(9))
    expected=float(np.median([np.median(x[:,o]) for o in range(6)])); assert m9(d)==expected
    with pytest.raises(ConformanceError): m9(LabelledArray(x.T,("offset","config"),(tuple(range(6)),tuple(range(9)))))


def test_tp_agg_001_qref_ties():
    assert q_ref(2,np.full(1000,2.))==1
    assert q_ref(3,np.full(1000,2.))==pytest.approx(1/1001)


def test_tp_agg_002_amd_015_capacity_linear_quantile():
    x=np.arange(200,dtype=float); assert capacity_floor(x)==np.quantile(x,.95,method="linear")==pytest.approx(189.05)
    with pytest.raises(ConformanceError): capacity_floor(x[:-1])


def independent_wy(obs,null):
    order=sorted(range(7),key=lambda i:(-obs[i],i)); raw=[]
    for k in range(7):
        exceed=sum(max(row[j] for j in order[k:])>=obs[order[k]] for row in null)
        raw.append((1+exceed)/1001)
    adj=np.maximum.accumulate(raw); out=np.empty(7)
    for k,i in enumerate(order): out[i]=adj[k]
    return np.array(order),out


def test_tp_agg_003_amd_016_westfall_young_independent():
    obs=np.array([3,3,2,1,1,0,-1.]); null=np.linspace(-2,4,7000).reshape(1000,7)
    got=westfall_young(obs,null); order,adjusted=independent_wy(obs,null)
    assert np.array_equal(got["order"],order) and np.allclose(got["adjusted"],adjusted)


def test_tp_amd_023_direct_r2_and_undefined():
    y=np.array([0.,1.,2.]); p=np.array([0.,1.,1.]); assert direct_r2(y,p).value==.5
    assert not direct_r2(np.ones(3),np.ones(3)).defined
    assert not direct_r2(y,np.array([0,np.nan,2])).defined


def test_tp_wire_004_paired_identity():
    p=PatchKey(0,0); rows=tuple(RowId(p,(i,)) for i in range(3)); y=np.arange(3.)
    assert paired_increment(y,y+1,y,rows,rows).value==pytest.approx(1.5)
    with pytest.raises(ConformanceError): paired_increment(y,y,y,rows,rows[::-1])


def test_tp_leak_004_005_amd_020_scaler_rejects_held_out():
    train=PatchKey(0,0); held=PatchKey(0,1); rows=frozenset(RowId(train,(i,)) for i in range(3))
    prov=FitProvenance(frozenset((train,)),rows,1,None,"s")
    scaler=PopulationScaler.fit(np.array([[1,2],[1,4],[1,6]],float),prov)
    out=scaler.transform(np.array([[99,8.]]),(),()); assert out[0,0]==0
    with pytest.raises(LeakageError): scaler.transform(np.array([[1,2.]]),(train,),())


@pytest.mark.parametrize("value,op,passed",[(1.,">",False),(np.nextafter(1,np.inf),">",True),(1.,">=",True),(1.,"<",False),(np.nextafter(1,-np.inf),"<",True)])
def test_tp_gate_001_amd_024_literal_boundaries(value,op,passed):
    assert (threshold_gate("x",value,1.,op).state=="pass") is passed
    with pytest.raises(ConformanceError): threshold_gate("x",np.nan,1.,op)


def make_gates(classical=.95,plain=.8):
    return evaluate_gates(np.inf,[.95]*9,[classical]*9,.001,.8,.1,.2,np.full((9,6),plain),np.full((9,6),.1),.7,.2)


def test_tp_amd_025_g1_all_nine_and_modifier_scope():
    g=make_gates(); assert g["G1_coherent"].state==g["G1_classical"].state=="pass"
    g=make_gates(classical=.89); assert g["G1_classical"].state=="fail" and g["G5"].state=="inconclusive"


def test_tp_wire_005_g4_undefined_no_drop():
    g=make_gates(plain=0); assert g["G4"].state=="undefined"


def test_tp_route_001_002_claim_boundaries_and_g7_isolation():
    g=make_gates(); a=route(g,np.ones(6)*.8,.1,.2); assert a.coherent_claim and a.modifier and a.physical=="compression"
    g2=dict(g); g2["G7"]=Gate("G7","descriptive",999,None,None)
    assert route(g2,np.ones(6)*.8,.1,.2)==a
    with pytest.raises(ConformanceError): validate_claim("This proves literal perpendicular-space physics")
