from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from hashlib import blake2b, sha256
import json
from typing import Iterable

import numpy as np

from .constants import CAPACITY_DRAWS, CAPACITY_PATCH_AXIS
from .errors import ConformanceError

SHUFFLE_PERSON = b"GIV-SHUFFLE-v1"
ADDRESS_PERSON = b"GIV-ADDRPERM-v1"


def _integer_motif(value):
    if isinstance(value, (tuple, list)):
        return [_integer_motif(x) for x in value]
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ConformanceError("motif JSON contains non-integer content")
    return int(value)


def canonical_json(fields: Iterable[tuple[str, object]]) -> bytes:
    obj = OrderedDict(fields)
    try:
        return json.dumps(obj, ensure_ascii=True, allow_nan=False, separators=(",", ":"),
                          sort_keys=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ConformanceError("noncanonical RNG identity") from exc


def digest_words(payload: bytes, person: bytes) -> tuple[int, int, bytes]:
    digest = blake2b(payload, digest_size=8, person=person).digest()
    return int.from_bytes(digest[:4], "big"), int.from_bytes(digest[4:], "big"), digest


def shuffle_key(family: str, tier: str, extent: int, offset_index: int) -> bytes:
    _validate_config(family, tier, extent, offset_index)
    return canonical_json((("family",family),("tier",tier),("extent",extent),("offset_index",offset_index)))


def address_key(family: str, tier: str, extent: int, offset_index: int, motif) -> bytes:
    _validate_config(family, tier, extent, offset_index)
    return canonical_json((("family",family),("tier",tier),("extent",extent),
                           ("offset_index",offset_index),("motif",_integer_motif(motif))))


def _validate_config(family, tier, extent, offset_index) -> None:
    if family not in ("silver","golden","platinum") or tier not in ("small","medium","large"):
        raise ConformanceError("invalid canonical family/tier")
    if isinstance(extent, bool) or not isinstance(extent, int) or isinstance(offset_index, bool) or not isinstance(offset_index, int) or offset_index not in range(6):
        raise ConformanceError("invalid canonical extent/offset")


def shuffle_rng(family: str, tier: str, extent: int, offset_index: int) -> np.random.Generator:
    u0,u1,_ = digest_words(shuffle_key(family,tier,extent,offset_index), SHUFFLE_PERSON)
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(20260901, spawn_key=(u0,u1))))


def address_rng(family: str, tier: str, extent: int, offset_index: int, motif, repetition: int) -> np.random.Generator:
    if repetition not in range(1000): raise ConformanceError("address repetition outside 0..999")
    u0,u1,_ = digest_words(address_key(family,tier,extent,offset_index,motif), ADDRESS_PERSON)
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(20260829, spawn_key=(u0,u1,repetition))))


@dataclass(frozen=True)
class CapacityField:
    draw_index: int
    patch_child_index: int
    values: np.ndarray
    sha256: str


class CapacityRegistry:
    def __init__(self) -> None:
        self._draw_children = np.random.SeedSequence(20260830).spawn(CAPACITY_DRAWS)
        self._patch_children = tuple(tuple(child.spawn(54)) for child in self._draw_children)
        self._cache: dict[tuple[int,int,int], CapacityField] = {}

    def field(self, draw: int, patch_child: int, n_vertices: int) -> CapacityField:
        if draw not in range(200) or patch_child not in range(54) or n_vertices <= 0:
            raise ConformanceError("invalid capacity identity")
        key = (draw, patch_child, n_vertices)
        if key not in self._cache:
            rng = np.random.Generator(np.random.PCG64(self._patch_children[draw][patch_child]))
            values = np.ascontiguousarray(rng.standard_normal((n_vertices,11), dtype=np.float64))
            self._cache[key] = CapacityField(draw, patch_child, values,
                                             sha256(values.view(np.uint8)).hexdigest())
        return self._cache[key]

    @property
    def axis(self): return CAPACITY_PATCH_AXIS


def golden_vectors() -> dict[str, object]:
    vectors = {}
    for name, key, person in (
        ("shuffle", shuffle_key("silver","small",14,0), SHUFFLE_PERSON),
        ("address", address_key("golden","large",22,5,((0,1),(3,-1))), ADDRESS_PERSON)):
        u0,u1,d = digest_words(key, person)
        vectors[name] = {"json_utf8_hex":key.hex(),"digest_hex":d.hex(),"u0":u0,"u1":u1}
    vectors["address_uniform_b"] = {str(b): address_rng("golden","large",22,5,((0,1),(3,-1)),b).random(8).tolist() for b in (0,1,999)}
    cap = CapacityRegistry()
    vectors["capacity_standard_normal"] = {
        f"{d}:{p}": cap.field(d,p,3).values.tolist() for d,p in ((0,0),(0,53),(199,0),(199,53))}
    return vectors
