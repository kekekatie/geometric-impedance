#!/usr/bin/env python3
"""EXPLORATORY (post hoc, prompted by Astra's review): the README's 'turning' number was the NET angle change between a
ribbon's ends, so bends that cancel disappear. Here, from the saved 4,000-tile ribbons, a fuller measure: for each ribbon
(points from 2.5 to 12 edges out, a radius every world reaches), fit a straight line (principal axis) and report the RMS
and maximum perpendicular deviation from it, in edges."""
import json, os
import numpy as np
W = json.load(open(os.path.join(os.path.dirname(__file__), "results", "worlds.json")))
lines = ["EXPLORATORY: ribbon deviation from a straight line (2.5-12 edges out; edges)"]
for w in W:
    rms, mx = [], []
    for r in w["ribbons"]:
        p = np.array([q for q in r if 2.5 <= np.hypot(*q) <= 12.0])
        if len(p) < 5:
            continue
        c = p - p.mean(axis=0)
        u = np.linalg.svd(c, full_matrices=False)[2][0]
        d = np.abs(c @ np.array([-u[1], u[0]]))
        rms.append(float(np.sqrt((d ** 2).mean()))); mx.append(float(d.max()))
    lines.append(f"  {w['kind']:<8} seed {w['seed']:>3}: RMS deviation mean {np.mean(rms):.3f} (range {min(rms):.3f}-{max(rms):.3f}); "
                 f"max deviation mean {np.mean(mx):.3f} (largest {max(mx):.3f})")
print("\n".join(lines))
open(os.path.join(os.path.dirname(__file__), "results", "straightness_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
