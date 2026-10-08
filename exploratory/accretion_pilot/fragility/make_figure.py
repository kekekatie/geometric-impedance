#!/usr/bin/env python3
"""EXPLORATORY picture (no predictions): one choice, both siblings. The world is regrown exactly as in fragility.py up
to its N-th choice; both siblings are grown 8 rounds ahead. Grey: the world at the moment of choice. Red: tiles only in
sibling A. Blue: tiles only in sibling B. Purple dashed: the local front line. Writes figures/one_choice.png."""
import os, sys, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import fragility as F
L, D, S = F.L, F.D, F.S
WORLD, NTH = int(sys.argv[1]) if len(sys.argv) > 1 else 0, int(sys.argv[2]) if len(sys.argv) > 2 else 2


def regrow():
    rng = random.Random(F.SEED0 + WORLD)
    P = L.Patch(L.seed_patch(0j, 3 * S)); seen = 0
    while True:
        fr = P.frontier(); forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        e = fr[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
        if seen == NTH:
            return P, e, cs
        seen += 1
        P.add(rng.choice(cs))


P, e, cs = regrow()
base = list(P.tris); line = F.front_line(P, e)
(QA, A, sA, rA), (QB, B, sB, rB) = F.sibling(base, cs[0]), F.sibling(base, cs[1])
kA = {D.dkey(t) for t in A}; kB = {D.dkey(t) for t in B}
SURF, INK, MUTED, TILE = "#fcfcfb", "#0b0b0b", "#52514e", "#bdbcb5"
RED, BLUE, SAME = "#d6402b", "#2a78d6", "#e9e8e2"
fig, axes = plt.subplots(1, 2, figsize=(16, 8.4), facecolor=SURF)
for ax, X, other, col, name in ((axes[0], A, kB, RED, "Sibling A"), (axes[1], B, kA, BLUE, "Sibling B")):
    poly = lambda ts: [[(z.real / S, z.imag / S) for z in t[1:]] for t in ts]
    ax.add_collection(PolyCollection(poly(base), facecolors="#00000000", edgecolors=TILE, linewidths=0.3))
    same = [t for t in X if D.dkey(t) in other]; diff = [t for t in X if D.dkey(t) not in other]
    ax.add_collection(PolyCollection(poly(same), facecolors=SAME, edgecolors=TILE, linewidths=0.3))
    ax.add_collection(PolyCollection(poly(diff), facecolors=col + "cc", edgecolors="white", linewidths=0.3))
    m, u = line
    ts = np.linspace(-14, 14, 2)
    ax.plot([(m / S + t * u).real for t in ts], [(m / S + t * u).imag for t in ts], ls="--", color="#7a4fc9", lw=1.2)
    ax.plot([(e[0] + e[1]).real / 2 / S], [(e[0] + e[1]).imag / 2 / S], "o", color=INK, ms=6)
    ax.set_xlim(-13, 13); ax.set_ylim(-13, 13); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{name}: {len(diff)} tiles that the other sibling lays differently", color=INK, fontsize=13, loc="left")
fig.suptitle(f"One two-way choice (black dot), both alternative presents grown 8 slices ahead. Light: the same in both. "
             f"Colour: different.\nPurple dashed: the growing front's direction at the moment of choice.",
             color=MUTED, fontsize=11, x=0.01, ha="left")
os.makedirs(os.path.join(F.HERE, "figures"), exist_ok=True)
plt.savefig(os.path.join(F.HERE, "figures", "one_choice.png"), dpi=120, facecolor=SURF, bbox_inches="tight")
print("ok", len(A), len(B), sA, sB)
