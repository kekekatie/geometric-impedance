#!/usr/bin/env python3
"""
penrose_address.py -- one step closer to E8: does the Fibonacci foundation hold in 2-D?

The Fibonacci chain (../fibonacci_address_environment/) is the smallest member of the
cut-and-project family (Z^2 -> 1-D, golden ratio). The Penrose tiling is the next (Z^5 -> 2-D,
SAME golden ratio tau -- the number field E8's 4-D quasicrystal (via H4) is also built on).
Here we re-establish, in 2-D, the two foundations everything later rested on:

  (1) ADDRESS -> ENVIRONMENT. A vertex's local environment is decided by its hidden
      (perpendicular) address, so "twins" -- same environment -- can be physically far apart,
      and the deeper two vertices agree, the closer their hidden addresses must be.
  (2) PATTERN INFORMATION. How many distinct radius-r environments exist? 1-D: grows ~ r.
      2-D: expected ~ r^2 (more information per step up the family; E8's 4-D would be ~ r^4).

Construction (de Bruijn pentagrid, exact integer identity).
  Five line families e_j . x = n + gamma_j (j=0..4), gamma = v10's Penrose offsets (sum 0).
  Each vertex IS an integer vector K in Z^5 (no float dedup):
     physical  x_par  = sum_j K_j e_j                 e_j   = (cos 2pi j/5, sin 2pi j/5)
     hidden    x_perp = sum_j K_j e_{2j mod 5}        (the Galois-conjugate "twisted" view)
     layer     iota   = sum_j K_j                     (an integer: which window pentagon)
  Radius-r environment E_r(v) = the exact set of integer K-offsets of the vertices and edges
  within graph distance r of v (translation to v) -- combinatorial, no floats.
  Only vertices whose radius-(r+2) physical disc lies inside the patch are used at radius r.

Exact: K, layers, environments, class counts, agreement radii. Numeric (float): perpendicular
distances and window shapes (claims about them are stated with their tolerance).
asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, math, itertools, collections, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fibonacci_address_environment"))
import fibonacci_cutproject as F                      # 1-D reference chain

REPORT = os.path.join(HERE, "results", "penrose_address_report.txt")
DATA = os.path.join(HERE, "results", "penrose_address.json")
LINES, FAILS = [], []
R_PATCH = 90.0                                          # complete counts (no singletons)
R_PAIR = 34.0                                           # pair analysis region
R_MAX = 7
GAMMA = (0.30, 0.10, -0.25, -0.25, 0.10)               # v10 DEFAULT_OFFSETS (sum 0, Penrose)
TAU = (1 + 5 ** 0.5) / 2
EV = [(math.cos(2 * math.pi * j / 5), math.sin(2 * math.pi * j / 5)) for j in range(5)]
SHIFT = math.hypot(sum(GAMMA[j] * EV[(2 * j) % 5][0] for j in range(5)),
                   sum(GAMMA[j] * EV[(2 * j) % 5][1] for j in range(5)))   # |gamma_perp|
UNIT = [tuple(1 if i == j else 0 for i in range(5)) for j in range(5)]


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def par(K):
    return (sum(k * e[0] for k, e in zip(K, EV)), sum(k * e[1] for k, e in zip(K, EV)))


def perp(K):
    return (sum(K[j] * EV[(2 * j) % 5][0] for j in range(5)),
            sum(K[j] * EV[(2 * j) % 5][1] for j in range(5)))


def star_type(K, adj):
    """vertex-star type up to all 20 symmetries of the star of e_j's: the 10 coordinate
    rotations/reflections AND the 180-degree turn K -> -K (exact, integer)."""
    S = [sub(w, K) for w in adj[K]]
    best = None
    for rot, refl, neg in itertools.product(range(5), (False, True), (1, -1)):
        idx = [((-j if refl else j) + rot) % 5 for j in range(5)]
        T = []
        for d in S:
            e = [0] * 5
            for j in range(5):
                e[idx[j]] = neg * d[j]
            T.append(tuple(e))
        key = tuple(sorted(T))
        best = key if best is None or key < best else best
    return str(best)


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


# ------------------------------------------------------------------ build the tiling
def build(R):
    faces, verts, edges = [], set(), set()
    nrange = range(-int(R) - 3, int(R) + 4)
    for r, s in itertools.combinations(range(5), 2):
        det = EV[r][0] * EV[s][1] - EV[r][1] * EV[s][0]
        for nr in nrange:
            for ns in nrange:
                br, bs = nr + GAMMA[r], ns + GAMMA[s]
                x = ((br * EV[s][1] - bs * EV[r][1]) / det, (bs * EV[r][0] - br * EV[s][0]) / det)
                if x[0] ** 2 + x[1] ** 2 > (R + 3) ** 2:
                    continue
                base = [math.ceil(x[0] * EV[j][0] + x[1] * EV[j][1] - GAMMA[j]) for j in range(5)]
                corners = []
                for dr, ds in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    K = list(base); K[r] = nr + dr; K[s] = ns + ds
                    corners.append(tuple(K))
                if any(math.hypot(*par(K)) > R for K in corners):
                    continue
                faces.append((tuple(corners), (r, s)))
                verts.update(corners)
                for i in range(4):
                    edges.add(frozenset((corners[i], corners[(i + 1) % 4])))
    return faces, verts, edges


def main():
    log("=" * 90)
    log("PENROSE ADDRESS -> ENVIRONMENT -- the Fibonacci foundation, one step closer to E8")
    log("=" * 90)
    faces, verts, edges = build(R_PATCH)
    adj = collections.defaultdict(set)
    for e in edges:
        a, b = tuple(e); adj[a].add(b); adj[b].add(a)
    log(f"  patch radius {R_PATCH}: {len(verts)} vertices, {len(edges)} edges, {len(faces)} rhombi")

    # ---- validity: every edge is a unit step along one e_j; every face a unit rhombus -------
    require(all(sorted(abs(x) for x in sub(*tuple(e))) == [0, 0, 0, 0, 1] for e in edges),
            "every edge joins K-vectors differing by exactly one unit vector (unit length, "
            "direction e_j)")
    shapes = collections.Counter("thick" if min((r - s) % 5, (s - r) % 5) == 1 else "thin"
                                 for _, (r, s) in faces)
    ratio = shapes["thick"] / shapes["thin"]
    require(abs(ratio - TAU) < 0.03,
            f"thick:thin rhombus ratio {ratio:.4f} ~ tau = {TAU:.4f} (Penrose frequency)")
    ext = [K for K in verts if math.hypot(*par(K)) < R_PATCH - 3]
    edge_angles_ok = all(len(adj[K]) >= 3 for K in ext)
    require(edge_angles_ok, "every interior vertex has degree >= 3 (no dangling vertices)")

    # ---- layers and window pentagons ------------------------------------------------------
    layers = collections.Counter(sum(K) for K in verts)
    require(len(layers) == 4 and max(layers) - min(layers) == 3,
            f"the layer index sum(K) takes exactly 4 consecutive values {sorted(layers)} "
            f"(the four window pentagons of de Bruijn)")
    rad = {i: max(math.hypot(*perp(K)) for K in verts if sum(K) == i) for i in layers}
    lo, hi = sorted(layers)[0], sorted(layers)[-1]
    small = [rad[lo], rad[hi]]; big = [rad[lo + 1], rad[lo + 2]]
    log(f"  hidden-window radii by layer: " + ", ".join(f"{i}: {rad[i]:.4f}" for i in sorted(rad)))
    require(all(abs(x - 1) < 0.01 for x in small) and all(abs(x - TAU) < 0.01 for x in big)
            and max(rad.values()) <= TAU + SHIFT + 1e-9,
            f"windows: layers {lo},{hi} fill SMALL pentagons (circumradius 1) and layers "
            f"{lo + 1},{lo + 2} LARGE ones (circumradius tau); every hidden address is bounded "
            f"by tau + |gamma_perp| = {TAU + SHIFT:.4f} (windows are centred at the offsets' "
            f"hidden image, not the origin; v1 wrongly capped all radii at 1.3, v2 at tau)")

    # ---- environments E_r (exact, combinatorial) -------------------------------------------
    def ball(v, r):
        seen = {v: 0}; q = collections.deque([v])
        while q:
            u = q.popleft()
            if seen[u] == r:
                continue
            for w in adj[u]:
                if w not in seen:
                    seen[w] = seen[u] + 1; q.append(w)
        vs = set(seen)
        es = frozenset(frozenset((sub(a, v), sub(b, v))) for a in vs for b in adj[a] if b in vs)
        return frozenset(sub(u, v) for u in vs), es

    cls = {}                                                  # (r) -> {K: class id}
    counts2d, singles = [], []
    for r in range(1, R_MAX + 1):
        valid = [K for K in verts if math.hypot(*par(K)) < R_PATCH - (r + 2)]
        ids, table, mult = {}, {}, collections.Counter()
        for K in valid:
            key = ball(K, r)
            ids[K] = table.setdefault(key, len(table)); mult[ids[K]] += 1
        cls[r] = ids; counts2d.append(len(table))
        singles.append(sum(1 for c in mult.values() if c == 1))
        log(f"  r={r}: {len(valid):>5} vertices with a complete radius-{r} view -> "
            f"{len(table):>4} distinct environments ({singles[-1]} seen only once)")
    require(all(x == 0 for x in singles),
            f"counts are COMPLETE: every environment up to r={R_MAX} is seen more than once "
            f"(v1 used a radius-34 patch; 465 singletons at r=7 showed it was undersampled)")

    # 1-D reference: distinct radius-r environments of the Fibonacci chain
    pts = F.generate(400); g = F.gaps_of(pts)
    counts1d = [len({tuple(g[i - r:i + r]) for i in range(r, len(g) - r)}) for r in range(1, R_MAX + 1)]
    log(f"  1-D Fibonacci, distinct radius-r environments: {counts1d}")
    log(f"  2-D Penrose,   distinct radius-r environments: {counts2d}")

    def fit(ys, r0=3):
        pts_ = [(math.log(r), math.log(y)) for r, y in zip(range(1, R_MAX + 1), ys) if r >= r0]
        mx = sum(x for x, _ in pts_) / len(pts_); my = sum(y for _, y in pts_) / len(pts_)
        return sum((x - mx) * (y - my) for x, y in pts_) / sum((x - mx) ** 2 for x, _ in pts_)
    a1, a2 = fit(counts1d), fit(counts2d)
    log(f"  growth exponent (log-log fit, r=3..{R_MAX}): 1-D {a1:.2f}   2-D {a2:.2f}")
    require(counts1d == [2 * r + 1 for r in range(1, R_MAX + 1)],
            "1-D pattern information grows exactly linearly: 2r+1 environments of radius r")
    ratios = [b / a for a, b in zip(counts1d, counts2d)]
    require(a2 > 1.4 and all(ratios[i + 1] > ratios[i] for i in range(len(ratios) - 1)),
            f"2-D carries MORE pattern information and it grows FASTER than 1-D: superlinear "
            f"(fitted r^{a2:.2f} over r=3..{R_MAX}; v1 predicted r^2 -- not confirmed at these "
            f"radii), and the 2-D/1-D ratio rises every step ({ratios[0]:.0f}x -> {ratios[-1]:.0f}x)")

    # ---- address -> environment: agreement radius vs hidden distance -----------------------
    base = [K for K in cls[R_MAX] if math.hypot(*par(K)) < R_PAIR]
    P = {K: perp(K) for K in base}
    X = {K: par(K) for K in base}
    rstar_pairs = collections.defaultdict(list)                 # r* -> list of (dperp, dpar)
    for a, b in itertools.combinations(base, 2):
        if sum(a) != sum(b):
            continue
        rs = next((r for r in range(1, R_MAX + 1) if cls[r][a] != cls[r][b]), R_MAX + 1)
        dp = math.hypot(P[a][0] - P[b][0], P[a][1] - P[b][1])
        dx = math.hypot(X[a][0] - X[b][0], X[a][1] - X[b][1])
        rstar_pairs[rs].append((dp, dx))
    log("  agreement radius r* (first radius at which two same-layer vertices' environments "
        "differ) vs hidden distance:")
    delta = {}
    for r in range(1, R_MAX + 2):
        L = rstar_pairs.get(r, [])
        if not L:
            continue
        lab = f"agree to r>={R_MAX}" if r == R_MAX + 1 else f"r*={r}"
        delta[r] = max(dp for dp, _ in L)
        log(f"    {lab:<14} pairs {len(L):>7}   max hidden distance {max(dp for dp, _ in L):.4f}   "
            f"median {sorted(dp for dp, _ in L)[len(L) // 2]:.4f}   "
            f"max physical distance {max(dx for _, dx in L):6.1f}")
    ks = sorted(delta)
    tw = [max(dp for rr in ks if rr > r for dp, _ in rstar_pairs[rr]) for r in range(1, R_MAX + 1)]
    log(f"  twin-cell size delta(r) = max hidden distance among pairs agreeing through radius r: "
        + ", ".join(f"{x:.4f}" for x in tw))
    require(all(tw[i + 1] <= tw[i] + 1e-12 for i in range(len(tw) - 1)) and tw[-1] < tw[0] / 4,
            f"the deeper two vertices agree, the closer their hidden addresses MUST be: the "
            f"twin-cell size shrinks monotonically ({tw[0]:.3f} -> {tw[-1]:.3f})")
    deep = rstar_pairs.get(R_MAX + 1, [])
    require(len(deep) > 0 and max(dx for _, dx in deep) > 20,
            f"twins exist FAR apart: {len(deep)} same-layer pairs agree through radius {R_MAX} "
            f"at physical distances up to {max(dx for _, dx in deep):.1f} (pair region radius {R_PAIR})")

    types = collections.Counter(star_type(K, adj) for K in cls[1])
    degs = sorted(len(eval(t)) for t in types)
    require(degs == [3, 3, 4, 5, 5, 6, 7],
            f"up to the 20 symmetries, exactly 7 vertex-star types with degrees {degs}: the "
            f"classic Penrose vertex types (S and S5 share one edge-star; they differ only in "
            f"their rhombi, so a radius-1 star cannot tell them apart)")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump({"counts1d": counts1d, "counts2d": counts2d, "alpha1": a1, "alpha2": a2,
               "singles": singles,
               "delta": tw,
               "perp_by_star": [[perp(K)[0], perp(K)[1], sum(K), star_type(K, adj)] for K in cls[1]]},
              open(DATA, "w"))
    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL CHECKS PASSED.")
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
