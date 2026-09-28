#!/usr/bin/env python3
"""EXPLORATORY (post hoc): why did the free paths go the 'wrong' way? Compare the CLOCK RATE h (happenings per round at
the now) near each body with far from it, over the rounds used (r1 .. r1+16), for CONTROL, QUIET and FULL.
Lateral distance bands at the front: 0-1.5, 1.5-3, 3-6 edges."""
import os, json, math
from multiprocessing import Pool
import numpy as np
import free_fall as F
W, D = F.W, F.D


def task(args):
    s, ring, bi, th = args
    ctrl = W.grow(ring, W.N_CTRL); rk = {D.dkey(t) for t in ring}
    stripe = [t for q, t in ctrl["geo"].items() if q not in rk and W.in_stripe(D.cen(t), th)]
    worlds = {"CONTROL": (W.grow(ring, W.N_ADD), set()),
              "QUIET": (W.grow(ring, W.N_ADD, th=th, quiet=True, rng_seed=W.SEED0 + 10 * s + bi), set()),
              "FULL": (W.grow(ring, W.N_ADD, prelaid=stripe), {D.dkey(t) for t in stripe})}
    Rc, _ = F.field(worlds["CONTROL"][0], th, set())
    r1 = next(r for r in range(Rc.shape[1]) if Rc[F.NB // 2, r] >= 5.0)
    out = {}
    for arm, (h, ex) in worlds.items():
        R, H = F.field(h, th, ex)
        bands = {}
        for r in range(r1, min(r1 + 16, R.shape[1])):
            lat = np.abs(R[:, r] * F.PHIS)
            for name, lo, hi in (("0-1.5", 0, 1.5), ("1.5-3", 1.5, 3), ("3-6", 3, 6)):
                sel = (lat >= lo) & (lat < hi)
                bands.setdefault(name, []).extend(H[sel, r].tolist())
        out[arm] = {k: float(np.mean(v)) for k, v in bands.items()}
    return out


if __name__ == "__main__":
    tasks = [(s, ring, bi, th) for s, ring in W.pick_seeds() for bi, th in enumerate(W.THETAS)]
    with Pool(4, maxtasksperchild=1) as p:
        res = p.map(task, tasks)
    lines = ["EXPLORATORY: mean clock rate h (happenings per round within 1.5 edges of the now) by lateral distance from",
             "the body's line, rounds r1..r1+16, averaged over the 18 bodies"]
    for arm in ("CONTROL", "QUIET", "FULL"):
        lines.append(f"  {arm:<8} " + ", ".join(f"{b}: {np.mean([r[arm][b] for r in res]):.3f}" for b in ("0-1.5", "1.5-3", "3-6")))
    lines.append("  per body, FULL minus CONTROL at 0-1.5 edges: " + str([round(r['FULL']['0-1.5'] - r['CONTROL']['0-1.5'], 2) for r in res]))
    lines.append("  per body, QUIET minus CONTROL at 0-1.5 edges: " + str([round(r['QUIET']['0-1.5'] - r['CONTROL']['0-1.5'], 2) for r in res]))
    print("\n".join(lines))
    open(os.path.join(F.RES, "clock_profile_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
