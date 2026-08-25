#!/usr/bin/env python3
"""EXPLORATORY figure: a wave on the substrate (see wave_pilot.py). Not confirmatory."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from wave_pilot import analyse, NAME

FAM = {8: "#4c78a8", 10: "#e45756", 12: "#54a24b"}
res = {N: analyse(N, extent=12) for N in (8, 10, 12)}

fig = plt.figure(figsize=(15, 9))
gs = fig.add_gridspec(2, 3, hspace=0.32, wspace=0.28)

# (0,0) density of states, all three
ax = fig.add_subplot(gs[0, 0])
for N in (8, 10, 12):
    ax.hist(res[N]["evals"], bins=80, histtype="step", density=True,
            color=FAM[N], lw=1.8, label=NAME[N])
ax.set_title("density of states  (H = tiling adjacency)")
ax.set_xlabel("energy E"); ax.set_ylabel("DOS"); ax.legend(frameon=False)

# (0,1) localization spectrum: participation ratio vs energy
ax = fig.add_subplot(gs[0, 1])
for N in (8, 10, 12):
    r = res[N]
    ax.plot(r["evals"], r["pr"] / r["n"], ".", ms=2.2, color=FAM[N], alpha=0.55,
            label=NAME[N])
ax.set_title("localization vs energy  (low = localized)")
ax.set_xlabel("energy E"); ax.set_ylabel("participation ratio / N")
ax.legend(frameon=False, markerscale=4)

# (0,2) zoom on the E~0 pseudogap / confined states, golden
ax = fig.add_subplot(gs[0, 2])
r = res[10]
m = np.abs(r["evals"]) < 0.6
ax.plot(r["evals"][m], (r["pr"] / r["n"])[m], "o", ms=4, color=FAM[10])
ax.axvline(0, color="0.6", lw=0.8, ls="--")
ax.set_title("golden: states near E = 0 (confined)")
ax.set_xlabel("energy E"); ax.set_ylabel("participation ratio / N")


def state_map(ax, r, idx, title):
    par = r["par"]
    w = r["evecs"][:, idx]**2
    w = w / w.max()
    ax.scatter(par[:, 0], par[:, 1], c="0.85", s=3, linewidths=0)
    sc = ax.scatter(par[:, 0], par[:, 1], c=w, s=6 + 60 * w, cmap="magma",
                    vmin=0, vmax=1, linewidths=0)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title)
    return sc


# bottom row: three golden eigenstates — most localized, critical, extended
r = res[10]
order = np.argsort(r["pr"])
picks = [(order[0], "most localized"),
         (order[len(order) // 2], "typical / critical"),
         (order[-1], "most extended")]
for c, (idx, lab) in enumerate(picks):
    ax = fig.add_subplot(gs[1, c])
    sc = state_map(ax, r, idx, f"golden eigenstate — {lab}\nE = {r['evals'][idx]:.3f}, "
                                f"PR = {r['pr'][idx]:.0f} sites")
fig.colorbar(sc, ax=fig.axes[-3:], shrink=0.6, label="|ψ|² (normalised)")

fig.suptitle("EXPLORATORY — a coherent wave on the rank-4 substrates "
             "(tight-binding; address not inserted)", fontsize=13)
out = __file__.rsplit("/", 1)[0] + "/wave_pilot.png"
fig.savefig(out, dpi=130, bbox_inches="tight")
print("wrote", out)
