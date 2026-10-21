#!/usr/bin/env python3
"""
Stage 1 exploration (descriptive only): does depth quantise into discrete
vertex-environment bands on the 2D substrates (AB, Penrose)?

DISCIPLINE NOTE: this script is intentionally DESCRIPTIVE. It reports the shell
structure and, transparently, ALL candidate successive-ratios (depth,
depth-complement, population/area) side by side -- precisely so that no single
one can be silently selected for matching T1=0.158. Per the sealed anti-fishing
rule (PREREGISTRATION.md sec 4), the legitimate "grip" quantity must be NAMED by
the pre-registration author before any ratio is promoted to a T1 test.
"""
import sys, json
sys.path.insert(0, '../reverse_loop_test')
import numpy as np
from geometry import Patch

def shells(substrate, radius=30.0, interior_frac=0.75):
    p = Patch(substrate, radius=radius)
    r = np.linalg.norm(p.par, axis=1); interior = r < interior_frac*radius
    deg = np.array([len(a) for a in p.adj])
    out = []
    for c in sorted(set(deg[interior].tolist())):
        m = interior & (deg == c)
        if m.sum() < 5: continue
        out.append(dict(coordination=int(c), count=int(m.sum()),
                        depth_mean=float(p.depth[m].mean()),
                        depth_std=float(p.depth[m].std())))
    return out, float(p.depth[interior].max())

def ratios(shells_list, dmax):
    d = np.array([s['depth_mean'] for s in shells_list])
    n = np.array([s['count'] for s in shells_list], float)
    rows = []
    for i in range(1, len(d)):
        rows.append(dict(
            step=f"{shells_list[i-1]['coordination']}->{shells_list[i]['coordination']}",
            depth_ratio=round(d[i]/d[i-1], 4),
            depthcomplement_ratio=round((dmax-d[i])/(dmax-d[i-1]), 4),
            population_ratio=round(n[i]/n[i-1], 4)))
    return rows

report = {"note": "Stage 1 descriptive exploration. NO grip quantity selected; "
                  "all candidate ratios shown transparently. T1 test deferred "
                  "until grip is named by the pre-registration author.",
          "T1_target": 0.158, "T1_sigma": 0.027,
          "live_powers": {"(sqrt2-1)^2": 0.172, "1/phi^4": 0.146},
          "substrates": {}}
for sub in ['ammann_beenker', 'penrose']:
    sh, dmax = shells(sub)
    report["substrates"][sub] = dict(n_bands=len(sh), depth_max=round(dmax,4),
                                     shells=sh, candidate_ratios=ratios(sh, dmax))
    print(f"=== {sub}: {len(sh)} depth bands, depth_max={dmax:.3f} ===")
    for s in sh:
        print(f"  coord {s['coordination']}: n={s['count']:5d} depth={s['depth_mean']:.4f}")
    print("  candidate successive ratios (depth / depth-complement / population):")
    for rr in ratios(sh, dmax):
        print(f"    {rr['step']}: depth={rr['depth_ratio']:.3f}  "
              f"complement={rr['depthcomplement_ratio']:.3f}  "
              f"pop={rr['population_ratio']:.3f}")
json.dump(report, open('stage1_exploration.json','w'), indent=2)
print("\n-> stage1_exploration.json  (T1=0.158; no ratio promoted -- grip unnamed)")
