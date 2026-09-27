#!/usr/bin/env python3
"""decapod_d4.py -- the pre-registered D4 test of decapod.py (same logic: decapod.road_task on the same 18
roads), run INCREMENTALLY: each road's knots are appended to results/decapod_roads.jsonl as soon as that road
finishes, and a restart skips roads already done. (Earlier attempts: OOM-killed workers; then a 2.5 h timeout
that discarded everything because results were only written at the end.)
Run with --summary to evaluate D4 from whatever roads are complete."""
import os, sys, json
from multiprocessing import Pool
import decapod as D

ROADS = [(0, c) for c in range(-4, 5)] + [(1, c) for c in range(-4, 5)]
OUT = os.path.join(D.W.RES, "decapod_roads.jsonl")


def done_roads():
    got = {}
    if os.path.exists(OUT):
        for line in open(OUT):
            rec = json.loads(line); got[(rec["J"], rec["C"])] = rec["rows"]
    return got


def summary():
    got = done_roads()
    rows = [r for road in ROADS if road in got for r in got[road]]
    out = [f"roads complete: {len(got)}/{len(ROADS)}"]
    for r in rows:
        out.append(f"    road family {r['J']} line {r['C']:+d}: knot at t={r['t']:+6.1f} size {r['size']:>2} "
                   f"{'HEALED d=' + str(r['depth']) if r['healed'] else 'stubborn':<11} decagon ring: {r['ring']}")
    agree = sum(1 for r in rows if r["ring"] == (not r["healed"]))
    stub = [r for r in rows if not r["healed"]]
    out.append(f"  {len(rows)} knots; stubborn: {len(stub)}; with decagon ring: {sum(r['ring'] for r in rows)}; "
               f"stubborn AND ring: {sum(1 for r in stub if r['ring'])}")
    if len(got) == len(ROADS):
        held = bool(rows) and agree / len(rows) >= 0.9
        out.append(f"  D4: {'HELD  ' if held else 'FAILED'}  'stubborn' agrees with 'contains a decagon ring' for "
                   f"{agree}/{len(rows)} knots ({agree / max(len(rows), 1):.0%}; need >= 90%)")
    else:
        out.append(f"  (partial) agreement so far: {agree}/{len(rows)}")
    print("\n".join(out), flush=True)
    open(os.path.join(D.W.RES, "decapod_d4.log"), "w").write("\n".join(out) + "\n")


def run(road):
    return road, D.road_task(road)


if __name__ == "__main__":
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    todo = [r for r in ROADS if r not in done_roads()]
    print(f"{len(todo)} roads to run", flush=True)
    with Pool(4, maxtasksperchild=1) as p:
        for road, rows in p.imap_unordered(run, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps({"J": road[0], "C": road[1], "rows": rows}, default=str) + "\n")
            print(f"road {road} done: {len(rows)} knots", flush=True)
    summary()
