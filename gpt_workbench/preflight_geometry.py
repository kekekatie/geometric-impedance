#!/usr/bin/env python3
"""
GEOMETRY-ONLY feasibility preflight for the radius-saturation + MSD manifests.

Authorised design-only step (Work-GPT/Sol, 2026-08-28). STRICTLY geometry and admission
masks: it builds the tilings and computes convex-hull depth, degree, Voronoi cells and
graph distances only. It uses NO Hamiltonian, NO eigen-decomposition, NO time evolution,
NO LDOS/MSD, NO perpendicular-space address, NO regression, NO targets and NO outcome
curves. It seals nothing and alters no manifest.

Outputs (per family x extent x fresh offset):
  1. surviving interior counts/proportions at radii r in {2,4,8,12,16} under d_bound >= r*l;
  2. the common r=16 interior population;
  3. Voronoi guard-ring losses (unbounded cells; cells failing the d_bound>=2l margin;
     censored-neighbour load on r=16 centres) reported separately;
  4. MSD time-window geometric feasibility: d_max, |STRIP|, graph distance to STRIP
     (G_strip), and the analytic Lieb-Robinson-admissible t_hi vs t_lo=2 -- computed WITHOUT
     any wave dynamics (pure series bound);
  5. generator saturation / patch-growth check across extents (esp. platinum/12-fold).
"""

import sys
from collections import deque

import numpy as np
from scipy.spatial import ConvexHull, cKDTree, Voronoi

sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../substrates")
from generate_rank4 import generate, build_edges

# ---- FROZEN CONFIGURATION (fixed before running; not tuned to any result) ---------------- #
FAMILIES = (8, 10, 12)                     # silver, golden, platinum
NAME = {8: "silver(8)", 10: "golden(10)", 12: "platinum(12)"}
EXTENTS = (12, 14, 16)
RADII = (2, 4, 8, 12, 16)                  # r*l interior masks (edge units)
# six FRESH offsets, disjoint from transport_run.OFFSETS
# [(0.31,0.19),(0.07,0.41),(0.23,0.05),(0.44,0.28),(0.16,0.33)]
FRESH_OFFSETS = [(0.13, 0.37), (0.29, 0.11), (0.41, 0.23),
                 (0.05, 0.47), (0.19, 0.31), (0.37, 0.09)]
W_STRIP = 2.0                              # boundary strip width (MSD manifest, l units)
MARGIN_VORO = 2.0                          # Voronoi guard-ring margin (l units)
R_MIN = 8.0                                # MSD launch interior depth (l units)
T_LO = 2.0                                 # MSD fit-window lower bound
LR_EPS = 5e-3                              # LR union-bound leakage cap (MSD manifest)
LR_LEVERAGE = 4.0                          # required t_hi/t_lo


def hull_depth(points):
    """Signed distance of each point to the boundary of its own convex hull (>0 inside)."""
    h = ConvexHull(points)
    A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(points @ A.T + b).max(axis=1)


def adjacency(n, E):
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j); adj[j].append(i)
    return adj


def multi_source_bfs(adj, sources):
    """Graph distance from the nearest source vertex to every vertex."""
    n = len(adj)
    dist = np.full(n, -1, dtype=np.int64)
    q = deque()
    for s in sources:
        dist[s] = 0; q.append(s)
    while q:
        u = q.popleft()
        for w in adj[u]:
            if dist[w] < 0:
                dist[w] = dist[u] + 1; q.append(w)
    return dist


def bounded_cells(par):
    """Boolean per-vertex: is its Voronoi cell bounded (no vertex at infinity)?"""
    vor = Voronoi(par)
    out = np.zeros(len(par), bool)
    for i in range(len(par)):
        reg = vor.regions[vor.point_region[i]]
        out[i] = len(reg) > 0 and (-1 not in reg)
    return out


def lr_series_tail(x, G, kmax=400):
    """Sum_{k>=G} x^k/k!  (=> e^x minus the low-order partial sum), stable for our x range."""
    # partial sum_{k=0}^{G-1}
    term = 1.0; part = 0.0
    for k in range(G):
        if k > 0:
            term *= x / k
        part += term
    return float(np.exp(x) - part)


def lr_t_hi(d_max, G_strip, n_strip):
    """Largest t with n_strip * (Sum_{k>=G}(d_max t)^k/k!)^2 <= LR_EPS. Pure geometry+series."""
    if G_strip <= 0 or n_strip == 0:
        return 0.0
    ts = np.linspace(1e-3, 3.0, 6000)
    ok = 0.0
    for t in ts:
        B = lr_series_tail(d_max * t, G_strip)
        if n_strip * B * B <= LR_EPS:
            ok = t
        else:
            break
    return ok


def run_patch(N, extent, offset):
    lifts, par, perp, ustar = generate(N, extent, offset=np.array(offset))
    n = len(par)
    E = build_edges(lifts, N, ustar)
    adj = adjacency(n, E)
    deg = np.array([len(a) for a in adj], float)
    # edge unit l = median edge length
    d = par[[i for i, _ in E]] - par[[j for _, j in E]]
    ell = float(np.median(np.linalg.norm(d, axis=1))) if len(E) else float("nan")
    dbound = hull_depth(par)

    res = {"N": N, "extent": extent, "offset": offset, "n": n, "n_edges": len(E),
           "ell": ell, "d_max": int(deg.max()) if n else 0,
           "deg_mean": float(deg.mean()) if n else float("nan")}

    # (1) interior counts at each radius
    res["radius_counts"] = {r: int((dbound >= r * ell).sum()) for r in RADII}
    res["radius_props"] = {r: res["radius_counts"][r] / n for r in RADII}

    # (3) Voronoi guard-ring losses
    bnd = bounded_cells(par)
    guard_valid = bnd & (dbound >= MARGIN_VORO * ell)
    res["voro_unbounded"] = int((~bnd).sum())
    res["voro_unbounded_prop"] = float((~bnd).mean())
    res["voro_guard_invalid"] = int((~guard_valid).sum())
    res["voro_guard_invalid_prop"] = float((~guard_valid).mean())
    # censored-neighbour load on the r=16 admitted centres
    centres16 = np.where(dbound >= 16 * ell)[0]
    res["n_centres16"] = int(len(centres16))
    if len(centres16):
        tree = cKDTree(par)
        loads, any_cens = [], 0
        for c in centres16:
            nb = tree.query_ball_point(par[c], 16 * ell)
            bad = int((~guard_valid[np.array(nb)]).sum())
            loads.append(bad); any_cens += (bad > 0)
        res["centre16_mean_censored_nbrs"] = float(np.mean(loads))
        res["centre16_frac_with_censored"] = float(any_cens / len(centres16))
    else:
        res["centre16_mean_censored_nbrs"] = float("nan")
        res["centre16_frac_with_censored"] = float("nan")

    # (4) MSD time-window geometric feasibility (no dynamics)
    strip = np.where(dbound < W_STRIP * ell)[0]
    admitted = np.where(dbound >= R_MIN * ell)[0]
    res["n_strip"] = int(len(strip))
    res["n_admitted_launch"] = int(len(admitted))
    if len(strip) and len(admitted):
        dstrip = multi_source_bfs(adj, strip.tolist())
        gvals = dstrip[admitted]
        gvals = gvals[gvals >= 0]
        if len(gvals):
            G_strip = int(gvals.min())
            res["G_strip_min"] = G_strip
            res["G_strip_median"] = float(np.median(gvals))
            t_hi = lr_t_hi(res["d_max"], G_strip, len(strip))
            res["lr_t_hi"] = t_hi
            res["lr_feasible"] = bool(t_hi >= LR_LEVERAGE * T_LO)
        else:
            res["G_strip_min"] = -1; res["G_strip_median"] = float("nan")
            res["lr_t_hi"] = 0.0; res["lr_feasible"] = False
    else:
        res["G_strip_min"] = -1; res["G_strip_median"] = float("nan")
        res["lr_t_hi"] = 0.0; res["lr_feasible"] = False
    return res


def main():
    print("# GEOMETRY-ONLY PREFLIGHT  (no dynamics, no address, no targets)")
    print(f"# frozen: radii={RADII} extents={EXTENTS} strip_w={W_STRIP} "
          f"voro_margin={MARGIN_VORO} R_min={R_MIN} t_lo={T_LO} lr_eps={LR_EPS} "
          f"lr_leverage={LR_LEVERAGE}")
    print(f"# fresh offsets: {FRESH_OFFSETS}")
    all_res = []
    for N in FAMILIES:
        for extent in EXTENTS:
            patch_res = []
            for off in FRESH_OFFSETS:
                r = run_patch(N, extent, off)
                patch_res.append(r); all_res.append(r)
            # aggregate across the 6 offsets for this (family, extent)
            n_mean = np.mean([r["n"] for r in patch_res])
            ell_mean = np.mean([r["ell"] for r in patch_res])
            dmax_mode = int(np.median([r["d_max"] for r in patch_res]))
            print(f"\n{'='*94}\n{NAME[N]}  extent={extent}  "
                  f"<n>={n_mean:.0f}  <l>={ell_mean:.3f}  d_max~{dmax_mode}  "
                  f"(6 fresh offsets)\n{'='*94}")
            print("  interior survivors  count (proportion)  [min..max over offsets]")
            for rr in RADII:
                cs = [r["radius_counts"][rr] for r in patch_res]
                ps = [r["radius_props"][rr] for r in patch_res]
                print(f"    r>={rr:2d}l : {np.mean(cs):8.0f} ({np.mean(ps):5.1%})   "
                      f"[{min(cs):5d}..{max(cs):5d}]")
            c16 = [r["n_centres16"] for r in patch_res]
            print(f"  COMMON r=16 interior population: mean {np.mean(c16):.0f}  "
                  f"[{min(c16)}..{max(c16)}]  (per offset)")
            vu = [r["voro_unbounded_prop"] for r in patch_res]
            vg = [r["voro_guard_invalid_prop"] for r in patch_res]
            print(f"  Voronoi: unbounded {np.mean(vu):.1%}   "
                  f"guard-invalid (unbounded OR depth<{MARGIN_VORO:.0f}l) {np.mean(vg):.1%}")
            if max(c16) > 0:
                ml = np.nanmean([r["centre16_mean_censored_nbrs"] for r in patch_res])
                fc = np.nanmean([r["centre16_frac_with_censored"] for r in patch_res])
                print(f"  r=16 centres censored-neighbour load: mean {ml:.1f} bad nbrs; "
                      f"{fc:.1%} of centres touch a censored cell")
            gs = [r["G_strip_min"] for r in patch_res if r["G_strip_min"] >= 0]
            th = [r["lr_t_hi"] for r in patch_res]
            adm = [r["n_admitted_launch"] for r in patch_res]
            feas = [r["lr_feasible"] for r in patch_res]
            gtxt = f"{min(gs)}..{max(gs)}" if gs else "n/a"
            print(f"  MSD launch (d_bound>={R_MIN:.0f}l): mean admitted {np.mean(adm):.0f}  "
                  f"| G_strip(min) [{gtxt}]  | LR t_hi mean {np.mean(th):.3f} "
                  f"(need >= {LR_LEVERAGE*T_LO:.0f})  | feasible: {sum(feas)}/6 offsets")

    # (5) generator saturation / patch growth across extents
    print(f"\n{'='*94}\nPATCH-GROWTH / SATURATION CHECK (mean n over 6 offsets)\n{'='*94}")
    for N in FAMILIES:
        row = []
        for extent in EXTENTS:
            ns = [r["n"] for r in all_res if r["N"] == N and r["extent"] == extent]
            row.append(np.mean(ns))
        grew = all(row[i] < row[i + 1] for i in range(len(row) - 1))
        print(f"  {NAME[N]:14s} extents {EXTENTS} -> n = "
              f"{[int(x) for x in row]}   monotone-growth: {grew}")


if __name__ == "__main__":
    main()
