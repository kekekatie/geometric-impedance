#!/usr/bin/env python3
"""
patience.py -- how patient must a local now be? (PREREGISTRATION_patience.md, frozen before this file.)
Re-runs local_nows.py's LOCAL scheduler on the same 24 seeds with radius of patience R = 6, 12, 24 edges.
`python3 patience.py` writes results/patience_report.txt and results/patience_worlds.json.
"""
from __future__ import annotations
import os, json, collections
from multiprocessing import Pool
import numpy as np
import local_nows as LN

RS = (6.0, 12.0, 24.0)


def job(args):
    k, r = args
    LN.R = r
    out = LN.run((k, "LOCAL")); out["R"] = r
    return out


def main():
    with Pool(4, maxtasksperchild=1) as p:
        out = p.map(job, [(k, r) for r in RS for k in range(LN.N_WORLDS)], chunksize=1)
    json.dump(out, open(os.path.join(LN.RES, "patience_worlds.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    prev = json.load(open(os.path.join(LN.RES, "worlds.json")))
    bad = lambda r: r["status"] == "JAM" or r["dead_at_end"]
    rows = {3.0: [r for r in prev if r["mode"] == "LOCAL"]}
    for r in RS:
        rows[r] = [w for w in out if w["R"] == r]
    glob = [r for r in prev if r["mode"] == "GLOBAL"]
    counts = {r: sum(map(bad, rows[r])) for r in sorted(rows)}
    lines = [f"bad worlds (jammed or dead) out of {LN.N_WORLDS}: " + ", ".join(f"R={r:g}: {counts[r]}" for r in sorted(counts)) +
             f", GLOBAL: {sum(map(bad, glob))}"]
    seq = [counts[r] for r in sorted(counts)]
    q1 = all(b <= a for a, b in zip(seq, seq[1:])) and counts[24.0] < counts[3.0]
    lines.append(f"  Q1: {'HELD  ' if q1 else 'FAILED'}  non-increasing in R {seq} and R=24 below R=3")
    lines.append(f"  Q2: {'HELD  ' if counts[24.0] <= 4 else 'FAILED'}  R=24 bad {counts[24.0]}/24 (need <= 4; GLOBAL {sum(map(bad, glob))})")
    for r in sorted(rows):
        W = rows[r]
        leads = [w["slices"] - w["died"] for w in W if w["status"] == "JAM" and w["died"] is not None]
        lines.append(f"  reported R={r:g}: statuses {dict(collections.Counter(w['status'] for w in W))}; dead at end {sum(w['dead_at_end'] for w in W)}; "
                     f"slices median {np.median([w['slices'] for w in W]):.0f}; tiles median {np.median([w['tiles'] for w in W]):.0f}; "
                     f"choices median {np.median([len(w['choices']) for w in W]):.0f}; max simultaneous {max(w['max_choices_per_slice'] for w in W)}; "
                     f"death-to-jam leads median {np.median(leads) if leads else float('nan')}")
    print("\n".join(lines))
    open(os.path.join(LN.RES, "patience_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
