#!/usr/bin/env python3
"""
Two panels summarising the unbiased-dynamics result.

Left: Branch A structural loss per flip (extent 12, 6 seeds). The three families
lie almost on top of each other - matched flips give matched microscopic damage,
family-independent, with only a small saturation-regime spread.

Right: history recoverability (extent 10, 6 seeds). Clustered-vs-dispersed damage
is plainly distinguishable at the instant it is applied, then unbiased mobility
erases the separation within ~0.06 flips/vertex - the same for all three fields.
Free phason dynamics forget, and forget alike.

Values are the confirmed run means/sds recorded in RECOVERY_UNBIASED.md.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

FPV = [0.02, 0.05, 0.10, 0.15, 0.20, 0.35]
LOSS = {"silver": [0.038, 0.085, 0.149, 0.199, 0.239, 0.314],
        "golden": [0.037, 0.082, 0.144, 0.188, 0.228, 0.302],
        "platinum": [0.037, 0.084, 0.142, 0.184, 0.218, 0.292]}

RELAX = [0.0, 0.06, 0.18]
SEP = {"silver": ([0.448, 0.044, 0.006], [0.082, 0.051, 0.017]),
       "golden": ([0.383, 0.052, -0.027], [0.121, 0.145, 0.076]),
       "platinum": ([0.486, 0.049, -0.033], [0.083, 0.039, 0.049])}

COL = {"silver": "#4c72b0", "golden": "#dd8452", "platinum": "#55a868"}


def main():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.5, 5.0))
    fig.suptitle("Unbiased phason dynamics: no recovery, no retained history, "
                 "no family difference", fontsize=13, fontweight="bold")

    for nm, y in LOSS.items():
        axL.plot(FPV, y, "-o", color=COL[nm], label=nm, lw=2, ms=5)
    axL.set_xlabel("damage  (flips per vertex)")
    axL.set_ylabel("structural loss  (1 − vertex Jaccard)")
    axL.set_title("Branch A — loss per flip is family-independent", fontsize=11)
    axL.legend(frameon=False)
    axL.grid(alpha=0.25)

    for nm, (m, s) in SEP.items():
        axR.errorbar(RELAX, m, yerr=s, fmt="-o", color=COL[nm], label=nm,
                     lw=2, ms=5, capsize=3)
    axR.axhline(0, color="0.5", lw=0.8, ls="--")
    axR.set_xlabel("free relaxation after damage  (flips per vertex)")
    axR.set_ylabel("history separation  (CE$_{dispersed}$ − CE$_{clustered}$)")
    axR.set_title("History — present at t=0, erased almost at once", fontsize=11)
    axR.legend(frameon=False)
    axR.grid(alpha=0.25)
    axR.annotate("history plainly present\njust after damage",
                 xy=(0.0, 0.44), xytext=(0.05, 0.50), fontsize=8.5, color="0.3",
                 arrowprops=dict(arrowstyle="->", color="0.5"))
    axR.annotate("gone after a whisker\nof free dynamics",
                 xy=(0.06, 0.05), xytext=(0.09, 0.22), fontsize=8.5, color="0.3",
                 arrowprops=dict(arrowstyle="->", color="0.5"))

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = __file__.rsplit("/", 1)[0] + "/figures/recovery_unbiased.png"
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
