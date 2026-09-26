#!/usr/bin/env python3
"""
svc2.py -- Surprise versus consequence, ROUND 2 (PREREGISTRATION_ROUND2.md, frozen at f45fa98).

New rules: gain (softmax, beta=5; Mattar-Daw-style, adapted to retention), gain (greedy, reported),
margin with INFERRED forks. New streams: stationary (replication), stationary short (T=600),
early-only (the cliff test), drift (the better action may change at T/2; the test uses post-change
values). Everything else as round 1 (svc.py): estimator, K=100 pool, leave-one-out, random ties,
regret / fact error, paired bootstrap. Predictions R1-R6 reported HELD / FAILED; structural
asserts only affect the exit code.
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
import svc as R1

HERE = R1.HERE
S, K, NSEED, NBOOT, BETA, F = R1.S, R1.K, 100, R1.NBOOT, 5.0, 0.3
NEG = -np.inf
RULES = ["recency", "random", "surprise", "fork-only random", "fork-only surprise", "margin",
         "margin (inferred forks)", "gain (softmax)", "gain (greedy)", "clairvoyant greedy"]
STREAMS = [("stationary", 2000), ("stationary short", 600), ("early-only", 2000), ("drift", 2000)]


def make_world(stream, T, seed):
    rng = np.random.default_rng([seed, 22, [x for x, _ in STREAMS].index(stream), T])
    fork = rng.random(S) < F
    mu = np.full((S, 2), np.nan)
    forced_mu = 2.0 * rng.standard_t(5, S)
    m1 = rng.standard_normal(S); d = 0.5 * rng.standard_normal(S)
    mu[:, 0] = np.where(fork, m1, forced_mu)
    mu[fork, 1] = m1[fork] + d[fork]
    if stream == "early-only":
        early = np.zeros(S, bool); early[rng.permutation(S)[: S // 2]] = True
        late = np.flatnonzero(~early)
        s = np.concatenate([rng.integers(0, S, T // 2), late[rng.integers(0, len(late), T - T // 2)]])
    else:
        s = rng.integers(0, S, T)
    a = np.where(fork[s], rng.integers(0, 2, T), 0)
    mu_t = np.repeat(mu[None], T, axis=0) if stream == "drift" else None
    mu_test = mu.copy()
    if stream == "drift":
        F_idx = np.flatnonzero(fork)
        ch = F_idx[rng.permutation(len(F_idx))[: len(F_idx) // 2]]
        mu_test[ch, 1] = mu[ch, 0] + 0.5 * rng.standard_normal(len(ch))
        mu_t[T // 2:] = mu_test
        r = mu_t[np.arange(T), s, a] + rng.standard_normal(T)
    else:
        r = mu[s, a] + rng.standard_normal(T)
    return fork, mu_test, s, a, r


def softmax_value(q0, q1, p_from0, p_from1):
    """sum_a pi(a) q(a) with pi = softmax(beta * p) (vectorised)."""
    z = BETA * (p_from1 - p_from0)
    p1 = 1 / (1 + np.exp(-z))
    return (1 - p1) * q0 + p1 * q1


def greedy_value(q0, q1, p0, p1):
    return np.where(p0 > p1, q0, np.where(p1 > p0, q1, 0.5 * (q0 + q1)))


def run_rule(rule, world, seed, T):
    fork, mu, s, a, r = world
    rng = np.random.default_rng([seed, 7, RULES.index(rule), T])
    if rule == "recency":
        return R1.evaluate(list(range(T - K, T)), *world)
    if rule in ("random", "fork-only random"):
        mem, j = [], 0
        for t in range(T):
            if rule == "fork-only random" and not fork[s[t]]:
                continue
            j += 1
            if len(mem) < K:
                mem.append(t)
            elif rng.random() < K / j:
                mem[rng.integers(K)] = t
        return R1.evaluate(mem, *world)

    sm = np.zeros((S, 2)); n = np.zeros((S, 2)); seen = np.zeros((S, 2), bool)
    mem = []
    for t in range(T):
        sm[s[t], a[t]] += r[t]; n[s[t], a[t]] += 1; seen[s[t], a[t]] = True
        mem.append(t)
        if len(mem) <= K:
            continue
        P = np.array(mem); ps, pa, pr = s[P], a[P], r[P]
        pf = fork[ps]
        n_loo = n[ps, pa] - 1
        q_loo = (sm[ps, pa] - pr) / (n_loo + 1)
        q_full = sm[ps, pa] / (n[ps, pa] + 1)
        ob = 1 - pa
        q_oth = np.where(pf, sm[ps, ob] / (n[ps, ob] + 1), 0.0)
        if rule == "surprise":
            sc = np.abs(pr - q_loo)
        elif rule == "fork-only surprise":
            sc = np.where(pf, np.abs(pr - q_loo), NEG)
        elif rule in ("margin", "margin (inferred forks)"):
            isf = pf if rule == "margin" else (seen[ps, 0] & seen[ps, 1])
            m = np.abs(q_loo - q_oth)
            sc = np.where(isf, (np.abs(pr - q_loo) / (n_loo + 2)) / (m + 0.1), NEG)
        elif rule in ("gain (softmax)", "gain (greedy)"):
            # beliefs with (+) and without (-) x, ordered as (action 0, action 1)
            qp0 = np.where(pa == 0, q_full, q_oth); qp1 = np.where(pa == 0, q_oth, q_full)
            qm0 = np.where(pa == 0, q_loo, q_oth); qm1 = np.where(pa == 0, q_oth, q_loo)
            val = softmax_value if rule == "gain (softmax)" else greedy_value
            g = val(qp0, qp1, qp0, qp1) - val(qp0, qp1, qm0, qm1)
            sc = np.where(pf, g, 0.0)                         # forced: one action -> gain exactly 0
        elif rule == "clairvoyant greedy":
            sc = np.zeros(len(P))
            for i in np.where(pf)[0]:
                si = ps[i]
                if pa[i] == 0:
                    w = R1.regret_one(q_full[i], q_oth[i], mu[si, 0], mu[si, 1])
                    wo = R1.regret_one(q_loo[i], q_oth[i], mu[si, 0], mu[si, 1])
                else:
                    w = R1.regret_one(q_oth[i], q_full[i], mu[si, 0], mu[si, 1])
                    wo = R1.regret_one(q_oth[i], q_loo[i], mu[si, 0], mu[si, 1])
                sc[i] = wo - w
        else:
            raise ValueError(rule)
        low = np.flatnonzero(sc == sc.min())
        x = mem.pop(int(low[rng.integers(len(low))]))
        sm[s[x], a[x]] -= r[x]; n[s[x], a[x]] -= 1
    assert len(mem) == K
    return R1.evaluate(mem, *world)


def run_task(args):
    stream, T, seed = args
    world = make_world(stream, T, seed)
    return stream, seed, {rule: run_rule(rule, world, seed, T) for rule in RULES}


LINES, V = [], []


def log(x=""):
    LINES.append(x); print(x, flush=True)


def main():
    # structural self-checks on the generators
    fk, mu, s, a, r = make_world("early-only", 2000, 0)
    first, second = set(s[:1000]), set(s[1000:])
    assert len(second) <= S // 2 and len(first - second) > 0, "early-only stream malformed"
    fk, mu, s, a, r = make_world("drift", 2000, 0)
    assert np.all(a[~fk[s]] == 0) and not np.isnan(mu[fk]).any()
    t0 = time.time()
    tasks = [(st, T, sd) for (st, T) in STREAMS for sd in range(10_000, 10_000 + NSEED)]  # fresh seeds
    with Pool(os.cpu_count()) as pool:
        raw = pool.map(run_task, tasks, chunksize=2)
    log(f"ran {len(tasks)} worlds x {len(RULES)} rules in {time.time() - t0:.0f} s (fresh seeds 10000-10099)")
    Rg = {st: {rule: [] for rule in RULES} for st, _ in STREAMS}
    Ef = {st: {rule: [] for rule in RULES} for st, _ in STREAMS}
    for st, sd, out in sorted(raw, key=lambda x: (x[0], x[1])):
        for rule in RULES:
            assert out[rule][0] is not None
            Rg[st][rule].append(out[rule][0]); Ef[st][rule].append(out[rule][1])
    Rg = {st: {k: np.array(v) for k, v in d.items()} for st, d in Rg.items()}
    Ef = {st: {k: np.array(v) for k, v in d.items()} for st, d in Ef.items()}
    log("=" * 100)
    for st, T in STREAMS:
        log(f"-- stream: {st} (T = {T})")
        for rule in RULES:
            log(f"   {rule:<24} regret {Rg[st][rule].mean():.4f}   fact error {Ef[st][rule].mean():.4f}")
    rng = np.random.default_rng(2027)

    def rel(st, A, B):
        return R1.boot_rel(Rg[st][A], Rg[st][B], rng)

    def claim(tag, st, A, B, thr):
        p, rci, dci = rel(st, A, B)
        held = p >= thr and dci[0] > 0
        V.append((tag, held, f"[{st}] {A} vs {B}: {p:+.1%} (CI {rci[0]:+.1%} to {rci[1]:+.1%}); need >= "
                              f"{thr:.0%}, paired-difference CI [{dci[0]:+.4f}, {dci[1]:+.4f}] excludes 0"))
        return held

    log("=" * 100)
    log("PRE-REGISTERED PREDICTIONS (round 2)")
    claim("R1a", "stationary", "margin", "surprise", 0.20)
    claim("R1b", "stationary", "margin", "fork-only surprise", 0.10)
    g = 1 - Rg["stationary"]["gain (softmax)"].mean() / Rg["stationary"]["margin"].mean()
    V.append(("R2", abs(g) <= 0.10, f"[stationary] gain (softmax) vs margin: gain's regret is "
              f"{-g:+.1%} relative to margin (need within +-10%)"))
    gi = 1 - Rg["stationary"]["margin (inferred forks)"].mean() / Rg["stationary"]["margin"].mean()
    V.append(("R3a", abs(gi) <= 0.05, f"[stationary] margin (inferred) vs margin: {-gi:+.1%} relative "
              f"regret (need within +-5%)"))
    claim("R3b", "stationary short", "margin (inferred forks)", "surprise", 0.10)
    eo = Rg["early-only"]
    worst = max(RULES, key=lambda k: eo[k].mean())
    p, rci, dci = rel("early-only", "random", "recency")
    V.append(("R4a", worst == "recency" and p >= 0.30 and dci[0] > 0,
              f"[early-only] highest-regret rule: {worst}; recency worse than random by {p:+.1%} "
              f"(recency regret {eo['recency'].mean():.4f} vs random {eo['random'].mean():.4f}; "
              f"CI of improvement {rci[0]:+.1%} to {rci[1]:+.1%}); need recency worst and >= 30%"))
    claim("R4b", "early-only", "margin", "surprise", 0.20)
    p, rci, dci = rel("drift", "recency", "random")
    V.append(("R5a", p > 0 and dci[0] > 0, f"[drift] recency vs random: {p:+.1%} (paired-difference CI "
              f"[{dci[0]:+.4f}, {dci[1]:+.4f}]); need positive, CI excluding 0"))
    claim("R5b", "drift", "margin", "surprise", 0.10)
    st = Ef["stationary"]
    lowest = min((k for k in RULES if k != "clairvoyant greedy"), key=lambda k: st[k].mean())
    V.append(("R6", lowest == "surprise" and Rg["stationary"]["margin"].mean() < Rg["stationary"]["surprise"].mean(),
              f"[stationary] lowest fact error (excluding clairvoyant): {lowest}; margin regret "
              f"{Rg['stationary']['margin'].mean():.4f} vs surprise {Rg['stationary']['surprise'].mean():.4f}"))
    for tag, held, msg in V:
        log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")
    log("-" * 100)
    log("Reported without prediction:")
    for stn, _ in STREAMS:
        for A, B in (("gain (softmax)", "surprise"), ("gain (softmax)", "fork-only surprise"),
                     ("gain (greedy)", "margin"), ("margin", "gain (softmax)")):
            p, rci, _ = rel(stn, A, B)
            log(f"  [{stn}] {A} vs {B}: {p:+.1%} (CI {rci[0]:+.1%} to {rci[1]:+.1%})")
    log("=" * 100)
    log("SUMMARY: " + ", ".join(f"{t} {'held' if h else 'FAILED'}" for t, h, _ in V))
    os.makedirs(R1.RES, exist_ok=True)
    json.dump({stn: {k: dict(regret=Rg[stn][k].tolist(), fact=Ef[stn][k].tolist()) for k in RULES}
               for stn, _ in STREAMS}, open(os.path.join(R1.RES, "svc2_raw.json"), "w"))
    open(os.path.join(R1.RES, "svc2_report.txt"), "w").write("\n".join(LINES) + "\n")
    figure(Rg)


def figure(Rg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"recency": "#8a8a8a", "random": "#b0b0b0", "surprise": "#c0392b", "fork-only random": "#e6a15c",
           "fork-only surprise": "#e67e22", "margin": "#1a5fb4", "margin (inferred forks)": "#5b8fd6",
           "gain (softmax)": "#6a3d9a", "gain (greedy)": "#b39ddb", "clairvoyant greedy": "#2e8b57"}
    fig, ax = plt.subplots(1, 4, figsize=(19, 4.6), sharey=True)
    xs = np.arange(len(RULES))
    for j, (st, T) in enumerate(STREAMS):
        m = [Rg[st][k].mean() for k in RULES]
        e = [1.96 * Rg[st][k].std() / np.sqrt(NSEED) for k in RULES]
        ax[j].bar(xs, m, yerr=e, color=[col[k] for k in RULES], capsize=2)
        ax[j].set_xticks(xs); ax[j].set_xticklabels(RULES, rotation=45, ha="right", fontsize=7.5)
        ax[j].set_title(f"{st} (T = {T})", fontsize=10)
        ax[j].grid(alpha=0.2, axis="y"); [ax[j].spines[k].set_visible(False) for k in ("top", "right")]
    ax[0].set_ylabel("decision regret (lower = better)")
    fig.tight_layout(); fig.savefig(os.path.join(R1.FIG, "svc2.png"), dpi=160)


if __name__ == "__main__":
    main()
