#!/usr/bin/env python3
"""
History-recoverability under unbiased phason dynamics (the functional-residue
test). Prioritised ahead of Branch B because it needs no energy, so it cannot be
accused of finding memory in a landscape we built to contain it.

The memory claim is not "some tilings lose fewer vertices". It is: after equal
structural disturbance, does the present configuration still carry information
about how it got there? So two perturbation histories are applied to the clean
tiling at a MATCHED flip budget -

    H_A : spatially clustered flips (all inside a disk)
    H_B : spatially dispersed flips (whole patch)

- and we ask whether the final state remains distinguishable, using a readout
that is intrinsic to the present state and free of the two known leaks:

  * no clean-snapshot comparison (that would just re-read which vertices moved);
    a defect is a bulk vertex whose local type does not occur in the ideal
    vocabulary, which is a property of the substrate, not a stored snapshot;
  * no degree/label classifier; the statistic is the spatial clustering of those
    defects (mean nearest-neighbour distance vs an equal-size random draw of
    bulk vertices), which distinguishes clustered from dispersed damage without
    reading degree.

Then unbiased dynamics are allowed to run, and the A-vs-B separation is tracked
as it erases. If it vanishes at once, mobility erases history. If one family
holds it longer, the geometry carries history. If all three behave alike, the
effect is not cyclotomic-family-specific. All three outcomes are informative.
"""

import argparse
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import flippable
from phason_energy import clean_frequencies, vertex_types

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def run_flips(L, U, star, K, par4, k, rng, center=None, radius=None):
    """Apply up to k flips; if center/radius given, only sites inside that disk."""
    L, U = L.copy(), U.copy()
    done = 0
    for _ in range(k):
        sites = flippable(L, U, star, K)
        if center is not None:
            P = L @ par4
            sites = [s for s in sites
                     if np.linalg.norm(P[s[0]] - center) <= radius]
        if not sites:
            break
        i, t, u = sites[rng.integers(len(sites))]
        L[i] = np.array(t, dtype=L.dtype)
        U[i] = u
        done += 1
    return L, U, done


def defects(L, U, star, K, par4, vocab):
    """Parallel positions of bulk vertices whose type is absent from the ideal."""
    types = vertex_types(L, U, star, K, par4)
    P = L @ par4
    pts = [P[i] for i, t in enumerate(types) if len(t) >= 3 and t not in vocab]
    return np.array(pts) if pts else np.zeros((0, 2))


def clustering(defect_pts, bulk_pts, rng, reps=8):
    """Mean NN distance of defects / that of equal-size random bulk samples.
    < 1 clustered, ~ 1 as-random, > 1 over-dispersed. Robust to count and lattice."""
    if len(defect_pts) < 6:
        return np.nan
    mnn = lambda p: cKDTree(p).query(p, k=2)[0][:, 1].mean()
    base = np.mean([mnn(bulk_pts[rng.choice(len(bulk_pts), len(defect_pts),
                                            replace=False)]) for _ in range(reps)])
    return mnn(defect_pts) / base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=10)
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--damage", type=float, default=0.06, help="flips/vertex")
    args = ap.parse_args()
    RELAX = [0.0, 0.06, 0.18]                     # extra flips/vertex after damage

    print(f"History-recoverability, extent {args.extent}, {args.seeds} seeds, "
          f"damage {args.damage} flips/vtx\n")
    for N in (8, 10, 12):
        st = structure(N)
        star, K, par4 = st["star"], st["K"], st["par4"]
        lifts, _, _, ustar = generate(N, args.extent)
        n = len(lifts)
        vocab = set(clean_frequencies(vertex_types(lifts, ustar, star, K, par4)))
        Pbulk = lifts @ par4
        c = Pbulk.mean(0)
        radius = 0.34 * np.linalg.norm(Pbulk - c, axis=1).max()
        kdmg = int(round(args.damage * n))

        seps = {t: [] for t in RELAX}
        ceA = {t: [] for t in RELAX}
        ceB = {t: [] for t in RELAX}
        ndef = []
        for s in range(args.seeds):
            rng = np.random.default_rng(100 + s)
            # matched budget: clustered first, then match its accepted count
            LA, UA, kA = run_flips(lifts, ustar, star, K, par4, kdmg, rng,
                                   center=c, radius=radius)
            LB, UB, kB = run_flips(lifts, ustar, star, K, par4, kA, rng)
            ndef.append((kA, kB))
            prev = 0
            for t in RELAX:
                extra = int(round(t * n)) - prev
                prev = int(round(t * n))
                if extra > 0:
                    LA, UA, _ = run_flips(LA, UA, star, K, par4, extra, rng)
                    LB, UB, _ = run_flips(LB, UB, star, K, par4, extra, rng)
                bulkA = LA @ par4
                bulkB = LB @ par4
                a = clustering(defects(LA, UA, star, K, par4, vocab), bulkA, rng)
                b = clustering(defects(LB, UB, star, K, par4, vocab), bulkB, rng)
                ceA[t].append(a)
                ceB[t].append(b)
                seps[t].append(b - a)

        kA_m = np.mean([x[0] for x in ndef])
        print(f"{NAME[N]:>9} ({N:>2}-fold)  {n} verts   matched budget ~{kA_m:.0f} flips")
        print(f"    {'relax f/v':>10} {'CE_clustered':>13} {'CE_dispersed':>13} "
              f"{'separation':>12}")
        for t in RELAX:
            a, b = np.nanmean(ceA[t]), np.nanmean(ceB[t])
            sm = np.nanmean(seps[t])
            ss = np.nanstd(seps[t], ddof=1) if np.sum(~np.isnan(seps[t])) > 1 else np.nan
            print(f"    {t:>10.2f} {a:>13.3f} {b:>13.3f} "
                  f"{sm:>8.3f} +-{ss:.3f}")
        print()


if __name__ == "__main__":
    main()
