#!/usr/bin/env python3
"""make_figure.py -- figures/complexity.png: how many different patterns does each rule write?"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "results", "complexity.json")))
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
COL = {"TICK": "#2a78d6", "CLONE": "#eb6834", "RANDOM": "#1baf7a"}      # palette slots 1-3
LAB = {"TICK": "TICK (topple): n+1, never repeats, costs nothing",
       "CLONE": "CLONE (copy): record freezes",
       "RANDOM": "RANDOM: noise, costs ~0.96 bits/symbol"}

fig, ax = plt.subplots(figsize=(8, 5), dpi=160)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
for r in ("RANDOM", "TICK", "CLONE"):
    ys = D[r]["complexity"]; xs = list(range(1, len(ys) + 1))
    pts = [(x, y) for x, y in zip(xs, ys) if y > 0]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=COL[r], lw=2,
            marker="o", ms=5, mec=SURF, mew=1.5, label=LAB[r])
    x, y = pts[-1]
    off = (-6, 14) if r == "CLONE" else (6, 0)
    ax.annotate(r, (x, y), xytext=off, textcoords="offset points", va="center",
                ha="right" if r == "CLONE" else "left",
                color=INK, fontsize=10, fontweight="bold")
ax.set_yscale("log")
ax.set_xlabel("pattern length n (tiles)", color=INK2)
ax.set_ylabel("different patterns of length n written", color=INK2)
ax.set_title("What does a collapsed universe keep writing?", color=INK, loc="left",
             fontsize=13, fontweight="bold", pad=22)
ax.text(0, 1.015, "100 worlds × 40-site Fibonacci chain; each surviving pair writes 400 more events",
        transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GRID)
ax.tick_params(colors=INK2)
ax.set_xlim(0.5, 13.8)
leg = ax.legend(frameon=False, loc="upper left", fontsize=9)
for t in leg.get_texts():
    t.set_color(INK)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "figures", "complexity.png"), facecolor=SURF)
print("wrote figures/complexity.png")
