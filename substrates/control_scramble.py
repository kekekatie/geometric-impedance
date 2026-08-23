#!/usr/bin/env python3
"""
Matched-scramble / QC-specificity control (sealed prereg rung 4).

Flips are the only scrambling operation available, and they simultaneously add
defects and destroy quasiperiodic order, so a clean "same defects, no order"
counterpart does not exist. The honest control is therefore the trajectory: track
the residual continuation-volume structure (Omega_r beyond local degree) as the
tiling moves from the quasiperiodic point (low flip damage) to the random-tiling
bulk (flip-saturated). Local mobility d_R is roughly constant along the way, so the
comparison is approximately degree-matched; defect fraction is reported since it is
the one low-order statistic that necessarily varies.

Reading:
  - residual_std elevated near the QC and decaying to a floor as the tiling
    saturates  ->  the structure is quasiperiodic-specific (rung 4 alive);
  - residual_std flat across the trajectory                ->  generic rhombus-tiling
    combinatorics (H1a), and the family hint is not about quasiperiodic order.
Fixed R=2.0, r=3 (strongest-signal cell from the bulk sweep).
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import apply_flips
from phason_energy import clean_frequencies, vertex_types
from intrinsic_drift_bulk_sweep import region_arrays, residual

NAME = {8: "silver", 10: "golden", 12: "platinum"}
DAMAGE = [0.03, 0.15, 0.5, 1.5]          # near-QC -> saturated random tiling


def defect_fraction(lifts, ustar, star, K, par4, vocab):
    types = vertex_types(lifts, ustar, star, K, par4)
    bulk = [t for t in types if len(t) >= 3]
    if not bulk:
        return np.nan
    return sum(1 for t in bulk if t not in vocab) / len(bulk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=9)
    ap.add_argument("--radius", type=float, default=2.0)
    ap.add_argument("--r", type=int, default=3)
    ap.add_argument("--ncenters", type=int, default=10)
    ap.add_argument("--margin", type=float, default=1.5)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    R, r = args.radius, args.r

    print(f"QC-specificity control: extent {args.extent}, R={R}, r={r}, "
          f"{args.ncenters} bulk regions/level\n")
    for N in (8, 10, 12):
        st = structure(N)
        star, K, par4 = st["star"], st["K"], st["par4"]
        clean, _, _, ust0 = generate(N, args.extent)
        vocab = set(clean_frequencies(vertex_types(clean, ust0, star, K, par4)))
        rng = np.random.default_rng(args.seed)

        print(f"=== {NAME[N]} ({N}-fold), n={len(clean)} ===")
        print(f"{'flips/vtx':>10} {'defect%':>8} {'d_R':>5} {'V':>7} {'resid_std':>10}")
        for dmg in DAMAGE:
            L, U, _ = apply_flips(clean, ust0, star, K,
                                  int(round(dmg * len(clean))), rng)
            P = L @ par4
            rad = np.linalg.norm(P - P.mean(0), axis=1)
            bulk = np.where(rad + R + args.margin < rad.max())[0]
            pick = rng.choice(bulk, size=min(args.ncenters, len(bulk)), replace=False)
            Vs, resids, dRs = [], [], []
            for ci in pick:
                ra = region_arrays(L, U, star, K, par4, P[ci], R, r)
                if ra is None:
                    continue
                logd, logo = ra
                Vs.append(float(logo.var()))
                resids.append(residual(logd, logo))
                dRs.append(len(logo))
            df = defect_fraction(L, U, star, K, par4, vocab)
            dR = np.mean(dRs) if dRs else np.nan
            rstd = np.std(np.concatenate(resids)) if resids else np.nan
            vm = np.mean(Vs) if Vs else np.nan
            print(f"{dmg:>10.2f} {100*df:>7.1f}% {dR:>5.1f} {vm:>7.3f} {rstd:>10.4f}",
                  flush=True)
        print()


if __name__ == "__main__":
    main()
