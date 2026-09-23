#!/usr/bin/env python3
"""Two-panel figure for the present-width study.
 Left  (Part 1): the present progressively inherits the past -- full-state vs present-only
       distinguishability, and the surviving fraction rho(h).
 Right (Part 2): once the past is deleted the present coasts (fade-or-hold, provably
       non-increasing); with the archive kept, distinguishability holds/grows (needs the past)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import present_width as P


def main():
    fulls = P.depth2_classes(); i, j = P.find_pair(fulls); Gi, Gj = fulls[i], fulls[j]

    # Part 1
    H1 = 3
    fi, si = P.run_process(Gi, P.events_ext, H1, P.events_ext, 0, False)
    fj, sj = P.run_process(Gj, P.events_ext, H1, P.events_ext, 0, False)
    hs = list(range(H1 + 1))
    Dfull = [float(P.tv(fi[h], fj[h])) for h in hs]
    Dslice = [float(P.tv(si[h], sj[h])) for h in hs]
    rho = [(Dslice[h] / Dfull[h]) if Dfull[h] else 0.0 for h in hs]

    # Part 2
    H, K = 2, 3
    ef_i = P.run_process(Gi, P.events_ext, H, P.events_bud, K, True)[1]
    ef_j = P.run_process(Gj, P.events_ext, H, P.events_bud, K, True)[1]
    kp_i = P.run_process(Gi, P.events_ext, H, P.events_ext, K, False)[1]
    kp_j = P.run_process(Gj, P.events_ext, H, P.events_ext, K, False)[1]
    ss = list(range(H + K + 1))
    coast = [float(P.tv(ef_i[s], ef_j[s])) for s in ss]
    kept = [float(P.tv(kp_i[s], kp_j[s])) for s in ss]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.5, 5.2))

    axL.plot(hs, Dfull, "-o", color="#333", lw=2.2, label="D_full  (active + archive)")
    axL.plot(hs, Dslice, "-o", color="#1a7f37", lw=2.2, label="D_slice (present only)")
    axL.set_xlabel("history imprinted  h  (events)")
    axL.set_ylabel("distinguishability of the two lineages (TV)")
    axL.set_xticks(hs); axL.set_ylim(-0.03, 1.03); axL.grid(alpha=0.25)
    axL.set_title("Part 1 — the present progressively inherits the past", fontsize=9.5)
    ax2 = axL.twinx()
    ax2.plot(hs, rho, ":D", color="#8e44ad", lw=2, label="rho = slice / full (right axis)")
    ax2.set_ylabel("surviving fraction  rho", color="#8e44ad")
    ax2.set_ylim(-0.03, 1.03); ax2.tick_params(axis="y", labelcolor="#8e44ad")
    l1, la1 = axL.get_legend_handles_labels(); l2, la2 = ax2.get_legend_handles_labels()
    axL.legend(l1 + l2, la1 + la2, fontsize=8, loc="center right")

    axR.plot(ss, kept, "-s", color="#1f77b4", lw=2.2, ms=6,
             label="archive KEPT (extended): holds / grows")
    axR.plot(ss, coast, "-o", color="#8e44ad", lw=2.4, ms=6,
             label="archive DELETED (coast, BUD-only): fade-or-hold")
    axR.axvline(H, color="#c0392b", ls=":", lw=1.6)
    axR.annotate("past deleted", (H, 0.02), color="#c0392b", fontsize=8, ha="center")
    L_LIMIT = 4321 / 44100          # exact coast limit L = 4321/44100 (Proposition 3, coast_asymptote.py)
    axR.axhline(L_LIMIT, color="#8e44ad", ls="--", lw=1, alpha=0.6)
    axR.annotate("coast → exact limit L = 4321/44100 ≈ 0.098\n(Prop 3: permanent ensemble "
                 "bias, not a per-world memory)",
                 (H + K, L_LIMIT), fontsize=7.5, color="#8e44ad",
                 xytext=(H + 0.3, L_LIMIT + 0.03), textcoords="data")
    axR.set_xlabel("events elapsed"); axR.set_ylabel("distinguishability (TV)  i vs j")
    axR.set_xticks(ss); axR.set_ylim(-0.01, 0.2); axR.grid(alpha=0.25)
    axR.set_title("Part 2 — coasting momentum vs a re-read past (the width of 'now')",
                  fontsize=9.5)
    axR.legend(fontsize=8, loc="lower right")

    fig.suptitle("How much of the past biases the present, and for how long "
                 "(an ensemble bias, not a per-world memory).\n"
                 "The distribution over presents starts unbiased and becomes biased (Part 1); "
                 "once the past is deleted the bias can only fade to an exact limit, held above "
                 "it only while the past is kept (Part 2).", fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures",
                       "present_width.png")
    fig.savefig(out, dpi=140); print("wrote", out)


if __name__ == "__main__":
    main()
