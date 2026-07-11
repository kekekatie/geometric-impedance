#!/usr/bin/env python3
"""Stage-D control-validity gate #1: does the approximant degree histogram match
the ideal? Uses the histograms e0c already computed (no rebuild). Penrose shows a
systematic, real (not boundary) deficit in degree-5 and degree-7 vertices."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IDEAL, APPROX = "#0072B2", "#D55E00"
d = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                                "approximant", "e0c_results.json")))

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
panels = [("penrose", ["2/1", "5/3"]), ("ammann_beenker", ["3/2", "17/12"])]
for ax, (sub, convs) in zip(axes, panels):
    # average approx over the listed orders; ideal is the same reference
    degs = list(range(2, 9))
    ih = d["substrates"][sub][convs[0]]["ideal_deg_hist"]
    iv = np.array([ih.get(str(k), 0) for k in degs], float); iv /= iv.sum()
    av = np.zeros(len(degs))
    for c in convs:
        ah = d["substrates"][sub][c]["approx_deg_hist"]
        a = np.array([ah.get(str(k), 0) for k in degs], float); a /= a.sum()
        av += a
    av /= len(convs)
    x = np.arange(len(degs)); w = 0.38
    ax.bar(x - w/2, iv, w, color=IDEAL, label="ideal tiling")
    ax.bar(x + w/2, av, w, color=APPROX, label=f"approximant (avg {', '.join(convs)})")
    tvd = 0.5*np.abs(iv-av).sum()
    ax.set_title(f"{sub}   (degree TVD ≈ {tvd:.2f})", fontsize=12)
    ax.set_xticks(x); ax.set_xticklabels(degs)
    ax.set_xlabel("vertex coordination (degree)")
    ax.legend(fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("fraction of interior vertices")
# annotate the Penrose deficit
axes[0].annotate("approximant short on\ndegree-5 and degree-7",
                 xy=(3, 0.33), xytext=(4.3, 0.42), fontsize=9, color=APPROX,
                 arrowprops=dict(arrowstyle="->", color=APPROX))
fig.suptitle("Stage-D gate #1: approximant vs ideal degree histogram\n"
             "AB matches well (~0.05); Penrose has a real, systematic gap (~0.07-0.12) — a materiality call",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
out = os.path.join(os.path.dirname(__file__), "degree_gate.png")
fig.savefig(out, dpi=135, bbox_inches="tight")
print("saved", out)
