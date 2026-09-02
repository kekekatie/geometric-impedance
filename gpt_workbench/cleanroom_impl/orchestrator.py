"""Study-blind production workflow orchestration with injected data/component providers."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Protocol

import numpy as np

from .aggregation import (CAPACITY_DRAW_LABELS, GENERAL_LABELS, NULL_DRAW_LABELS,
                          OFFSET_LABELS, PERMUTATION_LABELS, LabelledArray,
                          capacity_floor, capacity_m9, m9, mperm7, q_ref)
from .constants import CONFIGS, OFFSETS, PERMUTATION_CONFIGS
from .endpoint import BetaEndpoint, beta_fit, boundary_crossing
from .errors import ConformanceError, GeometryPreflightFailure
from .folds import pca_slabs, select_launches
from .gates import Gate, evaluate_gates
from .identity import LiftId, PatchKey
from .routing import Route, route


@dataclass(frozen=True)
class GeometryStage:
    key: PatchKey
    lifts: tuple[LiftId, ...]
    par: np.ndarray
    common: np.ndarray


@dataclass(frozen=True)
class FeatureStage:
    physical: np.ndarray
    address: np.ndarray
    parity: np.ndarray
    position: np.ndarray
    far: np.ndarray


@dataclass(frozen=True)
class PropagationStage:
    msd_fit: np.ndarray
    strip_mass: np.ndarray


@dataclass(frozen=True)
class RegressionStage:
    plain: float
    shuffled: float
    address: float
    parity: float
    residual: float
    position_reported: bool
    far_reported: bool


class WorkflowBackend(Protocol):
    def geometry(self, config, offset_index: int) -> GeometryStage: ...
    def features(self, geometry: GeometryStage) -> FeatureStage: ...
    def propagate(self, engine: str, geometry: GeometryStage,
                  launch_indices: tuple[int, ...]) -> PropagationStage: ...
    def regress(self, engine: str, geometry: GeometryStage, features: FeatureStage,
                endpoint: BetaEndpoint) -> RegressionStage: ...
    def local_null(self, config, offset_index: int, repetition: int) -> float: ...
    def capacity(self, draw: int, config, offset_index: int) -> float: ...
    def counters(self) -> dict[str, int]: ...


@dataclass(frozen=True)
class PatchPhase:
    config_id: int
    offset_index: int
    geometry: GeometryStage
    features: FeatureStage
    launches: tuple[int, ...]
    dynamics: dict[str, PropagationStage]


@dataclass(frozen=True)
class WorkflowResult:
    g0_passed: bool
    t_bound: float
    route: Route
    gates: dict[str, Gate]
    keyed_digest: str
    schedule_trace: tuple[tuple[int, int], ...]
    counters: dict[str, int]
    null_count: int
    capacity_count: int


def _patch_phase(backend: WorkflowBackend, config, offset_index: int) -> PatchPhase:
    geometry=backend.geometry(config,offset_index)
    if geometry.key!=PatchKey(config.config_id,offset_index):
        raise ConformanceError("geometry provider returned wrong PatchKey")
    common=np.asarray(geometry.common,dtype=np.int64)
    if common.shape!=(400,) or len(set(common.tolist()))!=400:
        raise GeometryPreflightFailure("synthetic conformance patch must expose exactly 400 unique common rows")
    if common.min()<0 or common.max()>=len(geometry.lifts): raise ConformanceError("common population out of range")
    features=backend.features(geometry)
    for name in ("physical","address","parity","position","far"):
        value=np.asarray(getattr(features,name))
        if len(value)!=len(geometry.lifts) or not np.isfinite(value).all():
            raise ConformanceError(f"invalid {name} feature population")
    common_lifts=tuple(geometry.lifts[i] for i in common)
    slabs=pca_slabs(geometry.par[common],common_lifts,production=True)
    launch_ids=select_launches(slabs,common_lifts)
    lookup={lift:i for i,lift in enumerate(geometry.lifts)}
    launches=tuple(lookup[x] for x in launch_ids)
    if len(launches)!=200: raise ConformanceError("launch registry drift")
    dynamics={engine:backend.propagate(engine,geometry,launches) for engine in ("coherent","classical")}
    return PatchPhase(config.config_id,offset_index,geometry,features,launches,dynamics)


def run_protocol(backend: WorkflowBackend, iteration_order: str="forward", parallelism: int=1) -> WorkflowResult:
    """Run the full synthetic-capable protocol. There is deliberately no data loader here."""
    if iteration_order not in ("forward","reverse") or parallelism not in (1,2):
        raise ConformanceError("unsupported traversal/scheduling mode")
    tasks=[(c,o) for c in CONFIGS for o in range(6)]
    if iteration_order=="reverse": tasks.reverse()
    if parallelism==1:
        completed=[_patch_phase(backend,c,o) for c,o in tasks]
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            completed=list(pool.map(lambda co:_patch_phase(backend,*co),tasks))
    schedule=tuple((x.config_id,x.offset_index) for x in completed)
    keyed={(x.config_id,x.offset_index):x for x in completed}
    expected={(c.config_id,o) for c in CONFIGS for o in range(6)}
    if set(keyed)!=expected or len(keyed)!=54: raise ConformanceError("missing or duplicate patch result")

    # G0 is a hard global barrier. No endpoint or fitted/control operation occurs above this line.
    crossings=[boundary_crossing(x.dynamics[e].strip_mass) for x in keyed.values() for e in ("coherent","classical")]
    t_bound=min(crossings)
    if t_bound<=8:
        g0=Gate("G0","fail",t_bound,8.0,t_bound-8.0)
        finite=Route("not evaluated",False,False,"finite-size-limited")
        digest=_digest({"t_bound":t_bound,"g0":"fail","keys":sorted(keyed)})
        counters=backend.counters(); counters["beta"]=0
        return WorkflowResult(False,t_bound,finite,{"G0":g0},digest,schedule,counters,0,0)

    endpoints: dict[tuple[int,int,str],BetaEndpoint]={}
    regressions: dict[tuple[int,int,str],RegressionStage]={}
    for key in sorted(keyed):
        patch=keyed[key]
        for engine in ("coherent","classical"):
            endpoint=beta_fit(patch.dynamics[engine].msd_fit)
            if not endpoint.valid: raise ConformanceError(f"invalid {engine} endpoint")
            endpoints[key+(engine,)]=endpoint
            regression=backend.regress(engine,patch.geometry,patch.features,endpoint)
            if not regression.position_reported or not regression.far_reported:
                raise ConformanceError("mandatory descriptive control omitted")
            regressions[key+(engine,)]=regression

    def matrix(engine: str, field: str) -> np.ndarray:
        return np.asarray([[getattr(regressions[(c.config_id,o,engine)],field) for o in range(6)] for c in CONFIGS],dtype=np.float64)
    coherent_address=matrix("coherent","address"); classical_address=matrix("classical","address")
    plain=matrix("coherent","plain"); shuffled=matrix("coherent","shuffled")
    residual=matrix("coherent","residual"); parity=matrix("coherent","parity")
    observed=m9(LabelledArray(coherent_address,("config","offset"),(GENERAL_LABELS,OFFSET_LABELS)))
    classical=m9(LabelledArray(classical_address,("config","offset"),(GENERAL_LABELS,OFFSET_LABELS)))
    residual_m9=m9(LabelledArray(residual,("config","offset"),(GENERAL_LABELS,OFFSET_LABELS)))
    parity_m9=m9(LabelledArray(parity,("config","offset"),(GENERAL_LABELS,OFFSET_LABELS)))

    null=np.empty((1000,7,6),dtype=np.float64)
    null_tasks=[(b,c,o) for b in range(1000) for c in PERMUTATION_CONFIGS for o in range(6)]
    if iteration_order=="reverse": null_tasks.reverse()
    for b,c,o in null_tasks: null[b,PERMUTATION_CONFIGS.index(c),o]=backend.local_null(c,o,b)
    null_m=mperm7(LabelledArray(null,("draw","config","offset"),(NULL_DRAW_LABELS,PERMUTATION_LABELS,OFFSET_LABELS)))

    capacity=np.empty((200,9,6),dtype=np.float64)
    cap_tasks=[(b,c,o) for b in range(200) for c in CONFIGS for o in range(6)]
    if iteration_order=="reverse": cap_tasks.reverse()
    for b,c,o in cap_tasks: capacity[b,c.config_id,o]=backend.capacity(b,c,o)
    cap_m=capacity_m9(LabelledArray(capacity,("draw","config","offset"),(CAPACITY_DRAW_LABELS,GENERAL_LABELS,OFFSET_LABELS)))
    floor=capacity_floor(cap_m)
    coherent_g1=[float(np.median(np.concatenate([endpoints[(c.config_id,o,"coherent")].r2_fit for o in range(6)]))) for c in CONFIGS]
    classical_g1=[float(np.median(np.concatenate([endpoints[(c.config_id,o,"classical")].r2_fit for o in range(6)]))) for c in CONFIGS]
    gates=evaluate_gates(t_bound,coherent_g1,classical_g1,q_ref(observed,null_m),observed,classical,floor,plain,shuffled,residual_m9,parity_m9)
    r2_folds=np.median(coherent_address,axis=0)
    routed=route(gates,r2_folds,observed,floor)
    payload={"gates":{k:v.__dict__ for k,v in gates.items()},"route":routed.__dict__,
             "address":coherent_address.tolist(),"classical":classical_address.tolist(),
             "null":null_m.tolist(),"capacity":cap_m.tolist(),"keys":sorted(keyed)}
    counters=backend.counters(); counters["beta"]=len(endpoints)
    return WorkflowResult(True,t_bound,routed,gates,_digest(payload),schedule,counters,1000,200)


def _digest(value) -> str:
    def clean(x):
        if isinstance(x,float) and np.isinf(x): return "Infinity" if x>0 else "-Infinity"
        if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)): return [clean(v) for v in x]
        return x
    return sha256(json.dumps(clean(value),sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
