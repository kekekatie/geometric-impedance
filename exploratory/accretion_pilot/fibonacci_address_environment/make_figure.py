#!/usr/bin/env python3
"""Diagram: the Fibonacci physical chain and its internal acceptance window, with sites
marked consistently, the r=2 environment cells, and the three examples."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import fibonacci_cutproject as F

HERE = os.path.dirname(os.path.abspath(__file__))
pts = F.generate(46)
g = F.gaps_of(pts)
N = len(pts)
r = 2
bnd = F.region_boundaries(r)

# environment per cell
cell_env = {}
for i in range(r, N - r):
    q = pts[i][1]
    ci = max(k for k in range(len(bnd) - 1) if bnd[k] <= q)
    cell_env[ci] = "".join(g[i - r:i + r])

# the three example pairs (identical selection to the checks)
exA, exB, exC = F.examples(pts, g, N, r)


def pair(ex):
    qd, pd, i, j, _ = ex
    return qd, pd, pts[i][1].real(), pts[j][1].real()


TAU = F.TAU_F

fig, (axP, axI) = plt.subplots(2, 1, figsize=(13, 6.4),
                               gridspec_kw={"height_ratios": [1, 1.5]})

# ---- physical chain (a stretch near origin) ----
p0 = [p.real() for p, q, mn in pts]
i_lo = next(i for i, p in enumerate(p0) if p >= 0)
i_hi = next(i for i, p in enumerate(p0) if p >= 26)
for i in range(i_lo, i_hi):
    x0, x1 = p0[i], p0[i + 1]
    col = "#2c7fb8" if g[i] == "L" else "#d95f0e"
    axP.plot([x0, x1], [0, 0], "-", color=col, lw=6, solid_capstyle="butt")
    axP.text((x0 + x1) / 2, 0.16, g[i], ha="center", fontsize=8, color=col)
for i in range(i_lo, i_hi + 1):
    axP.plot([p0[i]], [0], "o", ms=6, color="#222", zorder=3)
axP.set_title("physical Fibonacci chain  (site positions m + nτ;  tiles L = τ, S = 1) — "
              "aperiodic, two tile lengths", fontsize=10)
axP.set_xlim(-0.5, 26); axP.set_ylim(-0.6, 0.7); axP.set_yticks([]); axP.set_xlabel("physical position")

# ---- internal window W=[0,tau) with cells + sites + examples ----
cellcols = ["#f7fbff", "#e5eef7", "#d3e3f0", "#c1d7e9", "#aecbe2", "#9cc0db"]
for k in range(len(bnd) - 1):
    x0, x1 = bnd[k].real(), bnd[k + 1].real()
    axI.axvspan(x0, x1, ymin=0.30, ymax=0.92, color=cellcols[k % len(cellcols)], zorder=0)
    axI.text((x0 + x1) / 2, 0.98, cell_env.get(k, "?"), ha="center", va="bottom",
             fontsize=8, family="monospace", rotation=0)
for b_ in bnd:
    axI.axvline(b_.real(), ymin=0.30, ymax=0.92, color="#555", lw=1, ls="--")
# all site internal coords as ticks
for i in range(N):
    axI.plot([pts[i][1].real()], [0.30], "|", ms=9, color="#888", zorder=2)

# example markers
def mark(ex, y, color, label):
    qd, pd, qx, qy = pair(ex)
    axI.plot([qx, qy], [y, y], "-", color=color, lw=1.4, zorder=4)
    axI.plot([qx, qy], [y, y], "o", color=color, ms=7, zorder=5)
    axI.annotate(f"{label}: |Δq|={qd:.3f}, |Δp|={pd:.1f}",
                 xy=((qx + qy) / 2, y), xytext=((qx + qy) / 2, y - 0.075),
                 ha="center", fontsize=8, color=color)

mark(exA, 0.20, "#1a7f37", "(a) same env")
mark(exB, 0.10, "#c0392b", "(b) diff env (boundary between)")
mark(exC, 0.00, "#8e44ad", "(c) same env, wide Δq")
axI.set_title("internal acceptance window  W = [0, τ)  — partitioned into environment "
              "CELLS (r=2, 4-letter word above each). The environment is a function of the "
              "internal address alone.", fontsize=10)
axI.set_xlim(-0.03, TAU + 0.03); axI.set_ylim(-0.12, 1.1)
axI.set_yticks([]); axI.set_xlabel("internal (perpendicular) address  q = m + nτ'")

fig.suptitle("Fibonacci cut-and-project: what internal-address proximity guarantees — "
             "same cell ⇒ identical local environment (any physical distance); a cell "
             "boundary between ⇒ different environment (even if internally close)", fontsize=10.5)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(HERE, "figures", "fibonacci_address_environment.png"), dpi=140)
print("wrote figures/fibonacci_address_environment.png")
