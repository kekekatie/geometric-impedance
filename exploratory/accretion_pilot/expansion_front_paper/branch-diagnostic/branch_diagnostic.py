#!/usr/bin/env python3
"""
branch_diagnostic.py -- Astra's paired visual diagnostic (consolidation pass).

From a GENUINE free choice (a tie the bounded forced-only wave leaves open), grow
three forced-only arms from the same locally-saturated 'before' state:
  no-commit  /  commit option A  /  commit option B
with a larger radius (15*S) and cap (120). Compare the FINAL decorated tile sets:
common to A and B (grey), A-specific, B-specific. Mark the intervention tiles and
record each arm's stopping reason (saturated / cap / contradiction). Fresh worlds
(seeds 216+). This replaces the broken rib-length subtraction -- no bookkeeping
offset, no counting-opportunity asymmetry; it compares end states directly.

Run:  python3 branch_diagnostic.py            |   --worlds 4 --nadd 600
"""
from __future__ import annotations
from pathlib import Path
import sys, json, math, cmath, random, collections, argparse, base64, io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "corner-response-catalogue"))
import figures as F
import corner_response as CR

L, D, S, SN = F.L, F.D, F.S, F.SN
RES = HERE / "results"; RES.mkdir(exist_ok=True)
EPS = 1e-9
SEED0 = 20261200          # same base; fresh wedge entries below
WEDGE0 = 216              # fresh worlds (A/B/C used 192-215)
BIG_R = 7                 # the A/B divergence region is local; this captures it fast
BIG_CAP = 50
MAX_CASES = 24            # enough genuine free choices for a divergence distribution
GREY, ABLUE, BORANGE = "#c9d1d6", "#167c9b", "#d66a34"
dk = lambda t: D.dkey(t)
ek = CR.ek


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[WEDGE0:WEDGE0 + 24]


def forced_arm(start, mid, cap=BIG_CAP, R=BIG_R):
    """Localised forced-only growth to saturation; return (final tiles, stop reason)."""
    P = L.Patch(list(start)); rr = R * S + EPS
    for _ in range(cap):
        forced = {}; jam = False
        for e in P.frontier():
            if abs((e[0] + e[1]) / 2 - mid) > rr:
                continue
            cs = D.candidates(P, *e[:3])
            if len(cs) == 0:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(dk(cs[0]), cs[0])
        if jam:
            return list(P.tris), "contradiction"
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        if placed == 0:
            return list(P.tris), "saturated"
    return list(P.tris), "cap"


def genuine_free_choices(k, nadd, limit):
    """Grow fresh world k; yield (before, edge, mid) for ties the local wave leaves open.
    Stops once `limit` genuine free choices are found (bounds cost)."""
    rng = random.Random(SEED0 + 999 + k)
    P = L.Patch(L.seed_patch(centres()[k], 3 * S)); n0 = len(P.tris); seen = set(); out = []
    while len(P.tris) - n0 < nadd and len(out) < limit:
        fr = P.frontier()
        for e in fr:
            sk = ek(e)
            if sk in seen:
                continue
            cs = D.candidates(P, *e[:3])
            if len(cs) == 2:
                seen.add(sk); before = list(P.tris); mid = (e[0] + e[1]) / 2
                tris0, _ = forced_arm(before, mid, cap=12, R=5)    # cheap screen
                still_open = len(D.candidates(L.Patch(tris0), *e[:3])) == 2
                if still_open:                        # the bounded wave did NOT settle it
                    out.append((before, e, mid))
                    if len(out) >= limit:
                        break
        forced = {}
        for e in fr:
            c = D.candidates(P, *e[:3])
            if len(c) == 1:
                forced.setdefault(dk(c[0]), c[0])
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        P.add(rng.choice(SN.ordered(D.candidates(P, *fr[0][:3]))))
    return out


def diagnose(before, edge, mid):
    cs = D.candidates(L.Patch(before), *edge[:3])
    if len(cs) != 2:
        return None
    oa, ob = cs
    trisA, rA = forced_arm(before + [oa], mid)
    trisB, rB = forced_arm(before + [ob], mid)
    kb = set(dk(t) for t in before)
    kA = {dk(t) for t in trisA} - kb; kB = {dk(t) for t in trisB} - kb
    common = kA & kB; a_spec = kA - kB; b_spec = kB - kA
    return dict(before=before, edge=edge, mid=mid, oa=oa, ob=ob, trisA=trisA, trisB=trisB,
                stopA=rA, stopB=rB, n_common=len(common), n_a=len(a_spec), n_b=len(b_spec),
                common=common, a_spec=a_spec, b_spec=b_spec)


def panel(ax, d):
    base, mid = d["before"], d["mid"]
    def polys(ts): return [[((z - mid).real / S, (z - mid).imag / S) for z in t[1:]] for t in ts]
    # base (context) in light grey
    near = [t for t in base if any(abs(z - mid) <= (BIG_R + 1) * S for z in t[1:])]
    ax.add_collection(PolyCollection(polys(near), facecolors="#eef1f3", edgecolors="#dde3e7", linewidths=.2))
    tA = {dk(t): t for t in d["trisA"]}; tB = {dk(t): t for t in d["trisB"]}
    ax.add_collection(PolyCollection(polys([tA[k] for k in d["common"]]), facecolors=GREY, edgecolors="white", linewidths=.25))
    ax.add_collection(PolyCollection(polys([tA[k] for k in d["a_spec"]]), facecolors=ABLUE, edgecolors="white", linewidths=.25))
    ax.add_collection(PolyCollection(polys([tB[k] for k in d["b_spec"]]), facecolors=BORANGE, edgecolors="white", linewidths=.25))
    for t, col in [(d["oa"], "#0b4a5e"), (d["ob"], "#8a3e17")]:
        ax.add_collection(PolyCollection(polys([t]), facecolors="none", edgecolors=col, linewidths=1.8))
    allp = np.array([q for t in near for q in polys([t])[0]])
    if len(allp):
        lo, hi = allp.min(0) - 1, allp.max(0) + 1
        m = max(hi - lo)
        ax.set(xlim=(lo[0], lo[0] + m), ylim=(lo[1], lo[1] + m))
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"common {d['n_common']}  ·  A-only {d['n_a']} ({d['stopA']})  ·  B-only {d['n_b']} ({d['stopB']})", fontsize=9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=4)
    ap.add_argument("--nadd", type=int, default=600)
    args = ap.parse_args()
    cases = []
    for k in range(args.worlds):
        if len(cases) >= MAX_CASES:
            break
        need = MAX_CASES - len(cases)
        for before, edge, mid in genuine_free_choices(k, args.nadd, need):
            d = diagnose(before, edge, mid)
            if d and (d["n_a"] + d["n_b"]) > 0:
                cases.append(d)
        print(f"world {k}: cumulative genuine-free diagnostics {len(cases)}", flush=True)
    div = np.array([c["n_a"] + c["n_b"] for c in cases])
    report = [f"genuine free choices diagnosed: {len(cases)} (fresh worlds {WEDGE0}-{WEDGE0+args.worlds-1}, radius {BIG_R}*S, cap {BIG_CAP})",
              f"branch divergence |A-only|+|B-only|: median {np.median(div):.0f}, mean {div.mean():.1f}, "
              f"p10 {np.percentile(div,10):.0f}, p90 {np.percentile(div,90):.0f}, max {div.max()}",
              f"both-arms-identical (zero divergence excluded above): would be {int((div==0).sum())} of diagnosed",
              f"stop reasons A: {dict(collections.Counter(c['stopA'] for c in cases))}",
              f"stop reasons B: {dict(collections.Counter(c['stopB'] for c in cases))}"]
    print("\n".join(report))
    # figure: the 4 largest-divergence examples
    top = sorted(cases, key=lambda c: -(c["n_a"] + c["n_b"]))[:4]
    fig, axs = plt.subplots(2, 2, figsize=(11, 11))
    for ax, d in zip(axs.ravel(), top):
        panel(ax, d)
    fig.suptitle("Committing a genuine free choice: what each option forces differently\n"
                 "grey = common to A & B   ·   blue = A-only   ·   orange = B-only   ·   outlines = the two committed tiles",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(HERE / "divergence.png", dpi=150, facecolor="white", bbox_inches="tight"); plt.close(fig)
    (RES / "report.txt").write_text("\n".join(report) + "\n")
    (RES / "measurements.json").write_text(json.dumps(dict(
        n=len(cases), divergence=[int(x) for x in div],
        median_divergence=float(np.median(div)),
        examples=[dict(n_common=c["n_common"], n_a=c["n_a"], n_b=c["n_b"], stopA=c["stopA"], stopB=c["stopB"]) for c in top]), indent=2))
    print("wrote divergence.png, results/report.txt, results/measurements.json")


if __name__ == "__main__":
    main()
