#!/usr/bin/env python3
"""make_figure.py -- figures/patches.png: three ways of laying the Penrose tiling with no map."""
import os, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import laying_the_tiling as T

HERE = os.path.dirname(os.path.abspath(__file__))
SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
THIN, THICK, WRONG, SEEDC = "#bcd6f5", "#2a78d6", "#eb6834", "#d9d8d3"
seed = T.seed_patch(0j, 3 * T.SCALE_LEN)
refset = {T.canon(t) for t in T.REF}
seedset = {T.canon(t) for t in seed}
runs = [("LOCAL, dice", *T.lay("LOCAL-DICE", seed, random.Random(T.SEED + 3))),
        ("LOCAL, forced first", *T.lay("LOCAL-FORCED", seed, random.Random(T.SEED))),
        ("SCALE: own zoomed-out self", *T.lay("SCALE", seed, None))]
fig, axes = plt.subplots(1, 3, figsize=(13, 5.2), dpi=150)
fig.patch.set_facecolor(SURF)
for ax, (title, n, st, P) in zip(axes, runs):
    ax.set_facecolor(SURF)
    wrong = 0
    for t in P.tris:
        ck = T.canon(t)
        col = SEEDC if ck in seedset else ((THIN if t[0] == 0 else THICK) if ck in refset else WRONG)
        wrong += (ck not in refset)
        ax.add_patch(Polygon([(z.real, z.imag) for z in t[1:]], closed=True, fc=col,
                             ec=SURF, lw=0.4))
    if st == "JAM":
        p, q, r, _ = P.frontier()[0]
        ax.plot([p.real, q.real], [p.imag, q.imag], color=INK, lw=2.5)
    L = 16 * T.SCALE_LEN
    ax.set_xlim(-L, L); ax.set_ylim(-L, L); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    status = {"JAM": f"JAMMED after {n} half-tiles (black edge: nothing fits)",
              "ok": f"{n} half-tiles, no jam"}.get(st, st)
    ax.set_title(title, color=INK, fontsize=11, fontweight="bold", loc="left")
    ax.text(0, -0.04, f"{status}\n{wrong} tiles differ from the self-similar tiling",
            transform=ax.transAxes, color=INK2, fontsize=8.5, va="top")
fig.suptitle("Laying the Penrose tiling with no map", color=INK, fontsize=13, fontweight="bold",
             x=0.01, ha="left", y=0.985)
fig.text(0.01, 0.925, "Grey = the starting patch. Blue = tiles matching the self-similar Penrose "
         "tiling (light = thin, dark = thick). Orange = legal tiles of a DIFFERENT Penrose universe.",
         color=INK2, fontsize=9, ha="left")
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.12, wspace=0.05)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.savefig(os.path.join(HERE, "figures", "patches.png"), facecolor=SURF)
print("wrote figures/patches.png")
