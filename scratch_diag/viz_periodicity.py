#!/usr/bin/env python3
"""Visualize WHY the Penrose phason-shear approximant is only ~42% periodic.
Panel A (physical space): slide every interior vertex by the period arrow P_a;
  green = lands on a real partner vertex, red = misses (no partner).
Panel B (internal/perp space): the four per-class acceptance windows are
  different shapes; the period arrow shifts a point's class by +2, so it gets
  judged by a *different* window -- and class 3 -> class 5 == 0, which has no
  window at all.
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, FancyArrow
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approximant"))
from geometry import Patch, _convex_polygon
from phason_shear import PhasonShearApproximant

# colourblind-safe (Okabe-Ito) per class
CLS_COL = {1: "#E69F00", 2: "#56B4E9", 3: "#009E73", 4: "#CC79A7", 0: "#999999"}
PASS_COL, FAIL_COL = "#0072B2", "#D55E00"

ap = PhasonShearApproximant("penrose", 0, radius=14.0)
N = ap.N
rc = ap.K.sum(1) % N
tree = cKDTree(ap.par)
r = np.linalg.norm(ap.par, axis=1)
Rp = 0.55 * ap.radius
sM_a = int(ap.M_a.sum() % N)

pass_pts, fail_pts = [], []
for i in np.where(r < Rp)[0]:
    tgt = ap.par[i] + ap.P_a
    if np.linalg.norm(tgt) < ap.radius - 1.0:
        d, _ = tree.query(tgt)
        (pass_pts if d < 1e-6 else fail_pts).append(ap.par[i])
pass_pts = np.array(pass_pts); fail_pts = np.array(fail_pts)
pct = 100 * len(pass_pts) / (len(pass_pts) + len(fail_pts))

fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 7))

# ---- Panel A: physical space, pass/fail under P_a ----
axA.scatter(ap.par[:, 0], ap.par[:, 1], s=6, color="#dddddd", zorder=1)
if len(pass_pts):
    axA.scatter(pass_pts[:, 0], pass_pts[:, 1], s=26, color=PASS_COL,
                label=f"has a partner ({len(pass_pts)})", zorder=3)
if len(fail_pts):
    axA.scatter(fail_pts[:, 0], fail_pts[:, 1], s=42, marker="x", color=FAIL_COL,
                linewidths=2, label=f"no partner ({len(fail_pts)})", zorder=4)
# period arrow, drawn from patch centre
c0 = np.array([0, 0.0])
axA.add_patch(FancyArrow(c0[0], c0[1], ap.P_a[0], ap.P_a[1], width=0.05,
              head_width=0.6, length_includes_head=True, color="black", zorder=5))
axA.text(ap.P_a[0]*0.5, ap.P_a[1]*0.5 - 0.9, "period arrow $P_a$",
         fontsize=11, ha="center")
axA.set_title(f"Physical space: slide every point by the period arrow\n"
              f"only {pct:.0f}% find a partner  (a real period would be 100%)",
              fontsize=12)
axA.set_aspect("equal"); axA.legend(loc="upper left", fontsize=10)
axA.set_xlim(-Rp-1, Rp+1); axA.set_ylim(-Rp-1, Rp+1)
axA.set_xticks([]); axA.set_yticks([])

# ---- Panel B: perp space, the four windows drawn SEPARATELY (true rel. size) ----
base = Patch("penrose", radius=24.0)   # faithful
slots = {1: -4.5, 2: -1.5, 3: 1.5, 4: 4.5}
size_lbl = {1: "small", 2: "large", 3: "large", 4: "small"}
for cls in [1, 2, 3, 4]:
    m = base.residue_class == cls
    hull = _convex_polygon(base.perp[m])
    hull = hull - hull.mean(0) + np.array([slots[cls], 0.6])  # centre in slot
    axB.add_patch(MPoly(hull, closed=True, facecolor=CLS_COL[cls], alpha=0.45,
                        edgecolor=CLS_COL[cls], lw=2))
    axB.text(slots[cls], 2.55, f"class {cls}\n({size_lbl[cls]})", ha="center",
             va="bottom", fontsize=10, fontweight="bold")
# the slide mapping, shown as text with the broken one in red
axB.text(0, -1.7, f"slide by the period arrow  $\\Rightarrow$  class shifts by +{sM_a}",
         ha="center", fontsize=11)
maps = [("1$\\to$3", "#333"), ("2$\\to$4", "#333"),
        ("3$\\to$5$\\equiv$0  (NO window)", FAIL_COL), ("4$\\to$1", "#333")]
xs = [-4.7, -2.2, 0.9, 4.4]
for (txt, col), x in zip(maps, xs):
    axB.text(x, -2.5, txt, ha="center", fontsize=11, color=col,
             fontweight="bold" if col == FAIL_COL else "normal")
axB.text(0, -3.3, "each point is judged by its class's window; the slide sends it\n"
         "to a different-shaped window (or to class 0, which has none)",
         ha="center", fontsize=10, color="#555")
axB.set_title("Internal space: four *different* windows, one per class\n"
              "(sizes differ by the golden ratio $\\varphi$)", fontsize=12)
axB.set_aspect("equal")
axB.set_xlim(-6.5, 6.5); axB.set_ylim(-3.8, 3.2)
axB.set_xticks([]); axB.set_yticks([])
for s in axB.spines.values():
    s.set_visible(False)

fig.suptitle("Why the Penrose approximant isn't periodic (AB is 100%: it uses ONE window)",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96])
out = os.path.join(os.path.dirname(__file__), "penrose_periodicity.png")
fig.savefig(out, dpi=130, bbox_inches="tight")
print("saved", out, f"  periodicity={pct:.1f}%")
