#!/usr/bin/env python3
"""
penrose_growth.py -- "more now" on the Penrose tiling: does the growing now fill space in every
direction, and what do momentum and branching do?  (2-D follow-on to ../geometric_clock/ Part B.)

In 1-D (geometric_clock Part B) k=2 TICK growth reduced, at the level of the houses held by the
now, to: each event adds the next house along the street, and nothing ever leaves. Here the same
held-set accretion runs on the exact Penrose tiling of ../penrose_address_environment/, using
the ROADS found in ../least_resistance_paths/: a road is (family j, heading s); its next vertex
from x keeps the grid coordinate K_j fixed and steps forward along s*t_j (t_j = e_j turned 90
degrees), taking the MOST forward option at a fork (momentum).

The now is a set of held tiling vertices; each newborn carries the road it was born on.
  RAY   an event at walker (x, road) adds the next vertex along its OWN road, if not held.
  FORK  momentum first: continue along the own road if the way ahead is free; if it is taken,
        turn onto the GENTLEST free road at x (smallest turn from the current heading); a walker
        with no free road left is exhausted and leaves the clock.
Clocks:
  QUEUE deterministic: walkers act in birth order, round and round (imports nothing).
  DICE  a uniformly random live walker acts (imports randomness).
Seed: one vertex near the centre, with two walkers heading both ways along family 0's road.

Checked every event: every new vertex is a tiling neighbour of a held vertex (a legal bond) and
nothing ever leaves the now. Measured: houses held vs events; radius growth law; roundness
(extent in 20 directions, min/max); holes (unheld vertices fully enclosed by the now);
boundary share. asserts + nonzero exit. Integer K steps exact; distances float.
"""
from __future__ import annotations
import os, sys, math, random, collections, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "penrose_address_environment"))
import penrose_address as P

REPORT = os.path.join(HERE, "results", "penrose_growth_report.txt")
DATA = os.path.join(HERE, "results", "penrose_growth.json")
LINES, FAILS = [], []
R = 60.0
T = 4000
SEED = 20260924
SAMPLE = sorted({int(round(10 ** (e / 8))) for e in range(8, 29)} | {T})


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


faces, VERTS, EDGES = P.build(R)
ADJ = collections.defaultdict(set)
for _e in EDGES:
    _a, _b = tuple(_e); ADJ[_a].add(_b); ADJ[_b].add(_a)
POS = {K: P.par(K) for K in VERTS}
EDGE_R = R - 3
ROADS = [(j, s) for j in range(5) for s in (1, -1)]


def heading(road):
    j, s = road
    return (-s * P.EV[j][1], s * P.EV[j][0])


def ang(u, v):
    c = max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / math.hypot(*u) / math.hypot(*v)))
    return math.acos(c)


def road_next(x, road):
    j, _ = road; h = heading(road)
    fwd = [W for W in ADJ[x] if W[j] == x[j]
           and (POS[W][0] - POS[x][0]) * h[0] + (POS[W][1] - POS[x][1]) * h[1] > 1e-9]
    if not fwd:
        return None
    return max(fwd, key=lambda W: ((POS[W][0] - POS[x][0]) * h[0] + (POS[W][1] - POS[x][1]) * h[1], W))


def grow(rule, clock, rng):
    """uniform over ELIGIBLE moves, as everywhere in the pilot: a walker with no free move has
    no eligible event and is never chosen. The held set only grows, so a blocked walker stays
    blocked forever -- it is dropped from the clock at no cost."""
    c0 = min(VERTS, key=lambda K: math.hypot(*POS[K]))
    held = {c0}; order = [c0]
    walkers = [(c0, (0, 1)), (c0, (0, -1))]            # (vertex, road)
    live = collections.deque(range(len(walkers)))
    legal = True; series = []; t = 0

    def move(i):
        x, road = walkers[i]
        if rule == "RAY":
            w = road_next(x, road)
            return (w, road) if (w is not None and w not in held) else None
        for r in sorted(ROADS, key=lambda r: (ang(heading(r), heading(road)), r)):
            w = road_next(x, r)
            if w is not None and w not in held:
                return (w, r)
        return None

    while t < T and live:
        if clock == "QUEUE":
            i = live.popleft()
        else:
            k = rng.randrange(len(live)); live.rotate(-k); i = live.popleft()
        new = move(i)
        if new is None:
            continue                                       # ineligible: dropped, no event
        t += 1
        w, r = new
        legal &= w in ADJ[walkers[i][0]]
        held.add(w); order.append(w); walkers.append((w, r))
        live.append(i); live.append(len(walkers) - 1)
        if t in SAMPLE:
            rad = max(math.hypot(POS[K][0] - POS[c0][0], POS[K][1] - POS[c0][1]) for K in held)
            series.append((t, len(held), rad))
    rad = max(math.hypot(POS[K][0] - POS[c0][0], POS[K][1] - POS[c0][1]) for K in held)
    far = max(math.hypot(*POS[K]) for K in held)
    return dict(held=held, order=order, series=series, legal=legal, c0=c0, t=t, frozen=not live,
                radius=rad, far=far)


def shape(held, c0):
    ext = []
    for k in range(20):
        th = math.pi * k / 10; u = (math.cos(th), math.sin(th))
        ext.append(max((POS[K][0] - POS[c0][0]) * u[0] + (POS[K][1] - POS[c0][1]) * u[1] for K in held))
    roundness = min(ext) / max(ext)
    seen, holes, hole_verts = set(), 0, 0                  # unheld components not reaching edge
    for v in VERTS:
        if v in held or v in seen:
            continue
        comp, q, edge = [v], [v], False; seen.add(v)
        while q:
            u = q.pop()
            if math.hypot(*POS[u]) > EDGE_R:
                edge = True
            for w in ADJ[u]:
                if w not in held and w not in seen:
                    seen.add(w); comp.append(w); q.append(w)
        if not edge:
            holes += 1; hole_verts += len(comp)
    boundary = sum(1 for K in held if any(w not in held for w in ADJ[K]))
    return dict(roundness=roundness, holes=holes, hole_verts=hole_verts,
                boundary_share=boundary / len(held))


def fit(series, tmin=100):
    pts = [(math.log(t), math.log(r)) for t, _, r in series if t >= tmin and r > 0]
    if len(pts) < 2:
        return float("nan")
    mx = sum(x for x, _ in pts) / len(pts); my = sum(y for _, y in pts) / len(pts)
    return sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)


def main():
    log("=" * 90)
    log("PENROSE GROWTH -- does the growing now fill space in every direction?")
    log("=" * 90)
    log(f"  tiling patch radius {R}: {len(VERTS)} vertices; up to {T} events per run")
    rng = random.Random(SEED)
    res, out = {}, {}
    for rule in ("RAY", "FORK"):
        for clock in ("QUEUE", "DICE"):
            g = grow(rule, clock, rng); s = shape(g["held"], g["c0"])
            beta = fit(g["series"])
            res[(rule, clock)] = (g, s, beta)
            t_end = g["t"]
            log("-" * 90)
            log(f"[{rule} / {clock}] events {t_end}; houses held {len(g['held'])}"
                f"{'; FROZEN (no eligible move left), furthest house at radius %.1f of the %.0f patch' % (g['far'], R) if g['frozen'] else ''}")
            log(f"    radius growth: R ~ t^{beta:.2f};  roundness (min/max extent over 20 directions) "
                f"{s['roundness']:.2f};  holes {s['holes']} ({s['hole_verts']} vertices);  "
                f"boundary share {s['boundary_share']:.2f}")
            out[f"{rule}_{clock}"] = dict(series=g["series"], t=t_end, frozen=g["frozen"],
                                          held=len(g["held"]), beta=beta, **s,
                                          pts=[POS[K] for K in g["order"]])
    log("=" * 90)
    log("[checks]")
    for k, (g, s, b) in res.items():
        require(g["legal"], f"{k[0]}/{k[1]}: every new vertex is a tiling neighbour of the walker "
                            f"that grew it (legal bond); nothing ever leaves the now (held set only grows)")
    for k, (g, s, b) in res.items():
        require(len(g["held"]) == g["t"] + 1,
                f"{k[0]}/{k[1]}: every event adds exactly one new house (held = events + 1 = "
                f"{len(g['held'])}): more now = more space, 1:1")
    for clock in ("QUEUE", "DICE"):
        g, s, b = res[("RAY", clock)]
        require(g["frozen"] and g["far"] > R - 10 and s["roundness"] < 0.2,
                f"RAY/{clock}: momentum alone grows the now as a LINE -- both ends run along the "
                f"road until it leaves the patch (furthest house at {g['far']:.1f} of {R:.0f}), "
                f"then it freezes with {len(g['held'])} houses (roundness {s['roundness']:.2f})")
        g, s, b = res[("FORK", clock)]
        require(not g["frozen"] and s["roundness"] > 0.6 and 0.4 < b < 0.6,
                f"FORK/{clock}: momentum + branching fills space in EVERY direction -- a blob "
                f"(roundness {s['roundness']:.2f}) whose radius grows like t^{b:.2f} (area ~ t)")
    extra = []
    for k in range(4):                                  # more DICE seeds for the comparison
        g = grow("FORK", "DICE", random.Random(SEED + 100 + k)); sh = shape(g["held"], g["c0"])
        extra.append((sh["roundness"], sh["holes"], fit(g["series"])))
    dice_all = [(res[("FORK", "DICE")][1]["roundness"], res[("FORK", "DICE")][1]["holes"],
                 res[("FORK", "DICE")][2])] + extra
    log(f"  FORK/DICE over 5 seeds: roundness {', '.join(f'{r:.2f}' for r, _, _ in dice_all)}; "
        f"holes {', '.join(str(h) for _, h, _ in dice_all)}; radius exponent "
        f"{', '.join(f'{b:.2f}' for _, _, b in dice_all)}")
    rq = res[("FORK", "QUEUE")][1]
    require(all(rq["roundness"] > r for r, _, _ in dice_all) and all(rq["holes"] < h for _, h, _ in dice_all),
            f"the deterministic QUEUE clock grows a ROUNDER now with FEWER holes than dice, against "
            f"every one of 5 dice seeds (roundness {rq['roundness']:.2f} vs {min(r for r, _, _ in dice_all):.2f}-"
            f"{max(r for r, _, _ in dice_all):.2f}; holes {rq['holes']} vs "
            f"{min(h for _, h, _ in dice_all)}-{max(h for _, h, _ in dice_all)})")
    out["dice_seeds"] = dice_all
    sq, sd = res[("FORK", "QUEUE")][1], res[("FORK", "DICE")][1]
    log(f"  FORK: QUEUE vs DICE -- roundness {sq['roundness']:.2f} vs {sd['roundness']:.2f}; "
        f"holes {sq['holes']} vs {sd['holes']}; boundary share {sq['boundary_share']:.3f} vs "
        f"{sd['boundary_share']:.3f}")
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
