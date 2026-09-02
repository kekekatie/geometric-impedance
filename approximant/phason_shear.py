#!/usr/bin/env python3
"""
Seamless phason-shear rational approximant.

The object that unblocks three programme threads at once:
  * winding-staircase Stage D's primary matched-degree control (aperiodicity
    isolated: periodic, planar, local, same degree histogram, differing from the
    ideal only in rational vs irrational slope);
  * the memory paper's outstanding surgical leg (a seamless substrate to cut a
    dislocation dipole into);
  * the AI-memory paper's foundational control (holds degree AND locality, which
    degree-preserving rewiring cannot).

Construction (the key idea): keep IDEAL parallel positions -- so every edge stays
an exact unit star vector, seamless everywhere -- and apply the phason shear to
the ACCEPTANCE only.

    pi_perp'(K) = pi_perp(K) - A . pi_par(K),   A chosen so pi_perp'(M_a)=pi_perp'(M_b)=0

With the period sublattice S = <M_a, M_b> in the kernel of the sheared perp,
acceptance is S-periodic, so the tiling is genuinely periodic with period lattice
{pi_par(M_a), pi_par(M_b)} while every edge remains a unit ideal star. As the
approximant order rises, the shear A -> 0 and the tiling -> the ideal quasicrystal
(the memory-paper price list: misfit shrinks at sqrt2-1 per order (AB), 1/phi
(Penrose)).

Penrose note: the (1,1,1,1,1) direction maps to zero in BOTH par and perp, so
lifts differing by it share a position; vertices are therefore deduplicated by
position and edges built by unit-distance adjacency on ideal positions.
"""

import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reverse_loop_test"))
import numpy as np
from collections import deque
from scipy.spatial import cKDTree
from geometry import (Patch, star_vectors, SUBSTRATES,
                      _convex_polygon, polygon_halfplanes, window_depth)

REG = json.load(open(Path(__file__).parent.parent /
                     "defect_holonomy_test" / "phase0_registration.json"))


class PhasonShearApproximant:
    def __init__(self, substrate, order_index, radius=13.0, edge_tol=0.15):
        cfg = SUBSTRATES[substrate]
        self.substrate = substrate
        self.N = cfg["N"]
        self.radius = radius
        self.par_star, self.perp_star = star_vectors(
            cfg["N"], cfg["par_step"], cfg["perp_step"])
        o = REG[substrate]["orders"][order_index]
        self.order = o["order"]
        self.convergent = o["convergent"]
        self.M_a = np.array(o["M_a"]); self.M_b = np.array(o["M_b"])
        self.P_a = self.M_a @ self.par_star
        self.P_b = self.M_b @ self.par_star
        self.q_a = self.M_a @ self.perp_star      # ideal perp quantum
        self.q_b = self.M_b @ self.perp_star
        # phason shear A : E_par(2D) -> E_perp(2D), A @ [P_a P_b] = [q_a q_b]
        Qpar = np.array([self.P_a, self.P_b]).T
        Qperp = np.array([self.q_a, self.q_b]).T
        self.A = Qperp @ np.linalg.inv(Qpar)
        self._build(radius, edge_tol)

    def _windows(self, radius):
        p = Patch(self.substrate, radius=radius + 3)
        if self.substrate == "penrose":
            wins = {}
            for rc in range(self.N):
                m = p.residue_class == rc
                if m.sum() >= 3:
                    hull = _convex_polygon(p.perp[m])
                    wins[rc] = polygon_halfplanes(hull)[:2]
            return wins
        hull = _convex_polygon(p.perp)
        return {0: polygon_halfplanes(hull)[:2]}

    def _build(self, radius, edge_tol):
        N = self.N
        wins = self._windows(radius)
        M = int(radius) + 4
        axis = np.arange(-M, M + 1)
        K = np.stack(np.meshgrid(*([axis] * N), indexing="ij"), -1).reshape(-1, N)
        par = K @ self.par_star
        perp = K @ self.perp_star
        perp_sh = perp - (self.A @ par.T).T
        rc = (K.sum(1) % N) if self.substrate == "penrose" else np.zeros(len(K), int)
        acc = np.zeros(len(K), bool)
        for key, (nrm, off) in wins.items():
            sel = np.where(rc == key)[0]
            d = window_depth(perp_sh[sel], nrm, off)
            acc[sel[d > 0]] = True
        r = np.linalg.norm(par, axis=1)
        keep = acc & (r < radius)
        Kk = K[keep]; pos = par[keep]; perp_k = perp[keep]
        # dedupe by position (removes (1,1,1,1,1)-gauge duplicates on Penrose)
        key = np.round(pos, 6)
        _, uniq = np.unique(key, axis=0, return_index=True)
        uniq = np.sort(uniq)
        self.K = Kk[uniq]; self.par = pos[uniq]; self.perp = perp_k[uniq]
        self.n = len(self.K)
        self._accepted_all = set(map(tuple, K[acc].tolist()))
        # edges by unit-distance adjacency on ideal positions (exact stars)
        tree = cKDTree(self.par)
        pairs = tree.query_pairs(r=1.0 + edge_tol)
        adj = [[] for _ in range(self.n)]
        edges = []
        maxres = 0.0
        cand = np.concatenate([self.par_star, -self.par_star], 0)
        for i, j in pairs:
            d = self.par[j] - self.par[i]
            if abs(np.linalg.norm(d) - 1.0) > edge_tol:
                continue
            res = np.linalg.norm(cand - d, axis=1).min()
            maxres = max(maxres, res)
            adj[i].append(j); adj[j].append(i)
            edges.append((i, j))
        self.adj = [np.array(sorted(a), dtype=np.int64) for a in adj]
        self.edges = edges
        self.max_edge_star_residual = float(maxres)

    def largest_component(self):
        seen = np.zeros(self.n, bool); best = []
        for s in range(self.n):
            if seen[s]:
                continue
            comp = []; q = deque([s]); seen[s] = True
            while q:
                u = q.popleft(); comp.append(u)
                for v in self.adj[u]:
                    if not seen[v]:
                        seen[v] = True; q.append(v)
            if len(comp) > len(best):
                best = comp
        return np.array(sorted(best), dtype=np.int64)

    def periodicity_fraction(self):
        s = sum(1 for k in self.K.tolist()
                if tuple((np.array(k) + self.M_a).tolist()) in self._accepted_all)
        return s / self.n
