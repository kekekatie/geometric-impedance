#!/usr/bin/env python3
"""
(R, r) sensitivity sweep -- the gate before any control or interpretation
(PREREG_intrinsic_drift.md, Amendment 1).

The r=2 whole-patch pilot gave corr(d, Omega) ~ 1.0; the r=3 local run gave < 1.
Before trusting that, we need the qualitative pattern to be stable: decoupling
that grows with horizon r and holds across local radii R, not a hand-picked
(R, r) artefact. For each family and each (R, r) cell this reports, over many
(state, region) samples, the mean +/- SEM of

  - corr(d_R, Omega_r)  : degree-volume coupling (1.0 = volume is just degree);
  - V_r                 : branch dispersion (uneven doors);

so we can read whether corr falls with r consistently and whether the family
pattern survives changing R. No interpretation of family ordering here -- this
only decides whether the estimator has a stable signal at all.
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import apply_flips
from intrinsic_drift_local import region_branch

NAME = {8: "silver", 10: "golden", 12: "platinum"}
RADII = [2.0, 2.5, 3.0]
HORIZONS = [1, 2, 3]
SKIP = {(3.0, 3)}                      # too costly; omitted


def sem(x):
    x = np.asarray([v for v in x if np.isfinite(v)])
    return (float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 1 \
        else (float(x.mean()) if len(x) else np.nan, np.nan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=6)
    ap.add_argument("--nstates", type=int, default=3)
    ap.add_argument("--gap", type=int, default=6)
    ap.add_argument("--ncenters", type=int, default=5)
    args = ap.parse_args()

    print(f"(R,r) sweep: extent {args.extent}, {args.nstates} states x "
          f"{args.ncenters} regions/cell\n")
    for N in (8, 10, 12):
        st = structure(N)
        star, K, par4 = st["star"], st["K"], st["par4"]
        lifts, _, _, ustar = generate(N, args.extent)
        # pre-sample the states and centres once, reuse across (R,r)
        rng = np.random.default_rng(0)
        states = []
        L, U = lifts.copy(), ustar.copy()
        for s in range(args.nstates):
            if s:
                L, U, _ = apply_flips(L, U, star, K, args.gap, rng)
            P = L @ par4
            rad = np.linalg.norm(P - P.mean(0), axis=1)
            cand = np.where(rad < 0.55 * rad.max())[0]
            centers = P[rng.choice(cand, size=min(args.ncenters, len(cand)),
                                   replace=False)]
            states.append((L.copy(), U.copy(), centers))

        print(f"=== {NAME[N]} ({N}-fold) ===")
        print(f"{'R \\ r':>7}" + "".join(f"{r:>18}" for r in HORIZONS))
        for R in RADII:
            cells = []
            for r in HORIZONS:
                if (R, r) in SKIP:
                    cells.append("        --        ")
                    continue
                corrs, Vs = [], []
                for L, U, centers in states:
                    for c in centers:
                        res = region_branch(L, U, star, K, par4, c, R, r)
                        if res:
                            corrs.append(res["corr"])
                            Vs.append(res["V"])
                cm, ce = sem(corrs)
                vm, ve = sem(Vs)
                cells.append(f" c{cm:.2f}±{ce:.2f} V{vm:.3f}")
            print(f"{R:>7.1f}" + "".join(f"{x:>18}" for x in cells), flush=True)
        print()


if __name__ == "__main__":
    main()
