import hashlib, json, subprocess
from pathlib import Path

import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.errors import ConformanceError
from gpt_workbench.cleanroom_impl.identity import *
from gpt_workbench.cleanroom_impl.parity import fit_parity_scaler, parity_block
from gpt_workbench.cleanroom_impl.residual_null import cross_fitted_residuals


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def test_tp_reg_004_normative_bytes_exact():
    package=Path(__file__).parents[1]; root=package.parents[1]
    frozen=json.loads((package/"normative_hashes.json").read_text())["git_blobs"]
    for relative,expected in frozen.items():
        actual=subprocess.check_output(
            ["git","-C",str(root),"rev-parse",f"HEAD:{relative}"], text=True).strip()
        assert actual==expected, relative


def test_tp_leak_001_002_003_amd_022_residual_topology():
    rng=np.random.Generator(np.random.PCG64(7)); n=40
    X=rng.normal(size=(n,3)); address=np.column_stack([X[:,0]*(j+1)+rng.normal(scale=.01,size=n) for j in range(11)])
    p=PatchKey(0,0); hp=PatchKey(0,1); rows=tuple(RowId(p,(i,)) for i in range(n)); held=tuple(RowId(hp,(i,)) for i in range(8))
    out=cross_fitted_residuals(X,address,np.arange(n)%4,rows,X[:8],address[:8],held,1,"schema")
    assert out.training_residuals.shape==(n,11) and out.held_out_residuals.shape==(8,11) and out.model_count==55


def test_tp_leak_004_parity_floor_and_training_only(grid_patch):
    n=len(grid_patch.lifts); raw=np.column_stack((np.arange(n),np.arange(n)**2)).astype(float)
    p=PatchKey(0,0); prov=FitProvenance(frozenset((p,)),frozenset(),1,None,"p")
    scaler=fit_parity_scaler(raw,np.array([[1,1],[2,2.]]),prov)
    result=parity_block(grid_patch,raw[:,0],raw[:,1],scaler)
    assert result.available and result.address11.shape==(n,11)
    with pytest.raises(ConformanceError): fit_parity_scaler(raw,np.array([[1,0.5e-9]]),prov)
