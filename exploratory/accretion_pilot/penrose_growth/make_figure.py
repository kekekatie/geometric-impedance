#!/usr/bin/env python3
"""make_figure.py -- figures/growth.png: the growing now, coloured by when each house joined."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "results", "penrose_growth.json")))
SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
SEQ = LinearSegmentedColormap.from_list("blue_seq", ["#bcd6f5", "#2a78d6", "#0d3a73"])  # one hue, light->dark
VIEW = 60

panels = [("RAY_QUEUE", "RAY · queue clock", "momentum alone: a line that runs off the world"),
          ("RAY_DICE", "RAY · dice", "the same line"),
          ("FORK_QUEUE", "FORK · queue clock (imports nothing)", "momentum + branching: round, 11 gaps pending"),
          ("FORK_DICE", "FORK · dice", "rougher: roundness 0.74, 34 gaps pending")]
fig, axes = plt.subplots(2, 2, figsize=(9, 9.6), dpi=150)
fig.patch.set_facecolor(SURF)
for ax, (key, title, sub) in zip(axes.flat, panels):
    pts = D[key]["pts"]; n = len(pts)
    ax.set_facecolor(SURF)
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], c=list(range(n)), cmap=SEQ,
               s=2.2 if n > 1000 else 5, lw=0)
    ax.set_xlim(-VIEW, VIEW); ax.set_ylim(-VIEW, VIEW); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#e4e3df")
    ax.set_title(f"{title}\n", color=INK, fontsize=10.5, fontweight="bold", loc="left")
    ax.text(0, 1.012, f"{sub} ({n:,} houses)", transform=ax.transAxes, color=INK2, fontsize=8.5,
            va="bottom")
fig.suptitle("The growing now on the Penrose tiling", color=INK, fontsize=13.5,
             fontweight="bold", x=0.03, ha="left", y=0.985)
fig.text(0.03, 0.955, "Each dot is a house held by the now, shaded by when it joined (light = early, "
         "dark = late). Nothing ever leaves.", color=INK2, fontsize=9, ha="left")
fig.subplots_adjust(left=0.03, right=0.97, top=0.9, bottom=0.02, hspace=0.18, wspace=0.06)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.savefig(os.path.join(HERE, "figures", "growth.png"), facecolor=SURF)
print("wrote figures/growth.png")
