#!/usr/bin/env python3
"""EXPLORATORY picture for speed_of_now: (left) burst size against the piece of wiggle room each option keeps, every
distinct sibling, with the dead options at zero; (middle) tiles laid slice by slice for both siblings of every distinct
choice; (right) one choice drawn: what each alternative present has laid 20 slices later. Writes figures/speed_of_now.png."""
import os, json, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.stats import spearmanr
import speed_of_now as SN
Sl, L, D, S = SN.Sl, SN.L, SN.D, SN.S
BG, INK, MUTED, GOLD, BLUE, RED, DIM = "#07080d", "#ece8dc", "#8f8b80", "#f2b84b", "#5b8fe0", "#ff5a4d", "#2a2d3a"
SHOW_WORLD, SHOW_SLICES = 8, 20

W = json.load(open(os.path.join(SN.RES, "worlds.json")))
two = [c for w in W for c in w["choices"] if "A" in c]
live = [c for c in two if c["A"]["piece"] > 0 and c["B"]["piece"] > 0]
dead = [c for c in two if c not in live]
seen = {}
for c in live:
    seen.setdefault((tuple(c["A"]["per"]), tuple(c["B"]["per"])), c)
U = list(seen.values())
sib = [s for c in U for s in (c["A"], c["B"])]
rho = spearmanr([s["piece"] for s in sib], [s["burst"] for s in sib]).correlation


def regrow(k, slice_no):
    """replay world k to the choice at slice_no and grow both options SHOW_SLICES slices."""
    rng = random.Random(SN.SEED0 + k); P = L.Patch(L.seed_patch(SN.centres()[k], 3 * S)); r = 0
    while True:
        r += 1
        fr = P.frontier(); forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if forced:
            for t in forced.values():
                if P.legal(t):
                    P.add(t)
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3]))
        if r == slice_no:
            break
        P.add(rng.choice(cs))
    base = list(P.tris); out = []
    for i, t in enumerate(cs):
        Q = L.Patch(list(base)); Q.add(t); g = random.Random(0)
        for _ in range(SHOW_SLICES):
            SN.patient(Q, g)
        out.append(Q.tris[len(base):])
    return base, out, cs


if __name__ == "__main__":
    fig = plt.figure(figsize=(19, 6.8), facecolor=BG)
    ax1 = fig.add_axes([0.04, 0.12, 0.25, 0.7]); ax2 = fig.add_axes([0.34, 0.12, 0.25, 0.7])
    for ax in (ax1, ax2):
        ax.set_facecolor(BG); ax.tick_params(colors=MUTED)
        for sp in ax.spines.values():
            sp.set_color(MUTED)
    xs = np.array([s["piece"] for s in sib]); ys = np.array([s["burst"] for s in sib])
    ax1.scatter(xs + np.random.default_rng(0).uniform(-0.008, 0.008, len(xs)), ys, s=26,
                c=[GOLD if x < 0.5 else BLUE for x in xs], edgecolors="none", alpha=0.85)
    for c in dead:
        d = c["A"] if c["A"]["piece"] == 0 else c["B"]
        ax1.scatter([0], [d["burst"]], marker="x", s=70, color=RED)
    ax1.text(0.02, 260, "dead options:\nrush, then jam", color=RED, fontsize=9)
    ax1.set_yscale("log"); ax1.set_xlabel("piece of wiggle room the option keeps", color=INK)
    ax1.set_ylabel("burst: tiles laid before the next guess (max 40 slices)", color=INK)
    ax1.set_title(f"the less an option keeps, the further the now runs\n(Spearman {rho:+.2f}, {len(sib)} siblings)", color=INK, fontsize=11)
    for c in U:
        sm, lg = sorted((c["A"], c["B"]), key=lambda s: s["piece"])
        for s, col in ((sm, GOLD), (lg, BLUE)):
            ax2.plot(np.cumsum(s["per"]), color=col, lw=1, alpha=0.55)
    ax2.set_xlabel("slices after the choice", color=INK); ax2.set_ylabel("tiles laid since the choice", color=INK)
    ax2.set_title("both futures of every choice: gold = smaller piece, blue = larger.\nThe gap opens and is still there at slice 40",
                  color=INK, fontsize=11)
    c = next(c for c in U if c["world"] == SHOW_WORLD)
    base, (nA, nB), cs = regrow(SHOW_WORLD, c["slice"])
    order = sorted([(c["A"]["piece"], nA, "A"), (c["B"]["piece"], nB, "B")])
    view = [z for t in base + nA + nB for z in t[1:]]
    lim = (min(z.real for z in view) / S - 1, max(z.real for z in view) / S + 1, min(z.imag for z in view) / S - 1, max(z.imag for z in view) / S + 1)
    for i, (piece, new, _) in enumerate(order):
        ax = fig.add_axes([0.62 + i * 0.19, 0.12, 0.18, 0.7]); ax.set_facecolor(BG); ax.axis("off")
        poly = lambda ts: [[(z.real / S, z.imag / S) for z in t[1:]] for t in ts]
        ax.add_collection(PolyCollection(poly(base), facecolors=DIM, edgecolors="#0d0e14", linewidths=0.2))
        ax.add_collection(PolyCollection(poly(new), facecolors=GOLD if i == 0 else BLUE, edgecolors="#0d0e14", linewidths=0.2))
        m = (cs[0][1] + cs[0][2] + cs[0][3]) / 3
        ax.plot([m.real / S], [m.imag / S], "*", color=RED, ms=14, markeredgecolor="white")
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal")
        ax.set_title(f"option keeping {piece:.3f} of F:\n{len(new)} tiles in {SHOW_SLICES} slices", color=INK, fontsize=11)
    fig.suptitle("the speed of now: a choice that decides more lets the present run further before it must choose again",
                 color=INK, fontsize=14, family="serif", style="italic")
    os.makedirs(os.path.join(SN.HERE, "figures"), exist_ok=True)
    plt.savefig(os.path.join(SN.HERE, "figures", "speed_of_now.png"), dpi=105, facecolor=BG, bbox_inches="tight")
    print("rho", rho, "shown world", SHOW_WORLD, "slice", c["slice"], [len(nA), len(nB)])
