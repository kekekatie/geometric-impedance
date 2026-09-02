from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

from .constants import GBT_PARAMS
from .errors import ConformanceError
from .identity import FitProvenance, PatchKey, RowId


@dataclass(frozen=True)
class R2Result:
    value: float | None
    reason: str | None = None

    @property
    def defined(self) -> bool:
        return self.value is not None


def direct_r2(y: np.ndarray, prediction: np.ndarray) -> R2Result:
    y = np.asarray(y, dtype=np.float64); p = np.asarray(prediction, dtype=np.float64)
    if y.shape != p.shape or y.ndim != 1:
        raise ConformanceError("R2 inputs are not paired one-dimensional arrays")
    if not np.isfinite(y).all() or not np.isfinite(p).all():
        return R2Result(None, "nonfinite")
    sst = float(np.sum((y-y.mean())**2, dtype=np.float64))
    if sst <= 0: return R2Result(None, "SST<=0")
    sse = float(np.sum((y-p)**2, dtype=np.float64))
    return R2Result(float(1.0-sse/sst))


@dataclass
class ScalarRegressor:
    model: HistGradientBoostingRegressor
    provenance: FitProvenance
    applied: set[tuple[int, int | None]]

    @classmethod
    def fit(cls, X: np.ndarray, y: np.ndarray, provenance: FitProvenance) -> "ScalarRegressor":
        X = np.asarray(X, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
        if X.ndim != 2 or y.shape != (len(X),) or not np.isfinite(X).all() or not np.isfinite(y).all():
            raise ConformanceError("invalid scalar-regressor fit data")
        model = HistGradientBoostingRegressor(**GBT_PARAMS).fit(X, y)
        return cls(model, provenance, set())

    def predict(self, X: np.ndarray, patch_keys: Iterable[PatchKey], rows: Iterable[RowId],
                application: tuple[int, int | None] | None = None) -> np.ndarray:
        self.provenance.reject_held_out(patch_keys, rows)
        if application is not None:
            if application in self.applied: raise ConformanceError("duplicate fitted-object application")
            self.applied.add(application)
        return np.asarray(self.model.predict(np.asarray(X, dtype=np.float64)), dtype=np.float64)


def paired_increment(y: np.ndarray, base_prediction: np.ndarray, augmented_prediction: np.ndarray,
                     base_rows: tuple[RowId, ...], augmented_rows: tuple[RowId, ...]) -> R2Result:
    if base_rows != augmented_rows:
        raise ConformanceError("paired increment row identity mismatch")
    base = direct_r2(y, base_prediction); augmented = direct_r2(y, augmented_prediction)
    if not base.defined or not augmented.defined:
        return R2Result(None, base.reason or augmented.reason)
    return R2Result(float(augmented.value - base.value))


@dataclass(frozen=True)
class PopulationScaler:
    mean: np.ndarray
    sd: np.ndarray
    provenance: FitProvenance
    floor: float

    @classmethod
    def fit(cls, values: np.ndarray, provenance: FitProvenance, floor: float = 1e-12) -> "PopulationScaler":
        x = np.asarray(values, dtype=np.float64)
        if x.ndim != 2 or not np.isfinite(x).all(): raise ConformanceError("invalid scaler input")
        return cls(x.mean(axis=0), x.std(axis=0, ddof=0), provenance, floor)

    def transform(self, values: np.ndarray, patch_keys: Iterable[PatchKey], rows: Iterable[RowId]) -> np.ndarray:
        self.provenance.reject_held_out(patch_keys, rows)
        x = np.asarray(values, dtype=np.float64)
        out = np.zeros_like(x, dtype=np.float64); active = self.sd >= self.floor
        out[:, active] = (x[:, active] - self.mean[active]) / self.sd[active]
        return out


def fit_independent_residualisers(X: np.ndarray, address11: np.ndarray,
                                  provenances: tuple[FitProvenance, ...]) -> tuple[ScalarRegressor, ...]:
    a = np.asarray(address11, dtype=np.float64)
    if a.ndim != 2 or a.shape[1] != 11 or len(provenances) != 11:
        raise ConformanceError("residualiser topology must contain 11 scalar models")
    return tuple(ScalarRegressor.fit(X, a[:, j], provenances[j]) for j in range(11))
