#!/usr/bin/env python3
"""
ENGINEERING benchmark v2 — ACTUAL combined workload (Work-GPT/Sol authorised, implementation only).
STRICTLY synthetic sparse graphs matched only in n and degree range. NO study geometry, tiling,
address, distances, LDOS, beta, targets, or scientific outcome. Positions/weights below are random
placeholders solely to exercise the O(n) reduction cost (which is position-independent).

Combined production workload: L=200 launches, 161 linear boundary times on [0,8] (dt=0.05), 48 log
beta times on [2,8], coherent + CTMC engines, launch-batching, reduce-on-the-fly (no T x V x L
tensor kept). Tests whether the 161-grid propagation SUBSUMES the beta grid (shared work) and
whether L=200/dt=0.05 remain practical.
"""
import time, resource, sys
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import expm_multiply

RNG = np.random.default_rng(0)
L, BATCH = 200, 50
BND = np.linspace(0.0, 8.0, 161)          # boundary-monitoring grid, dt=0.05
BETA = np.logspace(np.log10(2.0), np.log10(8.0), 48)   # beta-fit log grid on [2,8]


def peak_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def rand_graph(n, mean_deg=4):
    m = n * mean_deg // 2
    i = RNG.integers(0, n, m); j = RNG.integers(0, n, m)
    k = i != j; i, j = i[k], j[k]
    A = sp.coo_matrix((np.ones(len(i)), (i, j)), shape=(n, n)).tocsr()
    return ((A + A.T) > 0).astype(float)


def ctmc(A):
    d = np.asarray(A.sum(1)).ravel(); d[d == 0] = 1
    return A.multiply(1.0 / d[None, :]).tocsr() - sp.identity(A.shape[0], format="csr")


def reduce_batch(op, X, times, w, strip_mask):
    """expm_multiply on a uniform grid, reduce each time-slice to scalars, discard the slice."""
    Y = expm_multiply(op, X, start=times[0], stop=times[-1], num=len(times), endpoint=True)
    prob = (Y.real**2 + Y.imag**2)                      # (T, n, Lb)
    msd = np.einsum('v,tvl->tl', w, prob)               # weighted reduce (placeholder weight)
    pstr = prob[:, strip_mask, :].sum(1)                # strip-mass reduce
    return msd, pstr


def run_engine(op, n, complexop):
    w = RNG.random(n); strip = np.zeros(n, bool); strip[RNG.choice(n, n // 10, replace=False)] = True
    t0 = time.perf_counter()
    for b0 in range(0, L, BATCH):
        Lb = min(BATCH, L - b0)
        X = np.zeros((n, Lb), complex if complexop else float)
        for c in range(Lb):
            X[RNG.integers(0, n), c] = 1.0
        A = (-1j * op) if complexop else op
        reduce_batch(A, X, BND, w, strip)               # 161-grid: boundary + (its [2,8] subset -> beta)
    return time.perf_counter() - t0


def run_separate_beta(op, n, complexop):
    """Cost of ALSO propagating the 48 log beta points separately (non-uniform => per-time calls)."""
    X = np.zeros((n, BATCH), complex if complexop else float)
    for c in range(BATCH):
        X[RNG.integers(0, n), c] = 1.0
    A = (-1j * op) if complexop else op
    t0 = time.perf_counter()
    for t in BETA[:8]:                                  # sample 8 of 48 to project cost
        expm_multiply(t * A, X)
    return (time.perf_counter() - t0) * (48 / 8) * (L / BATCH)


def numtol(n=500):
    A = rand_graph(n); Ad = A.toarray(); ev, U = np.linalg.eigh(Ad)
    v0 = np.zeros(n); v0[0] = 1.0
    exact = U @ (np.exp(-1j * ev * 8.0) * (U.T @ v0))
    kry = expm_multiply(-1j * 8.0 * A, v0.astype(complex))
    return float(np.max(np.abs(exact - kry)))


def main():
    print("# ACTUAL-GRID BENCHMARK (synthetic; no study geometry/dynamics/outcomes)")
    print(f"# L={L} batch={BATCH} | boundary 161 lin [0,8] dt=0.05 | beta 48 log [2,8] | reduce-on-fly")
    print(f"\nnumerical agreement (Krylov vs exact, t=8, n=500): {numtol():.2e}")
    NS = [4000, 6000]
    print(f"\n{'n':>6} {'engine':>10} {'shared161_s':>12} {'sep_beta_s':>11} {'peakRSS_MB':>11}")
    tot = {}
    for n in NS:
        A = rand_graph(n); Q = ctmc(A)
        tc = run_engine(A, n, True); sc = run_separate_beta(A, n, True)
        print(f"{n:>6} {'coherent':>10} {tc:>12.1f} {sc:>11.1f} {peak_mb():>11.0f}")
        tq = run_engine(Q, n, False); sq = run_separate_beta(Q, n, False)
        print(f"{n:>6} {'CTMC':>10} {tq:>12.1f} {sq:>11.1f} {peak_mb():>11.0f}")
        tot[n] = (tc + tq, sc + sq)
    n = NS[-1]
    shared, sep = tot[n]
    print(f"\n# at n={n}, per patch (both engines): shared-161 grid = {shared:.1f}s; "
          f"separate 48-log beta would ADD {sep:.1f}s")
    print(f"# projected over 54 patches, shared-grid only: {shared*54/60:.1f} min")
    print(f"# projected if beta computed separately too:   {(shared+sep)*54/60:.1f} min")
    print(f"peak RSS overall: {peak_mb():.0f} MB")
    print("DONE_GRID")


if __name__ == "__main__":
    main()
