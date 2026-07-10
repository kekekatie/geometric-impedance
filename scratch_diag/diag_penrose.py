#!/usr/bin/env python3
"""STEP 0 diagnostic: localize the Penrose over-coordination.

Questions:
  (Q1) Reproduce: max interior coordination, degree histogram (AB vs Penrose).
  (Q2) Are the degree>=8 vertices gauge duplicates? (coincident positions?)
  (Q3) Does over-coordination survive a clean unit-distance edge rebuild?
  (Q4) What is sum(gammas)? (de Bruijn: Penrose proper needs sum in Z.)
  (Q5) For degree>=8 vertices: perp coord, residue class, which +-e_j present.
  (Q6) Are the offending vertices' perp coords INSIDE the empirical hull but
       would be OUTSIDE a true (smaller) pentagon? i.e. window-shape story.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
from geometry import Patch, SUBSTRATES

np.set_printoptions(precision=4, suppress=True)

def degree_hist(p):
    degs = np.array([len(a) for a in p.adj])
    return degs

def interior_mask(p, frac=0.75):
    """Interior = inner frac of radius, to avoid boundary truncation effects."""
    r = np.linalg.norm(p.par, axis=1)
    return r <= frac * p.radius

for name in ["ammann_beenker", "penrose"]:
    print("="*70)
    print(name.upper())
    print("="*70)
    p = Patch(name, radius=16.0, verbose=True)
    degs = degree_hist(p)
    int_m = interior_mask(p)
    ideg = degs[int_m]
    print(f"  sum(gammas) = {p.gammas.sum():.6f}   gammas={p.gammas}")
    print(f"  N vertices = {p.n}  interior = {int_m.sum()}")
    print(f"  ALL      degree hist:", np.bincount(degs).tolist())
    print(f"  INTERIOR degree hist:", np.bincount(ideg).tolist())
    print(f"  max interior coordination = {ideg.max()}")

    if name == "penrose":
        # (Q2) coincident positions?
        # round perp+par to detect duplicates
        pos = np.round(p.par, 6)
        uniq = np.unique(pos, axis=0)
        print(f"  distinct parallel positions: {len(uniq)} / {p.n} "
              f"(coincident: {p.n - len(uniq)})")

        # (Q3) clean unit-distance rebuild of edges among ALL vertices
        # neighbors = pairs at physical distance == edge length (min positive dist)
        from scipy.spatial import cKDTree
        tree = cKDTree(p.par)
        # find typical edge length: min nonzero pair distance
        d, idx = tree.query(p.par, k=2)
        edge_len = np.median(d[:, 1])
        print(f"  physical edge length (median NN) = {edge_len:.4f}")
        pairs = tree.query_pairs(edge_len * 1.02)
        deg2 = np.zeros(p.n, dtype=int)
        for i, j in pairs:
            if abs(np.linalg.norm(p.par[i]-p.par[j]) - edge_len) < 1e-3:
                deg2[i]+=1; deg2[j]+=1
        print(f"  unit-distance-rebuild INTERIOR degree hist:",
              np.bincount(deg2[int_m]).tolist(),
              f" max={deg2[int_m].max()}")

        # (Q5) look at the worst offenders
        hi = np.where(int_m & (degs >= 8))[0]
        print(f"\n  {len(hi)} interior vertices with degree>=8 "
              f"({100*len(hi)/int_m.sum():.2f}% of interior)")
        # perp radius distribution of offenders vs all
        pr_all = np.linalg.norm(p.perp, axis=1)
        print(f"  perp |r|: all interior  mean={pr_all[int_m].mean():.3f} "
              f"max={pr_all[int_m].max():.3f}")
        if len(hi):
            print(f"  perp |r|: degree>=8     mean={pr_all[hi].mean():.3f} "
                  f"max={pr_all[hi].max():.3f} min={pr_all[hi].min():.3f}")
        # show a few
        eye = np.eye(p.N, dtype=np.int64)
        for v in hi[:5]:
            K = p.K[v]
            present = []
            for j in range(p.N):
                for s in (+1,-1):
                    nb = tuple((K + s*eye[j]).tolist())
                    if nb in p._index:
                        present.append(f"{'+' if s>0 else '-'}e{j}")
            print(f"    v{v}: deg={degs[v]} rc={p.residue_class[v]} "
                  f"perp={p.perp[v]} |perp|={pr_all[v]:.3f}")
            print(f"         present edges ({len(present)}): {present}")
