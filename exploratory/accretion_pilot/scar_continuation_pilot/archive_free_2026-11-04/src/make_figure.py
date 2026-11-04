#!/usr/bin/env python3
"""
make_figure.py -- w7 archive-free comparison figure: the worker's retained
material vs the genuinely deleted interior space it never consulted.
"""
from __future__ import annotations
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection
import af_common as AF
from af_common import L, dk
import isolated_worker as IW


def tri(t):
    return [(z.real, z.imag) for z in t[1:]]


def main():
    exports = json.loads((AF.INPUT / "worker_band_exports.json").read_text())
    ex = exports["w7-s0"]
    band = [IW.dtile(t) for t in ex["final"]]
    full = [IW.dtile(t) for t in ex["full_final"]]
    band_keys = {repr(dk(t)) for t in band}
    deleted = [t for t in full if repr(dk(t)) not in band_keys]

    fig, ax = plt.subplots(figsize=(11, 10))
    # genuinely deleted interior (never consulted by the worker)
    ax.add_collection(PatchCollection([MPoly(tri(t)) for t in deleted],
                                      facecolor="#f3f4f5", edgecolor="#e2e5e7", linewidths=0.15))
    # worker retained band (its entire world)
    ax.add_collection(PatchCollection([MPoly(tri(t)) for t in band],
                                      facecolor="#8fb8e6", edgecolor="#5d8dc0", linewidths=0.25))
    # pinned scars
    for ek in ex["scars"]:
        p, q = [complex(*v) for v in ek]
        ax.plot([p.real, q.real], [p.imag, q.imag], "-", color="#c0392b", lw=3)
        m = (p + q) / 2
        ax.plot(m.real, m.imag, "x", color="#c0392b", ms=9, mew=2)

    handles = [
        mpatches.Patch(color="#8fb8e6", label=f"worker RETAINED band ({len(band)} tiles) — its entire world"),
        mpatches.Patch(color="#f3f4f5", label=f"GENUINELY DELETED interior ({len(deleted)} tiles) — never consulted"),
        plt.Line2D([], [], color="#c0392b", marker="x", lw=3, label=f"pinned scars ({len(ex['scars'])})"),
    ]
    ax.legend(handles=handles, fontsize=10, loc="upper left")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("w7-B-s0 archive-free scar continuation to step 44\n"
                 "the radius-2 retained band reproduces the full-patch scheduler EXACTLY, "
                 "without the deleted interior",
                 fontsize=11)
    fig.tight_layout()
    AF.FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(AF.FIGURES / "archive_free_w7.png", dpi=140, bbox_inches="tight")
    print(f"wrote figures/archive_free_w7.png (band {len(band)}, deleted {len(deleted)})")


if __name__ == "__main__":
    main()
