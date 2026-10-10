#!/usr/bin/env python3
"""
ribbons_EXPLORATORY.py -- EXPLORATORY (no predictions; Astra's requested first step). The tiling's own continuation rule:
a RIBBON is a chain of half-tiles linked across shared rhombus edges of one direction family (and across the diagonal
inside each rhombus). Continuation along a ribbon is local and unique: no similarity matching, no branching.

One ordinary world is grown (patient scheduler, as ../fragility/); every tile's round is recorded; at every choice both
siblings are grown 8 rounds ahead (../fragility/ sibling()). Outputs:
  * figures/gold_thread_frames.png -- six moments: settled interior, active frontier, gold ribbons, choices + strips
  * figures/gold_thread.gif        -- the same as an animation
  * results/ribbons_EXPLORATORY.txt -- where ribbons end (frontier vs interior); do gold ribbons continue in both siblings
    at each choice; and, in one decapod world, how many ribbons end at the unfillable hole.
`python3 ribbons_EXPLORATORY.py [world] [n_tiles]`
"""
import os, sys, random, collections, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.animation import FuncAnimation, PillowWriter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fragility"))
import fragility as F
M, D, L, S = F.M, F.D, F.L, F.S
WORLD = int(sys.argv[1]) if len(sys.argv) > 1 else 0
N_ADD = int(sys.argv[2]) if len(sys.argv) > 2 else 900
RES, FIG = os.path.join(HERE, "results"), os.path.join(HERE, "figures")
ek = lambda p, q: frozenset((L.key(p), L.key(q)))
is_leg = lambda p, q: abs(abs(q - p) - S) < 1e-4 * S


def legs_and_base(t):
    sides = [(t[1], t[2]), (t[2], t[3]), (t[3], t[1])]
    return [s for s in sides if is_leg(*s)], [s for s in sides if not is_leg(*s)]


def ribbons(tiles):
    """union-find per direction family. returns {family: {dkey: root}} and the patch's edge index."""
    idx = {D.dkey(t): t for t in tiles}; by_edge = collections.defaultdict(list)
    for t in tiles:
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            by_edge[ek(p, q)].append(D.dkey(t))
    out = {}
    for j in range(5):
        par = {}

        def find(a):
            par.setdefault(a, a)
            while par[a] != a:
                par[a] = par[par[a]]; a = par[a]
            return a

        def union(a, b):
            par[find(a)] = find(b)
        for k, t in idx.items():
            legs, base = legs_and_base(t)
            fams = [M.edge_dir(p, q)[0] for p, q in legs]
            if j not in fams:
                continue
            find(k)
            for (p, q), f in zip(legs, fams):
                if f == j:
                    for o in by_edge[ek(p, q)]:
                        if o != k:
                            union(k, o)
            for p, q in base:                                    # partner half of the same rhombus
                for o in by_edge[ek(p, q)]:
                    if o != k:
                        union(k, o)
        out[j] = {k: find(k) for k in par}
    return out, by_edge


def ribbon_ends(tiles, by_edge):
    """open ends: a j-leg with no tile on its other side. returns list of (family, edge midpoint)."""
    ends = []
    for t in tiles:
        legs, _ = legs_and_base(t)
        for p, q in legs:
            if len(by_edge[ek(p, q)]) == 1:
                ends.append((M.edge_dir(p, q)[0], (p + q) / 2))
    return ends


def grow_world():
    rng = random.Random(F.SEED0 + WORLD)
    P = L.Patch(L.seed_patch(0j, 3 * S)); n0 = len(P.tris); r = 0
    rnd = {D.dkey(t): 0 for t in P.tris}; choices = []
    while len(P.tris) - n0 < N_ADD:
        r += 1
        st, placed, any_forced = F.step(P)
        for t in placed:
            rnd[D.dkey(t)] = r
        if placed or any_forced:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
        base = list(P.tris)
        sib = [F.sibling(base, c) for c in cs]
        kA = {D.dkey(t) for t in sib[0][1]}; kB = {D.dkey(t) for t in sib[1][1]} if len(sib) > 1 else set()
        strip = [t for t in sib[0][1] if D.dkey(t) not in kB]                   # sibling-A tiles that B lays differently
        choices.append(dict(round=r, at=(e[0] + e[1]) / 2, base=base, sibs=sib, strip=strip, n_options=len(cs)))
        t = rng.choice(cs); P.add(t); rnd[D.dkey(t)] = r
    return P, rnd, r, choices


def main():
    os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
    P, rnd, R, choices = grow_world()
    tiles = list(P.tris); rib, by_edge = ribbons(tiles)
    lines = [f"EXPLORATORY ribbons, ordinary world {WORLD}: {len(tiles)} half-tiles, {R} rounds, {len(choices)} choices "
             f"(options {[c['n_options'] for c in choices]})"]
    # 1. where do ribbons end?  only at the frontier (unfinished = censored), never inside
    fr_edges = {ek(e[0], e[1]) for e in P.frontier()}
    ends = ribbon_ends(tiles, by_edge)
    inside = 0
    for t in tiles:
        legs, _ = legs_and_base(t)
        for p, q in legs:
            if len(by_edge[ek(p, q)]) == 1 and ek(p, q) not in fr_edges:
                inside += 1
    lines.append(f"  ribbon ends: {len(ends)} open ends, all on the frontier except {inside}")
    # 2. gold ribbons: the ribbons through the tiles nearest the centre, one per family
    gold = {}
    for j in range(5):
        near = sorted((abs(F.cen(t)), D.dkey(t)) for t in tiles if D.dkey(t) in rib[j])
        root = rib[j][near[0][1]]
        gold[j] = {k for k, rr in rib[j].items() if rr == root}
    lines.append("  gold ribbons (one per family, through the centre): tiles " + str({j: len(v) for j, v in gold.items()}))
    # 3. at each choice, does each gold ribbon continue (gain new tiles) in both siblings?
    for c in choices:
        res = []
        for j in range(5):
            base_keys = {D.dkey(t) for t in c["base"]}
            g_old = gold[j] & base_keys
            gains = []
            for Q, new, status, rr in c["sibs"]:
                rb, _ = ribbons(list(Q.tris))
                roots = {rb[j][k] for k in g_old if k in rb[j]}
                gains.append(sum(1 for t in new if rb[j].get(D.dkey(t)) in roots))
            res.append(gains)
        both = sum(1 for g in res if all(x > 0 for x in g)); one = sum(1 for g in res if sum(x > 0 for x in g) == 1)
        lines.append(f"  choice at round {c['round']}: strip {len(c['strip'])} tiles; gold ribbons continuing in both siblings "
                     f"{both}/5, in one {one}/5, in neither {5 - both - one}/5; new gold tiles per sibling {res}")
    # 4. a decapod world: ribbon ends at the unfillable hole
    import json
    sd = json.load(open(os.path.join(D.RES, "seeds.json")))
    x = next(v for v in sd if v["kind"] == "DECAPOD" and v["seed"] == 3)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    dt, _, g, st = M.grow(ring, 800, D.SEED0 + 100 * 3, wall=True)
    rb, be = ribbons(dt)
    hole = [(j, m) for j, m in ribbon_ends(dt, be) if abs(m) < D.APO + 1e-6]
    fams = collections.Counter(j for j, _ in hole)
    lines.append(f"  decapod world (seed 3, 800 tiles, {len(g)} guesses): ribbon ends at the hole {len(hole)} "
                 f"(by family {dict(sorted(fams.items()))})")
    print("\n".join(lines))
    open(os.path.join(RES, "ribbons_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
    draw(tiles, rnd, R, gold, choices)


def draw(tiles, rnd, R, gold, choices):
    SURF, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"
    SETTLED, EDGE, FRONT, STRIP = "#e4e3dd", "#c9c8c1", "#9cc3ee", "#d6402b"
    GOLDS = ["#c98a00", "#e0a400", "#b8770a", "#eab531", "#a86a00"]
    poly = lambda t: [(z.real / S, z.imag / S) for z in t[1:]]
    lim = max(abs(z) for t in tiles for z in t[1:]) / S + 0.5

    def frame(ax, upto):
        ax.clear(); ax.set_facecolor(SURF)
        now = [t for t in tiles if rnd[D.dkey(t)] <= upto]
        fc = []
        for t in now:
            k = D.dkey(t); age = upto - rnd[k]
            fam = next((j for j in range(5) if k in gold[j]), None)
            fc.append(GOLDS[fam] if fam is not None else (FRONT if age < 2 else SETTLED))
        ax.add_collection(PolyCollection([poly(t) for t in now], facecolors=fc, edgecolors=EDGE, linewidths=0.25))
        for c in choices:
            if c["round"] <= upto:
                if c["round"] > upto - 12:
                    ax.add_collection(PolyCollection([poly(t) for t in c["strip"]], facecolors="none", edgecolors=STRIP, linewidths=0.9))
                ax.plot([c["at"].real / S], [c["at"].imag / S], "o", color=INK, ms=4.5)
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"slice {upto}", color=MUTED, fontsize=11)

    picks = [int(round(x)) for x in np.linspace(R * 0.12, R, 6)]
    fig, axes = plt.subplots(2, 3, figsize=(16, 11), facecolor=SURF)
    for ax, u in zip(axes.flat, picks):
        frame(ax, u)
    fig.suptitle("Gold: five ribbons through the centre, one per direction, re-made slice after slice as the world grows.\n"
                 "Blue: the active frontier (last 2 slices). Grey: settled past. Black dots: two-way choices; red outlines: "
                 "the strip each choice decided (shown for 12 slices).", color=INK, fontsize=12, x=0.01, ha="left")
    plt.savefig(os.path.join(FIG, "gold_thread_frames.png"), dpi=110, facecolor=SURF, bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.5, 7.5), facecolor=SURF)
    steps = list(range(1, R + 1, max(1, R // 70))) + [R] * 8
    anim = FuncAnimation(fig, lambda i: frame(ax, steps[i]), frames=len(steps))
    anim.save(os.path.join(FIG, "gold_thread.gif"), writer=PillowWriter(fps=8), dpi=80)


if __name__ == "__main__":
    main()
