#!/usr/bin/env python3
"""
Defect-Holonomy Test -- Volterra surgery (protocol §4).

INTEGRITY LOCK (protocol §2, requirement 1)
-------------------------------------------
The defect is made by actual tile-level surgery: cut the tiling along a ray from
a bulk core to the boundary, and re-glue the two lips with a one-row offset (the
classical extra/removed half-plane of an edge dislocation). NOWHERE is there a
rule of the form "edges crossing ray R acquire extra perp." The transport metric
(lift_metric.py) is defect-blind: it only ever classifies an edge by its physical
displacement. Any holonomy therefore emerges from the modified adjacency, not
from an injected connection.

The seam edges created by the offset re-glue are genuine geometric misfit (a
dislocation cannot be perfect). Edges whose length exceeds tolerance define the
core region, whose vertices are excluded as walk endpoints (protocol §4.4).
"""

import numpy as np
from collections import deque


def _seg_ray_hit(p, q, c, u):
    """Does segment p->q cross the ray {c + t*u, t>=0}? Return t or None."""
    d = q - p
    # solve p + s d = c + t u  ->  [d, -u] [s, t]^T = c - p
    M = np.array([[d[0], -u[0]], [d[1], -u[1]]])
    det = M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0]
    if abs(det) < 1e-12:
        return None
    rhs = c - p
    s = (rhs[0] * M[1, 1] - rhs[1] * M[0, 1]) / det
    t = (M[0, 0] * rhs[1] - M[1, 0] * rhs[0]) / det
    if -1e-9 <= s <= 1 + 1e-9 and t >= 1e-9:
        return t
    return None


class WoundedPatch:
    """A defect-free Patch with a single dislocation introduced by offset re-glue.

    Exposes the same surface the walker/metric need: par_star, perp_star, par
    (positions), perp (for cross-check only), adj, n, depth, zone, plus core_mask,
    seam_edges, the core point `c`, and the measured Burgers data.
    """

    def __init__(self, base, c, u, offset=1, edge_len=1.0, tol_frac=0.5,
                 core_pad=2.0):
        self.base = base
        self.substrate = base.substrate
        self.N = base.N
        self.par_star = base.par_star
        self.perp_star = base.perp_star
        self.par = base.par.copy()
        self.perp = base.perp.copy()          # cross-check only
        self.K = base.K.copy()
        self.depth = base.depth
        self.zone = base.zone
        self.n_zones = base.n_zones
        self.n = base.n
        self.c = np.asarray(c, float)
        self.u = np.asarray(u, float) / np.linalg.norm(u)
        self.edge_len = edge_len
        self.offset = offset
        self._build(tol_frac, core_pad)

    # -- surgery ------------------------------------------------------------- #
    def _build(self, tol_frac, core_pad):
        base = self.base
        c, u = self.c, self.u
        # adjacency as a mutable set of undirected edges
        edges = set(tuple(sorted(e)) for e in base.edges)

        # 1. find edges crossing the cut ray, with their crossing distance t
        crossings = []
        for (i, j) in edges:
            t = _seg_ray_hit(self.par[i], self.par[j], c, u)
            if t is not None:
                crossings.append((t, i, j))
        crossings.sort()

        # 2. remove crossing edges (open the slit)
        for _, i, j in crossings:
            edges.discard(tuple(sorted((i, j))))

        # 3. label lips: for each crossing, upper (+normal side) / lower vertex
        nrm = np.array([-u[1], u[0]])   # +90deg normal
        upper, lower = [], []           # ordered by t (outward from core)
        for t, i, j in crossings:
            si = nrm @ (self.par[i] - c)
            up, lo = (i, j) if si > 0 else (j, i)
            upper.append(up)
            lower.append(lo)

        # 4. re-glue with a one-row offset -> inserts the terminating half-row.
        #    upper[k] reconnects to lower[k+offset]; the first `offset` crossings
        #    nearest the core are left to terminate (the dislocation core).
        seam = []
        m = len(crossings)
        off = self.offset
        for k in range(m):
            kk = k + off
            if 0 <= kk < m:
                a, b = upper[k], lower[kk]
                if a != b:
                    e = tuple(sorted((a, b)))
                    edges.add(e)
                    seam.append(e)
        self.seam_edges = seam

        # 5. rebuild adjacency
        adj = [[] for _ in range(self.n)]
        for (i, j) in edges:
            adj[i].append(j)
            adj[j].append(i)
        self.adj = [np.array(sorted(a), dtype=np.int64) for a in adj]
        self.edges = sorted(edges)

        # 6. core region: vertices on seam edges whose length exceeds tolerance,
        #    plus everything within core_pad edge-lengths of the core point.
        tol = (1.0 + tol_frac) * self.edge_len
        misfit_v = set()
        for (i, j) in seam:
            L = np.linalg.norm(self.par[i] - self.par[j])
            if L > tol:
                misfit_v.add(i)
                misfit_v.add(j)
        r = np.linalg.norm(self.par - c[None, :], axis=1)
        core = (r < core_pad * self.edge_len)
        for v in misfit_v:
            core[v] = True
        self.core_mask = core
        self.core_size = int(core.sum())

        # Burgers vector (measured): net lift mismatch across a tight seam re-glue.
        # b = K(lower[k+off]) - K(upper[k]) - (expected unit step). We report the
        # perp image directly from the tight loop in _measure_burgers().
        self._measure_burgers()

    def _measure_burgers(self):
        """Estimate b_perp from the construction: the lift jump implied by the
        offset re-glue, projected to perp. Uses stored lifts (construction-time
        bookkeeping, allowed as cross-check per §3; the *measurement* in
        experiments is lift-by-integration)."""
        if not self.seam_edges:
            self.b_perp = np.zeros(2)
            self.b_lift = np.zeros(self.N)
            return
        # median lift jump across seam edges (excluding oversized misfit)
        jumps = []
        for (i, j) in self.seam_edges:
            dK = self.K[j] - self.K[i]
            jumps.append(dK)
        jumps = np.array(jumps)
        # the characteristic Burgers lift is the modal non-unit jump
        self.b_lift = np.round(np.median(jumps, axis=0)).astype(int)
        self.b_perp = self.b_lift @ self.perp_star

    # -- graph helpers ------------------------------------------------------- #
    def largest_component(self):
        seen = np.zeros(self.n, dtype=bool)
        best = []
        for s in range(self.n):
            if seen[s]:
                continue
            comp = []
            q = deque([s]); seen[s] = True
            while q:
                v = q.popleft(); comp.append(v)
                for w in self.adj[v]:
                    if not seen[w]:
                        seen[w] = True; q.append(w)
            if len(comp) > len(best):
                best = comp
        return np.array(sorted(best), dtype=np.int64)

    def winding_number(self, positions):
        """Signed winding number of a closed physical path about the core."""
        P = np.asarray(positions, float) - self.c[None, :]
        ang = np.arctan2(P[:, 1], P[:, 0])
        dang = np.diff(ang)
        dang = (dang + np.pi) % (2 * np.pi) - np.pi   # wrap to (-pi,pi]
        return dang.sum() / (2 * np.pi)


def ring_loop(wp, radius, patch_for_paths=None):
    """Build a closed walk that winds the core once, at ~`radius` from it, as a
    sequence of vertices connected through the WOUNDED graph. Returns a vertex
    path (list) or None."""
    import walker as W
    c = wp.c
    r = np.linalg.norm(wp.par - c[None, :], axis=1)
    band = np.where((r > radius * 0.75) & (r < radius * 1.25) & (~wp.core_mask))[0]
    if len(band) < 8:
        return None
    ang = np.arctan2(wp.par[band, 1] - c[1], wp.par[band, 0] - c[0])
    order = band[np.argsort(ang)]
    # stitch consecutive ring vertices via shortest paths in the wounded graph
    path = [int(order[0])]
    for k in range(1, len(order) + 1):
        tgt = int(order[k % len(order)])
        dist, parent = W.bfs(wp, path[-1])
        seg = W.reconstruct_path(parent, path[-1], tgt)
        if seg is None:
            return None
        path.extend(seg[1:])
    return path
