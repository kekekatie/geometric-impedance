#!/usr/bin/env python3
"""
relative_nows.py -- what happens when two growing fronts meet? (PREREGISTRATION.md, frozen before this file.)

Two genuine reference patches at -8 and +8 tile edges grow simultaneously as rings of Gromits (full matching
rules, corrected vertex check, via ../soft_zone). Arms: TWO-LOCAL (random guesses: relative nows), TWO-ORACLE
(guesses resolved to the reference tiling: a universal now), ONE-LOCAL (single seed, size control).
Incremental: results/runs.jsonl; `--summary` evaluates M1-M4.
"""
from __future__ import annotations
import os, sys, math, json, random, time, collections
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "soft_zone"))
import soft_zone as SZ            # installs the corrected vertex check on laying_the_tiling.Patch
L = SZ.L
S = L.SCALE_LEN
C1, C2 = -8 * S + 0j, 8 * S + 0j
N_ADD, RUNS, SEED0 = 1100, 12, 20260929
ARMS = ["TWO-LOCAL", "TWO-ORACLE", "ONE-LOCAL"]
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "runs.jsonl")
REFSET = {L.canon(t) for t in L.REF}


def grow(arm, rng):
    seeds = [(C1, 1)] + ([(C2, 2)] if arm != "ONE-LOCAL" else [])
    label = {}
    tris = []
    for c, lab in seeds:
        for t in L.seed_patch(c, 3 * S):
            label[L.canon(t)] = lab; tris.append(t)
    P = L.Patch(tris); n0 = len(P.tris); rounds = 0; guesses = collections.Counter()
    centre = {1: C1, 2: C2}
    while len(P.tris) - n0 < N_ADD:
        rounds += 1
        fr = P.frontier()
        forced = {}
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                return P, label, rounds, guesses, "JAM", ((e[0] + e[1]) / 2)
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), (cs[0], label[L.canon(e[3])]))
        placed = 0
        for k, (t, lab) in forced.items():
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); label[k] = lab; placed += 1
        if placed == 0:
            e = min(fr, key=lambda e: abs((e[0] + e[1]) / 2 - centre[label[L.canon(e[3])]]))
            lab = label[L.canon(e[3])]
            cs = sorted(P.candidates(*e[:3]), key=lambda u: sorted(L.canon(u)[1]))
            if arm == "TWO-ORACLE":
                ref = [u for u in cs if L.canon(u) in REFSET]
                t = ref[0] if ref else rng.choice(cs)
            else:
                t = rng.choice(cs)
            P.add(t); label[L.canon(t)] = lab; guesses[lab] += 1
    return P, label, rounds, guesses, "ok", None


def refill_radius(remaining, centre, removed_area, rng, radius, cap=120):
    Q = L.Patch(remaining); laid = []; got = 0.0; lim = radius + 0.25 * S
    for _ in range(cap):
        if got >= removed_area - 1e-9:
            return Q, laid, True
        edges = [e for e in Q.frontier() if abs((e[0] + e[1]) / 2 - centre) <= lim]
        opts = []
        for e in edges:
            cs = [t for t in Q.candidates(*e[:3]) if abs(SZ.centroid(t) - centre) <= lim]
            opts.append(cs)
            if len(cs) == 1:
                break
        forced = next((cs[0] for cs in opts if len(cs) == 1), None)
        if forced is None:
            nonempty = [cs for cs in opts if cs]
            if not nonempty:
                return Q, laid, False
            forced = rng.choice(sorted(nonempty[0], key=lambda u: sorted(L.canon(u)[1])))
        Q.add(forced); laid.append(forced); got += SZ.area(forced)
    return Q, laid, got >= removed_area - 1e-9


def soft_repair(P, jam_mid, rng_seed):
    tiles = list(P.tris); rad = 2 * S
    removed = [t for t in tiles if abs(SZ.centroid(t) - jam_mid) <= rad]
    remaining = [t for t in tiles if abs(SZ.centroid(t) - jam_mid) > rad]
    A = sum(SZ.area(t) for t in removed)
    for a in range(8):
        Q, laid, done = refill_radius(remaining, jam_mid, A, random.Random(rng_seed * 100 + a), rad)
        if not done:
            continue
        near = [e for e in Q.frontier() if abs((e[0] + e[1]) / 2 - jam_mid) <= rad + 1.5 * S]
        if all(Q.candidates(*e[:3]) for e in near):
            return True, a + 1
    return False, None


def task(args):
    arm, k = args
    t0 = time.time(); rng = random.Random(SEED0 + k)
    P, label, rounds, guesses, status, jam_mid = grow(arm, rng)
    by = collections.defaultdict(list)
    for t in P.tris:
        by[label[L.canon(t)]].append(L.canon(t) in REFSET)
    agree = {lab: sum(v) / len(v) for lab, v in by.items()}
    iface = sum(1 for ek, ts in P.edges.items() if len(ts) == 2 and label[L.canon(ts[0])] != label[L.canon(ts[1])])
    # agreement with the reference near the interface (tiles within 3 edges of the bisector), per region
    near = collections.defaultdict(list)
    for t in P.tris:
        if abs(SZ.centroid(t).real) <= 3 * S:
            near[label[L.canon(t)]].append(L.canon(t) in REFSET)
    near_agree = {lab: (sum(v) / len(v) if v else None) for lab, v in near.items()}
    rep = None
    if status == "JAM" and arm == "TWO-LOCAL":
        rep = soft_repair(P, jam_mid, SEED0 + k)
    return dict(arm=arm, run=k, status=status, rounds=rounds, tiles=len(P.tris),
                guesses={str(a): b for a, b in guesses.items()}, agree={str(a): b for a, b in agree.items()},
                near_agree={str(a): b for a, b in near_agree.items()}, interface_edges=iface,
                jam=[jam_mid.real / S, jam_mid.imag / S] if jam_mid is not None else None,
                repaired=rep[0] if rep else None, repair_attempt=rep[1] if rep else None,
                seconds=round(time.time() - t0))


def summary():
    R = [json.loads(l) for l in open(OUT)]
    by = {a: [r for r in R if r["arm"] == a] for a in ARMS}
    lines = []
    for a in ARMS:
        rs = by[a]
        jams = [r for r in rs if r["status"] == "JAM"]
        met = [r for r in rs if r["interface_edges"] >= 10]
        lines.append(f"{a}: {len(rs)} runs; jammed {len(jams)}; fronts met (>=10 interface edges) {len(met)}; "
                     f"merged (met and ok) {sum(1 for r in met if r['status'] == 'ok')}; "
                     f"guesses per run {[sum(r['guesses'].values()) for r in rs]}")
        for r in rs:
            lines.append(f"    run {r['run']:>2}: {r['status']:<4} tiles {r['tiles']} interface {r['interface_edges']:>3} "
                         f"agree {({k: round(v, 3) for k, v in r['agree'].items()})} near-interface "
                         f"{({k: (round(v, 3) if v is not None else None) for k, v in r['near_agree'].items()})}"
                         + (f" jam at x={r['jam'][0]:+.1f} edges" if r["jam"] else "")
                         + (f" repaired={r['repaired']}" if r["repaired"] is not None else ""))
    to, tl, ol = by["TWO-ORACLE"], by["TWO-LOCAL"], by["ONE-LOCAL"]
    m1 = all(r["status"] == "ok" for r in to) and all(abs(v - 1.0) < 1e-12 for r in to for v in r["agree"].values())
    m2 = all(r["status"] == "ok" for r in ol)
    j = [r for r in tl if r["status"] == "JAM"]
    m3 = len(j) >= 6
    m4 = bool(j) and all(abs(r["jam"][0]) < 3 for r in j)
    lines += [f"  M1: {'HELD  ' if m1 else 'FAILED'}  TWO-ORACLE never jams and agrees with the reference everywhere",
              f"  M2: {'HELD  ' if m2 else 'FAILED'}  ONE-LOCAL never jams ({sum(1 for r in ol if r['status'] == 'JAM')}/{len(ol)} jammed)",
              f"  M3: {'HELD  ' if m3 else 'FAILED'}  TWO-LOCAL jams in >= 6/12 runs ({len(j)}/{len(tl)})",
              f"  M4: {'HELD  ' if m4 else 'FAILED'}  TWO-LOCAL jams lie in the meeting zone (|x| < 3 edges): "
              f"{[round(r['jam'][0], 1) for r in j]}",
              f"  soft repair of TWO-LOCAL seams: {sum(1 for r in j if r['repaired'])}/{len(j)} repaired"]
    print("\n".join(lines))
    open(os.path.join(RES, "relative_nows_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = {(json.loads(l)["arm"], json.loads(l)["run"]) for l in open(OUT)} if os.path.exists(OUT) else set()
    todo = [(a, k) for a in ARMS for k in range(RUNS) if (a, k) not in done]
    with Pool(4, maxtasksperchild=1) as p:
        for res in p.imap_unordered(task, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"{res['arm']} run {res['run']}: {res['status']}, {res['tiles']} tiles, interface {res['interface_edges']}, "
                  f"{res['seconds']} s", flush=True)
    summary()
