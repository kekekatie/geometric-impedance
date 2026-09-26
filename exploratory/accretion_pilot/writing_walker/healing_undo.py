#!/usr/bin/env python3
"""healing_undo.py -- EXPLORATORY. The blind depth-5/6 search on the centre knot (healing_deep.py) ran out of
time. Targeted version: allow only UNDO flips (flips whose three new rhombi all belong to the pristine tiling),
i.e. locally reverse the walker's own writing, and search much deeper (up to depth 14) within radius 3, 4, 6.
Same heal criterion as healing.py. Run for every mid-wake knot, both pushes."""
import math, collections
import healing as H, writing_walker as W

def undo_search(T, knot, atlas, illegal_before, base_keys, radius, depth_max):
    pts = list(knot); ks = set(knot); others = illegal_before - ks
    near = lambda K: min(H.dist(K, q) for q in pts) <= radius
    local = [cs for cs in T.faces.values() if any(min(H.dist(K, q) for q in pts) <= radius + 3 for K in cs)]
    start = H.Tiling(local); seen = {frozenset(start.faces)}; frontier = [(start, set())]
    for depth in range(1, depth_max + 1):
        nxt = []
        for tl, ch0 in frontier:
            for v in [K for K in list(tl.vf) if near(K)]:
                plan = tl.flip_plan(v)
                if plan is None or not all(frozenset(cs) in base_keys for cs in plan[1]):
                    continue
                t2 = tl.copy(); t2.apply(plan); key = frozenset(t2.faces)
                if key in seen: continue
                seen.add(key)
                ch = ch0 | H.affected(plan) | {K for k in plan[0] for K in tl.faces[k]}
                check = {K for K in (ch | ks) if K in t2.vf}
                bad = {K for K in check if t2.star(K) not in atlas}
                if not (bad - others) and not (bad & ks):
                    return depth, len(seen)
                nxt.append((t2, ch))
        frontier = nxt
        if not frontier: return None, len(seen)
    return None, len(seen)

base = W.build(0.0, 0.0); atlas = set(W.star_types(base).values()); base_keys = set(base)
for delta in (0.2, 0.05):
    T, illegal, groups = H.knots_of(W.build(delta, 30.0), atlas)
    for g in sorted(groups, key=lambda g: sum(W.dot(W.EJP, W.par(K)) for K in g)):
        t = sum(W.dot(W.EJP, W.par(K)) for K in g) / len(g)
        res = []
        for radius in (3.0, 4.0, 6.0):
            d, n = undo_search(T, g, atlas, illegal, base_keys, radius, 14)
            res.append(f"r={radius:g}: " + (f"healed at {d}" if d else f"no ({n} states, all undo paths exhausted or depth 14)"))
        print(f"push {delta} knot at t={t:+.1f} ({len(g)} vertices): " + "; ".join(res), flush=True)
