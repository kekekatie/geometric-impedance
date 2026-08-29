#!/usr/bin/env python3
"""
ENGINEERING benchmark for the MSD endpoint (Work-GPT/Sol authorised, implementation only).

STRICTLY synthetic: random sparse graphs matched ONLY in vertex count n and degree range to the
planned patches. NO tiling/cut-and-project geometry, NO perpendicular-space address, NO scientific
outcome, NO beta, NO family comparison. It measures propagation cost only, to propose a feasible
frozen launch count L and algorithm.

Compares: exact dense diagonalisation vs sparse Krylov (scipy expm_multiply); coherent
(e^{-iHt}) vs CTMC (e^{Qt}); launch-batch sizes. Records wall time, peak RSS, numerical tolerance
(Krylov vs exact on a small graph), and a projected total over the planned 9 tiers x 6 offsets.
"""
import time, resource, sys
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import expm_multiply

RNG = np.random.default_rng(0)
N_LIST = [2000, 4000, 6000]      # brackets the planned patch sizes (~1.8k-8k)
MEAN_DEG = 4                     # rank-4 tilings have mean degree ~4
T_LO, T_HI, N_T = 2.0, 8.0, 48   # the frozen beta-fit grid
N_PATCHES = 9 * 6                # 9 tiers x 6 offsets, for the projection


def peak_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0  # KB->MB (Linux)


def rand_graph(n, mean_deg=MEAN_DEG):
    """Random sparse symmetric 0/1 adjacency, ~mean_deg per row. NOT a tiling."""
    m = n * mean_deg // 2
    i = RNG.integers(0, n, m); j = RNG.integers(0, n, m)
    keep = i != j
    i, j = i[keep], j[keep]
    A = sp.coo_matrix((np.ones(len(i)), (i, j)), shape=(n, n)).tocsr()
    A = ((A + A.T) > 0).astype(float)
    return A


def ctmc_gen(A):
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
    return (A.multiply(1.0 / deg[None, :])).tocsr() - sp.identity(A.shape[0], format="csr")


def bench_krylov(M, X, complex_op=False):
    A = (-1j * M) if complex_op else M
    t0 = time.perf_counter()
    Y = expm_multiply(A, X, start=T_LO, stop=T_HI, num=N_T, endpoint=True)
    return time.perf_counter() - t0, Y.shape


def bench_exact(A):
    n = A.shape[0]
    Ad = A.toarray()
    t0 = time.perf_counter()
    ev, U = np.linalg.eigh(Ad)
    return time.perf_counter() - t0, ev, U


def numtol():
    """Krylov vs exact for e^{-iH*8}|v0> on a small graph."""
    n = 500; A = rand_graph(n); Ad = A.toarray()
    ev, U = np.linalg.eigh(Ad)
    v0 = np.zeros(n); v0[0] = 1.0
    exact = U @ (np.exp(-1j * ev * T_HI) * (U.T @ v0))
    kry = expm_multiply(-1j * T_HI * A, v0.astype(complex))
    return float(np.max(np.abs(exact - kry)))


def main():
    print("# ENGINEERING BENCHMARK (synthetic sparse graphs; no study geometry/dynamics/outcomes)")
    print(f"# grid: beta-fit [{T_LO},{T_HI}] x {N_T} pts; mean degree {MEAN_DEG}; "
          f"projection over {N_PATCHES} patches (9 tiers x 6 offsets)")
    tol = numtol()
    print(f"\nNumerical agreement (Krylov vs exact, e^-iH*8 v0, n=500): max abs diff = {tol:.2e}")

    print(f"\n{'n':>6} {'method':>22} {'L':>5} {'wall_s':>9} {'peakRSS_MB':>11}")
    per_patch_best = {}
    for n in N_LIST:
        A = rand_graph(n); Q = ctmc_gen(A)
        # exact diagonalisation (one-off per patch); reconstruction of MSD is O(n^2 L T) on top
        te, ev, U = bench_exact(A)
        print(f"{n:>6} {'exact eigh (dense)':>22} {'-':>5} {te:>9.2f} {peak_mb():>11.0f}")
        best = ("exact-eigh", te)
        for L in (50, 400):
            X = np.zeros((n, L));
            for c in range(L): X[RNG.integers(0, n), c] = 1.0
            tk, shp = bench_krylov(A, X.astype(complex), complex_op=True)
            print(f"{n:>6} {'Krylov coherent':>22} {L:>5} {tk:>9.2f} {peak_mb():>11.0f}")
            tq, _ = bench_krylov(Q, X, complex_op=False)
            print(f"{n:>6} {'Krylov CTMC':>22} {L:>5} {tq:>9.2f} {peak_mb():>11.0f}")
            if L == 400 and (tk + tq) < best[1] * 1e9:  # track krylov total for L=400
                best = ("krylov(L=400,coh+ctmc)", tk + tq)
        per_patch_best[n] = best
    print("\n# projected TOTAL cost over 9 tiers x 6 offsets (= 54 patches), per method, at largest n:")
    n = N_LIST[-1]
    A = rand_graph(n); Q = ctmc_gen(A)
    te, _, _ = bench_exact(A)
    X = np.zeros((n, 400))
    for c in range(400): X[RNG.integers(0, n), c] = 1.0
    tk, _ = bench_krylov(A, X.astype(complex), complex_op=True)
    tq, _ = bench_krylov(Q, X, complex_op=False)
    print(f"  exact eigh alone:            {te*N_PATCHES/60:.1f} min  (x{N_PATCHES}; excl. O(n^2 L T) reconstruction)")
    print(f"  Krylov coherent+CTMC L=400:  {(tk+tq)*N_PATCHES/60:.1f} min  (x{N_PATCHES}, full 48-pt grid, both engines)")
    print(f"\nPeak RSS overall: {peak_mb():.0f} MB")
    print("DONE_BENCH")


if __name__ == "__main__":
    main()
