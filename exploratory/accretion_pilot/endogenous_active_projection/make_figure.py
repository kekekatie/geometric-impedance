#!/usr/bin/env python3
"""Explanatory diagram: two full states with DIFFERENT quiet archives (0s) but the SAME
active projection (1s + 1-1 bonds) evolve their active front identically. The archive is
write-only: the active dynamics never reads it."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import active_projection_checks as C

HERE = os.path.dirname(os.path.abspath(__file__))
A_FACE, Q_FACE, BOND = "#d62728", "#c9c9c9", "#d62728"

fulls, _ = C.depth2_full_classes()
G0, G1 = fulls[0], fulls[1]


def draw(ax, G, title):
    pos = nx.spring_layout(G, seed=3, k=1.1)
    AA = [(u, v) for u, v in G.edges()
          if G.nodes[u]["label"] == "A" and G.nodes[v]["label"] == "A"]
    other = [e for e in G.edges() if e not in AA and (e[1], e[0]) not in AA]
    nx.draw_networkx_edges(ax=ax, G=G, pos=pos, edgelist=other, edge_color="#bbb",
                           width=1.3, style="dashed")
    nx.draw_networkx_edges(ax=ax, G=G, pos=pos, edgelist=AA, edge_color=BOND, width=3.2)
    for n in G:
        act = G.nodes[n]["label"] == "A"
        ax.scatter([pos[n][0]], [pos[n][1]], s=560,
                   c=(A_FACE if act else Q_FACE), edgecolors="k", zorder=3, linewidths=1.2)
        ax.text(pos[n][0], pos[n][1], "1" if act else "0", ha="center", va="center",
                color=("white" if act else "#333"), fontsize=12, fontweight="bold", zorder=4)
    ax.set_title(title, fontsize=10); ax.axis("off")


def draw_proj(ax):
    P = nx.Graph()
    P.add_nodes_from([0, 1, 2, 3])
    P.add_edge(0, 1); P.add_edge(2, 3)          # two disjoint active bonds
    pos = {0: (0, 1), 1: (0, 0), 2: (1, 1), 3: (1, 0)}
    nx.draw_networkx_edges(ax=ax, G=P, pos=pos, width=3.2, edge_color=BOND)
    for n in P:
        ax.scatter([pos[n][0]], [pos[n][1]], s=560, c=A_FACE, edgecolors="k",
                   zorder=3, linewidths=1.2)
        ax.text(pos[n][0], pos[n][1], "1", ha="center", va="center", color="white",
                fontsize=12, fontweight="bold", zorder=4)
    ax.set_title("shared active projection  π\n(two 1-1 bonds; every 0 dropped)",
                 fontsize=10)
    ax.set_xlim(-0.5, 1.5); ax.set_ylim(-0.6, 1.6); ax.axis("off")
    ax.text(0.5, -0.5, "next-active distribution (uniform over the 4 directed bonds):\n"
                       "one class, probability 1  —  identical for BOTH states above",
            ha="center", fontsize=8.5, color="#111",
            bbox=dict(boxstyle="round", fc="#fff3cd", ec="#e0a800"))


fig, axes = plt.subplots(1, 3, figsize=(14.5, 5.0))
draw(axes[0], G0, "full state A  (archive 0-degrees {3,3})\n1s = active front, 0s = quiet archive")
draw(axes[1], G1, "full state B  (archive 0-degrees {2,3})\ndifferent archive, NON-isomorphic full graph")
draw_proj(axes[2])
# both full states A and B project (π) onto the shared active graph in panel 3
for xf in (0.34, 0.66):
    fig.text(xf, 0.09, "──  π  ⟶", fontsize=12, color="#444", ha="center")
fig.suptitle("The active front is a closed system; the quiet archive is write-only.  "
             "Different 0-archives, same 1-front  →  same next-active dynamics.",
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(HERE, "figures", "active_projection.png"), dpi=140)
print("wrote figures/active_projection.png")
