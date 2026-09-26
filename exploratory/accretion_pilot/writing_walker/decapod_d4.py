#!/usr/bin/env python3
"""decapod_d4.py -- runs the pre-registered D4 test of decapod.py in a fresh, lean process (the first run's
worker pool hung after the memory-heavy D3 stage). Identical logic: decapod.road_task on the same 18 roads."""
import os, json
from multiprocessing import Pool
import decapod as D

if __name__ == "__main__":
    roads = [(0, c) for c in range(-4, 5)] + [(1, c) for c in range(-4, 5)]
    with Pool(4, maxtasksperchild=1) as p:
        rows = [r for rs in p.imap(D.road_task, roads) for r in rs]
    out = []
    for r in rows:
        out.append(f"    road family {r['J']} line {r['C']:+d}: knot at t={r['t']:+6.1f} size {r['size']:>2} "
                   f"{'HEALED d=' + str(r['depth']) if r['healed'] else 'stubborn':<11} decagon ring: {r['ring']}")
    agree = sum(1 for r in rows if r["ring"] == (not r["healed"]))
    stub = [r for r in rows if not r["healed"]]
    out.append(f"  {len(rows)} knots on {len(roads)} roads; stubborn: {len(stub)}; with decagon ring: "
               f"{sum(r['ring'] for r in rows)}; stubborn AND ring: {sum(1 for r in stub if r['ring'])}")
    held = bool(rows) and agree / len(rows) >= 0.9
    out.append(f"  D4: {'HELD  ' if held else 'FAILED'}  'stubborn' agrees with 'contains a decagon ring' for "
               f"{agree}/{len(rows)} knots ({agree / max(len(rows), 1):.0%}; need >= 90%)")
    print("\n".join(out), flush=True)
    open(os.path.join(D.W.RES, "decapod_d4.log"), "w").write("\n".join(out) + "\n")
    json.dump(rows, open(os.path.join(D.W.RES, "decapod_roads.json"), "w"), default=str)
