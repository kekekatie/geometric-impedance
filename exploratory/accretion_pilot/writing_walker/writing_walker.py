#!/usr/bin/env python3
"""
writing_walker.py -- Gemini's "writing memory" test (PREREGISTRATION.md, frozen before this file).

A walker travels along its own pentagrid line (family J=0, line c=0) and pushes that line sideways by
delta in its WAKE (between its birthplace t_start and its current position t0; linear ramps of width w
at both ends). The Penrose tiling is rebuilt as the exact dual of the bent arrangement (integer
addresses K in Z^5). Where a crossing of two other lines slips across the bent line, three tiles
rearrange (a hexagon flip). We ask whether the rewriting stays on the road, only in the wake, grows
with the journey, and whether the wake is a legal sibling Penrose universe (vertex-star atlas).
Structural checks (W1) are asserts; predictions W2-W5 are reported HELD / FAILED.
"""
from __future__ import annotations
import os, sys, math, itertools, collections, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "penrose_address_environment"))
import penrose_address as PA

EV, GAMMA, par = PA.EV, PA.GAMMA, PA.par
J, C = 0, 0
R = 40.0
T_START, W = -30.0, 2.0
DELTAS = [0.05, 0.1, 0.2, 0.4]
T0S = [-20.0, -10.0, 0.0, 10.0, 20.0, 30.0]
R_INT = R - 3.0                                           # vertices with complete stars
RES = os.path.join(HERE, "results")
LINES, FAILS, VERDICTS = [], [], []


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    log(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def verdict(tag, held, msg):
    VERDICTS.append((tag, held, msg)); log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


EJ = EV[J]
EJP = (-EJ[1], EJ[0])                                     # along-line direction: t = EJP . x


def h(t, t0):
    """wake profile: 1 on [T_START+W, t0-W], linear ramps to 0 at T_START and t0, 0 elsewhere."""
    if t0 - T_START < 2 * W:
        return 0.0
    if t <= T_START or t >= t0:
        return 0.0
    if t < T_START + W:
        return (t - T_START) / W
    if t > t0 - W:
        return (t0 - t) / W
    return 1.0


def bent_offset(x, delta, t0):
    return delta * h(dot(EJP, x), t0)


def build(delta, t0):
    """dual tiling of the arrangement with line (J, C) bent by delta*h(t) in the walker's wake.
    Returns {face_key: (corners, (r, s), n_r, n_s)} and the list of triple points that crossed."""
    faces = {}
    nrange = range(-int(R) - 3, int(R) + 4)
    for r, s in itertools.combinations(range(5), 2):
        det = EV[r][0] * EV[s][1] - EV[r][1] * EV[s][0]
        for nr in nrange:
            for ns in nrange:
                br, bs = nr + GAMMA[r], ns + GAMMA[s]
                x = ((br * EV[s][1] - bs * EV[r][1]) / det, (bs * EV[r][0] - br * EV[s][0]) / det)
                if r == J and nr == C and delta > 0:
                    # intersection of the BENT line with straight line (s, ns): bisection along line s
                    d = (-EV[s][1], EV[s][0]); p0 = (bs * EV[s][0], bs * EV[s][1])
                    g = lambda u: dot(EJ, (p0[0] + u * d[0], p0[1] + u * d[1])) - GAMMA[J] - C - \
                        bent_offset((p0[0] + u * d[0], p0[1] + u * d[1]), delta, t0)
                    u_star = (C + GAMMA[J] - dot(EJ, p0)) / dot(EJ, d)
                    lo, hi = u_star - 2.0, u_star + 2.0
                    glo, ghi = g(lo), g(hi)
                    assert glo * ghi < 0, "bent line not bracketed"
                    for _ in range(80):
                        mid = 0.5 * (lo + hi); gm = g(mid)
                        if gm * glo <= 0:
                            hi = mid
                        else:
                            lo, glo = mid, gm
                    u = 0.5 * (lo + hi); x = (p0[0] + u * d[0], p0[1] + u * d[1])
                if x[0] ** 2 + x[1] ** 2 > (R + 3) ** 2:
                    continue
                base = [math.ceil(x[0] * EV[j][0] + x[1] * EV[j][1] - GAMMA[j]) for j in range(5)]
                if J not in (r, s) and delta > 0:
                    sj = dot(EJ, x) - GAMMA[J]
                    if C < sj < C + bent_offset(x, delta, t0):
                        base[J] -= 1                      # below the bent line, although above the straight one
                corners = []
                for dr, ds in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    K = list(base); K[r] = nr + dr; K[s] = ns + ds
                    corners.append(tuple(K))
                if any(math.hypot(*par(K)) > R for K in corners):
                    continue
                faces[frozenset(corners)] = (tuple(corners), (r, s), nr, ns)
    return faces


def crossed_triples(delta, t0):
    """crossings of two non-J lines lying strictly between the straight and the bent line c."""
    out = []
    nrange = range(-int(R) - 3, int(R) + 4)
    for r, s in itertools.combinations([j for j in range(5) if j != J], 2):
        det = EV[r][0] * EV[s][1] - EV[r][1] * EV[s][0]
        for nr in nrange:
            for ns in nrange:
                br, bs = nr + GAMMA[r], ns + GAMMA[s]
                x = ((br * EV[s][1] - bs * EV[r][1]) / det, (bs * EV[r][0] - br * EV[s][0]) / det)
                if math.hypot(*x) > R - 4:
                    continue
                sj = dot(EJ, x) - GAMMA[J]
                if C < sj < C + bent_offset(x, delta, t0):
                    out.append(x)
    return out


def adjacency(faces):
    adj = collections.defaultdict(set); edge_count = collections.Counter()
    for corners, *_ in faces.values():
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            adj[a].add(b); adj[b].add(a); edge_count[frozenset((a, b))] += 1
    return adj, edge_count


def star_types(faces):
    adj, _ = adjacency(faces)
    return {K: PA.star_type(K, adj) for K in adj if math.hypot(*par(K)) < R_INT}


def centroid(corners):
    ps = [par(K) for K in corners]
    return (sum(p[0] for p in ps) / 4, sum(p[1] for p in ps) / 4)


def pca(pts):
    n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts) / n; syy = sum((p[1] - my) ** 2 for p in pts) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts) / n
    tr, dt = sxx + syy, sxx * syy - sxy ** 2
    l1 = tr / 2 + math.sqrt(max(tr * tr / 4 - dt, 0)); l2 = tr / 2 - math.sqrt(max(tr * tr / 4 - dt, 0))
    ang = math.degrees(math.atan2(l1 - sxx, sxy)) if abs(sxy) > 1e-12 else (0.0 if sxx >= syy else 90.0)
    return math.sqrt(l1 / max(l2, 1e-12)), ang % 180


def main():
    os.makedirs(RES, exist_ok=True)
    log("=" * 96)
    log("THE WRITING WALKER -- does a walker that nudges its own grid line rewrite the tiling in its wake?")
    log("=" * 96)
    base = build(0.0, 0.0)
    ref_types = star_types(base)
    atlas = set(ref_types.values())
    log(f"unperturbed patch: {len(base)} rhombi; vertex-star atlas (interior): {len(atlas)} star types")
    # W1 structure
    require(build(0.0, 30.0) == base, "W1a: delta = 0 reproduces the unperturbed tiling exactly")
    ribbon0 = {k for k, v in base.items() if v[1][0] == J and v[2] == C}
    results = {}
    for delta in DELTAS:
        for t0 in T0S:
            F = build(delta, t0)
            _, ec = adjacency(F)
            interior_edges = [e for e in ec if all(math.hypot(*par(K)) < R - 2 for K in e)]
            ok_edges = all(ec[e] == 2 for e in interior_edges)
            removed = [k for k in base if k not in F]; added = [k for k in F if k not in base]
            tri = crossed_triples(delta, t0)
            types = star_types(F)
            illegal = [K for K, tp in types.items() if tp not in atlas]
            ribbon = ribbon0 | {k for k, v in F.items() if v[1][0] == J and v[2] == C}
            rib_verts = set(itertools.chain.from_iterable(base[k][0] if k in base else F[k][0] for k in ribbon))
            changed = [(base[k][0] if k in base else F[k][0]) for k in removed + added]
            on_road = all(any(K in rib_verts for K in cs) for cs in changed)
            ts = [dot(EJP, centroid(cs)) for cs in changed]
            in_wake = all(T_START - 1 <= t <= t0 + 1 for t in ts)
            ill_t = [dot(EJP, par(K)) for K in illegal]
            results[(delta, t0)] = dict(faces=len(F), edges_ok=ok_edges, removed=len(removed), added=len(added),
                                        flips=len(tri), on_road=on_road, in_wake=in_wake,
                                        illegal=len(illegal), ill_t=ill_t,
                                        changed_centroids=[centroid(cs) for cs in changed],
                                        illegal_pos=[par(K) for K in illegal])
    for (delta, t0), m in results.items():
        log(f"  delta {delta:<4} walker at t0 {t0:>5}: flips {m['flips']:>3}  faces removed/added "
            f"{m['removed']:>3}/{m['added']:>3}  illegal vertices {m['illegal']:>3}  on road {m['on_road']}  "
            f"in wake {m['in_wake']}")
    require(all(m["edges_ok"] for m in results.values()),
            "W1b: every perturbed patch is a valid rhombus tiling (every interior edge in exactly 2 rhombi)")
    require(all(m["removed"] == m["added"] == 3 * m["flips"] for m in results.values()),
            "W1c: the changed rhombi are exactly the predicted hexagon flips (3 out, 3 in per crossed triple point)")
    log("-" * 96)
    verdict("W2", all(m["on_road"] for m in results.values()),
            "every changed rhombus shares a vertex with the walker's own ribbon (the writing stays on the road)")
    verdict("W3", all(m["in_wake"] for m in results.values()),
            "no rhombus changes ahead of the walker or behind its birthplace (only in the wake)")
    r2s, ratios = {}, []
    for delta in DELTAS:
        xs = [t0 - T_START for t0 in T0S]; ys = [results[(delta, t0)]["flips"] for t0 in T0S]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys)); sxx = sum((a - mx) ** 2 for a in xs)
        syy = sum((b - my) ** 2 for b in ys)
        r2s[delta] = (sxy * sxy / (sxx * syy)) if syy > 0 else 0.0
    for d1, d2 in zip(DELTAS, DELTAS[1:]):
        ratios.append(results[(d2, 30.0)]["flips"] / max(results[(d1, 30.0)]["flips"], 1))
    verdict("W4", all(v >= 0.95 for v in r2s.values()) and all(1.5 <= q <= 2.5 for q in ratios),
            f"flips grow linearly with the journey (R^2 by delta: "
            + ", ".join(f"{d}: {v:.3f}" for d, v in r2s.items())
            + f") and double with the push (ratios {', '.join(f'{q:.2f}' for q in ratios)})")
    ends = [t for m in results.values() for t in []]
    mid_illegal = []
    for (delta, t0), m in results.items():
        for t in m["ill_t"]:
            if not (abs(t - t0) <= 3 or abs(t - T_START) <= 3):
                mid_illegal.append((delta, t0, round(t, 1)))
    total_ill = sum(m["illegal"] for m in results.values())
    verdict("W5", len(mid_illegal) == 0,
            f"illegal vertices only near the two ends (walker or birthplace): {total_ill} illegal in total, "
            f"{len(mid_illegal)} in the middle of the wake"
            + (f" e.g. {mid_illegal[:6]}" if mid_illegal else ""))
    log("-" * 96)
    log("Reported without prediction:")
    for delta in DELTAS:
        m = results[(delta, 30.0)]
        el, ang = pca(m["changed_centroids"]) if len(m["changed_centroids"]) > 2 else (float("nan"), float("nan"))
        wake_len = 30.0 - T_START
        log(f"  delta {delta}: rewritten region elongation {el:.1f}, axis {ang:.1f} deg (the ribbon runs at 90 deg); "
            f"illegal vertices per unit of wake {m['illegal'] / wake_len:.3f}")
    log("=" * 96)
    log("PREDICTIONS: " + ", ".join(f"{t} {'held' if hd else 'FAILED'}" for t, hd, _ in VERDICTS))
    log("STRUCTURAL CHECKS: " + ("ALL PASSED" if not FAILS else "FAILED: " + "; ".join(FAILS)))
    open(os.path.join(RES, "writing_walker_report.txt"), "w").write("\n".join(LINES) + "\n")
    json.dump({f"{d}_{t}": {k: v for k, v in m.items()} for (d, t), m in results.items()},
              open(os.path.join(RES, "writing_walker.json"), "w"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
