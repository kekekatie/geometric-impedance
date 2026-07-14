#!/usr/bin/env python3
"""
Stage D (winding staircase) — the real experiment. Emergent Kuramoto oscillators
on the substrate's own torus graph; natural frequencies from vertex depth;
measure the synchronisation onset K* up the approximant ladder, both substrates.

Governed by STAGE_D_IMPLEMENTATION_PREREG.md (sealed). This module builds the
machinery; measurements are run by the driver at the bottom. See the prereg for
every pinned choice (RK4 dt=0.05, transient/avg 200/200, r_c=0.5, standardised
frequencies primary, torus topology, canary F, etc.).
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reverse_loop_test"))
sys.path.insert(0, str(Path(__file__).parent.parent / "defect_holonomy_test"))
import numpy as np
from scipy.spatial import cKDTree
from geometry import Patch, star_vectors, SUBSTRATES

REG = json.load(open(Path(__file__).parent.parent /
                     "defect_holonomy_test" / "phase0_registration.json"))
TWO_PI = 2.0 * np.pi


# --------------------------------------------------------------------------- #
# Substrate torus graph (nodes = vertices, edges = native tiling edges)
# --------------------------------------------------------------------------- #
def class_preserving_basis(M_a, M_b, N, par_star, span=10):
    sa, sb = int(M_a.sum()) % N, int(M_b.sum()) % N
    cands = []
    for a in range(-span, span + 1):
        for b in range(-span, span + 1):
            if a == 0 and b == 0:
                continue
            if (a * sa + b * sb) % N == 0:
                m = a * M_a + b * M_b
                cands.append((float(np.linalg.norm(m @ par_star)), a, b, m))
    cands.sort(key=lambda t: t[0])
    a0 = b0 = None
    basis = []
    for _, a, b, m in cands:
        if not basis:
            a0, b0 = a, b
            basis.append(m)
        elif a0 * b - b0 * a != 0:
            basis.append(m)
            break
    return basis


def torus_graph(substrate, order_index, supercell=1, wrap_tol=0.25):
    """Return (depth[N], edges_i[E], edges_j[E], N) for the approximant torus.
    Penrose wraps by the class-preserving x5 cell; AB by the naive cell. supercell
    n gives an n x n larger torus (same tiling) for the finite-size canary F."""
    cfg = SUBSTRATES[substrate]
    N = cfg["N"]
    par_star, perp_star = star_vectors(N, cfg["par_step"], cfg["perp_step"])
    o = REG[substrate]["orders"][order_index]
    M_a, M_b = np.array(o["M_a"]), np.array(o["M_b"])
    if substrate == "penrose":
        g1, g2 = class_preserving_basis(M_a, M_b, N, par_star)
    else:
        g1, g2 = M_a, M_b
    g1, g2 = supercell * g1, supercell * g2
    P1, P2 = g1 @ par_star, g2 @ par_star
    Mcell = np.array([P1, P2]).T
    Minv = np.linalg.inv(Mcell)
    side = max(np.linalg.norm(P1), np.linalg.norm(P2))
    radius = 1.35 * side + 6.0
    pt = Patch(substrate, radius=radius)
    K, par = pt.K, pt.par
    frac = (Minv @ par.T).T
    incell = np.all((frac >= -1e-9) & (frac < 1 - 1e-9), axis=1)
    cell = np.where(incell)[0]
    local = {int(c): i for i, c in enumerate(cell)}
    tree = cKDTree(par[cell])
    lift_of = {tuple(K[i]): i for i in range(pt.n)}
    eye = np.eye(N, dtype=int)
    ei, ej = [], []
    seen = set()
    for c in cell:
        for j in range(N):
            for s in (1, -1):
                gi = lift_of.get(tuple(K[c] + s * eye[j]))
                if gi is None:
                    continue
                fp = Minv @ par[gi]
                wrapped = par[gi] - Mcell @ np.floor(fp + 1e-9)
                d, idx = tree.query(wrapped)
                if d > wrap_tol:
                    continue
                a, b = local[int(c)], int(idx)
                key = (min(a, b), max(a, b))
                if a != b and key not in seen:
                    seen.add(key)
                    ei.append(key[0]); ej.append(key[1])
    depth = pt.depth[cell].astype(float)
    return depth, np.array(ei), np.array(ej), len(cell)


# --------------------------------------------------------------------------- #
# Kuramoto dynamics (prereg §1): RK4, unnormalised native-edge coupling
# --------------------------------------------------------------------------- #
def _dtheta(theta, omega, ei, ej, K, N):
    s = np.sin(theta[ej] - theta[ei])            # per-edge
    coup = np.bincount(ei, weights=s, minlength=N) - np.bincount(ej, weights=s, minlength=N)
    return omega + K * coup


def steady_r(omega, ei, ej, K, dt=0.05, T_trans=200.0, T_avg=200.0, seed=0):
    """Time-averaged global order parameter r at coupling K."""
    N = len(omega)
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, TWO_PI, N)
    nt, na = int(T_trans / dt), int(T_avg / dt)
    def step(th):
        k1 = _dtheta(th, omega, ei, ej, K, N)
        k2 = _dtheta(th + 0.5 * dt * k1, omega, ei, ej, K, N)
        k3 = _dtheta(th + 0.5 * dt * k2, omega, ei, ej, K, N)
        k4 = _dtheta(th + dt * k3, omega, ei, ej, K, N)
        return th + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    for _ in range(nt):
        theta = step(theta)
    acc = 0.0
    for _ in range(na):
        theta = step(theta)
        acc += abs(np.mean(np.exp(1j * theta)))
    return acc / na


def frequencies(depth, standardise=True):
    if standardise:
        return (depth - depth.mean()) / depth.std()
    return depth - depth.mean()


def find_Kstar(omega, ei, ej, r_c=0.5, seeds=(1, 2, 3), T_trans=200.0, T_avg=200.0,
               coarse=(0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0, 1.3, 1.7), n_bisect=7):
    """K* = coupling where steady-state r first crosses r_c (prereg §4). Coarse
    grid to bracket the crossing, then bisection; linear-interpolated crossing.
    r is averaged over several random initial conditions (`seeds`) to damp the
    finite-network multistability."""
    def R(K):
        return float(np.mean([steady_r(omega, ei, ej, K, T_trans=T_trans,
                                       T_avg=T_avg, seed=s) for s in seeds]))
    grid = list(coarse)
    rs = [R(K) for K in grid]
    lo = hi = None
    for i in range(len(grid) - 1):
        if rs[i] < r_c <= rs[i + 1]:
            lo, hi, rlo, rhi = grid[i], grid[i + 1], rs[i], rs[i + 1]
            break
    if lo is None:                       # never crosses within grid
        if rs[-1] < r_c:
            return float("nan"), list(zip(grid, rs))
        lo, hi, rlo, rhi = grid[0], grid[0], rs[0], rs[0]
    for _ in range(n_bisect):
        mid = 0.5 * (lo + hi)
        rm = R(mid)
        if rm < r_c:
            lo, rlo = mid, rm
        else:
            hi, rhi = mid, rm
    frac = (r_c - rlo) / (rhi - rlo) if rhi > rlo else 0.5
    return lo + frac * (hi - lo), list(zip(grid, rs))


# --------------------------------------------------------------------------- #
# Engine validation (NOT the pre-registered run): one config, coarse K sweep
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print("Stage D engine validation (one config, coarse sweep — not the real run)\n")
    depth, ei, ej, N = torus_graph("penrose", 1, supercell=1)
    print(f"penrose order 2 torus: N={N} vertices, E={len(ei)} edges, "
          f"mean degree {2*len(ei)/N:.2f}")
    omega = frequencies(depth, standardise=True)
    print(f"standardised omega: mean={omega.mean():.2e} std={omega.std():.3f}\n")
    print(f"  {'K':>5}  {'r(steady)':>10}")
    for K in [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8]:
        r = steady_r(omega, ei, ej, K, T_trans=80, T_avg=80, seed=1)
        print(f"  {K:>5.2f}  {r:>10.3f}")
