#!/usr/bin/env python3
"""make_figure.py -- figures/embiggening.png: how much SPACE does the growing NOW occupy, per clock?"""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "results", "geometric_clock.json")))["B"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"          # palette slots 1-3

fig, ax = plt.subplots(figsize=(8, 5), dpi=160)
fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
T = [s[0] for s in D["SWEEP"]["series"]]
ax.plot(T, [s[1] for s in D["SWEEP"]["series"]], color=INK2, lw=1, ls=(0, (4, 3)),
        label="more now: active vertices A = t + 2 (every clock)")
ax.plot(T, [s[2] for s in D["SWEEP"]["series"]], color=BLUE, lw=2,
        label="SWEEP clock (geometric): space = now, one new house per event")
ax.plot(T, [s[2] for s in D["HAND"]["series"]], color=ORANGE, lw=0, marker="o", ms=5,
        mfc=SURF, mec=ORANGE, mew=1.5, label="HAND clock (geometric): the same, less 1")
for k, ser in enumerate(D["DICE_all"]):
    ax.plot([s[0] for s in ser], [s[2] for s in ser], color=AQUA, lw=2 if k == 0 else 1,
            alpha=1 if k == 0 else 0.55,
            label="DICE clock, 5 seeds: space creeps like √t, the now crowds" if k == 0 else None)
ax.annotate("SWEEP", (T[-1], D["SWEEP"]["series"][-1][2]), xytext=(6, 0),
            textcoords="offset points", va="center", color=INK, fontsize=10, fontweight="bold")
last = max(ser[-1][2] for ser in D["DICE_all"])
ax.annotate("DICE", (T[-1], last), xytext=(6, 0), textcoords="offset points", va="center",
            color=INK, fontsize=10, fontweight="bold")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("events t", color=INK2)
ax.set_ylabel("houses of the hidden street held by the now", color=INK2)
ax.set_title("Does the growing now become more space?", color=INK, loc="left",
             fontsize=13, fontweight="bold", pad=22)
ax.text(0, 1.015, "k=2 TICK growth from one legal pair; the now never loses a house, under every clock",
        transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
ax.grid(True, color=GRID, lw=0.8, which="major"); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GRID)
ax.tick_params(colors=INK2, which="both")
ax.set_xlim(8, 7000)
leg = ax.legend(frameon=False, loc="upper left", fontsize=8.5)
for t in leg.get_texts():
    t.set_color(INK)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "figures", "embiggening.png"), facecolor=SURF)
print("wrote figures/embiggening.png")
