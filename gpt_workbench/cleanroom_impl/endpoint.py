from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .constants import BOUNDARY_TIMES, FIT_TIMES
from .errors import ConformanceError


@dataclass(frozen=True)
class BetaEndpoint:
    valid: bool
    beta: np.ndarray | None
    r2_fit: np.ndarray | None
    reason: str | None


def boundary_crossing(strip_mass: np.ndarray, times=BOUNDARY_TIMES) -> float:
    x=np.asarray(strip_mass,dtype=np.float64)
    if x.ndim!=2 or x.shape[1]!=len(times) or not np.isfinite(x).all():
        raise ConformanceError("invalid boundary scan input")
    excess=x-x[:,[0]]
    hit=np.argwhere(excess>=0.01)
    return math.inf if len(hit)==0 else float(times[int(hit[np.argmin(hit[:,1]),1])])


def beta_fit(msd: np.ndarray, times=FIT_TIMES) -> BetaEndpoint:
    y=np.asarray(msd,dtype=np.float64); t=np.asarray(times,dtype=np.float64)
    if y.ndim!=2 or y.shape[1]!=48 or t.shape!=(48,): raise ConformanceError("beta requires all 48 fit times")
    if not np.isfinite(y).all(): return BetaEndpoint(False,None,None,"nonfinite MSD")
    if np.any(y<=0): return BetaEndpoint(False,None,None,"nonpositive MSD")
    lx=np.log(t); xc=lx-lx.mean(); denom=float(xc@xc)
    beta=np.empty(len(y)); r2=np.empty(len(y))
    for i,row in enumerate(y):
        ly=np.log(row); yc=ly-ly.mean(); slope=float(xc@yc/denom); predicted=ly.mean()+slope*xc
        sst=float(yc@yc); sse=float(np.sum((ly-predicted)**2))
        beta[i]=0.5*slope; r2[i]=1.0-sse/sst if sst>0 else 1.0
    return BetaEndpoint(True,beta,r2,None)


def admission_smd(admitted: np.ndarray, excluded: np.ndarray) -> float:
    a=np.asarray(admitted,dtype=np.float64); b=np.asarray(excluded,dtype=np.float64)
    if not len(a) or not len(b) or not np.isfinite(a).all() or not np.isfinite(b).all(): raise ConformanceError("invalid SMD groups")
    delta=float(a.mean()-b.mean()); pooled=float(np.sqrt((a.var(ddof=0)+b.var(ddof=0))/2))
    if pooled<1e-12:
        return 0.0 if abs(delta)<=1e-12 else math.copysign(math.inf,delta)
    return delta/pooled
