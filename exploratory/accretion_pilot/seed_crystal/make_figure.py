#!/usr/bin/env python3
"""make_figure.py -- figures/seeds.png: how likeness depth trades against availability and distance."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "results", "seed_crystal.json")))
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
COL = {"QUEUE": "#2a78d6", "DICE": "#eb6834"}
LAB = {"QUEUE": "queue clock", "DICE": "dice"}

fig, axes = plt.subplots(1, 3, figsize=(12, 4.4), dpi=150)
fig.patch.set_facecolor(SURF)
panels = [("have", "gaps that already have a twin seed (%)", False),
          ("dist", "world distance to the nearest seed", False),
          ("wdist", "hidden-window distance to it", False)]
for ax, (key, ylab, _) in zip(axes, panels):
    ax.set_facecolor(SURF)
    for c in ("QUEUE", "DICE"):
        rows = D["rows"][c]["rows"]
        xs = [r["r"] for r in rows]
        ys = [100 * r["have"] / r["n"] for r in rows] if key == "have" else [r[key] for r in rows]
        ax.plot(xs, ys, color=COL[c], lw=2, marker="o", ms=5, mec=SURF, mew=1.5, label=LAB[c])
    ax.set_xlabel("likeness depth r (how much neighbourhood must match)", color=INK2, fontsize=8.5)
    ax.set_title(ylab, color=INK, fontsize=10, loc="left")
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8.5)
axes[0].set_ylim(0, 105)
leg = axes[0].legend(frameon=False, loc="lower left", fontsize=9)
for t in leg.get_texts():
    t.set_color(INK)
fig.suptitle("Seed crystals: the deeper the likeness, the rarer and farther the twin - "
             "and the closer in the hidden window", color=INK, fontsize=12, fontweight="bold",
             x=0.01, ha="left", y=0.99)
fig.text(0.01, 0.905, f"Gaps in the growing 2-D now (all filled later by the roads anyway). "
         f"A random same-layer 'dust' vertex fits a gap only {100 * D['dust']:.0f}% of the time.",
         color=INK2, fontsize=9, ha="left")
fig.subplots_adjust(left=0.05, right=0.98, top=0.8, bottom=0.14, wspace=0.28)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.savefig(os.path.join(HERE, "figures", "seeds.png"), facecolor=SURF)
print("wrote figures/seeds.png")
