#!/usr/bin/env python3
"""Before/after of the recommended GRAFT rule: new active structure (w) grafts onto an
existing quiet trace (q) via a bounded wedge, turning an empty CONTACT menu nonempty."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
A, Q, NEW, OPP = "#d62728", "#c9c9c9", "#1a7f37", "#d6a400"
pos = {"q": (0.0, 0.0), "x": (1.1, 0.7), "z": (1.1, -0.7), "w": (2.3, 1.2)}


def node(ax, n, active):
    ax.scatter(*pos[n], s=620, c=(A if active else Q), edgecolors="k", zorder=3, linewidths=1.2)
    ax.text(pos[n][0], pos[n][1], "1" if active else "0", ha="center", va="center",
            color="white" if active else "#333", fontsize=12, fontweight="bold", zorder=4)
    ax.text(pos[n][0], pos[n][1] - 0.28, n, ha="center", va="top", fontsize=8, color="#444")


def edge(ax, u, v, color="#111", lw=2.6, style="-"):
    ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], style, color=color, lw=lw, zorder=2)


fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0))

# BEFORE
ax = axes[0]
for n, act in [("q", False), ("x", True), ("z", True), ("w", True)]:
    node(ax, n, act)
edge(ax, "q", "x"); edge(ax, "q", "z"); edge(ax, "x", "z"); edge(ax, "x", "w")
ax.annotate("wedge  w–x–q\n(q–w absent)", xy=(1.15, 0.95), xytext=(1.5, 0.1),
            fontsize=8, color="#444")
ax.set_title("before: q is a quiet trace (0) with an EMPTY CONTACT menu\n"
             "(its active neighbours x,z are already joined; nothing to mediate)", fontsize=9.5)
ax.set_xlim(-0.6, 3.0); ax.set_ylim(-1.3, 1.7); ax.axis("off")

# AFTER
ax = axes[1]
for n, act in [("q", False), ("x", True), ("z", True), ("w", True)]:
    node(ax, n, act)
edge(ax, "q", "x"); edge(ax, "q", "z"); edge(ax, "x", "z"); edge(ax, "x", "w")
edge(ax, "q", "w", color=NEW, lw=3.4)                          # grafted edge
edge(ax, "z", "w", color=OPP, lw=2.2, style="--")             # new opportunity
ax.text(1.9, 0.05, "grafted\nq–w", color=NEW, fontsize=8, ha="center")
ax.text(1.9, 0.55, "new CONTACT\nopportunity {z,w}\n(via q)", color="#9a7500", fontsize=7.5,
        ha="center")
ax.set_title("after GRAFT(q,x,w): q gains active neighbour w (green, append-only)\n"
             "→ menu becomes NONEMPTY: {z,w} is newly enabled (amber, dashed)", fontsize=9.5)
ax.set_xlim(-0.6, 3.0); ax.set_ylim(-1.3, 1.7); ax.axis("off")

fig.suptitle("Renewed contact (option 1 = add an active neighbour to an old quiet trace): "
             "new structure grafts onto the archive, manufacturing a NEW opportunity —\n"
             "not reading an already-eligible one. Record preserved in the append-only "
             "sense (no label or edge deleted; one edge added at q).", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.9])
fig.savefig(os.path.join(HERE, "figures", "graft_before_after.png"), dpi=140)
print("wrote figures/graft_before_after.png")
