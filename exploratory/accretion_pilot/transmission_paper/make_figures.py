#!/usr/bin/env python3
"""
make_figures.py -- the three figures for "When the past matters, II".

  fig1_coast.png   the archive-free coast D(t) of the original pair, falling monotonically to
                   its exact limit L = 4321/44100 (Proposition 3).
  fig2_fates.png   the 97 depth-3 matched pairs: expression D_slice(2) against the number of
                   reachable sinks, coloured by fate (inert / washout / durable) -- the fork law.
  fig3_22_26.png   washout pair (22,26) against the 70 durable pairs: D_slice at h = 1, 2, 3,
                   then the coast limit L. Strongly marked, yet nothing stays.

Every plotted number is recomputed here with the repository's own machinery (present_width,
pair_robustness, depth3_criterion -- all unchanged) in exact rationals, and the key numbers the
text quotes are asserted before anything is drawn. Exit non-zero on any mismatch.
"""
from __future__ import annotations
import os, sys, random
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "endogenous_pair_robustness"))
sys.path.insert(0, os.path.join(ROOT, "endogenous_present_width"))
os.chdir(os.path.join(ROOT, "endogenous_pair_robustness"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import depth3_criterion as D3
PW, PR = D3.PW, D3.PR

FIG = os.path.join(HERE, "figures")
C = dict(inert="#8a8a8a", washout="#c0392b", durable="#1a5fb4")
FAILS = []


def check(cond, msg):
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def coast_series(Gi, Gj, tmax, horizon=2):
    """Exact coast D(t) = TV(mu_i T^t, mu_j T^t), t = 0..tmax, on the BUD-only projection chain
    (same construction as pair_robustness.coast_limit), plus L from that function."""
    reps, buckets = [], {}

    def cidx(P):
        h = PW.wl(P)
        for k in buckets.get(h, ()):
            if PW.iso(P, reps[k]):
                return k
        reps.append(P); buckets.setdefault(h, []).append(len(reps) - 1)
        return len(reps) - 1

    def slice_dist(G):
        d = {}

        def rec(Gg, prob, s):
            evs = PW.events_ext(Gg) if s < horizon else []
            if not evs:
                k = cidx(PW.erase(Gg)); d[k] = d.get(k, Fr(0)) + prob; return
            for e in evs:
                rec(PW.apply_ev(Gg, e), prob * Fr(1, len(evs)), s + 1)
        rec(G, Fr(1), 0)
        return d

    vi, vj = slice_dist(Gi), slice_dist(Gj)
    T, frontier = {}, list(set(vi) | set(vj))
    seen = set(frontier)
    while frontier:
        s = frontier.pop(); evs = PW.events_bud(reps[s])
        if not evs:
            T[s] = {s: Fr(1)}
        else:
            row = {}
            for (_, x, y) in evs:
                s2 = cidx(PW.erase(PW.bud(reps[s], x, y))); row[s2] = row.get(s2, Fr(0)) + Fr(1, len(evs))
            T[s] = row
        for s2 in T[s]:
            if s2 not in seen:
                seen.add(s2); frontier.append(s2)

    def step(v):
        out = {}
        for s, p in v.items():
            for s2, q in T[s].items():
                out[s2] = out.get(s2, Fr(0)) + p * q
        return out

    seq = []
    for _ in range(tmax + 1):
        seq.append(PR.tv(vi, vj)); vi, vj = step(vi), step(vj)
    return seq, PR.coast_limit(Gi, Gj)[0]


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(alpha=0.2)


def fig1():
    fulls = PW.depth2_classes(); i, j = PW.find_pair(fulls)
    seq, L = coast_series(fulls[i], fulls[j], 20)
    check(L == Fr(4321, 44100), f"original pair: L = {L} (text: 4321/44100)")
    check(seq[:4] == [Fr(463, 3150), Fr(4439, 37800), Fr(3805, 36288), Fr(312041, 3110400)],
          "original pair: coast t=0..3 matches coast_asymptote.py exactly")
    check(all(a >= b for a, b in zip(seq, seq[1:])) and all(x >= L for x in seq),
          "coast non-increasing and never below L")
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(range(len(seq)), [float(x) for x in seq], "-o", color=C["durable"], ms=4.5, lw=1.8,
            label=r"coast $D(t)$ (exact)")
    ax.axhline(float(L), color=C["durable"], ls="--", lw=1)
    ax.text(len(seq) - 1, float(L) - 0.0035, r"$L = 4321/44100 \approx 0.0980$", ha="right", va="top",
            fontsize=9, color=C["durable"])
    ax.set_ylim(0.09, 0.152); ax.set_xticks(range(0, len(seq), 2))
    ax.set_xlabel(r"coast step $t$ after the archive is deleted at $H = 2$")
    ax.set_ylabel("total-variation distance\nbetween the two lineages")
    ax.set_title("The coast falls monotonically to a positive limit", fontsize=10.5)
    style(ax); ax.legend(fontsize=8.5, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_coast.png"), dpi=200); plt.close(fig)


def depth3_records():
    d3 = D3.depth3_classes()
    pairs = [(a, b) for a in range(len(d3)) for b in range(a + 1, len(d3))
             if PW.iso(PW.erase(d3[a]), PW.erase(d3[b])) and not PW.iso(d3[a], d3[b])]
    rec = {}
    for (a, b) in pairs:
        ds = [D3.Dslice(d3[a], d3[b], h) for h in (1, 2, 3)]
        L, shapes, _ = PR.coast_limit(d3[a], d3[b])
        fate = "durable" if L > 0 else ("washout" if any(x > 0 for x in ds) else "inert")
        rec[(a, b)] = dict(ds=ds, L=L, nsink=len(shapes), fate=fate)
    return d3, rec


def fig2(rec):
    n = {f: sum(1 for r in rec.values() if r["fate"] == f) for f in C}
    check(len(rec) == 97 and n == dict(inert=22, washout=5, durable=70),
          f"depth-3: {len(rec)} pairs; fates {n} (text: 22 / 5 / 70)")
    check(sum(1 for r in rec.values() if r["nsink"] == 2) == 85
          and sum(1 for r in rec.values() if r["nsink"] == 1) == 12,
          "sinks: 85 two-sink, 12 single-sink (text)")
    expd = [r for r in rec.values() if r["ds"][1] > 0]
    check(len(expd) == 75 and all((r["L"] > 0) == (r["nsink"] >= 2) for r in expd),
          "fork law: all 75 expressed pairs are durable iff two reachable sinks")
    rng = random.Random(1)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for f, lab in (("inert", "inert"), ("washout", "washout"), ("durable", "durable")):
        rs = [r for r in rec.values() if r["fate"] == f]
        xs = [r["nsink"] + rng.uniform(-0.17, 0.17) for r in rs]
        ys = [float(r["ds"][1]) for r in rs]
        ax.scatter(xs, ys, s=30, color=C[f], alpha=0.8, edgecolor="white", lw=0.5,
                   label=f"{lab} ({len(rs)})", zorder=3)
    ax.axhline(0, color="#444", lw=0.6)
    ax.axvspan(1.5, 2.5, ymin=0.08, color=C["durable"], alpha=0.05, zorder=0)
    ax.set_xticks([1, 2]); ax.set_xticklabels(["one sink", "two sinks"])
    ax.set_xlim(0.4, 2.6)
    ax.set_xlabel("reachable sinks of the coast")
    ax.set_ylabel(r"expression  $D_{\mathrm{slice}}(2)$")
    ax.set_title("Fork law, 97 depth-3 pairs: expressed + two sinks = durable", fontsize=10.5)
    ax.text(2.0, -0.012, "15 unexpressed two-sink pairs:\ninert (nothing to split)",
            ha="center", va="top", fontsize=7.5, color=C["inert"])
    ax.text(1.0, -0.012, "7 inert", ha="center", va="top", fontsize=7.5, color=C["inert"])
    lo = min(-0.05, ax.get_ylim()[0]); ax.set_ylim(lo, ax.get_ylim()[1])
    style(ax); ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_fates.png"), dpi=200); plt.close(fig)


def fig3(d3, rec):
    w = rec[(22, 26)]
    dur = [r for r in rec.values() if r["fate"] == "durable"]
    check(w["fate"] == "washout" and w["ds"] == [Fr(1, 6), Fr(17, 90), Fr(539, 2700)] and w["L"] == 0,
          "(22,26): D_slice = 1/6, 17/90, 539/2700; L = 0")
    check(sum(1 for r in dur if r["ds"][1] < w["ds"][1]) == 20, "20 of 70 durable pairs weaker at h=2")
    seq, L = coast_series(d3[22], d3[26], 12)
    check(L == 0 and seq[-1] < Fr(1, 10**3), "(22,26) coast drains to 0")
    rng = random.Random(2)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.0), gridspec_kw=dict(width_ratios=[3, 2]))
    # left: expression before erasure, and the limit after
    xs_pos = [0, 1, 2, 3.6]
    for r in dur:
        ys = [float(x) for x in r["ds"]] + [float(r["L"])]
        a1.scatter([x + rng.uniform(-0.13, 0.13) for x in xs_pos], ys, s=13, color=C["durable"],
                   alpha=0.35, edgecolor="none", zorder=2)
    a1.scatter([], [], s=13, color=C["durable"], alpha=0.6, label="durable pairs (70)")
    wy = [float(x) for x in w["ds"]] + [0.0]
    a1.plot(xs_pos[:3], wy[:3], "-o", color=C["washout"], lw=2, ms=7, zorder=4, label="pair (22,26)")
    a1.plot(xs_pos[2:], wy[2:], ":", color=C["washout"], lw=1.5, zorder=4)
    a1.scatter([xs_pos[3]], [0], s=60, color=C["washout"], zorder=5)
    a1.axvline(2.8, color="#444", lw=0.8, ls="--")
    a1.set_xticks(xs_pos); a1.set_xticklabels([r"$h=1$", r"$h=2$", r"$h=3$", r"limit $L$"])
    a1.set_ylabel("distinguishability (TV)")
    a1.set_title("Marked more than 20 of 70 durable pairs at $h=2$ ...", fontsize=10)
    style(a1); a1.legend(fontsize=8.5, frameon=False, loc="upper left")
    # right: its own coast
    a2.plot(range(len(seq)), [float(x) for x in seq], "-o", color=C["washout"], ms=4, lw=1.8)
    a2.axhline(0, color="#444", lw=0.6)
    a2.set_xlabel(r"coast step $t$ after deletion at $H=2$")
    a2.set_ylabel(r"coast $D(t)$")
    a2.set_title("... yet its coast drains to $L = 0$ (one sink)", fontsize=10)
    style(a2)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_22_26.png"), dpi=200); plt.close(fig)


def main():
    os.makedirs(FIG, exist_ok=True)
    print("figure 1: the coast of the original pair"); fig1()
    print("depth-3 records (97 pairs) ..."); d3, rec = depth3_records()
    print("figure 2: fates and the fork law"); fig2(rec)
    print("figure 3: (22,26) against the durable pairs"); fig3(d3, rec)
    print("FAILED: " + "; ".join(FAILS) if FAILS else "ALL CHECKS PASSED; figures in " + FIG)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
