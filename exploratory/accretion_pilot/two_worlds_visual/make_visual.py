#!/usr/bin/env python3
"""
make_visual.py -- EXPLORATORY picture (no predictions), suggested by Astra: one decapod world and one ordinary world,
side by side. Left: the physical tiling with five 72-degree sectors coloured. Right: the same vertices' hidden
(perp-space) addresses, one panel per layer, in the same colours. Matched region: vertices 2.5-11 edges from the centre
in both worlds (4,000 half-tiles each). The question to look at: are the coloured clouds similar shapes in different
places, or differently shaped clouds?
"""
import os, sys, json, math, cmath, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "perp_map"))
import perp_map as M
D, L, S = M.D, M.L, M.S

SURF, INK, MUTED, TILE = "#fcfcfb", "#0b0b0b", "#52514e", "#d6d5cf"
COLS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]      # validated (scripts/validate_palette.js, light)
NAMES = ["A", "B", "C", "D", "E"]
R_LO, R_HI, OFF0 = 2.5, 11.0, 32.0                                    # sector boundaries at 32 + 72k degrees
sector = lambda z: int(((math.degrees(cmath.phase(z)) - OFF0) % 360) // 72)

seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
worlds = [(3, "Decapod world (seed 3): no guesses"), (0, "Ordinary world (fillable seed 0): guesses")]
data = []
for s, title in worlds:
    x = next(v for v in seeds if v["seed"] == s)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    tiles, _, g, status = M.grow(ring, 4000, D.SEED0 + 100 * s, wall=True)
    K, pos, conf = M.lift(tiles)
    pts = [(sector(pos[v]), int(k.sum()), M.perp(k)) for v, k in K.items() if R_LO * S <= abs(pos[v]) <= R_HI * S]
    # the lift starts from an arbitrary vertex, so a world's absolute perp position is meaningless across worlds:
    # centre each layer's cloud on its own mean so that only SHAPES are compared
    cen = {l: sum(z for _, ll, z in pts if ll == l) / max(1, sum(1 for _, ll, _ in pts if ll == l)) for l in {ll for _, ll, _ in pts}}
    pts = [(sec, l, z - cen[l]) for sec, l, z in pts]
    data.append((s, title + f" ({len(g)})" if "guesses" in title and "no" not in title else title, tiles, pts, conf))
layers = sorted({l for _, _, pts, _ in [(d[0], d[1], d[3], d[4]) for d in data] for _, l, _ in pts})
fig, axes = plt.subplots(2, 1 + len(layers), figsize=(4.2 * (1 + len(layers)), 9), facecolor=SURF,
                         gridspec_kw=dict(width_ratios=[1.6] + [1] * len(layers)))
lim = {}
for l in layers:
    zs = [z for d in data for _, ll, z in d[3] if ll == l]
    lim[l] = (min(z.real for z in zs) - 0.15, max(z.real for z in zs) + 0.15, min(z.imag for z in zs) - 0.15, max(z.imag for z in zs) + 0.15)
counts = []
for row, (s, title, tiles, pts, conf) in enumerate(data):
    ax = axes[row, 0]
    polys, fcs = [], []
    for t in tiles:
        c = sum(t[1:]) / 3
        polys.append([(z.real / S, z.imag / S) for z in t[1:]])
        fcs.append(COLS[sector(c)] + "55" if R_LO * S <= abs(c) <= R_HI * S else "#00000000")
    ax.add_collection(PolyCollection(polys, facecolors=fcs, edgecolors=TILE, linewidths=0.25))
    for k in range(5):
        a = math.radians(OFF0 + 72 * k + 36)
        ax.text(13.2 * math.cos(a), 13.2 * math.sin(a), NAMES[k], color=INK, fontsize=12, ha="center", va="center", weight="bold")
    ax.set_xlim(-15, 15); ax.set_ylim(-15, 15); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, color=INK, fontsize=12, loc="left")
    for j, l in enumerate(layers):
        ax = axes[row, 1 + j]
        n_by = collections.Counter(sec for sec, ll, _ in pts if ll == l)
        for sec in range(5):
            zs = [z for ss, ll, z in pts if ll == l and ss == sec]
            ax.scatter([z.real for z in zs], [z.imag for z in zs], s=9, color=COLS[sec], edgecolors=SURF, linewidths=0.4, label=NAMES[sec])
        ax.set_xlim(*lim[l][:2]); ax.set_ylim(*lim[l][2:]); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color(TILE)
        ax.set_title(f"hidden addresses, layer {l}  (n = {sum(n_by.values())})", color=MUTED, fontsize=9, loc="left")
        counts.append((s, l, dict(sorted(n_by.items()))))
axes[0, 1].legend(title="sector", fontsize=8, title_fontsize=8, frameon=False, loc="upper left", bbox_to_anchor=(0, -0.02), ncol=5)
fig.suptitle("Two worlds, physical sectors (left) and the same vertices' hidden addresses (right), 2.5-11 edges out",
             color=INK, fontsize=14, x=0.01, ha="left")
fig.text(0.01, 0.01, "Each colour is one 72-degree slice of the world. Same colours in the hidden-address panels. Axes are shared between "
         "the two worlds for each layer; each world's clouds are centred on their own mean (absolute position is arbitrary). "
         "Exploratory picture; no prediction was registered.", color=MUTED, fontsize=9)
fig.savefig(os.path.join(HERE, "figures", "two_worlds.png"), dpi=140, facecolor=SURF, bbox_inches="tight")
with open(os.path.join(HERE, "figures", "two_worlds_counts.txt"), "w") as f:
    for c in counts:
        f.write(f"seed {c[0]} layer {c[1]}: vertices per sector {c[2]}\n")
print("saved; lift conflicts", [d[4] for d in data])
