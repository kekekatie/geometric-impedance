#!/usr/bin/env python3
"""
geometric_clock.py -- can the WHEN come from the geometry too? And can the NOW grow?

Follows ../tick_forward/ (TICK: a newborn's hidden address is its parent's, stepped by the
window's own map f). There, WHAT is written cost 0 random bits, but WHEN came from a dice-roll
scheduler. Katie's picture (../../../THREE_COMMANDMENTS.md, addendum 2026-09-24): the timing IS
the geometry -- the track laid as it is ridden, a momentum-like falling forward into the next
slice of now, and the now itself embiggening.

Street coordinates. Every TICK address lies on ONE orbit of f, so an address is a house number
j on the hidden street: f is j -> j+1, the backward map b is j -> j-1 (checked exactly below).
T(j) = the tile to the right of house j (S or L), computed EXACTLY in Z[tau]; the circle order
of addresses (for the geometric clocks) uses the exact address's float value (orbit points are
>= ~1e-4 apart here; float error ~1e-12).

PART A (k=1, the collapsed universe: m lone pairs, pair i = legal bond (j_i, j_i+1)).
  DICE   (the tick_forward scheduler) pick a pair with weight 1/l, then a fair coin:
         stutter (re-lay the same tile) or advance (j_i += 1).
  SWEEP  the next pair to act is the one whose address comes NEXT around the window after the
         last one that acted; it always ADVANCES (falling forward: no stutters).
  HAND   a clock hand that is itself a TICK walker (h -> f(h) each event) points at the circle;
         the pair whose address comes first at-or-after the hand acts, and advances.
  SWEEP and HAND import nothing: they are deterministic functions of the geometry.
  Measures: random bits imported per event; per-pair content; the GLOBAL record (the tile laid
  by each event, in event order, across the whole universe) -- its pattern complexity p(n);
  fairness (does every pair keep advancing?).

PART B (k=2: the now can grow). BUD at k sprouts k tips (../endogenous_growth_audit/:
  DeltaA = k-1 exactly). TICK at k=2: BUD(x,y) turns y quiet and sprouts z1 at house j_x+1
  (bond x-z1) and z2 at house j_x-1 (bond z2-x): the keeper's next AND previous house.
  Claim checked: every active bond stays a legal tile, and the depositor's house is always
  re-born in the now (y is x's neighbour, so y's house is j_x+1 or j_x-1) -- so the SET of
  houses held by the now NEVER loses a member: "nothing unbecomes". Measures: active count
  A(t) (= A0 + t exactly), the extent D(t) = number of distinct houses held, contiguity (is
  the now one unbroken stretch of street?), and the growth law D(t) ~ t^alpha per clock.

asserts + nonzero exit. DICE runs are seeded Monte Carlo; SWEEP/HAND are deterministic.
"""
from __future__ import annotations
import os, sys, math, random, json, bisect, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fibonacci_address_environment"))
import fibonacci_cutproject as F

REPORT = os.path.join(HERE, "results", "geometric_clock_report.txt")
DATA = os.path.join(HERE, "results", "geometric_clock.json")
LINES, FAILS = [], []
SEED = 20260924
M_A = 4000            # Part A events
M_B = 4000            # Part B events
N_MAX = 12
SAMPLE_T = sorted({int(round(10 ** (e / 8))) for e in range(8, 29)} | {4000})   # 10 .. 4000, log-spaced
DICE_SEEDS = 5
JR = 12000            # street houses precomputed on each side of house 0


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


# ---------------------------------------------------------------- the hidden street
PTS = F.generate(60)
Q0 = PTS[len(PTS) // 2][1]                          # house 0 = a chain site's address
_fw, _bw = [Q0], [Q0]
for _ in range(JR):
    _fw.append(F.f_step(_fw[-1])[1]); _bw.append(F.b_step(_bw[-1])[1])
ADDR = {j: _fw[j] for j in range(JR + 1)}
ADDR.update({-j: _bw[j] for j in range(1, JR + 1)})
TILE = {j: F.f_step(ADDR[j])[0] for j in ADDR}      # exact
POS = {j: ADDR[j].real() for j in ADDR}             # circle position in [0, tau)
W = {"S": 1.0, "L": F.TAU_F - 1.0}                   # rate 1/l


def factors(words, n):
    s = set()
    for w in words:
        for i in range(len(w) - n + 1):
            s.add(w[i:i + n])
    return s


def complexity(words):
    return [len(factors(words, n)) for n in range(1, N_MAX + 1)]


# ================================================================== PART A
def part_a_run(clock, m, rng):
    js = [2 * i for i in range(m)]                   # matching seed: chain pairs (0,1),(2,3),...
    content = [[TILE[j]] for j in js]
    glob, bits, adv = [], 0.0, [0] * m
    ptr = POS[js[0]] - 1e-9                          # SWEEP pointer
    hand = -1                                        # HAND walker's house
    coincide = 0
    for _ in range(M_A):
        if clock == "DICE":
            ws = [W[TILE[j]] for j in js]; tot = sum(ws)
            ps = [w / tot for w in ws]
            bits += 1 + -sum(p * math.log2(p) for p in ps)       # which pair + which direction
            r = rng.random() * tot; i = 0
            while r > ws[i]:
                r -= ws[i]; i += 1
            if rng.random() < 0.5:                   # stutter
                glob.append(TILE[js[i]]); continue
        elif clock == "SWEEP":
            order = sorted(range(m), key=lambda k: POS[js[k]])
            keys = [POS[js[k]] for k in order]
            p = bisect.bisect_right(keys, ptr)
            i = order[p % m]; ptr = POS[js[i]]
        else:                                        # HAND
            order = sorted(range(m), key=lambda k: POS[js[k]])
            keys = [POS[js[k]] for k in order]
            p = bisect.bisect_left(keys, POS[hand])
            i = order[p % m]; hand += 1
        js[i] += 1; adv[i] += 1                      # advance: new pair (j+1, j+2)
        content[i].append(TILE[js[i]]); glob.append(TILE[js[i]])
        coincide += len(js) - len(set(js))
    return dict(content=["".join(c) for c in content], glob="".join(glob),
                bits=bits / M_A, adv=adv, coincide=coincide)


# ================================================================== PART B
class K2World:
    """k=2 TICK. vertices: id -> house j. active bonds: oriented (left_id, right_id), right = left+1."""

    def __init__(self, j0):
        self.house = {0: j0, 1: j0 + 1}; self.nxt = 2
        self.bonds = {(0, 1)}
        self.adj = collections.defaultdict(set); self.adj[0].add((0, 1)); self.adj[1].add((0, 1))

    def add_bond(self, b):
        self.bonds.add(b); self.adj[b[0]].add(b); self.adj[b[1]].add(b)

    def bud(self, x, y):
        for b in list(self.adj[y]):                  # y goes quiet: its active bonds leave
            self.bonds.discard(b); self.adj[b[0]].discard(b); self.adj[b[1]].discard(b)
        del self.house[y]
        jx = self.house[x]
        z1, z2 = self.nxt, self.nxt + 1; self.nxt += 2
        self.house[z1] = jx + 1; self.house[z2] = jx - 1
        self.add_bond((x, z1)); self.add_bond((z2, x))

    def held(self):
        return set(self.house.values())


def part_b_run(clock, rng):
    Wd = K2World(0)
    ptr, hand = POS[0] - 1e-9, -1
    series, ok_legal, ok_mono, ok_reborn = [], True, True, True
    for t in range(1, M_B + 1):
        before = Wd.held()
        bl = list(Wd.bonds)
        if clock == "DICE":
            ws = [W[TILE[Wd.house[u]]] for u, v in bl]; tot = sum(ws)
            r = rng.random() * tot; i = 0
            while r > ws[i]:
                r -= ws[i]; i += 1
            u, v = bl[i]
            x, y = (u, v) if rng.random() < 0.5 else (v, u)
        else:
            bl.sort(key=lambda b: POS[Wd.house[b[0]]])
            keys = [POS[Wd.house[b[0]]] for b in bl]
            if clock == "SWEEP":
                p = bisect.bisect_right(keys, ptr); u, v = bl[p % len(bl)]; ptr = POS[Wd.house[u]]
            else:
                p = bisect.bisect_left(keys, POS[hand]); u, v = bl[p % len(bl)]; hand += 1
            x, y = v, u                              # always fall forward: right end keeps
        jy = Wd.house[y]
        Wd.bud(x, y)
        after = Wd.held()
        ok_reborn &= (jy in after)
        ok_mono &= before <= after
        ok_legal &= all(Wd.house[b[1]] == Wd.house[b[0]] + 1 for b in Wd.bonds)
        if t in SAMPLE_T:
            h = sorted(after)
            series.append((t, len(Wd.house), len(after), h[-1] - h[0] + 1 == len(h)))
    return dict(series=series, legal=ok_legal, mono=ok_mono, reborn=ok_reborn)


def slope(series, tmin=100):
    """least-squares slope of log D vs log t over t >= tmin."""
    pts = [(math.log(t), math.log(d)) for t, _, d, _ in series if t >= tmin]
    mx = sum(x for x, _ in pts) / len(pts); my = sum(y for _, y in pts) / len(pts)
    return sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)


# ================================================================== MAIN
def main():
    log("=" * 90)
    log("GEOMETRIC CLOCK -- can the WHEN come from the geometry? can the NOW grow?")
    log("=" * 90)
    require(all(F.b_step(ADDR[j + 1])[1] == ADDR[j] for j in range(-50, 50))
            and all(F.f_step(ADDR[j])[1] == ADDR[j + 1] for j in range(-50, 50)),
            "street coordinates exact: f is j -> j+1 and b is j -> j-1 on the TICK orbit")
    street = "".join(TILE[j] for j in range(-JR, JR))
    require(complexity([street]) == [n + 1 for n in range(1, N_MAX + 1)],
            "the hidden street's own tile word is Sturmian (n+1 patterns of length n)")
    rng = random.Random(SEED)
    out = {"A": {}, "B": {}}

    # ---------------- PART A
    m = 20
    log("-" * 90)
    log(f"PART A (k=1): the collapsed universe, {m} lone pairs, {M_A} events per clock")
    A = {c: part_a_run(c, m, rng) for c in ("DICE", "SWEEP", "HAND")}
    for c, R in A.items():
        cg = complexity([R["glob"]]); cc = complexity(R["content"])
        out["A"][c] = dict(bits=R["bits"], glob_complexity=cg, content_complexity=cc,
                           adv_min=min(R["adv"]), adv_max=max(R["adv"]), coincide=R["coincide"])
        log(f"  [{c}] random bits imported per event: {R['bits']:.3f}")
        log(f"      per-pair content complexity p(n): {cc}")
        log(f"      GLOBAL record complexity p(n):    {cg}")
        log(f"      advances per pair: min {min(R['adv'])}, max {max(R['adv'])}; "
            f"simultaneous same-house coincidences: {R['coincide']}")
    for c in ("SWEEP", "HAND"):
        require(A[c]["bits"] == 0.0, f"{c}: imports 0 random bits (deterministic in the geometry)")
        require(out["A"][c]["content_complexity"] == [n + 1 for n in range(1, N_MAX + 1)],
                f"{c}: every pair still writes the Sturmian record (n+1)")
    require(min(A["SWEEP"]["adv"]) > 0 and max(A["SWEEP"]["adv"]) - min(A["SWEEP"]["adv"]) <= 2,
            f"SWEEP is FAIR: every pair keeps falling forward ({min(A['SWEEP']['adv'])}-"
            f"{max(A['SWEEP']['adv'])} advances each) and no two pairs ever share a house "
            f"({A['SWEEP']['coincide']} coincidences)")
    require(max(A["HAND"]["adv"]) >= M_A - 1,
            f"HAND PHASE-LOCKS (finding, not a bug; v1 of this gate predicted fairness and failed): "
            f"the hand steps by f exactly as the pair just ahead of it does, so after the first "
            f"event they co-rotate forever -- one pair takes {max(A['HAND']['adv'])} of {M_A} "
            f"events, every other pair freezes")
    gs = A["SWEEP"]["glob"]
    per = [d for d in range(1, len(gs) // 2) if all(gs[i] == gs[i + d] for i in range(len(gs) - d))]
    pl = [len(factors([gs], n)) for n in range(1, 41)]
    out["A"]["SWEEP"]["glob_complexity_40"] = pl
    require(not per and pl[:12] == [2 * n for n in range(1, 13)] and pl[-1] <= 4 * 40,
            f"SWEEP's GLOBAL record (the whole universe's history) NEVER repeats (no period "
            f"<= half its length), and its variety grows only LINEARLY: p(n) = 2n for n <= 12, "
            f"p(40) = {pl[-1]} (DICE: exponential) -- zero-entropy order, not noise")
    require(A["DICE"]["bits"] > 5, f"DICE imports {A['DICE']['bits']:.2f} bits per event "
                                   f"(which pair ~log2(20) + which direction 1)")
    gd = out["A"]["DICE"]["glob_complexity"]
    log(f"  => GLOBAL record at n=12: DICE {gd[-1]}, SWEEP {out['A']['SWEEP']['glob_complexity'][-1]}, "
        f"HAND {out['A']['HAND']['glob_complexity'][-1]}  (Sturmian would be 13)")

    # ---------------- PART B
    log("-" * 90)
    log(f"PART B (k=2): TICK sprouts the keeper's next AND previous house; {M_B} events per clock")
    log("  first, k=1 for contrast: DeltaA = 0 exactly -- the now keeps a fixed size and slides")
    B = {c: part_b_run(c, rng) for c in ("SWEEP", "HAND")}
    dice_runs = [part_b_run("DICE", rng) for _ in range(DICE_SEEDS)]
    B["DICE"] = dice_runs[0]
    for c, R in B.items():
        out["B"][c] = dict(series=R["series"], alpha=slope(R["series"]))
        log(f"  [{c}{' seed 1' if c == 'DICE' else ''}]  t: active vertices A(t), houses held D(t), "
            f"one unbroken stretch?")
        for t, a, d, cont in R["series"][::3] + [R["series"][-1]]:
            log(f"      t={t:>5}   A={a:>5}   D={d:>5}   contiguous={cont}")
        log(f"      growth law D(t) ~ t^{slope(R['series']):.3f}  (fit over t >= 100)")
    alphas = [slope(R["series"]) for R in dice_runs]
    out["B"]["DICE_all"] = [R["series"] for R in dice_runs]
    out["B"]["DICE_alphas"] = alphas
    log(f"  DICE over {DICE_SEEDS} seeds: alpha = {', '.join(f'{a:.3f}' for a in alphas)}; "
        f"mean {sum(alphas) / len(alphas):.3f};  final extent D(4000) = "
        f"{', '.join(str(R['series'][-1][2]) for R in dice_runs)} houses for 4002 vertices")
    require(all(d == a for _, a, d, _ in B["SWEEP"]["series"]),
            "SWEEP: EVERY event claims a brand-new house -- D(t) = A(t) = t+2: all the 'more now' "
            "becomes more space, 1:1 (no crowding)")
    require(all(0.3 < a < 0.65 for a in alphas),
            f"DICE: the extent grows only diffusively, D ~ t^alpha with alpha in (0.3, 0.65) for "
            f"every seed (mean {sum(alphas) / len(alphas):.3f}; ~1/2 expected: new houses appear "
            f"only at the two ends of a stretch holding ~t/D vertices per house)")
    for c, R in list(B.items()) + [(f"DICE seed {k + 1}", R) for k, R in enumerate(dice_runs[1:], 1)]:
        require(R["legal"], f"{c}: every active bond stays a legal Fibonacci tile at every event")
        require(R["reborn"] and R["mono"],
                f"{c}: the depositor's house is re-born in the now at every event; the set of "
                f"houses held NEVER loses a member ('nothing unbecomes')")
        require(all(a == 2 + t for t, a, _, _ in R["series"]),
                f"{c}: active count A(t) = 2 + t exactly (DeltaA = k-1 = 1: 'more now')")
        require(all(cont for *_, cont in R["series"]),
                f"{c}: the now is always ONE unbroken stretch of the hidden street")

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(DATA, "w"), indent=1)
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
