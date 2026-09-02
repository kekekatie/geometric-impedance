from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import numpy as np
from scipy.linalg import expm
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm_multiply

from .errors import ConformanceError


@dataclass(frozen=True)
class CoherentHamiltonian:
    H: csc_matrix


@dataclass(frozen=True)
class ClassicalGenerator:
    Q: csc_matrix


def coherent_hamiltonian(adjacency: np.ndarray) -> CoherentHamiltonian:
    a=np.asarray(adjacency,dtype=np.float64)
    _validate_adjacency(a)
    return CoherentHamiltonian(csc_matrix(a))


def classical_generator(adjacency: np.ndarray) -> ClassicalGenerator:
    a=np.asarray(adjacency,dtype=np.float64); _validate_adjacency(a)
    degree=a.sum(axis=0)
    if np.any(degree <= 0): raise ConformanceError("zero-degree classical column")
    q=a/degree[None,:]-np.eye(len(a))
    if not np.allclose(q.sum(axis=0),0,atol=1e-15,rtol=0): raise ConformanceError("Q is not column conservative")
    return ClassicalGenerator(csc_matrix(q))


def _validate_adjacency(a):
    if a.ndim!=2 or a.shape[0]!=a.shape[1] or not np.isfinite(a).all() or not np.array_equal(a,a.T) or np.any(np.diag(a)!=0):
        raise ConformanceError("adjacency must be finite, symmetric and loop-free")


def coherent_slice(hamiltonian: CoherentHamiltonian, initial: np.ndarray, time: float) -> np.ndarray:
    if not isinstance(hamiltonian,CoherentHamiltonian): raise TypeError("coherent interface requires H=A")
    return expm_multiply((-1j*time)*hamiltonian.H, initial)


def classical_slice(generator: ClassicalGenerator, initial: np.ndarray, time: float) -> np.ndarray:
    if not isinstance(generator,ClassicalGenerator): raise TypeError("classical interface requires Q=A*D^-1-I")
    return expm_multiply(time*generator.Q, initial)


def exact_coherent_reference(H: np.ndarray, initial: np.ndarray, time: float) -> np.ndarray:
    return expm(-1j*time*np.asarray(H,dtype=np.float64)) @ initial


def exact_classical_reference(Q: np.ndarray, initial: np.ndarray, time: float) -> np.ndarray:
    return expm(time*np.asarray(Q,dtype=np.float64)) @ initial


@dataclass(frozen=True)
class ReducedPropagation:
    msd: np.ndarray
    strip_mass: np.ndarray
    max_conservation_error: float
    min_probability: float | None


def stream_reduce(generator: CoherentHamiltonian | ClassicalGenerator, launch_indices: Iterable[int],
                  times: Iterable[float], par: np.ndarray, strip_mask: np.ndarray,
                  batch_size: int=50) -> ReducedPropagation:
    launches=tuple(int(x) for x in launch_indices); t=tuple(float(x) for x in times)
    n=len(par)
    if len(set(launches))!=len(launches) or any(x not in range(n) for x in launches) or batch_size<=0:
        raise ConformanceError("invalid launch batch")
    msd=np.empty((len(launches),len(t))); strip=np.empty_like(msd); maxerr=0.0; minprob=np.inf
    for start in range(0,len(launches),batch_size):
        batch=launches[start:start+batch_size]
        initial=np.zeros((n,len(batch)),dtype=np.complex128 if isinstance(generator,CoherentHamiltonian) else np.float64)
        initial[batch,np.arange(len(batch))]=1
        for ti,time in enumerate(t):
            state=coherent_slice(generator,initial,time) if isinstance(generator,CoherentHamiltonian) else classical_slice(generator,initial,time)
            probability=np.abs(state)**2 if isinstance(generator,CoherentHamiltonian) else np.asarray(state).real
            total=probability.sum(axis=0); maxerr=max(maxerr,float(np.max(np.abs(total-1))))
            if isinstance(generator,ClassicalGenerator): minprob=min(minprob,float(probability.min()))
            for j,origin in enumerate(batch):
                d2=np.sum((par-par[origin])**2,axis=1)
                msd[start+j,ti]=probability[:,j]@d2
                strip[start+j,ti]=probability[strip_mask,j].sum()
    if maxerr>1e-8 or (isinstance(generator,ClassicalGenerator) and minprob < -1e-10):
        raise ConformanceError("propagation conservation tolerance breached")
    return ReducedPropagation(msd,strip,maxerr,None if np.isinf(minprob) else minprob)
