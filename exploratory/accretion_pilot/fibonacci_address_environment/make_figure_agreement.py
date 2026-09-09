#!/usr/bin/env python3
"""Diagram: the window partition refines with radius r; two same-E_2 sites agree until the
refinement first drops a boundary between their internal addresses (their r*)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import agreement_radius as AR

HERE = os.path.dirname(os.path.abspath(__file__))
pts, g, N = AR.pts, AR.g, AR.N
TAU = AR.F.TAU_F
RS = [2, 3, 4, 5, 6]

# recompute the same three examples + unresolved pair as the checks
idx = [i for i in range(N) if AR.rmax(i) >= 2]
pairs = [(idx[a], idx[b]) for a in range(len(idx)) for b in range(a + 1, len(idx))
         if AR.env(idx[a], 2) == AR.env(idx[b], 2)]
by_r, unres = {}, []
for (i, j) in pairs:
    rs, thru, res = AR.first_disagreement(i, j)
    if res:
        by_r.setdefault(rs, (i, j, rs, thru))
    else:
        unres.append((i, j, thru))
examples = [by_r[r] for r in sorted(by_r)][:3]
unres.sort(key=lambda t: -t[2])
uex = unres[0] if unres else None

fig, ax = plt.subplots(figsize=(13, 6.2))

# refinement ladder: one row per r, boundaries as ticks (new ones highlighted)
for row, r in enumerate(RS):
    y = row
    ax.hlines(y, 0, TAU, color="#eee", lw=8, zorder=0)
    B = AR.boundaries(r); Bprev = AR.boundaries(r - 1) if r > 2 else []
    for b in B:
        new = b not in Bprev
        ax.vlines(b.real(), y - 0.34, y + 0.34,
                  color=("#e67e22" if new else "#95a5a6"),
                  lw=(2.4 if new else 1.2), zorder=2)
    ax.text(-0.06, y, f"r={r}", ha="right", va="center", fontsize=9)
    ax.text(TAU + 0.02, y, f"{len(B)-1} cells", ha="left", va="center", fontsize=8, color="#777")

# the three example pairs, drawn on a lane below, each split at its own r*
cols = ["#1a7f37", "#2980b9", "#8e44ad"]
lane0 = -1.2
for k, (i, j, rs, thru) in enumerate(examples):
    y = lane0 - k * 0.9
    qi, qj = pts[i][1].real(), pts[j][1].real()
    ax.hlines(y, min(qi, qj), max(qi, qj), color=cols[k], lw=2, zorder=3)
    ax.plot([qi, qj], [y, y], "o", color=cols[k], ms=7, zorder=4)
    sb = AR.sep_boundary(i, j, rs)
    for b in sb:
        ax.vlines(b.real(), y - 0.3, RS.index(rs) + 0.34, color=cols[k], ls="--", lw=1.3, zorder=1)
    ax.text((qi + qj) / 2, y - 0.34,
            f"agree to r={thru}, split at r*={rs}   |Δq|={abs(qi-qj):.3f}",
            ha="center", va="top", fontsize=8, color=cols[k])

if uex:
    i, j, thru = uex
    y = lane0 - 3 * 0.9
    qi, qj = pts[i][1].real(), pts[j][1].real()
    ax.hlines(y, min(qi, qj), max(qi, qj), color="#c0392b", lw=2, zorder=3)
    ax.plot([qi, qj], [y, y], "s", color="#c0392b", ms=6, zorder=4)
    ax.text((qi + qj) / 2, y - 0.34,
            f"agree to r={thru} = patch limit → UNRESOLVED (not 'forever'): distinct "
            f"addresses, |Δq|={abs(qi-qj):.3f}", ha="center", va="top", fontsize=8, color="#c0392b")

ax.set_xlim(-0.16, TAU + 0.16); ax.set_ylim(lane0 - 3 * 0.9 - 0.7, len(RS) - 0.4)
ax.set_yticks([]); ax.set_xlabel("internal (perpendicular) address  q")
ax.set_title("Same here, different farther out: two sites with identical E₂ agree until the "
             "refining window partition\nfirst places a boundary between their (distinct) "
             "internal addresses — that radius is r*.   (orange = boundary newly added at that r)",
             fontsize=10.5)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "figures", "agreement_radius.png"), dpi=140)
print("wrote figures/agreement_radius.png")
