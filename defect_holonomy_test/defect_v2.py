#!/usr/bin/env python3
"""
Defect-Holonomy Test -- v2 terminating grid-line construction (protocol §4-v2).

A dislocation is built INSIDE the de Bruijn multigrid: one grid line of family
j* at level m* is truncated to a half-line H terminating at a bulk core c*. The
removed half is the branch cut. Dualizing with a path-based (BFS) lift
assignment that skips the removed crossings makes the lift K multivalued with
monodromy exactly +-e_{j*} around c*. Positions pos' = K'@par_star then differ
across the cut by exactly the lattice edge vector e_{j*}, so re-gluing at unit
length is seamless -- unit edges everywhere except the single core (and the
phason wall the dislocation trails).

Nothing is injected into the transport. The metric (lift_metric.py) still reads
perp displacement from physical edge geometry alone. Holonomy, if present, is a
property of the wounded tiling produced by the truncation.

Registered predictions: b = +-e_{j*}; b_perp = +-perp_star[j*];
loop holonomy = w * b_perp.
"""

import numpy as np
from collections import deque
from scipy.spatial import cKDTree


class TerminatingLineDefect:
    def __init__(self, base, j_star, m_star=None, c_star=None, t_dir=None,
                 removed_side=-1, reglue_tol=0.3, core_pad=2.0):
        self.base = base
        self.substrate = base.substrate
        self.N = base.N
        self.j_star = int(j_star)
        self.par_star = base.par_star
        self.perp_star = base.perp_star
        self.K0 = base.K.copy()
        self.par0 = base.par.copy()
        self.n = base.n
        self.depth = base.depth
        self.zone = base.zone
        self.n_zones = base.n_zones
        # Burgers vector predictions
        self.b_lift = np.zeros(self.N, int); self.b_lift[self.j_star] = 1
        self.b_par = self.b_lift @ self.par_star
        self.b_perp = self.b_lift @ self.perp_star

        # grid geometry of family j*: normal n_j, line direction t_j
        n_j = self.par_star[self.j_star]
        self.n_j = n_j
        self.t_j = np.array([-n_j[1], n_j[0]])       # line direction (perp to normal)
        # projection value s_j(v) = K_{j*}; choose a central level if m* not given
        if m_star is None:
            m_star = int(np.median(self.K0[:, self.j_star]))
        self.m_star = m_star
        # core point c*: a generic point on line level m*, near centre
        if c_star is None:
            c_star = self._pick_core_point()
        self.c = np.asarray(c_star, float)
        self.t_dir = (np.asarray(t_dir, float) if t_dir is not None
                      else self.t_j / np.linalg.norm(self.t_j))
        self.removed_side = removed_side
        self._build(reglue_tol, core_pad)

    def _pick_core_point(self):
        """A point on grid line L(j*, m*) near the patch centre."""
        j = self.j_star
        # vertices adjacent across level m* sit on the line; take their centroid
        onlvl = np.abs(self.K0[:, j] - self.m_star) <= 0
        if onlvl.sum() == 0:
            onlvl = np.abs(self.K0[:, j] - self.m_star) <= 1
        pts = self.par0[onlvl]
        centre = pts[np.argmin(np.linalg.norm(pts, axis=1))]
        return centre

    def _build(self, reglue_tol, core_pad):
        base = self.base
        j = self.j_star
        K = self.K0
        # 1. identify the worm of line L(j*, m*): edges whose only lift change is
        #    +-e_{j*} and whose two j* levels straddle m*.
        removed = set()
        worm = []
        for (u, v) in base.edges:
            dK = K[v] - K[u]
            nz = np.nonzero(dK)[0]
            if len(nz) != 1 or nz[0] != j or abs(dK[j]) != 1:
                continue
            lv = max(K[u, j], K[v, j])
            if lv != self.m_star:
                continue
            worm.append((u, v))
            mid = 0.5 * (self.par0[u] + self.par0[v])
            if np.sign((mid - self.c) @ self.t_dir) == self.removed_side:
                removed.add((u, v)); removed.add((v, u))
        self.worm_size = len(worm)
        self.removed_size = len(removed) // 2

        # 2. path-based lift: BFS from a base vertex far from c*, tracking how
        #    many removed worm edges each path crosses. Beyond the removed half-
        #    ribbon a vertex is shifted by -e_{j*} (the ribbon collapses).
        base_v = int(np.argmax(np.linalg.norm(self.par0 - self.c, axis=1)))
        sc = np.zeros(self.n, dtype=np.int64)   # removed-ribbon crossing count
        seen = np.zeros(self.n, bool)
        seen[base_v] = True
        dq = deque([base_v])
        while dq:
            a = dq.popleft()
            for b in base.adj[a]:
                if seen[b]:
                    continue
                sc[b] = sc[a] + (1 if (a, b) in removed else 0)
                seen[b] = True
                dq.append(b)
        Kp = K - sc[:, None] * self.b_lift[None, :]
        self.Kp = Kp
        self.shift_count = sc

        # 3. closure defect: across removed worm edges the lift mismatch must be
        #    +-e_{j*}; nowhere else. (The topological monodromy check.)
        defects = []
        for (u, v) in base.edges:
            dK_true = K[v] - K[u]
            mism = Kp[v] - Kp[u] - dK_true
            if np.any(mism != 0):
                defects.append((u, v, mism.copy()))
        self.closure_defects = defects
        self.closure_ok = bool(defects) and all(
            np.array_equal(np.abs(m), np.abs(self.b_lift)) for _, _, m in defects)

        # 4. merge collapsed-ribbon vertices (identical lift) and re-glue by LIFT
        #    adjacency, so every edge is an exact star vector (zero residual).
        groups = {}
        rep = np.full(self.n, -1, dtype=np.int64)
        for v in range(self.n):
            key = tuple(Kp[v].tolist())
            if key not in groups:
                groups[key] = v
            rep[v] = groups[key]
        self.rep = rep
        reps = sorted(set(rep.tolist()))
        self.merged = self.n - len(reps)
        # positions on merged reps
        self.par = Kp @ self.par_star
        self.perp = Kp @ self.perp_star     # cross-check only
        self.K = Kp
        lift_index = {tuple(Kp[v].tolist()): v for v in reps}
        eye = np.eye(self.N, dtype=np.int64)
        adj2 = [[] for _ in range(self.n)]
        edges2 = set()
        for v in reps:
            for jj in range(self.N):
                for s in (+1, -1):
                    nb = tuple((Kp[v] + s * eye[jj]).tolist())
                    q = lift_index.get(nb)
                    if q is not None and q != v:
                        adj2[v].append(q)
                        edges2.add((min(v, q), max(v, q)))
        self.adj = [np.array(sorted(set(a)), dtype=np.int64) for a in adj2]
        self.edges = sorted(edges2)

        # 5. core region: near c* + coordination anomalies among reps
        r = np.linalg.norm(self.par - self.c[None, :], axis=1)
        deg = np.array([len(a) for a in self.adj])
        base_deg = np.array([len(a) for a in base.adj])
        anom = (deg != base_deg) & np.isin(np.arange(self.n), reps)
        core = (r < core_pad) | ((r < 5.0) & anom)
        # non-representative (merged-away) vertices are part of the collapsed
        # ribbon; keep them out of walks
        core[rep != np.arange(self.n)] = True
        self.core_mask = core
        self.core_size = int(core.sum())
        self.deg = deg
        self.reps = np.array(reps, dtype=np.int64)

    # graph helpers -------------------------------------------------------- #
    def largest_component(self):
        seen = np.zeros(self.n, bool); best = []
        for s in range(self.n):
            if seen[s]:
                continue
            comp = []; q = deque([s]); seen[s] = True
            while q:
                v = q.popleft(); comp.append(v)
                for w in self.adj[v]:
                    if not seen[w]:
                        seen[w] = True; q.append(w)
            if len(comp) > len(best):
                best = comp
        return np.array(sorted(best), dtype=np.int64)

    def winding_number(self, positions):
        P = np.asarray(positions, float) - self.c[None, :]
        a = np.arctan2(P[:, 1], P[:, 0])
        d = np.diff(a); d = (d + np.pi) % (2 * np.pi) - np.pi
        return d.sum() / (2 * np.pi)
