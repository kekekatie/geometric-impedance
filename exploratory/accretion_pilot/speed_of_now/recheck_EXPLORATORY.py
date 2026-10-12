#!/usr/bin/env python3
"""EXPLORATORY recheck after Astra's review of #51 (no new predictions; the registered results stand as reported).
  1. Structural grouping: the '36 distinct' in the README grouped choices by their two tile-count traces. Here choices
     are grouped by geometry instead: the decorated tiles within R edges of the choice edge (R = 4, 8) and the whole
     patch, all relative to the choice point (translations only, so rotated copies count as different).
  2. Equal splits: choices whose two pieces differ by less than EQ_TOL are set aside (no meaningful 'smaller piece').
  3. S1 recounted per structural group and per world.
  4. Unfinished bursts: how many bursts hit the 40-slice cap (lower bounds), and how many S2/S3 pairs compare
     quantities that overlap or coincide because a burst never ended.
  5. Dead options: the empty/point classifier on F after each dead sibling's burst (zero area is not proof of empty).
Writes results/recheck_EXPLORATORY.txt."""
import os, sys, json, random, hashlib, collections
from multiprocessing import Pool
import numpy as np
import speed_of_now as SN
sys.path.insert(0, os.path.join(SN.HERE, "..", "slack"))
import classify_EXPLORATORY as CL
Sl, L, D, S = SN.Sl, SN.L, SN.D, SN.S
EQ_TOL, RADII = 0.01, (4, 8)


def key(tiles, z, r=None):
    rk = lambda w: (round((w - z).real / S, 3), round((w - z).imag / S, 3))
    items = sorted((t[0], rk(t[1]), rk(t[2]), rk(t[3])) for t in tiles if r is None or abs(sum(t[1:]) / 3 - z) <= r * S)
    return hashlib.md5(repr(items).encode()).hexdigest()[:16]


def dead_kind(base, t, rank):
    """re-grow one sibling exactly as speed_of_now.sibling does until its first stall or jam; classify F there."""
    Q = L.Patch(list(base)); Q.add(t); g = random.Random(0)
    for s in range(1, SN.LONG + 1):
        fr = Q.frontier(); forced = {}; jam = False
        for e in fr:
            cs = D.candidates(Q, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam or not forced:
            break
        for x in forced.values():
            if Q.legal(x):
                Q.add(x)
    return CL.classify(Sl.constraints(list(Q.tris), rank))[0], ("JAM" if jam else "stall"), s


def replay(k):
    W = json.load(open(os.path.join(SN.RES, "worlds.json")))[k]
    want = {c["slice"]: c for c in W["choices"] if "A" in c}
    rng = random.Random(SN.SEED0 + k)
    P = L.Patch(L.seed_patch(SN.centres()[k], 3 * S)); n0 = len(P.tris); r = 0; rank = Sl.rank_of(P.tris); out = []
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
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3]))
        if r in want:
            z = (fr[0][0] + fr[0][1]) / 2; base = list(P.tris); c = want[r]
            rec = dict(world=k, slice=r, keys={str(R): key(base, z, R) for R in RADII}, whole=key(base, z))
            if min(c["A"]["piece"], c["B"]["piece"]) == 0:
                rec["dead"] = [dead_kind(base, t, rank) for t in cs]
            out.append(rec)
        P.add(rng.choice(cs))
    return out


def main():
    with Pool(4, maxtasksperchild=1) as p:
        K = [x for xs in p.map(replay, range(SN.N_WORLDS)) for x in xs]
    W = json.load(open(os.path.join(SN.RES, "worlds.json")))
    C = {(c["world"], c["slice"]): c for w in W for c in w["choices"] if "A" in c}
    for x in K:
        C[(x["world"], x["slice"])].update(keys=x["keys"], whole=x["whole"], dead=x.get("dead"))
    two = list(C.values())
    live = [c for c in two if c["A"]["piece"] > 0 and c["B"]["piece"] > 0]
    equal = [c for c in live if abs(c["A"]["piece"] - c["B"]["piece"]) < EQ_TOL]
    neq = [c for c in live if c not in equal]
    uneq = [c for c in neq if abs(c["A"]["burst"] - c["B"]["burst"]) >= SN.UNEQUAL]
    sm = lambda c: min((c["A"], c["B"]), key=lambda s: s["piece"]); lg = lambda c: max((c["A"], c["B"]), key=lambda s: s["piece"])
    win = lambda c: sm(c)["burst"] > lg(c)["burst"]
    lines = [f"EXPLORATORY recheck of speed_of_now: {len(two)} two-option choices, live {len(live)}, equal splits (|piece A - piece B| < {EQ_TOL}) "
             f"{len(equal)}, live unequal-share {len(neq)}, of which bursts differ by >= {SN.UNEQUAL}: {len(uneq)}",
             "  equal splits (set aside): " + "; ".join(f"w{c['world']} s{c['slice']} pieces {c['A']['piece']:.4f}/{c['B']['piece']:.4f} bursts {c['A']['burst']}/{c['B']['burst']}" for c in equal),
             f"  S1 recount without equal splits: smaller piece has the larger burst in {sum(map(win, uneq))}/{len(uneq)}"]
    for lab, g in [(f"local key R={R}", lambda c, R=R: c["keys"][str(R)]) for R in RADII] + [("whole patch", lambda c: c["whole"]),
                                                                                             ("activity traces", lambda c: (tuple(c["A"]["per"]), tuple(c["B"]["per"])))]:
        grp = collections.defaultdict(list)
        for c in uneq:
            grp[g(c)].append(c)
        mixed = sum(len({win(c) for c in v}) > 1 for v in grp.values())
        maj = sum(np.mean([win(c) for c in v]) > 0.5 for v in grp.values())
        lines.append(f"  grouped by {lab}: {len(grp)} groups (sizes {sorted((len(v) for v in grp.values()), reverse=True)}); S1 majority holds in "
                     f"{maj}/{len(grp)} groups; groups with mixed outcomes {mixed}")
    # traces vs geometry: do identical traces come from identical whole patches?
    tr = collections.defaultdict(set)
    for c in live:
        tr[(tuple(c["A"]["per"]), tuple(c["B"]["per"]))].add(c["whole"])
    lines.append(f"  identical activity traces spanning more than one whole-patch geometry: {sum(len(v) > 1 for v in tr.values())} of {len(tr)}")
    per_w = collections.defaultdict(list)
    for c in uneq:
        per_w[c["world"]].append(win(c))
    lines.append(f"  per world: {len(per_w)} worlds with qualifying choices; S1 holds in a majority of choices in "
                 f"{sum(np.mean(v) > 0.5 for v in per_w.values())}, exactly half {sum(np.mean(v) == 0.5 for v in per_w.values())}, "
                 f"minority {sum(np.mean(v) < 0.5 for v in per_w.values())}")
    cap = [s for c in live for s in (c["A"], c["B"])]
    unf = [s for s in cap if s["burst_slices"] >= SN.LONG and s["status"] == "ok"]
    both = [c for c in uneq if all(s["burst_slices"] >= SN.LONG for s in (c["A"], c["B"]))]
    one = [c for c in uneq if sum(s["burst_slices"] >= SN.LONG for s in (c["A"], c["B"])) == 1]
    late_in = [c for c in live if any(s["burst_slices"] >= SN.LATE[0] for s in (c["A"], c["B"]))]
    lines += [f"  unfinished bursts (never stalled in {SN.LONG} slices; burst is a lower bound): {len(unf)}/{len(cap)} siblings "
              f"(smaller piece {sum(sm(c)['burst_slices'] >= SN.LONG for c in live)}/{len(live)}, larger {sum(lg(c)['burst_slices'] >= SN.LONG for c in live)}/{len(live)})",
              f"  S3 pairs where burst = total for both (neither stalled): {len(both)}/{len(uneq)}; for one: {len(one)}/{len(uneq)}",
              f"  S2 pairs whose late window (slices {SN.LATE[0]}-{SN.LATE[1]}) still overlaps at least one burst: {len(late_in)}/{len(live)}"]
    for c in two:
        if c.get("dead"):
            lines.append(f"  dead option w{c['world']} s{c['slice']}: pieces {c['A']['piece']:.3f}/{c['B']['piece']:.3f}; "
                         f"classifier on each sibling's F at its first stall or jam: {c['dead']}")
    print("\n".join(lines))
    open(os.path.join(SN.RES, "recheck_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
