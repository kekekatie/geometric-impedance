#!/usr/bin/env python3
"""
astra_checks.py -- EXPLORATORY (post hoc) checks of three issues Astra raised about quiet_lasts_longer.
  A. Uncertainty by growth run, not by probe (paired quiet-vs-busy per run).
  B. The refill counts "enough area laid" as complete; near an open front, a "different" refill might add area
     OUTSIDE the removed footprint. Re-test every probe, splitting alternatives into SAME-FOOTPRINT
     rearrangements and OTHER (different footprint) ones. Also split lifetime into construction
     (first tile -> disc complete) and after completion.
  C. The scheduler guesses whenever nothing was placed, even when forced moves were only throttled. Count such
     guesses, and regrow every seed with a WAIT scheduler (no guess while forced moves are pending).
Growth is deterministic per seed (checked: identical under different PYTHONHASHSEED values).
"""
from __future__ import annotations
import os, sys, json, random, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import quiet_lasts_longer as Q
HD, SZ, L = Q.HD, Q.SZ, Q.L
S, RHO = Q.S, Q.RHO
RES = Q.RES


# ------------------------------------------------------------------ A
def check_a():
    R = [json.loads(l) for l in open(Q.OUT)]
    ok = [r for r in R if r["status"] == "ok"]
    rows = []
    for r in ok:
        m = {h: [p for p in r["probes"] if p["half"] == h] for h in ("slow", "fast")}
        rows.append((r["seed"], len(m["slow"]), len(m["fast"]),
                     np.mean([p["L_rounds"] for p in m["slow"]]), np.mean([p["L_rounds"] for p in m["fast"]]),
                     np.mean([p["L_local"] for p in m["slow"]]), np.mean([p["L_local"] for p in m["fast"]])))
    out = ["A. per-run paired summaries (conditional on growth completing: 4 of 12 seeds jammed and give no probes)",
           "   seed  n_quiet n_busy  L_rounds quiet  busy   diff   |  L_local quiet  busy  ratio"]
    for s, nq, nb, rq, rb, lq, lb in rows:
        out.append(f"   {s:>4}  {nq:>7} {nb:>6}  {rq:>13.1f} {rb:>5.1f} {rq - rb:>+6.1f}   |  {lq:>13.1f} {lb:>5.1f} {lq / lb:>6.2f}")
    d = np.array([x[3] - x[4] for x in rows]); rl = np.array([x[3] / x[4] for x in rows])
    dl = np.array([x[5] - x[6] for x in rows]); ll = np.array([x[5] / x[6] for x in rows])
    n = len(d); pos = int((d > 0).sum())
    from math import comb
    sign_p = sum(comb(n, k) for k in range(pos, n + 1)) / 2 ** n
    se = d.std(ddof=1) / np.sqrt(n)
    # exact paired permutation (sign-flip) test over runs
    flips = [np.mean(d * np.array([1 if (i >> j) & 1 else -1 for j in range(n)])) for i in range(2 ** n)]
    perm_p = sum(1 for f in flips if f >= d.mean() - 1e-12) / 2 ** n
    boot = np.random.default_rng(2030)
    bl = [np.mean(ll[boot.integers(0, n, n)]) for _ in range(10000)]
    br = [np.mean(rl[boot.integers(0, n, n)]) for _ in range(10000)]
    out += [f"   runs with quiet > busy (L_rounds): {pos}/{n}; one-sided sign test p = {sign_p:.4f}; "
            f"exact sign-flip permutation p = {perm_p:.4f}",
            f"   mean per-run difference {d.mean():+.1f} rounds (SE {se:.1f}); per-run ratio mean {rl.mean():.2f} "
            f"(bootstrap 95% {np.percentile(br, 2.5):.2f}-{np.percentile(br, 97.5):.2f})",
            f"   L_local per-run ratio mean {ll.mean():.2f} (bootstrap 95% {np.percentile(bl, 2.5):.2f}-{np.percentile(bl, 97.5):.2f}); "
            f"runs with quiet > busy {int((dl > 0).sum())}/{n}",
            "   (meeting the 0.67-1.5 tolerance is not evidence of equality; the interval is what to read)"]
    return out


# ------------------------------------------------------------------ B
def inside_any(p, tris):
    return any(L.inside(p, *t[1:]) for t in tris)


def classify(tiles, rnd, r, c, key):
    snap = [t for t in tiles if rnd[L.canon(t)] <= r]
    removed = [t for t in snap if abs(SZ.centroid(t) - c) <= RHO * S]
    remaining = [t for t in snap if abs(SZ.centroid(t) - c) > RHO * S]
    A = sum(SZ.area(t) for t in removed); orig = {L.canon(t) for t in removed}
    same_fp = other = False
    for a in range(SZ.ATTEMPTS):
        laid, done = SZ.refill(remaining, c, A, random.Random(key * 100 + a))
        if not done or frozenset(L.canon(t) for t in laid) == orig:
            continue
        fp = (all(inside_any(SZ.centroid(t), removed) for t in laid)
              and all(inside_any(SZ.centroid(t), laid) for t in removed)
              and abs(sum(SZ.area(t) for t in laid) - A) < 1e-9)
        same_fp |= fp; other |= not fp
    return same_fp, other


def regrow_probe_task(rec):
    k = rec["seed"]
    P, rnd, rounds, *_ = HD.grow(random.Random(Q.SEED0 + k))
    tiles = list(P.tris); out = []
    for i, p in enumerate(rec["probes"]):
        c = complex(p["x"], p["y"]) * S
        # recover the exact probe centre (x, y were rounded): nearest tile centroid
        c = min((SZ.centroid(t) for t in tiles), key=lambda z: abs(z - c))
        seq = []
        for j, orig_soft in enumerate(p["tests"]):
            r = p["birth"] + j
            sf, ot = classify(tiles, rnd, r, c, key=(Q.SEED0 + k) * 100000 + i * 1000 + r)
            assert bool(orig_soft) == (sf or ot), "re-test does not reproduce the original result"
            seq.append((int(sf), int(ot)))
        out.append(dict(seed=k, half=p["half"], birth=p["birth"], full=p["full"], seq=seq))
    return out


def check_b():
    R = [json.loads(l) for l in open(Q.OUT)]
    ok = [r for r in R if r["status"] == "ok"]
    with Pool(4, maxtasksperchild=1) as pool:
        probes = [p for res in pool.imap(regrow_probe_task, ok) for p in res]
    json.dump(probes, open(os.path.join(RES, "astra_check_b_probes.json"), "w"))
    out = ["B. refill footprint: are 'different' refills rearrangements of the SAME region, or different regions?",
           "   (the re-test reproduced every original soft/hard result exactly)"]
    per_run = collections.defaultdict(dict)
    for h, name in (("slow", "quiet"), ("fast", "busy")):
        ps = [p for p in probes if p["half"] == h]
        cons = [s for p in ps for j, s in enumerate(p["seq"]) if p["birth"] + j < p["full"]]
        after = [s for p in ps for j, s in enumerate(p["seq"]) if p["birth"] + j >= p["full"]]
        def frac(xs, i): return np.mean([x[i] for x in xs]) if xs else float("nan")
        def only_other(xs): return np.mean([x[1] and not x[0] for x in xs]) if xs else float("nan")
        out.append(f"   {name}: during construction {len(cons)} tests: same-footprint alternative {frac(cons, 0):.2f}, "
                   f"only different-footprint alternatives {only_other(cons):.2f}; after completion {len(after)} tests: "
                   f"same-footprint {frac(after, 0):.2f}, only different-footprint {only_other(after):.2f}")
        lc, la, ls = [], [], []
        for p in ps:
            last = max((p["birth"] + j for j, s in enumerate(p["seq"]) if s[0]), default=None)
            ls.append(last - p["birth"] + 1 if last is not None else 0)
            lc.append(p["full"] - p["birth"])
            la.append(max(0, last - p["full"] + 1) if last is not None else 0)
            per_run[p["seed"]].setdefault(h, []).append((ls[-1], lc[-1], la[-1]))
        out.append(f"   {name}: construction interval (first tile -> complete) mean {np.mean(lc):.1f} rounds; "
                   f"strict lifetime (same-footprint only) mean {np.mean(ls):.1f}; flexibility AFTER completion "
                   f"(same-footprint) mean {np.mean(la):.2f} rounds, nonzero in {np.mean([x > 0 for x in la]):.2f} of probes")
    d = [np.mean([x[0] for x in v["slow"]]) - np.mean([x[0] for x in v["fast"]]) for v in per_run.values()]
    da = [np.mean([x[2] for x in v["slow"]]) - np.mean([x[2] for x in v["fast"]]) for v in per_run.values()]
    out.append(f"   per run, strict lifetime quiet - busy: {[round(x, 1) for x in d]} ({sum(x > 0 for x in d)}/{len(d)} positive)")
    out.append(f"   per run, after-completion flexibility quiet - busy: {[round(x, 2) for x in da]}")
    return out


# ------------------------------------------------------------------ C
def grow_counting(rng, wait):
    """HD.grow with one change when wait=True: if forced moves existed this round but the throttle skipped them
    all, NO guess is made (the round simply passes). Also counts guesses made while forced moves were pending."""
    seed = L.seed_patch(0j, 3 * S)
    P = L.Patch(seed); n0 = len(P.tris); r = 0; guesses = pending_guesses = idle = 0
    while len(P.tris) - n0 < HD.N_ADD:
        r += 1
        if r > 5000:
            return "STALL", r, guesses, pending_guesses, idle, None
        fr = P.frontier(); forced = {}
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                return "JAM", r, guesses, pending_guesses, idle, (e[0] + e[1]) / 2
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), (cs[0], HD.half((e[0] + e[1]) / 2)))
        placed = 0
        for k, (t, h) in forced.items():
            if len(P.tris) - n0 >= HD.N_ADD:
                break
            if h == "slow" and rng.random() >= HD.P_SLOW:
                continue
            if P.legal(t):
                P.add(t); placed += 1
        if placed == 0:
            if forced and wait:
                idle += 1; continue
            if forced:
                pending_guesses += 1
            cs = P.candidates(*fr[0][:3])
            P.add(rng.choice(sorted(cs, key=lambda u: sorted(L.canon(u)[1])))); guesses += 1
    return "ok", r, guesses, pending_guesses, idle, None


def c_task(args):
    study, seed0, n_add, k, wait = args
    HD.N_ADD = n_add
    st, r, g, pg, idle, jam = grow_counting(random.Random(seed0 + k), wait)
    return dict(study=study, k=k, wait=wait, status=st, rounds=r, guesses=g, pending_guesses=pg, idle=idle,
                jam=[round(jam.real / S, 2), round(jam.imag / S, 2)] if jam is not None else None)


def check_c():
    tasks = ([("happening_density", 20260930, 500, k, w) for k in range(8) for w in (False, True)]
             + [("quiet_lasts_longer", Q.SEED0, 1000, k, w) for k in range(12) for w in (False, True)])
    with Pool(4, maxtasksperchild=1) as pool:
        res = list(pool.imap(c_task, tasks))
    out = ["C. scheduler: guesses made while throttled forced moves were pending; and a WAIT scheduler"]
    for study in ("happening_density", "quiet_lasts_longer"):
        for w in (False, True):
            rs = [x for x in res if x["study"] == study and x["wait"] == w]
            out.append(f"   {study:<19} {'WAIT    ' if w else 'original'}: jammed {sum(x['status'] == 'JAM' for x in rs)}/{len(rs)}; "
                       f"guesses {[x['guesses'] for x in rs]}; guesses-while-forced-pending {[x['pending_guesses'] for x in rs]}"
                       + (f"; idle rounds {[x['idle'] for x in rs]}" if w else "")
                       + f"; jam spots {[x['jam'] for x in rs if x['jam']]}")
    return out


if __name__ == "__main__":
    which = sys.argv[1:] or ["a", "c", "b"]
    lines = ["EXPLORATORY (post hoc): checks of the issues Astra raised (A: run-level uncertainty; B: refill footprint;",
             "C: scheduler guessing while throttled). Not pre-registered."]
    for w in which:
        lines += {"a": check_a, "b": check_b, "c": check_c}[w]()
        print("\n".join(lines[-12:]), flush=True)
    open(os.path.join(RES, "astra_checks_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
