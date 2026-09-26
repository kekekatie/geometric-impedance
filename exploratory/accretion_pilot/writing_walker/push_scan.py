#!/usr/bin/env python3
"""push_scan.py -- EXPLORATORY (after the pre-registered run): is there any push size delta for which
the writing walker leaves a LEGAL wake (no atlas-illegal vertices in the middle of the wake)?
Full journey (t_start=-30 -> t0=30, tile units); middle of wake = |t| <= 25."""
import numpy as np, writing_walker as W
from multiprocessing import Pool
base = W.build(0.0, 0.0); atlas = set(W.star_types(base).values())
def one(d):
    F = W.build(d, 30.0); ty = W.star_types(F)
    ill = [K for K, tp in ty.items() if tp not in atlas]
    mid = [K for K in ill if abs(W.dot(W.EJP, W.par(K))) <= 25 and abs(W.dot(W.EJ, W.par(K))) < 6]
    return d, len(W.crossed_triples(d, 30.0)), len(ill), len(mid)
if __name__ == "__main__":
    ds = [round(x, 2) for x in np.arange(0.01, 1.0, 0.01)]
    with Pool(4) as p: rows = p.map(one, ds)
    out = ["delta  flips  illegal_total  illegal_mid_wake"] + [f"{d:5.2f}  {f:5d}  {a:5d}  {m:5d}" for d, f, a, m in rows]
    open("results/push_scan.txt", "w").write("\n".join(out) + "\n")
    clean = [d for d, f, a, m in rows if m == 0]
    print("\n".join(out[::5])); print("pushes with a CLEAN middle of wake:", clean)
    import json; json.dump(rows, open("results/push_scan.json", "w"))
