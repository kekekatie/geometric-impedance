#!/usr/bin/env python3
"""Comparison figure: exact return-to-start probabilities for the two walks, for the three
pairs (r*=3,4,5). Length-blind control is identical for both sites (grey = SSRW binomial);
the length-sensitive walk's return probabilities first differ at step 2(r*-1)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import motion_return as M

HERE = os.path.dirname(os.path.abspath(__file__))
binom = [q.real() for q in M.ssrw_binomial()]
evens = list(range(0, M.NSTEPS + 1, 2))

fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.6), sharey=True)
for ax, r in zip(axes, (3, 4, 5)):
    i, j = M.find_pair(r)
    si = [q.real() for q in M.return_probs(i, "sensitive")[0]]
    sj = [q.real() for q in M.return_probs(j, "sensitive")[0]]
    fd = next((n for n in range(M.NSTEPS + 1) if M.return_probs(i, "sensitive")[0][n]
               != M.return_probs(j, "sensitive")[0][n]), None)
    ax.plot(evens, [binom[n] for n in evens], "-", color="#bbb", lw=2, zorder=1,
            label="length-blind (both sites)")
    ax.plot(evens, [si[n] for n in evens], "-o", color="#1a7f37", ms=4, lw=1.8,
            label="length-sensitive, site i")
    ax.plot(evens, [sj[n] for n in evens], "--s", color="#c0392b", ms=4, lw=1.8,
            label="length-sensitive, site j")
    if fd is not None:
        ax.axvline(fd, color="#8e44ad", ls=":", lw=1.5)
        ax.annotate(f"return probs\nfirst differ\nat step {fd} = 2(r*−1)",
                    xy=(fd, 0.5), xytext=(fd + 0.6, 0.62), fontsize=8, color="#8e44ad")
    ax.set_title(f"pair with first-disagreement radius  r* = {r}", fontsize=10)
    ax.set_xlabel("walk step"); ax.set_xticks(evens)
    ax.grid(alpha=0.25)
axes[0].set_ylabel("P(back at start)")
axes[0].legend(fontsize=7.5, loc="upper right")
fig.suptitle("Does the far-out structural difference change motion? Exact return-to-start "
             "probabilities.\nLength-blind walk is identical for both sites (control); the "
             "length-sensitive walk first distinguishes them at step 2(r*−1) — motion feels "
             "the difference exactly when the walk can reach it.", fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.9])
fig.savefig(os.path.join(HERE, "figures", "motion_return.png"), dpi=140)
print("wrote figures/motion_return.png")
