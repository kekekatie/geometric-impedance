#!/usr/bin/env python3
"""
Local-region branch asymmetry (sealed intrinsic-drift test, method (a)).

The whole-patch r=2 pilot found continuation volume was just degree (corr ~1.0):
too shallow. This restricts flips to a local disk and pushes the horizon deeper,
where the r=4 probe already showed volume-per-degree separating by family. For
sampled (state, focal-region) pairs it measures, over the local moves A_R(x):

  - Omega_r^R(y): local continuation volume after each move (disk BFS to depth r);
  - branch dispersion V_r = Var_y log Omega_r(y), contrast C_r, drift Delta S_r;
  - corr(log d_R(y), log Omega_r(y)): does deeper local volume DECOUPLE from local
    degree (the headline rung-3 question) or is it still just degree?

Reported with local mobility d_R so the family comparison can be read against
degree. Controls (matched-scramble, degree-matched, label-shuffle) are the next
increment; this establishes whether the deeper local estimator carries any
signal beyond degree at all.
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import apply_flips
from continuation_volume import flippable_local, omega_local, one_step_local

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def region_branch(lifts, ustar, star, K, par4, center, radius, r):
    moves = one_step_local(lifts, ustar, star, K, par4, center, radius)
    dR = len(moves)
    if dR < 3:
        return None
    oR_x = omega_local(lifts, ustar, star, K, par4, center, radius, r)
    logo, logd = [], []
    for L, U in moves:
        logo.append(np.log(max(omega_local(L, U, star, K, par4, center, radius, r), 1)))
        logd.append(np.log(max(len(flippable_local(L, U, star, K, par4, center, radius)), 1)))
    logo, logd = np.array(logo), np.array(logd)
    corr = (float(np.corrcoef(logd, logo)[0, 1])
            if logd.std() > 1e-9 and logo.std() > 1e-9 else np.nan)
    return dict(dR=dR, V=float(logo.var()), C=float(logo.max() - logo.min()),
                dS=float(logo.mean() - np.log(max(oR_x, 1))), corr=corr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=6)
    ap.add_argument("--radius", type=float, default=2.5)
    ap.add_argument("--r", type=int, default=3)
    ap.add_argument("--nstates", type=int, default=3)
    ap.add_argument("--gap", type=int, default=6)
    ap.add_argument("--ncenters", type=int, default=5)
    args = ap.parse_args()

    print(f"Local branch asymmetry: extent {args.extent}, radius {args.radius}, "
          f"horizon r={args.r}, {args.nstates} states x {args.ncenters} regions\n")
    print(f"{'':>9} {'d_R':>5} {'V_r':>7} {'C_r':>6} {'dS_r':>7} "
          f"{'corr(d,O)':>10}  (r={args.r})")
    for N in (8, 10, 12):
        st = structure(N)
        star, K, par4 = st["star"], st["K"], st["par4"]
        lifts, _, _, ustar = generate(N, args.extent)
        rng = np.random.default_rng(0)
        L, U = lifts.copy(), ustar.copy()
        rows = []
        for s in range(args.nstates):
            if s:
                L, U, _ = apply_flips(L, U, star, K, args.gap, rng)
            P = L @ par4
            ctr = P.mean(0)
            rad_pool = np.linalg.norm(P - ctr, axis=1)
            cand = np.where(rad_pool < 0.55 * rad_pool.max())[0]   # bulk centers
            for ci in rng.choice(cand, size=min(args.ncenters, len(cand)),
                                 replace=False):
                res = region_branch(L, U, star, K, par4, P[ci], args.radius, args.r)
                if res:
                    rows.append(res)
        agg = {k: np.nanmean([r[k] for r in rows]) for k in rows[0]}
        print(f"{NAME[N]:>9} {agg['dR']:>5.1f} {agg['V']:>7.3f} {agg['C']:>6.2f} "
              f"{agg['dS']:>7.3f} {agg['corr']:>10.3f}")


if __name__ == "__main__":
    main()
