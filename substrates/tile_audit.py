#!/usr/bin/env python3
"""
Are the three cyclotomic substrates genuine rhombus tilings?

Everything so far has treated them as graphs. A phason flip is not a graph
operation, it is a *tile* operation: a local rearrangement of rhombi that leaves
the tiling valid. Before any recovery dynamics can be built, the face structure
has to exist and be clean.

This traces the planar embedding, enumerates bounded faces, and reports the tile
and vertex vocabulary. The gate is simple: every bounded face should be a
4-cycle, and the distinct rhombus shapes should be the small finite set the
N-fold construction predicts.
"""

import argparse
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_cyclotomic import generate, build_edges

FAMILIES = ((8, "silver"), (10, "golden"), (12, "platinum"))


def rotation_system(n, edges, par):
    """Neighbours of each vertex in counter-clockwise angular order."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for v in range(n):
        d = par[adj[v]] - par[v]
        order = np.argsort(np.arctan2(d[:, 1], d[:, 0]))
        adj[v] = [adj[v][k] for k in order]
    return adj


def faces(n, edges, par):
    """Trace faces of the planar embedding as cycles of vertex indices.

    For a directed edge u->v the successor is v->w, where w is the neighbour of
    v immediately clockwise from u. This walks every bounded face once; the
    outer boundary comes out as one huge face and is discarded by the caller.
    """
    adj = rotation_system(n, edges, par)
    pos = [{u: k for k, u in enumerate(adj[v])} for v in range(n)]
    seen = set()
    out = []
    for u, v in edges:
        for a, b in ((u, v), (v, u)):
            if (a, b) in seen:
                continue
            cyc, x, y = [], a, b
            while (x, y) not in seen:
                seen.add((x, y))
                cyc.append(y)
                nb = adj[y]
                x, y = y, nb[(pos[y][x] - 1) % len(nb)]
            out.append(cyc)
    return out


def shape_key(cyc, par):
    """Canonical descriptor of a face: sorted edge lengths and interior angles."""
    p = par[cyc]
    e = np.roll(p, -1, axis=0) - p
    L = np.linalg.norm(e, axis=1)
    ang = []
    for k in range(len(cyc)):
        a, b = -e[k - 1], e[k]
        c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        ang.append(np.degrees(np.arccos(np.clip(c, -1, 1))))
    return (tuple(np.round(np.sort(L), 4)), tuple(np.round(np.sort(ang), 1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=10)
    args = ap.parse_args()

    for N, name in FAMILIES:
        lifts, par, perp = generate(N, args.extent)
        E = build_edges(lifts)
        n = len(par)
        F = faces(n, E, par)
        sizes = Counter(len(c) for c in F)
        outer = max(sizes)
        bounded = [c for c in F if len(c) != outer]

        print(f"\n{'='*66}\n{N}-fold ({name}) — {n} vertices, {len(E)} edges\n{'='*66}")
        print(f"faces traced      : {len(F)}  (outer boundary = {outer}-cycle, dropped)")
        bs = Counter(len(c) for c in bounded)
        print(f"bounded face sizes: {dict(sorted(bs.items()))}")
        quad = bs.get(4, 0)
        print(f"quadrilaterals    : {quad}/{len(bounded)} = {quad/max(len(bounded),1):.4%}")

        # Euler check: V - E + F = 2 for a connected planar graph (F counts outer).
        print(f"Euler V-E+F       : {n - len(E) + len(F)}   (2 if the embedding is sound)")

        shapes = Counter(shape_key(c, par) for c in bounded if len(c) == 4)
        print(f"distinct rhombi   : {len(shapes)}")
        tot = sum(shapes.values())
        for (L, A), cnt in sorted(shapes.items(), key=lambda kv: -kv[1]):
            print(f"    angles {A[0]:5.1f}/{A[-1]:5.1f}   side {L[0]:.4f}   "
                  f"{cnt:6d}  {cnt/tot:6.2%}")

        deg = Counter()
        for u, v in E:
            deg[u] += 1
            deg[v] += 1
        print(f"degree spectrum   : {dict(sorted(Counter(deg.values()).items()))}")


if __name__ == "__main__":
    main()
