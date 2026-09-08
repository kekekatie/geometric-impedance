#!/usr/bin/env python3
"""Stacked partition of probability into consulted / waiting / gone, per horizon, for
each state -- a picture of 'delayed consultation of an already-present opportunity'."""
import os
from fractions import Fraction
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import contact_timing_checks as T

HERE = os.path.dirname(os.path.abspath(__file__))
COL = {"consulted": "#1a7f37", "waiting": "#d6a400", "gone": "#8a8a8a"}

reps = T.depth2_classes(); i, j = T.find_pair(reps)


def timing(G0):
    iQ = set(T.quiets(G0)); out = {}
    for h in (1, 2, 3):
        acc = {"consulted": Fraction(0), "waiting": Fraction(0), "gone": Fraction(0)}
        for seq, Gf, p in T.paths(G0, h):
            acc[T.classify(seq, Gf, iQ)] += p
        out[h] = acc
    return out


fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, (lab, G0, nopp) in zip(axes, [(str(i), reps[i], 1), (str(j), reps[j], 2)]):
    tm = timing(G0)
    hs = [1, 2, 3]
    bottoms = [0.0, 0.0, 0.0]
    for cat in ("consulted", "waiting", "gone"):
        vals = [float(tm[h][cat]) for h in hs]
        ax.bar(hs, vals, bottom=bottoms, color=COL[cat], label=cat, width=0.6,
               edgecolor="white")
        for k, h in enumerate(hs):
            if vals[k] > 0.045:
                ax.text(h, bottoms[k] + vals[k] / 2, str(tm[h][cat]),
                        ha="center", va="center", fontsize=8,
                        color="white" if cat != "waiting" else "#333")
        bottoms = [bottoms[k] + vals[k] for k in range(3)]
    ax.set_title(f"state {lab}  ({nopp} initial "
                 f"{'opportunity' if nopp == 1 else 'opportunities'})", fontsize=10)
    ax.set_xlabel("events elapsed (horizon)"); ax.set_xticks(hs)
    ax.set_ylim(0, 1)
axes[0].set_ylabel("probability")
axes[1].legend(loc="upper right", fontsize=8, framealpha=0.9)
fig.suptitle("Timing of the initial archive: consulted (green) / waiting = eligible-not-"
             "yet-consulted (amber) / gone = opportunity lost before consultation (grey)\n"
             "menus only shrink — 'waiting' is delayed consultation of an ALREADY-present "
             "opportunity, never newly-enabled relevance", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.9])
fig.savefig(os.path.join(HERE, "results", "timing_partition.png"), dpi=140)
print("wrote results/timing_partition.png")
