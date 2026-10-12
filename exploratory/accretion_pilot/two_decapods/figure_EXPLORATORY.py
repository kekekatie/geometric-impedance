#!/usr/bin/env python3
"""EXPLORATORY picture: one TWO world (two decapod centres) at the moment it jams, beside one CTRL world (a decapod and a
piece of its own world) after it rejoined. Tiles coloured by which seed they grew from. Writes figures/two_centres.png."""
import os, collections, cmath
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import two_decapods as T
D, L, S, SC = T.D, T.L, T.S, T.SC
BG, INK, MUTED = "#07080d", "#ece8dc", "#8f8b80"
COLA, COLB, EDGE = "#f2b84b", "#5b8fe0", "#1d1f29"


def grow_keep(seed_tiles, centres, rounds=400):
    P = L.Patch(list(seed_tiles)); jam = None
    walled = lambda e: any(abs((e[0] + e[1]) / 2 - c) <= D.APO + 1e-6 for c in centres)
    for _ in range(rounds):
        forced = {}
        for e in P.frontier():
            if walled(e):
                continue
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = e; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam is not None:
            break
        placed = [t for t in forced.values() if P.legal(t)]
        for t in placed:
            P.add(t)
        if not placed:
            break
    return P, jam


def labels(P, a_keys):
    adj = collections.defaultdict(list)
    for ek, ts in P.edges.items():
        if len(ts) == 2:
            k0, k1 = D.dkey(ts[0]), D.dkey(ts[1]); adj[k0].append(k1); adj[k1].append(k0)
    seen = set(a_keys); stack = list(a_keys)
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return seen


def panel(ax, P, a_keys, centres, jam, title, col_other):
    A = labels(P, a_keys)
    poly = [[(z.real / S, z.imag / S) for z in t[1:]] for t in P.tris]
    fc = [COLA if D.dkey(t) in A else col_other for t in P.tris]
    ax.add_collection(PolyCollection(poly, facecolors=fc, edgecolors=EDGE, linewidths=0.3, alpha=0.9))
    for c in centres:
        ax.plot([c.real / S], [c.imag / S], "o", color=INK, ms=5)
    if jam is not None:
        m = (jam[0] + jam[1]) / 2
        ax.plot([m.real / S], [m.imag / S], "*", color="#ff4d4d", ms=22, markeredgecolor="white")
    xs = [p[0] for q in poly for p in q]; ys = [p[1] for q in poly for p in q]
    ax.set_xlim(min(xs) - 1, max(xs) + 1); ax.set_ylim(min(ys) - 1, max(ys) + 1); ax.set_aspect("equal")
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(title, color=INK, fontsize=12)


if __name__ == "__main__":
    s, n, j = 3, 5, 0
    A = T.ring_of(s); v = n * (T.eps(j) + T.eps(j + 1))
    B = T.shift(T.ring_of(T.SEEDS[(T.SEEDS.index(s) + 1) % 8]), v)
    P2, jam = grow_keep(A + B, [0j, v])
    Pw, rnd, rounds, g, st = SC.grow(A, 3000, D.SEED0 + 100 * s)
    piece = [t for t in Pw.tris if abs(SC.cen(t) - v) <= T.PIECE_R * S]
    P1, jam1 = grow_keep(A + piece, [0j], rounds=16)
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.4), facecolor=BG)
    panel(axes[0], P2, {D.dkey(t) for t in A}, [0j, v], jam, "two centres: gold grew from one decapod, blue from the other.\nThey jam at the seam (red star) before they can join.", COLB)
    panel(axes[1], P1, {D.dkey(t) for t in A}, [0j], jam1, "one centre and a piece of its own world:\nthey meet and join seamlessly (all gold once joined)", COLB)
    fig.suptitle("can two centres of the universe coexist?", color=INK, fontsize=15, family="serif", style="italic")
    os.makedirs(os.path.join(T.HERE, "figures"), exist_ok=True)
    plt.savefig(os.path.join(T.HERE, "figures", "two_centres.png"), dpi=110, facecolor=BG, bbox_inches="tight")
    print("jam at", None if jam is None else (jam[0] + jam[1]) / 2 / S, "tiles", len(P2.tris), "| ctrl jam", jam1, "tiles", len(P1.tris))
