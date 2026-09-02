"""Compliant invented provider for the real production orchestrator."""

from __future__ import annotations

from collections import Counter
from threading import Lock, current_thread

import numpy as np

from .constants import BOUNDARY_TIMES, CAPACITY_PATCH_AXIS, FIT_TIMES
from .endpoint import BetaEndpoint
from .identity import PatchKey
from .orchestrator import (FeatureStage, GeometryStage, PropagationStage,
                           RegressionStage, WorkflowResult, run_protocol)
from .propagation import (classical_generator, classical_slice,
                          coherent_hamiltonian, coherent_slice)
from .regression import direct_r2
from .seed_registry import CapacityRegistry, address_rng


class SyntheticBackend:
    """Study-blind deterministic dependency injection used only by conformance tests."""

    def __init__(self, variant: str="earned") -> None:
        self.variant=variant; self._counts=Counter(); self._lock=Lock()
        self._capacity=CapacityRegistry(); self._worker_threads=set()

    def _count(self,name: str) -> None:
        with self._lock: self._counts[name]+=1

    def counters(self) -> dict[str,int]:
        with self._lock: return {**dict(self._counts),"worker_thread_count":len(self._worker_threads)}

    def geometry(self,config,offset_index: int) -> GeometryStage:
        self._count("geometry")
        with self._lock: self._worker_threads.add(current_thread().name)
        lifts=tuple((config.config_id,offset_index,i,0) for i in range(400))
        x=np.arange(400,dtype=np.float64); par=np.column_stack((x,(x%17)*1e-4))
        return GeometryStage(PatchKey(config.config_id,offset_index),lifts,par,np.arange(400,dtype=np.int64))

    def features(self,geometry: GeometryStage) -> FeatureStage:
        self._count("features"); x=geometry.par[:,0]; y=geometry.par[:,1]
        physical=np.column_stack((x/400,(x%7)/7)); address=np.column_stack((np.sin(x/17),np.cos(x/19)))
        parity=np.column_stack(((x%5)/5,(x%11)/11)); position=np.column_stack((x,y,np.hypot(x,y)))
        far=np.column_stack(tuple((x%(k+3))/(k+3) for k in range(6)))
        return FeatureStage(physical,address,parity,position,far)

    def propagate(self,engine: str,geometry: GeometryStage,launch_indices: tuple[int,...]) -> PropagationStage:
        self._count(f"propagate_{engine}")
        if len(launch_indices)!=200: raise AssertionError("production launch count weakened")
        A=np.array([[0,1,1,0],[1,0,1,1],[1,1,0,0],[0,1,0,0]],dtype=np.float64)
        initial=np.eye(4)[:,0]
        if engine=="coherent": coherent_slice(coherent_hamiltonian(A),initial,.25)
        elif engine=="classical": classical_slice(classical_generator(A),initial,.25)
        else: raise ValueError("unknown engine")
        beta=.72 if engine=="coherent" else .48
        msd=np.asarray([1.0+(j%5)*.01 for j in range(200)])[:,None]*np.asarray(FIT_TIMES)[None,:]**(2*beta)
        if self.variant=="modifier_withheld" and engine=="classical" and geometry.key.config_id==0:
            msd=msd*(1.0+.8*np.sin(np.asarray(FIT_TIMES)[None,:]*3.0))
        strip=np.zeros((200,len(BOUNDARY_TIMES)),dtype=np.float64)
        if self.variant=="g0_at_8" and geometry.key==PatchKey(0,0) and engine=="coherent": strip[0,-1]=.01
        return PropagationStage(msd,strip)

    def regress(self,engine: str,geometry: GeometryStage,features: FeatureStage,
                endpoint: BetaEndpoint) -> RegressionStage:
        self._count("regress")
        if direct_r2(np.arange(4,dtype=float),np.arange(4,dtype=float)).value!=1: raise AssertionError
        base=.8 if engine=="coherent" else .12
        if self.variant=="modifier_withheld" and engine=="classical" and geometry.key.config_id==0: base=.3
        return RegressionStage(base,.1,base,.2,.7,True,True)

    def local_null(self,config,offset_index: int,repetition: int) -> float:
        self._count("local_null")
        return float(address_rng(config.family,config.tier,config.extent,offset_index,((0,1),),repetition).random()-.5)

    def capacity(self,draw: int,config,offset_index: int) -> float:
        self._count("capacity")
        child=CAPACITY_PATCH_AXIS.index((config,offset_index))
        return float(self._capacity.field(draw,child,1).values.mean())


def run_synthetic_suite(iteration_order: str="forward", parallelism: int=1,
                        variant: str="earned") -> WorkflowResult:
    return run_protocol(SyntheticBackend(variant),iteration_order,parallelism)
