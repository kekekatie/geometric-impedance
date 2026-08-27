#!/usr/bin/env python3
"""Figure: confined weight decomposed into radial depth + (≈0) angular + neighbourhood
address organization. Numbers from address_split.py (held-out R², 3 offsets)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fam = ["platinum\n(N=12)", "golden\n(N=10)", "silver\n(N=8)"]
radial = [0.212, 0.447, 0.676]
nbhd   = [0.531, 0.307, 0.294]     # neighbourhood address org, beyond depth+angular
# angular contribution is ~0 everywhere (−0.004, −0.033, +0.075); shown as a note

y = np.arange(3)
fig, ax = plt.subplots(figsize=(10, 4.8))
b1 = ax.barh(y, radial, color="#b8860b", label="radial window-depth")
b2 = ax.barh(y, nbhd, left=radial, color="#2a7f9e",
             label="neighbourhood address organization")
for i in range(3):
    ax.text(radial[i]+nbhd[i]+.012, y[i], f"total R² {radial[i]+nbhd[i]:.2f}",
            va="center", fontsize=9, color="#333")
    ax.text(radial[i]/2, y[i], f"{radial[i]:.2f}", va="center", ha="center",
            fontsize=9, color="white", fontweight="bold")
    ax.text(radial[i]+nbhd[i]/2, y[i], f"+{nbhd[i]:.2f}", va="center", ha="center",
            fontsize=9, color="white", fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels(fam)
ax.set_xlabel("held-out R² predicting E≈0 confined-state weight")
ax.set_xlim(0, 1.05)
ax.set_title("What decides a vertex's confined-state role?\n"
             "radial window-depth + neighbourhood address organization "
             "(angular position adds ≈0)")
ax.legend(frameon=False, loc="lower right", fontsize=9)
fig.text(0.13, -0.02, "Angular position on a depth-ring contributes ≈0 in all three "
         "(−0.00 / −0.03 / +0.08) — the pointwise window field is radially symmetric.  "
         "The neighbourhood\nterm survives fixing the exact fine vertex type, and is the "
         "same multiscale address a coherent wave reads in transport.",
         fontsize=8.4, color="0.35")
out = __file__.rsplit("/", 1)[0] + "/address_split.png"
fig.savefig(out, dpi=130, bbox_inches="tight")
print("wrote", out)
