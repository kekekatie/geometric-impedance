from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal

import numpy as np

from .errors import ConformanceError

State=Literal["pass","fail","undefined","inconclusive","descriptive"]


@dataclass(frozen=True)
class Gate:
    name: str
    state: State
    value: float | None
    threshold: float | None
    margin: float | None


def threshold_gate(name,value,threshold,operator:Literal[">",">=","<","<="]) -> Gate:
    if not np.isfinite(value): raise ConformanceError(f"nonfinite {name}")
    ops={">":value>threshold,">=":value>=threshold,"<":value<threshold,"<=":value<=threshold}
    margin=float(value-threshold) if operator in (">",">=") else float(threshold-value)
    return Gate(name,"pass" if ops[operator] else "fail",float(value),float(threshold),margin)


def evaluate_gates(t_bound: float, coherent_g1_cells, classical_g1_cells, qref_value: float,
                   coherent_address: float, classical_address: float, delta_cap: float,
                   plain: np.ndarray, shuffled: np.ndarray, residual: float,
                   parity: float) -> dict[str,Gate]:
    if len(coherent_g1_cells)!=9 or len(classical_g1_cells)!=9: raise ConformanceError("G1 requires all nine cells")
    g={"G0":Gate("G0","pass" if t_bound>8 else "fail",t_bound,8.0,t_bound-8)}
    coh=all(float(x)>=.90 for x in coherent_g1_cells); cla=all(float(x)>=.90 for x in classical_g1_cells)
    g["G1_coherent"]=Gate("G1_coherent","pass" if coh else "fail",float(min(coherent_g1_cells)),.90,float(min(coherent_g1_cells)-.90))
    g["G1_classical"]=Gate("G1_classical","pass" if cla else "fail",float(min(classical_g1_cells)),.90,float(min(classical_g1_cells)-.90))
    g["G2"]=threshold_gate("G2",qref_value,.05,"<")
    g["G3"]=threshold_gate("G3",coherent_address,delta_cap,">")
    p=np.asarray(plain,dtype=float); s=np.asarray(shuffled,dtype=float)
    if p.shape!=(9,6) or s.shape!=(9,6): raise ConformanceError("G4 requires labelled 9×6 paired values")
    if np.any(p<=delta_cap) or np.any(p<=0): g["G4"]=Gate("G4","undefined",None,.70,None)
    else:
        kill=float(np.median(np.median((p-s)/p,axis=0)))
        g["G4"]=threshold_gate("G4",kill,.70,">=")
    if coherent_address<=delta_cap or coherent_address<=0: g["G5"]=Gate("G5","undefined",None,.2,None)
    elif not cla: g["G5"]=Gate("G5","inconclusive",None,.2,None)
    else: g["G5"]=threshold_gate("G5",classical_address/coherent_address,.2,"<=")
    g["G6"]=threshold_gate("G6",residual,delta_cap,">")
    g["G7"]=Gate("G7","descriptive",coherent_address-parity,None,None)
    g["G8"]=Gate("G8","descriptive",None,None,None)
    return g
