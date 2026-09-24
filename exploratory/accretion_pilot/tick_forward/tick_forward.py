#!/usr/bin/env python3
"""
tick_forward.py -- what postcode does a newborn get? Katie's "topple" rule vs two controls.

Growth runs ON the Fibonacci chain (as in ../twins_mirror/): every site starts active, every
tile is an active bond; BUD at k=1, rate 1/l (the MOTION.md conductance choice). Every vertex
carries a hidden (perpendicular) address q in W = [0, tau). The only new ingredient is the
NEWBORN-ADDRESS rule for the tip z created by BUD(x, y) (keeper x):

  TICK    q_z = f(q_x)      the window's own "next house" step (rotation by 1 on the circle
                            R/tauZ; never returns to a previous point). Katie's topple:
                            "it cannot be the same as what came before".
  CLONE   q_z = q_x         a copy: the same as what came before.
  RANDOM  q_z ~ uniform W   unrelated: fresh randomness every birth.

Facts reused from ../fibonacci_address_environment/ (re-checked below): f_step(q) returns
(the tile to the RIGHT of the site with address q, the next site's address). So a bond (u,v)
is a LEGAL Fibonacci tile iff q_v = f(q_u), and its type is T(q_u).

What we measure (after the shape collapses -- the BUD-only lemma of ../pair_collision_toy/
says the active structure always ends as lone pairs, which keep budding forever):
  the RECORD each surviving pair keeps writing. Per event a pair either STUTTERS (re-lays the
  same address pair) or produces a NEW address pair. We split the record into
    CONTENT  the sequence of tile types of the distinct address pairs, in order (WHAT is written)
    TIMING   which events were stutters                                  (WHEN it is written)
  and ask: does content keep coming (novelty)? is it ever repeated? how complex is it?
  is it legal Fibonacci pattern? how much randomness does it cost?

Monte Carlo over the scheduler (seeded), with EXACT structural claims asserted per run
(Z[tau] exact addresses throughout). asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, random, math, json, collections
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fibonacci_address_environment"))
import fibonacci_cutproject as F                      # exact Z[tau], chain, f_step (no main)

REPORT = os.path.join(HERE, "results", "tick_forward_report.txt")
DATA = os.path.join(HERE, "results", "complexity.json")
LINES, FAILS = [], []
RULES = ("TICK", "CLONE", "RANDOM")
N_SITES, RUNS, M_AFTER, N_MAX, SEED = 40, 100, 400, 12, 20260924
W = {"S": 1.0, "L": F.TAU_F - 1.0}                   # 1/l ; only relative weights matter


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def f(q):
    return F.f_step(q)[1]


def T(q):
    return F.f_step(q)[0]


def random_address(rng):
    while True:                        # exact rational, uniform on a grid of spacing 1e-15
        q = F.Z(Fr(rng.randrange(0, 2 * 10 ** 15), 10 ** 15), 0)   # (a 1e-6 grid gave spurious
                                                                    # birthday collisions: v1 note)
        if F.in_window(q):
            return q


def newborn(rule, qx, rng):
    if rule == "TICK":
        return f(qx)
    if rule == "CLONE":
        return qx
    return random_address(rng)


# ------------------------------------------------------------------ growth on the chain
class World:
    """active vertices with addresses; ORIENTED active bonds (u, v): u 'left', v 'right'."""

    def __init__(self, chain_addrs):
        self.q = {i: a for i, a in enumerate(chain_addrs)}
        self.bonds = {(i, i + 1) for i in range(len(chain_addrs) - 1)}
        self.nxt = len(chain_addrs)

    def events(self):
        out = []
        for (u, v) in self.bonds:
            w = W[T(self.q[u])]
            out.append((u, v, (u, v), w)); out.append((v, u, (u, v), w))
        return out

    def bud(self, x, y, rule, rng):
        """BUD(x,y): y goes quiet (its bonds leave the active graph); tip z joins x as (x, z)."""
        z = self.nxt; self.nxt += 1
        self.q[z] = newborn(rule, self.q[x], rng)
        self.bonds = {b for b in self.bonds if y not in b}
        self.bonds.add((x, z))
        return (x, z)

    def is_matching(self):
        deg = collections.Counter(v for b in self.bonds for v in b)
        return all(d <= 1 for d in deg.values())

    def legal(self, b):
        return self.q[b[1]] == f(self.q[b[0]])


def pick(evs, rng):
    tot = sum(e[3] for e in evs); r = rng.random() * tot
    for e in evs:
        r -= e[3]
        if r <= 0:
            return e
    return evs[-1]


def run_once(rule, chain_addrs, rng):
    """grow until the shape collapses to a matching, then let each pair write M_AFTER events."""
    Wd = World(chain_addrs)
    illegal_before = 0; steps = 0
    while not Wd.is_matching():
        x, y, _, _ = pick(Wd.events(), rng)
        nb = Wd.bud(x, y, rule, rng); steps += 1
        illegal_before += (not Wd.legal(nb))
    lineages = []
    for (u, v) in sorted(Wd.bonds):
        qu, qv = Wd.q[u], Wd.q[v]
        pairs = [(qu, qv)]; timing = []; illegal = 0
        for _ in range(M_AFTER):                       # a lone pair: both directions weigh the same
            if rng.random() < 0.5:                     # BUD(u, v): keeper u (left)
                qu, qv = qu, newborn(rule, qu, rng)
            else:                                      # BUD(v, u): keeper v becomes the left end
                qu, qv = qv, newborn(rule, qv, rng)
            illegal += (qv != f(qu))
            new = (qu, qv) != pairs[-1]
            timing.append(0 if new else 1)            # 1 = stutter
            if new:
                pairs.append((qu, qv))
        lineages.append({"pairs": pairs, "timing": timing, "illegal": illegal})
    # MEETINGS: two different lineages of this world that independently reach the SAME address
    addrs = [set(a for pq in L["pairs"] for a in pq) for L in lineages]
    meets = sum(1 for i in range(len(addrs)) for j in range(i + 1, len(addrs)) if addrs[i] & addrs[j])
    return steps, illegal_before, lineages, meets


def factors(words, n):
    s = set()
    for w in words:
        for i in range(len(w) - n + 1):
            s.add(w[i:i + n])
    return s


def main():
    log("=" * 90)
    log("TICK-FORWARD -- the newborn's postcode: TICK (topple) vs CLONE (copy) vs RANDOM")
    log("=" * 90)
    pts = F.generate(60); g = F.gaps_of(pts)
    require(all(F.f_step(pts[i][1]) == (g[i], pts[i + 1][1]) for i in range(len(pts) - 1)),
            "geometry re-checked: f_step(q) = (tile to the right, next site's address) at every site")
    fib_word = "".join(g)
    FIB = {n: factors([fib_word], n) for n in range(1, N_MAX + 1)}
    require(all(len(FIB[n]) == n + 1 for n in range(1, N_MAX + 1)),
            f"the chain's own language is Sturmian: exactly n+1 distinct words of length n "
            f"(n=1..{N_MAX})")
    mid = len(pts) // 2 - N_SITES // 2
    chain = [pts[i][1] for i in range(mid, mid + N_SITES)]

    rng = random.Random(SEED)
    summary = {}
    for rule in RULES:
        allsteps, ill_before, lins, meet, npairs = [], 0, [], 0, 0
        for _ in range(RUNS):
            steps, ib, L, m = run_once(rule, chain, rng)
            allsteps.append(steps); ill_before += ib; lins.extend(L)
            meet += m; npairs += len(L) * (len(L) - 1) // 2
        content = ["".join(T(p[0]) for p in L["pairs"]) for L in lins]
        new_frac = sum(len(L["pairs"]) - 1 for L in lins) / (len(lins) * M_AFTER)
        repeats = sum(len(L["pairs"]) - len(set(L["pairs"])) for L in lins)
        ill_after = sum(L["illegal"] for L in lins)
        comp = [len(factors(content, n)) for n in range(1, N_MAX + 1)]
        legal_frac = []
        for n in (2, 4, 8, 12):
            tot = sum(max(0, len(w) - n + 1) for w in content)
            ok = sum(1 for w in content for i in range(len(w) - n + 1) if w[i:i + n] in FIB[n])
            legal_frac.append(ok / tot if tot else float("nan"))
        summary[rule] = dict(lineages=len(lins), collapse_steps=sum(allsteps) / RUNS,
                             illegal_before=ill_before, illegal_after=ill_after,
                             new_frac=new_frac, repeats=repeats, complexity=comp,
                             legal_frac=legal_frac, content=content, lins=lins,
                             meet=meet, npairs=npairs)
        log("-" * 90)
        log(f"[{rule}]  {RUNS} runs x {N_SITES}-site chain; collapse to lone pairs after "
            f"{sum(allsteps) / RUNS:.1f} events on average; {len(lins)} surviving pairs, "
            f"each then writes {M_AFTER} events")
        log(f"   new content per event        {new_frac:.3f}")
        log(f"   exact repeats of a pair      {repeats}")
        log(f"   illegal (non-tile) bonds     before collapse {ill_before}, after {ill_after}")
        log(f"   distinct content words p(n)  {comp}")
        log(f"   share of windows that are legal Fibonacci words (n=2,4,8,12)  "
            f"{', '.join(f'{x:.3f}' for x in legal_frac)}")
        log(f"   MEETINGS: lineage pairs (same world) sharing an exact address  {meet} of {npairs}")

    tk, cl, rd = summary["TICK"], summary["CLONE"], summary["RANDOM"]
    log("=" * 90)
    log("[checks]")
    require(tk["illegal_before"] == 0 and tk["illegal_after"] == 0,
            "TICK: every bond ever created is a legal Fibonacci tile -- the growth never leaves "
            "the quasicrystal (before AND after collapse)")
    require(cl["illegal_before"] + cl["illegal_after"] > 0 and rd["illegal_before"] + rd["illegal_after"] > 0,
            "CLONE and RANDOM both create illegal (non-tile) bonds")
    require(tk["repeats"] == 0, "TICK: no pair ever repeats an earlier address pair (the window's "
                                "step never returns: irrational rotation)")
    require(all(L["pairs"][k + 1][0] == L["pairs"][k][1] and L["pairs"][k + 1][1] == f(L["pairs"][k][1])
                for L in tk["lins"] for k in range(len(L["pairs"]) - 1)),
            "TICK: content is DETERMINED by the starting address (each new pair is the next step "
            "of the window orbit) -- zero random bits spent on WHAT is written")
    require(0.45 < tk["new_frac"] < 0.55,
            f"TICK: new content keeps coming at ~1/2 per event forever ({tk['new_frac']:.3f}); the "
            f"other ~1/2 are stutters -- the scheduler's coin decides WHEN, not WHAT")
    require(cl["new_frac"] < 0.01,
            f"CLONE: after its first event a pair writes nothing new ({cl['new_frac']:.4f} per event): "
            f"the record freezes")
    require(rd["new_frac"] > 0.99, f"RANDOM: every event writes new content ({rd['new_frac']:.3f})")
    require(tk["complexity"] == [n + 1 for n in range(1, N_MAX + 1)],
            f"TICK: content has EXACTLY n+1 distinct words of length n (n=1..{N_MAX}) -- the "
            f"minimal complexity any never-repeating sequence can have (Morse-Hedlund)")
    require(all(x == 1.0 for x in tk["legal_frac"]),
            "TICK: every window of content is a legal Fibonacci word")
    require(rd["complexity"][7] > 200 and rd["legal_frac"][3] < 0.01,
            f"RANDOM: complexity explodes (p(8)={rd['complexity'][7]} of 256 possible) and almost "
            f"no long window is legal (n=12: {rd['legal_frac'][3]:.4f})")
    require(tk["meet"] > 0 and rd["meet"] == 0,
            f"TICK: separate lineages MEET -- reach the identical hidden address ({tk['meet']} of "
            f"{tk['npairs']} lineage pairs: all walk ONE shared orbit, so meetings are structural, "
            f"not luck); RANDOM: never ({rd['meet']}) -- perfect twins arise only under the topple")
    h = -(1 / F.TAU_F) * math.log2(1 / F.TAU_F) - (1 - 1 / F.TAU_F) * math.log2(1 - 1 / F.TAU_F)
    log(f"  randomness cost per content symbol:  TICK 0 bits (determined),  CLONE 0 bits (but "
        f"no content),  RANDOM ~{h:.3f} bits (P(S)=1/tau)")

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({r: {"complexity": summary[r]["complexity"], "new_frac": summary[r]["new_frac"],
                   "legal_frac": summary[r]["legal_frac"]} for r in RULES},
              open(DATA, "w"), indent=1)
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
