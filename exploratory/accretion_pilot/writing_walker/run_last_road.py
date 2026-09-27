#!/usr/bin/env python3
"""run_last_road.py -- D4's last road, (0,-2), with the 400,000-state cap checked after EVERY state
(strict_cap) instead of only between depth levels: its 38-vertex centre knot made one level overshoot the cap by
far (6 h, 5 GB, run stopped). Same search otherwise. Appends to results/decapod_roads.jsonl like decapod_d4.py."""
import json, os, time
import decapod as D, writing_walker as W, healing as H

J, C = 0, -2
base = W.build(0.0, 0.0); atlas = set(W.star_types(base).values())
F, EJP = D.build_road(J, C, 0.2)
types = W.star_types(F); illegal = {K for K, tp in types.items() if tp not in atlas}
mid = [K for K in illegal if abs(W.dot(EJP, W.par(K))) <= 25]
gs, left = [], set(mid)
while left:
    g, st = [], [left.pop()]
    while st:
        u = st.pop(); g.append(u)
        for q in list(left):
            if H.dist(u, q) <= H.LINK:
                left.discard(q); st.append(q)
    gs.append(g)
T = H.Tiling([cs for cs, *_ in F.values()])
rows = []
for g in sorted(gs, key=len):
    t0 = time.time()
    d = D.heal_search_lean(T, g, atlas, illegal, strict_cap=True)
    c = D.ring_centre(g)
    rows.append(dict(J=J, C=C, size=len(g), healed=d is not None, depth=d, ring=c is not None, centre=c,
                     t=round(sum(W.dot(EJP, W.par(K)) for K in g) / len(g), 2), strict_cap=True))
    print(f"knot size {len(g)} at t={rows[-1]['t']:+.1f}: {'HEALED d=' + str(d) if d else 'stubborn'} "
          f"ring={c is not None} ({time.time() - t0:.0f}s)", flush=True)
with open(os.path.join(W.RES, "decapod_roads.jsonl"), "a") as f:
    f.write(json.dumps({"J": J, "C": C, "rows": rows}, default=str) + "\n")
print("appended road (0,-2)")
