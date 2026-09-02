from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from .constants import LAUNCHES_PER_PATCH, LAUNCHES_PER_SLAB, SLAB_MIN
from .errors import ConformanceError, GeometryPreflightFailure
from .identity import LiftId


@dataclass(frozen=True)
class SlabRegistry:
    pc1: tuple[float, float]
    projections: np.ndarray
    slab: np.ndarray
    order: np.ndarray


def pca_slabs(par: np.ndarray, lifts: Sequence[LiftId], production: bool = True) -> SlabRegistry:
    x = np.asarray(par, dtype=np.float64)
    if x.shape != (len(lifts), 2) or not np.isfinite(x).all() or len(set(lifts)) != len(lifts):
        raise ConformanceError("PCA rows/identities invalid")
    centred = x - x.mean(axis=0)
    covariance = centred.T @ centred / len(x)
    values, vectors = np.linalg.eigh(covariance)
    lam = float(values[-1]); gap = float(values[-1] - values[-2])
    if gap <= 1e-12 * max(1.0, abs(lam)):
        raise GeometryPreflightFailure("leading PCA eigenvalue is tied")
    pc = vectors[:, -1].copy()
    orient = np.flatnonzero(np.abs(pc) > 1e-15)
    if len(orient) == 0:
        raise GeometryPreflightFailure("PC1 has no orientable component")
    if pc[orient[0]] < 0: pc *= -1
    projection = centred @ pc
    order = np.asarray(sorted(range(len(x)), key=lambda i: (projection[i], lifts[i])), dtype=np.int64)
    sizes = [len(x)//4 + (1 if j < len(x)%4 else 0) for j in range(4)]
    if production and min(sizes) < SLAB_MIN:
        raise GeometryPreflightFailure("PCA slab has fewer than 100 rows")
    slab = np.empty(len(x), dtype=np.int64); start = 0
    for j, size in enumerate(sizes):
        slab[order[start:start+size]] = j; start += size
    return SlabRegistry(tuple(float(v) for v in pc), projection, slab, order)


def launch_positions(n: int) -> np.ndarray:
    if n < SLAB_MIN:
        raise GeometryPreflightFailure("launch slab has fewer than 100 rows")
    out = np.asarray([math.floor(j * (n - 1) / 49) for j in range(50)], dtype=np.int64)
    if len(out) != LAUNCHES_PER_SLAB or len(set(out.tolist())) != 50 or out.min() < 0 or out.max() >= n:
        raise ConformanceError("invalid launch formula result")
    return out


def select_launches(registry: SlabRegistry, lifts: Sequence[LiftId]) -> tuple[LiftId, ...]:
    selected = []
    for slab in range(4):
        members = [i for i in registry.order if registry.slab[i] == slab]
        selected.extend(lifts[members[j]] for j in launch_positions(len(members)))
    if len(selected) != LAUNCHES_PER_PATCH or len(set(selected)) != LAUNCHES_PER_PATCH:
        raise ConformanceError("launch registry must contain 200 unique LiftIds")
    return tuple(selected)


def outer_training_offsets(held_out: int) -> tuple[int, ...]:
    if held_out not in range(6): raise ConformanceError("invalid outer fold")
    return tuple(i for i in range(6) if i != held_out)


def inner_training_mask(slabs: np.ndarray, held_out_slab: int) -> np.ndarray:
    if held_out_slab not in range(4) or set(np.unique(slabs)) != set(range(4)):
        raise ConformanceError("invalid simultaneous inner-fold slabs")
    return np.asarray(slabs) != held_out_slab
