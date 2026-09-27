#!/usr/bin/env python3
"""recheck_fixed_vertex_ok.py -- re-runs this study's main arms with the CORRECTED vertex check (found in
../soft_zone: the original vertex_ok misread gaps wider than pi at a vertex as overlaps). Same seeds, same
rules; writes results/recheck_fixed_vertex_ok.txt; the original report is left untouched for comparison."""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "soft_zone"))
import soft_zone                      # noqa: F401  (importing it installs the fixed vertex_ok on laying_the_tiling.Patch)
import laying_the_tiling as L
assert L.Patch.vertex_ok is soft_zone.vertex_ok_fixed
out = []
seed = L.seed_patch(0j, 3 * L.SCALE_LEN)
refset = {L.canon(t) for t in L.REF}
for rule in ("LOCAL-DICE", "LOCAL-FORCED"):
    rs = [L.lay(rule, seed, random.Random(L.SEED + k)) for k in range(L.RUNS)]
    jams = sorted(n for n, st, _ in rs if st == "JAM")
    agree = [sum(1 for t in P.tris if L.canon(t) in refset) / len(P.tris) for _, _, P in rs]
    out.append(f"{rule}: jammed {len(jams)}/{L.RUNS} (tiles before jam: {jams}); reached {L.MAX_TILES}: "
               f"{sum(1 for _, st, _ in rs if st == 'ok')}; agreement min {min(agree):.1%}, exact "
               f"{sum(1 for a in agree if a == 1.0)}/{L.RUNS}; guesses {[P.guesses for _, _, P in rs]}")
    print(out[-1], flush=True)
for rule in ("COPY", "SCALE", "WRONGSCALE"):
    n, st, P = L.lay(rule, seed, random.Random(L.SEED))
    m = sum(1 for t in P.tris if L.canon(t) in refset) / len(P.tris)
    out.append(f"{rule} from the centre: {n} half-tiles, ended {st}, agreement {m:.1%}")
    print(out[-1], flush=True)
open(os.path.join(HERE, "results", "recheck_fixed_vertex_ok.txt"), "w").write("\n".join(out) + "\n")
