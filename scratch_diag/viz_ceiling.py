#!/usr/bin/env python3
"""How much can the 'cleanest smallest change' (exact pentagon windows) buy us?
Split the periodicity failures into:
  - SHAPE (target class exists, but the rough window rejects it) -> a window fix CAN help
  - CLASS-0 HOLE (the slide sends the point to class 0, which doesn't exist) -> NO window can help
Numbers measured in diag_periodicity.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PASS, SHAPE, HOLE = "#0072B2", "#E69F00", "#D55E00"
# measured (order, total, pass, shape_fail, hole_fail)
data = [("order 1 (1/1)", 434, 184, 92, 158),
        ("order 2 (2/1)", 405, 247, 105, 53)]

fig, ax = plt.subplots(figsize=(11, 3.6))
ypos = [1, 0]
for (lbl, tot, p, s, h), y in zip(data, ypos):
    pp, sp, hp = 100*p/tot, 100*s/tot, 100*h/tot
    ax.barh(y, pp, color=PASS, edgecolor="white")
    ax.barh(y, sp, left=pp, color=SHAPE, edgecolor="white")
    ax.barh(y, hp, left=pp+sp, color=HOLE, edgecolor="white")
    ax.text(pp/2, y, f"{pp:.0f}%", ha="center", va="center", color="white", fontsize=11, fontweight="bold")
    ax.text(pp+sp/2, y, f"{sp:.0f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    ax.text(pp+sp+hp/2, y, f"{hp:.0f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    # ceiling marker: pass + shape (what exact pentagons could reach at best)
    ax.plot([pp+sp, pp+sp], [y-0.42, y+0.42], color="black", lw=2.5, ls=(0,(2,1)))
    ax.text(pp+sp, y+0.5, f"exact-pentagons ceiling  {pp+sp:.0f}%",
            ha="center", va="bottom", fontsize=9)

ax.set_yticks(ypos); ax.set_yticklabels([d[0] for d in data], fontsize=11)
ax.set_xlim(0, 100); ax.set_xlabel("share of interior points  (a true period = 100% blue)")
ax.set_title("The cleanest small change (exact pentagons) can only reach the dashed line\n"
             "the RED 'class-0 hole' is a different kind of problem — no window shape can fill it",
             fontsize=12)
# legend
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=PASS, label="has a partner (periodic)"),
                   Patch(color=SHAPE, label="wrong-shape reject  (a window fix CAN help)"),
                   Patch(color=HOLE, label="class-0 hole  (no window can help)")],
          loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=3, fontsize=9, framealpha=0.95)
ax.spines[["top","right","left"]].set_visible(False)
fig.tight_layout()
out = __file__.replace("viz_ceiling.py", "penrose_ceiling.png")
fig.savefig(out, dpi=135, bbox_inches="tight")
print("saved", out)
