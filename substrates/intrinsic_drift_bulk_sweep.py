#!/usr/bin/env python3
"""
Bulk-restricted (R, r) sweep on bigger patches (GPT's spec after the amber gate).

At extent 6 the radius change was confounded with boundary contamination. Here:
  - bigger patches (default extent 9);
  - every local disk sampled COMFORTABLY inside the bulk (centre distance + R + margin
    < patch radius), so changing R is a near-pure scale change, not a change in how
    much boundary the disk feels;
  - R not tuned by family; family ordering treated as secondary/non-established.

The question is only whether the horizon-driven degree decoupling is stable across R
once finite-size is reduced. The key diagnostic, per GPT, is not corr alone but the
RESIDUAL variation of log Omega_r at fixed local degree: for each region, remove the
within-region degree fit from log Omega_r and pool the residuals; residual_std is the
continuation-volume structure that degree genuinely cannot explain. A stable, non-zero
residual_std growing with r (and steady across R) is a live rung 3; an erratic or
vanishing one in the bulk is a scale artefact and we pivot without remorse.
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import apply_flips
from continuation_volume import flippable_local, omega_local, one_step_local

NAME = {8: "silver", 10: "golden", 12: "platinum"}
RADII = [2.0, 2.5, 3.0]
HORIZONS = [1, 2, 3]
SKIP = {(3.0, 3)}


def region_arrays(lifts, ustar, star, K, par4, center, radius, r):
    moves = one_step_local(lifts, ustar, star, K, par4, center, radius)
    if len(moves) < 4:
        return None
    logo = np.array([np.log(max(omega_local(L, U, star, K, par4, center, radius, r), 1))
                     for L, U in moves])
    logd = np.array([np.log(max(len(flippable_local(L, U, star, K, par4, center, radius)), 1))
                     for L, U in moves])
    return logd, logo


def residual(logd, logo):
    if logd.std() > 1e-9:
        b = np.polyfit(logd, logo, 1)
        return logo - np.polyval(b, logd)
    return logo - logo.mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=9)
    ap.add_argument("--nstates", type=int, default=3)
    ap.add_argument("--gap", type=int, default=8)
    ap.add_argument("--ncenters", type=int, default=8)
    ap.add_argument("--margin", type=float, default=1.5)
    args = ap.parse_args()

    print(f"Bulk-restricted (R,r) sweep: extent {args.extent}, {args.nstates} states, "
          f"up to {args.ncenters} bulk regions/cell, margin {args.margin}\n")
    for N in (8, 10, 12):
        st = structure(N)
        star, K, par4 = st["star"], st["K"], st["par4"]
        lifts, _, _, ustar = generate(N, args.extent)
        rng = np.random.default_rng(0)
        states = []
        L, U = lifts.copy(), ustar.copy()
        for s in range(args.nstates):
            if s:
                L, U, _ = apply_flips(L, U, star, K, args.gap, rng)
            P = L @ par4
            rad = np.linalg.norm(P - P.mean(0), axis=1)
            states.append((L.copy(), U.copy(), P, rad, rad.max()))

        print(f"=== {NAME[N]} ({N}-fold), n={len(lifts)} ===")
        print(f"{'R':>4} {'r':>2} {'n_reg':>6} {'corr':>12} {'V':>7} {'resid_std':>10}")
        for R in RADII:
            for r in HORIZONS:
                if (R, r) in SKIP:
                    continue
                corrs, Vs, resids = [], [], []
                for L, U, P, rad, rmax in states:
                    bulk = np.where(rad + R + args.margin < rmax)[0]
                    if len(bulk) == 0:
                        continue
                    pick = rng.choice(bulk, size=min(args.ncenters, len(bulk)),
                                      replace=False)
                    for ci in pick:
                        ra = region_arrays(L, U, star, K, par4, P[ci], R, r)
                        if ra is None:
                            continue
                        logd, logo = ra
                        Vs.append(float(logo.var()))
                        if logd.std() > 1e-9 and logo.std() > 1e-9:
                            corrs.append(float(np.corrcoef(logd, logo)[0, 1]))
                        resids.append(residual(logd, logo))
                cm = np.mean(corrs) if corrs else np.nan
                ce = (np.std(corrs, ddof=1) / np.sqrt(len(corrs))
                      if len(corrs) > 1 else np.nan)
                vm = np.mean(Vs) if Vs else np.nan
                rstd = np.std(np.concatenate(resids)) if resids else np.nan
                print(f"{R:>4.1f} {r:>2} {len(Vs):>6} "
                      f"{cm:>7.3f}±{ce:<4.2f} {vm:>7.3f} {rstd:>10.4f}", flush=True)
        print()


if __name__ == "__main__":
    main()
