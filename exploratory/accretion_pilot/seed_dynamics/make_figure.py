#!/usr/bin/env python3
"""make_figure.py -- figures/arms.png: mean gaps per arm (8 dice-driven replicates, mean +- sd)."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results", "seed_dynamics.json")))["replicates"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8986"
arms = [("NONE_0", "no seeds", GREY), ("DUST_0", "dust\n(no likeness)", AQUA),
        ("TWIN_2", "twin r=2", BLUE), ("FAKE_2", "fake r=2", ORANGE),
        ("TWIN_4", "twin r=4", BLUE), ("FAKE_4", "fake r=4", ORANGE),
        ("TWIN_6", "twin r=6", BLUE), ("FAKE_6", "fake r=6", ORANGE)]
fig, ax = plt.subplots(figsize=(9, 4.8), dpi=160)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
for i, (k, lab, col) in enumerate(arms):
    m, sd = R[k]["gaps"]
    ax.errorbar([i], [m], yerr=[sd], fmt="o", ms=9, color=col, mec=SURF, mew=1.5,
                ecolor=col, elinewidth=2, capsize=4)
    ax.annotate(f"{m:.1f}", (i, m), xytext=(10, 0), textcoords="offset points", va="center",
                color=INK, fontsize=9)
ax.set_xticks(range(len(arms))); ax.set_xticklabels([a[1] for a in arms], fontsize=9, color=INK2)
ax.set_ylabel("gaps in the growing now (mean over snapshots)", color=INK2, fontsize=9)
ax.set_ylim(0, 36)
ax.set_title("Seeds close gaps - but real twins do no better than fakes or dust", color=INK,
             loc="left", fontsize=12.5, fontweight="bold", pad=22)
ax.text(0, 1.015, "8 dice-driven runs per arm, mean ± sd. Blue = real twins, orange = fake twins "
        "(shuffled labels), green = no likeness at all.", transform=ax.transAxes, color=INK2,
        fontsize=8.5, va="bottom")
ax.grid(True, axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GRID)
ax.tick_params(colors=INK2)
fig.tight_layout()
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.savefig(os.path.join(HERE, "figures", "arms.png"), facecolor=SURF)
print("wrote figures/arms.png")
