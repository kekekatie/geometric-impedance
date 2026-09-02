import subprocess, sys
from pathlib import Path

import pytest

from gpt_workbench.cleanroom_impl.synthetic_workflow import run_synthetic_suite


@pytest.fixture(scope="module")
def four_modes():
    return {(order,workers):run_synthetic_suite(order,workers)
            for order in ("forward","reverse") for workers in (1,2)}


def test_tp_e2e_001_amd_030_real_orchestrator_counts(four_modes):
    for result in four_modes.values():
        assert result.g0_passed and result.null_count==1000 and result.capacity_count==200
        expected={"geometry":54,"features":54,"propagate_coherent":54,
                  "propagate_classical":54,"regress":108,
                  "local_null":42000,"capacity":10800,"beta":108}
        assert {k:result.counters[k] for k in expected}==expected
        assert set(result.gates)=={"G0","G1_coherent","G1_classical","G2","G3","G4","G5","G6","G7","G8"}


def test_tp_e2e_four_mode_keyed_equivalence_and_real_traversal(four_modes):
    assert len({r.keyed_digest for r in four_modes.values()})==1
    forward=four_modes[("forward",1)].schedule_trace
    reverse=four_modes[("reverse",1)].schedule_trace
    assert forward==tuple(reversed(reverse)) and forward!=reverse
    assert four_modes[("forward",1)].counters["worker_thread_count"]==1
    assert four_modes[("forward",2)].counters["worker_thread_count"]==2


def test_tp_wire_008_neg_007_g0_exact_eight_is_hard_barrier():
    result=run_synthetic_suite(variant="g0_at_8")
    assert not result.g0_passed and result.t_bound==8.0 and result.route.wording=="finite-size-limited"
    assert result.counters["beta"]==0
    assert result.counters.get("regress",0)==0
    assert result.counters.get("local_null",0)==0
    assert result.counters.get("capacity",0)==0
    assert result.null_count==result.capacity_count==0 and set(result.gates)=={"G0"}


def test_tp_e2e_002_modifier_withheld_runs_full_chain():
    result=run_synthetic_suite(variant="modifier_withheld")
    assert result.g0_passed and result.route.coherent_claim and not result.route.modifier


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
