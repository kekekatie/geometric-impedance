#!/usr/bin/env python3
"""Survival ladder: how much of the coherent address increment survives each control.
See RESULTS_TRANSPORT.md (WHAT-diagnostic addendum). Numbers from transport_run.py."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# coherent primary window; M4 address increment over successively stronger baselines
controls = ["raw\n(over M3)", "over\nM3+position", "over M3+\nlong-range physical",
            "address\nshuffled"]
golden   = [0.0310, 0.0317, 0.0294, -0.0046]
platinum = [0.0885, 0.0896, 0.0728, 0.0125]
silver   = [0.0905, 0.0911, 0.0394, 0.0261]

x = np.arange(len(controls))
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, golden, "o-", color="#e45756", lw=2.4, ms=9, label="golden (N=10)")
ax.plot(x, platinum, "s-", color="#54a24b", lw=2.4, ms=8, label="platinum (N=12)")
ax.plot(x, silver, "^-", color="#4c78a8", lw=2.4, ms=8, label="silver (N=8)")
ax.axhline(0, color="0.5", lw=0.9, ls="--")
ax.set_xticks(x); ax.set_xticklabels(controls, fontsize=10)
ax.set_ylabel("coherent M4 address increment (held-out R²)")
ax.set_title("What is the address really carrying?\n"
             "how much of the coherent signal survives each control")
ax.legend(frameon=False, fontsize=11, loc="upper right")

ax.annotate("golden: survives long-range physical,\ndies only when the address is scrambled\n"
            "→ genuine non-redundant address",
            (2, 0.0294), xytext=(1.2, 0.052), fontsize=8.5, color="#7a1f1e",
            arrowprops=dict(arrowstyle="->", color="#7a1f1e", lw=0.8))
ax.annotate("silver: ~half is long-range\nphysical structure",
            (2, 0.0394), xytext=(2.05, 0.066), fontsize=8.5, color="#274a6d",
            arrowprops=dict(arrowstyle="->", color="#274a6d", lw=0.8))

ax.text(0.5, -0.14,
        "A control that DROPS a family's line removed real signal.  golden barely moves until "
        "the address itself is scrambled → the wave reads the address, not a physical proxy.\n"
        "silver falls steeply at 'long-range physical' → much of what looked like address was "
        "long-range real-space structure that perpendicular space compactly encodes.",
        transform=ax.transAxes, ha="center", va="top", fontsize=8.5, color="0.3")

out = __file__.rsplit("/", 1)[0] + "/transport_what.png"
fig.savefig(out, dpi=130, bbox_inches="tight")
print("wrote", out)
