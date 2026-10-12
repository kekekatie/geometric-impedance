#!/usr/bin/env python3
"""EXPLORATORY art + explanation (no predictions): TWINS. In the reference Penrose tiling, find two vertices at least
15 edges apart whose surroundings agree out to the largest radius r* (same decorated tiles in the same places), then
show where they first disagree, and where the two sit in the hidden window (their addresses are close but not equal).
Writes figures/twins.png and results/twins_EXPLORATORY.txt."""
import os, sys, math, hashlib, collections
import numpy as np
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "perp_map"))
import perp_map as M
D, L, S = M.D, M.L, M.S
MIN_SEP, STEP, RMAX = 15.0, 0.25, 14.0
BG, INK, MUTED, GOLD, RED, DIM = "#07080d", "#ece8dc", "#8f8b80", "#f2b84b", "#ff5a4d", "#1b1d27"

tiles = list(L.REF)
cen = np.array([sum(t[1:]) / 3 for t in tiles])
tree = cKDTree(np.c_[cen.real, cen.imag])
V = L.corners(tiles)
verts = [complex(*k) for k, l in V.items() if abs(sum(d for _, d, _ in l) - 2 * math.pi) < 1e-6 and abs(complex(*k)) < 0.55]


def disc(z, r):
    return tree.query_ball_point([z.real, z.imag], r * S + 1e-9)


def key(z, r):
    rk = lambda w: (round((w - z).real / S, 3), round((w - z).imag / S, 3))
    items = sorted((tiles[i][0], rk(tiles[i][1]), rk(tiles[i][2]), rk(tiles[i][3])) for i in disc(z, r))
    return hashlib.md5(repr(items).encode()).hexdigest()


def search():
    groups = [verts]; r = 1.0; best = None
    while r <= RMAX:
        new = []
        for g in groups:
            sub = collections.defaultdict(list)
            for z in g:
                sub[key(z, r)].append(z)
            for zs in sub.values():
                if len(zs) >= 2:
                    far = [(abs(a - b), a, b) for i, a in enumerate(zs) for b in zs[i + 1:] if abs(a - b) >= MIN_SEP * S]
                    if far:
                        new.append(zs); best = (r, max(far, key=lambda x: x[0]))
        if not new:
            break
        groups = new; r += STEP
    return best


r_found, (sep, a, b) = search()
r_split = r_found
while key(a, r_split) == key(b, r_split):        # walk outwards until the twins first differ
    r_split += STEP
r_agree = r_split - STEP
assert abs(a) / S + r_split < 46 and abs(b) / S + r_split < 46, "disc reaches the edge of the reference patch"
# the tiles of a's split-disc that b does not have (relative positions), and vice versa
rel = lambda z, i: (tiles[i][0], tuple(sorted(((round((w - z).real / S, 3), round((w - z).imag / S, 3)) for w in tiles[i][1:]))))
sa = {rel(a, i): i for i in disc(a, r_split)}; sb = {rel(b, i): i for i in disc(b, r_split)}
diff_a = [sa[k] for k in sa if k not in sb]; diff_b = [sb[k] for k in sb if k not in sa]
# hidden addresses
K, pos, conf = M.lift(tiles)
ka, kb = K[L.key(a)], K[L.key(b)]
pa, pb = M.perp(ka), M.perp(kb)
lines = [f"EXPLORATORY twins in the reference tiling: separation {sep / S:.1f} edges; identical out to radius {r_agree:.2f} edges; "
         f"first disagreement by radius {r_split:.2f}; tiles that differ: {len(diff_a)} / {len(diff_b)}",
         f"  same layer: {int(ka.sum()) == int(kb.sum())}; hidden-address distance {abs(pa - pb):.4f} (window circumradius 1 or tau)"]
print("\n".join(lines))
os.makedirs(os.path.join(HERE, "results"), exist_ok=True); os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
open(os.path.join(HERE, "results", "twins_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")

fig = plt.figure(figsize=(17, 6.6), facecolor=BG)
axes = [fig.add_axes([0.01, 0.05, 0.31, 0.8]), fig.add_axes([0.34, 0.05, 0.31, 0.8]), fig.add_axes([0.68, 0.08, 0.30, 0.74])]
view = r_split + 1.5
for ax, z, diff, name in ((axes[0], a, diff_a, "twin A"), (axes[1], b, diff_b, "twin B")):
    idx = disc(z, view); same = set(disc(z, r_agree)); dset = set(diff)
    poly = [[((w - z).real / S, (w - z).imag / S) for w in tiles[i][1:]] for i in idx]
    fc = [RED if i in dset else (GOLD if i in same else DIM) for i in idx]
    ax.add_collection(PolyCollection(poly, facecolors=fc, edgecolors="#0d0e14", linewidths=0.4))
    for rr, ls in ((r_agree, "-"), (r_split, ":")):
        th = np.linspace(0, 2 * np.pi, 200); ax.plot(rr * np.cos(th), rr * np.sin(th), color=INK, lw=0.8, ls=ls, alpha=0.7)
    ax.plot([0], [0], "o", color=INK, ms=4)
    ax.set_xlim(-view, view); ax.set_ylim(-view, view); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{name}: identical (gold) out to {r_agree:.2f} edges;\nred = where it first differs from its twin", color=INK, fontsize=11)
ax = axes[2]
lay = int(ka.sum())
pts = [M.perp(k) for k in K.values() if int(k.sum()) == lay]
ax.scatter([p.real for p in pts], [p.imag for p in pts], s=1.5, color="#3a3d4d")
ax.plot([pa.real], [pa.imag], "o", color=GOLD, ms=9, label="twin A's hidden address")
ax.plot([pb.real], [pb.imag], "o", color=RED, ms=7, label="twin B's hidden address")
ax.set_aspect("equal"); ax.axis("off"); ax.legend(loc="lower left", frameon=False, labelcolor=INK, fontsize=9)
ax.set_title(f"the hidden window (one layer): far apart in the world ({sep / S:.0f} edges),\nneighbours in the window (distance {abs(pa - pb):.3f})", color=INK, fontsize=11)
fig.suptitle("twins: the universe lets places be similar anywhere, but zoomed out far enough every place is unique",
             color=INK, fontsize=14, family="serif", style="italic")
plt.savefig(os.path.join(HERE, "figures", "twins.png"), dpi=110, facecolor=BG, bbox_inches="tight")
