"""Full-axis synthetic conformance orchestrator; never loads study geometry or data."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

import numpy as np

from .aggregation import LabelledArray, capacity_floor, capacity_m9, m9, mperm7, q_ref
from .constants import CONFIGS, OFFSETS, PERMUTATION_CONFIGS
from .gates import evaluate_gates
from .routing import Route, route
from .seed_registry import CapacityRegistry, golden_vectors


@dataclass(frozen=True)
class SyntheticResult:
    route: Route
    trace_markers: tuple[str,...]
    population_counts: np.ndarray
    slab_counts: np.ndarray
    launch_counts: np.ndarray
    null_count: int
    capacity_count: int
    audit_sha256: str


def run_synthetic_suite(iteration_order: str="forward", parallelism: int=1,
                        variant: str="earned") -> SyntheticResult:
    if iteration_order not in ("forward","reverse") or parallelism not in (1,2):
        raise ValueError("unsupported synthetic conformance mode")
    # Invented metadata-only fixture satisfying production floors and both labelled axes.
    population=np.full((9,6),400,dtype=np.int64)
    slabs=np.full((9,6,4),100,dtype=np.int64)
    launches=np.full((9,6),200,dtype=np.int64)
    config_labels=tuple(c.label for c in CONFIGS); offset_labels=tuple(range(6))
    plain=np.full((9,6),.8); shuffled=np.full((9,6),.1)
    observed=m9(LabelledArray(plain,("config","offset"),(config_labels,offset_labels)))
    null=np.linspace(-.5,.5,1000)[:,None,None]+np.zeros((1000,7,6))
    null_axis=(tuple(range(1000)),tuple(c.label for c in PERMUTATION_CONFIGS),offset_labels)
    null_m=mperm7(LabelledArray(null,("draw","config","offset"),null_axis))
    cap=np.linspace(-.2,.2,200)[:,None,None]+np.zeros((200,9,6))
    cap_axis=(tuple(range(200)),config_labels,offset_labels)
    cap_m=capacity_m9(LabelledArray(cap,("draw","config","offset"),cap_axis)); floor=capacity_floor(cap_m)
    coherent=np.full(9,.95); classical=np.full(9,.95); tbound=np.inf
    if variant=="modifier_withheld": classical[0]=.89
    if variant=="g0_fail": tbound=8.0
    if variant=="g4_undefined": plain[0,0]=0
    q=0.001 if variant!="mixed" else .2
    route_r16=.8 if variant in ("survives","mixed") else .1
    gates=evaluate_gates(tbound,coherent,classical,q,observed,.1,floor,plain,shuffled,.7,.2)
    routed=route(gates,np.full(6,.8),route_r16,floor)
    markers=tuple(f"AC-{i:02d}" for i in range(1,26))
    audit={"order":iteration_order,"parallelism":parallelism,"variant":variant,
           "configs":config_labels,"offsets":OFFSETS,"permutation":tuple(c.label for c in PERMUTATION_CONFIGS),
           "population":population.tolist(),"slabs":slabs.tolist(),"launches":launches.tolist(),
           "address_repetitions":len(null_m),"capacity_draws":len(cap_m),"trace":markers,
           "route":routed.__dict__}
    digest=sha256(json.dumps(audit,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return SyntheticResult(routed,markers,population,slabs,launches,len(null_m),len(cap_m),digest)
