#!/usr/bin/env python3
"""
offset_picture.py -- an explainer figure (no claims, no checks): "two universes, slightly offset".

Katie's picture: light through a window at an angle. A square grid of beads (the hidden lattice);
a slanted beam of light (the strip / acceptance window) at the golden slant; beads inside the beam
cast shadows on a line (the wall). Their spacing is the Fibonacci street. Slide the window a hair
sideways (the hidden direction): a few beads leave the beam, a few enter, and on the wall a few
shadows hop -- a sibling universe, locally identical, different in scattered spots.
Writes figures/offset_picture.png.
"""
import os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d9d8d3"
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
TAU = (1 + 5 ** 0.5) / 2
th = math.atan(1 / TAU)
ePar, ePerp = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
W = math.cos(th) + math.sin(th)                     # beam width = shadow of one grid square
C0, SHIFT = -0.62, 0.16
pts = [(m, n) for m in range(-1, 14) for n in range(-1, 10)]
par = lambda p: p[0] * ePar[0] + p[1] * ePar[1]
perp = lambda p: p[0] * ePerp[0] + p[1] * ePerp[1]
inA = {p for p in pts if C0 <= perp(p) < C0 + W and 0 <= par(p) <= 14}
inB = {p for p in pts if C0 + SHIFT <= perp(p) < C0 + SHIFT + W and 0 <= par(p) <= 14}


def street(sel):
    xs = sorted(par(p) for p in sel)
    cut = (math.cos(th) + math.sin(th)) / 2          # between the two gaps: cos(th), sin(th)
    return xs, "".join("L" if (b - a) > cut else "S" for a, b in zip(xs, xs[1:]))


fig, axes = plt.subplots(1, 2, figsize=(13, 6.4), dpi=150)
fig.patch.set_facecolor(SURF)
for ax, (sel, c, title) in zip(axes, [(inA, C0, "The beam through the window"),
                                      (inB, C0 + SHIFT, "The window slid a hair sideways")]):
    ax.set_facecolor(SURF)
    L = 16
    # beam (strip)
    corners = []
    for s, t in ((0, c), (L, c), (L, c + W), (0, c + W)):
        corners.append((s * ePar[0] + t * ePerp[0], s * ePar[1] + t * ePerp[1]))
    ax.fill([x for x, _ in corners], [y for _, y in corners], color="#fdf1c7", zorder=0)
    ax.plot([0, L * ePar[0]], [0, L * ePar[1]], color=INK2, lw=1, zorder=1)          # the wall
    for p in pts:
        lit = p in sel
        col, face = BLUE, BLUE
        if sel is inB and p in inA and p not in inB:
            col, face = ORANGE, SURF
        elif sel is inB and p in inB and p not in inA:
            col, face = GREEN, GREEN
        elif not lit:
            col, face = GRID, GRID
        ax.plot(p[0], p[1], "o", ms=6 if lit or col != GRID else 4, mfc=face, mec=col, mew=1.6, zorder=3)
        if lit:
            s = par(p)
            ax.plot([p[0], s * ePar[0]], [p[1], s * ePar[1]], color=col, lw=0.6, alpha=0.5, zorder=2)
            ax.plot(s * ePar[0], s * ePar[1], "|", ms=9, color=col, mew=2, zorder=4)
    ax.set_xlim(-1.5, 13.5); ax.set_ylim(-1.5, 9.5); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values():
        s_.set_visible(False)
    xs, word = street(sel)
    ax.set_title(title, color=INK, fontsize=11.5, fontweight="bold", loc="left")
    ax.text(0, -0.03, f"shadows on the wall read:  {word}", transform=ax.transAxes,
            color=INK, fontsize=10, family="monospace", va="top")
wa, wb = street(inA)[1], street(inB)[1]
diff = "".join("^" if i < len(wa) and i < len(wb) and wa[i] != wb[i] else " " for i in range(max(len(wa), len(wb))))
axes[1].text(0, -0.075, f"{'':26}{diff}", transform=axes[1].transAxes, color=ORANGE, fontsize=10,
             family="monospace", va="top")
fig.suptitle("Two universes, slightly offset: light through a window at an angle", color=INK,
             fontsize=13.5, fontweight="bold", x=0.01, ha="left", y=0.99)
fig.text(0.01, 0.93, "Beads in regular rows (the hidden grid). Only beads in the sunbeam cast shadows "
         "on the wall (the diagonal line). Their spacing is the Fibonacci street.\nSliding the window "
         "sideways by a hair: orange beads leave the beam, green beads enter - a few shadows hop, the "
         "rest of the wall is unchanged.", color=INK2, fontsize=9, ha="left", va="top")
fig.subplots_adjust(left=0.01, right=0.99, top=0.84, bottom=0.11, wspace=0.04)
os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
fig.savefig(os.path.join(HERE, "figures", "offset_picture.png"), facecolor=SURF)
print("A:", wa); print("B:", wb)
print("wrote figures/offset_picture.png")
