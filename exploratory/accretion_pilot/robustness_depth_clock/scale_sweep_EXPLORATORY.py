#!/usr/bin/env python3
"""EXPLORATORY (post hoc): RC failed (disc 0.8: no effect; 1.25: weaker). How does rho(depth, T) depend on the disc radius?
Sweep disc radius r (neighbourhood 2r) on the first 4 original decapod worlds."""
import os, json
from multiprocessing import Pool
import numpy as np
import robustness_depth_clock as RB
D = RB.D
seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
ok0 = lambda s: all(r["status"] == "ok" and not r["guesses"] for r in R if r["seed"] == s)
dec = [x for x in seeds if x["kind"] == "DECAPOD" and ok0(x["seed"])][:4]
ring = lambda x: [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
RADII = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0]
if __name__ == "__main__":
    tasks = [(f"r{r}", x["seed"], ring(x), D.SEED0 + 100 * x["seed"], r, 2 * r) for r in RADII for x in dec]
    with Pool(4, maxtasksperchild=2) as p:
        out = p.map(RB.analyse, tasks)
    lines = ["EXPLORATORY: rho(depth, T) against disc radius (neighbourhood = 2 x disc), 4 decapod worlds"]
    for r in RADII:
        v = [o["rho_T"] for o in out if o["test"] == f"r{r}"]
        lines.append(f"  disc {r:>4} edges: mean rho_T {np.mean(v):+.3f}  ({[round(x, 3) for x in v]})")
    print("\n".join(lines))
    open(os.path.join(RB.RES, "scale_sweep_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
