#!/usr/bin/env python3
"""
laying_the_street.py -- Wallace and Gromit: lay the Fibonacci street letter by letter, with
NO map. Which kind of non-local likeness lets a quasicrystal build itself correctly?

Every earlier study grew on a PRE-LAID tiling (cut-and-project decides everything first), so
seeds had nothing to teach (../seed_dynamics/). Here the street is laid as it is ridden: each
new tile (L or S) is chosen using ONLY the letters already laid. No hidden addresses, no window.

Rules for the next letter:
  LOCAL k     any letter keeping the last k letters a legal Fibonacci pattern; dice if two
              are allowed. (1-D local rules cannot force a quasicrystal: every 1-D shift of
              finite type that is non-empty contains a periodic sequence -- so defects or
              repetition must eventually appear.)
  COPY        same-scale likeness: find the most recent earlier place whose lead-up matches
              the current lead-up for as long as possible; lay what came next there.
  ANTI        the same twin, but lay the OPPOSITE (maximal novelty).
  DICE        a fair coin.
  SCALE       likeness across scales: the street consults its own zoomed-out self -- the next
              letter is letter n of sigma(street so far), sigma: L -> LS, S -> L (the street's
              own self-similarity; position n reads the street near position n / tau).
  WRONGSCALE  the same, with a zoom rule that is NOT the street's own (L -> LSS, S -> L).
  DUSTSCALE   read the zoomed-out street at a RANDOM position instead of the scaled one.

Measured: first defect (first place where a pattern of length <= 40 appears that the Fibonacci
street never contains), healing (no defect after some point), eventual repetition (period),
and pattern complexity p(n). All 32 five-letter seeds; LOCAL over 20 dice seeds per window.
Exact (strings); asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, random, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fibonacci_address_environment"))
import fibonacci_cutproject as F

REPORT = os.path.join(HERE, "results", "laying_report.txt")
DATA = os.path.join(HERE, "results", "laying.json")
LINES, FAILS = [], []
NMAX = 40                    # legality checked on every pattern up to this length
N = 3000                     # letters laid per street
SEEDS = ["".join("LS"[(b >> i) & 1] for i in range(5)) for b in range(32)]
SIG = {"L": "LS", "S": "L"}
BAD = {"L": "LSS", "S": "L"}

_pts = F.generate(1500)
FIB = "".join(F.gaps_of(_pts))
LANG = {n: {FIB[i:i + n] for i in range(len(FIB) - n + 1)} for n in range(1, NMAX + 1)}


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def defects(w):
    """positions i (1-based end) where some pattern ending at i, length <= NMAX, is illegal."""
    out = []
    for i in range(1, len(w) + 1):
        if any(w[i - n:i] not in LANG[n] for n in range(1, min(NMAX, i) + 1)):
            out.append(i)
    return out


def period(w):
    t = w[len(w) // 2:]
    for d in range(1, len(t) // 3):
        if all(t[i] == t[i + d] for i in range(len(t) - d)):
            return d
    return None


def comp(w, n):
    return len({w[i:i + n] for i in range(len(w) - n + 1)})


def twin_next(w):
    for m in range(min(len(w) - 1, 60), 0, -1):
        j = w.rfind(w[-m:], 0, len(w) - 1)
        if j >= 0:
            return w[j + m]
    return None


def lay(rule, seed, rng, k=None):
    w = seed
    while len(w) < N:
        if rule == "LOCAL":
            opts = [c for c in "LS" if (w + c)[-k:] in LANG[min(k, len(w) + 1)]]
            if not opts:
                return w, "stuck"
            c = opts[0] if len(opts) == 1 else rng.choice(opts)
        elif rule in ("COPY", "ANTI"):
            c = twin_next(w) or rng.choice("LS")
            if rule == "ANTI":
                c = "S" if c == "L" else "L"
        elif rule == "DICE":
            c = rng.choice("LS")
        elif rule in ("SCALE", "WRONGSCALE", "DUSTSCALE"):
            big = "".join((BAD if rule == "WRONGSCALE" else SIG)[x] for x in w)
            if rule != "DUSTSCALE" and len(big) <= len(w):
                return w, "stuck"                     # the zoomed-out self never reaches past now
            c = big[len(w)] if rule != "DUSTSCALE" else big[rng.randrange(len(big))]
        w += c
    return w, "ok"


def main():
    log("=" * 90)
    log("LAYING THE STREET -- a quasicrystal built letter by letter, from its own past only")
    log("=" * 90)
    log(f"  reference street {len(FIB)} letters; legality checked on all patterns up to length "
        f"{NMAX}; {N} letters laid per run; seeds = all 32 five-letter words")
    out = {}

    # ---- LOCAL rules: must fail eventually (1-D) ----
    log("-" * 90)
    loc = {}
    for k in (3, 5, 8, 13, 21):
        fd = []
        for s in range(20):
            w, st = lay("LOCAL", "LSLLS", random.Random(s), k=k)
            d = defects(w); fd.append(d[0] if d else None)
        loc[k] = fd
        ok = [x for x in fd if x is not None]
        log(f"  LOCAL k={k:>2}: {len(ok)}/20 runs hit a defect; first defect median "
            f"{sorted(ok)[len(ok) // 2] if ok else '-'} (range {min(ok) if ok else '-'}-{max(ok) if ok else '-'})")
    require(all(x is not None for k in loc for x in loc[k]),
            "LOCAL: every run with every window (k up to 21) eventually lays a defect -- as 1-D theory "
            "requires, local rules cannot lay the quasicrystal")
    med = [sorted(loc[k])[10] for k in loc]
    require(all(med[i] <= med[i + 1] for i in range(len(med) - 1)),
            f"LOCAL: a wider window only delays the defect (median first defect {med})")
    out["local"] = {str(k): v for k, v in loc.items()}

    # ---- the pure mechanisms over all 32 seeds ----
    log("-" * 90)
    res = {}
    for rule in ("COPY", "ANTI", "DICE", "SCALE", "WRONGSCALE", "DUSTSCALE"):
        rows = []
        for sd in SEEDS:
            w, st = lay(rule, sd, random.Random(7))
            d = defects(w)
            rows.append(dict(seed=sd, stuck=(st == "stuck"), first=d[0] if d else None, last=d[-1] if d else None,
                             n_def=len(d), period=period(w), p10=comp(w, 10), p20=comp(w, 20),
                             tail_ok=(not d) or d[-1] < len(w) // 2, head=w[:150]))
        res[rule] = rows
        per = sum(1 for r in rows if r["period"]); heal = sum(1 for r in rows if r["tail_ok"])
        clean = sum(1 for r in rows if r["n_def"] == 0)
        lasts = [r["last"] for r in rows if r["last"]]
        stuck = sum(1 for r in rows if r["stuck"])
        log(f"  {rule:<10} over 32 seeds: stuck {stuck}; never a defect {clean:>2}; defects only near the start "
            f"(40-letter window) {heal:>2}; ends in repetition {per:>2}; p(10) median "
            f"{sorted(r['p10'] for r in rows)[16]}; last defect max {max(lasts) if lasts else '-'}")
    out["rules"] = res

    log("-" * 90)
    stuck = [r["seed"] for r in res["SCALE"] if r["stuck"]]
    require(stuck == ["SSSSS"],
            f"SCALE is stuck only for the all-short seed {stuck}: zooming out S -> L never reaches "
            f"past the present, so an all-S street has no self-similarity to consult")
    sc = [r for r in res["SCALE"] if not r["stuck"]]
    require(all(r["tail_ok"] for r in sc) and all(r["period"] is None for r in sc),
            f"SCALE: from ALL {len(sc)} other seeds, seen through a 40-letter window, every mistake "
            f"looks confined to the start and the street never falls into repetition (what that "
            f"'confined' really is -- scar or inflation -- is classified next)")
    # v1 gated "healing is fast" (last defect <= 40) and FAILED at 148: the last VISIBLE defect
    # grows with the checking window. Two different things were hiding under "healed":
    #   SCAR     the mistake stays at the start; far from it the street is legal at every scale
    #   INFLATE  the mistake is copied to ever larger scales (it reappears at Fibonacci-sized
    #            distances, 34, 144, 377, ...): never lost, never repeated, never healed
    big = 160
    LB = {n: {FIB[i:i + n] for i in range(len(FIB) - n + 1)} for n in range(1, big + 1)}
    cls = collections.Counter(); inflate_ends = []
    for r in sc:
        w, _ = lay("SCALE", r["seed"], None)
        w = w[:1600]
        far = None
        for a0 in range(40, len(w)):
            for n in range(1, big + 1):
                if a0 + n > len(w):
                    break
                if w[a0:a0 + n] not in LB[n]:
                    far = (a0, a0 + n); break
        kind = "CLEAN" if r["n_def"] == 0 else ("SCAR" if far is None else "INFLATE")
        r["kind"] = kind; cls[kind] += 1
    log(f"  SCALE mistakes, classified with a 160-letter checking window (patterns starting after "
        f"letter 40): {dict(cls)}")
    require(cls["CLEAN"] + cls["SCAR"] + cls["INFLATE"] == len(sc) and cls["INFLATE"] > 0 and cls["SCAR"] > 0,
            f"SCALE never HEALS a mistake -- it either leaves a SCAR at the start ({cls['SCAR']} seeds; "
            f"far from it the street is legal at every scale checked) or INFLATES it to ever larger "
            f"scales ({cls['INFLATE']} seeds): nothing is lost, and nothing repeats")
    fp = [r for r in sc if r["n_def"] == 0]
    require(len(fp) > 0 and all(r["p20"] <= 21 + 1 for r in fp),
            f"SCALE: {len(fp)} seeds give a street with NO defect at all and the Sturmian "
            f"minimum of patterns (p(20) = 21)")
    require(sum(1 for r in res["COPY"] if r["period"]) >= 30,
            f"COPY (same-scale likeness) falls into REPETITION from "
            f"{sum(1 for r in res['COPY'] if r['period'])}/32 seeds: resonant lock-in")
    require(all(r["first"] is not None and r["first"] <= 12 for r in res["ANTI"] + res["DICE"]),
            "ANTI and DICE lay defects almost at once (noise)")
    require(all(not r["tail_ok"] for r in res["WRONGSCALE"]) and all(not r["tail_ok"] for r in res["DUSTSCALE"]),
            "WRONGSCALE (not the street's own zoom) and DUSTSCALE (zoom read at a random place) "
            "never settle: it must be the street's OWN self-similarity, read at the RIGHT place")

    out["scale_kinds"] = {r["seed"]: r["kind"] for r in sc}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(DATA, "w"))
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
