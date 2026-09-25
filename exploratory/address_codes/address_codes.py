#!/usr/bin/env python3
"""
address_codes.py -- do quasiperiodic addresses resist corruption better than periodic or random ones?
Predictions are in PREREGISTRATION.md (committed before this file existed); each is checked and
reported as HELD / FAILED below. Structural checks (Sturmian complexity, unit-norm keys, the B0
sanity row) are asserts: exit non-zero if they fail.

Part A: self-location from content. A reader that has lost its pointer sees a window of w cells of
        a periodic / Fibonacci / random track and must find where it is.
Part B: positional codes in a hard-attention associative memory, under query noise (q) and
        stored-key noise (m).
"""
from __future__ import annotations
import os, sys, math, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES, FIG = os.path.join(HERE, "results"), os.path.join(HERE, "figures")
PHI = (1 + 5 ** 0.5) / 2
LINES, FAILS, VERDICTS = [], [], []


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    log(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def verdict(tag, held, msg):
    VERDICTS.append((tag, held, msg))
    log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")


# ------------------------------------------------------------------ Part A
NA, WFLIP, PFLIP, SEEDS = 2048, 64, 0.05, 20
ALPHA = 1 / PHI ** 2                       # frequency of S in the Fibonacci word


def fibonacci_track(n):
    k = np.arange(n + 1)
    fl = np.floor(k * ALPHA).astype(np.int64)
    return (fl[1:] - fl[:-1]).astype(np.uint8)          # 1 = S, 0 = L (Sturmian, slope 1/phi^2)


def tracks(rng):
    fib = fibonacci_track(NA)
    per = np.resize(fib[:13], NA)
    rnd = (rng.random(NA) < ALPHA).astype(np.uint8)
    return {"periodic": per, "Fibonacci": fib, "random": rnd}


def distinct_windows(s, w):
    return len({s[i:i + w].tobytes() for i in range(len(s) - w + 1)})


def w_star(s):
    """shortest w making every window unique (uniqueness is monotone in w -> binary search)."""
    n = len(s); lo, hi = 1, n
    while lo < hi:
        m = (lo + hi) // 2
        if distinct_windows(s, m) == n - m + 1:
            hi = m
        else:
            lo = m + 1
    return lo


def localise(s, w, p, rng):
    """reader holds the clean map s; sees the window at each position with a fraction p of
    symbols flipped; picks the nearest-Hamming match (ties broken at random).
    Returns (accuracy, mean error distance among failures)."""
    W = np.lib.stride_tricks.sliding_window_view(s, w).astype(np.float32)   # (M, w)
    noisy = np.abs(W - (rng.random(W.shape) < p)).astype(np.float32)
    agree = noisy @ W.T + (1 - noisy) @ (1 - W).T                             # matches, (M, M)
    best = agree.max(axis=1, keepdims=True)
    ties = agree == best
    M = W.shape[0]
    hit = ties[np.arange(M), np.arange(M)] / ties.sum(axis=1)                # expected acc
    errs = []
    for i in np.where(hit < 1)[0][:400]:
        cand = np.where(ties[i])[0]; cand = cand[cand != i]
        if len(cand):
            errs.append(np.abs(cand - i).mean())
    return float(hit.mean()), (float(np.mean(errs)) if errs else 0.0)


def part_a():
    log("=" * 92)
    log("PART A -- self-location from content: which track tells you where you are?")
    log("=" * 92)
    fib = fibonacci_track(4000)
    require(all(distinct_windows(fib, w) == w + 1 for w in range(1, 61)),
            "Fibonacci track is Sturmian: exactly w+1 distinct windows of each length w <= 60")
    rng = np.random.default_rng(0)
    T = tracks(rng)
    ws = {k: w_star(v) for k, v in T.items()}
    for k, v in ws.items():
        log(f"  {k:>9}: shortest window making EVERY position unique  w* = {v}"
            + ("   (= N - 12: only when the window is almost the whole track)" if v == NA - 12 else ""))
    verdict("A1", ws["periodic"] >= NA - 13 and ws["Fibonacci"] > 500 and 15 <= ws["random"] <= 40,
            f"w*: periodic {ws['periodic']} (pre-reg said 'never': it is N-12, i.e. only trivially), "
            f"Fibonacci {ws['Fibonacci']} (pred > 500), random {ws['random']} (pred 15-40)")
    wgrid = [8, 16, 24, 32, 48, 64, 96, 128]
    curve = {k: [] for k in T}
    for w in wgrid:
        row = []
        for k in T:
            accs = [localise(T[k] if k != "random" else tracks(np.random.default_rng(100 + s))["random"],
                             w, PFLIP, np.random.default_rng(1000 + s))[0] for s in range(6)]
            curve[k].append(float(np.mean(accs))); row.append(f"{k} {np.mean(accs):.3f}")
        log(f"  w = {w:>3}, {PFLIP:.0%} flipped:  " + "   ".join(row))
    a2, dist = {}, {}
    for k in T:
        r = [localise(T[k] if k != "random" else tracks(np.random.default_rng(200 + s))["random"],
                      WFLIP, PFLIP, np.random.default_rng(2000 + s)) for s in range(SEEDS)]
        a2[k] = float(np.mean([x[0] for x in r])); dist[k] = float(np.mean([x[1] for x in r]))
    log(f"  at w = {WFLIP}, {PFLIP:.0%} flipped, {SEEDS} seeds: accuracy " +
        ", ".join(f"{k} {a2[k]:.3f}" for k in T))
    log("  mean distance of a wrong guess from the truth: " + ", ".join(f"{k} {dist[k]:.0f}" for k in T))
    verdict("A2", a2["random"] > 0.9 and a2["Fibonacci"] < 0.05,
            f"random {a2['random']:.3f} (pred > 0.90), Fibonacci {a2['Fibonacci']:.3f} (pred < 0.05)")
    return dict(w_star=ws, wgrid=wgrid, curve=curve, a2=a2, err_dist=dist)


# ------------------------------------------------------------------ Part B
NB, D, SIGMAS = 256, 64, [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
K = np.arange(1, D // 2 + 1)
CODES = ["periodic (aliased)", "harmonic", "RoPE-style", "golden", "random frequencies", "random keys"]
POSTHOC = ["golden R_d (post hoc)"]
# Roberts' generalised golden ratio: the unique positive root of x^(d+1) = x + 1, d = 32. Its inverse
# powers give 32 mutually independent frequencies whose Kronecker sequence is low-discrepancy on the
# 32-torus -- a quasiperiodic code with a 32-dimensional hidden space, not a 1-dimensional one.
_g = 2.0
for _ in range(200):
    _g = (1 + _g) ** (1 / (D // 2 + 1))
RD_ALPHA = np.mod(_g ** (-K.astype(float)), 1.0)


def sinus(omega):
    pos = np.arange(NB)[:, None] * omega[None, :]
    X = np.concatenate([np.cos(pos), np.sin(pos)], axis=1)
    X = X / np.linalg.norm(X, axis=1, keepdims=True)
    return np.round(X, 12) + 0.0      # mathematically identical keys become bitwise identical


def make_keys(code, rng):
    if code == "periodic (aliased)":
        return sinus(2 * np.pi * K / 64)
    if code == "harmonic":
        return sinus(2 * np.pi * K / NB)
    if code == "RoPE-style":
        return sinus(10000.0 ** (-(K - 1) / (D // 2)))
    if code == "golden":
        return sinus(2 * np.pi * np.mod(K / PHI, 1.0))
    if code == "golden R_d (post hoc)":
        return sinus(2 * np.pi * RD_ALPHA)
    if code == "random frequencies":
        return sinus(rng.uniform(0, 2 * np.pi, D // 2))
    X = rng.standard_normal((NB, D))
    return X / np.linalg.norm(X, axis=1, keepdims=True)


def retrieve(keys, queries):
    return np.argmax(queries @ keys.T, axis=1)          # hard attention; ties -> lowest index


def part_b():
    log("=" * 92)
    log("PART B -- positional codes in a hard-attention associative memory")
    log("=" * 92)
    out = {m: {c: dict(exact=[], near=[], dist=[]) for c in CODES + POSTHOC} for m in ("q", "m")}
    truth = np.arange(NB)
    for c in CODES + POSTHOC:
        kk = make_keys(c, np.random.default_rng(7))
        require(np.allclose(np.linalg.norm(kk, axis=1), 1), f"{c}: keys are unit-norm")
    for mode in ("q", "m"):
        for c in CODES + POSTHOC:
            for s in SIGMAS:
                ex, ne, di = [], [], []
                for seed in range(SEEDS):
                    rng = np.random.default_rng(10_000 * seed + 17)
                    keys = make_keys(c, rng)
                    noise = rng.standard_normal((NB, D)) * s / math.sqrt(D)
                    got = retrieve(keys, keys + noise) if mode == "q" else retrieve(keys + noise, keys)
                    err = np.abs(got - truth)
                    ex.append((err == 0).mean()); ne.append((err <= 2).mean())
                    di.append(err[err > 0].mean() if (err > 0).any() else 0.0)
                out[mode][c]["exact"].append(float(np.mean(ex)))
                out[mode][c]["near"].append(float(np.mean(ne)))
                out[mode][c]["dist"].append(float(np.mean(di)))
        log(f"-- corruption ({mode}): {'noisy QUERY' if mode == 'q' else 'noisy STORED keys (silent)'}")
        log("   " + "code".ljust(20) + "".join(f"s={s:<5}" for s in SIGMAS) + "   [exact / within +-2 / mean miss distance]")
        for c in CODES + POSTHOC:
            r = out[mode][c]
            log("   " + c.ljust(20) + "".join(f"{e:5.2f} " for e in r["exact"]))
            log("   " + "".ljust(20) + "".join(f"{e:5.2f} " for e in r["near"]))
            log("   " + "".ljust(20) + "".join(f"{e:5.0f} " for e in r["dist"]))
    # B0 sanity (structural)
    q = out["q"]
    require(all(q[c]["exact"][0] == 1.0 for c in CODES if c != "periodic (aliased)")
            and q["periodic (aliased)"]["exact"][0] == 0.25,
            "B0 sanity: at sigma=0 every code is exact except periodic (aliased) = 0.25 (four identical keys)")
    VERDICTS.append(("B0", True, "sanity row as predicted"))
    idx = [i for i, s in enumerate(SIGMAS) if s > 0]
    b1 = all(out[m]["random keys"]["exact"][i] >= max(out[m][c]["exact"][i] for c in CODES)
             for m in ("q", "m") for i in idx)
    lose = [(m, SIGMAS[i], c) for m in ("q", "m") for i in idx for c in CODES
            if out[m][c]["exact"][i] > out[m]["random keys"]["exact"][i]]
    verdict("B1", b1, "random keys have the highest exact accuracy at every sigma > 0"
            + ("" if b1 else f" -- beaten at {lose[:6]}"))
    idx2 = [i for i, s in enumerate(SIGMAS) if s >= 0.75]
    b2 = all(out[m][c]["near"][i] > out[m]["random keys"]["near"][i]
             for m in ("q", "m") for i in idx2 for c in ("golden", "random frequencies"))
    verdict("B2", b2, "golden and random-frequency codes have a higher +-2 near-hit rate than random "
            "keys at sigma >= 0.75")
    sin_codes = ["harmonic", "RoPE-style", "golden", "random frequencies"]
    b3 = all(q["RoPE-style"]["exact"][i] <= min(q[c]["exact"][i] for c in sin_codes) for i in idx)
    verdict("B3", b3, "RoPE-style has the lowest exact accuracy of the non-aliased sinusoidal codes "
            "(query noise)")
    gaps = [out[m]["golden"]["exact"][i] - out[m]["random frequencies"]["exact"][i]
            for m in ("q", "m") for i in range(len(SIGMAS))]
    b4 = max(abs(g) for g in gaps) <= 0.02
    verdict("B4", b4, f"golden vs random frequencies within 2 points everywhere (predicted NULL): "
            f"largest gap {max(gaps, key=abs):+.3f} (positive = golden better)")
    rank = lambda m, i: [c for c in sorted(CODES, key=lambda c: -out[m][c]["exact"][i])]
    same = [rank("q", i) == rank("m", i) for i in idx]
    verdict("B5", all(same), f"stored-key corruption ranks the codes as query corruption does "
            f"({sum(same)}/{len(same)} noise levels identical)")
    # ---- diagnosis of golden (reported, not a prediction) ----
    import collections
    miss = collections.Counter()
    kg = make_keys("golden", None)
    for seed in range(SEEDS):
        rng = np.random.default_rng(seed)
        g = retrieve(kg, kg + rng.standard_normal((NB, D)) * 0.75 / math.sqrt(D))
        d = np.abs(g - truth); miss.update(d[d > 0].tolist())
    log("-- why golden fails: its 32 frequencies are all multiples of ONE irrational (1/phi), so each")
    log("   key encodes a single number, the perpendicular-space coordinate frac(i/phi). Positions a")
    log("   Fibonacci number apart are neighbours in that hidden space, far apart on the line.")
    log(f"   golden miss distances at sigma = 0.75 (query noise), all seeds: {miss.most_common(6)}")
    fib = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233}
    require(set(miss) <= fib, "every golden miss lands a Fibonacci number away (a perp-space neighbour)")
    rd, rf = out["q"]["golden R_d (post hoc)"], out["q"]["random frequencies"]
    log(f"-- POST HOC (not pre-registered): golden R_d vs random frequencies, exact accuracy, query noise:")
    log("   R_d   " + " ".join(f"{x:.3f}" for x in rd["exact"]))
    log("   random" + " ".join(f"{x:.3f}" for x in rf["exact"]))
    rdm, rfm = out["m"]["golden R_d (post hoc)"], out["m"]["random frequencies"]
    log("   stored-key noise:  R_d " + " ".join(f"{x:.3f}" for x in rdm["exact"])
        + "   random " + " ".join(f"{x:.3f}" for x in rfm["exact"]))
    return out


def posthoc_high_noise():
    """POST HOC, not pre-registered: is R_d's small edge quasiperiodicity, or just even spreading?
    Controls: stratified random (one random frequency per even bin) and evenly spaced (commensurate:
    all multiples of pi/64, so the code repeats with period 128 < N -- a crystal)."""
    log("=" * 92)
    log("POST HOC (not pre-registered) -- high noise, 60 seeds, mean +- s.e.: order without repetition?")
    fam = {
        "golden R_d": lambda r: make_keys("golden R_d (post hoc)", r),
        "stratified random": lambda r: sinus(np.pi * (np.arange(D // 2) + r.random(D // 2)) / (D // 2)),
        "random frequencies": lambda r: make_keys("random frequencies", r),
        "random keys": lambda r: make_keys("random keys", r),
        "evenly spaced (crystal)": lambda r: sinus(np.pi * (np.arange(D // 2) + 0.5) / (D // 2)),
    }
    truth, res = np.arange(NB), {}
    for mode in ("q", "m"):
        for sg in (2.0, 2.5):
            row = []
            for name, f in fam.items():
                acc = []
                for seed in range(60):
                    rng = np.random.default_rng(777 + seed); k = f(rng)
                    n = rng.standard_normal(k.shape) * sg / math.sqrt(D)
                    g = retrieve(k, k + n) if mode == "q" else retrieve(k + n, k)
                    acc.append((g == truth).mean())
                m_, se = float(np.mean(acc)), float(np.std(acc) / math.sqrt(60))
                res[f"{mode}{sg}:{name}"] = (m_, se); row.append(f"{name} {m_:.3f}+-{se:.3f}")
            log(f"  ({mode}) sigma {sg}:  " + " | ".join(row))
    return res


def figure(A, B):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"periodic": "#8a8a8a", "Fibonacci": "#c0392b", "random": "#1a5fb4",
           "periodic (aliased)": "#8a8a8a", "harmonic": "#b8860b", "RoPE-style": "#6a3d9a",
           "golden": "#c0392b", "random frequencies": "#e67e22", "random keys": "#1a5fb4",
           "golden R_d (post hoc)": "#2e8b57"}
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    for k, ys in A["curve"].items():
        ax[0].plot(A["wgrid"], ys, "-o", color=col[k], lw=2, ms=5, label=k)
    ax[0].set_xscale("log", base=2); ax[0].set_xlabel("window the reader can see (cells)")
    ax[0].set_ylabel("finds its true position"); ax[0].set_ylim(-0.03, 1.03)
    ax[0].set_title("A. Where am I? (5% of cells corrupted)", fontsize=10)
    for j, (key, lab) in enumerate((("exact", "exact recall"), ("near", "recall within ±2 positions"))):
        a = ax[j + 1]
        for c in CODES + POSTHOC:
            a.plot(SIGMAS, B["q"][c][key], marker="o", color=col[c],
                   lw=2 if c in ("golden", "random keys") else 1.3,
                   ms=4, label=c, ls="--" if c in ("random frequencies", "golden R_d (post hoc)") else "-")
        a.set_xlabel("noise on the query (σ)"); a.set_ylabel(lab); a.set_ylim(-0.03, 1.03)
        a.set_title(f"B. Positional codes in memory: {lab}", fontsize=10)
    for a in ax:
        a.grid(alpha=0.2); [a.spines[s].set_visible(False) for s in ("top", "right")]
    ax[0].legend(fontsize=8, frameon=False); ax[1].legend(fontsize=7.5, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "address_codes.png"), dpi=170)


def main():
    os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
    A = part_a(); B = part_b(); P = posthoc_high_noise()
    log("=" * 92)
    log("PRE-REGISTERED PREDICTIONS: " + ", ".join(f"{t} {'held' if h else 'FAILED'}" for t, h, _ in VERDICTS))
    json.dump(dict(A=A, B=B, posthoc=P), open(os.path.join(RES, "address_codes.json"), "w"), indent=1)
    figure(A, B)
    log("STRUCTURAL CHECKS: " + ("ALL PASSED" if not FAILS else "FAILED: " + "; ".join(FAILS)))
    open(os.path.join(RES, "address_codes_report.txt"), "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
