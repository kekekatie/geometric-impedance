"""
VERBATIM extract of the sealed transport baseline's address primitives, bundled ONLY so the
m4_cols bit-identity test is self-contained inside the audit ZIP (where the full substrates/ package
is not present). In the repository the test imports the real `substrates/transport_run.py` and uses
this file only as a fallback.

PROVENANCE — copied byte-for-byte from `substrates/transport_run.py` (git blob
23b0dfd926697f8bd3a3433391e0a048d446abe3), functions `ball_shells`, `hull_depth`, `_m4_cols`. Verify
against that file: it is the sealed baseline referenced by the manifests. This file changes nothing.
"""
from collections import deque
import numpy as np
from scipy.spatial import ConvexHull


def ball_shells(adj, src, rmax):
    """Graph-distance ball memberships: dist[v] for v within rmax of src (BFS)."""
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


def hull_depth(perp):
    """Signed distance of each perp point to the boundary of the address point cloud."""
    h = ConvexHull(perp)
    A, b = h.equations[:, :-1], h.equations[:, -1]          # A x + b <= 0 inside
    return -(perp @ A.T + b).max(axis=1)                    # >0 inside = depth


def _m4_cols(f, perp_field):
    """Raw M4 columns: shell-averaged perp, perp variance, gradient, hull depth."""
    n, adj, tree, par, shell_r = f["n"], f["adj"], f["tree"], f["par"], f["shell_r"]
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
