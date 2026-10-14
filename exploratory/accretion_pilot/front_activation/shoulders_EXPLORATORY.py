#!/usr/bin/env python3
"""EXPLORATORY check of Argon's 'keystone' idea (Katie relayed, 2026-10-14): is the two-sided zip decided right at the
choice tile's two shoulders? For every distinct situation of front_activation.py, grow both options 5 slices (same
streams) and record, for each slice, whether new tiles appear on the LEFT and/or RIGHT of the choice tile (signed arc
along the front, as in zip_EXPLORATORY.py; a side counts if a new tile's centre is >= 0.3 edges of arc that way).
Question: does 'two-sided at slice 1' (or by slice 3) already predict the two-sided burst?
Writes results/shoulders_EXPLORATORY.txt."""
import os, cmath, random, collections
from multiprocessing import Pool
import numpy as np
import front_activation as FA
SN, L, S = FA.SN, FA.L, FA.S
SLICES, SIDE = 5, 0.3


def sides(job):
    key, base, cs, c0 = job
    stream = FA.SEED0 * 1000 + int(key, 16) % (2 ** 31)
    rad = float(np.mean([abs(FA.cen(t) - c0) for t in base]))
    out = []
    for c in cs:
        zc = FA.cen(c)
        Q = L.Patch(list(base)); Q.add(c); rng = random.Random(stream); rows = []
        for s in range(1, SLICES + 1):
            n0 = len(Q.tris); st, n, kind = SN.patient(Q, rng)
            if st == "JAM":
                break
            arcs = [cmath.phase((FA.cen(t) - c0) / (zc - c0)) * rad / S for t in Q.tris[n0:]]
            rows.append(dict(kind=kind, n=n, left=sum(a <= -SIDE for a in arcs), right=sum(a >= SIDE for a in arcs)))
        out.append(rows)
    return key, out


def main():
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(FA.world, range(FA.N_WORLDS))
    jobs = {}; pieces = {}
    for w in W:
        for c in w["choices"]:
            if c["key"] not in jobs:
                jobs[c["key"]] = (c["key"], c["base"], c["cs"], FA.centres()[w["world"]]); pieces[c["key"]] = c["pieces"]
    with Pool(4, maxtasksperchild=1) as p:
        R = dict(p.map(sides, list(jobs.values())))
    lines = [f"EXPLORATORY shoulders: {len(R)} distinct situations; per slice: tiles placed (left/right of the choice tile)"]
    two = {"sm": collections.Counter(), "lg": collections.Counter()}
    for key, sib in R.items():
        i = 0 if pieces[key][0] < pieces[key][1] else 1
        txt = []
        for nm, rows in (("sm", sib[i]), ("lg", sib[1 - i])):
            for k in (1, 3):
                ok = any(r["left"] for r in rows[:k]) and any(r["right"] for r in rows[:k])
                two[nm][k] += ok
            txt.append(" ".join(f"{r['n']}({r['left']}/{r['right']}){'g' if r['kind'] == 'guess' else ''}" for r in rows))
        lines.append(f"  piece {min(pieces[key]):.3f}  smaller: {txt[0]}   |   larger: {txt[1]}")
    n = len(R)
    for nm, lab in (("sm", "smaller piece"), ("lg", "larger piece")):
        lines.append(f"  {lab}: new tiles on both sides by slice 1 in {two[nm][1]}/{n}; by slice 3 in {two[nm][3]}/{n}")
    print("\n".join(lines))
    open(os.path.join(FA.RES, "shoulders_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
