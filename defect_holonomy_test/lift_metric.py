#!/usr/bin/env python3
"""
Defect-Holonomy Test -- lift-by-integration address metric (protocol §3).

INTEGRITY LOCK (protocol §2, requirement 2)
-------------------------------------------
The walker reconstructs perpendicular-space displacement from EDGE GEOMETRY
ALONE -- the physical displacement direction of each traversed edge -- exactly as
a local observer inside the tiling would. It never consults a stored per-vertex
perp table. Stored perp coordinates are used only for the E0 cross-check on
defect-free patches, never as the measurement in wounded patches.

Each edge of a cut-and-project rhombus tiling is (in the bulk) a translate of one
star vector +-e_j. Classifying an edge by which +-e_j its *physical* displacement
best matches, and adding that star vector's *perpendicular* image e_perp_j, gives
the integrated address. On a defect-free patch this equals perp(end)-perp(start)
to machine precision (validation E0). Near surgical seams some edges match poorly
(residual above tolerance) -- those are logged and drive the core-region
definition (protocol §4).
"""

import numpy as np


class LiftMetric:
    """Edge-type classifier + integrated address for a patch-like object.

    The object must expose:
      par_star  (N,2)  parallel-space star vectors
      perp_star (N,2)  perpendicular-space star vectors
      pos(i) -> (2,)   physical position of vertex i   (we use .par[i])
    """

    def __init__(self, par_star, perp_star, edge_len=1.0, tol_frac=0.35):
        self.par_star = np.asarray(par_star, float)
        self.perp_star = np.asarray(perp_star, float)
        self.N = self.par_star.shape[0]
        # candidate directed step vectors: +-e_j in parallel and perp
        self.cand_par = np.concatenate([self.par_star, -self.par_star], axis=0)   # (2N,2)
        self.cand_perp = np.concatenate([self.perp_star, -self.perp_star], axis=0)
        self.tol = tol_frac * edge_len

    def classify(self, disp):
        """Classify a physical displacement vector -> (index into 2N, residual)."""
        d = np.asarray(disp, float)
        diffs = self.cand_par - d[None, :]
        dist = np.einsum("ij,ij->i", diffs, diffs)
        k = int(np.argmin(dist))
        return k, float(np.sqrt(dist[k]))

    def edge_dperp(self, pos_a, pos_b):
        """Perp increment of directed edge a->b, from physical geometry alone.
        Returns (dperp (2,), residual)."""
        k, res = self.classify(np.asarray(pos_b, float) - np.asarray(pos_a, float))
        return self.cand_perp[k], res

    def integrate(self, positions):
        """Integrated address along a walk given as an (n,2) array of physical
        positions. Returns (address_vector (2,), max_residual, n_over_tol)."""
        P = np.asarray(positions, float)
        if len(P) < 2:
            return np.zeros(2), 0.0, 0
        acc = np.zeros(2)
        max_res = 0.0
        n_over = 0
        for a, b in zip(P[:-1], P[1:]):
            dperp, res = self.edge_dperp(a, b)
            acc += dperp
            max_res = max(max_res, res)
            if res > self.tol:
                n_over += 1
        return acc, max_res, n_over

    def holonomy(self, positions):
        """Closed-loop holonomy: (‖address‖, address_vector, max_res, n_over)."""
        acc, max_res, n_over = self.integrate(positions)
        return float(np.linalg.norm(acc)), acc, max_res, n_over


def positions_of_path(patch, path):
    """Physical positions along a vertex path (uses patch.par -- geometry only)."""
    return patch.par[np.asarray(path, dtype=int)]
