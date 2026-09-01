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
