import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.constants import BOUNDARY_TIMES, FIT_TIMES
from gpt_workbench.cleanroom_impl.endpoint import *
from gpt_workbench.cleanroom_impl.errors import ConformanceError
from gpt_workbench.cleanroom_impl.propagation import *


@pytest.fixture
def irregular():
    return np.array([[0,1,1,0],[1,0,1,1],[1,1,0,0],[0,1,0,0]],float)


def test_tp_dyn_001_generators(irregular):
    h=coherent_hamiltonian(irregular); q=classical_generator(irregular)
    assert np.array_equal(h.H.toarray(),irregular)
    Q=q.Q.toarray(); assert np.allclose(Q.sum(axis=0),0) and np.all(np.diag(Q)==-1)
    degree=irregular.sum(axis=0); stationary=degree/degree.sum()
    assert np.allclose(Q@stationary,0)


def test_tp_dyn_002_independent_exact_propagation(irregular):
    h=coherent_hamiltonian(irregular); q=classical_generator(irregular); initial=np.eye(4)[:,0]
    for t in (0,.25,1.5):
        assert np.max(np.abs(coherent_slice(h,initial,t)-exact_coherent_reference(irregular,initial,t)))<=1e-10
        assert np.max(np.abs(classical_slice(q,initial,t)-exact_classical_reference(q.Q.toarray(),initial,t)))<=1e-12


def test_tp_dyn_operator_mutants_fail(irregular):
    h=coherent_hamiltonian(irregular); q=classical_generator(irregular); initial=np.eye(4)[:,0]; t=.7
    correct=coherent_slice(h,initial,t)
    assert not np.allclose(correct,expm_multiply(t*h.H,initial)) # omitted -i
    assert not np.allclose(correct,expm_multiply(-t*h.H,initial)) # -H mutant
    with pytest.raises(TypeError): coherent_slice(q,initial,t)
    with pytest.raises(TypeError): classical_slice(h,initial,t)


@pytest.mark.parametrize("batch",[1,3,7])
def test_tp_dyn_004_stream_reduced_batch_reference(irregular,batch):
    par=np.array([[0,0],[1,0],[0,1],[2,0]],float); strip=np.array([1,0,0,1],bool)
    times=(0.,.2,.8); launches=(0,1,2,3)
    out=stream_reduce(coherent_hamiltonian(irregular),launches,times,par,strip,batch)
    expected=np.empty_like(out.msd)
    for j,o in enumerate(launches):
        for k,t in enumerate(times):
            p=np.abs(exact_coherent_reference(irregular,np.eye(4)[:,o],t))**2
            expected[j,k]=p@np.sum((par-par[o])**2,axis=1)
    assert np.allclose(out.msd,expected,atol=1e-12)


def test_tp_dyn_005_beta_hand_reference():
    t=np.array(FIT_TIMES); expected=np.array([.3,.8,1.2]); msd=np.array([2*t**(2*b) for b in expected])
    result=beta_fit(msd); assert result.valid and result.beta==pytest.approx(expected) and np.allclose(result.r2_fit,1)
    for bad in (0,-1,np.nan,np.inf):
        x=msd.copy(); x[0,7]=bad; result=beta_fit(x); assert not result.valid and result.beta is None


def test_tp_dyn_006_boundary_equality_and_eight():
    x=np.zeros((2,161)); assert boundary_crossing(x)==np.inf
    x[0,-1]=.01; assert boundary_crossing(x)==8
    x[1,159]=.01; assert boundary_crossing(x)==7.95


def test_tp_amd_012_smd_floor():
    assert admission_smd(np.ones(3),np.ones(4))==0
    assert admission_smd(np.ones(3)*2,np.ones(4))==np.inf
    assert admission_smd(np.array([0.,2.]),np.array([0.,0.]))==pytest.approx(1/np.sqrt(.5))


def test_tp_neg_003_generator_rejects_wrong_normalization(irregular):
    with pytest.raises(ConformanceError): coherent_hamiltonian(irregular+np.eye(4))
    with pytest.raises(ConformanceError): classical_generator(np.zeros((3,3)))
