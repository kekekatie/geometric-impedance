#!/usr/bin/env python3
"""
GEOMETRY-ONLY checks for the manifest v3/v4 repairs (Work-GPT/Sol authorised).
STRICTLY geometry: generator + hull depth + degree + Voronoi + PCA. No Hamiltonian,
eigen, dynamics, LDOS, address-as-target, regression, or scientific outcome.

Covers all NINE planned tiers x six frozen offsets:
  1. new radial-bin occupancy + min inter-vertex distance (physical #1);
  2. missing geometry metrics for silver e14/e16, platinum e16 (physical #2) + all tiers
     (n, hull area, diameter, aspect ratio, usable r16 area, per-offset r16 counts);
  4. feasibility floor: r16 common-set >=400 and each of 4 equal-count PCA slabs >=100;
  5. parity-rank: variances of Re/Im z_N (document its rank problem) AND the covariance
     rank of the proposed (degree, Voronoi-area) field, z-scored within the r16 set.
"""
import sys
import numpy as np
from scipy.spatial import ConvexHull, cKDTree, Voronoi
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../substrates")
from generate_rank4 import generate, build_edges

TIERS = [("silver", 8, 14, "small"), ("silver", 8, 16, "medium"), ("silver", 8, 18, "large"),
         ("golden", 10, 18, "small"), ("golden", 10, 20, "medium"), ("golden", 10, 22, "large"),
         ("platinum", 12, 16, "small"), ("platinum", 12, 18, "medium"), ("platinum", 12, 20, "large")]
OFFS = [(0.13, 0.37), (0.29, 0.11), (0.41, 0.23), (0.05, 0.47), (0.19, 0.31), (0.37, 0.09)]
TAU = 1e-9


def hull_depth(P):
    h = ConvexHull(P); A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(P @ A.T + b).max(axis=1)


def hull_area_diam(P):
    h = ConvexHull(P); hp = P[h.vertices]
    d = max(np.linalg.norm(hp - hp[i], axis=1).max() for i in range(len(hp)))
    return float(h.volume), float(d)


def voro_areas(P, want):
    """Bounded Voronoi cell area for the indices in `want` (deep interior => bounded)."""
    vor = Voronoi(P); out = {}
    for i in want:
        reg = vor.regions[vor.point_region[i]]
        if len(reg) == 0 or -1 in reg:
            out[i] = np.nan; continue
        V = vor.vertices[reg]; c = V.mean(0)
        o = np.argsort(np.arctan2(V[:, 1] - c[1], V[:, 0] - c[0])); Q = V[o]
        out[i] = 0.5 * abs(np.dot(Q[:, 0], np.roll(Q[:, 1], -1)) - np.dot(Q[:, 1], np.roll(Q[:, 0], -1)))
    return np.array([out[i] for i in want])


def analyse(N, ext, off):
    lifts, par, perp, ustar = generate(N, ext, offset=np.array(off))
    n = len(par); E = build_edges(lifts, N, ustar)
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j); adj[j].append(i)
    deg = np.array([len(a) for a in adj], float)
    d = par[[i for i, _ in E]] - par[[j for _, j in E]]
    ell = float(np.median(np.linalg.norm(d, axis=1)))
    db = hull_depth(par); area, diam = hull_area_diam(par)
    r16 = np.where(db >= 16 * ell)[0]; n16 = len(r16)

    # bin check: min inter-vertex distance and bin-1 occupancy (new bins k=ceil(d/l - tau))
    tree = cKDTree(par)
    dmin = tree.query(par, k=2)[0][:, 1].min() / ell        # nearest-neighbour, ell units
    # bin-1 occupancy = # of j with 0 < d <= ell (ceil(d/l - tau) == 1)
    b1 = np.array(tree.query_ball_point(par, ell + 1e-9 * ell, return_length=True)) - 1  # minus self
    bin1_mean = float(b1.mean())

    res = dict(N=N, ext=ext, off=off, n=n, ell=ell, area=area, diam=diam, n16=n16,
               dmin_ell=float(dmin), bin1_mean=bin1_mean)
    if n16 >= 4:
        C = par[r16]; c = C.mean(0); cov = np.cov((C - c).T)
        w, Vc = np.linalg.eigh(cov)
        res["aspect"] = float(np.sqrt(w[-1] / max(w[0], 1e-12)))
        res["usable16"] = hull_area_diam(C)[0]
        # 4 equal-count contiguous PCA slabs along PC1
        proj = (C - c) @ Vc[:, -1]
        order = np.argsort(proj, kind="stable")
        sizes = [len(s) for s in np.array_split(order, 4)]
        res["slab_min"] = int(min(sizes))
        # parity-rank: z_N field on r16
        zN = np.zeros(n, complex)
        for i in range(n):
            if adj[i]:
                th = np.arctan2(par[np.array(adj[i]), 1] - par[i, 1], par[np.array(adj[i]), 0] - par[i, 0])
                zN[i] = np.mean(np.exp(1j * N * th))
        reZ, imZ = zN[r16].real, zN[r16].imag
        res["varReZ"] = float(np.var(reZ)); res["varImZ"] = float(np.var(imZ))
        covZ = np.cov(np.vstack([reZ, imZ])); wz = np.linalg.eigvalsh(covZ)
        res["zN_cond"] = float(wz[-1] / max(wz[0], 1e-30))
        # proposed field: (degree, Voronoi area), z-scored within r16
        va = voro_areas(par, list(r16))
        F = np.vstack([deg[r16], va]).T
        good = np.isfinite(F).all(1)
        Fz = F[good]
        Fz = (Fz - Fz.mean(0)) / np.where(Fz.std(0) > 1e-12, Fz.std(0), 1.0)
        covF = np.cov(Fz.T); wf = np.linalg.eigvalsh(covF)
        res["field_eig_min"] = float(wf[0]); res["field_eig_max"] = float(wf[-1])
        res["field_cond"] = float(wf[-1] / max(wf[0], 1e-30))
        res["deg_var"] = float(deg[r16].var()); res["voro_var"] = float(np.nanvar(va))
    return res


def agg(key, rs, fmt="{:.0f}"):
    v = [r[key] for r in rs if key in r]
    return f"{np.mean(v):.3f} [{min(v):.3f}..{max(v):.3f}]" if v else "n/a"


def main():
    print("# GEOMETRY-ONLY CHECKS v3  (no dynamics/address/targets)")
    for name, N, ext, tier in TIERS:
        rs = [analyse(N, ext, o) for o in OFFS]
        n16s = [r["n16"] for r in rs]
        print(f"\n{'='*90}\n{name}({N}) e{ext} [{tier}]  <n>={np.mean([r['n'] for r in rs]):.0f}  "
              f"<l>={np.mean([r['ell'] for r in rs]):.3f}\n{'='*90}")
        print(f"  hull area {agg('area',rs)}  diameter {agg('diam',rs)}  "
              f"aspect(r16) {agg('aspect',rs)}  usable16 area {agg('usable16',rs)}")
        print(f"  r16 common-set per offset: {n16s}  (min {min(n16s)})   "
              f"slab_min {agg('slab_min',rs)}  -> floor(>=400 & slab>=100): "
              f"{'PASS' if min(n16s)>=400 and min(r['slab_min'] for r in rs)>=100 else 'FAIL'}")
        print(f"  bin check: min inter-vertex dist {agg('dmin_ell',rs)} l  "
              f"(sub-edge<1 => diagonals exist)   bin1 occupancy {agg('bin1_mean',rs)}")
        print(f"  parity z_N: var(Re) {agg('varReZ',rs,'{:.4f}')}  var(Im) {agg('varImZ',rs,'{:.4f}')}  "
              f"cond {agg('zN_cond',rs,'{:.1f}')}  (high cond => near rank-one)")
        print(f"  parity (deg,voro): eig_min {agg('field_eig_min',rs,'{:.3f}')}  "
              f"eig_max {agg('field_eig_max',rs,'{:.3f}')}  cond {agg('field_cond',rs,'{:.2f}')}  "
              f"deg_var {agg('deg_var',rs,'{:.3f}')}  voro_var {agg('voro_var',rs,'{:.5f}')}")
    print("\nDONE_CHECKS")


if __name__ == "__main__":
    main()
