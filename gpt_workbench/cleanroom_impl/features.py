from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy.spatial import cKDTree

from .constants import RADII
from .errors import ConformanceError
from .geometry import PatchGeometry, hull_depth
from .identity import LiftId

Motif = tuple[tuple[int, int], ...]


def motif_registry(offset_motifs: Iterable[Iterable[Motif]]) -> tuple[Motif, ...]:
    registry = tuple(sorted({tuple(tuple(int(x) for x in pair) for pair in motif)
                             for group in offset_motifs for motif in group}))
    return registry


def motif_one_hot(motifs: Sequence[Motif], registry: Sequence[Motif]) -> np.ndarray:
    lookup = {m: i for i, m in enumerate(registry)}
    if len(lookup) != len(registry):
        raise ConformanceError("duplicate motif in registry")
    out = np.zeros((len(motifs), len(registry)), dtype=np.float64)
    for i, motif in enumerate(motifs):
        if motif not in lookup:
            raise ConformanceError("motif absent from frozen registry")
        out[i, lookup[motif]] = 1.0
    return out


def graph_shell_distances(adjacency: Sequence[Sequence[int]], source: int, maximum: int) -> dict[int, int]:
    dist = {source: 0}; q = deque([source])
    while q:
        v = q.popleft()
        if dist[v] == maximum:
            continue
        for w in adjacency[v]:
            if w not in dist:
                dist[w] = dist[v] + 1; q.append(w)
    return dist


def address_operator(patch: PatchGeometry, raw_field: np.ndarray) -> np.ndarray:
    raw = np.asarray(raw_field, dtype=np.float64)
    n = len(patch.lifts)
    if raw.shape != (n, 2) or not np.isfinite(raw).all():
        raise ConformanceError("raw address field must be finite n×2")
    sm = {r: np.zeros((n, 2)) for r in (2, 4, 8)}
    sv = {r: np.zeros(n) for r in (2, 4, 8)}
    grad = np.zeros(n)
    tree = cKDTree(patch.par)
    for i in range(n):
        dist = graph_shell_distances(patch.adjacency, i, 8)
        members = np.asarray(sorted(dist), dtype=np.int64)
        dd = np.asarray([dist[v] for v in members])
        for r in (2, 4, 8):
            selected = members[dd <= r]
            sm[r][i] = raw[selected].mean(axis=0)
            sv[r][i] = raw[selected].var(axis=0, ddof=0).sum()
        nb = np.asarray(tree.query_ball_point(patch.par[i], 3.0), dtype=np.int64)
        if len(nb) >= 4:
            X = np.column_stack((patch.par[nb] - patch.par[i], np.ones(len(nb))))
            coef, *_ = np.linalg.lstsq(X, raw[nb], rcond=None)
            grad[i] = np.linalg.norm(coef[:2])
    cols = []
    for r in (2, 4, 8):
        cols.extend((sm[r], sv[r][:, None]))
    cols.extend((grad[:, None], hull_depth(raw)[:, None]))
    out = np.column_stack(cols)
    if out.shape != (n, 11):
        raise AssertionError("address operator width drift")
    return out


def population_moments(values: np.ndarray) -> tuple[float, float, float, float]:
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 1 or len(x) == 0 or not np.isfinite(x).all():
        raise ConformanceError("moment sample must be finite and nonempty")
    mean = float(x.mean()); centred = x - mean
    var = float(np.mean(centred * centred)); sigma = float(np.sqrt(var))
    if sigma < 1e-9:
        return mean, 0.0, 0.0, 0.0
    skew = float(np.mean((centred / sigma) ** 3))
    excess = float(np.mean((centred / sigma) ** 4) - 3.0)
    return mean, var, skew, excess


def baseline_features(patch: PatchGeometry, motifs: Sequence[Motif], registry: Sequence[Motif], rank: int) -> tuple[np.ndarray, list[str], dict[str, np.ndarray]]:
    n = len(patch.lifts); tree = cKDTree(patch.par)
    deg = np.asarray([len(x) for x in patch.adjacency], dtype=np.float64)
    def counts(r: float) -> np.ndarray:
        return np.asarray(tree.query_ball_point(patch.par, r, return_length=True), dtype=np.float64)
    means = np.zeros(n); variances = np.zeros(n)
    psi = {k: np.zeros(n) for k in (rank, rank // 2, 2 * rank)}
    for i, neighbours in enumerate(patch.adjacency):
        d = patch.par[list(neighbours)] - patch.par[i]
        lengths = np.linalg.norm(d, axis=1)
        means[i], variances[i] = lengths.mean(), lengths.var(ddof=0)
        theta = np.arctan2(d[:, 1], d[:, 0])
        for k in psi:
            psi[k][i] = abs(np.exp(1j * k * theta).mean())
    names = ["dens", "deg", "edge_len_mean", "edge_len_var"]
    names += [f"motif:{json.dumps(m,separators=(',',':'))}" for m in registry]
    names += ["g1.6", "g2.6", f"psi{rank}", f"psi{rank//2}", f"psi{2*rank}", "g4", "g6"]
    out = np.column_stack((counts(2.0), deg, means, variances,
                           motif_one_hot(motifs, registry), counts(1.6), counts(2.6),
                           psi[rank], psi[rank//2], psi[2*rank], counts(4.0), counts(6.0)))
    aux = {"degree": deg, "dens": counts(2.0), "g1.6": counts(1.6), "g2.6": counts(2.6),
           "g4": counts(4.0), "g6": counts(6.0), "psiN": psi[rank],
           "psiHalf": psi[rank//2], "psiDouble": psi[2*rank]}
    return out, names, aux


def physical_features(patch: PatchGeometry, degree: np.ndarray, psi_half: np.ndarray,
                      psi_n: np.ndarray, psi_double: np.ndarray,
                      voronoi_area: np.ndarray) -> dict[int, tuple[np.ndarray, tuple[str, ...]]]:
    n = len(patch.lifts); tree = cKDTree(patch.par)
    degree = np.asarray(degree, dtype=np.float64); area = np.asarray(voronoi_area, dtype=np.float64)
    if any(x.shape != (n,) for x in (degree, psi_half, psi_n, psi_double, area)):
        raise ConformanceError("physical source arrays are misaligned")
    columns: list[np.ndarray] = []; names: list[str] = []; result = {}
    last = 0
    for s in RADII:
        distances = tree.query_ball_point(patch.par, s * patch.ell)
        # Newly admitted annuli, centre excluded, left-open/right-closed.
        for bin_index in range(last + 1, s + 1):
            vals = np.zeros(n)
            for i in range(n):
                d = np.linalg.norm(patch.par - patch.par[i], axis=1) / patch.ell
                bins = np.ceil(d - 1e-9).astype(int)
                vals[i] = np.count_nonzero((np.arange(n) != i) & (bins == bin_index))
            columns.append(vals); names.append(f"annulus_{bin_index}")
        b = np.zeros((n, 4)); dcols = np.zeros((n, 3)); e = np.zeros((n, 2))
        for i, candidates in enumerate(distances):
            nb = [j for j in candidates if j != i]
            sample = degree[nb] if nb else degree[i:i+1]
            b[i] = population_moments(sample)
            incl = [i] + nb
            dcols[i] = [np.mean(psi_half[incl]), np.mean(psi_n[incl]), np.mean(psi_double[incl])]
            av = area[nb] if nb else area[i:i+1]
            e[i] = [np.mean(av), np.var(av, ddof=0)]
        columns.extend(b[:, j] for j in range(4)); names.extend(f"s{s}_degree_{x}" for x in ("mean","var","skew","excess"))
        columns.extend(dcols[:, j] for j in range(3)); names.extend((f"s{s}_psi_half",f"s{s}_psi_n",f"s{s}_psi_double"))
        columns.extend(e[:, j] for j in range(2)); names.extend((f"s{s}_voronoi_mean",f"s{s}_voronoi_var"))
        matrix = np.column_stack(columns)
        expected = {2:11, 4:22, 8:35, 12:48, 16:61}[s]
        if matrix.shape != (n, expected):
            raise AssertionError("physical serialization width drift")
        result[s] = (matrix.copy(), tuple(names))
        last = s
    return result


@dataclass(frozen=True)
class DedupSchema:
    retained: tuple[int, ...]
    dropped: tuple[int, ...]
    matches: Mapping[int, tuple[int, ...]]
    pooled_hash: str


def build_dedup_schema(m3_blocks: Sequence[np.ndarray], physical_blocks: Sequence[np.ndarray]) -> DedupSchema:
    if len(m3_blocks) != 6 or len(physical_blocks) != 6:
        raise ConformanceError("dedup schema requires all six offsets")
    m3 = np.vstack(m3_blocks); phys = np.vstack(physical_blocks)
    if len(m3) != len(phys) or not np.isfinite(m3).all() or not np.isfinite(phys).all():
        raise ConformanceError("dedup populations mismatch")
    matches: dict[int, tuple[int, ...]] = {}
    for j in range(phys.shape[1]):
        hit = tuple(k for k in range(m3.shape[1]) if np.max(np.abs(phys[:, j] - m3[:, k])) < 1e-12)
        if hit: matches[j] = hit
    retained = tuple(j for j in range(phys.shape[1]) if j not in matches)
    payload = np.ascontiguousarray(np.column_stack((m3, phys))).view(np.uint8)
    return DedupSchema(retained, tuple(matches), matches, sha256(payload).hexdigest())


def apply_dedup(schema: DedupSchema, m3: np.ndarray, physical: np.ndarray) -> np.ndarray:
    return np.column_stack((m3, physical[:, schema.retained]))
