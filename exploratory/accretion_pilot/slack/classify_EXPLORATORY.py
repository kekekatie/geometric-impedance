#!/usr/bin/env python3
"""EXPLORATORY (after Astra's review of PRs #40/#41). Zero AREA can mean a segment, a point, or nothing. Classify F
properly with linear programming:
  s* = max s such that every constraint n.t >= c + s holds  (an inscribed margin)
  s* > 1e-9  -> POLYGON;  s* < -1e-9 -> EMPTY;  otherwise degenerate: relax every c by 1e-9 and measure the extent of the
  relaxed set along 12 directions: < 1e-6 -> POINT, else SEGMENT.
Applied to: decapod worlds (bare ring, slice 1, final), the two worlds that took a dead option (slack world 14, golden
world 0) slice by slice, and a sample of ordinary patches. Also draws figures/window_cut.png: one ordinary choice's F, its
two eventual pieces and the new cutting lines, beside a decapod ring's F and its first slice."""
import os, sys, json, math, random, collections
import numpy as np
from scipy.optimize import linprog
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import slack as Sl
T, F_, L, D, S, SC = Sl.T, Sl.F_, Sl.L, Sl.D, Sl.S, Sl.SC
sys.path.insert(0, os.path.join(Sl.HERE, "..", "golden_digits"))
import golden_digits as GD


def classify(cm):
    rows = [(Sl.WIN[rk][0][i], c) for (rk, i), c in cm.items()]
    A = [[-n[0], -n[1], 1.0] for n, c in rows]; b = [-c for n, c in rows]
    res = linprog([0, 0, -1], A_ub=A, b_ub=b, bounds=[(None, None), (None, None), (None, 1.0)], method="highs")
    s = -res.fun
    if s > 1e-9:
        return "polygon", s
    if s < -1e-9:
        return "empty", s
    A2 = [[-n[0], -n[1]] for n, c in rows]; b2 = [-(c - 1e-9) for n, c in rows]
    ext = 0.0
    for k in range(12):
        d = (math.cos(math.pi * k / 12), math.sin(math.pi * k / 12))
        hi = linprog([-d[0], -d[1]], A_ub=A2, b_ub=b2, bounds=[(None, None)] * 2, method="highs")
        lo = linprog([d[0], d[1]], A_ub=A2, b_ub=b2, bounds=[(None, None)] * 2, method="highs")
        ext = max(ext, -hi.fun - lo.fun)
    return ("point" if ext < 1e-6 else "segment"), ext


def ordinary_classes(centre, stream, n_add=1500):
    rng = random.Random(stream)
    P = L.Patch(L.seed_patch(centre, 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris); out = []; r = 0
    while len(P.tris) - n0 < n_add:
        r += 1
        st, placed, anyf = F_.step(P)
        if st == "JAM":
            out.append((r, "JAM", None)); break
        if not placed and not anyf:
            e = P.frontier()[0]
            cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
            P.add(rng.choice(cs)); kind = "choice"
        elif placed:
            kind = "forced"
        else:
            continue
        out.append((r, kind, classify(Sl.constraints(P.tris, rank))[0]))
    return out


def figure():
    # an ordinary choice: golden_digits world 1, first two-option choice
    rng = random.Random(GD.SEED0 + 1); c0 = GD.centres()[1]
    P = L.Patch(L.seed_patch(c0, 3 * S)); rank = Sl.rank_of(P.tris)
    while True:
        st, placed, anyf = F_.step(P)
        if placed or anyf:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) == 2:
            break
        P.add(rng.choice(cs))
    base = list(P.tris); c0m = Sl.constraints(base, rank)
    cA = Sl.constraints(list(F_.sibling(base, cs[0])[0].tris), rank); cB = Sl.constraints(list(F_.sibling(base, cs[1])[0].tris), rank)
    pF, pA, pB = Sl.region(c0m), Sl.region(cA), Sl.region(cB)
    # a decapod ring and its first slice
    seeds = json.load(open(os.path.join(D.RES, "seeds.json"))); x = next(v for v in seeds if v["seed"] == 3)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    PD, rnd, rounds, g, st = SC.grow(ring, 800, D.SEED0 + 300)
    tiles = list(PD.tris); rk = Sl.rank_of(tiles)
    cR = Sl.constraints([t for t in tiles if rnd[D.dkey(t)] == 0], rk); c1 = Sl.constraints([t for t in tiles if rnd[D.dkey(t)] <= 1], rk)
    pR = Sl.region(cR); kind1 = classify(c1)
    rows = [(Sl.WIN[k[0]][0][k[1]], c) for k, c in c1.items()]
    A2 = [[-n[0], -n[1]] for n, c in rows]; b2 = [-(c - 1e-9) for n, c in rows]
    pt = linprog([0, 0], A_ub=A2, b_ub=b2, bounds=[(None, None)] * 2, method="highs").x
    SURF, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.2), facecolor=SURF)
    ax = axes[0]
    fill = lambda a, p, col, al, lab: a.fill([q[0] for q in p], [q[1] for q in p], color=col, alpha=al, label=lab, lw=0)
    fill(ax, pF, "#d6d5cf", 1.0, f"wiggle room at the choice (area {Sl.area(pF):.4f})")
    fill(ax, pA, "#d6402b", 0.55, f"option A's piece ({Sl.area(pA) / Sl.area(pF):.3f})")
    fill(ax, pB, "#2a78d6", 0.55, f"option B's piece ({Sl.area(pB) / Sl.area(pF):.3f})")
    xs = [q[0] for q in pF]; ys = [q[1] for q in pF]; pad = 0.25 * max(max(xs) - min(xs), max(ys) - min(ys))
    for cm, col in ((cA, "#d6402b"), (cB, "#2a78d6")):
        for key, c in cm.items():
            if c > c0m.get(key, -1e18) + 1e-12:
                n = Sl.WIN[key[0]][0][key[1]]; t = np.linspace(-1, 1, 2)
                p0 = (n[0] * c, n[1] * c); dvec = (-n[1], n[0])
                ax.plot([p0[0] + s * dvec[0] for s in t], [p0[1] + s * dvec[1] for s in t], color=col, lw=1.2, ls="--")
    ax.set_xlim(min(xs) - pad, max(xs) + pad); ax.set_ylim(min(ys) - pad, max(ys) + pad); ax.set_aspect("equal")
    ax.set_title("An ordinary choice: the wiggle room is cut in two\n(dashed: the new vertex constraints that do the cutting)", color=INK, fontsize=12, loc="left")
    ax.legend(loc="lower left", frameon=False, fontsize=9); ax.tick_params(colors=MUTED)
    ax = axes[1]
    fill(ax, pR, "#d6d5cf", 1.0, f"bare decapod ring (area {Sl.area(pR):.3f})")
    ax.plot([pt[0]], [pt[1]], "o", color="#c98a00", ms=9, label=f"after one slice: a {kind1[0]} (extent {kind1[1]:.1e})")
    ax.set_aspect("equal"); ax.legend(loc="lower left", frameon=False, fontsize=9); ax.tick_params(colors=MUTED)
    ax.set_title("A decapod world: large wiggle room, pinned after one slice", color=INK, fontsize=12, loc="left")
    os.makedirs(os.path.join(Sl.HERE, "figures"), exist_ok=True)
    plt.savefig(os.path.join(Sl.HERE, "figures", "window_cut.png"), dpi=120, facecolor=SURF, bbox_inches="tight")
    return Sl.area(pA) / Sl.area(pF), Sl.area(pB) / Sl.area(pF), kind1


if __name__ == "__main__":
    lines = ["EXPLORATORY: what zero-area F really is"]
    lines.append(f"  figure: ordinary choice shares and decapod slice-1 class: {figure()}")
    for s in range(2, 10):
        seeds = json.load(open(os.path.join(D.RES, "seeds.json"))); x = next(v for v in seeds if v["seed"] == s)
        ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
        P, rnd, rounds, g, st = SC.grow(ring, 800, D.SEED0 + 100 * s); tiles = list(P.tris); rk = Sl.rank_of(tiles)
        cl = [classify(Sl.constraints([t for t in tiles if rnd[D.dkey(t)] <= r], rk)) for r in (0, 1, rounds)]
        lines.append(f"  decapod seed {s}: ring {cl[0][0]}, slice 1 {cl[1][0]} ({cl[1][1]:.1e}), final {cl[2][0]} ({cl[2][1]:.1e})")
    for name, centre, stream in (("slack world 14", T.centres()[14], T.SEED0 + 14), ("golden world 0", GD.centres()[0], GD.SEED0 + 0)):
        seq = ordinary_classes(centre, stream)
        runs = []
        for r, kind, c in seq:
            if not runs or runs[-1][2] != c:
                runs.append([r, r, c])
            else:
                runs[-1][1] = r
        lines.append(f"  {name}: F class by slice (from-to: class): " + "; ".join(f"{a}-{b}: {c}" for a, b, c in runs))
    print("\n".join(lines))
    open(os.path.join(Sl.RES, "classify_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
