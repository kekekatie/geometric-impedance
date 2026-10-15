#!/usr/bin/env python3
"""EXPLORATORY numerical checks for DERIVATION.md (after the registered run).
 (a) the window's facet normals (all 4 pentagons, from window_cells.window) point along exactly the five lines of
     zeta^(2j), the window images of the five edge families (perp_map.perp: K_j steps along family-j edges);
 (b) in every distinct situation of cut_direction.py, the cut line's normal lies along zeta^(2j) of the decided family j;
 (c) the physical strip direction predicted by the derivation, 108 + 72 j (perpendicular to family-j edges at 18 + 72 j),
     equals 108 - 2 x cut direction (mod 180) as an identity, and matches the measured strip axis.
Writes results/derivation_check_EXPLORATORY.txt."""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "slack"))
import slack as Sl

mod180 = lambda a: a % 180
d180 = lambda a, b: min(abs(a - b) % 180, 180 - abs(a - b) % 180)
zeta2 = {j: mod180(144 * j) for j in range(5)}            # line direction of zeta^(2j)
lines = ["EXPLORATORY derivation checks"]
# (a)
normals = sorted({round(mod180(round(math.degrees(math.atan2(n[1], n[0])), 6)), 6) % 180 for rk in range(4) for n in Sl.WIN[rk][0]})
lines.append(f"  (a) facet-normal line directions across the 4 pentagons: {normals}; zeta^(2j) line directions: {sorted(zeta2.values())}; "
             f"same set: {sorted(round(x, 6) for x in zeta2.values()) == normals}")
# (b), (c)
W = json.load(open(os.path.join(HERE, "results", "worlds.json")))
first = {}
for w in W:
    for c in w["choices"]:
        first.setdefault(c["key"], c)
U = [c for c in first.values() if c.get("shares")]
dev_b = []; dev_c = []; ident = []
for c in U:
    j = int(np.argmax(c["shares"]))
    normal = mod180(c["line_angle"] - 90)
    dev_b.append(d180(normal, zeta2[j]))
    pred = mod180(108 + 72 * j)
    ident.append(d180(pred, mod180(108 - 2 * c["line_angle"])))
    if c["ratio"] >= 3:
        dev_c.append(d180(pred, c["axis"]))
lines.append(f"  (b) cut normal vs zeta^(2j) of the decided family: max deviation {max(dev_b):.6f} deg over {len(U)} situations")
lines.append(f"  (c) 108 + 72 j vs 108 - 2 x cut: max difference {max(ident):.6f} deg (identity given (b)); "
             f"vs measured strip axis: max {max(dev_c):.2f} deg over {len(dev_c)} elongated strips")
print("\n".join(lines))
open(os.path.join(HERE, "results", "derivation_check_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
