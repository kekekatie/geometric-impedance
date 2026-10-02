#!/usr/bin/env python3
"""Figure: a decapod world and an ordinary (fillable) world at 4,000 tiles, with the ten ribbons traced from the decagon."""
import os, json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import worm_lines as WL

SURF, INK, MUTED, TILE_EDGE, RIBBON = "#fcfcfb", "#0b0b0b", "#52514e", "#c9c8c2", "#2a78d6"
seeds = json.load(open(os.path.join(WL.D.RES, "seeds.json")))
pick = {2: "Decapod world (seed 2): no guesses", 0: "Ordinary world (fillable seed 0): 3 guesses"}
fig, axes = plt.subplots(1, 2, figsize=(12, 6.2), facecolor=SURF)
for ax, (s, title) in zip(axes, pick.items()):
    x = next(v for v in seeds if v["seed"] == s)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    tiles, _, _, _ = WL.M.grow(ring, WL.N_TILES, WL.D.SEED0 + 100 * s, wall=True)
    et = WL.build(tiles)
    polys = [[(z.real / WL.S, z.imag / WL.S) for z in t[1:]] for t in tiles]
    ax.add_collection(PolyCollection(polys, facecolors="none", edgecolors=TILE_EDGE, linewidths=0.3))
    for e in WL.D.EDGES:
        r = WL.trace(e, et)
        ax.plot([z.real / WL.S for z in r], [z.imag / WL.S for z in r], color=RIBBON, lw=2, solid_capstyle="round")
    dec = [(v.real / WL.S, v.imag / WL.S) for v in WL.D.V] + [(WL.D.V[0].real / WL.S, WL.D.V[0].imag / WL.S)]
    ax.plot(*zip(*dec), color=INK, lw=1.2)
    ax.set_xlim(-24, 24); ax.set_ylim(-24, 24); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, color=INK, fontsize=12, loc="left")
fig.suptitle("The ten ribbons (half-worms) traced outward from the decagon, 4,000 half-tiles", color=INK, fontsize=13, x=0.02, ha="left")
fig.text(0.02, 0.02, "Blue: ribbons traced rhomb by rhomb through parallel edges. Grey: tile outlines. Black: the decagon (never filled).",
         color=MUTED, fontsize=9)
fig.savefig(os.path.join(WL.RES, "..", "figures", "worm_lines.png"), dpi=150, facecolor=SURF, bbox_inches="tight")
print("saved")
