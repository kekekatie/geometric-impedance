from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

import numpy as np

from .errors import ConformanceError, LeakageError

LiftId = tuple[int, ...]


@dataclass(frozen=True, order=True)
class PatchKey:
    config_id: int
    offset_index: int

    def __post_init__(self) -> None:
        if not 0 <= self.config_id < 9 or not 0 <= self.offset_index < 6:
            raise ConformanceError("PatchKey outside frozen axes")


@dataclass(frozen=True, order=True)
class RowId:
    patch: PatchKey
    lift: LiftId


def lift_ids(lifts: np.ndarray) -> tuple[LiftId, ...]:
    a = np.asarray(lifts)
    if a.ndim != 2 or not np.issubdtype(a.dtype, np.integer):
        raise ConformanceError("lifts must be a two-dimensional integer array")
    ids = tuple(tuple(int(v) for v in row) for row in a)
    if len(set(ids)) != len(ids):
        raise ConformanceError("duplicate LiftId")
    return ids


def identity_hash(ids: Iterable[object]) -> str:
    payload = json.dumps(list(ids), separators=(",", ":"), ensure_ascii=True,
                         allow_nan=False).encode("utf-8")
    return sha256(payload).hexdigest()


@dataclass(frozen=True)
class FitProvenance:
    patch_keys: frozenset[PatchKey]
    row_ids: frozenset[RowId]
    outer_fold: int
    inner_fold: int | None
    schema_hash: str

    def reject_held_out(self, patch_keys: Iterable[PatchKey], rows: Iterable[RowId]) -> None:
        if self.patch_keys.intersection(patch_keys) or self.row_ids.intersection(rows):
            raise LeakageError("held-out identity present in fit provenance")
