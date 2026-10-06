#!/usr/bin/env python3
"""EXPLORATORY (post hoc, after Part C): decapod worlds fit the true window with zero slack. Which vertices sit ON the
window boundary, and where are they in the tiling? Also: how the result depends on window orientation (the reference
tiling alone left a tie). Writes results/boundary_EXPLORATORY.txt and figures/window_boundary.png."""
import os, json, math, cmath, collections
from multiprocessing import Pool
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import window_cells as WC
M, D, L, S = WC.M, WC.D, WC.L, WC.S
EPS, MAIN = 1e-6, (1, -1, 1, -1)          # MAIN = the orientation part_c chose (the only one the fillable worlds fit)
FIG = os.path.join(WC.HERE, "figures")


def lines_through(P, tol=0.03, min_pts=4):
    """greedy: straight lines (any direction) holding >= min_pts of the points P (complex, edge units)."""
    P = list(P); found = []
    while len(P) >= min_pts:
        best = None
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                d = P[j] - P[i]; u = d / abs(d)
                on = [k for k, p in enumerate(P) if abs(((p - P[i]) * u.conjugate()).imag) < tol]
                if best is None or len(on) > len(best[0]):
                    best = (on, u, P[i])
        if len(best[0]) < min_pts:
            break
        on, u, p0 = best
        dist0 = abs(((0 - p0) * u.conjugate()).imag)          # how far the line passes from the centre
        found.append((len(on), round(math.degrees(cmath.phase(u)) % 180, 1), round(dist0, 2)))
        P = [p for k, p in enumerate(P) if k not in set(on)]
    return found, len(P)


def task(args):
    s, kind, ring, wins = args
    tiles, _, g, st = M.grow(ring, 800, D.SEED0 + 100 * s, wall=True)
    K, pos, conf = M.lift(tiles); pr = WC.points_by_rank(K); vs = sorted(pr)
    per = []
    for sg, win in wins:
        sa, t = WC.fit([pr[v] for v in vs], win)
        per.append((sg, round(sa, 4), sum(WC.violation(*pr[v], t, win) > -EPS for v in vs)))
    win = WC.window(MAIN); sa, t = WC.fit([pr[v] for v in vs], win)
    on = [v for v in vs if WC.violation(*pr[v], t, win) > -EPS]
    found, left = lines_through([pos[v] / S for v in on])
    return dict(seed=s, kind=kind, per=per, n=len(vs), n_on=len(on), lines=found, off_line=left,
                rad=sorted(round(abs(pos[v]) / S, 2) for v in on), tiles=tiles,
                on=[(pos[v] / S, pr[v][0], pr[v][1] - t) for v in on], all=[(pr[v][0], pr[v][1] - t) for v in vs])


def figure(res):
    SURF, INK, MUTED, TILE, HOT, DOT = "#fcfcfb", "#0b0b0b", "#52514e", "#d6d5cf", "#d6402b", "#9a9890"
    pick = [r for r in res if r["seed"] in (3, 0)]
    win = WC.window(MAIN)
    fig, axes = plt.subplots(2, 5, figsize=(21, 9), facecolor=SURF, gridspec_kw=dict(width_ratios=[1.6, 1, 1, 1, 1]))
    for row, r in enumerate(sorted(pick, key=lambda r: r["kind"])):
        ax = axes[row, 0]
        polys = [[(z.real / S, z.imag / S) for z in t[1:]] for t in r["tiles"]]
        ax.add_collection(PolyCollection(polys, facecolors="#00000000", edgecolors=TILE, linewidths=0.35))
        if r["on"]:
            ax.scatter([p.real for p, _, _ in r["on"]], [p.imag for p, _, _ in r["on"]], s=18, color=HOT, zorder=3)
        ax.set_xlim(-11, 11); ax.set_ylim(-11, 11); ax.set_aspect("equal"); ax.axis("off")
        name = "Decapod world (seed 3)" if r["kind"] == "DECAPOD" else "Ordinary world (fillable seed 0)"
        ax.set_title(f"{name}: {r['n_on']} of {r['n']} vertices on the window's edge", color=INK, fontsize=12, loc="left")
        for k in range(4):
            a = axes[row, 1 + k]; n, h = win[k]; R = h / math.cos(math.pi / 5)
            ang = sorted(math.atan2(ny, nx) - math.pi / 5 for nx, ny in n)        # corner angles, in order round the pentagon
            vx = [R * math.cos(q) for q in ang + ang[:1]]; vy = [R * math.sin(q) for q in ang + ang[:1]]
            a.plot(vx, vy, color=INK, lw=1)
            zs = [z for rk, z in r["all"] if rk == k]; hs = [z for _, rk, z in r["on"] if rk == k]
            a.scatter([z.real for z in zs], [z.imag for z in zs], s=5, color=DOT)
            a.scatter([z.real for z in hs], [z.imag for z in hs], s=16, color=HOT, zorder=3)
            a.set_xlim(-1.75, 1.75); a.set_ylim(-1.75, 1.75); a.set_aspect("equal"); a.axis("off")
            a.set_title(f"hidden window, layer {k + 1}", color=MUTED, fontsize=10)
    fig.suptitle("Where each vertex sits in the true Penrose window (pentagons). Red: exactly on the window's edge.",
                 color=INK, fontsize=14, x=0.01, ha="left")
    os.makedirs(FIG, exist_ok=True)
    plt.savefig(os.path.join(FIG, "window_boundary.png"), dpi=130, facecolor=SURF, bbox_inches="tight")


if __name__ == "__main__":
    ref = [t for t in L.REF if max(abs(z) for z in t[1:]) < 10 * S]
    K, pos, conf = M.lift(ref); pts = list(WC.points_by_rank(K).values())
    combos = [(a, b, c, d) for a in (1, -1) for b in (1, -1) for c in (1, -1) for d in (1, -1)]
    ref_s = {sg: WC.fit(pts, WC.window(sg))[0] for sg in combos}
    good = [sg for sg in combos if ref_s[sg] <= WC.TOL]
    seeds, _ = WC.seeds_and_ok(); by = {x["seed"]: x for x in seeds}
    saved = json.load(open(os.path.join(WC.HERE, "..", "perp_map", "results", "m2_worlds.json")))
    with Pool(4) as p:
        out = p.map(task, [(x["seed"], x["kind"], WC.ring_of(by[x["seed"]]), [(sg, WC.window(sg)) for sg in good]) for x in saved])
    lines = [f"EXPLORATORY: orientations fitting the reference tiling (s* <= {WC.TOL}): " + ", ".join(f"{sg} s*={ref_s[sg]:+.4f}" for sg in good),
             f"  main orientation {MAIN}; per world: (orientation, s*, vertices on boundary) for each candidate orientation"]
    for r in out:
        lines.append(f"  {r['kind']:8s} seed {r['seed']:3d}: {[(sg, a, n) for sg, a, n in r['per']]}")
        lines.append(f"      under {MAIN}: {r['n_on']}/{r['n']} vertices on the boundary; straight lines with >= 4 of them "
                     f"(count, direction deg, distance from centre in edges): {r['lines']}; not on such a line: {r['off_line']}")
        lines.append(f"      their radii (edges): {r['rad']}")
    print("\n".join(lines))
    open(os.path.join(WC.RES, "boundary_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
    figure(out)
