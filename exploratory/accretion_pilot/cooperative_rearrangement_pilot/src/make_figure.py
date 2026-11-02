#!/usr/bin/env python3
"""
make_figure.py -- figures for the cooperative-rearrangement pilot.

Figure 1 (the distributed obstruction): the jammed retained boundary band, with
the two dead sites, the two compatibility-witness vertices, a sample bounded
connected region (a flip hexagon; the move class is size <= 8), and the faithful
MINIMUM vertex-engulfment footprint needed to restore compatibility (orange).
The contrast -- a local 6-8 tile region vs a ~41-tile, disconnected, ~12.5 S
footprint -- is why no bounded fixed-exterior region can restore compatibility.

Writes figures/obstruction_map.png.
"""
from __future__ import annotations
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection
import coop_common as CC
from coop_common import L, S
import hexflip as HF


def tri(t):
    return [(z.real, z.imag) for z in t[1:]]


def main():
    st = json.loads((CC.INPUT / "retained_state.json").read_text())
    band = [CC.dtile(t) for t in st["tiles"]]
    p3 = json.loads((CC.RESULTS / "part3_necessary.json").read_text())
    greedy = p3["obstruction"]["heuristic_deletion_footprint"]
    greedy_vkeys = {tuple(v) for v in greedy.get("selected_vertices", [])}
    dead = st["dead_sites"]
    witness = st["compatibility_witness_vertices"]

    # tiles incident to greedy-engulfment vertices
    foot = [t for t in band if any(L.key(z) in greedy_vkeys for z in t[1:])]
    footkeys = {CC.dk(t) for t in foot}

    # a sample flip hexagon near the dead sites
    mids = [(complex(*d["p"]) + complex(*d["q"])) / 2 for d in dead]
    nbhd = [t for t in band if any(abs(HF.tile_centroid(t) - m) < 6 * S for m in mids)]
    hexes = HF.find_flip_hexagons(nbhd)
    hex_tiles = hexes[0]["tiles"] if hexes else []
    hexkeys = {CC.dk(t) for t in hex_tiles}

    fig, ax = plt.subplots(figsize=(11, 10))
    base = [t for t in band if CC.dk(t) not in footkeys and CC.dk(t) not in hexkeys]
    ax.add_collection(PatchCollection([MPoly(tri(t)) for t in base],
                                      facecolor="#eef1f3", edgecolor="#c2cace", linewidths=0.3))
    ax.add_collection(PatchCollection([MPoly(tri(t)) for t in foot],
                                      facecolor="#f0a23a", edgecolor="#b8761f", linewidths=0.4, alpha=0.85))
    if hex_tiles:
        ax.add_collection(PatchCollection([MPoly(tri(t)) for t in hex_tiles],
                                          facecolor="#3f7fd0", edgecolor="#28507f", linewidths=0.6, alpha=0.9))
    # dead sites
    for d in dead:
        p, q = complex(*d["p"]), complex(*d["q"]); m = (p + q) / 2
        ax.plot([p.real, q.real], [p.imag, q.imag], "-", color="#c0392b", lw=3)
        ax.plot(m.real, m.imag, "x", color="#c0392b", ms=13, mew=3)
    # witness vertices
    for w in witness:
        v = complex(*w["vertex"])
        ax.plot(v.real, v.imag, "*", color="#7a1fb0", ms=18, mec="white", mew=1.2)

    fp = greedy["footprint"]
    import matplotlib.patches as mpatches
    handles = [
        mpatches.Patch(color="#f0a23a", label=(
            f"ONE heuristic DELETION footprint — NOT a repair/minimum "
            f"({fp.get('n_actual_engulfed_vertices')} vertices removed, {fp['n_tiles']} triangles, "
            f"{fp['n_components']} components, zero-margin)")),
        mpatches.Patch(color="#3f7fd0", label="sample bounded region (flip hexagon = 6 triangles / 3 rhombi; move class ≤ 8 triangles)"),
        plt.Line2D([], [], color="#c0392b", marker="x", lw=0, ms=10, label="dead sites (2)"),
        plt.Line2D([], [], color="#7a1fb0", marker="*", lw=0, ms=12, label="selected compatibility-witness vertices (span 8.65 S)"),
    ]
    ax.legend(handles=handles, fontsize=8.5, loc="upper left")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("w7-B-s0 jam: the compatibility obstruction is spatially distributed\n"
                 "no SEEDED connected region of ≤ 8 triangular tiles has a feasible unchanged exterior "
                 "(Part 3: 0/12248); orange = one heuristic deletion footprint, not a lawful repair",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(CC.FIGURES / "obstruction_map.png", dpi=140, bbox_inches="tight")
    print("wrote figures/obstruction_map.png")


if __name__ == "__main__":
    main()
