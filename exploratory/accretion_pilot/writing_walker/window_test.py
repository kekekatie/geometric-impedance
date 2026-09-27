#!/usr/bin/env python3
"""window_test.py -- PREREGISTRATION_WINDOW.md (frozen before this file existed).
Does a knot's position relative to the hidden-space window (the 'shaft of light') predict whether it is
stubborn? Window per layer = convex hull of perp(K) over pristine vertices of that layer (R = 40). For each knot:
out = largest distance OUTSIDE the window among its vertices (0 if all inside). Knots are recomputed
deterministically per road and matched to D4's records (road, position, size); the original road's knots
from healing.py are included. Wn1: stubborn knots have larger 'out' (one-sided Mann-Whitney p < 0.05).
Wn2: AUC of 'out' and of knot size for stubborn vs healed."""
from __future__ import annotations
import os, sys, math, json, collections
import numpy as np
import writing_walker as W, healing as H, decapod as D

par, perp = W.par, W.PA.perp
LAST_RECS = []


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def signed_depth(p, poly):
    """positive inside the convex polygon, negative outside: distance to its boundary."""
    def seg_d(p, a, b):
        ax, ay = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay)))
        return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)
    d = min(seg_d(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
    inside = all((poly[(i + 1) % len(poly)][0] - poly[i][0]) * (p[1] - poly[i][1]) -
                 (poly[(i + 1) % len(poly)][1] - poly[i][1]) * (p[0] - poly[i][0]) >= -1e-12 for i in range(len(poly)))
    return d if inside else -d


def mannwhitney_one_sided(a, b):
    """P(U >= observed) for 'a larger than b', normal approximation with tie correction."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    allv = np.concatenate([a, b]); order = allv.argsort(); ranks = np.empty(len(allv))
    sv = allv[order]; i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    n1, n2 = len(a), len(b); U = ranks[:n1].sum() - n1 * (n1 + 1) / 2
    counts = collections.Counter(allv); N = n1 + n2
    tie = sum(c ** 3 - c for c in counts.values())
    sd = math.sqrt(n1 * n2 / 12 * ((N + 1) - tie / (N * (N - 1))))
    z = (U - n1 * n2 / 2 - 0.5) / sd if sd > 0 else 0.0
    return U, 0.5 * math.erfc(z / math.sqrt(2)), U / (n1 * n2)


def main(partial=False):
    base = W.build(0.0, 0.0); atlas = set(W.star_types(base).values())
    by_layer = collections.defaultdict(list)
    for cs, *_ in base.values():
        for K in cs:
            by_layer[sum(K)].append(perp(K))
    windows = {L: hull(v) for L, v in by_layer.items() if len(v) > 50}
    print("window layers (vertex count):", {L: len(set(v)) for L, v in by_layer.items()})
    recs = []
    # original road (healing.py results)
    heal = json.load(open(os.path.join(W.RES, "healing.json")))["0.2"]["depths"]
    T, ill, groups = H.knots_of(W.build(0.2, 30.0), atlas)
    for g, d in zip(groups, heal):
        recs.append(dict(road="orig J0 C0", knot=g, stubborn=d is None))
    # D4 roads (D4's road (0, 0) IS the original road: its knots are then taken from D4 only, not twice)
    done = {}
    for line in open(os.path.join(W.RES, "decapod_roads.jsonl")):
        r = json.loads(line); done[(r["J"], r["C"])] = r["rows"]
    if (0, 0) in done:
        recs = [r for r in recs if r["road"] != "orig J0 C0"]
    for (J, C), rows in sorted(done.items()):
        F, EJP = D.build_road(J, C, 0.2)
        types = W.star_types(F); illegal = {K for K, tp in types.items() if tp not in atlas}
        mid = [K for K in illegal if abs(W.dot(EJP, par(K))) <= 25]
        gs, left = [], set(mid)
        while left:
            g, st = [], [left.pop()]
            while st:
                u = st.pop(); g.append(u)
                for q in list(left):
                    if H.dist(u, q) <= H.LINK:
                        left.discard(q); st.append(q)
            gs.append(g)
        for row in rows:
            match = [g for g in gs if len(g) == row["size"] and
                     abs(sum(W.dot(EJP, par(K)) for K in g) / len(g) - row["t"]) < 0.06]
            assert len(match) == 1, (J, C, row["t"], row["size"], len(match))
            recs.append(dict(road=f"J{J} C{C:+d}", knot=match[0], stubborn=not row["healed"]))
    missing = 0
    for r in recs:
        ds = []
        for K in r["knot"]:
            L = sum(K)
            if L not in windows:
                missing += 1; ds.append(-float("inf")); continue
            ds.append(signed_depth(perp(K), windows[L]))
        finite_out = [max(0.0, -d) for d in ds if d != -float("inf")]
        r["out"] = float("inf") if any(d == -float("inf") for d in ds) else max(finite_out)
        r["size"] = len(r["knot"])
    global LAST_RECS
    LAST_RECS = recs
    stub = [r for r in recs if r["stubborn"]]; ok = [r for r in recs if not r["stubborn"]]
    lines = [f"{'PARTIAL: ' if partial else ''}{len(done)} D4 roads + the original road; knots: {len(recs)} "
             f"(stubborn {len(stub)}, healed {len(ok)}); knot vertices in a layer missing from the window: {missing}"]
    for r in sorted(recs, key=lambda r: (not r["stubborn"], -r["out"]))[:14]:
        lines.append(f"   {r['road']:<11} size {r['size']:>2}  {'STUBBORN' if r['stubborn'] else 'healed  '}  out = {r['out']:.4f}")
    finite = lambda xs: [min(x, 1e6) for x in xs]
    U, p, auc_out = mannwhitney_one_sided(finite([r["out"] for r in stub]), finite([r["out"] for r in ok]))
    _, p_size, auc_size = mannwhitney_one_sided([r["size"] for r in stub], [r["size"] for r in ok])
    lines.append(f"   mean out: stubborn {np.mean(finite([r['out'] for r in stub])):.4f}, healed {np.mean(finite([r['out'] for r in ok])):.4f}")
    lines.append(f"  Wn1: {'HELD  ' if p < 0.05 else 'FAILED'}  stubborn knots lie further outside the window: "
                 f"one-sided Mann-Whitney p = {p:.4f} (AUC {auc_out:.2f}; need p < 0.05)")
    lines.append(f"  Wn2 (reported): AUC of 'out' {auc_out:.2f}; AUC of knot size {auc_size:.2f} (p = {p_size:.4f})")
    print("\n".join(lines))
    open(os.path.join(W.RES, "window_test_partial.txt" if partial else "window_test.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(partial="--partial" in sys.argv)
