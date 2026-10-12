#!/usr/bin/env python3
"""EXPLORATORY follow-up (after the registered run; no predictions): does the speed of now track how PINNED a world is?
Replays the 24 main worlds of speed_of_now.py (same seeds, so the same worlds) recording, for every slice, the tiles
placed, the frontier length and the wiggle room F. F only changes at choices, so each world's history splits into
stretches of constant F. For each stretch: the share of the frontier laid per forced slice. Then Spearman between that
share and F's area, across stretches, and within each world. Also: the same for the sibling bursts (matched size and
moment, so no growth-size confound). Writes results/pinned_speed_EXPLORATORY.txt."""
import os, json, math, random, collections
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr
import speed_of_now as SN
Sl, L, D, S = SN.Sl, SN.L, SN.D, SN.S


def replay(k):
    rng = random.Random(SN.SEED0 + k)
    P = L.Patch(L.seed_patch(SN.centres()[k], 3 * S)); n0 = len(P.tris); r = 0
    rank = Sl.rank_of(P.tris); rows = []; aF = Sl.area(Sl.region(Sl.constraints(P.tris, rank))); after_choice = False
    while len(P.tris) - n0 < SN.N_ADD:
        r += 1
        fr = P.frontier(); forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= SN.N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            if after_choice:
                aF = Sl.area(Sl.region(Sl.constraints(P.tris, rank))); after_choice = False
            rows.append(dict(slice=r, kind="forced", placed=placed, frontier=len(fr), area=aF, n=len(P.tris)))
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3]))
        P.add(rng.choice(cs)); after_choice = True
        rows.append(dict(slice=r, kind="choice", placed=1, frontier=len(fr), area=aF, n=len(P.tris)))
    return rows


def stretches(rows):
    out = []; cur = []
    for x in rows:
        if x["kind"] == "choice":
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(x)
    if cur:
        out.append(cur)
    res = []
    for st in out:
        st = st[1:]                          # skip the slice right after a choice (F still settling)
        if len(st) >= 3:
            res.append(dict(area=st[0]["area"], share=float(np.mean([x["placed"] / x["frontier"] for x in st])),
                            n=st[0]["n"], slices=len(st)))
    return res


def main():
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(replay, range(SN.N_WORLDS))
    ST = [(k, s) for k, rows in enumerate(R) for s in stretches(rows)]
    a = [s["area"] for _, s in ST]; sh = [s["share"] for _, s in ST]; n = [s["n"] for _, s in ST]
    lines = [f"EXPLORATORY pinned speed: {len(ST)} stretches of constant F in {SN.N_WORLDS} worlds",
             f"  across stretches: Spearman(F area, share of frontier laid per slice) = {spearmanr(a, sh).correlation:+.3f}; "
             f"Spearman(patch size, share) = {spearmanr(n, sh).correlation:+.3f}; Spearman(F area, patch size) = {spearmanr(a, n).correlation:+.3f}"]
    # within world: does the share rise each time F shrinks? (consecutive stretches)
    up = down = same = 0
    for k in range(SN.N_WORLDS):
        ss = [s for kk, s in ST if kk == k]
        for x, y in zip(ss, ss[1:]):
            if y["area"] < x["area"] * (1 - 1e-6):
                if y["share"] > x["share"]:
                    up += 1
                else:
                    down += 1
            else:
                same += 1
    lines.append(f"  consecutive stretches where F shrank: share went up {up}, down {down}; (F unchanged: {same})")
    # siblings (matched size and moment)
    W = json.load(open(os.path.join(SN.RES, "worlds.json")))
    live = [c for w in W for c in w["choices"] if "A" in c and c["A"]["piece"] > 0 and c["B"]["piece"] > 0]
    seen = {}
    for c in live:
        seen.setdefault((tuple(c["A"]["per"]), tuple(c["B"]["per"])), c)
    pairs = []
    for c in seen.values():
        sm, lg = sorted((c["A"], c["B"]), key=lambda s: s["piece"])
        m = min(sm["burst_slices"], lg["burst_slices"])
        if m >= 3:
            pairs.append((np.mean(sm["per"][1:m + 1]), np.mean(lg["per"][1:m + 1])))
    lines.append(f"  sibling bursts, same slices compared ({len(pairs)} distinct choices): smaller piece faster in "
                 f"{sum(x > y for x, y in pairs)}, slower in {sum(x < y for x, y in pairs)}; mean tiles per slice {np.mean([x for x, _ in pairs]):.1f} "
                 f"vs {np.mean([y for _, y in pairs]):.1f}")
    print("\n".join(lines))
    open(os.path.join(SN.RES, "pinned_speed_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
    json.dump(R, open(os.path.join(SN.RES, "replay_EXPLORATORY.json"), "w"))


if __name__ == "__main__":
    main()
