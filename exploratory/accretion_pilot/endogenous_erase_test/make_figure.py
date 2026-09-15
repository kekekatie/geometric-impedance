#!/usr/bin/env python3
"""Two-panel figure for the ERASE test.
 Left  (Q1 durable mark): total-variation distance between lineages i and j at each step,
       for NULL / ERASE / KEEP, with the ERASE moment marked. ERASE stays > 0 after deletion.
 Right (Q2 redundancy): TV distance between ERASE (archive deleted) and KEEP (archive kept)
       within each lineage -- nonzero after H means the archive is not redundant."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fractions import Fraction as Fr
import erase_test as E


def tv(d1, d2):
    keys = set(d1) | set(d2)
    return float(sum(abs(d1.get(k, Fr(0)) - d2.get(k, Fr(0))) for k in keys)) / 2


def main():
    fulls = E.depth2_classes(); i, j = E.find_pair(fulls); Gi, Gj = fulls[i], fulls[j]
    P = {}
    for lab, G in (("i", Gi), ("j", Gj)):
        P[("NULL", lab)] = E.run_process(G, E.events_bud, E.ERASE_H, E.events_bud, E.FUT_K, True)
        P[("ERASE", lab)] = E.run_process(G, E.events_ext, E.ERASE_H, E.events_bud, E.FUT_K, True)
        P[("KEEP", lab)] = E.run_process(G, E.events_ext, E.ERASE_H, E.events_ext, E.FUT_K, False)
    steps = list(range(E.ERASE_H + E.FUT_K + 1))

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5))

    styles = {"NULL": ("#8a8a8a", "--", "o", "NULL  (BUD-only throughout)"),
              "KEEP": ("#1f77b4", "-", "s", "KEEP  (archive retained, extended future)"),
              "ERASE": ("#8e44ad", "-", "o", "ERASE (archive DELETED at H, BUD-only future)")}
    for proc in ("NULL", "KEEP", "ERASE"):
        col, ls, mk, lbl = styles[proc]
        ys = [tv(P[(proc, "i")][s], P[(proc, "j")][s]) for s in steps]
        axL.plot(steps, ys, ls, marker=mk, color=col, lw=2.2, ms=6, label=lbl)
    axL.axvline(E.ERASE_H, color="#c0392b", ls=":", lw=1.6)
    axL.annotate("archive deleted", (E.ERASE_H, axL.get_ylim()[1]), color="#c0392b",
                 fontsize=8, ha="center", xytext=(E.ERASE_H, 0.02), textcoords="data")
    axL.set_title("Q1 — do lineages i, j still differ? (TV distance between them)", fontsize=9.5)
    axL.set_xlabel("events elapsed"); axL.set_ylabel("total-variation distance  i vs j")
    axL.set_xticks(steps); axL.grid(alpha=0.25); axL.legend(fontsize=8, loc="upper left")

    for lab, col in (("i", "#1a7f37"), ("j", "#c0392b")):
        ys = [tv(P[("ERASE", lab)][s], P[("KEEP", lab)][s]) for s in steps]
        axR.plot(steps, ys, "-o", color=col, lw=2.2, ms=6,
                 label=f"lineage {lab}:  ERASE vs KEEP")
    axR.axvline(E.ERASE_H, color="#c0392b", ls=":", lw=1.6)
    axR.set_title("Q2 — does deleting the archive change the future? (ERASE vs KEEP)",
                  fontsize=9.5)
    axR.set_xlabel("events elapsed"); axR.set_ylabel("TV distance  ERASE vs KEEP")
    axR.set_xticks(steps); axR.grid(alpha=0.25); axR.legend(fontsize=8, loc="upper left")

    fig.suptitle("The ERASE test: the past leaves a DURABLE mark on the active slice (Q1, "
                 "ERASE stays >0 after deletion),\nyet the archive is NOT redundant (Q2, "
                 "ERASE≠KEEP after H). One matched pair; exact.", fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "erase_test.png")
    fig.savefig(out, dpi=140); print("wrote", out)


if __name__ == "__main__":
    main()
