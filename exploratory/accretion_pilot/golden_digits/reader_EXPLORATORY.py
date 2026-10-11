#!/usr/bin/env python3
"""EXPLORATORY art (no predictions): "the reader, reading". One golden_digits world (11, five choices) is regrown. Left:
the tiling as it grows, each choice marked. Right: the wiggle room F in the hidden window. At each choice the cutting
line appears, the two alternative presents' pieces light up, the road not taken fades, and the view zooms into the
piece that is kept. Writes figures/reader.gif and figures/reader_frames.png."""
import os, sys, math, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.animation import FuncAnimation, PillowWriter
import golden_digits as GD
Sl, T, F_, L, D, S = GD.Sl, GD.T, GD.F_, GD.L, GD.D, GD.S
WORLD = int(sys.argv[1]) if len(sys.argv) > 1 else 11
BG, INK, MUTED, TILE = "#07080d", "#ece8dc", "#8f8b80", "#2a2c36"
GOLD, RED, BLUE = "#f2b84b", "#e0604a", "#5b8fe0"


def regrow():
    rng = random.Random(GD.SEED0 + WORLD); c0 = GD.centres()[WORLD]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris); r = 0; steps = []
    while len(P.tris) - n0 < GD.N_ADD:
        r += 1
        st, placed, anyf = F_.step(P)
        if st == "JAM":
            break
        if placed or anyf:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        base = list(P.tris); c0m = Sl.constraints(base, rank); pF = Sl.region(c0m)
        t = rng.choice(cs); k = cs.index(t)
        if len(cs) == 2 and Sl.area(pF) > 0:
            pieces = [Sl.region(Sl.constraints(list(F_.sibling(base, c)[0].tris), rank)) for c in cs]
            steps.append(dict(slice=r, F=pF, pieces=pieces, picked=k, tiles=base, at=(e[0] + e[1]) / 2,
                              shares=[Sl.area(p) / Sl.area(pF) for p in pieces]))
        P.add(t)
    return steps, list(P.tris)


def bbox(poly, pad=0.18):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    h = max(max(xs) - min(xs), max(ys) - min(ys)) * (0.5 + pad)
    return cx, cy, h


def main():
    steps, final = regrow()
    tile_poly = lambda ts: [[(z.real / S, z.imag / S) for z in t[1:]] for t in ts]
    frames = []                       # (step index, phase, t in [0,1])
    for i in range(len(steps)):
        frames += [(i, "show", f) for f in np.linspace(0, 1, 6)]
        frames += [(i, "cut", f) for f in np.linspace(0, 1, 8)]
        frames += [(i, "keep", f) for f in np.linspace(0, 1, 6)]
        frames += [(i, "zoom", f) for f in np.linspace(0, 1, 12)]
    frames += [(len(steps) - 1, "end", 1.0)] * 12
    fig = plt.figure(figsize=(13, 6.6), facecolor=BG)
    axL = fig.add_axes([0.02, 0.06, 0.44, 0.84]); axR = fig.add_axes([0.53, 0.06, 0.44, 0.84])
    allxy = [z / S for t in final for z in t[1:]]
    lim = (min(z.real for z in allxy) - 1, max(z.real for z in allxy) + 1, min(z.imag for z in allxy) - 1, max(z.imag for z in allxy) + 1)

    def draw(fr):
        i, phase, f = fr
        st = steps[i]
        axL.clear(); axR.clear()
        for ax in (axL, axR):
            ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
        tiles = st["tiles"] if phase != "end" else final
        axL.add_collection(PolyCollection(tile_poly(tiles), facecolors="#151722", edgecolors=TILE, linewidths=0.3))
        for j, s2 in enumerate(steps[:i + 1]):
            axL.plot([s2["at"].real / S], [s2["at"].imag / S], "o", color=GOLD if j == i else MUTED, ms=7 if j == i else 4)
        axL.set_xlim(lim[0], lim[1]); axL.set_ylim(lim[2], lim[3]); axL.set_aspect("equal")
        axL.set_title(f"the world, slice {st['slice']}" + ("  (grown on)" if phase == "end" else ""), color=MUTED, fontsize=11)
        # window view: zoom from F_i to the kept piece
        a = bbox(st["F"]); kept = st["pieces"][st["picked"]]; b = bbox(kept)
        if phase == "zoom":
            w = 0.5 - 0.5 * math.cos(math.pi * f)
            cx, cy = a[0] + w * (b[0] - a[0]), a[1] + w * (b[1] - a[1]); h = a[2] * (b[2] / a[2]) ** w
        elif phase == "end":
            cx, cy, h = b
        else:
            cx, cy, h = a
        for j in range(i):                               # earlier wiggle rooms, faint
            p = steps[j]["F"]; axR.fill([q[0] for q in p], [q[1] for q in p], color="#ffffff", alpha=0.04, lw=0)
        p = st["F"]
        axR.fill([q[0] for q in p], [q[1] for q in p], color="#2b2e3b", lw=0)
        axR.plot([q[0] for q in p] + [p[0][0]], [q[1] for q in p] + [p[0][1]], color=MUTED, lw=0.8)
        if phase in ("cut", "keep", "zoom", "end"):
            alpha = f if phase == "cut" else 1.0
            for k, (pc, col) in enumerate(zip(st["pieces"], (RED, BLUE))):
                fade = 1.0
                if phase in ("keep", "zoom", "end") and k != st["picked"]:
                    fade = max(0.0, 1 - f) if phase == "keep" else 0.0
                if fade > 0 and pc:
                    axR.fill([q[0] for q in pc], [q[1] for q in pc], color=col, alpha=0.75 * alpha * fade, lw=0)
            if phase in ("keep", "zoom", "end"):
                axR.fill([q[0] for q in kept], [q[1] for q in kept], color=GOLD, alpha=0.85 * (f if phase == "keep" else 1.0), lw=0)
            sh = st["shares"]
            axR.text(0.02, 0.02, f"choice {i + 1}: the two alternative presents take {sh[0]:.3f} and {sh[1]:.3f} of the possibilities",
                     transform=axR.transAxes, color=INK, fontsize=10)
        axR.set_xlim(cx - h, cx + h); axR.set_ylim(cy - h, cy + h); axR.set_aspect("equal")
        axR.set_title("the hidden window: what the world could still be", color=MUTED, fontsize=11)
        fig.suptitle("the reader, reading", color=INK, fontsize=15, family="serif", style="italic")

    out = os.path.join(GD.HERE, "figures"); os.makedirs(out, exist_ok=True)
    anim = FuncAnimation(fig, lambda n: draw(frames[n]), frames=len(frames))
    anim.save(os.path.join(out, "reader.gif"), writer=PillowWriter(fps=10), dpi=72)
    # a still strip: each choice at its "keep" moment
    fig2, axes = plt.subplots(1, len(steps), figsize=(3.6 * len(steps), 3.8), facecolor=BG)
    for ax, st, i in zip(np.atleast_1d(axes), steps, range(len(steps))):
        ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        p = st["F"]; ax.fill([q[0] for q in p], [q[1] for q in p], color="#2b2e3b", lw=0)
        for k, (pc, col) in enumerate(zip(st["pieces"], (RED, BLUE))):
            ax.fill([q[0] for q in pc], [q[1] for q in pc], color=GOLD if k == st["picked"] else col, alpha=0.85 if k == st["picked"] else 0.35, lw=0)
        cx, cy, h = bbox(p); ax.set_xlim(cx - h, cx + h); ax.set_ylim(cy - h, cy + h); ax.set_aspect("equal")
        ax.set_title(f"choice {i + 1}: kept {st['shares'][st['picked']]:.3f}", color=INK, fontsize=10)
    fig2.suptitle("each choice cuts what the world could still be; gold is the piece the world kept", color=MUTED, fontsize=11)
    fig2.savefig(os.path.join(out, "reader_frames.png"), dpi=110, facecolor=BG, bbox_inches="tight")
    print("choices:", [(s["slice"], [round(x, 3) for x in s["shares"]], s["picked"]) for s in steps])


if __name__ == "__main__":
    main()
