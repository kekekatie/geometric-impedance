#!/usr/bin/env python3
"""
seed_crystal.py -- a first, gentle resonance test: would TWINS fill the now's gaps sooner than
the roads do?

Katie's seed crystal (cheese-wheel chat): a supersaturated syrup waits until a seed of the
RIGHT shape drops in; wrong-shaped dust does nothing. Here:
  syrup   the GAPS in the growing 2-D now (../penrose_growth/, FORK): tiling vertices enclosed
          by the now but not yet held. (v1 of this study called them houses the roads SKIP --
          wrong: every gap has a road leading in and is filled later. Gaps are LAG.)
  seed    a TWIN of the gap already held by the now: same layer and the same radius-r
          neighbourhood (exact integer K-offsets), anywhere in the now -- often far away.
  dust    the control: a random held vertex of the same layer, with no likeness required.

A true twin fits by definition (same neighbourhood). Measured, over snapshots of one QUEUE run
and one DICE run:
  (1) ROADS-WAIT    how many more events until the roads fill each gap (the syrup would
                    crystallise by itself -- how long does it take?)
  (2) AVAILABILITY  is a seed already in the now at match depth r = 1..R_MAX? At which depth do
                    seeds run out (the nothing-happens case)?
  (3) DISTANCE      nearest seed: how far in the world, how close in the hidden window?
  (4) DUST          how often would a random same-layer vertex even fit (same star of edges)?
Resonance is NOT run as a dynamics here: this is the census that says whether a seed rule
could act as a shortcut, and at what depth. asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, math, random, collections, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "penrose_growth"))
sys.path.insert(0, os.path.join(HERE, "..", "penrose_address_environment"))
import penrose_growth as G                            # growth + the exact tiling (no main)
import penrose_address as P

REPORT = os.path.join(HERE, "results", "seed_crystal_report.txt")
DATA = os.path.join(HERE, "results", "seed_crystal.json")
LINES, FAILS = [], []
R_MAX = 9
SNAPS = (1000, 2000, 3000, 4000)
T_END = 7000
SEED = 20260924
N_DUST = 200


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def env(v, r):
    """exact radius-r neighbourhood: K-offsets of vertices and edges within r steps."""
    seen = {v: 0}; q = collections.deque([v])
    while q:
        u = q.popleft()
        if seen[u] == r:
            continue
        for w in G.ADJ[u]:
            if w not in seen:
                seen[w] = seen[u] + 1; q.append(w)
    vs = set(seen)
    return (frozenset(P.sub(u, v) for u in vs),
            frozenset(frozenset((P.sub(a, v), P.sub(b, v))) for a in vs for b in G.ADJ[a] if b in vs))


def holes_of(held):
    seen, holes = set(), []
    for v in G.VERTS:
        if v in held or v in seen:
            continue
        comp, q, edge = [v], [v], False; seen.add(v)
        while q:
            u = q.pop()
            if math.hypot(*G.POS[u]) > G.EDGE_R:
                edge = True
            for w in G.ADJ[u]:
                if w not in held and w not in seen:
                    seen.add(w); comp.append(w); q.append(w)
        if not edge:
            holes.extend(comp)
    return holes


def roads_reach(h, held):
    return any(G.road_next(n, rd) == h for n in G.ADJ[h] if n in held for rd in G.ROADS)


def main():
    log("=" * 90)
    log("SEED CRYSTAL -- would twins fill the now's gaps sooner than the roads do?")
    log("=" * 90)
    G.T = T_END
    core = G.R - (R_MAX + 3)
    cache = {r: {} for r in range(1, R_MAX + 1)}

    def E(K, r):
        if K not in cache[r]:
            cache[r][K] = env(K, r)
        return cache[r][K]

    rows_all, dust_fit, dust_tot = {}, 0, 0
    rng_d = random.Random(SEED + 1)
    for clock, rs in (("QUEUE", 0), ("DICE", 7)):
        g = G.grow("FORK", clock, random.Random(SEED + rs))
        order = g["order"]; born = {K: i for i, K in enumerate(order)}
        gaps = []                                           # (snapshot T, gap vertex)
        for T in SNAPS:
            held = set(order[:T + 1])
            for h in holes_of(held):
                gaps.append((T, h, held))
        require(all(roads_reach(h, held) for _, h, held in gaps),
                f"{clock}: every gap at every snapshot has a road leading in -- none is skipped "
                f"({len(gaps)} gaps over snapshots {SNAPS})")
        filled = [born.get(h) for _, h, _ in gaps]
        require(all(b is not None for b in filled),
                f"{clock}: the roads fill every gap eventually (all {len(gaps)} filled by event "
                f"{T_END}): the syrup crystallises by itself")
        waits = sorted(born[h] - T for T, h, _ in gaps)
        med = lambda L: sorted(L)[len(L) // 2] if L else float("nan")
        log("-" * 90)
        log(f"[{clock}] {len(gaps)} gaps over snapshots {SNAPS}; the roads fill them after "
            f"median {med(waits)} more events (range {waits[0]}-{waits[-1]})")
        log("    depth r | gaps with a seed already in the now | nearest seed: median world "
            "distance | median window distance")
        rows = []
        for r in range(1, R_MAX + 1):
            have, dists, wd = 0, [], []
            for T, h, held in gaps:
                if math.hypot(*G.POS[h]) >= core:
                    continue
                key = (sum(h), E(h, r))
                seeds = [s for s in held if s != h and math.hypot(*G.POS[s]) < core
                         and sum(s) == sum(h) and E(s, r) == key[1]]
                if not seeds:
                    continue
                have += 1
                near = min(seeds, key=lambda s: math.hypot(G.POS[s][0] - G.POS[h][0], G.POS[s][1] - G.POS[h][1]))
                dists.append(math.hypot(G.POS[near][0] - G.POS[h][0], G.POS[near][1] - G.POS[h][1]))
                ph, ps = P.perp(h), P.perp(near)
                wd.append(math.hypot(ph[0] - ps[0], ph[1] - ps[1]))
            n_in = sum(1 for _, h, _ in gaps if math.hypot(*G.POS[h]) < core)
            rows.append(dict(r=r, have=have, n=n_in, dist=med(dists), wdist=med(wd)))
            log(f"    r={r:<2}    | {have:>4} / {n_in:<4}                          | "
                f"{med(dists):8.1f}                        | {med(wd):.3f}")
        rows_all[clock] = dict(rows=rows, waits=waits, n=len(gaps))
        require(rows[0]["have"] == rows[0]["n"],
                f"{clock}: at shallow depth (r=1) every gap already has a seed in the now")
        require(all(rows[i + 1]["have"] <= rows[i]["have"] for i in range(len(rows) - 1)),
                f"{clock}: a deeper match never adds seeds (availability falls or holds with depth)")
        dry = next((x["r"] for x in rows if x["have"] < x["n"]), None)
        log(f"    seeds first run out (some gap has no twin in the now) at depth: "
            f"{dry if dry else 'not within r <= %d' % R_MAX}")
        for T, h, held in gaps[:40]:
            same = [K for K in held if sum(K) == sum(h) and math.hypot(*G.POS[K]) < core]
            for _ in range(20):
                d = rng_d.choice(same)
                dust_fit += E(d, 1) == E(h, 1); dust_tot += 1
    dust = dust_fit / dust_tot
    log("-" * 90)
    log(f"  dust control: a random same-layer house fits a gap's star of edges {dust:.1%} of the "
        f"time (a true twin: 100%, by definition)")
    require(dust < 0.5, f"wrong-shaped dust usually does NOT fit ({dust:.0%}): likeness is what "
                        f"makes a seed work, not merely something arriving")
    q, d = rows_all["QUEUE"], rows_all["DICE"]
    mq, md = sorted(q["waits"])[len(q["waits"]) // 2], sorted(d["waits"])[len(d["waits"]) // 2]
    log(f"  QUEUE vs DICE: gaps {q['n']} vs {d['n']}; median roads-wait {mq} vs {md}; longest "
        f"{max(q['waits'])} vs {max(d['waits'])}  (v1 PREDICTED dice gaps wait longer at the "
        f"median -- wrong: dice makes many more gaps, with a longer tail, but a similar median)")
    require(d["n"] > 3 * q["n"] and max(d["waits"]) > max(q["waits"]),
            f"dice leaves far MORE gaps ({d['n']} vs {q['n']}) with a LONGER tail of waiting "
            f"({max(d['waits'])} vs {max(q['waits'])} events)")

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(dict(rows=rows_all, dust=dust, snaps=SNAPS), open(DATA, "w"))
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
