#!/usr/bin/env python3
"""diag_puzzles.py -- EXPLORATORY diagnostics (not pre-registered), prompted by Katie's questions.
Puzzle 1 ("wisdom of crowds"): does the clairvoyant keep LESS misleading evidence (smaller noise,
errors that cancel) than margin? Puzzle 3 ("bias / lock-in"): on short streams, are margin's wrong
decisions made with LARGE apparent margins (confidently wrong, so no longer treated as close calls)?
Uses round-2 worlds (seeds 10000-10039)."""
import numpy as np, svc2
from multiprocessing import Pool

def kept(rule, world, seed, T):
    box = {}
    orig = svc2.R1.evaluate
    svc2.R1.evaluate = lambda items, *w: box.setdefault("m", list(items)) and (0.0, 0.0)
    try:
        svc2.run_rule(rule, world, seed, T)
    finally:
        svc2.R1.evaluate = orig
    return np.array(box["m"])

def stats(args):
    st, T, seed = args
    w = svc2.make_world(st, T, seed); fork, mu, s, a, r = w
    out = {}
    for rule in ("margin", "clairvoyant greedy", "fork-only surprise"):
        m = kept(rule, w, seed, T)
        m = m[fork[s[m]]]                                    # kept fork observations
        eps = r[m] - mu[s[m], a[m]]                          # each kept memory's own noise
        Q = svc2.R1.beliefs(m, s, a, r)
        F = np.flatnonzero(fork)
        right = np.sign(Q[F, 1] - Q[F, 0]) == np.sign(mu[F, 1] - mu[F, 0])
        wrong = ~right
        conf_wrong = np.abs(Q[F, 1] - Q[F, 0])[wrong]
        conf_right = np.abs(Q[F, 1] - Q[F, 0])[right]
        # per situation-action: is the average kept noise pulled one way (errors not cancelling)?
        bias = [abs(eps[(s[m] == si) & (a[m] == ai)].mean()) for si, ai in set(zip(s[m], a[m]))]
        out[rule] = dict(noise=np.abs(eps).mean(), bias=np.mean(bias), right=right.mean(),
                         conf_wrong=conf_wrong.mean() if len(conf_wrong) else np.nan,
                         conf_right=conf_right.mean())
    return st, out

if __name__ == "__main__":
    tasks = [(st, T, sd) for st, T in (("stationary", 2000), ("stationary short", 600)) for sd in range(10000, 10040)]
    with Pool(4) as p:
        res = p.map(stats, tasks)
    for st in ("stationary", "stationary short"):
        print(f"-- {st}")
        for rule in ("fork-only surprise", "margin", "clairvoyant greedy"):
            rows = [o[rule] for s_, o in res if s_ == st]
            f = lambda k: np.nanmean([x[k] for x in rows])
            print(f"   {rule:<20} kept-noise |eps| {f('noise'):.3f}   non-cancelling bias {f('bias'):.3f}   "
                  f"forks decided right {f('right'):.1%}   |estimated margin| when WRONG {f('conf_wrong'):.3f} vs RIGHT {f('conf_right'):.3f}")
