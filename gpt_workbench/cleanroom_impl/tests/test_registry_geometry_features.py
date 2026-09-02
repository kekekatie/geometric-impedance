import json
import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.constants import *
from gpt_workbench.cleanroom_impl.errors import ConformanceError, GeometryPreflightFailure
from gpt_workbench.cleanroom_impl.features import *
from gpt_workbench.cleanroom_impl.folds import launch_positions, pca_slabs, select_launches
from gpt_workbench.cleanroom_impl.geometry import *
from gpt_workbench.cleanroom_impl.identity import PatchKey
from gpt_workbench.cleanroom_impl.preflight import *


def test_tp_reg_001_exact_registries():
    assert RADII==(2,4,8,12,16) and len(OFFSETS)==6
    assert [c.label for c in CONFIGS]==["silver-e14","golden-e18","platinum-e16","silver-e16","golden-e20","platinum-e18","silver-e18","golden-e22","platinum-e20"]
    assert [c.label for c in PERMUTATION_CONFIGS]==["silver-e14","golden-e18","silver-e16","golden-e20","silver-e18","golden-e22","platinum-e20"]
    assert [c.label for c in CAPACITY_CONFIGS]==["silver-e14","silver-e16","silver-e18","golden-e18","golden-e20","golden-e22","platinum-e16","platinum-e18","platinum-e20"]


def test_tp_reg_003_companion_times():
    assert len(FIT_TIMES)==48 and len(set(FIT_TIMES))==48 and FIT_TIMES[0]==2 and FIT_TIMES[-1]==8
    assert set(FIT_TIMES)<=set(BOUNDARY_TIMES)


def test_tp_geo_001_hull_depth_analytic_and_invariance():
    p=np.array([[0,0],[1,0],[1,1],[0,1],[.5,.5]])
    d=hull_depth(p); assert d[-1]==pytest.approx(.5)
    assert hull_depth(p+7)[-1]==pytest.approx(.5)
    with pytest.raises(GeometryPreflightFailure): hull_depth(np.array([[0,0],[1,0],[2,0]]))


def test_tp_geo_002_common_exact_boundary(grid_patch):
    object.__setattr__(grid_patch,"d_bound",np.array([16*grid_patch.ell-1e-12,16*grid_patch.ell,16*grid_patch.ell+1e-12]+[0.]*(len(grid_patch.lifts)-3)))
    assert common_indices(grid_patch).tolist()==[1,2]


def test_tp_amd_002_canonical_identity_and_edges():
    lifts=np.array([[1,0],[0,0],[0,1],[1,1]],int); par=lifts.astype(float); perp=par+np.array([.2,.3])
    p=canonicalize_geometry(PatchKey(0,0),lifts,par,perp,[(0,1),(1,2),(2,3),(3,0)])
    assert p.ids==((0,0),(0,1),(1,0),(1,1)) and p.edges==tuple(sorted(p.edges))
    with pytest.raises(ConformanceError): canonicalize_geometry(PatchKey(0,0),np.vstack((lifts,lifts[0])),np.vstack((par,par[0])),np.vstack((perp,perp[0])),[(0,1)])


@pytest.mark.parametrize("sigma,zero",[(.5e-9,True),(1e-9,False),(1.5e-9,False)])
def test_tp_fea_002_amd_028_sigma_floor(sigma,zero):
    x=np.array([-1.,1.])*sigma
    mean,var,skew,kurt=population_moments(x)
    assert mean==0
    assert (var==skew==kurt==0) if zero else var>0


def test_tp_fea_004_address_operator_exact_shape_and_centre(grid_patch):
    out=address_operator(grid_patch,grid_patch.perp)
    assert out.shape==(49,11) and np.isfinite(out).all()
    # Shell-2 first two columns independently enumerate BFS members including source.
    dist=graph_shell_distances(grid_patch.adjacency,0,8); members=sorted(v for v,d in dist.items() if d<=2)
    assert out[0,:2]==pytest.approx(grid_patch.perp[members].mean(axis=0))


def test_tp_amd_003_motif_registry_pool_and_unseen():
    a=((0,1),); b=((1,-1),)
    reg=motif_registry([[b],[a],[],[],[],[]]); assert reg==(a,b)
    assert motif_one_hot([b,a],reg).tolist()==[[0,1],[1,0]]
    with pytest.raises(ConformanceError): motif_one_hot([((9,9),)],reg)


def test_tp_fea_007_amd_004_dedup_strict_pooled_multimatch():
    m3=[np.column_stack((np.arange(3)+i,np.arange(3)+i)) for i in range(6)]
    phys=[np.column_stack((x[:,0]+.5e-12,x[:,0]+1e-12,x[:,0]+2)) for x in m3]
    s=build_dedup_schema(m3,phys)
    assert s.dropped==(0,) and s.matches[0]==(0,1) and s.retained==(1,2)
    assert apply_dedup(s,m3[0],phys[0]).shape[1]==4


def test_tp_amd_005_physical_prefixes(grid_patch):
    n=len(grid_patch.lifts); degree=np.array([len(x) for x in grid_patch.adjacency],float)
    psi=np.linspace(.1,.9,n); area=np.ones(n)
    blocks=physical_features(grid_patch,degree,psi,psi**2,psi**3,area)
    assert [blocks[r][0].shape[1] for r in RADII]==[11,22,35,48,61]
    for a,b in zip(RADII,RADII[1:]):
        assert np.array_equal(blocks[a][0],blocks[b][0][:,:blocks[a][0].shape[1]])
        assert blocks[a][1]==blocks[b][1][:len(blocks[a][1])]


def test_tp_amd_006_pca_tie_and_launch_formula():
    # Four unequal-axis lines, 400 identities, four exact 100-row slabs.
    x=np.column_stack((np.arange(400,dtype=float),np.sin(np.arange(400))*1e-3))
    lifts=tuple((i,0) for i in range(400)); reg=pca_slabs(x,lifts)
    assert np.bincount(reg.slab).tolist()==[100]*4
    launches=select_launches(reg,lifts); assert len(launches)==len(set(launches))==200
    assert launch_positions(100)[[0,-1]].tolist()==[0,99]
    circle=np.array([[1,0],[0,1],[-1,0],[0,-1]],float)
    with pytest.raises(GeometryPreflightFailure): pca_slabs(circle,tuple((i,) for i in range(4)),production=False)


def test_tp_amd_025_exact_correspondence_padding():
    core=np.array([[0,0],[1,0]]); padded=np.array([[2,0],[1,0],[0,0]])
    assert exact_core_to_padded(core,padded).tolist()==[2,1]
    assert validate_padding(1,np.array([3,4]),np.ones(2),np.ones(2),np.ones(2),np.ones(2))["ring_width"]==3
    with pytest.raises(GeometryPreflightFailure): validate_padding(1,np.array([2.999]),np.ones(2),np.ones(2),np.ones(2),np.ones(2))


def test_tp_amd_027_registry_roles_and_membership():
    availability=validate_exact_patch_registry(EXACT_PATCH_REGISTRY)
    assert not any(availability["platinum-e16"]) and not any(availability["platinum-e18"])
    assert report_rounded_expectations({"silver":1})["role"]=="ProvenanceOnly"
    bad=dict(EXACT_PATCH_REGISTRY); bad["silver-e14"]=((667,)+bad["silver-e14"][0][1:],bad["silver-e14"][1])
    with pytest.raises(GeometryPreflightFailure): validate_exact_patch_registry(bad)
