"""
Frozen physical-radius feature pipeline (PHYSICAL_RADIUS_MANIFEST_DRAFT.md v7 §2/§3).

Pure functions over explicit geometry arrays so every component is independently testable on
synthetic fixtures. No study dynamics, no address-as-outcome, no LDOS/beta.
"""
import numpy as np
from scipy.spatial import cKDTree, Voronoi
from . import constants as C


# ---- moment conventions (physical v7 §1) --------------------------------------------------------
def moments(x):
    """(mean, var[ddof=0], skewness, excess kurtosis). If sigma < 1e-9, higher moments = 0."""
    x = np.asarray(x, float)
    mu = x.mean(); var = x.var()  # population variance, ddof=0
    sig = np.sqrt(var)
    if sig < C.MOMENT_SIGMA_FLOOR:
        return mu, var, 0.0, 0.0
    z = (x - mu)
    skew = np.mean(z ** 3) / sig ** 3
    exkurt = np.mean(z ** 4) / sig ** 4 - 3.0
    return mu, var, skew, exkurt


def gcount(tree, par, radius):
    """Vertex counts within Euclidean radius (dens = gcount(2.0))."""
    return np.array(tree.query_ball_point(par, radius, return_length=True), float)


def psi_n(adj, par, n):
    """psi_n(i) = |mean over incident bonds of exp(i n theta)|."""
    out = np.zeros(len(par))
    for i, nb in enumerate(adj):
        if nb:
            a = np.array(nb)
            th = np.arctan2(par[a, 1] - par[i, 1], par[a, 0] - par[i, 0])
            out[i] = abs(np.mean(np.exp(1j * n * th)))
    return out


def voronoi_areas(points):
    """Bounded Voronoi cell area per input point; np.nan for unbounded/censored cells.
    In production the caller passes a PADDED super-patch (physical v7 §3a) and restricts to core."""
    from scipy.spatial import ConvexHull
    vor = Voronoi(points)
    areas = np.full(len(points), np.nan)
    for p, reg_idx in enumerate(vor.point_region):
        reg = vor.regions[reg_idx]
        if len(reg) == 0 or -1 in reg:
            continue
        poly = vor.vertices[reg]
        areas[p] = ConvexHull(poly).volume  # 2-D "volume" = area
    return areas


# ---- neighbourhoods -----------------------------------------------------------------------------
def neighbourhoods(tree, par, s, ell):
    """Nb(i,s) = {j != i : ||par[j]-par[i]|| <= s*ell}."""
    balls = tree.query_ball_point(par, s * ell)
    return [np.array([j for j in b if j != i], int) for i, b in enumerate(balls)]


# ---- Group A: radial histogram g(rho), right-closed bins (physical v7 §3 Group A) ---------------
def group_A(tree, par, ell, r):
    """phys_gann_k = #{j!=i : bin(j)=k}, bin k = ceil(d/ell - tau), k=1..r. Returns (n, r)."""
    n = len(par)
    out = np.zeros((n, r))
    balls = tree.query_ball_point(par, r * ell + 1e-9)
    for i, b in enumerate(balls):
        for j in b:
            if j == i:
                continue
            d = np.linalg.norm(par[j] - par[i])
            k = int(np.ceil(d / ell - C.BIN_TAU))
            if 1 <= k <= r:
                out[i, k - 1] += 1
    return out


# ---- Group B: neighbour-degree moments per s (physical v7 §3 Group B) ---------------------------
def group_B(nbs_by_s, deg, S_r):
    """For each s: moments of {deg[j]: j in Nb(i,s)} (if empty -> {deg[i]}). 4 cols per s."""
    n = len(deg)
    cols = []
    for s in S_r:
        nbs = nbs_by_s[s]
        block = np.zeros((n, 4))
        for i in range(n):
            sample = deg[nbs[i]] if len(nbs[i]) else deg[i:i + 1]
            block[i] = moments(sample)
        cols.append(block)
    return np.hstack(cols)


# ---- Group D: coarse-grained bond-orientational order per s (physical v7 §3 Group D) ------------
def group_D(nbs_by_s, psis, S_r):
    """phys_psi{n}_cg_s = mean over {i} U Nb(i,s) of psi_n(j), for n in {N/2, N, 2N}. 3 cols per s."""
    n = len(next(iter(psis.values())))
    cols = []
    for s in S_r:
        nbs = nbs_by_s[s]
        block = np.zeros((n, 3))
        for ci, key in enumerate(("N//2", "N", "2N")):
            v = psis[key]
            for i in range(n):
                idx = np.concatenate([[i], nbs[i]]).astype(int)
                block[i, ci] = v[idx].mean()
        cols.append(block)
    return np.hstack(cols)


# ---- Group E: Voronoi packing/void per s (physical v7 §3 Group E; empty-nbhd convention) --------
def group_E(nbs_by_s, voro_area, S_r):
    """phys_voro_{mean,var}_s over BOUNDED cells in Nb(i,s). Empty-neighbourhood convention:
    if no bounded cell, mean = area[i], var = 0. 2 cols per s."""
    n = len(voro_area)
    cols = []
    for s in S_r:
        nbs = nbs_by_s[s]
        block = np.zeros((n, 2))
        for i in range(n):
            a = voro_area[nbs[i]]
            a = a[~np.isnan(a)]
            if a.size == 0:
                own = voro_area[i]
                block[i] = (own if not np.isnan(own) else 0.0, 0.0)
            else:
                block[i] = (a.mean(), a.var())
        cols.append(block)
    return np.hstack(cols)


def physical_extra(r, tree, par, deg, psis, voro_area, ell):
    """[Group A | Group B | Group D | Group E] with the exact sealed dimension r + 9*m(r)."""
    S_r = [s for s in C.RADII if s <= r]
    nbs_by_s = {s: neighbourhoods(tree, par, s, ell) for s in S_r}
    A = group_A(tree, par, ell, r)
    B = group_B(nbs_by_s, deg, S_r)
    D = group_D(nbs_by_s, psis, S_r)
    E = group_E(nbs_by_s, voro_area, S_r)
    extra = np.hstack([A, B, D, E])
    assert extra.shape[1] == C.phys_extra_dim(r), \
        f"physical_extra(r={r}) dim {extra.shape[1]} != sealed {C.phys_extra_dim(r)}"
    return extra


# ---- M3 (full, sealed baseline) and continuous match-features -----------------------------------
def m3_full(dens, deg, edge_len_mean, edge_len_var, motif_onehot, g16, g26, psiN, psiNh, psi2N, g40, g60):
    """M3 = [dens, deg, edge_len_mean, edge_len_var, motif one-hot, g(1.6), g(2.6),
    psi_N, psi_{N/2}, psi_{2N}, g(4.0), g(6.0)]. dim = 11 + |codebook|."""
    return np.column_stack([dens, deg, edge_len_mean, edge_len_var, motif_onehot,
                            g16, g26, psiN, psiNh, psi2N, g40, g60])


def match_features(dens, deg, g16, g26, g40, g60, psiN, psiNh, psi2N):
    """The reconciled continuous M3 physical family used by the local permutation matching law
    (conditional-null v4.1 §3/§9): [dens=g(2.0), deg, g(1.6), g(2.6), g(4.0), g(6.0),
    psi_N, psi_{N/2}, psi_{2N}] (9 features). Edge-length moments & motif one-hot excluded."""
    return np.column_stack([dens, deg, g16, g26, g40, g60, psiN, psiNh, psi2N])


def standardise(F, ref_idx=None):
    """z-score using the mean/std of the reference rows (ref_idx) or all rows; std<1e-12 -> 1."""
    R = F if ref_idx is None else F[ref_idx]
    mu = R.mean(0); sd = R.std(0)
    sd = np.where(sd > 1e-12, sd, 1.0)
    return (F - mu) / sd


# ---- X_r assembly with bit-identical dedup (physical v7 §2) --------------------------------------
def build_Xr(M3, extra):
    """X_r = [M3, physical_extra(r)]; M3 retained IN FULL. Drop a physical_extra column ONLY if
    bit-identical (max|delta| < 1e-12) to an M3 column. Never drop an M3 column."""
    keep = []
    for c in range(extra.shape[1]):
        col = extra[:, c]
        dup = any(np.max(np.abs(col - M3[:, k])) < C.DEDUP_TOL for k in range(M3.shape[1]))
        if not dup:
            keep.append(c)
    return np.column_stack([M3, extra[:, keep]]) if keep else M3.copy(), keep
