#!/usr/bin/env python3
"""
worldline_body.py -- does a persisting body (a worldline stripe) make a field of time around it? (PREREGISTRATION.md,
frozen before this file.) Decapod worlds (no guesses, fully repeatable). Arms: CONTROL, QUIET (stripe throttled to 0.25),
FULL (stripe pre-laid from CONTROL). Delay of the arriving now beside the stripe and on the far side.
`python3 worldline_body.py` runs everything; results/ holds runs.jsonl and the report.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "decapod_seed"))
import decapod_seed as D
L, S = D.L, D.S
N_ADD, N_CTRL, P_QUIET, SEED0 = 2000, 3500, 0.25, 20261060
THETAS = [10, 130, 250]
RHOS, DS = [5, 6, 7], [1, 2, 3, 4, 6]
HALF_W, R_MIN, STALL = 0.75, 3.0, 50000
OFF = (0.0123 + 0.0071j) * S
RES = os.path.join(HERE, "results")


def in_stripe(z, th):
    w = z * cmath.exp(-1j * math.radians(th))
    return abs(w.imag) <= HALF_W * S and w.real >= R_MIN * S


def grow(ring, n_add, th=None, quiet=False, rng_seed=0, prelaid=()):
    rng = random.Random(rng_seed)
    P = L.Patch(list(ring) + list(prelaid)); n0 = len(P.tris)
    rnd = {D.dkey(t): 0 for t in list(ring) + list(prelaid)}; geo = {D.dkey(t): t for t in list(ring) + list(prelaid)}
    r = 0; guesses = 0; idle = 0; status = "ok"
    while len(P.tris) - n0 < n_add:
        r += 1
        if r > STALL:
            status = "STALL"; break
        fr = [e for e in P.frontier() if abs((e[0] + e[1]) / 2) > D.APO + 1e-6]
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                status = "JAM"; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), (cs[0], (e[0] + e[1]) / 2))
        if status == "JAM":
            break
        legal = [(q, t, m) for q, (t, m) in forced.items() if P.legal(t)]
        if forced and not legal:
            status = "STUCK"; break
        placed = 0
        for q, t, m in legal:
            if len(P.tris) - n0 >= n_add:
                break
            if quiet and in_stripe(m, th) and rng.random() >= P_QUIET:
                continue
            if P.legal(t):
                P.add(t); rnd[q] = r; geo[q] = t; placed += 1
        if placed == 0:
            if forced:
                idle += 1; continue
            guesses += 1                                   # should never happen in a decapod world (W0)
            cs = sorted(D.candidates(P, *fr[0][:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
            t = rng.choice(cs); P.add(t); rnd[D.dkey(t)] = r; geo[D.dkey(t)] = t
    return dict(rnd=rnd, geo=geo, status=status, rounds=r, guesses=guesses, idle=idle)


def points(th):
    out = {"side": [], "far": []}
    for rho in RHOS:
        for d in DS:
            for sgn in (-1, 1):
                a = math.radians(th) + sgn * d / rho
                out["side"].append((d, rho, rho * S * cmath.exp(1j * a) + OFF))
                a2 = math.radians(th + 180) + sgn * d / rho
                out["far"].append((d, rho, rho * S * cmath.exp(1j * a2) + OFF))
    return out


def arrival(h, p):
    for q, t in h["geo"].items():
        if abs(D.cen(t) - p) < 1.2 * S and L.inside(p, *t[1:]):
            return h["rnd"][q], q
    return None, None


def pick_seeds():
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
    good = []
    for x in seeds:
        rs = [r for r in R if r["seed"] == x["seed"]]
        if x["kind"] == "DECAPOD" and len(rs) == 3 and all(r["status"] == "ok" and not r["guesses"] for r in rs):
            good.append(x)
    good = sorted(good, key=lambda x: x["seed"])[:6]
    return [(x["seed"], [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]) for x in good]


def control_task(args):
    s, ring = args
    return s, grow(ring, N_CTRL)


def arm_task(args):
    s, ring, bi, th, arm, ctrl_stripe, ctrl_keys = args; t0 = time.time()
    if arm == "QUIET":
        h = grow(ring, N_ADD, th=th, quiet=True, rng_seed=SEED0 + 10 * s + bi)
    else:
        h = grow(ring, N_ADD, prelaid=ctrl_stripe)
    pts = points(th)
    arr = {g: [(d, rho, *arrival(h, p)) for d, rho, p in ps] for g, ps in pts.items()}
    return dict(seed=s, body=bi, theta=th, arm=arm, status=h["status"], rounds=h["rounds"], guesses=h["guesses"],
                idle=h["idle"], all_in_control=set(h["rnd"]) <= ctrl_keys, n_prelaid=len(ctrl_stripe),
                arrivals={g: [[d, rho, T, None if q is None else str(q)] for d, rho, T, q in v] for g, v in arr.items()},
                seconds=round(time.time() - t0))


def main():
    os.makedirs(RES, exist_ok=True)
    worlds = pick_seeds()
    print(f"decapod worlds: {[s for s, _ in worlds]}", flush=True)
    with Pool(4) as p:
        ctrl = dict(p.map(control_task, worlds))
    for s in ctrl:
        print(f"control seed {s}: {ctrl[s]['status']}, {ctrl[s]['rounds']} rounds, {ctrl[s]['guesses']} guesses", flush=True)
    tasks = []
    for s, ring in worlds:
        rk = {D.dkey(t) for t in ring}
        for bi, th in enumerate(THETAS):
            stripe = [t for q, t in ctrl[s]["geo"].items() if q not in rk and in_stripe(D.cen(t), th)]
            for arm in ("QUIET", "FULL"):
                tasks.append((s, ring, bi, th, arm, stripe, set(ctrl[s]["rnd"])))
    out = []
    with Pool(4, maxtasksperchild=2) as p:
        for res in p.imap_unordered(arm_task, tasks):
            out.append(res)
            print(f"seed {res['seed']} body {res['body']} {res['arm']}: {res['status']}, {res['rounds']} rounds, "
                  f"{res['guesses']} guesses, idle {res['idle']}, {res['seconds']} s", flush=True)
    ctrl_arr = {}
    for s, _ in worlds:
        for th in THETAS:
            ctrl_arr[(s, th)] = {g: [(d, rho, *arrival(ctrl[s], p)) for d, rho, p in ps] for g, ps in points(th).items()}
    with open(os.path.join(RES, "runs.jsonl"), "w") as f:
        for r in sorted(out, key=lambda r: (r["seed"], r["body"], r["arm"])):
            r["control_arrivals"] = {g: [[d, rho, T, None if q is None else str(q)] for d, rho, T, q in v]
                                     for g, v in ctrl_arr[(r["seed"], r["theta"])].items()}
            f.write(json.dumps(r) + "\n")
    json.dump({str(s): dict(status=ctrl[s]["status"], rounds=ctrl[s]["rounds"], guesses=ctrl[s]["guesses"]) for s in ctrl},
              open(os.path.join(RES, "controls.json"), "w"))
    report()


def report():
    import numpy as np
    R = [json.loads(l) for l in open(os.path.join(RES, "runs.jsonl"))]
    C = json.load(open(os.path.join(RES, "controls.json")))
    w0 = all(c["status"] == "ok" and c["guesses"] == 0 for c in C.values())
    w0 &= all(r["status"] == "ok" and r["guesses"] == 0 and r["all_in_control"] for r in R)
    prof = {}
    for r in R:
        dl = {}; far = []
        for (d, rho, T, q), (d2, rho2, Tc, qc) in zip(r["arrivals"]["side"], r["control_arrivals"]["side"]):
            if T is None or Tc is None:
                w0 = False; continue
            if T == 0 and r["arm"] == "FULL":
                continue                                   # covered by a pre-laid stripe tile (not expected)
            dl.setdefault(d, []).append(T - Tc)
        for (d, rho, T, q), (d2, rho2, Tc, qc) in zip(r["arrivals"]["far"], r["control_arrivals"]["far"]):
            if T is None or Tc is None:
                w0 = False; continue
            far.append(T - Tc)
        byrho = {}
        for (d, rho, T, q), (d2, rho2, Tc, qc) in zip(r["arrivals"]["side"], r["control_arrivals"]["side"]):
            if T is not None and Tc is not None and d <= 2:
                byrho.setdefault(rho, []).append(T - Tc)
        prof[(r["seed"], r["body"], r["arm"])] = dict(D={d: float(np.mean(v)) for d, v in dl.items()}, far=float(np.mean(far)),
                                                      rho={k: float(np.mean(v)) for k, v in byrho.items()},
                                                      rounds=r["rounds"], idle=r["idle"])
    lines = [f"controls: {C}"]
    res = {}
    for arm in ("QUIET", "FULL"):
        ps = [v for (s, b, a), v in prof.items() if a == arm]
        near = [(p["D"][1] + p["D"][2]) / 2 for p in ps]
        res[arm] = (ps, near)
        lines.append(f"{arm}: {len(ps)} bodies; mean delay profile Delta(d): "
                     + ", ".join(f"d={d}: {np.mean([p['D'][d] for p in ps]):+.2f}" for d in DS)
                     + f"; far {np.mean([p['far'] for p in ps]):+.2f}")
        lines.append(f"    near delay (d = 1-2) per body: {[round(x, 1) for x in near]}")
        lines.append(f"    delay (d <= 2) by radius rho: " + ", ".join(f"{rho}: {np.mean([p['rho'][rho] for p in ps]):+.2f}" for rho in RHOS))
        lines.append(f"    far delay per body: {[round(p['far'], 1) for p in ps]}")
        if arm == "QUIET":
            lines.append(f"    rounds {[p['rounds'] for p in ps]}; idle {[p['idle'] for p in ps]}")
    q, qn = res["QUIET"]; f, fn = res["FULL"]
    w1 = sum(x > 0 for x in qn) >= 0.8 * len(qn)
    w2a = sum(p["D"][1] > p["D"][6] for p in q) >= 0.7 * len(q)
    w2b = float(np.median([abs(p["far"]) for p in q])) <= 1
    w3 = sum(x < 0 for x in fn) >= 0.8 * len(fn)
    lines += [f"  W0: {'PASS' if w0 else 'FAIL'}  no guesses/jams; every tile in CONTROL's tiling; every sample point covered",
              f"  W1: {'HELD  ' if w1 else 'FAILED'}  QUIET near delay > 0 in {sum(x > 0 for x in qn)}/{len(qn)} (need >= 80%)",
              f"  W2: {'HELD  ' if (w2a and w2b) else 'FAILED'}  QUIET Delta(1) > Delta(6) in {sum(p['D'][1] > p['D'][6] for p in q)}/{len(q)} "
              f"(need >= 70%); median |far| {float(np.median([abs(p['far']) for p in q])):.2f} (need <= 1)",
              f"  W3: {'HELD  ' if w3 else 'FAILED'}  FULL near delay < 0 in {sum(x < 0 for x in fn)}/{len(fn)} (need >= 80%)"]
    print("\n".join(lines))
    open(os.path.join(RES, "worldline_body_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if "--report" in sys.argv:
        report(); sys.exit(0)
    main()
