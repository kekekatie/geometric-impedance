#!/usr/bin/env python3
"""
crossroads_test.py -- Gemini's "intersection crash": when the growing tiling has to GUESS, does the
change it makes travel down one road, or down both roads that cross there?

Uses forced-first local growth from laying_the_tiling.py (never jams, but guesses 3-4 times per
run and so builds a sibling Penrose universe). Here every guess is RECORDED: where it happened
(the frontier edge), and whether the tile chosen differs from the self-similar tiling (a
DIVERGENT guess -- the moment the growth steered into a sibling universe). The differing rhombi
form thin bands along road directions (worm_test.py). For each band we find the divergent guess
it grows from (the guess nearest its inner end), then ask:
  * how many bands leave each divergent guess?
  * in which road directions?
  -> one band = the change travels down ONE road; two bands in two directions = BOTH roads.
Pre-registered expectation (written before running): each divergent guess starts exactly ONE band
(a guess picks one tile at one edge, and the difference it seeds lives on one road).
Recorded honestly either way. asserts + nonzero exit on the structural checks only.
"""
from __future__ import annotations
import os, sys, math, random, collections, json
import laying_the_tiling as T
import worm_test as W

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "crossroads_report.txt")
DATA = os.path.join(HERE, "results", "crossroads.json")
LINES, FAILS = [], []
RUNS = 30


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


REFSET = {T.canon(t) for t in T.REF}


def forced_with_log(seed, rng):
    """forced-first growth, recording every guess: (step, edge midpoint, divergent?)."""
    P = T.Patch(seed); n0 = len(P.tris); guesses = []
    while len(P.tris) - n0 < T.MAX_TILES:
        fr = P.frontier()
        chosen, first, fe = None, None, None
        for e in fr[:40]:
            cs = P.candidates(*e[:3])
            if not cs:
                return P, guesses, "JAM"
            if len(cs) == 1:
                chosen = cs[0]; break
            if first is None:
                first, fe = cs, e
        if chosen is None:
            chosen = rng.choice(first)
            ref_ok = [T.canon(c) in REFSET for c in first]
            guesses.append(dict(step=len(P.tris) - n0, mid=(fe[0] + fe[1]) / 2,
                                n_options=len(first), divergent=T.canon(chosen) not in REFSET,
                                any_ref_option=any(ref_ok)))
        P.add(chosen)
    return P, guesses, "ok"


def bands(P):
    allr = W.rhombi(P.tris)
    diff = [i for i, (_, ts, _) in enumerate(allr) if any(T.canon(t) not in REFSET for t in ts)]
    edge_to = collections.defaultdict(list)
    for i in diff:
        for ek, _ in allr[i][2]:
            edge_to[ek].append(i)
    nb = collections.defaultdict(set)
    for ids in edge_to.values():
        for a in ids:
            for b in ids:
                if a != b:
                    nb[a].add(b)
    pieces, vis = [], set()
    for s0 in diff:
        if s0 in vis:
            continue
        c, st = [], [s0]; vis.add(s0)
        while st:
            u = st.pop(); c.append(u)
            for w in nb[u]:
                if w not in vis:
                    vis.add(w); st.append(w)
        pieces.append(c)
    out = []
    for c in pieces:
        cen = [sum(sum(t[1:]) for t in allr[i][1]) / 6 for i in c]
        el, ang = W.pca(cen)
        inner = min(cen, key=abs)                       # the band's end nearest the centre
        out.append(dict(size=len(c), axis=ang, elong=el, inner=inner, cen=cen))
    return out


def main():
    log("=" * 90)
    log("CROSSROADS TEST -- does a guess's change travel down one road, or both?")
    log("=" * 90)
    seed = T.seed_patch(0j, 3 * T.SCALE_LEN)
    rows, seen = [], {}
    for k in range(RUNS):
        P, gs, st = forced_with_log(seed, random.Random(T.SEED + k))
        bs = bands(P)
        div = [g for g in gs if g["divergent"]]
        # attach each band to the divergent guess nearest its inner end
        links = collections.defaultdict(list)
        for bi, b in enumerate(bs):
            if b["size"] < 5 or not div:
                continue
            gi = min(range(len(div)), key=lambda g: abs(div[g]["mid"] - b["inner"]))
            links[gi].append(bi)
        sig = tuple(sorted(b["size"] for b in bs))
        row = dict(run=k, status=st, n_guess=len(gs), n_div=len(div), bands=[(b["size"], round(b["axis"]))
                   for b in bs], links={gi: [(bs[bi]["size"], round(bs[bi]["axis"]),
                                              round(abs(div[gi]["mid"] - bs[bi]["inner"]) / T.SCALE_LEN, 1))
                                             for bi in bl] for gi, bl in links.items()},
                   div_steps=[g["step"] for g in div], every_guess_had_ref=all(g["any_ref_option"] for g in gs))
        rows.append(row)
        if sig not in seen:
            seen[sig] = k
            log(f"  run {k:>2}: {len(gs)} guesses, {len(div)} divergent (at steps {row['div_steps']}); "
                f"bands (size, axis deg): {row['bands']}")
            for gi, bl in row["links"].items():
                log(f"          divergent guess #{gi} (step {div[gi]['step']}, {div[gi]['n_options']} options) "
                    f"-> {len(bl)} band(s): " + ", ".join(f"{s} rhombi along {a} deg "
                                                           f"(inner end {d} tile-edges away)" for s, a, d in bl))
    log("-" * 90)
    per_guess = [len(bl) for r in rows for bl in r["links"].values()]
    dist = [d for r in rows for bl in r["links"].values() for _, _, d in bl]
    log(f"  distinct outcomes: {len(seen)}; divergent guesses with bands: {len(per_guess)}; bands per "
        f"divergent guess: {collections.Counter(per_guess)}")
    log(f"  inner end of each band to its guess: max {max(dist) if dist else '-'} tile-edges")
    require(all(r["status"] == "ok" for r in rows), "forced growth never jammed (as before)")
    require(all(r["every_guess_had_ref"] for r in rows),
            "at every guess, one of the options WAS the self-similar tile: the guess is a genuine fork "
            "between sibling universes, not a forced error")
    require(all(r["n_div"] >= 1 for r in rows) and dist and max(dist) <= 3,
            "every band starts right at a divergent guess (within 3 tile-edges): each seam grows FROM "
            "the moment of choice")
    both = sum(1 for n in per_guess if n >= 2)
    if all(n == 1 for n in per_guess):
        log("  RESULT: each divergent guess seeds exactly ONE band -- the change travels down ONE road "
            "(pre-registered expectation held)")
    else:
        log(f"  RESULT: {both} divergent guess(es) seed TWO OR MORE bands in different road directions -- "
            f"the change travels down BOTH roads there (pre-registered expectation of one road FAILED "
            f"for these)")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(rows, open(DATA, "w"), indent=1, default=str)
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
