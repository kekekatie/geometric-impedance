#!/usr/bin/env python3
"""EXPLORATORY picture (after the registered run): one LOCAL carry-forward world, and the GLOBAL world from the same
seed. Least-bad tiles in red, defect vertices as white dots, frontier edges in gold, so we can see whether defects travel
with the outer front or sit in pockets the world grew around. Writes figures/carry_forward.png and prints, for each world,
how many frontier edges belong to the outer boundary vs inner pockets."""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
import carry_forward as CF
L, D, S = CF.L, CF.D, CF.S
BG, INK, GOLD, RED, OLD, DOT = "#07080d", "#ece8dc", "#f2b84b", "#ff5a4d", "#2b2f40", "#ffffff"
WORLD = int(os.environ.get("WORLD", "0"))


def loops(P):
    """split frontier edges into connected loops; the longest is the outer boundary."""
    fr = P.frontier(); adj = {}
    for e in fr:
        a, b = L.key(e[0]), L.key(e[1]); adj.setdefault(a, []).append((b, e)); adj.setdefault(b, []).append((a, e))
    seen = set(); comps = []
    for v in adj:
        if v in seen:
            continue
        comp = []; st = [v]; seen.add(v)
        while st:
            u = st.pop()
            for w, e in adj[u]:
                comp.append(e)
                if w not in seen:
                    seen.add(w); st.append(w)
        comps.append(comp)
    return sorted(comps, key=len, reverse=True)


fig, axes = plt.subplots(1, 2, figsize=(15, 7.6), facecolor=BG)
for ax, mode in zip(axes, ("LOCAL", "GLOBAL")):
    P, bad, dk, n0 = CF.run((WORLD, mode), keep=True)
    comps = loops(P)
    outer = comps[0] if comps else []
    okeys = {L.key(z) for e in outer for z in e[:2]}
    dpts = [complex(*v) for v in dk]
    on_outer = sum(1 for v in dk if v in okeys)
    print(f"{mode}: tiles {len(P.tris) - n0}, least-bad {len(bad)}, defects {len(dk)} (on the outer boundary {on_outer}, elsewhere {len(dk) - on_outer}); "
          f"frontier loops {len(comps)} (outer {len(outer)} edges; inner pockets {len(comps) - 1}, sizes {[len(c) for c in comps[1:]][:12]})")
    poly = [[(z.real / S, z.imag / S) for z in t[1:]] for t in P.tris]
    fc = [RED if D.dkey(t) in bad else OLD for t in P.tris]
    ax.add_collection(PolyCollection(poly, facecolors=fc, edgecolors="#0d0e14", linewidths=0.15))
    ax.add_collection(LineCollection([[(e[0].real / S, e[0].imag / S), (e[1].real / S, e[1].imag / S)] for c in comps for e in c], colors=GOLD, linewidths=0.6))
    if dpts:
        ax.plot([z.real / S for z in dpts], [z.imag / S for z in dpts], "o", color=DOT, ms=2.5)
    xs = [p[0] for q in poly for p in q]; ys = [p[1] for q in poly for p in q]
    ax.set_xlim(min(xs) - 1, max(xs) + 1); ax.set_ylim(min(ys) - 1, max(ys) + 1); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{mode} scheduler: red = least-bad tiles, white = broken corners,\ngold = frontier (outer edge and any inner pockets)", color=INK, fontsize=11)
fig.suptitle("carrying the disagreement forward: where do the broken corners end up?", color=INK, fontsize=14, family="serif", style="italic")
os.makedirs(os.path.join(CF.HERE, "figures"), exist_ok=True)
plt.savefig(os.path.join(CF.HERE, "figures", "carry_forward.png"), dpi=100, facecolor=BG, bbox_inches="tight")
