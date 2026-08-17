#!/usr/bin/env python3
"""
Draw the acceptance-window pieces for the rank-4 family, to scale, coloured by
area. Makes the mechanism behind class (in)ertness visible: the congruence
classes are equal-width slabs of a fixed zonotope, so their areas follow the
solid's profile - a fat middle and thin ends - and the thin end-slabs are what
let the class predict vertex degree and leak into the address measurement.

Two panels per member: the exact window-piece polygons laid in a row (each the
2D Galois-plane slice at one congruence label), and the area spectrum as a bar,
annotated with the share of the window each piece holds. Golden's two 3.5%
end-slabs and platinum's four 5.3% ones are the geometrically forced slivers.

Singular convention throughout (extra_offset = 0), matching generate_rank4's
default. Areas are exact (linprog + halfspace intersection), not sampled.
"""

import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly
from matplotlib import cm, colors

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from window_geometry import pieces, measure


def ordered_pieces(N):
    """Window pieces as (area, polygon), largest first, singular convention."""
    P = pieces(N, extra_offset=(0.0, 0.0))
    out = [(measure(poly)[0], poly - poly.mean(0)) for _, poly in P]
    return sorted(out, key=lambda t: -t[0])


def main():
    families = [(10, "Golden  (10-fold, decagonal)"),
                (12, "Platinum  (12-fold, dodecagonal)")]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.6),
                             gridspec_kw=dict(width_ratios=[3.1, 1.0]))
    fig.suptitle("Rank-4 acceptance windows: the classes are unequal slabs of a "
                 "fixed solid\n(singular convention — exact piece areas, not sampled)",
                 fontsize=13, fontweight="bold")

    for row, (N, title) in enumerate(families):
        pcs = ordered_pieces(N)
        total = sum(a for a, _ in pcs)
        amax = max(a for a, _ in pcs)
        cmap = plt.get_cmap("viridis")
        norm = colors.Normalize(vmin=0, vmax=amax)

        # Left: the polygons in a row, each to scale, coloured by area.
        axp = axes[row, 0]
        span = 2.0 * max(np.abs(poly).max() for _, poly in pcs)
        x = 0.0
        for a, poly in pcs:
            p = poly.copy()
            p[:, 0] += x
            axp.add_patch(MplPoly(p, closed=True, facecolor=cmap(norm(a)),
                                  edgecolor="black", linewidth=1.1))
            axp.text(x, -span * 0.62, f"{100 * a / total:.1f}%",
                     ha="center", va="top", fontsize=10, fontweight="bold")
            axp.text(x, -span * 0.74, f"area {a:.2f}",
                     ha="center", va="top", fontsize=8, color="0.35")
            x += span
        axp.set_xlim(-span * 0.7, x - span + span * 0.7)
        axp.set_ylim(-span * 0.9, span * 0.7)
        axp.set_aspect("equal")
        axp.axis("off")
        axp.set_title(f"{title}   —   {len(pcs)} pieces", fontsize=11,
                      loc="left", fontweight="bold")

        # Right: area spectrum as a horizontal bar, thinnest at the bottom.
        axb = axes[row, 1]
        vals = [a for a, _ in pcs][::-1]
        ypos = np.arange(len(vals))
        axb.barh(ypos, [100 * v / total for v in vals],
                 color=[cmap(norm(v)) for v in vals],
                 edgecolor="black", linewidth=0.6)
        axb.set_yticks([])
        axb.set_xlabel("share of window (%)", fontsize=9)
        axb.axvline(100 / len(vals), color="crimson", ls="--", lw=1.0)
        axb.text(100 / len(vals), len(vals) - 0.4, " equal-share", color="crimson",
                 fontsize=8, va="top")
        axb.set_title("area spectrum", fontsize=10)
        for s in ("top", "right"):
            axb.spines[s].set_visible(False)

    fig.text(0.5, 0.005,
             "Equal-width slabs of a 3-D zonotope have unequal cross-sectional "
             "areas: a fat centre and thin ends. The thin end-slabs (Golden 3.5%, "
             "Platinum 5.3%) sit against the window boundary,\nso their vertices "
             "carry a distinct degree — that is the channel through which the "
             "congruence class leaks into the address measurement. No offset "
             "removes them; the imbalance is fixed by the field.",
             ha="center", fontsize=8.5, color="0.25")

    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    out = __file__.rsplit("/", 1)[0] + "/figures/window_slabs.png"
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=140)
    print("wrote", out)


if __name__ == "__main__":
    main()
