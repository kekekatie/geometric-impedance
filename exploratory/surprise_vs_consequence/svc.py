#!/usr/bin/env python3
"""
svc.py -- Surprise versus consequence, Part A: what should a capacity-limited learning memory keep?

Implements PREREGISTRATION.md (FROZEN v2, commit e110a11) exactly; every prediction there is
evaluated at the end and reported HELD / FAILED. Structural self-checks are asserts (exit non-zero
if any fails); predictions never change the exit code.

World: S situations, forced (1 action) w.p. 1-f or fork (2 actions) w.p. f. Stream of T noisy
rewards. Memory keeps K observations; beliefs Q = sum/(n+1) (prior N(0,1), noise var 1) come only
from memory. At each arrival past capacity, the pool is K stored + newcomer; every item is scored
LEAVE-ONE-OUT (beliefs from pool minus that item); the lowest score is evicted, ties uniformly at
random. Rules: recency, random (reservoir), surprise, fork-only random (reservoir over fork
observations), fork-only surprise, margin (decision-sensitive surprise), clairvoyant greedy.
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
RES, FIG = os.path.join(HERE, "results"), os.path.join(HERE, "figures")
S, T, K, NSEED, NBOOT = 200, 2000, 100, 100, 10_000
RULES = ["recency", "random", "surprise", "fork-only random", "fork-only surprise", "margin",
         "clairvoyant greedy"]
CONDS = [("t5", 0.1), ("t5", 0.3), ("t5", 0.5), ("t5", 0.9),
         ("norm", 0.1), ("norm", 0.3), ("norm", 0.5), ("norm", 0.9), ("t2", 0.3)]
NEG = -np.inf


# ------------------------------------------------------------------ world and stream
def make_world(dist, f, seed):
    rng = np.random.default_rng([seed, 11, int(f * 100), {"t5": 5, "t2": 2, "norm": 0}[dist]])
    fork = rng.random(S) < f
    mu = np.full((S, 2), np.nan)
    if dist == "norm":
        forced_mu = rng.standard_normal(S)
    else:
        forced_mu = 2.0 * rng.standard_t(5 if dist == "t5" else 2, S)
    m1 = rng.standard_normal(S)
    d = 0.5 * rng.standard_normal(S)
    mu[:, 0] = np.where(fork, m1, forced_mu)
    mu[fork, 1] = m1[fork] + d[fork]
    s = rng.integers(0, S, T)
    a = np.where(fork[s], rng.integers(0, 2, T), 0)
    r = mu[s, a] + rng.standard_normal(T)
    return fork, mu, s, a, r


# ------------------------------------------------------------------ beliefs and regret
def beliefs(items, s, a, r):
    sm = np.zeros((S, 2)); n = np.zeros((S, 2))
    np.add.at(sm, (s[items], a[items]), r[items]); np.add.at(n, (s[items], a[items]), 1)
    return sm / (n + 1)


def regret_one(q0, q1, m0, m1):
    """regret in one fork situation; ties -> mean over tied actions (random tie-break)."""
    if q0 > q1:
        return max(m0, m1) - m0
    if q1 > q0:
        return max(m0, m1) - m1
    return max(m0, m1) - 0.5 * (m0 + m1)


def evaluate(items, fork, mu, s, a, r):
    Q = beliefs(np.asarray(items, dtype=int), s, a, r)
    F = np.where(fork)[0]
    reg = np.array([regret_one(Q[i, 0], Q[i, 1], mu[i, 0], mu[i, 1]) for i in F])
    err = np.concatenate([(Q[~fork, 0] - mu[~fork, 0]) ** 2,
                          (Q[fork, 0] - mu[fork, 0]) ** 2, (Q[fork, 1] - mu[fork, 1]) ** 2])
    return (float(reg.mean()) if len(F) else None), float(err.mean())


# ------------------------------------------------------------------ one rule on one world
def run_rule(rule, world, seed):
    fork, mu, s, a, r = world
    rng = np.random.default_rng([seed, 7, RULES.index(rule)])
    if rule == "recency":
        return evaluate(list(range(T - K, T)), *world)
    if rule == "random":                                      # reservoir sampling over the stream
        mem = []
        for t in range(T):
            if len(mem) < K:
                mem.append(t)
            elif rng.random() < K / (t + 1):
                mem[rng.integers(K)] = t
        return evaluate(mem, *world)
    if rule == "fork-only random":                            # reservoir over fork observations
        mem, j = [], 0
        for t in range(T):
            if not fork[s[t]]:
                continue
            j += 1
            if len(mem) < K:
                mem.append(t)
            elif rng.random() < K / j:
                mem[rng.integers(K)] = t
        return evaluate(mem, *world)

    # score-based rules: leave-one-out over the common pool of K+1
    sm = np.zeros((S, 2)); n = np.zeros((S, 2))
    mem = []
    for t in range(T):
        sm[s[t], a[t]] += r[t]; n[s[t], a[t]] += 1
        mem.append(t)
        if len(mem) <= K:
            continue
        P = np.array(mem); ps, pa, pr = s[P], a[P], r[P]
        pf = fork[ps]
        n_loo = n[ps, pa] - 1
        q_loo = (sm[ps, pa] - pr) / (n_loo + 1)
        ob = 1 - pa
        q_oth = np.where(pf, sm[ps, ob] / (n[ps, ob] + 1), 0.0)
        if rule == "surprise":
            sc = np.abs(pr - q_loo)
        elif rule == "fork-only surprise":
            sc = np.where(pf, np.abs(pr - q_loo), NEG)
        elif rule == "margin":
            m = np.abs(q_loo - q_oth)
            sc = np.where(pf, (np.abs(pr - q_loo) / (n_loo + 2)) / (m + 0.1), NEG)
        elif rule == "clairvoyant greedy":
            q_full = sm[ps, pa] / (n[ps, pa] + 1)
            sc = np.zeros(len(P))
            for i in np.where(pf)[0]:
                si = ps[i]
                if pa[i] == 0:
                    with_ = regret_one(q_full[i], q_oth[i], mu[si, 0], mu[si, 1])
                    without = regret_one(q_loo[i], q_oth[i], mu[si, 0], mu[si, 1])
                else:
                    with_ = regret_one(q_oth[i], q_full[i], mu[si, 0], mu[si, 1])
                    without = regret_one(q_oth[i], q_loo[i], mu[si, 0], mu[si, 1])
                sc[i] = without - with_                        # how much removing it would hurt
        else:
            raise ValueError(rule)
        low = np.flatnonzero(sc == sc.min())
        k = int(low[rng.integers(len(low))])
        x = mem.pop(k)
        sm[s[x], a[x]] -= r[x]; n[s[x], a[x]] -= 1
    assert len(mem) == K
    return evaluate(mem, *world)


def run_task(args):
    dist, f, seed = args
    world = make_world(dist, f, seed)
    out = {}
    for rule in RULES:
        out[rule] = run_rule(rule, world, seed)
    return dist, f, seed, out


# ------------------------------------------------------------------ statistics
def boot_rel(A, B, rng):
    """relative improvement of A over B = 1 - mean(A)/mean(B); paired bootstrap over seeds.
    Returns point, CI of the relative improvement, CI of the paired difference (B - A)."""
    A, B = np.asarray(A), np.asarray(B)
    idx = rng.integers(0, len(A), (NBOOT, len(A)))
    ma, mb = A[idx].mean(1), B[idx].mean(1)
    rel = 1 - ma / mb
    diff = mb - ma
    return (float(1 - A.mean() / B.mean()), tuple(np.percentile(rel, [2.5, 97.5])),
            tuple(np.percentile(diff, [2.5, 97.5])))


LINES = []


def log(x=""):
    LINES.append(x); print(x, flush=True)


def main():
    os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
    # structural self-checks
    fk, mu, s, a, r = make_world("t5", 0.3, 0)
    assert np.all(a[~fk[s]] == 0) and np.all(np.isnan(mu[~fk, 1])) and not np.isnan(mu[fk]).any()
    t0 = time.time()
    tasks = [(d, f, sd) for (d, f) in CONDS for sd in range(NSEED)]
    with Pool(os.cpu_count()) as pool:
        raw = pool.map(run_task, tasks, chunksize=4)
    log(f"ran {len(tasks)} worlds x {len(RULES)} rules in {time.time() - t0:.0f} s")
    data = {}
    for dist, f, seed, out in raw:
        data.setdefault((dist, f), {}).setdefault(seed, out)
    R = {c: {rule: np.array([data[c][sd][rule][0] for sd in range(NSEED)]) for rule in RULES} for c in data}
    E = {c: {rule: np.array([data[c][sd][rule][1] for sd in range(NSEED)]) for rule in RULES} for c in data}
    nofork = sum(1 for c in data for sd in data[c] if data[c][sd]["random"][0] is None)
    assert nofork == 0, f"{nofork} no-fork worlds"
    log("no world without forks (none excluded)")

    rng = np.random.default_rng(2026)
    log("=" * 100)
    log("Mean decision regret (lower = better) and fact error, per condition (100 paired worlds each)")
    for c in CONDS:
        agg = "median" if c[0] == "t2" else "mean"
        log(f"-- {c[0]}, f = {c[1]}")
        for rule in RULES:
            fe = np.median(E[c][rule]) if agg == "median" else E[c][rule].mean()
            log(f"   {rule:<20} regret {R[c][rule].mean():.4f}   fact error ({agg}) {fe:.4f}")

    V = []

    def claim(tag, A, B, cond, thresh):
        p, rel_ci, d_ci = boot_rel(R[cond][A], R[cond][B], rng)
        held = p >= thresh and d_ci[0] > 0
        extra = " (CI lower end also >= threshold)" if rel_ci[0] >= thresh else ""
        msg = (f"{A} vs {B} [{cond[0]}, f={cond[1]}]: regret improvement {p:+.1%} "
               f"(95% CI {rel_ci[0]:+.1%} to {rel_ci[1]:+.1%}); need >= {thresh:.0%} with the paired "
               f"difference CI [{d_ci[0]:+.4f}, {d_ci[1]:+.4f}] excluding zero{extra}")
        V.append((tag, held, msg)); return p

    P = ("t5", 0.3)
    log("=" * 100)
    log("PRE-REGISTERED PREDICTIONS (primary condition t5, f = 0.3 unless stated)")
    claim("P1", "margin", "fork-only surprise", P, 0.10)
    claim("P2a", "fork-only random", "surprise", P, 0.20)
    claim("P2b", "fork-only surprise", "surprise", P, 0.20)
    claim("P3", "margin", "surprise", P, 0.20)
    ed = E[P]["margin"] - E[P]["surprise"]
    idx = rng.integers(0, NSEED, (NBOOT, NSEED)); dci = np.percentile(ed[idx].mean(1), [2.5, 97.5])
    V.append(("P4", ed.mean() > 0 and dci[0] > 0,
              f"fact error: surprise {E[P]['surprise'].mean():.4f} vs margin {E[P]['margin'].mean():.4f} "
              f"(margin - surprise CI [{dci[0]:+.4f}, {dci[1]:+.4f}])"))
    so = E[P]["surprise"] - E[P]["random"]; sci = np.percentile(so[idx].mean(1), [2.5, 97.5])
    log(f"  outcome (iii) check, no prediction: fact error surprise {E[P]['surprise'].mean():.4f} vs random "
        f"{E[P]['random'].mean():.4f} (surprise - random CI [{sci[0]:+.4f}, {sci[1]:+.4f}])")
    adv = {c: 1 - R[c]["margin"].mean() / R[c]["surprise"].mean() for c in CONDS}
    p5 = adv[("t5", 0.9)] < adv[("t5", 0.3)] and adv[("norm", 0.9)] < adv[("norm", 0.3)] \
        and adv[("norm", 0.3)] < adv[("t5", 0.3)]
    V.append(("P5", p5, "margin's advantage over surprise: " +
              ", ".join(f"{c[0]} f={c[1]}: {adv[c]:+.1%}" for c in CONDS)))
    claim("P6", "margin", "random", P, 0.10)
    rr = 1 - R[P]["recency"].mean() / R[P]["random"].mean()
    V.append(("P7", abs(rr) <= 0.05, f"recency vs random regret: relative difference {rr:+.1%} (need within 5%)"))
    sr = 1 - R[P]["surprise"].mean() / R[P]["random"].mean()
    log(f"  no prediction: surprise vs random regret improvement {sr:+.1%}")
    cg = {rule: R[P][rule].mean() for rule in RULES}
    log(f"  clairvoyant greedy comparator (no bound claim): regret {cg['clairvoyant greedy']:.4f}; "
        f"rules below it: {[k for k, v in cg.items() if v < cg['clairvoyant greedy']]}")
    for tag, held, msg in V:
        log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")
    log("=" * 100)
    log("SUMMARY: " + ", ".join(f"{t} {'held' if h else 'FAILED'}" for t, h, _ in V))
    json.dump({f"{c[0]}_{c[1]}": {rule: dict(regret=R[c][rule].tolist(), fact=E[c][rule].tolist())
                                  for rule in RULES} for c in CONDS},
              open(os.path.join(RES, "svc_raw.json"), "w"))
    open(os.path.join(RES, "svc_report.txt"), "w").write("\n".join(LINES) + "\n")
    make_figure(R, E, adv)


def make_figure(R, E, adv):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"recency": "#8a8a8a", "random": "#b0b0b0", "surprise": "#c0392b", "fork-only random": "#e6a15c",
           "fork-only surprise": "#e67e22", "margin": "#1a5fb4", "clairvoyant greedy": "#2e8b57"}
    P = ("t5", 0.3)
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.4))
    xs = np.arange(len(RULES))
    ax[0].bar(xs, [R[P][r].mean() for r in RULES], yerr=[1.96 * R[P][r].std() / np.sqrt(NSEED) for r in RULES],
              color=[col[r] for r in RULES], capsize=3)
    ax[0].set_xticks(xs); ax[0].set_xticklabels(RULES, rotation=35, ha="right", fontsize=8)
    ax[0].set_ylabel("decision regret (lower = better)"); ax[0].set_title("Decisions (t5, f = 0.3)", fontsize=10)
    ax[1].bar(xs, [E[P][r].mean() for r in RULES], color=[col[r] for r in RULES])
    ax[1].set_xticks(xs); ax[1].set_xticklabels(RULES, rotation=35, ha="right", fontsize=8)
    ax[1].set_ylabel("fact error (lower = better)"); ax[1].set_title("Facts (t5, f = 0.3)", fontsize=10)
    for dist, ls in (("t5", "-"), ("norm", "--")):
        fs = [0.1, 0.3, 0.5, 0.9]
        for rule in ("surprise", "fork-only surprise", "margin"):
            ax[2].plot(fs, [R[(dist, f)][rule].mean() for f in fs], ls, marker="o", color=col[rule], ms=4,
                       label=f"{rule} ({dist})")
    ax[2].set_xlabel("fraction of situations that are forks (f)"); ax[2].set_ylabel("decision regret")
    ax[2].set_title("Where the difference lives", fontsize=10); ax[2].legend(fontsize=7, frameon=False)
    for a_ in ax:
        a_.grid(alpha=0.2, axis="y"); [a_.spines[k].set_visible(False) for k in ("top", "right")]
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "svc.png"), dpi=170)


if __name__ == "__main__":
    main()
