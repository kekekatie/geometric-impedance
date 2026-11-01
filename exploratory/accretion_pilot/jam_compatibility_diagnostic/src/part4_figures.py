#!/usr/bin/env python3
"""
part4_figures.py -- figures + spatial analysis for the IIS (Part 4).

Figure A (per state): retained tiles, BOTH boundary components (true growth
frontier vs edges merely exposed by pruning), the zero-candidate dead sites, and
the tiles/vertices supplying the IIS constraints.
Figure B: the IIS constraints drawn in internal (perp/offset) space, showing the
binding half-planes have no common point.

Also computes spatial stats: distance between IIS origin vertices, and their
distance to the dead sites (concentrated at the notch vs separated across the ring).

Outputs ../figures/part4_*.png and ../results/part4_spatial.json.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection
import study_common as SC
from study_common import Sl, PC, L, D, M, WIN
import feas
import part4_iis as P4

FIG = Path(__file__).resolve().parent.parent / "figures"
OUT = Path(__file__).resolve().parent.parent / "results"


def boundaries(full, skin):
    """true frontier edge-keys (from the full patch) vs pruning-exposed inner
    boundary edge-keys (skin boundary that is not true frontier)."""
    true_fr = {frozenset((L.key(e[0]), L.key(e[1]))) for e in L.Patch(full).frontier()}
    skin_b = {frozenset((L.key(e[0]), L.key(e[1]))) for e in L.Patch(skin).frontier()}
    exposed = skin_b - true_fr
    true_in_skin = skin_b & true_fr
    return true_in_skin, exposed


def dead_sites(skin):
    P = L.Patch(skin)
    return [e for e in P.frontier() if len(D.candidates(P, *e[:3])) == 0]


def tri(t):
    return [(z.real, z.imag) for z in t[1:]]


def draw_patch(ax, skin, full, prov, title):
    pats = [MPoly(tri(t)) for t in skin]
    ax.add_collection(PatchCollection(pats, facecolor="#e7ebee", edgecolor="#aab4bb", linewidths=0.3))
    true_in_skin, exposed = boundaries(full, skin)
    ekpts = {}
    for e in L.Patch(skin).frontier():
        ekpts[frozenset((L.key(e[0]), L.key(e[1])))] = (e[0], e[1])
    for ek in true_in_skin:
        p, q = ekpts[ek]; ax.plot([p.real, q.real], [p.imag, q.imag], "-", color="#2b7a3d", lw=1.6)
    for ek in exposed:
        p, q = ekpts[ek]; ax.plot([p.real, q.real], [p.imag, q.imag], "-", color="#b8912f", lw=1.0, alpha=0.8)
    for e in dead_sites(skin):
        m = (e[0] + e[1]) / 2
        ax.plot([e[0].real, e[1].real], [e[0].imag, e[1].imag], "-", color="#c0392b", lw=3)
        ax.plot(m.real, m.imag, "x", color="#c0392b", ms=11, mew=2.5)
    # IIS origin tiles + vertices
    for p in prov["prov"]:
        vz = complex(*p["origin_vertex"])
        ax.plot(vz.real, vz.imag, "o", color="#6a1fb0", ms=9, mec="white", mew=1)
        for td in p["tiles_at_origin"]:
            c = td["centroid"]; ax.plot(c[0], c[1], ".", color="#6a1fb0", ms=4)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=10)


def draw_perp(ax, cmax, origin, iis, title):
    # draw each rank's window pentagon and the binding IIS half-planes; shade infeasibility
    for key in iis:
        rk, i = key
        n, h = WIN[rk]
        # window pentagon for this rank (centered at origin in offset space): {u: n_j.u <= h}?
        # we draw the binding half-plane line n_i.t = c and its feasible side arrow
        c = cmax[key]; nx, ny = float(n[i][0]), float(n[i][1])
        # a line n.t = c
        d = np.array([-ny, nx])  # direction along the line
        p0 = np.array([nx, ny]) * c  # a point on the line (n unit)
        seg = np.array([p0 - 3 * d, p0 + 3 * d])
        ax.plot(seg[:, 0], seg[:, 1], "-", lw=1.8, label=f"rk{rk} e{i}")
        ax.annotate("", xy=(p0 + 0.5 * np.array([nx, ny])), xytext=(p0),
                    arrowprops=dict(arrowstyle="->", color="gray"))
    ax.set_aspect("equal"); ax.set_title(title, fontsize=10); ax.legend(fontsize=7, loc="upper right")
    ax.axhline(0, color="#ddd", lw=0.5); ax.axvline(0, color="#ddd", lw=0.5)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    forks = SC.P3.load_forks()
    prov_all = json.loads((OUT / "part4_provenance.json").read_text())
    spatial = []
    for (w, si, js, first_inf) in [(7, 0, 23, 9), (5, 0, 42, 17)]:
        B = forks[w]["cs"][1]; stream = PC.streams_for(w)[si]
        arm = PC.grow(forks[w]["Sstar"], B, stream, 44)
        snaps = arm["snaps"]
        full9 = snaps[first_inf]
        skin, _ = PC.skin_of(snaps[-1])
        full_jam = snaps[-1]

        labA = f"w{w}-first_infeasible_full@{first_inf}"
        labB = f"w{w}-jam_trigger_skin@{js}"
        provA = prov_all[labA]; provB = prov_all[labB]

        fig, axes = plt.subplots(1, 2, figsize=(14, 7))
        draw_patch(axes[0], [t for t in full9], full9, provA,
                   f"w{w} step {first_inf}: first infeasible (full)\n"
                   "green=true frontier, gold=pruning-exposed, red=dead site, purple=conflict vertex")
        draw_patch(axes[1], skin, full_jam, provB,
                   f"w{w} step {js}: jam-trigger skin")
        # zoom both to the dead-site region of the jam skin
        ds = dead_sites(skin)
        if ds:
            mid = sum((e[0] + e[1]) / 2 for e in ds) / len(ds)
            for ax in axes:
                ax.set_xlim(mid.real - 12 * SC.S, mid.real + 12 * SC.S)
                ax.set_ylim(mid.imag - 12 * SC.S, mid.imag + 12 * SC.S)
        fig.tight_layout(); fig.savefig(FIG / f"part4_w{w}_patch.png", dpi=140, bbox_inches="tight")
        plt.close(fig)

        # spatial stats for the jam-skin IIS
        vs = [complex(*p["origin_vertex"]) for p in provB["prov"]]
        dmid = [ (e[0]+e[1])/2 for e in ds ]
        pair_dist = max((abs(a - b) / SC.S for a in vs for b in vs), default=0.0)
        to_dead = [min(abs(v - m) / SC.S for m in dmid) for v in vs] if dmid else []
        spatial.append(dict(case=f"w{w}", jam_skin_iis_vertices=len(vs),
                            max_pairwise_distance_S=round(pair_dist, 2),
                            iis_vertex_dist_to_nearest_dead_S=[round(x, 2) for x in to_dead],
                            concentrated_near_notch=bool(to_dead and max(to_dead) <= 4.0)))
        print(f"w{w}: IIS vertices span {pair_dist:.2f} S; distances to nearest dead site "
              f"{[round(x,2) for x in to_dead]} S", flush=True)

    (OUT / "part4_spatial.json").write_text(json.dumps(spatial, indent=2, default=float))
    print("wrote figures and part4_spatial.json")


if __name__ == "__main__":
    main()
