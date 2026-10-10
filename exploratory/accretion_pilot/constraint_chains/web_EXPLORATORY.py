#!/usr/bin/env python3
"""EXPLORATORY (post hoc, after Astra's review of PR #38). Same worlds and choices as constraint_chains.py, with finer
link categories:
  attachment     -- the owner of the forcing edge (included by convention, NOT removal-tested)
  decided ribbon -- removal-tested; shares a decided-ribbon rhombus edge
  ribbon edge    -- removal-tested; shares another rhombus edge (another ribbon)
  diagonal       -- removal-tested; shares the diagonal inside one rhombus (the other half-tile)
  corner         -- removal-tested; shares only a vertex
and a MATCHED comparison: all critical parents of difference tiles vs all critical parents of non-difference tiles.
Also draws figures/constraint_web.png for the first choice of world 1. `python3 web_EXPLORATORY.py` (FIGURE_ONLY=1 for the picture only)"""
import os, sys, random, collections, json
from multiprocessing import Pool
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D
import constraint_chains as C
T, R, F, M, D, L, S = C.T, C.R, C.F, C.M, C.D, C.L, C.S
KINDS = ["attachment", "decided ribbon", "ribbon edge", "diagonal", "corner", "distant"]
COL = {"attachment": "#52514e", "decided ribbon": "#c98a00", "ribbon edge": "#2a78d6", "diagonal": "#1baf7a",
       "corner": "#d6402b", "distant": "#9a9890"}


def kind(u, t, owner, jstar, Rk):
    if D.dkey(u) == D.dkey(owner):
        return "attachment"
    shared = C.vkeys(u) & C.vkeys(t)
    if len(shared) == 2:
        pts = {L.key(z): z for z in t[1:]}; p, q = [pts[k] for k in shared]
        if not R.is_leg(p, q):
            return "diagonal"
        if M.edge_dir(p, q)[0] == jstar and D.dkey(u) in Rk and D.dkey(t) in Rk:
            return "decided ribbon"
        return "ribbon edge"
    return "corner" if len(shared) == 1 else "distant"


def analyse2(base, cs, line, rng, keep=False):
    sib = [C.sibling(base, c) for c in cs]
    smax = min(sib[0][3], sib[1][3])
    out = dict(smax=smax, sides=[])
    for (Q, rec, st, rr), (Q2, rec2, _, _), t0 in ((sib[0], sib[1], cs[0]), (sib[1], sib[0], cs[1])):
        X = {k: v for k, v in rec.items() if v[1] <= smax}; Y = {k: v for k, v in rec2.items() if v[1] <= smax}
        yo = [v[0] for k, v in Y.items() if k not in X]
        delta = {k for k, v in X.items() if k not in Y and any(L.inside(C.cen(v[0]), *w[1:]) for w in yo)}
        jstar, Rk = T.decided_ribbon(Q, t0, line[1])
        diff_links, all_links_delta, all_links_non, drawn = [], [], [], []
        for k, (t, s, e) in X.items():
            if s == 0:
                continue
            is_d = k in delta
            if not is_d and rng.random() > 0.15:
                continue                                     # sample ~15% of non-difference tiles for the matched baseline
            ok, crit = C.criticals(base, rec, t, s, e)
            if not ok:
                continue
            for p in crit:
                kd = kind(p, t, e[3], jstar, Rk)
                (all_links_delta if is_d else all_links_non).append(kd)
                if is_d and D.dkey(p) in delta:
                    diff_links.append(kd)
                    if keep:
                        drawn.append((C.cen(p), C.cen(t), kd))
        side = dict(diff=diff_links, all_delta=all_links_delta, all_non=all_links_non)
        if keep:
            side.update(base=base, X=[v[0] for v in X.values()], delta=[X[k][0] for k in delta], R=[v[0] for k, v in X.items() if k in Rk],
                        links=drawn, chosen=t0, line=line)
        out["sides"].append(side)
    return out


def world2(k):
    C.analyse_choice = lambda base, cs, line, rng: analyse2(base, cs, line, rng)
    return C.world(k)


def share(xs):
    c = collections.Counter(xs); n = sum(c.values())
    return {kd: round(c[kd] / n, 3) for kd in KINDS if c[kd]}, n


def figure():
    rng = random.Random(T.SEED0 + 1); c0 = T.centres()[1]
    P = L.Patch(L.seed_patch(c0, 3 * S))
    while True:
        st, placed, any_forced = F.step(P)
        if placed or any_forced:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) == 2:
            break
        P.add(rng.choice(cs))
    res = analyse2(list(P.tris), cs, F.front_line(P, e), random.Random(1), keep=True)
    sd = res["sides"][0]
    SURF, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"
    poly = lambda ts: [[(z.real / S, z.imag / S) for z in t[1:]] for t in ts]
    fig, ax = plt.subplots(figsize=(11, 11), facecolor=SURF)
    ax.add_collection(PolyCollection(poly(sd["base"]), facecolors="#ecebe6", edgecolors="#cfcec8", linewidths=0.3))
    ax.add_collection(PolyCollection(poly(sd["X"]), facecolors="#f7f6f2", edgecolors="#cfcec8", linewidths=0.3))
    ax.add_collection(PolyCollection(poly(sd["delta"]), facecolors="#f3c9c2", edgecolors="#cfcec8", linewidths=0.3))
    ax.add_collection(PolyCollection(poly(sd["R"]), facecolors="none", edgecolors="#c98a00", linewidths=1.6))
    for a, b, kd in sd["links"]:
        ax.annotate("", xy=(b.real / S, b.imag / S), xytext=(a.real / S, a.imag / S),
                    arrowprops=dict(arrowstyle="-|>", color=COL[kd], lw=1.3, shrinkA=2, shrinkB=2, mutation_scale=9))
    ch = C.cen(sd["chosen"]); ax.plot([ch.real / S], [ch.imag / S], "o", color=INK, ms=8, zorder=5)
    xs = [z.real / S for t in sd["delta"] for z in t[1:]]; ys = [z.imag / S for t in sd["delta"] for z in t[1:]]
    pad = 2.0; ax.set_xlim(min(xs) - pad, max(xs) + pad); ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_aspect("equal"); ax.axis("off")
    hand = [Line2D([0], [0], color=COL[k], lw=2, label=lab) for k, lab in
            (("attachment", "attachment (owner of the edge it grew from; not removal-tested)"),
             ("decided ribbon", "along the decided ribbon"), ("ribbon edge", "across another ribbon's edge"),
             ("diagonal", "across the diagonal inside a rhombus"), ("corner", "corner only (shares just a point)"))]
    hand += [Line2D([0], [0], marker="s", color="w", markerfacecolor="#f3c9c2", markersize=12, label="tiles that differ from the other present"),
             Line2D([0], [0], color="#c98a00", lw=1.6, label="the decided ribbon (outlined)"),
             Line2D([0], [0], marker="o", color="w", markerfacecolor=INK, markersize=9, label="the choice")]
    ax.legend(handles=hand, loc="upper left", bbox_to_anchor=(0, -0.01), ncol=2, frameon=False, fontsize=10)
    ax.set_title("How one choice's consequences are carried: each arrow points from a differing tile to a later tile it helps force",
                 color=INK, fontsize=12, loc="left")
    os.makedirs(os.path.join(C.HERE, "figures"), exist_ok=True)
    plt.savefig(os.path.join(C.HERE, "figures", "constraint_web.png"), dpi=120, facecolor=SURF, bbox_inches="tight")
    return share(sd["diff"])


if __name__ == "__main__":
    print("figure (world 1, first choice, sibling A) differing-parent links:", figure())
    if os.environ.get("FIGURE_ONLY"):
        sys.exit()
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world2, range(T.N_WORLDS))
    seen = set(); CH = []
    for w in W:
        for c in w["choices"]:
            if c["key"] not in seen:
                seen.add(c["key"]); CH.append(c)
    sides = [sd for c in CH for sd in c["sides"]]
    tested = lambda xs: [x for x in xs if x != "attachment"]
    lines = [f"EXPLORATORY finer link categories over {len(CH)} distinct configurations",
             f"  differing-parent links (as in the report), all: {share([x for s in sides for x in s['diff']])}",
             f"  differing-parent links, removal-tested only (attachments excluded): {share(tested([x for s in sides for x in s['diff']]))}",
             f"  MATCHED: all critical parents of difference tiles: {share([x for s in sides for x in s['all_delta']])}",
             f"  MATCHED: all critical parents of sampled non-difference tiles: {share([x for s in sides for x in s['all_non']])}",
             f"  MATCHED, removal-tested only: difference {share(tested([x for s in sides for x in s['all_delta']]))} vs "
             f"non-difference {share(tested([x for s in sides for x in s['all_non']]))}"]
    print("\n".join(lines))
    open(os.path.join(C.RES, "web_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
