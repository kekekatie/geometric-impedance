#!/usr/bin/env python3
"""Figure: the M4-over-M3 transport increment and its controls (see RESULTS_TRANSPORT.md)."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# coherent primary window; numbers from transport_run.py (committed run)
fam = ["silver\n(N=8)", "golden\n(N=10)", "platinum\n(N=12)"]
raw      = [0.0905, 0.0310, 0.0885]     # M4 - M3
shuffle  = [0.0261, -0.0046, 0.0125]    # M4(stratified-shuffle) - M3   (address destroyed)
position = [0.0911, 0.0317, 0.0896]     # M4 - (M3 + x,y,r)             (position controlled)
incoh    = [0.0036, 0.0023, 0.0025]     # incoherent M4 - M3

x = np.arange(3); w = 0.2
fig, ax = plt.subplots(figsize=(10, 6))
b1 = ax.bar(x - 1.5*w, raw, w, label="coherent M4−M3 (raw)", color="#e45756")
b2 = ax.bar(x - 0.5*w, shuffle, w, label="…address shuffled (stratified)", color="#f2b0af")
b3 = ax.bar(x + 0.5*w, position, w, label="…physical position controlled", color="#b23b3a")
b4 = ax.bar(x + 1.5*w, incoh, w, label="incoherent M4−M3 (null)", color="#9aa0a6")

ax.axhline(0, color="0.4", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(fam)
ax.set_ylabel("held-out R²  increment of M4 over M3")
ax.set_title("Does a physical law read the address?\n"
             "coherent transport carries multiscale-address structure; "
             "the incoherent null does not")
ax.set_ylim(-0.012, 0.108)
ax.legend(frameon=False, fontsize=9, loc="upper center", ncol=2)

# annotate the address-specific gap (raw minus shuffle)
for i in range(3):
    gap = raw[i] - shuffle[i]
    ax.text(x[i], 0.055, f"address-specific\n≈ {gap:+.3f}",
            ha="center", va="center", fontsize=8.5, color="#7a1f1e",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#e0c0c0", lw=0.5))

ax.text(0.5, -0.16,
        "raw ≈ shuffled  → not address (silver: a third survives).   "
        "raw ≫ shuffled ≈ 0  → genuine address (golden: fully killed).\n"
        "raw ≈ position-controlled everywhere → not a smooth-coordinate artefact.   "
        "incoherent ≈ 0 everywhere → the random walk reads no address.",
        transform=ax.transAxes, ha="center", va="top", fontsize=8.5, color="0.3")

out = __file__.rsplit("/", 1)[0] + "/transport_result.png"
fig.savefig(out, dpi=130, bbox_inches="tight")
print("wrote", out)
