#!/usr/bin/env python3
"""Before/after diagram: a later read-only local change (CONTACT: promote a-0-b to a-b)
makes a dormant 0-trace matter. Same intervention, different archives -> divergent 1-fronts."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import active_latent_checks as C

HERE = os.path.dirname(os.path.abspath(__file__))
A_FACE, Q_FACE, BOND, NEW = "#d62728", "#c9c9c9", "#d62728", "#1a7f37"

fulls = C.depth2_classes()
i, j = C.find_pair(fulls)
G0, G1 = fulls[i], fulls[j]
C0, add0 = C.contact_sweep(G0)
C1, add1 = C.contact_sweep(G1)


def draw_active(ax, G, added, title):
    P = C.proj(G)
    pos = nx.spring_layout(P, seed=5, k=1.3)
    old = [(u, v) for u, v in P.edges()
           if (u, v) not in added and (v, u) not in added]
    new = [(u, v) for u, v in P.edges()
           if (u, v) in added or (v, u) in added]
    nx.draw_networkx_edges(ax=ax, G=P, pos=pos, edgelist=old, edge_color=BOND, width=3.0)
    nx.draw_networkx_edges(ax=ax, G=P, pos=pos, edgelist=new, edge_color=NEW, width=3.4)
    for n in P:
        ax.scatter([pos[n][0]], [pos[n][1]], s=560, c=A_FACE, edgecolors="k",
                   zorder=3, linewidths=1.2)
        ax.text(pos[n][0], pos[n][1], "1", ha="center", va="center", color="white",
                fontsize=12, fontweight="bold", zorder=4)
    ax.set_title(title, fontsize=9.5); ax.axis("off")


def draw_rule(ax):
    pos = {"a": (0, 0), "q": (1, 0), "b": (2, 0), "a2": (4, 0), "b2": (6, 0)}
    ax.plot([0, 1], [0, 0], "--", color="#999", lw=1.6)
    ax.plot([1, 2], [0, 0], "--", color="#999", lw=1.6)
    for nm, xy, lab, act in [("a", (0, 0), "1", True), ("q", (1, 0), "0", False),
                             ("b", (2, 0), "1", True)]:
        ax.scatter([xy[0]], [xy[1]], s=520, c=(A_FACE if act else Q_FACE),
                   edgecolors="k", zorder=3, linewidths=1.2)
        ax.text(xy[0], xy[1], lab, ha="center", va="center",
                color=("white" if act else "#333"), fontsize=12, fontweight="bold", zorder=4)
    ax.annotate("", xy=(3.6, 0), xytext=(2.5, 0),
                arrowprops=dict(arrowstyle="-|>", lw=2, color="#444"))
    ax.text(3.05, 0.28, "CONTACT", ha="center", fontsize=8.5, color="#444")
    ax.plot([4, 6], [0, 0], "-", color=NEW, lw=3.4)
    for xy in [(4, 0), (6, 0)]:
        ax.scatter([xy[0]], [xy[1]], s=520, c=A_FACE, edgecolors="k", zorder=3, linewidths=1.2)
        ax.text(xy[0], xy[1], "1", ha="center", va="center", color="white",
                fontsize=12, fontweight="bold", zorder=4)
    ax.text(1, -0.55, "latent link through a 0", ha="center", fontsize=8, color="#555")
    ax.text(5, -0.55, "live 1–1 bond", ha="center", fontsize=8, color=NEW)
    ax.set_title("the extension rule (a modelling assumption):\n"
                 "promote a–0–b to a–b, read-only on the 0s", fontsize=9.5)
    ax.set_xlim(-0.7, 6.7); ax.set_ylim(-0.9, 0.7); ax.axis("off")


fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
draw_rule(axes[0])
draw_active(axes[1], C0, add0,
            f"state {i} after CONTACT  (archive 0-degrees {{3,3}})\n"
            "front = path;  successors  1/3, 1/3, 1/3")
draw_active(axes[2], C1, add1,
            f"state {j} after CONTACT  (archive 0-degrees {{2,3}})\n"
            "front = triangle+pendant;  successors  1/4,1/8,1/4,1/8,1/4")
fig.suptitle("A later local change makes a dormant trace matter again.  Before: identical "
             "1-fronts, identical futures.  The SAME read-only CONTACT promotes DIFFERENT "
             "latent links (archives differ) → divergent futures.", fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.9])
fig.savefig(os.path.join(HERE, "figures", "latent_relevance.png"), dpi=140)
print("wrote figures/latent_relevance.png")
