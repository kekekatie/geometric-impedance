#!/usr/bin/env python3
"""diag_echo.py -- EXPLORATORY (post hoc, after round 3 failed). Is the crowd-aware rule's failure an
ECHO CHAMBER, i.e. 'typical' judged against the agent's own (possibly wrong) belief instead of the truth?
Compares crowd-aware margin with a CHEATING twin that judges typicality against the true mu, and
measures how often kept fork memories AGREE with a wrong current decision. Round-3 worlds, 40 seeds."""
import numpy as np, svc as R1, svc2 as R2, svc3 as R3
from multiprocessing import Pool
S, K, NEG = R2.S, R2.K, -np.inf

def run(rule, world, seed, T=2000):
    fork, mu, s, a, r = world
    rng = np.random.default_rng([seed, 10, rule == "crowd vs TRUTH (cheat)"])
    sm = np.zeros((S, 2)); n = np.zeros((S, 2)); mem = []
    for t in range(T):
        sm[s[t], a[t]] += r[t]; n[s[t], a[t]] += 1; mem.append(t)
        if len(mem) <= K:
            continue
        P = np.array(mem); ps, pa, pr = s[P], a[P], r[P]; pf = fork[ps]
        n_loo = n[ps, pa] - 1; q_loo = (sm[ps, pa] - pr) / (n_loo + 1)
        ob = 1 - pa; q_oth = np.where(pf, sm[ps, ob] / (n[ps, ob] + 1), 0.0)
        z = np.abs(pr - q_loo); m = np.abs(q_loo - q_oth); rel = 1 / ((n_loo + 2) * (m + 0.1))
        if rule == "crowd vs own belief":
            v = 1 + 1 / (n_loo + 1); typ = z * np.exp(-z ** 2 / (2 * v))
        else:                                             # typicality judged against the TRUTH
            e = np.abs(pr - np.nan_to_num(mu[ps, pa])); typ = z * np.exp(-e ** 2 / 2)
        sc = np.where(pf, typ * rel, NEG)
        low = np.flatnonzero(sc == sc.min()); x = mem.pop(int(low[rng.integers(len(low))]))
        sm[s[x], a[x]] -= r[x]; n[s[x], a[x]] -= 1
    mem = np.array(mem); Q = R1.beliefs(mem, s, a, r)
    F = np.flatnonzero(fork)
    wrong = F[np.sign(Q[F, 1] - Q[F, 0]) != np.sign(mu[F, 1] - mu[F, 0])]
    # in wrongly decided forks: fraction of kept memories that SUPPORT the wrong choice
    sup = []
    for si in wrong:
        km = mem[s[mem] == si]
        if len(km) == 0: continue
        chosen = int(Q[si, 1] > Q[si, 0])
        for x in km:   # a memory 'supports' the choice if it pushes its action's estimate in the chosen direction
            push_up = r[x] > mu[si, a[x]]
            sup.append(push_up == (a[x] == chosen))
    return R1.evaluate(mem, *world)[0], (np.mean(sup) if sup else np.nan)

def task(seed):
    w = R2.make_world("stationary", 2000, seed)
    return {k: run(k, w, seed) for k in ("crowd vs own belief", "crowd vs TRUTH (cheat)")}

if __name__ == "__main__":
    with Pool(4) as p:
        res = p.map(task, range(20000, 20040))
    for k in res[0]:
        print(f"{k:<24} regret {np.mean([r_[k][0] for r_ in res]):.4f}   in WRONG forks, kept memories "
              f"that support the wrong choice: {np.nanmean([r_[k][1] for r_ in res]):.0%}")
    print("reference (round 3, same worlds 20000-20099): margin 0.0969, crowd-aware 0.1377, clairvoyant 0.0506")
