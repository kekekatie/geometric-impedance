from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Callable, Iterable

import numpy as np
from scipy.spatial import ConvexHull, QhullError

from .constants import COMMON_MIN, OFFSETS
from .errors import ConformanceError, GeometryPreflightFailure
from .identity import LiftId, PatchKey, RowId, lift_ids


@dataclass(frozen=True)
class PatchGeometry:
    key: PatchKey
    lifts: np.ndarray
    par: np.ndarray
    perp: np.ndarray
    edges: tuple[tuple[int, int], ...]
    ell: float
    d_bound: np.ndarray
    adjacency: tuple[tuple[int, ...], ...]

    @property
    def ids(self) -> tuple[LiftId, ...]:
        return lift_ids(self.lifts)

    @property
    def row_ids(self) -> tuple[RowId, ...]:
        return tuple(RowId(self.key, x) for x in self.ids)


def hull_depth(points: np.ndarray) -> np.ndarray:
    p = np.asarray(points, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 2 or not np.isfinite(p).all():
        raise GeometryPreflightFailure("hull input must be finite n×2")
    try:
        h = ConvexHull(p)
    except QhullError as exc:
        raise GeometryPreflightFailure("degenerate convex hull") from exc
    A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(p @ A.T + b).max(axis=1)


def canonicalize_geometry(key: PatchKey, lifts: np.ndarray, par: np.ndarray,
                          perp: np.ndarray, edge_positions: Iterable[tuple[int, int]]) -> PatchGeometry:
    lifts = np.asarray(lifts)
    par = np.asarray(par, dtype=np.float64)
    perp = np.asarray(perp, dtype=np.float64)
    ids = lift_ids(lifts)
    n = len(ids)
    if par.shape != (n, 2) or perp.shape != (n, 2) or not np.isfinite(par).all() or not np.isfinite(perp).all():
        raise ConformanceError("row-aligned coordinates must be finite n×2")
    order = sorted(range(n), key=ids.__getitem__)
    inverse = np.empty(n, dtype=np.int64)
    inverse[order] = np.arange(n)
    sorted_lifts, sorted_par, sorted_perp = lifts[order], par[order], perp[order]
    edge_ids: set[tuple[LiftId, LiftId]] = set()
    for raw_i, raw_j in edge_positions:
        if raw_i == raw_j or not (0 <= raw_i < n and 0 <= raw_j < n):
            raise ConformanceError("invalid or self edge")
        edge = tuple(sorted((ids[raw_i], ids[raw_j])))
        if edge in edge_ids:
            raise ConformanceError("duplicate edge identity")
        edge_ids.add(edge)
    sorted_ids = tuple(sorted(ids))
    pos = {v: i for i, v in enumerate(sorted_ids)}
    edges = tuple(sorted((pos[a], pos[b]) for a, b in edge_ids))
    adj = [set() for _ in range(n)]
    lengths = []
    for i, j in edges:
        adj[i].add(j); adj[j].add(i)
        lengths.append(float(np.linalg.norm(sorted_par[i] - sorted_par[j])))
    if not lengths or any(len(x) == 0 for x in adj):
        raise GeometryPreflightFailure("empty edge set or zero-degree vertex")
    ell = float(np.median(np.asarray(lengths, dtype=np.float64)))
    if not np.isfinite(ell) or ell <= 0:
        raise GeometryPreflightFailure("invalid median edge length")
    return PatchGeometry(key, sorted_lifts, sorted_par, sorted_perp, edges, ell,
                         hull_depth(sorted_par), tuple(tuple(sorted(x)) for x in adj))


def generate_adapter(structure: Callable, generate: Callable, build_edges: Callable,
                     key: PatchKey, rank: int, extent: int) -> PatchGeometry:
    expected = {"N", "extent", "offset", "disorder", "seed", "extra_offset", "disorder_extra"}
    if not expected.issubset(inspect.signature(generate).parameters):
        raise ConformanceError("generator signature does not implement AC-02")
    st = structure(rank)
    lifts, par, perp, ustar = generate(rank, extent, offset=np.asarray(OFFSETS[key.offset_index]),
                                       disorder=0.0, seed=0, extra_offset=None,
                                       disorder_extra=False)
    raw_edges = build_edges(lifts, rank, ustar)
    if not isinstance(st, dict):
        raise ConformanceError("structure must return a mapping")
    return canonicalize_geometry(key, lifts, par, perp, raw_edges)


def common_indices(patch: PatchGeometry) -> np.ndarray:
    return np.flatnonzero(patch.d_bound >= np.float64(16.0 * patch.ell))


def validate_common_floor(patch: PatchGeometry, production: bool = True) -> np.ndarray:
    idx = common_indices(patch)
    if production and len(idx) < COMMON_MIN:
        raise GeometryPreflightFailure("r16 common set has fewer than 400 rows")
    return idx


def exact_core_to_padded(core_lifts: np.ndarray, padded_lifts: np.ndarray) -> np.ndarray:
    core, padded = lift_ids(core_lifts), lift_ids(padded_lifts)
    lookup = {v: i for i, v in enumerate(padded)}
    if len(lookup) != len(padded) or any(v not in lookup for v in core):
        raise GeometryPreflightFailure("core/padded LiftId correspondence is not one-to-one")
    out = np.asarray([lookup[v] for v in core], dtype=np.int64)
    if len(set(out.tolist())) != len(core):
        raise GeometryPreflightFailure("duplicate padded match")
    return out


def validate_padding(ell: float, padded_depth_on_core: np.ndarray,
                     area4: np.ndarray, area6: np.ndarray,
                     perimeter4: np.ndarray, perimeter6: np.ndarray) -> dict[str, float]:
    arrays = [np.asarray(x, dtype=np.float64) for x in
              (padded_depth_on_core, area4, area6, perimeter4, perimeter6)]
    if ell <= 0 or not all(np.isfinite(x).all() for x in arrays):
        raise GeometryPreflightFailure("nonfinite padded-cell geometry")
    if not (arrays[1].shape == arrays[2].shape == arrays[3].shape == arrays[4].shape):
        raise GeometryPreflightFailure("Delta=4/6 cell arrays are misaligned")
    ring = float(np.min(arrays[0]) / ell)
    area_rel = float(np.max(np.abs(arrays[1]-arrays[2]) / np.maximum(np.abs(arrays[2]), 1e-15)))
    perim_rel = float(np.max(np.abs(arrays[3]-arrays[4]) / np.maximum(np.abs(arrays[4]), 1e-15)))
    if ring < 3 or area_rel > 1e-6 or perim_rel > 1e-6:
        raise GeometryPreflightFailure("padding ring or convergence requirement failed")
    return {"ring_width": ring, "area_relative_delta": area_rel,
            "perimeter_relative_delta": perim_rel}
