from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .constants import CAPACITY_DRAWS
from .errors import ConformanceError


@dataclass(frozen=True)
class LabelledArray:
    values: np.ndarray
    axes: tuple[str,...]
    labels: tuple[tuple[object,...],...]

    def require(self, axes: tuple[str,...], sizes: tuple[int,...]) -> np.ndarray:
        if self.axes!=axes or self.values.shape!=sizes or tuple(len(x) for x in self.labels)!=sizes or not np.isfinite(self.values).all():
            raise ConformanceError("labelled aggregation boundary mismatch")
        return np.asarray(self.values,dtype=np.float64)


def m9(data: LabelledArray) -> float:
    x=data.require(("config","offset"),(9,6))
    return float(np.median(np.median(x,axis=0)))


def mperm7(data: LabelledArray) -> np.ndarray:
    x=data.require(("draw","config","offset"),(1000,7,6))
    return np.median(np.median(x,axis=1),axis=1)


def capacity_m9(data: LabelledArray) -> np.ndarray:
    x=data.require(("draw","config","offset"),(200,9,6))
    return np.median(np.median(x,axis=1),axis=1)


def capacity_floor(draws: np.ndarray) -> float:
    x=np.asarray(draws,dtype=np.float64)
    if x.shape!=(CAPACITY_DRAWS,) or not np.isfinite(x).all(): raise ConformanceError("capacity floor requires 200 complete M9 draws")
    return float(np.quantile(x,0.95,method="linear"))


def q_ref(observed: float, null: np.ndarray) -> float:
    x=np.asarray(null,dtype=np.float64)
    if x.shape!=(1000,) or not np.isfinite(x).all() or not np.isfinite(observed): raise ConformanceError("q_ref requires 1000 complete nulls")
    return float((1+np.count_nonzero(x>=observed))/1001)


def westfall_young(observed: np.ndarray, null: np.ndarray) -> dict[str,np.ndarray]:
    obs=np.asarray(observed,dtype=np.float64); n=np.asarray(null,dtype=np.float64)
    if obs.shape!=(7,) or n.shape!=(1000,7) or not np.isfinite(obs).all() or not np.isfinite(n).all(): raise ConformanceError("G8 requires 7 cells and 1000 synchronized null rows")
    order=np.argsort(-obs,kind="stable"); ordered=obs[order]; nn=n[:,order]
    raw=np.empty(7)
    for k in range(7): raw[k]=(1+np.count_nonzero(np.max(nn[:,k:],axis=1)>=ordered[k]))/1001
    adjusted=np.maximum.accumulate(raw)
    inverse=np.empty(7,dtype=int); inverse[order]=np.arange(7)
    return {"order":order,"raw_ordered":raw,"adjusted":adjusted[inverse]}
