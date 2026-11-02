#!/usr/bin/env python3
"""
audit_figures.py -- corrected witness figure for the 2026-11-02 audit.

The study's part4 figures draw the binding half-planes but never compute whether
they oppose. This figure draws each recorded IIS in offset (t) space with the
measured unit-normal geometry annotated, making the corrected finding explicit:
w7 (both states) and w5 first-infeasible are genuine ANTI-PARALLEL pairs
(unit dot = -1); the w5 jam witness is a THREE-FACET squeeze of ONE pentagon
(rank 3, facets 2/3/4), not an opposing pair.

Writes figures/audit_witness_halfplanes.png.
"""
from __future__ import annotations
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import audit_common as A
from audit_common import Sl, WIN
import part4_iis as P4


def iis_for(tiles, label):
    rec, p = P4.analyse(tiles, label)
    return [tuple(k) for k in p["iis"]], p["cmax"]


def draw(ax, cmax, iis, title):
    xs = np.linspace(-3, 3, 2)
    dots = []
    units = []
    for key in iis:
        rk, i = key
        n, h = WIN[rk]
        nx, ny = float(n[i][0]), float(n[i][1]); nn = (nx*nx+ny*ny)**0.5
        ux, uy = nx/nn, ny/nn; c = float(cmax[key]) / nn
        units.append((ux, uy))
        p0 = np.array([ux, uy]) * c; d = np.array([-uy, ux])
        seg = np.array([p0 - 3*d, p0 + 3*d])
        ax.plot(seg[:, 0], seg[:, 1], "-", lw=2, label=f"rk{rk} facet{i}")
        ax.annotate("", xy=p0 + 0.45*np.array([ux, uy]), xytext=p0,
                    arrowprops=dict(arrowstyle="->", lw=1.5, color="gray"))
    for a in range(len(units)):
        for b in range(a+1, len(units)):
            dots.append(round(units[a][0]*units[b][0] + units[a][1]*units[b][1], 3))
    kind = "anti-parallel pair" if (len(iis) == 2 and any(abs(d+1) < 1e-6 for d in dots)) \
        else ("single-pentagon 3-facet squeeze" if len({k[0] for k in iis}) == 1 and len(iis) >= 3
              else "multi-constraint")
    ax.set_title(f"{title}\nIIS {[list(k) for k in iis]}  unit-dots {dots}\n{kind}", fontsize=8)
    ax.set_aspect("equal"); ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
    ax.axhline(0, color="#ddd", lw=.5); ax.axvline(0, color="#ddd", lw=.5)
    ax.legend(fontsize=6, loc="upper right")


def main():
    A.FIGURES.mkdir(parents=True, exist_ok=True)
    panels = []
    for (w, si, js, fi) in [(7, 0, 23, 9), (5, 0, 42, 17)]:
        arm, full, skin = A.jam_full_and_skin(w, si, js)
        full_fi = arm["snaps"][fi]
        panels.append((full_fi, f"w{w} first-infeasible full @ {fi}"))
        panels.append((skin, f"w{w} jam-trigger skin @ {js}"))
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    for ax, (tiles, title) in zip(axes.ravel(), panels):
        iis, cmax = iis_for(tiles, title)
        draw(ax, cmax, iis, title)
    fig.suptitle("Audit 2026-11-02 -- recorded IIS witnesses in offset (t) space (corrected)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(A.FIGURES / "audit_witness_halfplanes.png", dpi=130, bbox_inches="tight")
    print("wrote figures/audit_witness_halfplanes.png")


if __name__ == "__main__":
    main()
