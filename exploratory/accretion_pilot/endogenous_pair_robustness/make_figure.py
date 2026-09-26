#!/usr/bin/env python3
"""Figure for the pair-robustness study.
 Left : exact coast limit L for every matched pair, coloured by active-projection family;
        zeros (washout pairs) marked -- L is pair-specific, positive for most, zero for some.
 Right: the two flavours -- a durable pair's archive-free coast decaying to its positive L,
        vs a washout pair flat at 0 (archive difference never reaches the active layer)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pair_robustness as PR
import present_width as PW

HERE = os.path.dirname(os.path.abspath(__file__))
FAM_COLORS = {"91016ad6": "#1f77b4", "a3bec69c": "#1a7f37",
              "04fabdef": "#8e44ad", "176ca6f6": "#c0392b"}


def main():
    fulls = PW.depth2_classes()
    pairs = PR.all_matched_pairs(fulls)
    Ls, fams, labels = [], [], []
    for (a, b) in pairs:
        L, _, _ = PR.coast_limit(fulls[a], fulls[b])
        Ls.append(float(L)); fams.append(PW.wl(PW.erase(fulls[a]))[:8]); labels.append(f"{a},{b}")

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 5))

    xs = range(len(pairs))
    bars = axA.bar(xs, Ls, color=[FAM_COLORS.get(f, "#888") for f in fams], edgecolor="#333")
    for i, L in enumerate(Ls):
        if L == 0:
            axA.annotate("inert\nL=0", (i, 0.004), ha="center", va="bottom",
                         fontsize=7, color="#c0392b")
    axA.set_xticks(list(xs)); axA.set_xticklabels(labels, fontsize=8, rotation=45)
    axA.set_xlabel("matched pair (classes)"); axA.set_ylabel("exact coast limit  L")
    axA.set_title("L for every matched pair — durable (bar) vs inert (L=0)", fontsize=9.5)
    axA.grid(alpha=0.2, axis="y")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in FAM_COLORS.values()]
    axA.legend(handles, [f"proj family {k[:6]}" for k in FAM_COLORS], fontsize=7.5,
               title="active-projection family", title_fontsize=7.5)

    # right: durable vs washout coast
    dur = next((a, b) for (a, b) in pairs
               if PW.wl(PW.erase(fulls[a]))[:8] != PW.wl(PW.erase(fulls[0]))[:8]
               and PR.coast_limit(fulls[a], fulls[b])[0] > 0)
    ine = next((a, b) for (a, b) in pairs if PR.coast_limit(fulls[a], fulls[b])[0] == 0)
    for (pair, col, lab, ls) in [(dur, "#1a7f37", f"durable pair {dur}", "-o"),
                                 (ine, "#c0392b", f"inert pair {ine} (never expressed)", "--s")]:
        a, b = pair
        ef_i = PW.run_process(fulls[a], PW.events_ext, 2, PW.events_bud, 4, True)[1]
        ef_j = PW.run_process(fulls[b], PW.events_ext, 2, PW.events_bud, 4, True)[1]
        ys = [float(PW.tv(ef_i[s], ef_j[s])) for s in range(2, 7)]
        axB.plot(range(5), ys, ls, color=col, lw=2.2, ms=6, label=lab)
    Ld = float(PR.coast_limit(fulls[dur[0]], fulls[dur[1]])[0])
    axB.axhline(Ld, color="#1a7f37", ls=":", lw=1, alpha=0.6)
    axB.annotate(f"L = {Ld:.3f}", (4, Ld), fontsize=7.5, color="#1a7f37",
                 xytext=(3.1, Ld + 0.015), textcoords="data")
    axB.set_xlabel("archive-free coast step (after deletion at H=2)")
    axB.set_ylabel("distinguishability  i vs j (TV)")
    axB.set_title("Two fates of a deleted archive: durable residue vs inert (never expressed)",
                  fontsize=9.5)
    axB.set_xticks(range(5)); axB.grid(alpha=0.25); axB.legend(fontsize=8)

    fig.suptitle("Is the coast limit L one example's property? No — it is the pair's. The "
                 "finite-absorbing-chain STRUCTURE is universal.\nThree fates: durable (8/11, "
                 "L>0), inert (3/11, L=0, never expressed), washout (EMPTY) — every expressed "
                 "difference leaves a permanent residue.", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    out = os.path.join(HERE, "figures", "pair_robustness.png")
    fig.savefig(out, dpi=140); print("wrote", out)


if __name__ == "__main__":
    main()
