#!/usr/bin/env python3
"""EXPLORATORY (post hoc): M1 counted every frontier edge once per round, so an edge that stays open for many rounds is
counted many times. Here each distinct edge counts once: 'open' if it ever had >= 2 candidates, else 'forced'.
Runs 0, 1, 2 (three distinct histories)."""
import os, numpy as np
from multiprocessing import Pool
import perp_map as M


def task(k):
    tiles, events, guesses, status = M.grow(M.L.seed_patch(0j, 3 * M.S), M.N_M1, M.SEED0 + k, record=True)
    K, pos, conf = M.lift(tiles); dep, areas, lays = M.depths(K)
    ever = {}
    for a, b, n in events:
        e = frozenset((a, b)); ever[e] = max(ever.get(e, 0), n)
    d = lambda e: np.mean([dep[v] for v in e]) if all(v in dep for v in e) else None
    op = [d(e) for e, n in ever.items() if n >= 2 and d(e) is not None]
    fo = [d(e) for e, n in ever.items() if n == 1 and d(e) is not None]
    return k, len(op), float(np.median(op)), len(fo), float(np.median(fo))


if __name__ == "__main__":
    with Pool(3) as p:
        res = p.map(task, [0, 1, 2])
    lines = ["EXPLORATORY: each distinct frontier edge counted once"]
    lines += [f"  run {k}: ever-open edges {no}, median depth {mo:.3f}; always-forced edges {nf}, median depth {mf:.3f}" for k, no, mo, nf, mf in res]
    print("\n".join(lines))
    open(os.path.join(M.RES, "unique_edges_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
