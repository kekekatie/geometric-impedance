from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment

from .errors import ConformanceError, ReproducibilityFailure
from .features import Motif, address_operator
from .geometry import PatchGeometry
from .identity import LiftId
from .seed_registry import address_rng, shuffle_rng


def stable_degree_deciles(degree: np.ndarray) -> np.ndarray:
    degree = np.asarray(degree, dtype=np.float64)
    first = np.argsort(degree, kind="stable")
    rank = np.argsort(first, kind="stable")
    return np.clip(rank * 10 // len(degree), 0, 9)


def stratified_shuffle(patch: PatchGeometry, raw: np.ndarray, motifs: Sequence[Motif],
                       motif_registry: Sequence[Motif], family: str, tier: str,
                       extent: int) -> tuple[np.ndarray, np.ndarray]:
    if len(raw) != len(patch.lifts) or len(motifs) != len(raw):
        raise ConformanceError("shuffle rows mismatch")
    code = {m:i for i,m in enumerate(motif_registry)}
    if any(m not in code for m in motifs): raise ConformanceError("unseen motif")
    degree = np.asarray([len(a) for a in patch.adjacency])
    groups = [(code[m], int(d)) for m,d in zip(motifs, stable_degree_deciles(degree))]
    out = np.asarray(raw, dtype=np.float64).copy(); rng = shuffle_rng(family,tier,extent,patch.key.offset_index)
    permutation = np.arange(len(out))
    for group in sorted(set(groups)):
        members = sorted((i for i,g in enumerate(groups) if g == group), key=lambda i: patch.ids[i])
        if len(members) > 1:
            order = rng.permutation(len(members)); src = np.asarray(members); dest = src[order]
            out[src] = raw[dest]; permutation[src] = dest
    return out, permutation


@dataclass(frozen=True)
class AssignmentResult:
    destination_by_source: tuple[int, ...]
    escalation: int | str
    total_cost: float


def local_assignment(features: np.ndarray, lifts: Sequence[LiftId], family: str, tier: str,
                     extent: int, offset_index: int, motif: Motif, repetition: int,
                     candidate_sizes: tuple[int | str, ...] = (32,64,"full")) -> AssignmentResult:
    x = np.asarray(features, dtype=np.float64); n = len(x)
    if x.ndim != 2 or len(lifts) != n or n < 2 or not np.isfinite(x).all():
        raise ConformanceError("invalid local-assignment group")
    source_order = sorted(range(n), key=lambda i:lifts[i])
    distances = np.linalg.norm(x[:,None,:]-x[None,:,:], axis=2)
    rng = address_rng(family,tier,extent,offset_index,motif,repetition)
    # One fixed row-major full random matrix makes escalation independent of attempts.
    uniforms = rng.random((n,n), dtype=np.float64)
    for size in candidate_sizes:
        k = n-1 if size == "full" else min(int(size), n-1)
        cost = np.full((n,n), np.inf)
        for i in source_order:
            candidates = sorted((j for j in range(n) if j != i), key=lambda j:(distances[i,j],lifts[j]))[:k]
            cost[i,candidates] = distances[i,candidates] + uniforms[i,candidates]
        try:
            rows, cols = linear_sum_assignment(cost)
        except ValueError:
            continue
        if np.isfinite(cost[rows,cols]).all() and all(i != j for i,j in zip(rows,cols)):
            total = float(cost[rows,cols].sum())
            # Detect a second exactly tied complete assignment by excluding each selected edge.
            for i,j in zip(rows,cols):
                mutant=cost.copy(); mutant[i,j]=np.inf
                try:
                    rr,cc=linear_sum_assignment(mutant)
                except ValueError:
                    continue
                if np.isfinite(mutant[rr,cc]).all() and float(mutant[rr,cc].sum()) == total:
                    raise ReproducibilityFailure("equal complete assignment totals")
            mapping=np.empty(n,dtype=int); mapping[rows]=cols
            return AssignmentResult(tuple(int(v) for v in mapping), size, total)
    raise ConformanceError("no perfect derangement after full escalation")


def singleton_fraction(motifs: Sequence[Motif]) -> float:
    counts={m:motifs.count(m) for m in set(motifs)}
    return sum(counts[m] == 1 for m in motifs)/len(motifs)


def local_null_available(motifs: Sequence[Motif]) -> bool:
    return singleton_fraction(motifs) <= 0.05


def apply_assignment(raw: np.ndarray, assignment: AssignmentResult) -> np.ndarray:
    x=np.asarray(raw,dtype=np.float64)
    out=x[np.asarray(assignment.destination_by_source)]
    if out.shape != x.shape: raise ConformanceError("permuted population mismatch")
    return out


def position_control(m3: np.ndarray, patch: PatchGeometry, address11: np.ndarray):
    pos=np.column_stack((patch.par,np.hypot(patch.par[:,0],patch.par[:,1])))
    base=np.column_stack((m3,pos)); return base,np.column_stack((base,address11))


def far_control(m3: np.ndarray, far6: np.ndarray, address11: np.ndarray):
    if far6.shape != (len(m3),6): raise ConformanceError("far control must have six columns")
    base=np.column_stack((m3,far6)); return base,np.column_stack((base,address11))
