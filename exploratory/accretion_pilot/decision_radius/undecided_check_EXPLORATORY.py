#!/usr/bin/env python3
"""EXPLORATORY (post hoc), prompted by Gemini's 'zipper' question. The follow-up context already contained everything laid
up to round `full` (the disc's last tile), INCLUDING same-round sideways neighbours. Suspected artefact: the target's 17
points (out to 0.8 edges) can be covered by tiles whose centroids lie 1.0-1.8 edges away, i.e. OUTSIDE the 1.0-edge
'disc' that defines `full`. If such a covering tile was laid AFTER `full`, it is missing from the context, so the
completion must guess it, and the place looks 'undecided' even though its own disc was settled early.
Check: for each probe, does any target-covering tile lie outside the disc AND get laid after `full`?"""
import os, sys, json, random
import numpy as np
import decision_radius as DR
SC, CC, M, D, L, S = DR.SC, DR.CC, DR.M, DR.D, DR.L, DR.S
W = json.load(open(os.path.join(DR.RES, "worlds.json")))
out = ["EXPLORATORY: are the 'undecided' places an artefact of disc vs target?"]
tot = {"undecided": [0, 0], "decided": [0, 0]}
for w in W:
    s = w["seed"]
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    x = next(v for v in seeds if v["seed"] == s)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    P, rnd, rounds, g, st = SC.grow(ring, SC.N_TILES, D.SEED0 + 100 * s)
    tiles = list(P.tris); tc = np.array([DR.cen(t) for t in tiles]); tr = np.array([rnd[D.dkey(t)] for t in tiles])
    mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    K, pos, conf = M.lift(tiles); dep, areas, lays = M.depths(K)
    cands = sorted(v for v in K if v in dep and 4 * S <= abs(pos[v]) <= 10 * S and np.min(np.abs(mids - pos[v])) >= 4.5 * S)
    random.Random(2050 + s).shuffle(cands)
    for v, row in zip(cands[:DR.NPROBE], w["rows"]):
        c = pos[v]; d = np.abs(tc - c)
        disc_idx = np.where(d <= 1.0 * S)[0]; f = int(tr[disc_idx].max())
        near = [tiles[i] for i in np.where(d <= 2.5 * S)[0]]
        cov = CC.cover_of(near, CC.sample_points(c))
        late_outside = any(abs(DR.cen(t) - c) > 1.0 * S and rnd[D.dkey(t)] > f for t in cov)
        k = "undecided" if row["decision_radius"] == DR.CENSORED else "decided"
        tot[k][0] += late_outside; tot[k][1] += 1
for k, (a, n) in tot.items():
    out.append(f"  {k}: {a}/{n} have a target-covering tile outside the disc that was laid AFTER the disc finished")
print("\n".join(out))
open(os.path.join(DR.RES, "undecided_check_EXPLORATORY.txt"), "w").write("\n".join(out) + "\n")
