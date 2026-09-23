#!/usr/bin/env python3
"""Two-panel figure for the bounded GRAFT experiment.
 Left: the frozen seed and the before/after of one GRAFT on the designated trace q.
 Right: exact cumulative outcome probabilities by horizon (extended vs control)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import graft_experiment as E

HERE = os.path.dirname(os.path.abspath(__file__))
COL = {"A": "#1a7f37", "Q": "#c0392b"}


def draw(ax, G, title, hi_edge=None):
    pos = nx.spring_layout(G, seed=7)
    nx.draw_networkx_edges(ax=ax, G=G, pos=pos, width=1.6, edge_color="#888")
    if hi_edge:
        nx.draw_networkx_edges(ax=ax, G=G, pos=pos, edgelist=[hi_edge], width=3.2,
                               edge_color="#8e44ad")
    nx.draw_networkx_nodes(ax=ax, G=G, pos=pos, node_size=520,
                           node_color=[COL[G.nodes[n]["label"]] for n in G])
    nx.draw_networkx_labels(ax=ax, G=G, pos=pos,
                            labels={n: f"{n}\n{G.nodes[n]['label']}" for n in G},
                            font_size=8, font_color="white")
    ax.set_title(title, fontsize=9); ax.axis("off")


def main():
    S = E.frozen_seed()
    # one GRAFT on q at the seed: GRAFT(1,0,2) adds q-w = 1-2, creating new pair {2,3}
    H = E.apply_ev(S, ("G", 1, 0, 2))
    ext, done, *_ = E.enumerate_process(S, E.events_extended, E.QID)

    fig = plt.figure(figsize=(13.5, 5.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.25])
    a0 = fig.add_subplot(gs[0, 0]); a1 = fig.add_subplot(gs[1, 0])
    draw(a0, S, "frozen seed S   (q=1 quiet, menu C_q = empty)")
    draw(a1, H, "after GRAFT(1,0,2): edge 1-2 added -> new pair {2,3} in C_q", hi_edge=(1, 2))

    axr = fig.add_subplot(gs[:, 1])
    steps = list(range(done + 1))
    o0 = [float(ext[d]["o0"]) for d in steps]
    o1 = [float(ext[d]["o1"]) for d in steps]
    o2 = [float(ext[d]["o2"]) for d in steps]
    axr.plot(steps, o0, "-o", color="#8a8a8a", lw=2,
             label="O0  q gains a new neighbour (extended)")
    axr.plot(steps, o1, "-o", color="#1a7f37", lw=2.2,
             label="O1  q gains a never-before pair (extended)")
    axr.plot(steps, o2, "-s", color="#8e44ad", lw=2.2,
             label="O2  renew-then-consult through q (extended)")
    axr.plot(steps, [0] * len(steps), "--", color="#c0392b", lw=2,
             label="control (BUD+CONTACT): O0=O1=O2=0")
    for d in steps:
        if o1[d] > 0:
            axr.annotate(f"{o1[d]*100:.1f}%", (d, o1[d]), textcoords="offset points",
                         xytext=(4, 6), fontsize=7.5, color="#1a7f37")
        if o2[d] > 0:
            axr.annotate(f"{o2[d]*100:.1f}%", (d, o2[d]), textcoords="offset points",
                         xytext=(4, -12), fontsize=7.5, color="#8e44ad")
    axr.set_xlabel("events elapsed (horizon)"); axr.set_ylabel("cumulative probability")
    axr.set_xticks(steps); axr.set_ylim(-0.03, 0.55); axr.grid(alpha=0.25)
    axr.set_title("Exact cumulative outcome probabilities for the designated trace q",
                  fontsize=9.5)
    axr.legend(fontsize=8, loc="upper left")

    fig.suptitle("Bounded GRAFT experiment: renewal of a quiet trace occurs and is consulted "
                 "(extended) — impossible without GRAFT (control).\nMechanism test on one "
                 "deliberately chosen seed; equal event counts are not matched time.",
                 fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    out = os.path.join(HERE, "figures", "graft_experiment.png")
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
