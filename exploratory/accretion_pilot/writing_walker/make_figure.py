#!/usr/bin/env python3
"""make_figure.py -- the writing walker, drawn: the rewritten road, the defects it leaves, and the numbers."""
import json, math, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import writing_walker as W

D, T0 = 0.2, 10.0
base = W.build(0.0, 0.0); F = W.build(D, T0)
atlas = set(W.star_types(base).values()); ty = W.star_types(F)
ill = [W.par(K) for K, tp in ty.items() if tp not in atlas]
added = {k for k in F if k not in base}
fig = plt.figure(figsize=(15, 8.6))
ax = fig.add_axes([0.04, 0.47, 0.93, 0.47])
for k, (cs, rs, nr, ns) in F.items():
    ps = [W.par(K) for K in cs]
    if not all(-6.5 < p[0] < 7.5 and -42 < p[1] < 42 for p in ps):
        continue
    pts = [(p[1], p[0]) for p in ps]                       # rotate: along the road -> horizontal
    rib = rs[0] == W.J and nr == W.C
    col = "#c0392b" if k in added else ("#9ecae1" if rib else ("#f2f2f2" if abs(ps[1][0]-ps[0][0])*0 == 0 else "w"))
    ax.add_patch(Polygon(pts, closed=True, fc=col, ec="#555", lw=0.35))
for p in ill:
    if -6.5 < p[0] < 7.5:
        ax.plot(p[1], p[0], "o", ms=5, mfc="#ffd400", mec="k", mew=0.6, zorder=5)
ax.axvspan(T0 - 0.3, T0 + 0.3, color="#1a5fb4", alpha=0.5)
ax.annotate("walker", (T0, 7.2), ha="center", fontsize=9, color="#1a5fb4")
ax.axvspan(W.T_START - 0.3, W.T_START + 0.3, color="#2e8b57", alpha=0.5)
ax.annotate("birthplace", (W.T_START, 7.2), ha="center", fontsize=9, color="#2e8b57")
ax.set_xlim(-40, 40); ax.set_ylim(-6.5, 7.8); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"The walker's road (blue) and what it rewrote in its wake (red), push = {D}. "
             "Yellow dots: vertex shapes that never occur in a Penrose tiling (defects).", fontsize=10)
rows = json.load(open("results/push_scan.json"))
res = json.load(open("results/writing_walker.json"))
a1 = fig.add_axes([0.06, 0.07, 0.4, 0.3]); a2 = fig.add_axes([0.56, 0.07, 0.4, 0.3])
for d, c in zip(W.DELTAS, ["#9ecae1", "#6baed6", "#3182bd", "#08519c"]):
    a1.plot([t - W.T_START for t in W.T0S], [res[f"{d}_{t}"]["flips"] for t in W.T0S], "-o", color=c, ms=4, label=f"push {d}")
a1.set_xlabel("distance travelled (tile edges)"); a1.set_ylabel("tiles rewritten (flips)")
a1.set_title("The record grows steadily with the journey", fontsize=10); a1.legend(fontsize=8, frameon=False)
a2.plot([r[0] for r in rows], [r[1] for r in rows], color="#c0392b", label="flips (rewrites)")
a2.plot([r[0] for r in rows], [r[3] for r in rows], color="#b8860b", label="defects in the middle of the wake")
a2.set_xlabel("push size (fraction of the line spacing)"); a2.set_ylabel("count, whole journey")
a2.set_title("No push size leaves a clean wake", fontsize=10); a2.legend(fontsize=8, frameon=False)
for a in (a1, a2):
    a.grid(alpha=0.2); [a.spines[k].set_visible(False) for k in ("top", "right")]
fig.savefig("figures/writing_walker.png", dpi=150)
print("wrote figures/writing_walker.png")
