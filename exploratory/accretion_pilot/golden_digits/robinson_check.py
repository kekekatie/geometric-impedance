#!/usr/bin/env python3
"""robinson_check.py -- PREREGISTRATION_robinson.md (frozen before this file). The identical shape census
(shapes_EXPLORATORY.task) applied to the 24 worlds of ../slack/ (thread_influence centres, streams 20261110 + k)."""
import os, json, collections
from multiprocessing import Pool
import shapes_EXPLORATORY as SH
GD, T = SH.GD, SH.T
GD.centres = lambda: T.centres()          # slack's worlds: the first 24 wedge centres...
GD.SEED0 = T.SEED0                         # ...and slack's random streams
TARGET = 2 - GD.TAU                        # 1/tau^2

if __name__ == "__main__":
    with Pool(4, maxtasksperchild=1) as p:
        R = [r for out in p.map(SH.task, range(24)) for r in out]
    json.dump(R, open(os.path.join(GD.RES, "robinson_rows.json"), "w"))
    rob = {(1.0, 1.0, 3.0): "gnomon", (1.0, 2.0, 2.0): "golden triangle"}
    cls = [r for r in R if r["F"] and r["F"][0] == 3 and tuple(r["F"][1]) in rob and r["through_corners"] == 1]
    ok = [r for r in cls if abs(r["share"] - TARGET) <= 0.001 and tuple(r["small"] or ()) == tuple(r["F"][1])
          and r["big"] is not None and tuple(r["big"]) in rob and tuple(r["big"]) != tuple(r["F"][1])]
    held = bool(cls) and len(ok) >= 0.95 * len(cls)
    lines = [f"Robinson check on the slack worlds: {len(R)} two-option choices with both pieces live",
             f"  R: {'HELD  ' if held else 'FAILED'}  Robinson triangle cut through exactly one corner -> share 1/tau^2, smaller piece same type, "
             f"larger piece the other type: {len(ok)}/{len(cls)} (need >= 95%)"]
    for r in cls:
        if r not in ok:
            lines.append(f"      exception: F {rob[tuple(r['F'][1])]}, share {r['share']:.4f}, small {r['small']}, big {r['big']}")
    tab = collections.Counter((r["F"][0], tuple(r["F"][1]), round(r["share"], 3), r["through_corners"], r["parallel_to_side"]) for r in R if r["F"])
    lines.append("  reported: census (corners, angles, share, corners crossed, parallel to a side) x count:")
    lines += [f"      {k} x{v}" for k, v in tab.most_common()]
    print("\n".join(lines))
    open(os.path.join(GD.RES, "robinson_check.txt"), "w").write("\n".join(lines) + "\n")
