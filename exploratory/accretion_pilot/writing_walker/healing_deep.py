#!/usr/bin/env python3
"""healing_deep.py -- EXPLORATORY (after the pre-registered healing run): the one stubborn knot sits at the
tiling's centre (t = 0). Is it truly locally unhealable, or just deeper? Deeper search (depth 6) and
wider radius (4) on that knot only, for pushes 0.2 and 0.05. Also prints the knot-position pattern."""
import healing as H, writing_walker as W
base = W.build(0.0, 0.0); atlas = set(W.star_types(base).values())
for delta in (0.2, 0.05):
    T, illegal, groups = H.knots_of(W.build(delta, 30.0), atlas)
    ts = sorted(round(sum(W.dot(W.EJP, W.par(K)) for K in g) / len(g), 2) for g in groups)
    print(f"push {delta}: knot positions along the road: {ts}")
    g = max(groups, key=len)
    for depth, radius in ((5, 3.0), (6, 3.0), (5, 4.0)):
        H.DEPTH, H.RADIUS = depth, radius
        d = H.heal_search(T, g, atlas, illegal)
        print(f"   centre knot ({len(g)} vertices), depth {depth}, radius {radius}: "
              + (f"HEALED at depth {d}" if d else "NOT healed"), flush=True)
