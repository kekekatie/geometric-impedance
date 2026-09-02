from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .errors import ConformanceError
from .identity import FitProvenance, PatchKey, RowId
from .regression import fit_independent_residualisers


@dataclass(frozen=True)
class CrossFitResult:
    training_residuals: np.ndarray
    held_out_residuals: np.ndarray
    model_count: int


def cross_fitted_residuals(X_train: np.ndarray, address_train: np.ndarray, slabs: np.ndarray,
                           train_rows: tuple[RowId,...], held_X: np.ndarray,
                           held_address: np.ndarray, held_rows: tuple[RowId,...],
                           outer_fold: int, schema_hash: str) -> CrossFitResult:
    if set(np.unique(slabs))!=set(range(4)) or not (len(X_train)==len(address_train)==len(slabs)==len(train_rows)):
        raise ConformanceError("invalid residual cross-fit topology")
    result=np.empty_like(address_train,dtype=np.float64); count=0
    for inner in range(4):
        fit=slabs!=inner; test=~fit
        provs=tuple(FitProvenance(frozenset(r.patch for r in np.asarray(train_rows,dtype=object)[fit]),
                                  frozenset(np.asarray(train_rows,dtype=object)[fit]),outer_fold,inner,schema_hash) for _ in range(11))
        models=fit_independent_residualisers(X_train[fit],address_train[fit],provs); count+=len(models)
        for j,m in enumerate(models):
            prediction=m.predict(X_train[test],(),np.asarray(train_rows,dtype=object)[test])
            result[test,j]=address_train[test,j]-prediction
    provs=tuple(FitProvenance(frozenset(r.patch for r in train_rows),frozenset(train_rows),outer_fold,None,schema_hash) for _ in range(11))
    outer=fit_independent_residualisers(X_train,address_train,provs); count+=len(outer)
    held=np.empty_like(held_address,dtype=np.float64)
    for j,m in enumerate(outer): held[:,j]=held_address[:,j]-m.predict(held_X,(),held_rows,application=(outer_fold,None))
    return CrossFitResult(result,held,count)
