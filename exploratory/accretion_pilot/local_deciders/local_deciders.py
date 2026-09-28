#!/usr/bin/env python3
"""
local_deciders.py -- can the now become a local front without jamming? (PREREGISTRATION.md, frozen before this file.)
HORIZON-h scheduler: forced tiles are placed every round; a guess may be made at an edge when no forced edge lies
within h edges of it, at most one guess per h-neighbourhood per round. h = inf is the patient (WAIT) scheduler.
Measures: jams, sector spread SS of placement rounds in the 7-9 edge band. Incremental: results/runs.jsonl;
`--summary` evaluates H0-H3.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "continuation_choices"))
import continuation_choices as CC
SZ, L = CC.SZ, CC.L
S = L.SCALE_LEN
cen = SZ.centroid
N_ADD, RUNS, SEED0 = 1500, 8, 20261040
HORIZONS = [0.5, 1, 2, 3, 4, 6, math.inf]
BAND, SECTORS, STALL = (7.0, 9.0), 16, 20000
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "runs.jsonl")
mid = lambda e: (e[0] + e[1]) / 2


def grow(h, k):
    rng = random.Random(SEED0 + k)
    seed = L.seed_patch(0j, 3 * S)
    P = L.Patch(seed); n0 = len(P.tris)
    rnd = {L.canon(t): 0 for t in seed}; geo = {L.canon(t): t for t in seed}
    r = 0; guesses = []; per_round = []; status = "ok"; jam = None
    while len(P.tris) - n0 < N_ADD:
        r += 1
        if r > STALL:
            status = "STALL"; break
        fr = P.frontier(); forced = {}; multi = []
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                status = "JAM"; jam = mid(e); break
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), (cs[0], mid(e)))
            else:
                multi.append(e)
        if status == "JAM":
            break
        legal = [(q, t) for q, (t, m) in forced.items() if P.legal(t)]
        if forced and not legal:
            status = "STUCK"; break
        placed = 0
        for q, t in legal:
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); rnd[q] = r; geo[q] = t; placed += 1
        fmids = [m for _, m in forced.values()]
        made = []
        for e in multi:                                    # innermost first (frontier order)
            if len(P.tris) - n0 >= N_ADD:
                break
            m = mid(e)
            if math.isinf(h):
                if forced or made:
                    break
            else:
                if any(abs(m - f) < h * S for f in fmids) or any(abs(m - g) < h * S for g in made):
                    continue
            ek = frozenset((L.key(e[0]), L.key(e[1])))
            if len(P.edges.get(ek, [])) != 1:
                continue                                   # filled earlier this round
            cs = sorted(P.candidates(*e[:3]), key=lambda u: sorted(L.canon(u)[1]))
            if len(cs) < 2:
                continue                                   # now forced (or dead): leave it to the next round's scan
            t = rng.choice(cs)
            if not P.legal(t):
                continue
            P.add(t); rnd[L.canon(t)] = r; geo[L.canon(t)] = t; made.append(m)
            guesses.append(dict(round=r, x=m.real / S, y=m.imag / S))
        per_round.append(len(made))
    return dict(P=P, rnd=rnd, geo=geo, status=status, jam=jam, rounds=r, guesses=guesses, per_round=per_round)


def sector_spread(hh):
    band = [(cmath.phase(cen(hh["geo"][q])), x) for q, x in hh["rnd"].items()
            if BAND[0] * S <= abs(cen(hh["geo"][q])) <= BAND[1] * S]
    secs = [[] for _ in range(SECTORS)]
    for a, x in band:
        secs[int(((a % (2 * math.pi)) / (2 * math.pi)) * SECTORS) % SECTORS].append(x)
    if any(not s for s in secs):
        return None, None
    med = lambda v: sorted(v)[len(v) // 2] if len(v) % 2 else (sorted(v)[len(v) // 2 - 1] + sorted(v)[len(v) // 2]) / 2
    ms = [med(s) for s in secs]; overall = med([x for _, x in band])
    return (max(ms) - min(ms)) / overall, ms


def task(args):
    h, k = args; t0 = time.time()
    hh = grow(h, k)
    # jammed runs count only if every sector already had tiles in the band (sector_spread returns None otherwise)
    ss, ms = (None, None) if hh["status"] not in ("ok", "JAM") else sector_spread(hh)
    out = dict(h=None if math.isinf(h) else h, run=k, status=hh["status"], rounds=hh["rounds"], tiles=len(hh["rnd"]),
               n_guesses=len(hh["guesses"]), max_simultaneous=max(hh["per_round"], default=0),
               jam=[hh["jam"].real / S, hh["jam"].imag / S] if hh["jam"] is not None else None, SS=ss, sector_medians=ms,
               guesses=hh["guesses"], seconds=round(time.time() - t0))
    if math.isinf(h):                                      # H0: identical to continuation_choices FAST
        CC.N_ADD = N_ADD
        P2, rnd2, r2, *_ = CC.grow("FAST", random.Random(SEED0 + k))
        out["H0_identical"] = (rnd2 == hh["rnd"] and r2 == hh["rounds"])
    return out


def summary():
    import numpy as np
    R = [json.loads(l) for l in open(OUT)]
    key = lambda h: math.inf if h is None else h
    lines = []
    med = {}
    for h in HORIZONS:
        rs = sorted([r for r in R if key(r["h"]) == h], key=lambda r: r["run"])
        ss = [r["SS"] for r in rs if r["SS"] is not None]
        med[h] = float(np.median(ss)) if ss else float("nan")
        j = [r for r in rs if r["status"] == "JAM"]
        lines.append(f"h = {h}: jams {len(j)}/{len(rs)}; statuses {[r['status'] for r in rs]}; median SS {med[h]:.2f} "
                     f"(n = {len(ss)}; {[round(x, 2) for x in ss]}); guesses {[r['n_guesses'] for r in rs]}; "
                     f"max simultaneous guesses {[r['max_simultaneous'] for r in rs]}; rounds {[r['rounds'] for r in rs]}"
                     + (f"; jam radii {[round(abs(complex(*r['jam'])), 1) for r in j]}" if j else ""))
    inf_runs = [r for r in R if r["h"] is None]
    h0 = all(r.get("H0_identical") for r in inf_runs) and all(r["status"] == "ok" for r in inf_runs)
    h1 = med[2] < 0.5 * med[math.inf]
    rs05 = [r for r in R if r["h"] == 0.5]
    h2 = sum(r["status"] == "JAM" for r in rs05) >= len(rs05) / 2
    sweet = [h for h in HORIZONS if not math.isinf(h) and h <= 4
             and all(r["status"] == "ok" for r in R if r["h"] == h) and med[h] < 0.5 * med[math.inf]]
    lines += [f"  H0: {'PASS' if h0 else 'FAIL'}  h = inf reproduces the patient scheduler exactly and never jams",
              f"  H1: {'HELD  ' if h1 else 'FAILED'}  median SS at h = 2 {med[2]:.2f} vs h = inf {med[math.inf]:.2f} (need < half)",
              f"  H2: {'HELD  ' if h2 else 'FAILED'}  jams at h = 0.5: {sum(r['status'] == 'JAM' for r in rs05)}/{len(rs05)} (need >= half)",
              f"  H3: {'HELD  ' if sweet else 'FAILED'}  sweet-spot horizons (h <= 4, 0 jams, SS < half of h = inf): {sweet}"]
    print("\n".join(lines))
    open(os.path.join(RES, "local_deciders_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = {(json.loads(l)["h"], json.loads(l)["run"]) for l in open(OUT)} if os.path.exists(OUT) else set()
    todo = [(h, k) for h in HORIZONS for k in range(RUNS) if ((None if math.isinf(h) else h), k) not in done]
    with Pool(4, maxtasksperchild=1) as p:
        for res in p.imap_unordered(task, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"h {res['h']} run {res['run']}: {res['status']}, {res['rounds']} rounds, {res['n_guesses']} guesses, "
                  f"SS {res['SS']}, {res['seconds']} s", flush=True)
    summary()
