import subprocess, sys
from pathlib import Path

import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.synthetic_workflow import run_synthetic_suite


@pytest.mark.parametrize("order",["forward","reverse"])
@pytest.mark.parametrize("parallelism",[1,2])
def test_tp_e2e_001_amd_030_full_axes(order,parallelism):
    result=run_synthetic_suite(order,parallelism)
    assert result.population_counts.shape==(9,6) and np.min(result.population_counts)>=400
    assert result.slab_counts.shape==(9,6,4) and np.min(result.slab_counts)>=100
    assert result.launch_counts.shape==(9,6) and np.all(result.launch_counts==200)
    assert result.null_count==1000 and result.capacity_count==200
    assert result.trace_markers==tuple(f"AC-{i:02d}" for i in range(1,26))


@pytest.mark.parametrize("variant",["earned","modifier_withheld","g0_fail","g4_undefined","survives","mixed"])
def test_tp_e2e_002_route_variants(variant):
    result=run_synthetic_suite(variant=variant)
    if variant=="earned": assert result.route.coherent_claim and result.route.modifier
    if variant=="modifier_withheld": assert result.route.coherent_claim and not result.route.modifier
    if variant in ("g0_fail","g4_undefined","mixed"): assert not result.route.coherent_claim
    if variant=="survives": assert result.route.physical=="survives frozen stress controls"
    if variant=="mixed": assert result.route.physical=="mixed/undetectable"


def test_tp_rng_001_fresh_process_replay():
    root=Path(__file__).parents[3]
    code=("from gpt_workbench.cleanroom_impl.seed_registry import address_rng;"
          "print(address_rng('golden','large',22,5,((0,1),(3,-1)),999).random(4).tobytes().hex())")
    env={**__import__('os').environ,"PYTHONPATH":str(root)}
    a=subprocess.check_output([sys.executable,"-c",code],env=env,text=True).strip()
    b=subprocess.check_output([sys.executable,"-c",code],env=env,text=True).strip()
    assert a==b


def test_no_study_launcher_or_loader_exists():
    package=Path(__file__).parents[1]
    names={p.name for p in package.glob("*.py")}
    assert not names.intersection({"launcher.py","run_study.py","study_loader.py"})
