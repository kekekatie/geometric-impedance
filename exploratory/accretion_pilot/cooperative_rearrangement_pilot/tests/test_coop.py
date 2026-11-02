#!/usr/bin/env python3
"""
test_coop.py -- focused tests for the cooperative-rearrangement pilot. Exits
non-zero on failure. Run (from src dir, with EFP_SNAPSHOT set):
    python3 ../tests/test_coop.py
"""
from __future__ import annotations
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import coop_common as CC
from coop_common import L, S
import safeguards                  # audited validator (reused)
import hexflip as HF

FAILS = []
def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    st = json.loads((CC.INPUT / "retained_state.json").read_text())
    band = [CC.dtile(t) for t in st["tiles"]]
    rank = {int(k): int(v) for k, v in st["rank"].items()}
    BC = CC.BandConstraints(band, rank=rank)

    # 1. full band (empty region) is infeasible, box-independently
    base = CC.classify_exterior(BC.full_cmax)
    check(base["verdict"] == "infeasible", f"full band infeasible (got {base['verdict']})")

    # 2. provenance: a vertex constraint survives unless its ENTIRE star is engulfed.
    #    Take a vertex with a multi-tile star; engulf all-but-one of its tiles ->
    #    the vertex is NOT engulfed and its contribution remains.
    vk = max(BC.vincident, key=lambda v: len(BC.vincident[v]))
    star = list(BC.vincident[vk])
    partial = set(star[:-1])                       # leave one incident tile outside
    E_partial = BC.engulfed_vertices(partial)
    check(vk not in E_partial, "vertex with one incident tile outside R is NOT engulfed (provenance)")
    full_star = set(star)
    E_full = BC.engulfed_vertices(full_star)
    check(vk in E_full, "vertex with its entire star in R IS engulfed")

    # 3. classify_exterior on a controlled feasible system
    r_feas = CC.classify_exterior({(0, 0): -1.0, (0, 1): -1.0})
    check(r_feas["verdict"] == "feasible", f"synthetic feasible system (got {r_feas['verdict']})")

    # 4. completed-replacement validator: positive (identity) + rejection (perturbed)
    mids = [(complex(*d["p"]) + complex(*d["q"])) / 2 for d in st["dead_sites"]]
    nbhd = [t for t in band if any(abs(HF.tile_centroid(t) - m) < 6 * S for m in mids)]
    hexes = HF.find_flip_hexagons(nbhd)
    check(len(hexes) > 0, "found flip hexagons near dead sites")
    if hexes:
        h = hexes[0]["tiles"]
        # audited validator against the FULL exterior (band minus region)
        exterior_full = [t for t in band if CC.dk(t) not in {CC.dk(u) for u in h}]
        check(safeguards.completed_replacement_legal(exterior_full, h, list(h)),
              "positive control: identity replacement is legal (audited validator)")
        bad = list(h); c, A, B, Cc = bad[0]; bad[0] = (c, A + 0.13 + 0.07j, B, Cc)
        check(not safeguards.completed_replacement_legal(exterior_full, h, bad),
              "rejection control: atlas-breaking replacement is rejected")
        check(not safeguards.completed_replacement_legal(exterior_full, h, []),
              "rejection control: EMPTY filling is rejected (the audited defect)")
        # the deprecated weak validator is hardened to at least reject empties too
        check(not CC.completed_replacement_legal(exterior_full, h, []),
              "deprecated validator no longer accepts an empty filling")

    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)}"); sys.exit(1)
    print("ALL COOP PILOT CHECKS PASSED.")


if __name__ == "__main__":
    main()
