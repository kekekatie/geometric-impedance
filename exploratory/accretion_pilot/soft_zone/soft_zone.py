#!/usr/bin/env python3
"""
soft_zone.py -- how wide is the now at a growing front? (PREREGISTRATION.md, frozen before this file.)

Growth by a RING OF GROMITS: each round, every frontier edge with exactly one legal candidate (full Penrose
matching rules via ../laying_the_tiling) is filled simultaneously; if nothing is forced, one guess at the
innermost edge. Then holes are poked at depth bins behind the front and re-laid (8 attempts, forced-first with
random guesses, placements confined to the hole). A hole is SOFT if some attempt yields a different complete
legal refill. Freedom F(bin) = fraction of soft holes. Happening density = tiles per round locally.
Incremental: each run appends to results/holes.jsonl; `--summary` evaluates predictions.
"""
from __future__ import annotations
import os, sys, math, json, random, collections, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "laying_the_tiling"))
import laying_the_tiling as L

S = L.SCALE_LEN


def vertex_ok_fixed(s, k, extra):
    """Corrected version of laying_the_tiling.Patch.vertex_ok. The original wraps each gap between
    consecutive corners into (-pi, pi], so a gap WIDER than pi (common around holes) was misread as an
    overlap and a legal partial star was rejected. Here gaps are measured linearly along the sorted start
    angles, with one explicit wrap-around gap; arcs and complete stars are then checked exactly as before."""
    lst = sorted(s.V[k] + extra); n = len(lst)
    tot = sum(d for _, d, _ in lst)
    if tot > 2 * math.pi + 1e-6:
        return False
    if abs(tot - 2 * math.pi) < 1e-6:
        return L.star(lst) in L.STARS
    gaps = [lst[i][0] - (lst[i - 1][0] + lst[i - 1][1]) for i in range(1, n)]
    gaps = [lst[0][0] + 2 * math.pi - (lst[-1][0] + lst[-1][1])] + gaps      # gaps[i] = gap before lst[i]
    if any(g < -1e-6 for g in gaps):
        return False                                     # genuinely overlapping corners
    start = next((i for i in range(n) if gaps[i] > 1e-6), None)
    if start is None:
        return False
    seq = lst[start:] + lst[:start]; gs = gaps[start:] + gaps[:start]; arcs = [[seq[0]]]
    for i in range(1, n):
        if gs[i] > 1e-6:
            arcs.append([seq[i]])
        else:
            arcs[-1].append(seq[i])
    return all(tuple(l for _, _, l in arc) in L.ARCS for arc in arcs)


L.Patch.vertex_ok = vertex_ok_fixed     # used by growth AND refills in this study (see PREREGISTRATION changes)
N_TILES, RUNS, SEED0 = 400, 6, 20260928
BINS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6)]
HOLES_PER_BIN, RHO, ATTEMPTS = 6, 1.2, 8
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "holes.jsonl")


def area(t):
    return abs(L.orient(*t[1:])) / 2


def centroid(t):
    return sum(t[1:]) / 3


# ------------------------------------------------------------------ growth: a ring of Gromits
def grow(rng, n_tiles=N_TILES):
    seed = L.seed_patch(0j, 3 * S)
    P = L.Patch(seed); n0 = len(P.tris)
    rnd = {L.canon(t): 0 for t in seed}; r = 0; guesses = 0
    while len(P.tris) - n0 < n_tiles:
        r += 1
        fr = P.frontier()
        if not fr:
            return P, rnd, r, guesses, "closed"
        forced = {}
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                return P, rnd, r, guesses, "JAM"
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), cs[0])
        placed = 0
        for k, t in forced.items():
            if len(P.tris) - n0 >= n_tiles:
                break
            if P.legal(t):                         # re-checked against this round's earlier placements
                assert P.legal(t)                   # Z1
                P.add(t); rnd[k] = r; placed += 1
        if placed == 0:
            cs = P.candidates(*fr[0][:3])
            t = rng.choice(sorted(cs, key=lambda u: sorted(L.canon(u)[1])))
            assert P.legal(t)                       # Z1
            P.add(t); rnd[L.canon(t)] = r; guesses += 1
    return P, rnd, r, guesses, "ok"


# ------------------------------------------------------------------ holes and refills
def refill(remaining, centre, removed_area, rng, cap=60):
    Q = L.Patch(remaining); laid = []; got = 0.0
    lim = (RHO + 0.25) * S
    for _ in range(cap):
        if got >= removed_area - 1e-9:
            return laid, True
        edges = [e for e in Q.frontier() if abs((e[0] + e[1]) / 2 - centre) <= lim]
        opts = []
        for e in edges:
            cs = [t for t in Q.candidates(*e[:3]) if abs(centroid(t) - centre) <= lim]
            opts.append(cs)
            if len(cs) == 1:
                break
        forced = next((cs[0] for cs in opts if len(cs) == 1), None)
        if forced is not None:
            t = forced
        else:
            nonempty = [cs for cs in opts if cs]
            if not nonempty:
                return laid, False                  # jam: nothing fits anywhere in the hole
            t = rng.choice(sorted(nonempty[0], key=lambda u: sorted(L.canon(u)[1])))
        Q.add(t); laid.append(t); got += area(t)
    return laid, got >= removed_area - 1e-9


def run(k):
    rng = random.Random(SEED0 + k); t0 = time.time()
    P, rnd, rounds, guesses, status = grow(rng)
    fr = P.frontier(); mids = [(e[0] + e[1]) / 2 for e in fr]
    tiles = list(P.tris)
    info = []
    for t in tiles:
        c = centroid(t)
        if abs(c) < 4 * S:
            continue
        d = min(abs(c - m) for m in mids) / S
        info.append((c, d))
    holes = []
    for lo, hi in BINS:
        pool = [c for c, d in info if lo <= d < hi]
        rng.shuffle(pool)
        chosen = []
        for c in pool:                               # hole centres at least 2*RHO apart within a run
            if all(abs(c - q) > 2 * RHO * S for q in chosen):
                chosen.append(c)
            if len(chosen) == HOLES_PER_BIN:
                break
        for c in chosen:
            removed = [t for t in tiles if abs(centroid(t) - c) <= RHO * S]
            remaining = [t for t in tiles if abs(centroid(t) - c) > RHO * S]
            A = sum(area(t) for t in removed)
            # Z2: the original refill is legal
            Q = L.Patch(remaining)
            for t in removed:
                assert Q.legal(t), "Z2: original refill not legal"
                Q.add(t)
            orig = {L.canon(t) for t in removed}
            outcomes, diffs = collections.Counter(), set()
            for a in range(ATTEMPTS):
                laid, done = refill(remaining, c, A, random.Random((SEED0 + k) * 1000 + len(holes) * 10 + a))
                ks = frozenset(L.canon(t) for t in laid)
                if not done:
                    outcomes["jam"] += 1
                elif ks == orig:
                    outcomes["same"] += 1
                else:
                    outcomes["different"] += 1; diffs.add(ks)
            near = [t for t in tiles if abs(centroid(t) - c) <= 2 * S]
            H = len(near) / max(1, len({rnd[L.canon(t)] for t in near}))
            age = rounds - sum(rnd[L.canon(t)] for t in removed) / len(removed)
            holes.append(dict(run=k, bin=[lo, hi], dist=round(min(abs(c - m) for m in mids) / S, 3),
                              age=round(age, 2), H=round(H, 3), n_removed=len(removed),
                              same=outcomes["same"], different=outcomes["different"], jam=outcomes["jam"],
                              n_distinct_different=len(diffs), soft=outcomes["different"] > 0))
    return dict(run=k, status=status, rounds=rounds, guesses=guesses, tiles=len(tiles),
                seconds=round(time.time() - t0), holes=holes)


def summary():
    import numpy as np
    recs = [json.loads(l) for l in open(OUT)]
    H = [h for r in recs for h in r["holes"]]
    lines = [f"runs: {len(recs)} ({', '.join(r['status'] + '/' + str(r['rounds']) + 'rounds/' + str(r['guesses']) + 'guesses' for r in recs)}); holes: {len(H)}"]
    F = []
    for lo, hi in BINS:
        b = [h for h in H if h["bin"] == [lo, hi]]
        f = sum(h["soft"] for h in b) / len(b) if b else float("nan"); F.append(f)
        jam = sum(h["jam"] for h in b) / max(1, sum(h["same"] + h["different"] + h["jam"] for h in b))
        lines.append(f"  distance {lo}-{hi} edges: {len(b):>3} holes, freedom F = {f:.2f}, attempts jammed {jam:.0%}, "
                     f"mean age {np.mean([h['age'] for h in b]) if b else float('nan'):.1f} rounds")
    s1 = F[0] >= 0.5 and F[-1] <= 0.1
    ups = [(F[i + 1] - F[i]) for i in range(len(F) - 1) if F[i + 1] > F[i]]
    s2 = len(ups) <= 1 and all(u <= 0.1 for u in ups)
    # S3: within-bin permutation test on happening density (hard minus soft)
    rng = np.random.default_rng(2028)
    groups = [[h for h in H if h["bin"] == [lo, hi]] for lo, hi in BINS]
    groups = [g for g in groups if any(h["soft"] for h in g) and not all(h["soft"] for h in g)]

    def stat(gs, labels):
        vals = []
        for g, lab in zip(gs, labels):
            hs = [h["H"] for h, s in zip(g, lab) if not s]; ss = [h["H"] for h, s in zip(g, lab) if s]
            vals.append(np.mean(hs) - np.mean(ss))
        return float(np.mean(vals)) if vals else float("nan")
    if groups:
        obs = stat(groups, [[h["soft"] for h in g] for g in groups])
        perm = [stat(groups, [list(rng.permutation([h["soft"] for h in g])) for g in groups]) for _ in range(10000)]
        p = (1 + sum(1 for v in perm if v >= obs)) / (1 + len(perm))
    else:
        obs, p = float("nan"), float("nan")
    width = next((f"{lo}-{hi} edges" for (lo, hi), f in zip(BINS, F) if f < 0.1), "not reached")
    lines += [f"  S1: {'HELD  ' if s1 else 'FAILED'}  F at the front {F[0]:.2f} (need >= 0.5), F deepest {F[-1]:.2f} (need <= 0.1)",
              f"  S2: {'HELD  ' if s2 else 'FAILED'}  freedom narrows with depth: {', '.join(f'{f:.2f}' for f in F)}",
              f"  S3: {'HELD  ' if (groups and p < 0.05 and obs > 0) else 'FAILED'}  quiet places stay open longer: "
              f"mean (H hardened - H soft) within bins = {obs:+.3f}, permutation p = {p:.4f} ({len(groups)} usable bins)",
              f"  width of the now (first bin with F < 0.1): {width}"]
    ages = sorted(set(round(h["age"]) for h in H))
    for a in ages:
        b = [h for h in H if round(h["age"]) == a]
        lines.append(f"    by age {a:>3} rounds: {len(b):>3} holes, F = {sum(x['soft'] for x in b) / len(b):.2f}")
    print("\n".join(lines))
    open(os.path.join(RES, "soft_zone_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = {json.loads(l)["run"] for l in open(OUT)} if os.path.exists(OUT) else set()
    todo = [k for k in range(RUNS) if k not in done]
    with Pool(min(4, len(todo) or 1), maxtasksperchild=1) as p:
        for res in p.imap_unordered(run, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"run {res['run']} done: {res['status']}, {res['rounds']} rounds, {res['guesses']} guesses, "
                  f"{len(res['holes'])} holes, {res['seconds']} s", flush=True)
    summary()
