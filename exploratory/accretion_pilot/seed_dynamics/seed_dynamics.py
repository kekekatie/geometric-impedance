#!/usr/bin/env python3
"""
seed_dynamics.py -- the seed rule as actual dynamics: resonance joins the growing 2-D now.

Follows ../seed_crystal/ (the census: for every gap a twin seed already waits at shallow
likeness depth). Here the seed rule RUNS alongside the road growth of ../penrose_growth/
(FORK: continue along your road, else the gentlest free turn; uniform over eligible moves).

  ROAD event  as in penrose_growth (queue clock).
  SEED event  every SEED_EVERY-th event. Candidates: tiling vertices NOT held but touching the
              now (>= 1 held neighbour -- the seed supplies the shape, the house joins at the
              now's surface: a legal bond, no floating islands). A candidate h is ELIGIBLE iff
              the now already holds a TWIN of h at likeness depth r (same layer, same exact
              radius-r neighbourhood). Among eligible candidates the MOST ENCLOSED (most held
              neighbours; ties -> smallest K) joins -- syrup crystallises where it is most
              supersaturated. The twin nearest in the world is recorded as the seed's SOURCE.
              If nothing is eligible, the slot falls back to a road event (nothing happens
              from resonance). A seeded house FILLS but starts no walker (same in every arm).
Arms (same schedule):
  NONE   no seed events (roads only) -- baseline.
  TWIN   real likeness at depth r in {2, 4, 6}.
  DUST   same slots, the most enclosed candidate joins with NO likeness required.
  FAKE   likeness judged by SHUFFLED class labels (same class sizes, no real shape), depth r.

Pre-registered predictions (written before the first run; gates below, failures recorded):
  P1  TWIN seeds leave FEWER gaps than NONE (averaged over snapshots).
  P2  shallow TWIN (r=2) behaves almost like DUST (nearly everything has a twin); deep TWIN
      (r=6) finds fewer eligible candidates, so more seed slots fall back to roads.
  P3  no lock-in: no single source twin supplies more than 20% of all seed events.
Also checked every event: every new house is a tiling neighbour of the now; nothing leaves.
asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, math, random, collections, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "penrose_growth"))
sys.path.insert(0, os.path.join(HERE, "..", "seed_crystal"))
sys.path.insert(0, os.path.join(HERE, "..", "penrose_address_environment"))
import penrose_growth as G
import seed_crystal as S                              # env(), holes_of()
import penrose_address as P

REPORT = os.path.join(HERE, "results", "seed_dynamics_report.txt")
DATA = os.path.join(HERE, "results", "seed_dynamics.json")
LINES, FAILS = [], []
T = 4000
SEED_EVERY = 5
DEPTHS = (2, 4, 6)
SNAPS = (500, 1000, 1500, 2000, 2500, 3000, 3500, 4000)
SEED = 20260925
REPS = 8
CORE = G.R - 10                                        # environments exact inside this radius


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


_ENV = {}


def E(K, r):
    if (K, r) not in _ENV:
        _ENV[(K, r)] = S.env(K, r)
    return _ENV[(K, r)]


def label(K, r, fake):
    key = (sum(K), E(K, r))
    return fake[r][key] if fake is not None else key


def build_fake(rng):
    """shuffle class labels among core vertices: same class sizes, no shape meaning."""
    fake = {}
    core = sorted(K for K in G.VERTS if math.hypot(*G.POS[K]) < CORE)
    for r in DEPTHS:
        keys = [(sum(K), E(K, r)) for K in core]
        shuffled = keys[:]; rng.shuffle(shuffled)
        m = {}
        for K, k2 in zip(core, shuffled):
            m[(sum(K), E(K, r))] = m.get((sum(K), E(K, r)), k2)
        # a true re-labelling of vertices (not classes): map vertex -> random class of same size
        vm = dict(zip(core, shuffled))
        fake[r] = vm
    return fake


def run(arm, r, fake=None, rng=None):
    c0 = min(G.VERTS, key=lambda K: math.hypot(*G.POS[K]))
    held = {c0}; order = [c0]
    walkers = [(c0, (0, 1)), (c0, (0, -1))]
    live = collections.deque(range(len(walkers)))
    present = collections.defaultdict(list)            # label -> held vertices with it
    frontier = set(G.ADJ[c0])

    def lab(K):
        if arm == "FAKE":
            return fake[r].get(K)
        return (sum(K), E(K, r))

    def join(w):
        held.add(w); order.append(w)
        frontier.discard(w)
        for n in G.ADJ[w]:
            if n not in held:
                frontier.add(n)
        if arm in ("TWIN", "FAKE") and math.hypot(*G.POS[w]) < CORE:
            present[lab(w)].append(w)

    if arm in ("TWIN", "FAKE") and math.hypot(*G.POS[c0]) < CORE:
        present[lab(c0)].append(c0)

    def road_move(i):
        x, road = walkers[i]
        for rd in sorted(G.ROADS, key=lambda q: (G.ang(G.heading(q), G.heading(road)), q)):
            w = G.road_next(x, rd)
            if w is not None and w not in held:
                return (w, rd)
        return None

    t, legal, seeds, fallbacks, sources, gap_series = 0, True, 0, 0, collections.Counter(), []
    while t < T:
        seeded = False
        if arm != "NONE" and (t + 1) % SEED_EVERY == 0:
            cands = [h for h in frontier if math.hypot(*G.POS[h]) < CORE]
            if arm in ("TWIN", "FAKE"):
                cands = [h for h in cands if lab(h) is not None and present.get(lab(h))]
            if cands:
                h = max(cands, key=lambda v: (sum(1 for n in G.ADJ[v] if n in held), tuple(-x for x in v)))
                legal &= any(n in held for n in G.ADJ[h])
                if arm in ("TWIN", "FAKE"):
                    src = min(present[lab(h)], key=lambda s: math.hypot(G.POS[s][0] - G.POS[h][0], G.POS[s][1] - G.POS[h][1]))
                    sources[src] += 1
                t += 1; seeds += 1; join(h)          # seeded houses fill; they start no walker
                seeded = True                        # (v1 gave each a fixed-heading walker: that
                                                     # biased the shape in every seeded arm)
            else:
                fallbacks += 1
        if not seeded:
            moved = False
            while live and not moved:
                if rng is not None:                  # dice clock for road events
                    k = rng.randrange(len(live)); live.rotate(-k)
                i = live.popleft()
                nm = road_move(i)
                if nm is None:
                    continue
                w, rd = nm
                legal &= w in G.ADJ[walkers[i][0]]
                t += 1; join(w); walkers.append((w, rd))
                live.append(i); live.append(len(walkers) - 1); moved = True
            if not moved:
                break
        if t in SNAPS and (not gap_series or gap_series[-1][0] != t):
            gap_series.append((t, len(S.holes_of(held))))
    sh = G.shape(held, c0)
    top = max(sources.values()) / seeds if seeds and sources else 0.0
    return dict(t=t, held=len(held), legal=legal, seeds=seeds, fallbacks=fallbacks,
                gaps=gap_series, mean_gaps=sum(g for _, g in gap_series) / len(gap_series),
                roundness=sh["roundness"], boundary=sh["boundary_share"],
                n_sources=len(sources), top_share=top, pts=[G.POS[K] for K in order])


def main():
    log("=" * 90)
    log("SEED DYNAMICS -- the seed rule running alongside road growth on the Penrose tiling")
    log("=" * 90)
    log(f"  {T} events; a seed slot every {SEED_EVERY}th event; depths {DEPTHS}; gaps counted at {SNAPS}")
    fake = build_fake(random.Random(SEED))
    res = {}
    res[("NONE", 0)] = run("NONE", 0)
    res[("DUST", 0)] = run("DUST", 0)
    for r in DEPTHS:
        res[("TWIN", r)] = run("TWIN", r)
        res[("FAKE", r)] = run("FAKE", r, fake)
    log("-" * 90)
    log("  arm      r | houses | seed events | slots with nothing eligible | mean gaps | final gaps | "
        "roundness | distinct sources | top source share")
    for (arm, r), x in res.items():
        log(f"  {arm:<6} {r:>2} | {x['held']:>6} | {x['seeds']:>11} | {x['fallbacks']:>27} | "
            f"{x['mean_gaps']:>9.1f} | {x['gaps'][-1][1]:>10} | {x['roundness']:>9.2f} | "
            f"{x['n_sources']:>16} | {x['top_share']:>6.1%}")
    log("-" * 90)
    log(f"  REPLICATES: dice-driven road events, {REPS} runs per arm (fresh fake shuffle each run)")
    reps = collections.defaultdict(list)
    arms = [("NONE", 0), ("DUST", 0)] + [(a, r) for r in DEPTHS for a in ("TWIN", "FAKE")]
    for k in range(REPS):
        fk = build_fake(random.Random(SEED + 1000 + k))
        for a, r in arms:
            x = run(a, r, fk if a == "FAKE" else None, rng=random.Random(SEED + 17 * k))
            reps[(a, r)].append(x)
    ms = lambda L: (sum(L) / len(L), (sum((v - sum(L) / len(L)) ** 2 for v in L) / (len(L) - 1)) ** 0.5)
    summ = {}
    for key in arms:
        g = ms([x["mean_gaps"] for x in reps[key]]); rd = ms([x["roundness"] for x in reps[key]])
        fb = ms([x["fallbacks"] for x in reps[key]])
        summ[key] = dict(gaps=g, round=rd, fall=fb)
        log(f"  {key[0]:<6} {key[1]:>2} | mean gaps {g[0]:5.2f} +- {g[1]:4.2f} | roundness "
            f"{rd[0]:.3f} +- {rd[1]:.3f} | empty seed slots {fb[0]:5.1f}")
    log("=" * 90)
    log("[checks]")
    for (arm, r), x in res.items():
        require(x["legal"] and x["held"] == x["t"] + 1,
                f"{arm}{'' if not r else ' r=%d' % r}: every event adds one house touching the now "
                f"(legal bond); nothing leaves ({x['held']} houses from {x['t']} events)")
    base = res[("NONE", 0)]["mean_gaps"]
    for r in DEPTHS:
        require(res[("TWIN", r)]["mean_gaps"] < base,
                f"P1 r={r}: TWIN seeds leave fewer gaps than no seeds "
                f"({res[('TWIN', r)]['mean_gaps']:.1f} vs {base:.1f} on average)")
    require(res[("TWIN", 2)]["fallbacks"] <= res[("TWIN", 6)]["fallbacks"]
            and res[("TWIN", 6)]["seeds"] <= res[("TWIN", 2)]["seeds"],
            f"P2: deeper likeness finds nothing eligible more often (fallback slots r=2: "
            f"{res[('TWIN', 2)]['fallbacks']}, r=6: {res[('TWIN', 6)]['fallbacks']})")
    d2 = abs(res[("TWIN", 2)]["mean_gaps"] - res[("DUST", 0)]["mean_gaps"])
    log(f"  P2 (shallow twin ~ dust): mean gaps TWIN r=2 {res[('TWIN', 2)]['mean_gaps']:.1f} vs "
        f"DUST {res[('DUST', 0)]['mean_gaps']:.1f} (difference {d2:.1f})")
    for r in DEPTHS:
        require(res[("TWIN", r)]["top_share"] < 0.20,
                f"P3 r={r}: no lock-in -- the busiest source twin supplies "
                f"{res[('TWIN', r)]['top_share']:.1%} of seeds ({res[('TWIN', r)]['n_sources']} distinct sources)")
    se = lambda k: summ[k]["gaps"][1] / REPS ** 0.5
    for r in DEPTHS:
        tw, fk = summ[("TWIN", r)]["gaps"][0], summ[("FAKE", r)]["gaps"][0]
        sep = abs(tw - fk) / (se(("TWIN", r)) ** 2 + se(("FAKE", r)) ** 2) ** 0.5
        log(f"  replicates r={r}: TWIN {tw:.2f} vs FAKE {fk:.2f} mean gaps -> separation {sep:.1f} SE")
    none_g = summ[("NONE", 0)]["gaps"][0]
    require(all(summ[k]["gaps"][0] < none_g for k in arms if k[0] != "NONE"),
            f"replicates: EVERY seeding arm (dust, fake, twin) leaves fewer gaps than no seeds "
            f"({none_g:.2f}) -- filling the most enclosed place first is what closes gaps")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"single": {f"{a}_{r}": x for (a, r), x in res.items()},
               "replicates": {f"{a}_{r}": v for (a, r), v in summ.items()}}, open(DATA, "w"))
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
