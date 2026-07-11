#!/usr/bin/env python3
"""The resolution, side by side: the SAME Penrose approximant, slid by
(left) the class-SHIFTING arrow the validator used  -> ~40% land (looks broken)
(right) a class-PRESERVING arrow                     -> 100% land (it was periodic)
The tiling was periodic all along; the validator used the wrong-shaped cell.
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approximant"))
from phason_shear import PhasonShearApproximant

PASS, FAIL = "#0072B2", "#D55E00"
ap = PhasonShearApproximant("penrose", 0, radius=13.0)
tree = cKDTree(ap.par)
r = np.linalg.norm(ap.par, axis=1)
Rp = 0.5 * ap.radius
interior = np.where(r < Rp)[0]

def split(gvec):
    P = gvec @ ap.par_star
    p, f = [], []
    for i in interior:
        tgt = ap.par[i] + P
        if np.linalg.norm(tgt) < ap.radius - 1.0:
            d, _ = tree.query(tgt)
            (p if d < 1e-6 else f).append(ap.par[i])
    return np.array(p), np.array(f), P

arrows = [("class-SHIFTING arrow $P_a$  (what the validator used)", ap.M_a),
          ("class-PRESERVING arrow $M_b-M_a$", -ap.M_a + ap.M_b)]
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
for ax, (title, g) in zip(axes, arrows):
    p, f, P = split(g)
    tot = len(p) + len(f)
    ax.scatter(ap.par[:, 0], ap.par[:, 1], s=6, color="#dddddd", zorder=1)
    if len(p):
        ax.scatter(p[:, 0], p[:, 1], s=26, color=PASS, zorder=3,
                   label=f"lands on a partner ({len(p)})")
    if len(f):
        ax.scatter(f[:, 0], f[:, 1], s=42, marker="x", color=FAIL, linewidths=2,
                   zorder=4, label=f"no partner ({len(f)})")
    ax.add_patch(FancyArrow(0, 0, P[0], P[1], width=0.05, head_width=0.5,
                 length_includes_head=True, color="black", zorder=5))
    ax.set_title(f"{title}\n{100*len(p)/tot:.0f}% land", fontsize=12)
    ax.set_aspect("equal"); ax.legend(loc="upper left", fontsize=10)
    ax.set_xlim(-Rp-1, Rp+1); ax.set_ylim(-Rp-1, Rp+1)
    ax.set_xticks([]); ax.set_yticks([])

fig.suptitle("Penrose WAS periodic all along — you just have to slide it by the right cell\n"
             "(the right cell is 5x bigger: that 5x IS the four-class 'this/that' structure)",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.94])
out = os.path.join(os.path.dirname(__file__), "penrose_resolved.png")
fig.savefig(out, dpi=130, bbox_inches="tight")
print("saved", out)
