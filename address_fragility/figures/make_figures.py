#!/usr/bin/env python3
"""Figures for the address-fragility paper.

Palette: dataviz categorical slots 1-3, validated all-pairs light mode
(worst CVD dE 9.2, worst normal-vision dE 24.0). The aqua slot sits below 3:1
contrast on the light surface, so the relief rule applies and every series
carries a visible direct label.
"""
import sys, itertools
sys.path.insert(0, "../../substrates")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.spatial import ConvexHull
import generate_cyclotomic as GC

SURFACE   = "#fcfcfb"
INK       = "#0b0b0b"
INK_2     = "#52514e"
GRID      = "#dedcd6"
SILVER    = "#2a78d6"   # slot 1
GOLDEN    = "#eb6834"   # slot 2
PLATINUM  = "#1baf7a"   # slot 3

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.size": 9,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2,
    "xtick.color": INK_2, "ytick.color": INK_2,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "DejaVu Sans",
})

def tidy(ax):
    ax.grid(True, color=GRID, lw=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=3, width=0.6)

# ---------------------------------------------------------------- Figure 1
FIELDS = [(8, "8-fold", "silver  1+√2",   SILVER),
          (10, "10-fold", "golden  (1+√5)/2", GOLDEN),
          (12, "12-fold", "platinum  2+√3", PLATINUM)]

WIN = {}
for N, *_ in FIELDS:
    _, pm = GC.projections(N)
    sg = np.array(list(itertools.product([-0.5, 0.5], repeat=4))) @ pm
    WIN[N] = sg[ConvexHull(sg).vertices]
WLIM = 1.08 * max(np.abs(np.vstack(list(WIN.values()))).max(), 1e-9)

fig, axes = plt.subplots(2, 3, figsize=(9.0, 6.4))
for col, (N, name, ratio, colour) in enumerate(FIELDS):
    lifts, par, perp = GC.generate(N, 11)
    E = GC.build_edges(lifts)
    c = par.mean(0); r = np.linalg.norm(par - c, axis=1)
    keep = r <= np.quantile(r, 0.30)
    idx = {i for i in np.where(keep)[0]}

    ax = axes[0, col]
    segs = [(par[u], par[v]) for u, v in E if u in idx and v in idx]
    for a, b in segs:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=colour, lw=0.7, alpha=0.85,
                solid_capstyle="round")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{name}\n{ratio}", color=INK, fontsize=10, pad=8, linespacing=1.5)

    ax = axes[1, col]
    ax.add_patch(Polygon(WIN[N], closed=True, facecolor=colour, alpha=0.13,
                         edgecolor=colour, lw=1.6))
    sub = perp[np.random.default_rng(0).choice(len(perp), min(2200, len(perp)), replace=False)]
    ax.scatter(sub[:, 0], sub[:, 1], s=1.1, color=colour, alpha=0.5, linewidths=0)
    ax.set_xlim(-WLIM, WLIM); ax.set_ylim(-WLIM, WLIM)
    ax.set_aspect("equal"); ax.axis("off")

axes[0, 0].text(-0.06, 0.5, "parallel space\n(the tiling)", transform=axes[0,0].transAxes,
                rotation=90, va="center", ha="center", color=INK_2, fontsize=9)
axes[1, 0].text(-0.06, 0.5, "perpendicular space\n(the address)", transform=axes[1,0].transAxes,
                rotation=90, va="center", ha="center", color=INK_2, fontsize=9)
fig.suptitle("Three quasicrystals at matched perpendicular dimension",
             color=INK, fontsize=12, y=0.98)
fig.text(0.5, 0.015, "All three arise from Z⁴ with a two-dimensional perpendicular space. "
         "Only the cyclotomic field differs.", ha="center", color=INK_2, fontsize=8.5)
fig.tight_layout(rect=[0.02, 0.035, 1, 0.955])
fig.savefig("figure1_substrates.png", dpi=200)
plt.close(fig)
print("figure1_substrates.png")

# ---------------------------------------------------------------- Figure 2
DAMAGE = {8:  [0.0000, 0.0625, 0.1217, 0.2319, 0.3217],
          10: [0.0000, 0.0669, 0.1286, 0.2410, 0.3342],
          12: [0.0000, 0.0684, 0.1344, 0.2516, 0.3551]}
AUC    = {8:  [0.9763, 0.9720, 0.9782, 0.9424, 0.8555],
          10: [0.9241, 0.8568, 0.8294, 0.7922, 0.6946],
          12: [0.9726, 0.9320, 0.9076, 0.8511, 0.8015]}
ERR    = {8:  [0.0046, 0.0068, 0.0040, 0.0041, 0.0247],
          10: [0.0131, 0.0230, 0.0094, 0.0061, 0.0054],
          12: [0.0028, 0.0061, 0.0122, 0.0179, 0.0112]}

fig, ax = plt.subplots(figsize=(7.2, 4.8))
ax.axhspan(0.46, 0.52, color=INK_2, alpha=0.10, lw=0)
ax.text(0.365, 0.492, "shuffle null", color=INK_2, fontsize=8.5, style="italic")
for N, name, ratio, colour in FIELDS:
    ax.errorbar(DAMAGE[N], AUC[N], yerr=ERR[N], color=colour, lw=2.0,
                marker="o", ms=6, mew=1.6, mec=SURFACE, capsize=3,
                elinewidth=1.2, zorder=3, label=f"{name} — {ratio.split()[0]}")
    ax.annotate(f"{name}\n{ratio.split()[0]}", (DAMAGE[N][-1], AUC[N][-1]),
                xytext=(9, 0), textcoords="offset points", color=INK,
                fontsize=9, va="center", linespacing=1.4)
ax.set_xlim(-0.015, 0.46); ax.set_ylim(0.44, 1.02)
ax.set_xlabel("fraction of vertices displaced by phason disorder")
ax.set_ylabel("address readability (AUC)")
ax.set_title("Address fragility follows the cyclotomic field", color=INK,
             fontsize=12, loc="left", pad=12)
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.0, 0.13),
          labelcolor=INK_2, fontsize=8.5)
tidy(ax)
fig.tight_layout()
fig.savefig("figure2_cyclotomic.png", dpi=200)
plt.close(fig)
print("figure2_cyclotomic.png")

# ---------------------------------------------------------------- Figure 3
crop = [90, 75, 60, 50, 40, 30]
ab   = [0.9424, 0.9980, 0.9995, 0.9996, 0.9995, 0.9997]
pen  = [0.7473, 0.8234, 0.9492, 0.9837, 0.9802, 0.9738]

fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.axhspan(0.46, 0.52, color=INK_2, alpha=0.10, lw=0)
ax.axvline(75, color=INK_2, lw=1.0, ls=(0, (4, 3)), alpha=0.6, zorder=1)
ax.text(73.5, 0.635, "crop used by\nthe earlier analysis", color=INK_2,
        fontsize=8.5, va="center", ha="left", linespacing=1.4)
ax.plot(crop, ab, color=SILVER, lw=2.0, marker="o", ms=6, mew=1.6, mec=SURFACE,
        zorder=3, label="Ammann-Beenker")
ax.plot(crop, pen, color=GOLDEN, lw=2.0, marker="o", ms=6, mew=1.6, mec=SURFACE,
        zorder=3, label="Penrose")
# Label at the left end, where the two curves are furthest apart, so each label
# is unambiguously attached to its own line.
ax.annotate("Ammann-Beenker", (90, ab[0]), xytext=(6, 12), textcoords="offset points",
            color=INK, fontsize=9, ha="left")
ax.annotate("Penrose", (90, pen[0]), xytext=(6, -16), textcoords="offset points",
            color=INK, fontsize=9, ha="left")
ax.invert_xaxis()
ax.set_xlim(93, 27)
ax.set_ylim(0.44, 1.05)
ax.set_xlabel("percent of patch retained (boundary trimmed →)")
ax.set_ylabel("address readability (AUC)")
ax.set_title("The published asymmetry is boundary contamination", color=INK,
             fontsize=12, loc="left", pad=12)
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.0, 0.14),
          labelcolor=INK_2, fontsize=8.5)
tidy(ax)
fig.tight_layout()
fig.savefig("figure3_boundary.png", dpi=200)
plt.close(fig)
print("figure3_boundary.png")
