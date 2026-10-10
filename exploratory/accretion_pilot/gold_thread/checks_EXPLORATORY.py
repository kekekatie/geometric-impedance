#!/usr/bin/env python3
"""EXPLORATORY: (1) branching -- how many open ends does each ribbon (component) have? A thread has at most 2.
(2) is the strip a choice decides a single ribbon? For each choice: the share of strip tiles (sibling A only) lying in
the largest single ribbon of any family, in sibling A's patch. Same world as ribbons_EXPLORATORY.py."""
import collections, os
import ribbons_EXPLORATORY as R
D, M = R.D, R.M
P, rnd, Rr, ch = R.grow_world()
tiles = list(P.tris); rib, be = R.ribbons(tiles)
ends = collections.Counter()
for t in tiles:
    legs, _ = R.legs_and_base(t)
    for p, q in legs:
        if len(be[R.ek(p, q)]) == 1:
            j = M.edge_dir(p, q)[0]; ends[(j, rib[j][D.dkey(t)])] += 1
comps = {(j, r) for j in rib for r in set(rib[j].values())}
dist = collections.Counter(ends.get(c, 0) for c in comps)
lines = [f"(1) ribbons in world {R.WORLD}: {len(comps)}; open ends per ribbon: {dict(sorted(dist.items()))} (a branch would need 3+)"]
for c in ch:
    Q, new, st, rr = c["sibs"][0]; rb, _ = R.ribbons(list(Q.tris))
    sk = [D.dkey(t) for t in c["strip"]]
    best = max(((j, max(collections.Counter(rb[j][k] for k in sk if k in rb[j]).values(), default=0)) for j in range(5)), key=lambda x: x[1])
    lines.append(f"(2) choice at slice {c['round']}: strip {len(sk)} tiles; largest single ribbon holds {best[1]} ({best[1] / len(sk):.0%}), family {best[0]}")
print("\n".join(lines)); open(os.path.join(R.RES, "checks_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
