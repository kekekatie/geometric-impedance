#!/usr/bin/env python3
"""
paths.py -- on the Penrose tiling: what does the projection allow, is there a path of least
resistance, and does a momentum-like bias pick among several paths?  (Katie + Gemini's question.)

Reuses the exact pentagrid of ../penrose_address_environment/ (every vertex an integer K in Z^5,
so every move is an exact unit step +-u_j; the world step is +-e_j, the hidden step +-e_{2j},
and the layer changes by +-1).

  A  WHAT THE PROJECTION ALLOWS: how many of the 10 step directions exist at each vertex.
  B  STRAIGHT-LINE MOMENTUM: how often can the same step be repeated? How long a straight run?
  C  GREEDY "LEAST RESISTANCE": two short-sighted deterministic walkers, from many starts --
       STRAIGHT  take the step most aligned with the previous one (world momentum)
       CENTRAL   take the step landing most centrally in the hidden window
     Do they travel, or get trapped in loops?
  D  RIBBON MOMENTUM (momentum in the hidden grid): keep one grid coordinate K_j FIXED (exact)
     and always step forward along family j's lines. The pentagrid's lines are straight, so this
     is "going straight in hidden space"; in the world it is a wiggly ribbon. Measured: is a
     forward step always available? Do walkers cross the world? How many forward options (the
     MENU) at each step -- and does momentum's choice among them matter?

Exact: K arithmetic, "K_j fixed", step existence, run lengths, revisits. Float: the forward
component along the line direction (margin 1e-9) and physical distances. asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, math, random, collections, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "penrose_address_environment"))
import penrose_address as P                         # exact builder (no main on import)

REPORT = os.path.join(HERE, "results", "paths_report.txt")
DATA = os.path.join(HERE, "results", "paths.json")
LINES, FAILS = [], []
R = 70.0
N_STARTS = 300
SEED = 20260924


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def main():
    log("=" * 90)
    log("LEAST-RESISTANCE PATHS on the Penrose tiling")
    log("=" * 90)
    faces, verts, edges = P.build(R)
    adj = collections.defaultdict(set)
    for e in edges:
        a, b = tuple(e); adj[a].add(b); adj[b].add(a)
    inner = sorted(K for K in verts if math.hypot(*P.par(K)) < R - 5)
    edge_R = R - 3
    log(f"  patch radius {R}: {len(verts)} vertices; {len(inner)} interior vertices used")
    out = {}

    # ---------------------------------------------------------------- A: allowed steps
    log("-" * 90)
    deg = collections.Counter(len(adj[K]) for K in inner)
    log(f"[A] step directions open at a vertex (of 10): {dict(sorted(deg.items()))}")
    require(min(deg) == 3 and max(deg) == 7,
            "the projection opens only 3-7 of the 10 possible step directions at any vertex")
    twist = all(all(math.isclose(P.perp(add(K, P.UNIT[j]))[c],
                                 P.perp(K)[c] + P.EV[(2 * j) % 5][c], abs_tol=1e-9) for c in (0, 1))
                and sum(add(K, P.UNIT[j])) == sum(K) + 1
                for K in inner[:500] for j in range(5))
    require(twist, "a world step along e_j is a hidden step along e_2j (the twist) and changes "
                   "the layer by +-1 -- every step is also a step inside the bounded window")
    out["A"] = dict(sorted(deg.items()))

    # ---------------------------------------------------------------- B: straight runs
    log("-" * 90)
    runs = collections.Counter()
    for K in inner:
        for W in adj[K]:
            s = P.sub(W, K); n, X = 1, W
            while add(X, s) in adj[X]:
                n += 1; X = add(X, s)
            runs[n] += 1
    tot = sum(runs.values())
    log(f"[B] straight runs (same step repeated), over all {tot} directed steps: "
        f"{dict(sorted(runs.items()))}")
    require(max(runs) == 2,
            f"the same step can be repeated at most TWICE, never three times; a repeat is possible "
            f"after only {runs[2] / tot:.1%} of steps -- straight lines in the world are forbidden")
    out["B"] = dict(sorted(runs.items()))

    # ---------------------------------------------------------------- C: greedy walkers
    log("-" * 90)
    cent = {}
    for L in (1, 2, 3, 4):
        pts = [P.perp(K) for K in verts if sum(K) == L]
        cent[L] = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    def depth(K):
        p, c = P.perp(K), cent[sum(K)]
        return math.hypot(p[0] - c[0], p[1] - c[1])

    def greedy(rule, K, max_steps=5000):
        prev, seen, path = None, {K: 0}, [K]
        for t in range(1, max_steps + 1):
            def score(W):
                st = P.par(P.sub(W, K)); mom = 0.0 if prev is None else dot(st, prev)
                return (mom, -depth(W), W) if rule == "STRAIGHT" else (-depth(W), mom, W)
            W = max(adj[K], key=score)
            prev = P.par(P.sub(W, K)); K = W; path.append(K)
            if math.hypot(*P.par(K)) > edge_R:
                return dict(fate="edge", t=t, path=path)
            if K in seen:
                return dict(fate="loop", t=t, period=t - seen[K], path=path)
            seen[K] = t
        return dict(fate="running", t=max_steps, path=path)

    rng = random.Random(SEED)
    starts = rng.sample([K for K in inner if math.hypot(*P.par(K)) < R / 2], N_STARTS)
    greedy_res = {}
    for rule in ("STRAIGHT", "CENTRAL"):
        res = [greedy(rule, K) for K in starts]
        fates = collections.Counter(r["fate"] for r in res)
        periods = collections.Counter(r["period"] for r in res if r["fate"] == "loop")
        reach = [max(math.hypot(*P.par(X)) - math.hypot(*P.par(r["path"][0])) for X in r["path"])
                 for r in res]
        greedy_res[rule] = res
        log(f"[C] {rule:<8} from {N_STARTS} starts: fates {dict(fates)}; loop periods "
            f"{dict(sorted(periods.items()))}; steps before looping: median "
            f"{sorted(r['t'] for r in res)[N_STARTS // 2]}")
        require(fates.get("loop", 0) == N_STARTS,
                f"{rule}: EVERY greedy walker gets trapped in a loop ({N_STARTS}/{N_STARTS}); "
                f"the furthest any gets from its start is {max(reach):.1f}")
        out["C_" + rule] = dict(fates=dict(fates), periods=dict(sorted(periods.items())),
                                max_reach=max(reach))

    # ---------------------------------------------------------------- D: ribbon walkers
    log("-" * 90)

    def ribbon(j, K, choose, rng_=None):
        t_dir = (-P.EV[j][1], P.EV[j][0])            # along family j's lines
        path, menu = [K], []
        while True:
            fwd = [W for W in adj[K] if W[j] == K[j]
                   and dot(P.par(P.sub(W, K)), t_dir) > 1e-9]
            menu.append(len(fwd))
            if not fwd:
                return dict(fate="stuck", path=path, menu=menu)
            if choose == "most":
                K = max(fwd, key=lambda W: (dot(P.par(P.sub(W, K)), t_dir), W))
            elif choose == "least":
                K = min(fwd, key=lambda W: (dot(P.par(P.sub(W, K)), t_dir), W))
            else:
                K = rng_.choice(sorted(fwd))
            path.append(K)
            if math.hypot(*P.par(K)) > edge_R:
                return dict(fate="crossed", path=path, menu=menu)

    rib = collections.defaultdict(list)
    for K in starts:
        for j in range(5):
            for choose in ("most", "least", "random"):
                rib[choose].append((j, ribbon(j, K, choose, random.Random(SEED + j))))
    allrib = [r for v in rib.values() for _, r in v]
    menu = collections.Counter(m for r in allrib for m in r["menu"][:-1])
    fates = collections.Counter(r["fate"] for r in allrib)
    exact_fixed = all(W[j] == r["path"][0][j] for v in rib.values() for j, r in v for W in r["path"])
    no_revisit = all(len(set(r["path"])) == len(r["path"]) for r in allrib)
    eff = [(math.hypot(*P.par(r["path"][-1])) - 0) for r in allrib]
    speeds = []
    for j, r in rib["most"]:
        t_dir = (-P.EV[j][1], P.EV[j][0])
        a, b = P.par(r["path"][0]), P.par(r["path"][-1])
        speeds.append(dot((b[0] - a[0], b[1] - a[1]), t_dir) / (len(r["path"]) - 1))
    log(f"[D] RIBBON walkers: {len(allrib)} walks ({N_STARTS} starts x 5 families x 3 choice "
        f"rules): fates {dict(fates)}")
    log(f"    forward MENU size at each step: {dict(sorted(menu.items()))}  "
        f"({(menu[2] + menu[3]) / sum(menu.values()):.1%} of steps offer 2 or 3 ways forward)")
    log(f"    progress along the line per step (max-forward rule): "
        f"min {min(speeds):.3f}, mean {sum(speeds) / len(speeds):.3f}")
    require(fates == {"crossed": len(allrib)},
            f"EVERY ribbon walker crosses to the edge of the world ({len(allrib)}/{len(allrib)}), "
            f"never stuck: a forward step is ALWAYS available")
    require(exact_fixed and no_revisit,
            "ribbon walkers keep their grid coordinate K_j exactly fixed and never revisit a "
            "vertex (every step moves forward along a straight hidden line: no loop is possible)")
    require(min(menu) >= 1 and max(menu) == 3 and (menu[2] + menu[3]) / sum(menu.values()) > 0.5,
            f"the geometry offers a MENU: 1-3 forward options per step, 2 or 3 on "
            f"{(menu[2] + menu[3]) / sum(menu.values()):.0%} of steps -- more than one path, "
            f"usually")
    differ = sum(1 for (j, a), (_, b) in zip(rib["most"], rib["least"]) if a["path"] != b["path"])
    require(differ > 0.9 * len(rib["most"]),
            f"momentum's choice MATTERS for the route: 'most forward' and 'least forward' take "
            f"different routes in {differ}/{len(rib['most'])} walks, yet all of them cross -- the "
            f"road guarantees the progress, the bias chooses the way")
    out["D"] = dict(menu=dict(sorted(menu.items())), fates=dict(fates), speed_min=min(speeds),
                    speed_mean=sum(speeds) / len(speeds), differ=differ, n=len(rib["most"]))

    # ---- data for the figure: tiling edges near the centre, 3 greedy loops, 5 ribbons -------
    cK = min(inner, key=lambda v: math.hypot(*P.par(v)))
    fig_edges = [[P.par(a), P.par(b)] for a, b in (tuple(e) for e in edges)
                 if math.hypot(*P.par(a)) < 26 and math.hypot(*P.par(b)) < 26]
    loops = []
    near = [K for K in starts if 6 < math.hypot(*P.par(K)) < 15]
    for K in near[:4]:                                     # a few loops that fit the view
        r = greedy("STRAIGHT", K)
        loops.append(dict(rule="STRAIGHT", path=[P.par(X) for X in r["path"]]))
    ribs = []
    for j in range(5):
        t_dir = (-P.EV[j][1], P.EV[j][0])
        st = min((K for K in inner if abs(dot(P.par(K), P.EV[j])) < 1.0),
                 key=lambda K: dot(P.par(K), t_dir))
        r = ribbon(j, st, "most")
        ribs.append([P.par(X) for X in r["path"]])
    out["figure"] = dict(edges=fig_edges, loops=loops, ribbons=ribs)
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
