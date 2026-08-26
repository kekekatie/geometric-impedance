#!/usr/bin/env python3
"""Coherence ladder: where does the address-reading live? (see RESULTS_COHERENCE.md)
Numbers from wave_dephasing.py (short times 0.3/0.6/1.2, 4 offsets, extent 12)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rungs = ["coherent return\n(full interference)", "diagonal ensemble\n(dynamical phase gone)",
         "classical return\n(diffusive, no signed\namplitude structure)"]
silver   = [0.0792, 0.0816, 0.0037]
golden   = [0.0317, 0.0319, 0.0012]
platinum = [0.0746, 0.0610, 0.0011]

x = np.arange(3)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, silver, "^-", color="#4c78a8", lw=2.4, ms=9, label="silver (N=8)")
ax.plot(x, golden, "o-", color="#e45756", lw=2.4, ms=10, label="golden (N=10)")
ax.plot(x, platinum, "s-", color="#54a24b", lw=2.4, ms=9, label="platinum (N=12)")
ax.axhline(0, color="0.6", lw=0.8, ls="--")
ax.set_xticks(x); ax.set_xticklabels(rungs, fontsize=10)
ax.set_xlim(-0.3, 2.3)
ax.set_ylabel("coherent M4 address increment (held-out R²)")
ax.set_title("Where does the address-reading live?\n"
             "plateau (1→2) then cliff (2→3): the coherent stationary spectral structure, "
             "not dynamical interference")
ax.legend(frameon=False, fontsize=11, loc="center left")

ax.annotate("dynamical interference\nadds ~nothing\n(1 ≈ 2)", (0.5, 0.075),
            ha="center", fontsize=9, color="0.35")
ax.annotate("the cliff:\ncoherent Hψ=Eψ modes → classical diffusion\nkills the address-reading",
            (1.62, 0.032), xytext=(1.02, 0.050), fontsize=9, color="#7a1f1e",
            arrowprops=dict(arrowstyle="->", color="#7a1f1e", lw=1.0))

ax.text(0.5, -0.15,
        "The diagonal ensemble has NO dynamical phase between eigenstates, yet reads the "
        "address as well as the fully coherent wave.\nThe classical walker (stochastic "
        "probability relaxation, no interference) reads nothing.\n→ the address lives in the "
        "coherent Hamiltonian's stationary spectral structure, not in dynamical phase "
        "interference between eigenstates.",
        transform=ax.transAxes, ha="center", va="top", fontsize=8.3, color="0.3")

out = __file__.rsplit("/", 1)[0] + "/coherence_ladder.png"
fig.savefig(out, dpi=130, bbox_inches="tight")
print("wrote", out)
