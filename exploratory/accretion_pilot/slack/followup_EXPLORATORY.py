#!/usr/bin/env python3
"""EXPLORATORY (post hoc, after the run). Three checks on the registered failures:
(a) S2 measured each option's wiggle room right after its single tile, which barely constrains anything. Here each option
    is grown forced-only for up to 8 slices first (../fragility/ sibling growth), then F_A, F_B, overlap and union compared.
(b) S0's empty patches: which worlds, from which slice, and did that world jam?
(c) In the real growing world: the wiggle room just before choice n+1 divided by that just before choice n (the cost of
    one choice plus the forced growth after it), and the bits it represents."""
import os, sys, json, math, random, collections
from multiprocessing import Pool
import numpy as np
import slack as Sl
T, F_, L, D, S = Sl.T, Sl.F_, Sl.L, Sl.D, Sl.S


def task(k):
    rng = random.Random(T.SEED0 + k); c0 = T.centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris); out = []
    while len(P.tris) - n0 < T.N_ADD:
        st, placed, any_forced = F_.step(P)
        if st == "JAM":
            break
        if placed or any_forced:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) == 2:
            base = list(P.tris); aF = Sl.area(Sl.region(Sl.constraints(base, rank)))
            QA, A, sA, rA = F_.sibling(base, cs[0]); QB, B, sB, rB = F_.sibling(base, cs[1])
            cA = Sl.constraints(list(QA.tris), rank); cB = Sl.constraints(list(QB.tris), rank)
            aA, aB, aAB = Sl.area(Sl.region(cA)), Sl.area(Sl.region(cB)), Sl.area(Sl.region(cA, cB))
            out.append(dict(area=aF, A=aA / aF if aF else None, B=aB / aF if aF else None, overlap=aAB / aF if aF else None,
                            statuses=(sA, sB)))
        P.add(rng.choice(cs))
    return k, out


if __name__ == "__main__":
    W = json.load(open(os.path.join(Sl.RES, "worlds.json")))["ordinary"]
    lines = ["EXPLORATORY follow-up"]
    # (b) empties
    for w in W:
        em = [r for r, a, kind in w["trace"] if a <= 0]
        if em:
            pz = [c for c in w["choices"] if c.get("aA") is not None and min(c["aA"], c["aB"]) == 0]
            lines.append(f"  (b) world {w['world']}: empty from slice {min(em)} ({len(em)} records, last slice recorded "
                         f"{w['trace'][-1][0]}); choices with a zero-area option: "
                         f"{[(c['slice'], 'picked the zero option' if (c['aA'], c['aB'])[c['picked']] == 0 else 'picked the live option') for c in pz]}")
    # (c) cost of each choice in the real world
    ratios = []
    for w in W:
        a = [c["area"] for c in w["choices"]]
        ratios += [a[i + 1] / a[i] for i in range(len(a) - 1) if a[i] > 0 and a[i + 1] > 0]
    cnt = collections.Counter(round(x, 3) for x in ratios)
    lines.append(f"  (c) wiggle room kept per choice in the real world (n={len(ratios)}): {dict(sorted(cnt.items()))}")
    lines.append(f"      median kept {np.median(ratios):.3f}; median bits per choice {np.median([-math.log2(x) for x in ratios]):.3f} "
                 f"(log2 tau = {math.log2((1 + 5 ** 0.5) / 2):.3f})")
    # (a) siblings grown
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(task, range(T.N_WORLDS))
    rows = [r for _, out in R for r in out if r["A"] is not None]
    clean = [r for r in rows if r["A"] > 0 and r["B"] > 0 and r["overlap"] < 0.01 and abs(r["A"] + r["B"] - 1) < 0.01]
    lines.append(f"  (a) siblings grown up to 8 slices: clean cuts (both > 0, overlap < 1%, sum within 1%) {len(clean)}/{len(rows)}")
    lines.append("      (A share, B share, overlap share): " + "; ".join(f"{r['A']:.3f}, {r['B']:.3f}, {r['overlap']:.3f}" for r in rows))
    mins = [min(r["A"], r["B"]) for r in clean]
    lines.append(f"      smaller share among clean cuts: {dict(sorted(collections.Counter(round(x, 3) for x in mins).items()))}")
    print("\n".join(lines))
    open(os.path.join(Sl.RES, "followup_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
