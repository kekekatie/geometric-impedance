#!/usr/bin/env python3
"""
quiet_lasts_longer.py -- does the now last longer where it is quiet? (PREREGISTRATION.md, frozen before this file.)
Throttled ring-of-Gromits growth (../happening_density, 1,000 half-tiles). Fixed probe spots are followed through
snapshots from birth (the front arrives: first disc tile laid) until they harden; lifetime is counted on the universal clock (rounds) and
on a local clock (tiles laid within 2 edges). Incremental: results/runs.jsonl; `--summary` evaluates Q0-Q3.
"""
from __future__ import annotations
import os, sys, json, random, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "happening_density"))
import happening_density as HD
SZ, L = HD.SZ, HD.L
S, RHO = L.SCALE_LEN, SZ.RHO
HD.N_ADD = 1000
SEED0, TARGET_OK, MAX_SEEDS, PROBES, STOP_HARD, R_LOCAL = 20261001, 8, 24, 8, 4, 2.0
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "runs.jsonl")
half = HD.half


def soft_at(tiles, rnd, r, c, key):
    snap = [t for t in tiles if rnd[L.canon(t)] <= r]
    removed = [t for t in snap if abs(SZ.centroid(t) - c) <= RHO * S]
    remaining = [t for t in snap if abs(SZ.centroid(t) - c) > RHO * S]
    Q = L.Patch(remaining)
    for t in removed:
        assert Q.legal(t), "Z: original refill not legal"
        Q.add(t)
    A = sum(SZ.area(t) for t in removed); orig = {L.canon(t) for t in removed}
    for a in range(SZ.ATTEMPTS):
        laid, done = SZ.refill(remaining, c, A, random.Random(key * 100 + a))
        if done and frozenset(L.canon(t) for t in laid) != orig:
            return True
    return False


def mean_front_radius(P):
    mids = [(e[0] + e[1]) / 2 for e in P.frontier()]
    return {h: sum(abs(m) for m in mids if half(m) == h) / max(1, sum(1 for m in mids if half(m) == h)) / S
            for h in ("slow", "fast")}


def run(k):
    t0 = time.time(); rng = random.Random(SEED0 + k)
    P, rnd, rounds, guesses, placed_in, status = HD.grow(rng)
    out = dict(seed=k, status=status, rounds=rounds, guesses=guesses, placed={h: placed_in[h] for h in ("slow", "fast")})
    if status != "ok":
        fr = P.frontier()
        jam = next(((e[0] + e[1]) / 2 for e in fr if not P.candidates(*e[:3])), None)
        out["jam"] = [jam.real / S, jam.imag / S] if jam is not None else None
        out["seconds"] = round(time.time() - t0)
        return out
    r0 = mean_front_radius(L.Patch(L.seed_patch(0j, 3 * S))); r1 = mean_front_radius(P)
    out["front_speed"] = {h: (r1[h] - r0[h]) / rounds for h in ("slow", "fast")}
    tiles = list(P.tris); mids = [(e[0] + e[1]) / 2 for e in P.frontier()]
    cands = [SZ.centroid(t) for t in tiles]
    cands = [c for c in cands if abs(c) >= 4.5 * S and abs(c.real) >= 1.5 * S
             and min(abs(c - m) for m in mids) >= 3 * S]
    rng.shuffle(cands)
    probes = []
    for h in ("slow", "fast"):
        chosen = []
        for c in cands:
            if half(c) == h and all(abs(c - q) > 2 * RHO * S for q in chosen):
                chosen.append(c)
            if len(chosen) == PROBES:
                break
        for c in chosen:
            disc = [t for t in tiles if abs(SZ.centroid(t) - c) <= RHO * S]
            b = min(rnd[L.canon(t)] for t in disc)          # birth = the front arrives (first disc tile laid)
            full = max(rnd[L.canon(t)] for t in disc)       # disc complete; the stopping rule applies only after this
            results, last_soft, hard_run, r = [], None, 0, b
            while r <= rounds and (r <= full or hard_run < STOP_HARD):
                s = soft_at(tiles, rnd, r, c, key=(SEED0 + k) * 100000 + len(probes) * 1000 + r)
                results.append(int(s))
                if s:
                    last_soft, hard_run = r, 0
                else:
                    hard_run += 1
                r += 1
            L_rounds = (last_soft - b + 1) if last_soft is not None else 0
            L_local = (sum(1 for t in tiles if abs(SZ.centroid(t) - c) <= R_LOCAL * S
                           and b < rnd[L.canon(t)] <= last_soft) if last_soft is not None else 0)
            probes.append(dict(half=h, x=round(c.real / S, 3), y=round(c.imag / S, 3), birth=b, full=full,
                               soft_at_birth=bool(results[0]), L_rounds=L_rounds, L_local=L_local,
                               censored=hard_run < STOP_HARD, tests=results))
    out.update(probes=probes, seconds=round(time.time() - t0))
    return out


def summary():
    import numpy as np
    R = [json.loads(l) for l in open(OUT)]
    ok = [r for r in R if r["status"] == "ok"]; jam = [r for r in R if r["status"] != "ok"]
    lines = [f"seeds used {len(R)}: {len(ok)} completed, {len(jam)} jammed "
             f"(happening-density study: 3/8 jammed)"]
    for r in sorted(jam, key=lambda r: r["seed"]):
        j = r.get("jam")
        lines.append(f"    seed {r['seed']}: jam at round {r['rounds']}"
                     + (f", x = {j[0]:+.2f}, y = {j[1]:+.2f} edges" if j else ""))
    hd = {h: np.mean([r["placed"][h] / r["rounds"] for r in ok]) for h in ("slow", "fast")}
    sp = {h: np.mean([r["front_speed"][h] for r in ok]) for h in ("slow", "fast")}
    lines.append(f"  happening density (tiles/round): quiet {hd['slow']:.2f}, busy {hd['fast']:.2f} (ratio {hd['slow'] / hd['fast']:.2f})")
    lines.append(f"  front speed (edges/round): quiet {sp['slow']:.3f}, busy {sp['fast']:.3f} (ratio {sp['slow'] / sp['fast']:.2f})")
    P = {h: [p for r in ok for p in r["probes"] if p["half"] == h] for h in ("slow", "fast")}
    m = {}
    for h, name in (("slow", "quiet"), ("fast", "busy")):
        ps = P[h]
        lr = [p["L_rounds"] for p in ps]; ll = [p["L_local"] for p in ps]
        m[h] = (np.mean(lr), np.mean(ll))
        lines.append(f"  {name} half: {len(ps)} probes; soft at birth {np.mean([p['soft_at_birth'] for p in ps]):.2f}; "
                     f"ever soft {np.mean([p['L_rounds'] > 0 for p in ps]):.2f}; censored {sum(p['censored'] for p in ps)}; "
                     f"mean L_rounds {m[h][0]:.2f} (median {np.median(lr):.1f}, max {max(lr)}); "
                     f"mean L_local {m[h][1]:.2f} (median {np.median(ll):.1f})")
        lines.append(f"      L_rounds distribution: {sorted(lr)}")
        lines.append(f"      L_rounds x front speed (width in space recovered from time): {m[h][0] * sp[h]:.2f} edges")
    q0 = hd["slow"] < 0.6 * hd["fast"]
    rr = m["slow"][0] / m["fast"][0] if m["fast"][0] else float("inf")
    rl = m["slow"][1] / m["fast"][1] if m["fast"][1] else float("inf")
    q1 = rr >= 1.5; q2 = 0.67 <= rl <= 1.5
    both = np.array([p["L_rounds"] for p in P["slow"]] + [p["L_rounds"] for p in P["fast"]], float)
    n = len(P["slow"]); obs = both[:n].mean() - both[n:].mean(); g = np.random.default_rng(2029); hits = 0
    for _ in range(10000):
        x = g.permutation(both)
        hits += (x[:n].mean() - x[n:].mean()) >= obs
    p = (1 + hits) / 10001
    lines += [f"  Q0 (manipulation): {'PASS' if q0 else 'FAIL'}  ratio {hd['slow'] / hd['fast']:.2f} (need < 0.6)",
              f"  Q1: {'HELD  ' if q1 else 'FAILED'}  lasts longer where quiet (rounds): mean L_rounds ratio {rr:.2f} (need >= 1.5); "
              f"permutation p = {p:.4f} (reported only)",
              f"  Q2: {'HELD  ' if q2 else 'FAILED'}  same on the local clock: mean L_local ratio {rl:.2f} (need 0.67-1.5)",
              f"  Q3: {'HELD  ' if (q1 and q2) else 'FAILED'}  both together (a fixed-width now moving at the local pace)"]
    print("\n".join(lines))
    open(os.path.join(RES, "quiet_lasts_longer_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = [json.loads(l) for l in open(OUT)] if os.path.exists(OUT) else []
    seen = {r["seed"] for r in done}; n_ok = sum(r["status"] == "ok" for r in done)
    k = 0
    with Pool(4, maxtasksperchild=1) as pool:
        while n_ok < TARGET_OK and k < MAX_SEEDS:
            batch = [s for s in range(k, min(MAX_SEEDS, k + 4)) if s not in seen]
            k += 4
            for res in pool.imap(run, batch):
                if n_ok >= TARGET_OK:       # seeds are consumed in order; stop at exactly 8 completed runs
                    break
                with open(OUT, "a") as f:
                    f.write(json.dumps(res) + "\n")
                n_ok += res["status"] == "ok"
                print(f"seed {res['seed']}: {res['status']}, {res['rounds']} rounds, "
                      f"{len(res.get('probes', []))} probes, {res['seconds']} s", flush=True)
    summary()
