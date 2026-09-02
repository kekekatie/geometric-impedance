from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .errors import ConformanceError
from .features import address_operator
from .geometry import PatchGeometry
from .identity import FitProvenance, PatchKey, RowId
from .regression import PopulationScaler


@dataclass(frozen=True)
class ParityResult:
    available: bool
    raw_scaled: np.ndarray | None
    address11: np.ndarray | None
    reason: str | None


def fit_parity_scaler(training_raw: np.ndarray, patch_sds: np.ndarray,
                      provenance: FitProvenance) -> PopulationScaler:
    sds=np.asarray(patch_sds,dtype=np.float64)
    if sds.ndim!=2 or sds.shape[1]!=2 or np.any(sds<0): raise ConformanceError("invalid parity patch SDs")
    if np.any(sds<1e-9): raise ConformanceError("parity unavailable: patch component SD below 1e-9")
    return PopulationScaler.fit(training_raw,provenance,floor=1e-12)


def parity_block(patch: PatchGeometry, degree: np.ndarray, voronoi_area: np.ndarray,
                 scaler: PopulationScaler, patch_keys=(), rows=()) -> ParityResult:
    raw=np.column_stack((degree,voronoi_area)).astype(np.float64)
    if np.any(raw.std(axis=0,ddof=0)<1e-9): return ParityResult(False,None,None,"patch SD below 1e-9")
    scaled=scaler.transform(raw,patch_keys,rows)
    return ParityResult(True,scaled,address_operator(patch,scaled),None)
