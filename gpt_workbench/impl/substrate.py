"""
Substrate primitives for the sealed pipeline.

The short baseline helpers (ball_shells, hull_depth, _m4_cols) are reimplemented here BIT-FAITHFULLY
to the sealed transport baseline (substrates/transport_run.py); `tests/test_substrate.py` proves they
are identical to the original on synthetic inputs. Tiling generation (generate/build_edges/structure)
is imported lazily from substrates/generate_rank4.py for PRODUCTION use only — it is geometry
generation, and this module never runs study dynamics, addresses-as-outcomes, LDOS, or beta.
"""
from collections import deque
import numpy as np
from scipy.spatial import ConvexHull, cKDTree
from . import constants as C


def build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j); adj[j].append(i)
    return adj


def ball_shells(adj, src, rmax):
    """Graph-distance ball memberships (BFS). Bit-faithful to transport_run.ball_shells."""
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        if dist[u] == rmax:
            continue
        for w in adj[u]:
            if w not in dist:
                dist[w] = dist[u] + 1
                q.append(w)
    return dist


def hull_depth(points):
    """Signed distance of each point to the boundary of its convex hull (>0 inside).
    Bit-faithful to transport_run.hull_depth."""
    h = ConvexHull(points)
    A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(points @ A.T + b).max(axis=1)


def m4_cols(adj, tree, par, perp_field, shell_r=(2, 4, 8)):
    """The exact 11-column address block (bit-faithful to transport_run._m4_cols):
    shell-mean(2) + shell-var(1) at graph shells {2,4,8}, + gradient + hull-depth."""
    n = len(par)
    sm = {r: np.zeros((n, 2)) for r in shell_r}
    sv = {r: np.zeros(n) for r in shell_r}
    gr = np.zeros(n)
    for i in range(n):
        dist = ball_shells(adj, i, max(shell_r))
        members = np.array(sorted(dist)); dd = np.array([dist[v] for v in members])
        for r in shell_r:
            sel = members[dd <= r]
            sm[r][i] = perp_field[sel].mean(0); sv[r][i] = perp_field[sel].var(0).sum()
        nb = tree.query_ball_point(par[i], 3.0)
        if len(nb) >= 4:
            X = np.column_stack([par[nb] - par[i], np.ones(len(nb))])
            coef, *_ = np.linalg.lstsq(X, perp_field[nb], rcond=None)
            gr[i] = np.linalg.norm(coef[:2])
    dpt = hull_depth(perp_field)
    cols = []
    for r in shell_r:
        cols.append(sm[r]); cols.append(sv[r][:, None])
    cols.append(gr[:, None]); cols.append(dpt[:, None])
    return np.column_stack(cols)


def common_set_r16(par, ell, depth=16):
    """Evaluated population = the d_bound >= depth*ell common interior set (physical v7 §5).
    d_bound(i) = hull_depth(par)[i]; fixed across rungs."""
    return np.where(hull_depth(par) >= depth * ell) [0]


def median_edge_length(par, edges):
    d = par[[i for i, _ in edges]] - par[[j for _, j in edges]]
    return float(np.median(np.linalg.norm(d, axis=1)))


def generate_geometry(family_N, extent, offset):
    """PRODUCTION-ONLY lazy wrapper around generate_rank4 (geometry generation; no dynamics).
    Returns (lifts, par, perp, ustar, edges, adj). Not used by the synthetic test-suite."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "substrates"))
    from generate_rank4 import generate, build_edges
    lifts, par, perp, ustar = generate(family_N, extent, offset=np.array(offset))
    edges = build_edges(lifts, family_N, ustar)
    return lifts, par, perp, ustar, edges, build_adj(len(par), edges)


# ---- production geometry wiring: padded super-patch Voronoi (physical v7 §3a; §5 floors) --------
def assert_pad_params(delta, ring_width_ell):
    """Frozen: Delta >= 4 and padding ring width >= 3 ell (physical v7 §3a)."""
    assert delta >= 4, f"padded super-patch Delta must be >= 4 (got {delta})"
    assert ring_width_ell >= 3, f"padding ring width must be >= 3 ell (got {ring_width_ell})"


def restrict_voronoi_to_core(all_points, core_index):
    """Compute Voronoi on the PADDED super-patch and restrict areas to core vertices via EXPLICIT
    core-vertex correspondence (core_index into all_points). Asserts every core cell is bounded."""
    from .features import voronoi_areas
    core_index = np.asarray(core_index, int)
    areas_all = voronoi_areas(all_points)
    core_areas = areas_all[core_index]
    assert not np.isnan(core_areas).any(), \
        "a core Voronoi cell is unbounded/censored — increase padding (Delta/ring)"
    return core_areas


def pad_convergence(areas_delta4, areas_delta6, tol=None):
    """Per-core-cell relative agreement between Delta=4 and Delta=6 areas; pass iff worst-case
    relative difference <= tol (frozen 1e-6)."""
    tol = C.VORONOI_CONV_TOL if tol is None else tol
    a4 = np.asarray(areas_delta4, float); a6 = np.asarray(areas_delta6, float)
    rel = np.abs(a4 - a6) / np.maximum(np.abs(a6), 1e-30)
    return bool(rel.max() <= tol), float(rel.max())


def assert_floors(r16_count, slab_counts):
    """Common-set and count-floor assertions (physical v7 §5): r16 >= 400 and every slab >= 100."""
    assert r16_count >= 400, f"r16 common set {r16_count} < 400 floor"
    assert min(slab_counts) >= 100, f"a slab has {min(slab_counts)} < 100 floor"


def padded_core_voronoi_areas(family_N, extent, offset, delta=4):
    """PRODUCTION-ONLY: generate at core extent + Delta, restrict Voronoi to the core vertices.
    Geometry-only; not invoked by the synthetic test-suite and never on prohibited study outcomes."""
    assert_pad_params(delta, 3)
    lifts_c, par_c, _, _, _, _ = generate_geometry(family_N, extent, offset)
    lifts_p, par_p, _, _, _, _ = generate_geometry(family_N, extent + delta, offset)
    # explicit correspondence: match core par-points into the padded set by exact coordinate
    idx = {tuple(np.round(p, 9)): k for k, p in enumerate(par_p)}
    core_index = np.array([idx[tuple(np.round(p, 9))] for p in par_c], int)
    return restrict_voronoi_to_core(par_p, core_index)
