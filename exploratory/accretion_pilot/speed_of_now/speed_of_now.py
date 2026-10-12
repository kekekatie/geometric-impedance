#!/usr/bin/env python3
"""
speed_of_now.py -- why do some choices make the present rush ahead? (PREREGISTRATION.md, frozen before this file.)
24 fresh ordinary worlds grown with the patient scheduler. At every two-way choice, each option gets a sibling that is
grown on for 40 slices with the patient scheduler (same random stream for both): its BURST (tiles until the first slice
with nothing forced), the piece of wiggle room F it keeps, its late rate and its total.
`python3 speed_of_now.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, collections
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "golden_digits"))
import golden_digits as GD
Sl, L, D, S, G = GD.Sl, GD.L, GD.D, GD.S, GD.G
SEED0, N_ADD, N_WORLDS, LONG, LATE, UNEQUAL = 20261160, 1500, 24, 40, (21, 40), 10
RES = os.path.join(HERE, "results")


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[96:96 + N_WORLDS]


def ordered(cs):
    return sorted(cs, key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))


def patient(P, rng):
    """one slice of the patient scheduler. returns (status, tiles placed, kind) with kind 'forced' or 'guess'."""
    fr = P.frontier(); forced = {}
    for e in fr:
        cs = D.candidates(P, *e[:3])
        if not cs:
            return "JAM", 0, None
        if len(cs) == 1:
            forced.setdefault(D.dkey(cs[0]), cs[0])
    if forced:
        n = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); n += 1
        return "ok", n, "forced"
    P.add(rng.choice(ordered(D.candidates(P, *fr[0][:3]))))
    return "ok", 1, "guess"


def sibling(base, t, rank, aF, stream):
    Q = L.Patch(list(base)); Q.add(t); rng = random.Random(stream)
    per = [1]; burst = None; burst_slices = None; area_burst = None; guesses = 0; status = "ok"
    for s in range(1, LONG + 1):
        st, n, kind = patient(Q, rng)
        if st == "JAM":
            status = "JAM"; break
        if burst is None and kind == "guess":
            burst, burst_slices = sum(per), s - 1
            area_burst = Sl.area(Sl.region(Sl.constraints(list(Q.tris)[:-1], rank)))
        guesses += kind == "guess"
        per.append(n)
    if burst is None:          # never stalled within 40 slices, or jammed
        burst, burst_slices = sum(per), len(per) - 1
        area_burst = Sl.area(Sl.region(Sl.constraints(list(Q.tris), rank)))
    return dict(per=per, burst=burst, burst_slices=burst_slices, piece=area_burst / aF, guesses=guesses, status=status,
                total=sum(per), late=sum(per[LATE[0]:LATE[1] + 1]))


def world(k):
    rng = random.Random(SEED0 + k)
    P = L.Patch(L.seed_patch(centres()[k], 3 * S)); n0 = len(P.tris); r = 0
    rank = Sl.rank_of(P.tris); choices = []; status = "ok"
    while len(P.tris) - n0 < N_ADD:
        r += 1
        fr = P.frontier(); forced = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam:
            status = "JAM"; break
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        cs = ordered(D.candidates(P, *fr[0][:3]))
        base = list(P.tris); aF = Sl.area(Sl.region(Sl.constraints(base, rank)))
        rec = dict(world=k, slice=r, n_tiles=len(base), n_options=len(cs), area=aF, frontier=len(fr),
                   dist=abs(sum(fr[0][:2]) / 2 - centres()[k]) / S)
        if len(cs) == 2 and aF > 0:
            stream = SEED0 * 1000 + k * 100 + len(choices)
            rec["A"] = sibling(base, cs[0], rank, aF, stream); rec["B"] = sibling(base, cs[1], rank, aF, stream)
        t = rng.choice(cs); rec["picked"] = cs.index(t); P.add(t); choices.append(rec)
    return dict(world=k, status=status, slices=r, choices=choices)


def family(x):
    n = min(G, key=lambda m: abs(G[m] - min(x, 1 - x)))
    return n if abs(G[n] - min(x, 1 - x)) <= 0.002 else "other"


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(N_WORLDS))
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    two = [c for w in W for c in w["choices"] if "A" in c]
    live = [c for c in two if c["A"]["piece"] > 0 and c["B"]["piece"] > 0]
    dead = [c for c in two if c not in live]
    uneq = [c for c in live if abs(c["A"]["burst"] - c["B"]["burst"]) >= UNEQUAL]
    lines = [f"worlds: statuses {dict(collections.Counter(w['status'] for w in W))}; choices {sum(len(w['choices']) for w in W)}; "
             f"two-option with F > 0: {len(two)}; live {len(live)}; dead-optioned {len(dead)}; live and unequal {len(uneq)}",
             f"  bursts (live, smaller-piece sibling first): " + "; ".join(
                 f"{min(c['A'], c['B'], key=lambda s: s['piece'])['burst']}/{max(c['A'], c['B'], key=lambda s: s['piece'])['burst']}" for c in live)]
    sm = lambda c: min((c["A"], c["B"]), key=lambda s: s["piece"]); lg = lambda c: max((c["A"], c["B"]), key=lambda s: s["piece"])
    s1n = sum(sm(c)["burst"] > lg(c)["burst"] for c in uneq)
    s1 = bool(uneq) and s1n >= 0.7 * len(uneq)
    lines.append(f"  S1: {'HELD  ' if s1 else 'FAILED'}  smaller piece has the larger burst in {s1n}/{len(uneq)} live unequal choices (need >= 70%)")
    db = [c["A"]["burst"] - c["B"]["burst"] for c in live]; dl = [c["A"]["late"] - c["B"]["late"] for c in live]
    rho = spearmanr(db, dl).correlation if len(live) >= 3 else float("nan")
    s2 = -0.2 <= rho <= 0.2
    lines.append(f"  S2: {'HELD  ' if s2 else 'FAILED'}  Spearman(burst gap, late-rate gap, slices {LATE[0]}-{LATE[1]}) = {rho:+.3f} over {len(live)} "
                 f"(need within +-0.2)")
    fade = [abs(c["A"]["total"] - c["B"]["total"]) < 0.5 * abs(c["A"]["burst"] - c["B"]["burst"]) for c in uneq]
    s3 = bool(uneq) and sum(fade) >= 0.6 * len(uneq)
    lines.append(f"  S3: {'HELD  ' if s3 else 'FAILED'}  total gap at slice {LONG} < half the burst gap in {sum(fade)}/{len(uneq)} (need >= 60%); "
                 f"(burst gap -> total gap): " + ", ".join(f"{c['A']['burst'] - c['B']['burst']:+d}->{c['A']['total'] - c['B']['total']:+d}" for c in uneq))
    fam = collections.defaultdict(list)
    for c in live:
        for s in (c["A"], c["B"]):
            fam[(family(s["piece"]), "small" if s["piece"] < 0.5 else "large")].append(s["burst"])
    lines.append("  reported: burst by piece family -> " + "; ".join(
        f"{f}/{sz}: n {len(v)}, median {np.median(v):.0f}, range {min(v)}-{max(v)}" for (f, sz), v in sorted(fam.items())))
    lines.append(f"  reported: burst slices smaller/larger piece medians {np.median([sm(c)['burst_slices'] for c in live]):.0f}/"
                 f"{np.median([lg(c)['burst_slices'] for c in live]):.0f}; guesses in {LONG} slices smaller/larger piece "
                 f"{np.mean([sm(c)['guesses'] for c in live]):.2f}/{np.mean([lg(c)['guesses'] for c in live]):.2f}")
    lines.append(f"  reported: Spearman(burst gap, total gap at {LONG}) = {spearmanr(db, [c['A']['total'] - c['B']['total'] for c in live]).correlation:+.3f}")
    for c in dead:
        d, a = (c["A"], c["B"]) if c["A"]["piece"] == 0 else (c["B"], c["A"])
        lines.append(f"  dead option (world {c['world']}, slice {c['slice']}): dead sibling burst {d['burst']} status {d['status']} "
                     f"after {len(d['per']) - 1} slices; live sibling burst {a['burst']}")
    print("\n".join(lines))
    open(os.path.join(RES, "speed_of_now_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
