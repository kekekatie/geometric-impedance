#!/usr/bin/env python3
"""
continuation_choices.py -- does quietness only prolong the opportunity, or change the choices?
(PREREGISTRATION.md, frozen before this file, incl. its logged change: the IDLE exact-replay arm.)

WAIT-scheduler ring-of-Gromits growth (guess only when NO forced move exists anywhere). Arms FAST / HALF / SLOW,
plus IDLE = FAST replayed with round r -> 4r. Probes have an explicit target (17 sample points); at each round from
arrival to coverage, completions of the target from the current snapshot are sampled (16 attempts) and counted
as genuine if they agree with the forcing closure (the patch just before the next guess).
Incremental: results/runs.jsonl; `--summary` evaluates Z1-Z3, P1-P4.
"""
from __future__ import annotations
import os, sys, json, math, random, time, bisect
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "soft_zone"))
import soft_zone as SZ            # installs the corrected vertex check
L = SZ.L
S = L.SCALE_LEN
N_ADD, RUNS, SEED0, P_SLOW, K_IDLE = 1000, 8, 20261010, 0.25, 4
ARMS = ["FAST", "HALF", "SLOW", "IDLE"]
PROBES, ATT, REACH, LOCAL, CLOCK_R, MAX_ADD, STALL = 8, 16, 1.8 * S, 4.0 * S, 2.0 * S, 80, 20000
OFF = (0.0123 + 0.0071j) * S
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "runs.jsonl")
half = lambda z: "slow" if z.real < 0 else "fast"
cen = SZ.centroid


# ------------------------------------------------------------------ growth (WAIT scheduler)
def grow(arm, rng):
    seed = L.seed_patch(0j, 3 * S)
    P = L.Patch(seed); n0 = len(P.tris)
    rnd = {L.canon(t): 0 for t in seed}; r = 0; guesses = []; idle = 0; placed_in = {"slow": 0, "fast": 0}
    while len(P.tris) - n0 < N_ADD:
        r += 1
        if r > STALL:
            return P, rnd, r, guesses, idle, placed_in, "STALL"
        fr = P.frontier(); forced = {}
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                return P, rnd, r, guesses, idle, placed_in, "JAM"
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), (cs[0], half((e[0] + e[1]) / 2)))
        legal = [(k, t, h) for k, (t, h) in forced.items() if P.legal(t)]
        if forced and not legal:
            return P, rnd, r, guesses, idle, placed_in, "STUCK"
        placed = 0
        for k, t, h in legal:
            if len(P.tris) - n0 >= N_ADD:
                break
            p = 1.0 if arm == "FAST" else (P_SLOW if (arm == "SLOW" or h == "slow") else 1.0)
            if p < 1.0 and rng.random() >= p:
                continue
            if P.legal(t):
                P.add(t); rnd[k] = r; placed += 1; placed_in[h] += 1
        if placed == 0:
            if forced:
                idle += 1; continue                      # patient: forced moves are waiting, the round passes
            cs = P.candidates(*fr[0][:3])
            t = rng.choice(sorted(cs, key=lambda u: sorted(L.canon(u)[1])))
            P.add(t); rnd[L.canon(t)] = r; guesses.append(r); placed_in[half((fr[0][0] + fr[0][1]) / 2)] += 1
    return P, rnd, r, guesses, idle, placed_in, "ok"


# ------------------------------------------------------------------ probes
def sample_points(c):
    pts = [c + OFF]
    pts += [c + OFF + 0.4 * S * complex(math.cos(2 * math.pi * j / 6 + 0.1), math.sin(2 * math.pi * j / 6 + 0.1)) for j in range(6)]
    pts += [c + OFF + 0.8 * S * complex(math.cos(2 * math.pi * j / 10 + 0.05), math.sin(2 * math.pi * j / 10 + 0.05)) for j in range(10)]
    return pts


def cover_of(tiles, pts):
    out = [None] * len(pts)
    for t in tiles:
        for i, p in enumerate(pts):
            if out[i] is None and L.inside(p, *t[1:]):
                out[i] = t
    return out


def complete(base, c, pts, rng):
    """Add tiles (centroids within REACH of c) until all sample points are covered; forced-first, else random at
    the nearest edge with options. Returns (signature, laid) or None (dead end / not covered / look-ahead fails)."""
    Q = L.Patch(base); cov = cover_of(base, pts); laid = []
    for _ in range(MAX_ADD):
        if all(x is not None for x in cov):
            break
        edges = sorted((e for e in Q.frontier() if abs((e[0] + e[1]) / 2 - c) <= REACH),
                       key=lambda e: (abs((e[0] + e[1]) / 2 - c), L.key((e[0] + e[1]) / 2)))
        forced = None; first = None
        for e in edges:
            cs = [t for t in Q.candidates(*e[:3]) if abs(cen(t) - c) <= REACH]
            if len(cs) == 1:
                forced = cs[0]; break
            if cs and first is None:
                first = cs
        if forced is None and first is None:
            return None
        t = forced if forced is not None else rng.choice(sorted(first, key=lambda u: sorted(L.canon(u)[1])))
        Q.add(t); laid.append(t)
        for i, p in enumerate(pts):
            if cov[i] is None and L.inside(p, *t[1:]):
                cov[i] = t
    if any(x is None for x in cov):
        return None
    for e in Q.frontier():
        if abs((e[0] + e[1]) / 2 - c) <= REACH and not Q.candidates(*e[:3]):
            return None
    return tuple(L.canon(x) for x in cov), laid


def agrees(sig, laid, clos_tiles, clos_cov):
    for s, ct in zip(sig, clos_cov):
        if ct is not None and s != L.canon(ct):
            return False
    ck = {L.canon(t) for t in clos_tiles}
    new = [t for t in laid if L.canon(t) not in ck]
    for t in new:
        if any(L.inside(cen(t), *u[1:]) for u in clos_tiles):
            return False
        if any(L.inside(cen(u), *t[1:]) for u in clos_tiles if L.canon(u) not in {L.canon(x) for x in new}):
            return False
    return True


def measure(tiles, rnd, guesses, rounds, k, probe_id, c):
    """All probe measures for one growth history (rnd/guesses on that history's clock)."""
    pts = sample_points(c)
    near = [t for t in tiles if abs(cen(t) - c) <= LOCAL]
    cov_final = cover_of(near, pts)
    assert all(x is not None for x in cov_final)
    actual = tuple(L.canon(x) for x in cov_final)
    a = min(rnd[L.canon(t)] for t in near if abs(cen(t) - c) <= REACH)
    v = max(rnd[L.canon(x)] for x in cov_final)
    gs = sorted(guesses)

    def closure(r):
        i = bisect.bisect_right(gs, r)
        g = gs[i] if i < len(gs) else math.inf
        return [t for t in near if rnd[L.canon(t)] < g]
    d = next(r for r in range(0, v + 1) if all(x is not None for x in cover_of(closure(r), pts)))
    memo = {}; genuine, apparent = {}, {}
    for r in range(a, v):
        snap = [t for t in near if rnd[L.canon(t)] <= r]
        if len(snap) not in memo:
            clos = closure(r); clos_cov = cover_of(clos, pts)
            sigs, gen = set(), set()
            for att in range(ATT):
                res = complete(snap, c, pts, random.Random(((SEED0 + k) * 10000 + probe_id) * 1000000 + len(snap) * 100 + att))
                if res is None:
                    continue
                sig, laid = res; sigs.add(sig)
                if agrees(sig, laid, clos, clos_cov):
                    gen.add(sig)
            memo[len(snap)] = (len(sigs), len(gen))
        apparent[r], genuine[r] = memo[len(snap)]
    T_U = max(0, d - a); T_D = v - max(a, d)
    choices = max((genuine[r] for r in range(a, min(d, v))), default=1) if T_U > 0 else 1
    app = max((apparent[r] for r in range(max(a, d), v)), default=0)
    clock = lambda lo, hi: sum(1 for t in near if abs(cen(t) - c) <= CLOCK_R and lo < rnd[L.canon(t)] <= hi)
    # Z2: the past is fixed -- remove the target's tiles from the FINAL patch and complete again
    removed = {L.canon(x) for x in cov_final} | {L.canon(t) for t in near if abs(cen(t) - c) <= 0.8 * S}
    base = [t for t in near if L.canon(t) not in removed]
    z2 = [complete(base, c, pts, random.Random(((SEED0 + k) * 10000 + probe_id) * 1000 + att)) for att in range(ATT)]
    z2s = [x[0] for x in z2 if x is not None]
    return dict(a=a, d=d, v=v, T_U=T_U, T_D=T_D, choices=choices, apparent_D=app,
                clock_U=clock(a, max(a, d)), clock_D=clock(max(a, d), v),
                z2_success=len(z2s), z2_unique=bool(z2s) and all(s == actual for s in z2s))


def task(args):
    arm, k = args; t0 = time.time()
    base_arm = "FAST" if arm == "IDLE" else arm
    P, rnd, rounds, guesses, idle, placed_in, status = grow(base_arm, random.Random(SEED0 + k))
    out = dict(arm=arm, run=k, status=status, rounds=rounds, guesses=len(guesses), idle=idle, placed=placed_in)
    if status != "ok":
        out["seconds"] = round(time.time() - t0); return out
    if arm == "IDLE":
        rnd = {q: K_IDLE * r for q, r in rnd.items()}; guesses = [K_IDLE * g for g in guesses]
        rounds = K_IDLE * rounds; out.update(rounds=rounds, idle=idle + (K_IDLE - 1) * (rounds // K_IDLE))
    tiles = list(P.tris); mids = [(e[0] + e[1]) / 2 for e in P.frontier()]
    cands = sorted({cen(t) for t in tiles}, key=lambda z: (z.real, z.imag))
    cands = [c for c in cands if abs(c) >= 4.5 * S and abs(c.real) >= 1.5 * S and min(abs(c - m) for m in mids) >= 3 * S]
    prng = random.Random(SEED0 + k + 999); prng.shuffle(cands)   # arm-independent stream: IDLE picks FAST's probes
    probes = []
    for h in ("slow", "fast"):
        chosen = []
        for c in cands:
            if half(c) == h and all(abs(c - q) > 2.4 * S for q in chosen):
                chosen.append(c)
            if len(chosen) == PROBES:
                break
        for c in chosen:
            m = measure(tiles, rnd, guesses, rounds, k, len(probes), c)
            m.update(half=h, x=round(c.real / S, 4), y=round(c.imag / S, 4)); probes.append(m)
    out.update(probes=probes, seconds=round(time.time() - t0))
    return out


# ------------------------------------------------------------------ summary
def summary():
    import numpy as np
    R = [json.loads(l) for l in open(OUT)]
    by = {a: sorted([r for r in R if r["arm"] == a], key=lambda r: r["run"]) for a in ARMS}
    g = np.random.default_rng(2031); B = 10000
    lines = []
    for a in ARMS:
        rs = by[a]
        lines.append(f"{a}: {len(rs)} runs, statuses {[r['status'] for r in rs]}, rounds {[r['rounds'] for r in rs]}, "
                     f"guesses {[r['guesses'] for r in rs]}, idle {[r['idle'] for r in rs]}")
        if a != "IDLE":
            hd = {h: np.mean([r["placed"][h] / r["rounds"] for r in rs]) for h in ("slow", "fast")}
            lines.append(f"    happening density (tiles/round): left {hd['slow']:.2f}, right {hd['fast']:.2f}")
        for h in ("slow", "fast"):
            ps = [p for r in rs for p in r.get("probes", []) if p["half"] == h]
            if not ps:
                continue
            f = lambda key: np.mean([p[key] for p in ps])
            lines.append(f"    {h:<4}: {len(ps)} probes; T_U>0 in {np.mean([p['T_U'] > 0 for p in ps]):.2f}; mean T_U {f('T_U'):.1f}, "
                         f"T_D {f('T_D'):.1f}; clock_U {f('clock_U'):.1f}, clock_D {f('clock_D'):.1f}; "
                         f"choices (T_U>0) {np.mean([p['choices'] for p in ps if p['T_U'] > 0]) if any(p['T_U'] > 0 for p in ps) else float('nan'):.2f}; "
                         f"apparent choices in D {f('apparent_D'):.2f}; Z2 unique {np.mean([p['z2_unique'] for p in ps]):.2f}")

    def probes_of(runs, h=None, cond=None):
        return [[p for p in r.get("probes", []) if (h is None or p["half"] == h) and (cond is None or cond(p))] for r in runs]

    def ratio_ci(num_runs, den_runs, key, paired):
        """ratio of pooled means; bootstrap over runs (paired: same run indices for num and den)."""
        def rat(nr, dr):
            n = [p[key] for r in nr for p in r]; d = [p[key] for r in dr for p in r]
            return (np.mean(n) / np.mean(d)) if n and d and np.mean(d) > 0 else float("nan")
        est = rat(num_runs, den_runs); bs = []
        for _ in range(B):
            i = g.integers(0, len(num_runs), len(num_runs))
            j = i if paired else g.integers(0, len(den_runs), len(den_runs))
            bs.append(rat([num_runs[x] for x in i], [den_runs[x] for x in j]))
        bs = np.array(bs); bs = bs[~np.isnan(bs)]
        return est, (np.percentile(bs, 2.5), np.percentile(bs, 97.5)) if len(bs) else (float("nan"), float("nan"))

    allr = [r for a in ARMS for r in by[a]]
    z1 = all(r["status"] == "ok" for r in allr)
    ps_all = [p for r in allr for p in r.get("probes", [])]
    z2 = np.mean([p["z2_unique"] for p in ps_all]) >= 0.99 if ps_all else False
    z3 = True
    for rf, ri in zip(by["FAST"], by["IDLE"]):
        for pf, pi in zip(rf.get("probes", []), ri.get("probes", [])):
            same = (pf["x"], pf["y"], pf["choices"], pf["apparent_D"]) == (pi["x"], pi["y"], pi["choices"], pi["apparent_D"])
            scaled = all(pi[q] == K_IDLE * pf[q] for q in ("a", "d", "v", "T_U", "T_D"))
            z3 &= same and scaled
    lines += [f"  Z1: {'PASS' if z1 else 'FAIL'}  no JAM/STUCK/STALL in any arm",
              f"  Z2: {'PASS' if z2 else 'FAIL'}  past is fixed: unique completion in {np.mean([p['z2_unique'] for p in ps_all]):.3f} of {len(ps_all)} probes (need >= 0.99)",
              f"  Z3: {'PASS' if z3 else 'FAIL'}  IDLE reproduces FAST exactly (choices identical, a/d/v x{K_IDLE})"]
    hq, hb = probes_of(by["HALF"], "slow"), probes_of(by["HALF"], "fast")
    est1, ci1 = ratio_ci(hq, hb, "T_D", True)
    wins = sum(1 for q, b in zip(hq, hb) if q and b and np.mean([p["T_D"] for p in q]) > np.mean([p["T_D"] for p in b]))
    p1 = est1 >= 1.5 and wins >= 7
    est2, ci2 = ratio_ci(hq, hb, "T_U", True)
    p2 = 0.67 <= ci2[0] and ci2[1] <= 1.5
    tq, tb = probes_of(by["HALF"], "slow", lambda p: p["T_U"] > 0), probes_of(by["HALF"], "fast", lambda p: p["T_U"] > 0)
    nq, nb = sum(map(len, tq)), sum(map(len, tb))
    est3, ci3 = ratio_ci(tq, tb, "choices", True)
    p3 = "NOT TESTABLE" if min(nq, nb) < 10 else ("HELD  " if 0.75 <= ci3[0] and ci3[1] <= 1.33 else "FAILED")
    est4a, ci4a = ratio_ci(probes_of(by["SLOW"]), probes_of(by["FAST"]), "T_D", False)
    ts, ti = probes_of(by["SLOW"], None, lambda p: p["T_U"] > 0), probes_of(by["IDLE"], None, lambda p: p["T_U"] > 0)
    ns, ni = sum(map(len, ts)), sum(map(len, ti))
    est4b, ci4b = ratio_ci(ts, ti, "choices", False)
    p4 = "NOT TESTABLE" if min(ns, ni) < 10 else ("HELD  " if est4a >= 1.5 and 0.75 <= ci4b[0] and ci4b[1] <= 1.33 else "FAILED")
    estx, cix = ratio_ci(tq, ti, "choices", False)
    lines += [f"  P1: {'HELD  ' if p1 else 'FAILED'}  HALF quiet/busy T_D ratio {est1:.2f} (95% {ci1[0]:.2f}-{ci1[1]:.2f}; need >= 1.5), quiet > busy in {wins}/{len(hq)} runs (need >= 7)",
              f"  P2: {'HELD  ' if p2 else 'FAILED'}  HALF quiet/busy T_U ratio {est2:.2f} (95% {ci2[0]:.2f}-{ci2[1]:.2f}; need within 0.67-1.5)",
              f"  P3: {p3}  HALF quiet/busy choices ratio {est3:.2f} (95% {ci3[0]:.2f}-{ci3[1]:.2f}; need within 0.75-1.33); n(T_U>0) = {nq}, {nb}",
              f"  P4: {p4}  SLOW/FAST T_D ratio {est4a:.2f} (95% {ci4a[0]:.2f}-{ci4a[1]:.2f}; need >= 1.5); SLOW/IDLE choices ratio {est4b:.2f} "
              f"(95% {ci4b[0]:.2f}-{ci4b[1]:.2f}; need within 0.75-1.33); n(T_U>0) = {ns}, {ni}",
              f"  (reported) HALF-quiet / IDLE choices ratio {estx:.2f} (95% {cix[0]:.2f}-{cix[1]:.2f})"]
    print("\n".join(lines))
    open(os.path.join(RES, "continuation_choices_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = {(json.loads(l)["arm"], json.loads(l)["run"]) for l in open(OUT)} if os.path.exists(OUT) else set()
    todo = [(a, k) for k in range(RUNS) for a in ARMS if (a, k) not in done]
    with Pool(4, maxtasksperchild=1) as p:
        for res in p.imap_unordered(task, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"{res['arm']} run {res['run']}: {res['status']}, {res['rounds']} rounds, {res['guesses']} guesses, "
                  f"{len(res.get('probes', []))} probes, {res['seconds']} s", flush=True)
    summary()
