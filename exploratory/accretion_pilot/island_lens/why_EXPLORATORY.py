#!/usr/bin/env python3
"""EXPLORATORY (post hoc): why are the delays so large and so uniform? Compare the ORDER of guesses (where the growth
had to wait for a decision) in CONTROL, QUIET run 2, QUIET run 0 and FULL run 0, and how arrival time relates to
distance from the origin in CONTROL."""
import sys, os, cmath, math, collections
from multiprocessing import Pool
import numpy as np
import island_lens as IL
L, S = IL.L, IL.S


def guess_log(arm, k):
    """re-run grow() while recording each guess (round, position) via a wrapped Patch.candidates-free approach:
    identify guesses as rounds whose only new tile was not forced -- use the returned rnd: a guess round places exactly
    one tile and follows a round with no forced moves; we recompute from the history instead."""
    h = IL.grow(arm, k)
    per = collections.defaultdict(list)
    for q, r in h["rnd"].items():
        per[r].append(h["geo"][q])
    sizes = [len(per[r]) for r in range(1, h["rounds"] + 1)]
    return arm, k, h["rounds"], sizes, {r: [complex(IL.cen(t)) / S for t in per[r]] for r in per}


if __name__ == "__main__":
    with Pool(4) as p:
        res = p.starmap(guess_log, [("CONTROL", 0), ("QUIET", 2), ("QUIET", 0), ("FULL", 0)])
    out = ["EXPLORATORY (post hoc): what the arrival times look like"]
    for arm, k, rounds, sizes, pos in res:
        s = np.array(sizes)
        big = sorted(range(len(s)), key=lambda i: -s[i])[:5]
        out.append(f"{arm} run {k}: {rounds} rounds; tiles per round: median {np.median(s):.0f}, max {s.max()}, "
                   f"rounds with 0 tiles {int((s == 0).sum())}; share of all tiles laid in the busiest 10% of rounds "
                   f"{np.sort(s)[::-1][:max(1, len(s) // 10)].sum() / s.sum():.2f}")
        # arrival time vs distance from origin
        rs = [(abs(z), r) for r, zs in pos.items() for z in zs if r > 0]
        d = np.array([a for a, _ in rs]); t = np.array([b for _, b in rs])
        rank = lambda x: np.argsort(np.argsort(x))
        out.append(f"    Spearman correlation of arrival round with distance from origin: {np.corrcoef(rank(d), rank(t))[0, 1]:.2f}")
        # by angle sector: when does each 45-degree sector reach radius 10-12 edges?
        sec = collections.defaultdict(list)
        for r, zs in pos.items():
            for z in zs:
                if 10 <= abs(z) <= 12:
                    sec[int(((cmath.phase(z) % (2 * math.pi)) / (math.pi / 4)))].append(r)
        out.append("    median arrival round at radius 10-12 edges, by 45-degree sector: "
                   + ", ".join(f"{i * 45}deg {int(np.median(sec[i]))}" for i in range(8) if sec[i]))
    print("\n".join(out))
    open(os.path.join(IL.RES, "why_EXPLORATORY.txt"), "w").write("\n".join(out) + "\n")
