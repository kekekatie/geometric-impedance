from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import numpy as np

from .errors import ConformanceError
from .gates import Gate

MAXIMUM_CLAIM="The address representation predicts heterogeneity in full-spectrum wavepacket spreading beyond the frozen physical descriptions and controls."
FORBIDDEN=("perpendicular-space physics","irreducible","exchangeable-null significance","family ordering","isolation of coherence")


@dataclass(frozen=True)
class Route:
    physical: str
    coherent_claim: bool
    modifier: bool
    wording: str


def route(gates: Mapping[str,Gate], r2_folds: np.ndarray, r16: float, delta_cap: float) -> Route:
    r2=np.asarray(r2_folds,dtype=float)
    if r2.shape!=(6,) or not np.isfinite(r2).all() or not np.isfinite(r16): raise ConformanceError("route requires six r2 folds and finite r16")
    r2m=float(np.median(r2)); compression=False
    if r2m>0 and np.count_nonzero(r2>0)>=5 and r2m>delta_cap:
        compression=(r16<delta_cap and r16/r2m<.25)
    survives=all(gates[k].state=="pass" for k in ("G2","G3","G6"))
    physical="compression" if compression else "survives frozen stress controls" if survives else "mixed/undetectable"
    coherent=all(gates[k].state=="pass" for k in ("G0","G1_coherent","G2","G3","G4","G6"))
    modifier=coherent and gates["G1_classical"].state=="pass" and gates["G5"].state=="pass"
    wording=MAXIMUM_CLAIM if coherent else ("finite-size-limited" if gates["G0"].state=="fail" else "no surfaced spreading signal")
    validate_claim(wording)
    return Route(physical,coherent,modifier,wording)


def validate_claim(text: str) -> None:
    if any(x.lower() in text.lower() for x in FORBIDDEN): raise ConformanceError("claim exceeds sealed boundary")
