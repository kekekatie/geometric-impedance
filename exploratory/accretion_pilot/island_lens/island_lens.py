#!/usr/bin/env python3
"""
island_lens.py -- door 2: does a quiet island delay and bend the arriving now, and does a full one? (PREREGISTRATION.md,
frozen before this file.) WAIT scheduler with ORACLE guesses (every arm lays the same reference tiling; only timing
differs). Arms: CONTROL (no island), QUIET (island forced placements at rate 0.25), FULL (island pre-laid, inert until
reached). Arrival-time delays behind / beside / opposite the island. `--summary` evaluates G0-G3.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "soft_zone"))
import soft_zone as SZ            # installs the corrected vertex check
L = SZ.L
S = L.SCALE_LEN
cen = SZ.centroid
N_ADD, RUNS, SEED0, P_QUIET, R_I, D_I, STALL = 4000, 8, 20261030, 0.25, 2.0, 6.5, 50000
OFF = (0.0123 + 0.0071j) * S
REFSET = {L.canon(t) for t in L.REF}
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "runs.jsonl")


def island_centre(k):
    return D_I * S * cmath.exp(1j * (2 * math.pi * k / 8 + 0.2))


def grow(arm, k):
    c = island_centre(k) if arm != "CONTROL" else None
    rng = random.Random(SEED0 + k)
    seed = L.seed_patch(0j, 3 * S)
    island = [t for t in L.REF if abs(cen(t) - c) <= R_I * S] if arm == "FULL" else []
    ikeys = {L.canon(t) for t in island}
    ivert = {L.key(z) for t in island for z in t[1:]}
    P = L.Patch(seed + island); n0 = len(P.tris)
    rnd = {L.canon(t): 0 for t in seed}; geo = {L.canon(t): t for t in seed}
    r = 0; guesses = 0; idle = 0; awake = arm != "FULL"; wake_round = None; status = "ok"
    while len(P.tris) - n0 < N_ADD:
        r += 1
        if r > STALL:
            status = "STALL"; break
        fr = [e for e in P.frontier() if awake or L.canon(e[3]) not in ikeys]
        forced = {}; dead = False
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                dead = True; break
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), (cs[0], (e[0] + e[1]) / 2))
        if dead:
            status = "JAM"; break
        legal = [(q, t, m) for q, (t, m) in forced.items() if P.legal(t)]
        if forced and not legal:
            status = "STUCK"; break
        placed = 0; new = []
        for q, t, m in legal:
            if len(P.tris) - n0 >= N_ADD:
                break
            if arm == "QUIET" and abs(m - c) <= R_I * S and rng.random() >= P_QUIET:
                continue
            if P.legal(t):
                P.add(t); rnd[q] = r; geo[q] = t; placed += 1; new.append(t)
        if placed == 0:
            if forced:
                idle += 1; continue
            cs = P.candidates(*fr[0][:3])
            ref = [u for u in cs if L.canon(u) in REFSET]
            assert ref, "oracle: no reference candidate"
            t = ref[0]; P.add(t); rnd[L.canon(t)] = r; geo[L.canon(t)] = t; guesses += 1; new.append(t)
        if not awake and any(L.key(z) in ivert for t in new for z in t[1:]):
            awake = True; wake_round = r
    all_ref = all(q in REFSET for q in rnd)
    return dict(P=P, rnd=rnd, geo=geo, island=ikeys, status=status, rounds=r, guesses=guesses, idle=idle,
                wake_round=wake_round, all_ref=all_ref, c=c)


def points(c):
    u = c / abs(c); v = u * 1j; out = {"shadow": [], "side": [], "far": []}
    for i in range(6):
        s = (1.0 + 0.5 * i) * S
        for w in (-0.5, 0.0, 0.5):
            p = c + u * (R_I * S + s) + v * w * S
            out["shadow"].append(p + OFF); out["far"].append(-p + OFF)
        for sgn in (-1, 1):
            out["side"].append(c + u * (R_I * S + s) + sgn * v * 4.0 * S + OFF)
    return out


def arrival(h, pts):
    """round in which the tile covering each point was laid (None: uncovered; 'island': a pre-laid island tile)"""
    res = []
    for p in pts:
        hit = next((t for t in h["P"].tris if abs(cen(t) - p) < 1.2 * S and L.inside(p, *t[1:])), None)
        if hit is None:
            res.append(None)
        elif L.canon(hit) in h["island"]:
            res.append("island")
        else:
            res.append(h["rnd"][L.canon(hit)])
    return res


def happening(h, c):
    """QUIET cross-check: tiles per round per unit area inside the island vs in the ring R_I..R_I+2 around it,
    over the rounds in which island tiles were being laid."""
    ins = [(q, x) for q, x in h["rnd"].items() if abs(cen(h["geo"][q]) - c) <= R_I * S]
    if not ins:
        return None
    lo, hi = min(x for _, x in ins), max(x for _, x in ins); span = max(1, hi - lo + 1)
    ring = [x for q, x in h["rnd"].items() if R_I * S < abs(cen(h["geo"][q]) - c) <= (R_I + 2) * S and lo <= x <= hi]
    a_in = math.pi * R_I ** 2; a_ring = math.pi * ((R_I + 2) ** 2 - R_I ** 2)
    return dict(first=lo, last=hi, inside=len(ins) / span / a_in, ring=len(ring) / span / a_ring)


def task(args):
    arm, k = args; t0 = time.time()
    h = grow(arm, k)
    out = dict(arm=arm, run=k, status=h["status"], rounds=h["rounds"], guesses=h["guesses"], idle=h["idle"],
               wake_round=h["wake_round"], all_ref=h["all_ref"])
    if arm == "CONTROL":
        out["arrivals"] = {}
        for kk in range(RUNS):
            out["arrivals"][kk] = {g: arrival(h, ps) for g, ps in points(island_centre(kk)).items()}
    else:
        out["arrivals"] = {g: arrival(h, ps) for g, ps in points(h["c"]).items()}
        if arm == "QUIET":
            out["happening"] = happening(h, h["c"])
    out["seconds"] = round(time.time() - t0)
    return out


def summary():
    import numpy as np
    R = [json.loads(l) for l in open(OUT)]
    ctrl = next(r for r in R if r["arm"] == "CONTROL")
    lines = [f"CONTROL: {ctrl['status']}, {ctrl['rounds']} rounds, {ctrl['guesses']} guesses, idle {ctrl['idle']}, all reference {ctrl['all_ref']}"]
    g0 = ctrl["status"] == "ok" and ctrl["all_ref"]
    per = {}
    for arm in ("QUIET", "FULL"):
        rs = sorted([r for r in R if r["arm"] == arm], key=lambda r: r["run"])
        lines.append(f"{arm}: statuses {[r['status'] for r in rs]}, rounds {[r['rounds'] for r in rs]}, guesses {[r['guesses'] for r in rs]}, "
                     f"idle {[r['idle'] for r in rs]}, all reference {all(r['all_ref'] for r in rs)}"
                     + (f", wake rounds {[r['wake_round'] for r in rs]}" if arm == "FULL" else ""))
        g0 &= all(r["status"] == "ok" and r["all_ref"] for r in rs)
        rows = []
        for r in rs:
            cA = ctrl["arrivals"][str(r["run"])]; m = {}; excl = 0
            for g in ("shadow", "side", "far"):
                d = []
                for a, b in zip(r["arrivals"][g], cA[g]):
                    if a is None or b is None:
                        g0 = False; continue
                    if a == "island" or b == "island":
                        excl += 1; continue
                    d.append(a - b)
                m[g] = float(np.mean(d))
            byS = [float(np.mean([r["arrivals"]["shadow"][3 * i + j] - cA["shadow"][3 * i + j] for j in range(3)
                                  if isinstance(r["arrivals"]["shadow"][3 * i + j], int) and isinstance(cA["shadow"][3 * i + j], int)] or [float("nan")]))
                   for i in range(6)]
            rows.append(dict(run=r["run"], local=m["shadow"] - m["far"], lens=m["shadow"] - m["side"], far=m["far"],
                             shadow=m["shadow"], side=m["side"], excl=excl, byS=byS, hap=r.get("happening")))
        per[arm] = rows
        for x in rows:
            lines.append(f"    run {x['run']}: delay shadow {x['shadow']:+.1f}, side {x['side']:+.1f}, far {x['far']:+.1f} rounds -> "
                         f"local {x['local']:+.1f}, lens {x['lens']:+.1f}; excluded island points {x['excl']}; "
                         f"shadow delay by distance behind {[round(v, 1) for v in x['byS']]}"
                         + (f"; happening inside {x['hap']['inside']:.3f} vs ring {x['hap']['ring']:.3f} tiles/round/edge^2" if x["hap"] else ""))
    q, f = per["QUIET"], per["FULL"]
    g1 = sum(x["local"] > 0 for x in q) >= 7 and np.mean([x["local"] for x in q]) >= 2
    g2 = sum(x["lens"] > 0 for x in q) >= 7
    g3 = sum(x["local"] < 0 for x in f) >= 7
    lines += [f"  G0: {'PASS' if g0 else 'FAIL'}  no jams/stalls, all tiles in the reference tiling, all sample points covered",
              f"  G1: {'HELD  ' if g1 else 'FAILED'}  QUIET delays the now behind it: local delay > 0 in {sum(x['local'] > 0 for x in q)}/8 "
              f"(need >= 7), mean {np.mean([x['local'] for x in q]):+.1f} rounds (need >= 2)",
              f"  G2: {'HELD  ' if g2 else 'FAILED'}  QUIET focuses (lens > 0) in {sum(x['lens'] > 0 for x in q)}/8 (need >= 7); mean lens {np.mean([x['lens'] for x in q]):+.1f}",
              f"  G3: {'HELD  ' if g3 else 'FAILED'}  FULL: the now arrives EARLIER behind it (local < 0) in {sum(x['local'] < 0 for x in f)}/8 (need >= 7); "
              f"mean local {np.mean([x['local'] for x in f]):+.1f}",
              f"  (reported) FULL lens: {[round(x['lens'], 1) for x in f]} (mean {np.mean([x['lens'] for x in f]):+.1f}); "
              f"global delay far: QUIET mean {np.mean([x['far'] for x in q]):+.1f}, FULL mean {np.mean([x['far'] for x in f]):+.1f}"]
    print("\n".join(lines))
    open(os.path.join(RES, "island_lens_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = {(json.loads(l)["arm"], json.loads(l)["run"]) for l in open(OUT)} if os.path.exists(OUT) else set()
    todo = [("CONTROL", 0)] + [(a, k) for k in range(RUNS) for a in ("QUIET", "FULL")]
    todo = [t for t in todo if t not in done]
    with Pool(4, maxtasksperchild=1) as p:
        for res in p.imap_unordered(task, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"{res['arm']} run {res['run']}: {res['status']}, {res['rounds']} rounds, {res['guesses']} guesses, "
                  f"idle {res['idle']}, {res['seconds']} s", flush=True)
    summary()
