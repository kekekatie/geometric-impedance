#!/usr/bin/env python3
"""EXPLORATORY (post hoc, after Part A): A3's cross-world prediction may only reflect that decapod worlds are slices of
one tiling, so a probe's cell recurs in other worlds AT THE SAME PLACE. Re-run A3 learning only from other worlds' probes
at a DIFFERENT distance from the centre (|radius difference| > 1e-6 edges; same-place matches always share a radius).
Also reports how often a test probe's cell-mates in other worlds sit at its own radius."""
import os, json, random, collections
import numpy as np
import window_cells as WC

W = json.load(open(os.path.join(WC.RES, "a_worlds.json")))
lines = ["EXPLORATORY: cross-world R2, all matches vs matches at a different radius only"]
for r in map(str, WC.SCALES):
    data = []
    for w in W:
        rad = [row["rad"] for row in w["rows"]]
        y = WC.resid(rad, [row["T"][r] for row in w["rows"]])
        data.append([(row["cell"][r], round(row["rad"], 6), yi) for row, yi in zip(w["rows"], y)])
    pool = collections.defaultdict(list)                     # cell -> [(world, radius, y)]
    for wi, rows in enumerate(data):
        for c, rr, yi in rows:
            pool[c].append((wi, rr, yi))
    out = {}
    for mode in ("all", "different radius"):
        ys, ps, same_share = [], [], []
        for wi, rows in enumerate(data):
            for c, rr, yi in rows:
                other = [(r2, y2) for w2, r2, y2 in pool[c] if w2 != wi]
                if mode == "all":
                    if other:
                        same_share.append(np.mean([r2 == rr for r2, _ in other]))
                else:
                    other = [(r2, y2) for r2, y2 in other if r2 != rr]
                if len(other) >= WC.MIN_TRAIN:
                    ys.append(yi); ps.append(np.mean([y2 for _, y2 in other]))
        ys, ps = np.array(ys), np.array(ps)
        n_all = sum(len(d) for d in data)
        r2 = 1 - ((ys - ps) ** 2).sum() / ((ys - ys.mean()) ** 2).sum() if len(ys) > 2 else float("nan")
        out[mode] = (r2, len(ys) / n_all, float(np.mean(same_share)) if same_share else float("nan"))
    lines.append(f"  disc {r}: all matches R2 {out['all'][0]:+.3f} (coverage {out['all'][1]:.2f}; share of cell-mates at the same radius "
                 f"{out['all'][2]:.2f}) | different radius only R2 {out['different radius'][0]:+.3f} (coverage {out['different radius'][1]:.2f})")
print("\n".join(lines))
open(os.path.join(WC.RES, "same_place_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
