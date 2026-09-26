#!/usr/bin/env python3
"""
svc2b.py -- Round 2b (PREREGISTRATION_ROUND2B.md, frozen at 5fe1b74): separate DISCOVERY FAILURE
(a fork never recognised) from PREMATURE EVICTION (evidence discarded before recognition).
Same worlds and streams as round 2 (seeds 10000-10099; stationary T=2000 and T=600); round-2 rules
re-run on identical data, so everything is paired.
"""
from __future__ import annotations
import os, json, time
import numpy as np
from multiprocessing import Pool
import svc as R1
import svc2 as R2

S, K, NEG = R2.S, R2.K, -np.inf
OLD = ["surprise", "fork-only surprise", "margin", "margin (inferred forks)"]
NEW = ["fork-only surprise (inferred)", "margin (eventual-discovery oracle)", "margin (inferred + allowance)"]
STREAMS = [("stationary", 2000), ("stationary short", 600)]


def run_new(rule, world, seed, T):
    fork, mu, s, a, r = world
    rng = np.random.default_rng([seed, 8, NEW.index(rule), T])
    full_seen = np.zeros((S, 2), bool); full_seen[s, a] = True
    eventual = fork & full_seen[:, 0] & full_seen[:, 1]          # forks that WILL be discovered
    sm = np.zeros((S, 2)); n = np.zeros((S, 2)); seen = np.zeros((S, 2), bool)
    mem = []
    for t in range(T):
        sm[s[t], a[t]] += r[t]; n[s[t], a[t]] += 1; seen[s[t], a[t]] = True
        mem.append(t)
        if len(mem) <= K:
            continue
        P = np.array(mem); ps, pa, pr = s[P], a[P], r[P]
        n_loo = n[ps, pa] - 1
        q_loo = (sm[ps, pa] - pr) / (n_loo + 1)
        ob = 1 - pa
        q_oth = sm[ps, ob] / (n[ps, ob] + 1)                      # 0 if the other action is unseen
        disc = seen[ps, 0] & seen[ps, 1]
        dq = np.abs(pr - q_loo) / (n_loo + 2)
        if rule == "fork-only surprise (inferred)":
            sc = np.where(disc, np.abs(pr - q_loo), NEG)
        elif rule == "margin (eventual-discovery oracle)":
            sc = np.where(eventual[ps], dq / (np.abs(q_loo - q_oth) + 0.1), NEG)
        elif rule == "margin (inferred + allowance)":
            # discovered forks: margin as usual; unresolved: possible fork, unseen action at prior 0
            m = np.where(disc, np.abs(q_loo - q_oth), np.abs(q_loo - 0.0))
            sc = dq / (m + 0.1)
        else:
            raise ValueError(rule)
        low = np.flatnonzero(sc == sc.min())
        x = mem.pop(int(low[rng.integers(len(low))]))
        sm[s[x], a[x]] -= r[x]; n[s[x], a[x]] -= 1
    assert len(mem) == K
    return R1.evaluate(mem, *world)


def task(args):
    st, T, seed = args
    w = R2.make_world(st, T, seed)
    out = {rule: R2.run_rule(rule, w, seed, T) for rule in OLD}
    out.update({rule: run_new(rule, w, seed, T) for rule in NEW})
    fk, _, s, a, _ = w
    sn = np.zeros((S, 2), bool); sn[s, a] = True
    F = np.flatnonzero(fk)
    return st, seed, out, float(np.mean(~(sn[F, 0] & sn[F, 1])))


LINES, V = [], []


def log(x=""):
    LINES.append(x); print(x, flush=True)


def main():
    t0 = time.time()
    tasks = [(st, T, sd) for st, T in STREAMS for sd in range(10_000, 10_100)]
    with Pool(os.cpu_count()) as p:
        raw = p.map(task, tasks, chunksize=2)
    log(f"ran {len(tasks)} worlds in {time.time() - t0:.0f} s (round-2 seeds 10000-10099)")
    RULES = OLD + NEW
    Rg = {st: {k: np.array([o[k][0] for s_, sd, o, _ in sorted(raw, key=lambda x: x[1]) if s_ == st])
               for k in RULES} for st, _ in STREAMS}
    und = {st: np.mean([u for s_, _, _, u in raw if s_ == st]) for st, _ in STREAMS}
    # consistency: the re-run round-2 rules reproduce the saved round-2 results exactly
    saved = json.load(open(os.path.join(R1.RES, "svc2_raw.json")))
    for st, _ in STREAMS:
        for k in OLD:
            assert np.allclose(Rg[st][k], saved[st][k]["regret"]), (st, k)
    log("  [PASS] re-run round-2 rules reproduce the saved round-2 regrets exactly (paired data)")
    for st, T in STREAMS:
        log(f"-- {st} (T = {T}); true forks never recognised: {100 * und[st]:.2f}%")
        for k in RULES:
            log(f"   {k:<36} regret {Rg[st][k].mean():.4f}")
    rng = np.random.default_rng(2028)

    def claim(tag, st, A, B, thr):
        p, rci, dci = R1.boot_rel(Rg[st][A], Rg[st][B], rng)
        held = p >= thr and dci[0] > 0 if thr > 0 else (p > 0 and dci[0] > 0)
        V.append((tag, held, f"[{st}] {A} vs {B}: {p:+.1%} (CI {rci[0]:+.1%} to {rci[1]:+.1%}); paired-"
                              f"difference CI [{dci[0]:+.4f}, {dci[1]:+.4f}]; need "
                              + (f">= {thr:.0%}" if thr > 0 else "> 0") + " with CI excluding 0"))

    claim("B1a", "stationary", "margin (inferred forks)", "fork-only surprise (inferred)", 0.10)
    claim("B1b", "stationary short", "margin (inferred forks)", "fork-only surprise (inferred)", 0.0)
    D, E = {}, {}
    for st, _ in STREAMS:
        D[st] = Rg[st]["margin (eventual-discovery oracle)"].mean() - Rg[st]["margin"].mean()
        E[st] = Rg[st]["margin (inferred forks)"].mean() - Rg[st]["margin (eventual-discovery oracle)"].mean()
        log(f"  decomposition [{st}]: margin {Rg[st]['margin'].mean():.4f} -> (D, never discovered) "
            f"{D[st]:+.4f} -> (E, evicted before discovery) {E[st]:+.4f} -> inferred "
            f"{Rg[st]['margin (inferred forks)'].mean():.4f}")
    V.append(("B2a", E["stationary"] > D["stationary"],
              f"[stationary] premature eviction E {E['stationary']:+.4f} vs discovery failure D {D['stationary']:+.4f}; need E > D"))
    V.append(("B2b", D["stationary short"] > E["stationary short"],
              f"[stationary short] discovery failure D {D['stationary short']:+.4f} vs premature eviction E "
              f"{E['stationary short']:+.4f}; need D > E"))
    claim("B3", "stationary short", "margin (inferred + allowance)", "margin (inferred forks)", 0.0)
    p, rci, _ = R1.boot_rel(Rg["stationary"]["margin (inferred + allowance)"], Rg["stationary"]["margin (inferred forks)"], rng)
    log(f"  no prediction [stationary]: allowance vs inferred {p:+.1%} (CI {rci[0]:+.1%} to {rci[1]:+.1%})")
    for tag, held, msg in V:
        log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")
    log("SUMMARY: " + ", ".join(f"{t} {'held' if h else 'FAILED'}" for t, h, _ in V))
    open(os.path.join(R1.RES, "svc2b_report.txt"), "w").write("\n".join(LINES) + "\n")
    json.dump({st: {k: Rg[st][k].tolist() for k in RULES} for st, _ in STREAMS},
              open(os.path.join(R1.RES, "svc2b_raw.json"), "w"))


if __name__ == "__main__":
    main()
