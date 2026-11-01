#!/usr/bin/env python3
"""
make_figures.py -- a small number of diagnostic figures. No repair was attempted
(Phase 3 found no legal move), so there is no before/after pair; instead we draw,
for two B jams, the retained active skin with (a) the dead frontier sites and
(b) the eligible-but-illegal three-rhombus flip hexagons marked. This visualises
the Phase-3 finding: geometric flips sit right at the dead sites, but decorated
matching vetoes them.

Outputs ../figures/jam_wK-B-sN.png.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection
import pilot_common as PC
from pilot_common import L, D, S
import phase3_repair as P3
import hexflip as HF

FIG = Path(__file__).resolve().parent.parent / "figures"
CASES = [(7, 0, 23), (5, 0, 42)]


def tri_poly(t):
    return [(z.real, z.imag) for z in t[1:]]


def draw(world, si, js):
    forks = P3.load_forks()
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = PC.streams_for(world)[si]
    P, rng = P3.replay_to_trigger(Sstar, B, stream, js)
    skin = list(P.tris)
    deads = P3.dead_sites(P)
    dead_vkeys = set()
    for e in deads:
        dead_vkeys.add(L.key(e[0])); dead_vkeys.add(L.key(e[1]))
    true_fr = {frozenset((L.key(e[0]), L.key(e[1]))) for e in P.frontier()}
    dead_mids = [(e[0] + e[1]) / 2 for e in deads]
    nbhd = [t for t in skin if any(abs(sum(t[1:]) / 3 - m) < 5 * S for m in dead_mids)]
    hexes = HF.find_flip_hexagons(nbhd)

    fig, ax = plt.subplots(figsize=(8, 8))
    # skin tiles by type
    pats0 = [MPoly(tri_poly(t)) for t in skin if t[0] == 0]
    pats1 = [MPoly(tri_poly(t)) for t in skin if t[0] == 1]
    ax.add_collection(PatchCollection(pats0, facecolor="#dce1e4", edgecolor="#929da3", linewidths=0.3))
    ax.add_collection(PatchCollection(pats1, facecolor="#eef1f3", edgecolor="#929da3", linewidths=0.3))
    # eligible flip hexagons (interior & touch a dead vertex)
    for h in hexes:
        bverts = set(h["bverts"])
        boundary, cyc = HF._hexagon_boundary(h["tiles"])
        interior = not any(ek in true_fr for ek in boundary)
        if interior and (bverts & dead_vkeys):
            poly = [(complex(*k).real, complex(*k).imag) for k in cyc]
            ax.add_patch(MPoly(poly, closed=True, fill=True, facecolor="#d66a34",
                               alpha=0.35, edgecolor="#d66a34", linewidth=1.5))
            vz = complex(*h["vertex"])
            ax.plot(vz.real, vz.imag, "o", color="#713c91", ms=4)
    # dead sites
    for e in deads:
        xs = [e[0].real, e[1].real]; ys = [e[0].imag, e[1].imag]
        ax.plot(xs, ys, "-", color="#c0392b", linewidth=3)
        m = (e[0] + e[1]) / 2
        ax.plot(m.real, m.imag, "x", color="#c0392b", ms=10, mew=2)
    ax.set_aspect("equal")
    # zoom to the dead-site neighbourhood
    cx = sum(m.real for m in dead_mids) / len(dead_mids)
    cy = sum(m.imag for m in dead_mids) / len(dead_mids)
    R = 9 * S
    ax.set_xlim(cx - R, cx + R); ax.set_ylim(cy - R, cy + R)
    ax.set_title(f"w{world}-B-s{si}: jam at step {js}\n"
                 f"red = dead frontier sites; orange = eligible 3-rhombus flip hexagons "
                 f"(all vetoed by decorated matching)")
    ax.axis("off")
    FIG.mkdir(parents=True, exist_ok=True)
    out = FIG / f"jam_w{world}-B-s{si}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def main():
    for (w, si, js) in CASES:
        draw(w, si, js)


if __name__ == "__main__":
    main()
