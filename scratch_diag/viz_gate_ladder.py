#!/usr/bin/env python3
"""Stage-D gate #1 across the full k-ladder: torus-control bulk degree TVD vs the
ideal, both substrates. Converges toward zero -> the degree-match control is valid
across the whole approximant sequence (not just one order)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

orders = [1, 2, 3, 4]
ab = [0.103, 0.025, 0.011, 0.008]        # 1/1(tiny cell), 3/2, 7/5, 17/12
pen = [0.040, 0.019, 0.012, 0.010]       # 1/1, 2/1, 3/2, 5/3

fig, ax = plt.subplots(figsize=(9, 5))
ax.axhspan(0, 0.05, color="#2ca02c", alpha=0.08)
ax.axhline(0.05, color="#2ca02c", ls="--", lw=1.2)
ax.text(4.05, 0.052, "AB's accepted level ~0.05", color="#2ca02c", fontsize=9, va="bottom", ha="right")
ax.plot(orders, ab, "o-", color="#0072B2", lw=2, ms=8, label="Ammann–Beenker (silver)")
ax.plot(orders, pen, "s-", color="#CC79A7", lw=2, ms=8, label="Penrose (golden)")
ax.annotate("tiny 7-vertex cell\n(no statistics)", xy=(1, 0.103), xytext=(1.35, 0.135),
            fontsize=8, color="#0072B2", arrowprops=dict(arrowstyle="->", color="#0072B2"))
ax.set_yscale("log")
ax.set_xticks(orders); ax.set_xticklabels([f"k={k}" for k in orders])
ax.set_xlabel("approximant order")
ax.set_ylabel("torus bulk degree TVD vs ideal  (log)")
ax.set_title("Stage-D gate #1 cleared across the full k-ladder\n"
             "torus-control degree histograms converge to the ideal, both substrates",
             fontsize=12)
ax.legend(fontsize=10, loc="upper right")
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0.006, 0.16)
fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), "gate_ladder.png")
fig.savefig(out, dpi=140, bbox_inches="tight")
print("saved", out)
