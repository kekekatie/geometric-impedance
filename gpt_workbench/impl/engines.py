"""
Coherent and classical propagation engines (MSD_ENDPOINT_MANIFEST_DRAFT.md v8.1 §3-§6, §10).

Coherent:  H = A (tiling adjacency), |psi0> = |v0>, psi(t)=exp(-iHt)|v0>, MSD = sum|psi_v|^2 r_v^2.
Classical: the SPECIFIED degree-normalised CTMC Q = A D^-1 - I, p(t)=exp(Qt)e_v0, MSD = sum p_v r_v^2.
Both on the frozen 161-point boundary grid; beta from OLS of log MSD on log t over the 48 snapped times.
No study substrates are propagated here; the synthetic test-suite drives these on tiny graphs.
"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import expm_multiply
from . import constants as C


def adjacency(n, edges):
    A = sp.lil_matrix((n, n))
    for i, j in edges:
        A[i, j] = 1.0; A[j, i] = 1.0
    return A.tocsr()


def ctmc_generator(A):
    """Q = A D^-1 - I (column-stochastic: columns sum to 0; unit exit rate; stationary pi ~ deg)."""
    deg = np.asarray(A.sum(1)).ravel()
    Dinv = sp.diags(1.0 / np.where(deg > 0, deg, 1.0))
    return (A @ Dinv) - sp.identity(A.shape[0])


def _states_on_grid(op, v0, n, grid=C.BOUNDARY_GRID):
    """exp(op * t) e_v0 for t on the linear grid (grid must start at 0)."""
    e = np.zeros(n); e[v0] = 1.0
    assert grid[0] == 0.0
    return expm_multiply(op, e, start=float(grid[0]), stop=float(grid[-1]),
                         num=len(grid), endpoint=True)


def coherent_states(A, v0, grid=C.BOUNDARY_GRID):
    """psi(t) = exp(-iAt)|v0> on the grid -> (T, n) complex."""
    return _states_on_grid((-1j) * A, v0, A.shape[0], grid)


def classical_states(Q, v0, grid=C.BOUNDARY_GRID):
    """p(t) = exp(Qt) e_v0 on the grid -> (T, n) real."""
    return _states_on_grid(Q, v0, Q.shape[0], grid)


def coherent_exact(A, v0, times):
    """Exact-diagonalisation reference (dense) for synthetic validation of the Krylov engine."""
    Ad = A.toarray() if sp.issparse(A) else np.asarray(A, float)
    w, V = np.linalg.eigh(Ad)
    n = Ad.shape[0]; e = np.zeros(n); e[v0] = 1.0
    c = V.T @ e
    return np.array([V @ (np.exp(-1j * w * t) * c) for t in times])


def msd_curve(states, par, v0, coherent=True):
    """MSD(t) = sum_v w_v(t) * ||par[v]-par[v0]||^2, w = |psi|^2 (coherent) or p (classical)."""
    r2 = np.sum((par - par[v0]) ** 2, axis=1)
    w = np.abs(states) ** 2 if coherent else np.real(states)
    return w @ r2


def strip_mass(states, strip_mask, coherent=True):
    """P_strip(t): coherent sum|psi|^2 over the strip, classical sum p over the strip."""
    w = np.abs(states) ** 2 if coherent else np.real(states)
    return w[:, strip_mask].sum(1)


def boundary_crossing_time(delta_pstrip, grid=C.BOUNDARY_GRID):
    """Earliest grid time (incl t=8) with dP_strip >= 0.01; np.inf if no crossing."""
    hit = np.where(delta_pstrip >= C.CROSS_THRESHOLD)[0]
    return float(grid[hit[0]]) if hit.size else np.inf


def beta_from_msd(msd_on_grid, grid=C.BOUNDARY_GRID, snapped=C.SNAPPED_BETA_TIMES):
    """beta = 0.5 * OLS slope of log MSD on log t over the 48 snapped [2,8] grid points; plus R^2."""
    idx = [int(np.argmin(np.abs(grid - t))) for t in snapped]
    t = grid[idx]; y = msd_on_grid[idx]
    good = y > 0
    lt = np.log(t[good]); ly = np.log(y[good])
    Xd = np.column_stack([lt, np.ones_like(lt)])
    coef, *_ = np.linalg.lstsq(Xd, ly, rcond=None)
    slope = coef[0]
    resid = ly - Xd @ coef
    ss_res = np.sum(resid ** 2); ss_tot = np.sum((ly - ly.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return 0.5 * slope, r2


def check_conservation(states, coherent=True):
    """Norm/probability conservation tolerances (MSD v8.1 §9)."""
    if coherent:
        norms = np.sum(np.abs(states) ** 2, axis=1)
        return bool(np.all(np.abs(norms - 1.0) <= C.NORM_CONS_TOL))
    p = np.real(states)
    return bool(np.all(np.abs(p.sum(1) - 1.0) <= C.NORM_CONS_TOL) and np.all(p >= C.PROB_NEG_TOL))
