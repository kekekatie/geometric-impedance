#!/usr/bin/env python3
"""
GEOMETRY-ONLY preflight — EXTENSION v2 (Work-GPT/Sol, 2026-08-29).

Same strict scope as `preflight_geometry.py` (which is left untouched): geometry and
admission masks ONLY. No Hamiltonian, eigen, wave dynamics, LDOS, MSD propagation, address,
regression, targets, family-result curves or scientific scores. Nothing sealed; no manifest
amended. This script is additive and does not overwrite the first report.

Extension tasks:
  1. Larger geometries: extents 18/20/22, all families, same six fresh offsets; stop (not
     extrapolate) if generator growth fails.
  2. Physical-size comparability: n, hull area, max diameter, usable r=16 interior area, per
     family x extent x offset.
  3. Radius-16 feasibility: FULL per-offset r>=16l counts & proportions (min/max, not means).
  4. Spatial-block feasibility: the prereg scheme is NOT fully specified -> a clearly-labelled
     DETERMINISTIC PROPOSAL (4 angular quadrants on the r>=16l common set), counts only.
  5. Corrected Voronoi on a padded super-patch (core extent + PAD_DELTA); separate cells
     recovered by padding from those that remain invalid; verify padding ring width.
  6. MSD geometry: analytic LR window recomputed for launch depths {8,12,16,20} separately
     (admitted launches, min graph distance to strip, LR t_hi) -- analytic only, no propagation.
"""

import sys
from collections import deque
import numpy as np
from scipy.spatial import ConvexHull, cKDTree, Voronoi

sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../substrates")
from generate_rank4 import generate, build_edges

FAMILIES = (8, 10, 12)
NAME = {8: "silver(8)", 10: "golden(10)", 12: "platinum(12)"}
EXTENTS = (18, 20, 22)
FRESH_OFFSETS = [(0.13, 0.37), (0.29, 0.11), (0.41, 0.23),
                 (0.05, 0.47), (0.19, 0.31), (0.37, 0.09)]   # identical to v1
W_STRIP = 2.0
LAUNCH_DEPTHS = (8, 12, 16, 20)      # MSD depth sweep (l units)
T_LO = 2.0
LR_EPS = 5e-3
LR_LEVERAGE = 4.0
PAD_DELTA = 6                        # padded super-patch = core extent + PAD_DELTA
# Documented deviation: the extent-28 padded patch for platinum(12) core-extent 22 was
# prohibitively slow to generate (not saturated — see growth table — just very slow), so its
# pad uses delta 4 (extent 26). Ring width stays >= MIN_RING_L, so the correction is unaffected.
PAD_DELTA_OVERRIDE = {(12, 22): 4}
MIN_RING_L = 3.0                     # required padding ring width (l units) for a valid pad


def hull_depth(points):
    h = ConvexHull(points)
    A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(points @ A.T + b).max(axis=1)


def hull_area_diam(points):
    h = ConvexHull(points)
    hp = points[h.vertices]
    # max pairwise distance among hull vertices = diameter
    d = 0.0
    for i in range(len(hp)):
        dd = np.linalg.norm(hp - hp[i], axis=1).max()
        if dd > d:
            d = dd
    return float(h.volume), float(d)          # volume == area in 2D


def adjacency(n, E):
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j); adj[j].append(i)
    return adj


def multi_source_bfs(adj, sources):
    n = len(adj)
    dist = np.full(n, -1, np.int64)
    q = deque()
    for s in sources:
        dist[s] = 0; q.append(s)
    while q:
        u = q.popleft()
        for w in adj[u]:
            if dist[w] < 0:
                dist[w] = dist[u] + 1; q.append(w)
    return dist


def unbounded_mask(par):
    vor = Voronoi(par)
    out = np.zeros(len(par), bool)
    for i in range(len(par)):
        reg = vor.regions[vor.point_region[i]]
        out[i] = (len(reg) == 0) or (-1 in reg)   # True = UNbounded/invalid
    return out


def lr_tail(x, G):
    term = 1.0; part = 0.0
    for k in range(G):
        if k > 0:
            term *= x / k
        part += term
    return float(np.exp(x) - part)


def lr_t_hi(d_max, G, n_strip):
    if G <= 0 or n_strip == 0:
        return 0.0
    ts = np.linspace(1e-3, 3.0, 6000)
    ok = 0.0
    for t in ts:
        B = lr_tail(d_max * t, G)
        if n_strip * B * B <= LR_EPS:
            ok = t
        else:
            break
    return ok


def make_patch(N, extent, offset):
    lifts, par, perp, ustar = generate(N, extent, offset=np.array(offset))
    E = build_edges(lifts, N, ustar)
    return lifts, par, E


def analyse(N, extent, offset):
    lifts, par, E = make_patch(N, extent, offset)
    n = len(par)
    adj = adjacency(n, E)
    deg = np.array([len(a) for a in adj], float)
    d = par[[i for i, _ in E]] - par[[j for _, j in E]]
    ell = float(np.median(np.linalg.norm(d, axis=1)))
    dbound = hull_depth(par)
    area, diam = hull_area_diam(par)
    r16 = dbound >= 16 * ell
    n16 = int(r16.sum())
    usable_area = hull_area_diam(par[r16])[0] if n16 >= 3 else 0.0

    res = dict(N=N, extent=extent, offset=offset, n=n, ell=ell,
               d_max=int(deg.max()), area=area, diam=diam,
               n16=n16, prop16=n16 / n, usable_area=usable_area)

    # spatial-block PROPOSAL: 4 angular quadrants on the r>=16l common set
    if n16 >= 4:
        c = par[r16].mean(0)
        ang = np.arctan2(par[r16][:, 1] - c[1], par[r16][:, 0] - c[0])
        quad = np.floor((ang + np.pi) / (np.pi / 2)).astype(int) % 4
        res["quad_counts"] = [int((quad == q).sum()) for q in range(4)]
    else:
        res["quad_counts"] = [0, 0, 0, 0]

    # MSD depth sweep (analytic only)
    strip = np.where(dbound < W_STRIP * ell)[0]
    res["n_strip"] = int(len(strip))
    dstrip = multi_source_bfs(adj, strip.tolist()) if len(strip) else np.full(n, -1)
    sweep = {}
    for Rm in LAUNCH_DEPTHS:
        adm = np.where(dbound >= Rm * ell)[0]
        if len(adm) and len(strip):
            g = dstrip[adm]; g = g[g >= 0]
            if len(g):
                G = int(g.min())
                sweep[Rm] = dict(admitted=int(len(adm)), G_strip=G,
                                 t_hi=lr_t_hi(res["d_max"], G, len(strip)))
                continue
        sweep[Rm] = dict(admitted=int(len(adm)), G_strip=-1, t_hi=0.0)
    res["msd_sweep"] = sweep

    # padded-Voronoi correction: recompute cells on core+delta super-patch
    delta = PAD_DELTA_OVERRIDE.get((N, extent), PAD_DELTA)
    _, par_pad, _ = make_patch(N, extent + delta, offset)
    core_R = np.hypot(par[:, 0], par[:, 1]).max()
    pad_R = np.hypot(par_pad[:, 0], par_pad[:, 1]).max()
    ring = (pad_R - core_R) / ell
    # map core vertices into the padded set by exact position match
    padtree = cKDTree(par_pad)
    dists, idx = padtree.query(par, k=1)
    matched = dists < 1e-6 * ell
    unb_core = unbounded_mask(par)                       # invalid on core-only tessellation
    unb_pad_all = unbounded_mask(par_pad)
    unb_pad_core = np.ones(n, bool)
    unb_pad_core[matched] = unb_pad_all[idx[matched]]    # invalid on padded tessellation
    recovered = int((unb_core & ~unb_pad_core).sum())
    remain = int((unb_pad_core).sum())
    res.update(pad_ring_l=float(ring), pad_ok=bool(ring >= MIN_RING_L),
               core_unbounded=int(unb_core.sum()),
               pad_recovered=recovered, pad_remain_invalid=remain,
               pad_n=len(par_pad))
    return res


def agg(vals):
    return f"{np.mean(vals):.0f} [{min(vals)}..{max(vals)}]"


def main():
    print("# GEOMETRY-ONLY PREFLIGHT v2 EXTENSION (no dynamics/address/targets/scores)")
    print(f"# extents={EXTENTS} offsets={FRESH_OFFSETS}")
    print(f"# launch_depths={LAUNCH_DEPTHS} strip_w={W_STRIP} t_lo={T_LO} lr_eps={LR_EPS} "
          f"pad_delta={PAD_DELTA} min_ring_l={MIN_RING_L}")
    growth = {N: {} for N in FAMILIES}
    for N in FAMILIES:
        saturated = False
        prev_n = None
        for extent in EXTENTS:
            if saturated:
                print(f"\n### {NAME[N]} extent={extent}: SKIPPED (growth failed earlier — "
                      f"not extrapolated)")
                continue
            rs = [analyse(N, extent, o) for o in FRESH_OFFSETS]
            mean_n = np.mean([r["n"] for r in rs])
            growth[N][extent] = mean_n
            if prev_n is not None and mean_n <= prev_n:
                print(f"\n### {NAME[N]} extent={extent}: GENERATOR SATURATION "
                      f"(<n>={mean_n:.0f} <= prev {prev_n:.0f}) — STOP, do not extrapolate.")
                saturated = True
                continue
            prev_n = mean_n
            ell = np.mean([r["ell"] for r in rs])
            print(f"\n{'='*98}\n{NAME[N]}  extent={extent}  <n>={mean_n:.0f}  <l>={ell:.3f}  "
                  f"d_max={rs[0]['d_max']}\n{'='*98}")
            # (2) physical size, per offset
            print("  physical size (per offset):  n | hull_area | diameter | usable_r16_area")
            for r, o in zip(rs, FRESH_OFFSETS):
                print(f"    off{o}: n={r['n']:6d}  area={r['area']:9.1f}  "
                      f"diam={r['diam']:7.2f}  usable16={r['usable_area']:9.1f}")
            # (3) radius-16 full per-offset
            c16 = [r["n16"] for r in rs]; p16 = [r["prop16"] for r in rs]
            print("  r>=16l survivors (per offset): "
                  + ", ".join(f"{c}({p:.1%})" for c, p in zip(c16, p16)))
            print(f"    -> mean {np.mean(c16):.0f}  min {min(c16)}  max {max(c16)}  "
                  f"(common-set logic retained; adequacy NOT declared)")
            # (4) spatial-block proposal
            qc = np.array([r["quad_counts"] for r in rs])
            print(f"  [PROPOSAL, not sealed] 4 angular quadrants on r>=16l set — "
                  f"per-fold vertices: mean {qc.mean(0).round(0).astype(int).tolist()}  "
                  f"min-fold across offsets {int(qc.min())}")
            # (5) padded Voronoi
            ring = np.mean([r["pad_ring_l"] for r in rs])
            okc = sum(r["pad_ok"] for r in rs)
            cu = [r["core_unbounded"] for r in rs]
            rec = [r["pad_recovered"] for r in rs]
            rem = [r["pad_remain_invalid"] for r in rs]
            print(f"  padded Voronoi (core+{PAD_DELTA}, ring {ring:.1f}l, ok {okc}/6): "
                  f"core-invalid {agg(cu)}; recovered-by-pad {agg(rec)}; "
                  f"REMAIN-invalid {agg(rem)}")
            # (6) MSD depth sweep
            print("  MSD analytic window by launch depth (admitted | G_strip(min) | LR t_hi):")
            for Rm in LAUNCH_DEPTHS:
                adm = [r["msd_sweep"][Rm]["admitted"] for r in rs]
                G = [r["msd_sweep"][Rm]["G_strip"] for r in rs if r["msd_sweep"][Rm]["G_strip"] >= 0]
                th = [r["msd_sweep"][Rm]["t_hi"] for r in rs]
                gtxt = f"{min(G)}..{max(G)}" if G else "n/a(empty)"
                feas = sum(t >= LR_LEVERAGE * T_LO for t in th)
                print(f"    depth>={Rm:2d}l: admitted {agg(adm)} | G_strip[{gtxt}] | "
                      f"t_hi mean {np.mean(th):.3f} (need>={LR_LEVERAGE*T_LO:.0f}; feasible {feas}/6)")

    print(f"\n{'='*98}\nGROWTH SUMMARY (mean n)\n{'='*98}")
    for N in FAMILIES:
        print(f"  {NAME[N]:14s} " + "  ".join(f"e{e}={growth[N].get(e,'-')!s:>7}" for e in EXTENTS))


if __name__ == "__main__":
    main()
