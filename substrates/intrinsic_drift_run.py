#!/usr/bin/env python3
"""
Primary experiment of the sealed intrinsic-drift test: branch asymmetry of
continuation volume (PREREG_intrinsic_drift.md, rungs 1-3).

For sampled states x, over the immediate legal moves A(x):
  - Omega_1(y) = d(y): the mobility of each neighbour (cheap);
  - Omega_2(y): distinct states within 2 flips of y (bounded BFS);
and the branch quantities
  - Delta S_r = mean_y log Omega_r(y) - log Omega_r(x)   (mean volume drift)
  - V_r       = Var_y log Omega_r(y)                      (branch dispersion)
  - C_r       = max_y - min_y log Omega_r(y)              (branch contrast)
The "tip" needs V_r / C_r above the degree null: continuation-volume asymmetry
beyond what the spread of immediate mobilities {d(y)} already forces. So V_2 is
read against V_1, and the correlation of log Omega_2(y) with log d(y) is reported
(how much of Omega_2 is just degree).

PILOT scale: tiny patches (r=2 BFS blows up fast), so this is boundary-dominated
and horizon-local -- machinery and first signal, not a result. Controls
(matched scramble, degree-matched, label-shuffle) are the next increment.
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import apply_flips, flippable
from continuation_volume import omega_r, one_step

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def branch_stats(lifts, ustar, star, K, r2=True):
    moves = one_step(lifts, ustar, star, K)
    d_x = len(moves)
    if d_x < 3:
        return None
    logd_y = np.array([np.log(max(len(flippable(L, U, star, K)), 1))
                       for L, U in moves])
    row = dict(d=d_x,
               dS1=float(logd_y.mean() - np.log(d_x)),
               V1=float(logd_y.var()),
               C1=float(logd_y.max() - logd_y.min()))
    if r2:
        o2x = omega_r(lifts, ustar, star, K, 2)
        logo2_y = np.array([np.log(max(omega_r(L, U, star, K, 2), 1))
                            for L, U in moves])
        corr = (float(np.corrcoef(logd_y, logo2_y)[0, 1])
                if logd_y.std() > 1e-9 and logo2_y.std() > 1e-9 else np.nan)
        row.update(dS2=float(logo2_y.mean() - np.log(max(o2x, 1))),
                   V2=float(logo2_y.var()),
                   C2=float(logo2_y.max() - logo2_y.min()),
                   corr=corr)
    return row


def sample_states(N, extent, nstates, gap, seed):
    st = structure(N)
    star, K = st["star"], st["K"]
    lifts, _, _, ustar = generate(N, extent)
    rng = np.random.default_rng(seed)
    L, U = lifts.copy(), ustar.copy()
    yield L.copy(), U.copy()
    for _ in range(nstates - 1):
        L, U, _ = apply_flips(L, U, star, K, gap, rng)
        yield L.copy(), U.copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=3)
    ap.add_argument("--nstates", type=int, default=8)
    ap.add_argument("--gap", type=int, default=4)
    ap.add_argument("--no-r2", action="store_true")
    args = ap.parse_args()
    r2 = not args.no_r2

    print(f"Branch asymmetry (PILOT), extent {args.extent}, {args.nstates} states, "
          f"gap {args.gap}, r2={r2}\n")
    hdr = f"{'':>9} {'verts':>6} {'d(x)':>6} {'dS1':>7} {'V1':>6} {'C1':>6}"
    if r2:
        hdr += f" {'dS2':>7} {'V2':>6} {'C2':>6} {'corr(d,O2)':>11}"
    print(hdr)
    for N in (8, 10, 12):
        st = structure(N)
        star, K = st["star"], st["K"]
        rows = []
        nverts = None
        for L, U in sample_states(N, args.extent, args.nstates, args.gap, 0):
            nverts = len(L)
            s = branch_stats(L, U, star, K, r2=r2)
            if s:
                rows.append(s)
        agg = {k: np.nanmean([r[k] for r in rows]) for k in rows[0]}
        line = (f"{NAME[N]:>9} {nverts:>6} {agg['d']:>6.0f} {agg['dS1']:>7.3f} "
                f"{agg['V1']:>6.3f} {agg['C1']:>6.2f}")
        if r2:
            line += (f" {agg['dS2']:>7.3f} {agg['V2']:>6.3f} {agg['C2']:>6.2f} "
                     f"{agg['corr']:>11.3f}")
        print(line)


if __name__ == "__main__":
    main()
