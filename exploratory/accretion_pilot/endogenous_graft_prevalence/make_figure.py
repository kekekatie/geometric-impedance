#!/usr/bin/env python3
"""Figure for the GRAFT-prevalence sweep: renewal (O1) and consultation (O2) probabilities by
step 4 for every (seed, quiet-trace) case, coloured by whether the trace starts with an empty
CONTACT menu; the control (no GRAFT) is exactly 0 for all cases."""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "endogenous_graft_experiment"))
sys.path.insert(0, os.path.join(HERE, "..", "endogenous_present_width"))
import graft_experiment as GE
import present_width as PW


def main():
    fulls = PW.depth2_classes()
    cases = []
    for c, G in enumerate(fulls):
        for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
            m0 = len(GE.C_q(G, q))
            ea, *_ = GE.enumerate_process(G, GE.events_extended, q, horizon=4)
            cases.append((f"{c}.{q}", m0, float(ea[4]["o1"]), float(ea[4]["o2"])))
    labels = [x[0] for x in cases]
    o1 = [x[2] for x in cases]; o2 = [x[3] for x in cases]
    empty = [x[1] == 0 for x in cases]

    fig, ax = plt.subplots(figsize=(13.5, 5.2))
    xs = range(len(cases))
    w = 0.42
    c1 = ["#1a7f37" if e else "#1f77b4" for e in empty]      # O1 colour by empty/nonempty menu
    ax.bar([x - w/2 for x in xs], o1, width=w, color=c1, edgecolor="#333", label="O1 renewal")
    ax.bar([x + w/2 for x in xs], o2, width=w, color="#8e44ad", edgecolor="#333",
           alpha=0.9, label="O2 renew-then-consult")
    ax.axhline(0, color="#c0392b", lw=2)
    ax.annotate("control (BUD+CONTACT): O0 = O1 = O2 = 0 for ALL cases",
                (0.2, 0.005), color="#c0392b", fontsize=8, va="bottom")
    # mark the zero-renewal cases
    for i, v in enumerate(o1):
        if v == 0:
            ax.annotate("no wedge", (i, 0.01), rotation=90, fontsize=6.5, color="#888",
                        ha="center", va="bottom")
    ax.set_xticks(list(xs)); ax.set_xticklabels(labels, fontsize=7.5, rotation=90)
    ax.set_xlabel("(seed class . quiet-trace vertex)")
    ax.set_ylabel("cumulative probability by step 4")
    ax.grid(alpha=0.2, axis="y")
    # legend with menu-colour explanation
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#1a7f37", label="O1 renewal (empty-menu trace)"),
                       Patch(color="#1f77b4", label="O1 renewal (non-empty menu)"),
                       Patch(color="#8e44ad", label="O2 renew-then-consult")],
              fontsize=8, loc="upper right")
    ax.set_title("GRAFT-enabled renewal across every depth-2 seed and quiet trace "
                 "(20/22 renew; control ≡ 0)", fontsize=10)
    fig.tight_layout()
    out = os.path.join(HERE, "figures", "graft_prevalence.png")
    fig.savefig(out, dpi=140); print("wrote", out)


if __name__ == "__main__":
    main()
