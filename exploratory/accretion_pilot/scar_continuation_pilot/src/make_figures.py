#!/usr/bin/env python3
"""
make_figures.py -- Phase 3 diagnostic figures for w7-B-s0 and w5-B-s0.

Each figure shows, on the scar-tolerant continuation to step 44:
  * the original jam notch / pinned_scar sites (red),
  * new tiles accreted between the jam step and step 44 (blue),
  * tiles already present at the jam (grey),
  * the maximal connected compatible sub-arc of the FINAL retained band (green
    outline) that reads the historical B choice.

Writes figures/scar_w{7,5}.png.
"""
from __future__ import annotations
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection
import scar_common as SC
import arc_tools as AT
import scar_continuation as SCN

SCAN_STEPS = 32
COMPAT_TOL = 1e-9


def tri(t):
    return [(z.real, z.imag) for z in t[1:]]


def maximal_arc_tiles(state_like, band, c, theta0):
    center = theta0 + math.pi
    best = None
    for i in range(1, SCAN_STEPS + 1):
        hw = math.pi * i / SCAN_STEPS
        win = AT.angular_window(band, c, center, hw)
        comp = AT.largest_component(win)
        sc = AT.score_arc(state_like, comp)
        if (sc["F_area"] or 0.0) > COMPAT_TOL and (best is None or len(comp) > len(best)):
            best = comp
    return best or []


def figure(world, si, path):
    jam = SC.jam_state(world, si)
    res = SCN.scar_grow(world, si, steps=44, record_illegal=False)
    jam_keys = {SC.dk(t) for t in jam["full"]}
    final_full = res["full"]
    band = res["band"]
    band_keys = {SC.dk(t) for t in band}
    state_like = dict(Sstar=res["Sstar"], cs=res["cs"], B=res["B"], band=band)

    c = AT.centroid(band)
    # notch anchor at scar region
    pts = [sum(complex(*v) for v in ek) / 2 for ek in res["scars"]]
    th0 = math.atan2((sum(pts) / len(pts) - c).imag, (sum(pts) / len(pts) - c).real) if pts else 0.0
    arc = maximal_arc_tiles(state_like, band, c, th0)
    arc_keys = {SC.dk(t) for t in arc}

    old = [t for t in final_full if SC.dk(t) in jam_keys]
    new = [t for t in final_full if SC.dk(t) not in jam_keys]

    fig, ax = plt.subplots(figsize=(11, 10))
    ax.add_collection(PatchCollection([MPoly(tri(t)) for t in old],
                                      facecolor="#edf0f2", edgecolor="#cfd6da", linewidths=0.2))
    ax.add_collection(PatchCollection([MPoly(tri(t)) for t in new],
                                      facecolor="#bcd4ee", edgecolor="#89aed6", linewidths=0.2))
    # maximal compatible sub-arc of the final band (green fill over band tiles)
    arc_tiles = [t for t in band if SC.dk(t) in arc_keys]
    ax.add_collection(PatchCollection([MPoly(tri(t)) for t in arc_tiles],
                                      facecolor="#8fd6a0", edgecolor="#3f9a5c", linewidths=0.3, alpha=0.75))
    # pinned scar edges
    for ek in res["scars"]:
        p, q = [complex(*v) for v in ek]
        ax.plot([p.real, q.real], [p.imag, q.imag], "-", color="#c0392b", lw=3)
        m = (p + q) / 2
        ax.plot(m.real, m.imag, "x", color="#c0392b", ms=9, mew=2)

    import matplotlib.patches as mpatches
    handles = [
        mpatches.Patch(color="#edf0f2", label=f"tiles present at jam (step {res['jam_step']})"),
        mpatches.Patch(color="#bcd4ee", label=f"new tiles accreted (jam→44): +{len(new)}"),
        mpatches.Patch(color="#8fd6a0", label=f"maximal compatible sub-arc of final band ({len(arc_tiles)} tiles) → reads B"),
        plt.Line2D([], [], color="#c0392b", marker="x", lw=3, label=f"pinned_scar sites ({res['n_scars']})"),
    ]
    ax.legend(handles=handles, fontsize=9, loc="upper left")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"w{world}-B-s{si}: scar-tolerant continuation to step 44\n"
                 f"global band stays incompatible; historical B survives in a connected compatible sub-arc",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path} (jam-tiles {len(old)}, new {len(new)}, arc {len(arc_tiles)}, scars {res['n_scars']})")


def main():
    SC.FIGURES.mkdir(parents=True, exist_ok=True)
    figure(7, 0, SC.FIGURES / "scar_w7.png")
    figure(5, 0, SC.FIGURES / "scar_w5.png")


if __name__ == "__main__":
    main()
