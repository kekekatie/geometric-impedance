from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .constants import CAPACITY_DRAWS, CAPACITY_PATCH_AXIS, CONFIGS, PERMUTATION_CONFIGS
from .errors import ConformanceError


@dataclass(frozen=True)
class LabelledArray:
    values: np.ndarray
    axes: tuple[str,...]
    labels: tuple[tuple[object,...],...]

    def require(self, axes: tuple[str,...], expected_labels: tuple[tuple[object,...],...]) -> np.ndarray:
        sizes=tuple(len(x) for x in expected_labels)
        if (self.axes!=axes or self.values.shape!=sizes or self.labels!=expected_labels
                or any(len(set(x))!=len(x) for x in self.labels)
                or not np.isfinite(self.values).all()):
            raise ConformanceError("labelled aggregation boundary mismatch")
        return np.asarray(self.values,dtype=np.float64)


GENERAL_LABELS=tuple(c.label for c in CONFIGS)
PERMUTATION_LABELS=tuple(c.label for c in PERMUTATION_CONFIGS)
G8_LABELS=("silver-e14","silver-e16","silver-e18","golden-e18","golden-e20","golden-e22","platinum-e20")
OFFSET_LABELS=tuple(range(6))
NULL_DRAW_LABELS=tuple(range(1000))
CAPACITY_DRAW_LABELS=tuple(range(200))
CAPACITY_PATCH_LABELS=tuple((c.label,offset) for c,offset in CAPACITY_PATCH_AXIS)


def m9(data: LabelledArray) -> float:
    x=data.require(("config","offset"),(GENERAL_LABELS,OFFSET_LABELS))
    return float(np.median(np.median(x,axis=0)))


def mperm7(data: LabelledArray) -> np.ndarray:
    x=data.require(("draw","config","offset"),(NULL_DRAW_LABELS,PERMUTATION_LABELS,OFFSET_LABELS))
    return np.median(np.median(x,axis=1),axis=1)


def capacity_m9(data: LabelledArray) -> np.ndarray:
    x=data.require(("draw","config","offset"),(CAPACITY_DRAW_LABELS,GENERAL_LABELS,OFFSET_LABELS))
    return np.median(np.median(x,axis=1),axis=1)


def capacity_floor(draws: np.ndarray) -> float:
    x=np.asarray(draws,dtype=np.float64)
    if x.shape!=(CAPACITY_DRAWS,) or not np.isfinite(x).all(): raise ConformanceError("capacity floor requires 200 complete M9 draws")
    return float(np.quantile(x,0.95,method="linear"))


def q_ref(observed: float, null: np.ndarray) -> float:
    x=np.asarray(null,dtype=np.float64)
    if x.shape!=(1000,) or not np.isfinite(x).all() or not np.isfinite(observed): raise ConformanceError("q_ref requires 1000 complete nulls")
    return float((1+np.count_nonzero(x>=observed))/1001)


def validate_capacity_patch_axis(labels: tuple[tuple[str,int],...]) -> None:
    if labels!=CAPACITY_PATCH_LABELS or len(set(labels))!=54:
        raise ConformanceError("capacity patch children require family-major, offset-fast labels")


def westfall_young(observed: LabelledArray, null: LabelledArray) -> dict[str,np.ndarray]:
    obs=observed.require(("config",),(G8_LABELS,))
    n=null.require(("draw","config"),(NULL_DRAW_LABELS,G8_LABELS))
    order=np.argsort(-obs,kind="stable"); ordered=obs[order]; nn=n[:,order]
    raw=np.empty(7)
    for k in range(7): raw[k]=(1+np.count_nonzero(np.max(nn[:,k:],axis=1)>=ordered[k]))/1001
    adjusted=np.maximum.accumulate(raw)
    inverse=np.empty(7,dtype=int); inverse[order]=np.arange(7)
    return {"order":order,"raw_ordered":raw,"adjusted":adjusted[inverse]}
