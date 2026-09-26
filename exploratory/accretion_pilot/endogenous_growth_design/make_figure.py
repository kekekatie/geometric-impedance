#!/usr/bin/env python3
"""Small schematic: (A) one BUD event; (B) the non-joinable critical pair.
Events change structure; there is no traveller."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
A_FACE = "#d62728"   # active
Q_FACE = "#bdbdbd"   # quiet


def node(ax, xy, label, state, name=""):
    fc = A_FACE if state == "A" else Q_FACE
    ax.scatter([xy[0]], [xy[1]], s=620, c=fc, edgecolors="k", zorder=3, linewidths=1.3)
    ax.text(xy[0], xy[1], label, ha="center", va="center", color="white",
            fontsize=11, fontweight="bold", zorder=4)
    if name:
        ax.text(xy[0], xy[1] - 0.30, name, ha="center", va="top", fontsize=8, color="#333")


def edge(ax, p, q, active=True):
    ax.plot([p[0], q[0]], [p[1], q[1]], "-", lw=2.4 if active else 1.6,
            color=("#111" if active else "#999"), zorder=2)


def arrow(ax, x0, x1, y, txt=""):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", lw=2, color="#444"))
    if txt:
        ax.text((x0 + x1) / 2, y + 0.14, txt, ha="center", fontsize=8.5, color="#444")


fig, axes = plt.subplots(2, 1, figsize=(11.5, 8.2))

# ---- Panel A: one BUD (k=1) ------------------------------------------------
ax = axes[0]
x = {"A_": (-0.7, 0), "B_": (0.4, 0)}
node(ax, x["A_"], "A", "A", "x (keeper)")
node(ax, x["B_"], "A", "A", "y (depositor)")
edge(ax, x["A_"], x["B_"], active=True)
ax.text(-0.15, 0.55, "active bond", fontsize=8.5, color="#111", ha="center")
arrow(ax, 1.1, 2.1, 0.0, "BUD(x,y)")
# after
xa = {"x": (2.7, 0.0), "y": (3.8, -0.5), "z": (3.8, 0.6)}
node(ax, xa["x"], "A", "A", "x (still active)")
node(ax, xa["y"], "Q", "Q", "y (quiet, persistent)")
node(ax, xa["z"], "A", "A", "z (new active tip)")
edge(ax, xa["x"], xa["z"], active=True)      # new active bond
edge(ax, xa["x"], xa["y"], active=False)     # interior bond
edge(ax, xa["y"], xa["z"], active=False)     # interior bond -> triangle
ax.text(3.42, 0.05, "triangle x-y-z\n(interior motif)", fontsize=7.5, color="#333", ha="left")
ax.set_title("(A) One event = one BUD.  Active bond  ->  persistent quiet apex inside a "
             "new triangle  +  a new active tip.\nNo walker: the rule reads one edge and "
             "its two endpoint labels, nothing else.", fontsize=10, loc="left")
ax.set_xlim(-1.4, 5.1); ax.set_ylim(-1.2, 1.2); ax.axis("off")

# ---- Panel B: non-joinable critical pair -----------------------------------
ax = axes[1]
# seed path a-b-c
s = {"a": (-0.9, 0), "b": (0.0, 0), "c": (0.9, 0)}
for nm, xy in s.items():
    node(ax, xy, "A", "A", nm)
edge(ax, s["a"], s["b"], True); edge(ax, s["b"], s["c"], True)
ax.text(0.0, 0.5, "two events compete for shared vertex b", fontsize=8.5, ha="center")

arrow(ax, 1.35, 2.05, 0.55, "BUD(a,b)")
arrow(ax, 1.35, 2.05, -0.55, "BUD(b,a)")

# upper outcome: quiet b -> c stranded
u = {"a": (2.5, 0.95), "b": (3.4, 0.75), "z": (2.5, 1.5), "c": (4.3, 0.75)}
node(ax, u["a"], "A", "A"); node(ax, u["b"], "Q", "Q"); node(ax, u["z"], "A", "A")
node(ax, u["c"], "A", "A", "c: STRANDED")
edge(ax, u["a"], u["z"], True); edge(ax, u["a"], u["b"], False); edge(ax, u["b"], u["z"], False)
edge(ax, u["b"], u["c"], False)
ax.text(4.55, 0.75, "no active\nneighbour", fontsize=7, color="#b00", ha="left", va="center")

# lower outcome: quiet a -> b,c still active
lo = {"a": (2.5, -1.15), "b": (3.5, -0.95), "z": (2.5, -0.55), "c": (4.4, -0.95)}
node(ax, lo["a"], "Q", "Q"); node(ax, lo["b"], "A", "A"); node(ax, lo["z"], "A", "A")
node(ax, lo["c"], "A", "A", "c: active")
edge(ax, lo["b"], lo["z"], True); edge(ax, lo["b"], lo["a"], False); edge(ax, lo["a"], lo["z"], False)
edge(ax, lo["b"], lo["c"], True)
ax.text(4.6, -0.95, "bond b-c\nsurvives", fontsize=7, color="#060", ha="left", va="center")

ax.text(5.5, -0.1, "NOT isomorphic\nand not re-joinable\n=> order is remembered",
        fontsize=9, color="#111", ha="left", va="center",
        bbox=dict(boxstyle="round", fc="#fff3cd", ec="#e0a800"))
ax.set_title("(B) Non-confluence = memory.  Same seed, two local orders, permanently "
             "different structures (one strands c, one does not).\nGenuinely disjoint "
             "events would instead commute (parallel independence) and leave no trace.",
             fontsize=10, loc="left")
ax.set_xlim(-1.5, 7.6); ax.set_ylim(-1.8, 1.9); ax.axis("off")

fig.suptitle("Endogenous-growth model M1 (Competitive Accretion Grammar): events change "
             "structure; competition records their order", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(HERE, "figures", "rule_before_after.png"), dpi=140)
print("wrote figures/rule_before_after.png")
