#!/usr/bin/env python3
"""
svc3.py -- Round 3 (PREREGISTRATION_ROUND3.md, frozen at 5d83910): a crowd-aware memory.
Katie's hypothesis: prefer REPRESENTATIVE (typical-noise) decision-relevant memories over loud ones.
Stationary worlds as round 2 (t5, f=0.3, K=100), forks known, fresh seeds 20000-20099,
T=2000 (primary) and T=600 (secondary). Mechanism measures: kept noise and forks decided right.
"""
from __future__ import annotations
import os, json, time
import numpy as np
from multiprocessing import Pool
import svc as R1
import svc2 as R2

S, K, NEG = R2.S, R2.K, -np.inf
RULES = ["surprise", "fork-only surprise", "margin", "close calls only", "crowd-aware margin", "clairvoyant greedy"]
STREAMS = [("stationary", 2000), ("stationary short", 600)]


def run(rule, world, seed, T):
    fork, mu, s, a, r = world
    rng = np.random.default_rng([seed, 9, RULES.index(rule), T])
    sm = np.zeros((S, 2)); n = np.zeros((S, 2)); mem = []
    for t in range(T):
        sm[s[t], a[t]] += r[t]; n[s[t], a[t]] += 1; mem.append(t)
        if len(mem) <= K:
            continue
        P = np.array(mem); ps, pa, pr = s[P], a[P], r[P]; pf = fork[ps]
        n_loo = n[ps, pa] - 1
        q_loo = (sm[ps, pa] - pr) / (n_loo + 1)
        q_full = sm[ps, pa] / (n[ps, pa] + 1)
        ob = 1 - pa
        q_oth = np.where(pf, sm[ps, ob] / (n[ps, ob] + 1), 0.0)
        z = np.abs(pr - q_loo); m = np.abs(q_loo - q_oth)
        rel = 1.0 / ((n_loo + 2) * (m + 0.1))
        if rule == "surprise":
            sc = z
        elif rule == "fork-only surprise":
            sc = np.where(pf, z, NEG)
        elif rule == "margin":
            sc = np.where(pf, z * rel, NEG)
        elif rule == "close calls only":
            sc = np.where(pf, rel, NEG)
        elif rule == "crowd-aware margin":
            v = 1 + 1 / (n_loo + 1)
            sc = np.where(pf, z * np.exp(-z ** 2 / (2 * v)) * rel, NEG)
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
        low = np.flatnonzero(sc == sc.min())
        x = mem.pop(int(low[rng.integers(len(low))]))
        sm[s[x], a[x]] -= r[x]; n[s[x], a[x]] -= 1
    assert len(mem) == K
    mem = np.array(mem)
    reg, fact = R1.evaluate(mem, *world)
    kf = mem[fork[s[mem]]]
    noise = float(np.abs(r[kf] - mu[s[kf], a[kf]]).mean()) if len(kf) else np.nan
    Q = R1.beliefs(mem, s, a, r); F = np.flatnonzero(fork)
    right = float(np.mean(np.sign(Q[F, 1] - Q[F, 0]) == np.sign(mu[F, 1] - mu[F, 0])))
    return reg, fact, noise, right


def task(args):
    st, T, seed = args
    w = R2.make_world(st, T, seed)
    return st, seed, {rule: run(rule, w, seed, T) for rule in RULES}


LINES, V = [], []


def log(x=""):
    LINES.append(x); print(x, flush=True)


def main():
    t0 = time.time()
    tasks = [(st, T, sd) for st, T in STREAMS for sd in range(20_000, 20_100)]
    with Pool(os.cpu_count()) as p:
        raw = sorted(p.map(task, tasks, chunksize=2), key=lambda x: (x[0], x[1]))
    log(f"ran {len(tasks)} worlds in {time.time() - t0:.0f} s (fresh seeds 20000-20099)")
    D = {st: {k: np.array([o[k] for s_, _, o in raw if s_ == st]) for k in RULES} for st, _ in STREAMS}
    for st, T in STREAMS:
        log(f"-- {st} (T = {T})")
        for k in RULES:
            x = D[st][k]
            log(f"   {k:<20} regret {x[:, 0].mean():.4f}  fact {x[:, 1].mean():.3f}  kept noise "
                f"{np.nanmean(x[:, 2]):.3f}  forks right {x[:, 3].mean():.1%}")
    rng = np.random.default_rng(2029)
    idx = rng.integers(0, 100, (R1.NBOOT, 100))

    def rel_claim(tag, st, A, B, thr):
        p, rci, dci = R1.boot_rel(D[st][A][:, 0], D[st][B][:, 0], rng)
        held = (p >= thr if thr > 0 else p > 0) and dci[0] > 0
        V.append((tag, held, f"[{st}] {A} vs {B}: regret {p:+.1%} (CI {rci[0]:+.1%} to {rci[1]:+.1%}); need "
                              + (f">= {thr:.0%}" if thr > 0 else "> 0") + f", paired-difference CI "
                              f"[{dci[0]:+.4f}, {dci[1]:+.4f}] excluding 0"))

    def mech(tag, col, better_lower, what):
        a_, b_ = D["stationary"]["crowd-aware margin"][:, col], D["stationary"]["margin"][:, col]
        d = (b_ - a_) if better_lower else (a_ - b_)
        ci = np.percentile(d[idx].mean(1), [2.5, 97.5])
        V.append((tag, d.mean() > 0 and ci[0] > 0, f"[stationary] {what}: crowd-aware {a_.mean():.3f} vs margin "
                  f"{b_.mean():.3f} (improvement CI [{ci[0]:+.4f}, {ci[1]:+.4f}])"))

    rel_claim("C1", "stationary", "crowd-aware margin", "margin", 0.10)
    mech("C2", 2, True, "kept noise")
    mech("C3", 3, False, "forks decided right")
    rel_claim("C4", "stationary", "crowd-aware margin", "close calls only", 0.0)
    rel_claim("C5", "stationary short", "crowd-aware margin", "margin", 0.0)
    for tag, held, msg in V:
        log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")
    for st, _ in STREAMS:
        p, rci, _ = R1.boot_rel(D[st]["close calls only"][:, 0], D[st]["margin"][:, 0], rng)
        m_, c_, cl = (D[st][k][:, 0].mean() for k in ("margin", "crowd-aware margin", "clairvoyant greedy"))
        log(f"  no prediction [{st}]: close-calls-only vs margin {p:+.1%} (CI {rci[0]:+.1%} to {rci[1]:+.1%}); "
            f"crowd-aware closes {(m_ - c_) / (m_ - cl):.0%} of the margin-to-clairvoyant gap")
    log("SUMMARY: " + ", ".join(f"{t} {'held' if h else 'FAILED'}" for t, h, _ in V))
    open(os.path.join(R1.RES, "svc3_report.txt"), "w").write("\n".join(LINES) + "\n")
    json.dump({st: {k: D[st][k].tolist() for k in RULES} for st, _ in STREAMS},
              open(os.path.join(R1.RES, "svc3_raw.json"), "w"))
    figure(D)


def figure(D):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"surprise": "#c0392b", "fork-only surprise": "#e67e22", "margin": "#1a5fb4",
           "close calls only": "#8fb3e0", "crowd-aware margin": "#7b2cbf", "clairvoyant greedy": "#2e8b57"}
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    xs = np.arange(len(RULES)); X = D["stationary"]
    for j, (c, lab) in enumerate(((0, "decision regret (lower = better)"), (2, "noise in kept memories"),
                                  (3, "forks decided right"))):
        vals = [np.nanmean(X[k][:, c]) for k in RULES]
        ax[j].bar(xs, vals, color=[col[k] for k in RULES])
        ax[j].set_xticks(xs); ax[j].set_xticklabels(RULES, rotation=35, ha="right", fontsize=8)
        ax[j].set_ylabel(lab); ax[j].grid(alpha=0.2, axis="y")
        [ax[j].spines[k].set_visible(False) for k in ("top", "right")]
    ax[1].axhline(np.sqrt(2 / np.pi), color="#444", ls="--", lw=1)
    ax[1].text(len(RULES) - 0.5, np.sqrt(2 / np.pi) + 0.03, "typical noise", ha="right", fontsize=8)
    ax[0].set_title("Decisions", fontsize=10); ax[1].set_title("A crowd, or loud voices?", fontsize=10)
    ax[2].set_title("Getting the choice right", fontsize=10)
    fig.suptitle("Round 3: the crowd-aware memory (stationary, T = 2000)", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(R1.FIG, "svc3.png"), dpi=160)


if __name__ == "__main__":
    main()
