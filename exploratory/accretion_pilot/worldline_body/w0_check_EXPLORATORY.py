#!/usr/bin/env python3
"""EXPLORATORY (post hoc): why W0 failed. For every FULL body, where are the laid tiles that are NOT in CONTROL's 3,500-tile
tiling? (If they all lie beyond CONTROL's reach, they are continuations CONTROL never grew, not contradictions.)"""
import os, json
from multiprocessing import Pool
import worldline_body as W
D, L, S = W.D, W.L, W.S


def task(args):
    s, ring = args
    c = W.grow(ring, W.N_CTRL); rk = {D.dkey(t) for t in ring}
    cmax = max(abs(D.cen(t)) for t in c["geo"].values()) / S
    out = []
    for bi, th in enumerate(W.THETAS):
        stripe = [t for q, t in c["geo"].items() if q not in rk and W.in_stripe(D.cen(t), th)]
        h = W.grow(ring, W.N_ADD, prelaid=stripe)
        extra = [abs(D.cen(t)) / S for q, t in h["geo"].items() if q not in c["rnd"]]
        # conflicts: a non-control tile overlapping (sharing its position with) a control tile of a different decoration
        cpos = {L.canon(t): q for q, t in c["geo"].items()}
        conflicts = sum(1 for q, t in h["geo"].items() if q not in c["rnd"] and L.canon(t) in cpos)
        out.append((s, bi, round(cmax, 2), len(extra), round(min(extra), 2) if extra else None, conflicts))
    return out


if __name__ == "__main__":
    with Pool(4) as p:
        res = [x for r in p.map(task, W.pick_seeds()) for x in r]
    lines = ["EXPLORATORY: FULL tiles not in CONTROL's 3,500-tile tiling",
             "  (seed, body, CONTROL max radius, n not-in-control, their min radius, position conflicts with CONTROL)"]
    lines += [f"  {x}" for x in res]
    lines.append(f"  smallest radius of any not-in-control tile: {min(x[4] for x in res if x[4] is not None)} edges "
                 f"(sample points lie within 7.3 edges); total position conflicts: {sum(x[5] for x in res)}")
    print("\n".join(lines))
    open(os.path.join(W.RES, "w0_check_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
