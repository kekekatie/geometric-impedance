#!/usr/bin/env python3
"""make_figure.py -- two figures from results/penrose_address.json:
  figures/window_by_type.png  where in the hidden window each kind of vertex lives (small multiples)
  figures/information.png     how many distinct neighbourhoods exist at each radius: 1-D vs 2-D
"""
import os, json, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "results", "penrose_address.json")))
SURF, INK, INK2, GRID, FAINT = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#d9d8d3"
BLUE, ORANGE = "#2a78d6", "#eb6834"
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)

# ---------------- 1. the hidden window, one panel per vertex type --------------------
pts = D["perp_by_star"]
types = collections.Counter(p[3] for p in pts)
order = sorted(types, key=lambda t: (len(eval(t)), -types[t]))
layers = sorted({p[2] for p in pts})
fig, axes = plt.subplots(len(order), len(layers), figsize=(2.0 * len(layers), 1.95 * len(order)),
                         dpi=150)
fig.patch.set_facecolor(SURF)
for r, t in enumerate(order):
    for c, L in enumerate(layers):
        ax = axes[r][c]; ax.set_facecolor(SURF)
        allL = [(p[0], p[1]) for p in pts if p[2] == L]
        mine = [(p[0], p[1]) for p in pts if p[2] == L and p[3] == t]
        ax.scatter([x for x, _ in allL], [y for _, y in allL], s=0.6, color=FAINT, lw=0)
        if mine:
            ax.scatter([x for x, _ in mine], [y for _, y in mine], s=0.9, color=BLUE, lw=0)
        ax.set_xlim(-1.75, 1.75); ax.set_ylim(-1.75, 1.75); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        if r == 0:
            ax.set_title(f"layer {L}", color=INK2, fontsize=9)
        if c == 0:
            ax.set_ylabel(f"degree {len(eval(t))}\n({types[t]} vertices)", color=INK, fontsize=8.5)
fig.suptitle("Where in the hidden window does each kind of vertex live?", color=INK,
             fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.995)
fig.text(0.02, 0.975, "Penrose tiling, 31,306 vertices. Each row lights up (blue) one of the 7 vertex types;\n"
         "grey = every vertex of that layer. Every type owns its own regions of the window.",
         color=INK2, fontsize=8.5, ha="left", va="top")
fig.tight_layout(rect=(0, 0, 1, 0.958))
fig.savefig(os.path.join(HERE, "figures", "window_by_type.png"), facecolor=SURF)

# ---------------- 2. information per radius: 1-D vs 2-D -------------------------------
c1, c2 = D["counts1d"], D["counts2d"]; rs = list(range(1, len(c1) + 1))
fig, ax = plt.subplots(figsize=(8, 5), dpi=160)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
ax.plot(rs, c2, color=BLUE, lw=2, marker="o", ms=6, mec=SURF, mew=1.5,
        label=f"2-D Penrose (5-D → 2-D): grows like r^{D['alpha2']:.1f} here")
ax.plot(rs, c1, color=ORANGE, lw=2, marker="o", ms=6, mec=SURF, mew=1.5,
        label="1-D Fibonacci (2-D → 1-D): exactly 2r + 1")
for r, y in ((rs[-1], c2[-1]), (rs[-1], c1[-1])):
    ax.annotate(f"{y:,}", (r, y), xytext=(8, 0), textcoords="offset points", va="center",
                color=INK, fontsize=10, fontweight="bold")
ax.set_yscale("log")
ax.set_xlabel("radius r (steps along edges)", color=INK2)
ax.set_ylabel("distinct neighbourhoods of radius r", color=INK2)
ax.set_title("One step closer to E8: how much pattern information?", color=INK, loc="left",
             fontsize=13, fontweight="bold", pad=22)
ax.text(0, 1.015, "complete counts (every neighbourhood seen more than once); at r=7 the 2-D tiling has ~97× more",
        transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GRID)
ax.tick_params(colors=INK2, which="both")
ax.set_xlim(0.6, 7.9)
leg = ax.legend(frameon=False, loc="center right", fontsize=9)
for t in leg.get_texts():
    t.set_color(INK)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "figures", "information.png"), facecolor=SURF)
print("wrote figures/window_by_type.png, figures/information.png")
