#!/usr/bin/env python3
"""make_figure.py -- figures/paths.png: greedy walkers get trapped; ribbon walkers cross the world."""
import os, json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "results", "paths.json")))["figure"]
SURF, INK, INK2, TILE = "#fcfcfb", "#0b0b0b", "#52514e", "#d9d8d3"
BLUE, ORANGE = "#2a78d6", "#eb6834"
VIEW = 24

fig, ax = plt.subplots(figsize=(8, 8.5), dpi=150)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
ax.add_collection(LineCollection(D["edges"], colors=TILE, linewidths=0.6))


def clip(path):
    return [p for p in path if abs(p[0]) < VIEW and abs(p[1]) < VIEW]


first = True
for rb in D["ribbons"]:
    pts = clip(rb)
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=BLUE, lw=2.2, solid_capstyle="round",
            label="ribbon walker: straight in the hidden grid; crosses the whole world" if first else None)
    first = False
first = True
for lp in D["loops"]:
    if lp["rule"] != "STRAIGHT":
        continue
    pts = clip(lp["path"])
    if len(pts) < len(lp["path"]):
        continue
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=ORANGE, lw=2.2, solid_capstyle="round",
            label="greedy 'go as straight as possible' walker: trapped in a loop" if first else None)
    ax.plot(pts[0][0], pts[0][1], "o", ms=7, mfc=SURF, mec=ORANGE, mew=2)
    first = False
ax.set_xlim(-VIEW, VIEW); ax.set_ylim(-VIEW, VIEW); ax.set_aspect("equal")
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("Which paths does the Penrose geometry allow?", color=INK, loc="left",
             fontsize=13, fontweight="bold", pad=30)
ax.text(0, 1.012, "Grey: the tiling. Orange: short-sighted walkers (open circle = start) loop forever.\n"
        "Blue: momentum in the hidden grid, one walker per line family; each crosses the whole world.",
        transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
leg = ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, -0.01), fontsize=9)
for t in leg.get_texts():
    t.set_color(INK)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.subplots_adjust(left=0.04, right=0.96, top=0.905, bottom=0.075)
fig.savefig(os.path.join(HERE, "figures", "paths.png"), facecolor=SURF)
print("wrote figures/paths.png")
