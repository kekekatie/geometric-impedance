#!/usr/bin/env python3
"""
EXPLORATORY (not confirmatory) — a first look at a wave on the substrate.

This is pilot play for the transport-hierarchy pre-reg (PREREG_transport_hierarchy.md,
still DRAFT). It is NOT the sealed metric: no nested-increment / M4-over-M3 regression
is run here, and nothing here scores a hypothesis. Its only jobs are to (a) see whether
a coherent wave does anything visibly structured on these tilings, and (b) calibrate the
two knobs Fable's knives 4-5 say must be fixed *before* sealing: the energy window for
LDOS, and the incoherent (random-walk) timescale. Findings here feed the pre-reg
revision; the confirmatory run happens only after sealing.

The law (fixed in advance, address NEVER inserted): tight-binding, H = adjacency of the
tiling graph (uniform hopping on tile edges). We look at the density of states, the
inverse participation ratio IPR(E) = sum |psi|^4 (localization vs energy), and a couple
of eigenstates. The incoherent null (random walk) mixing time is estimated from the
graph Laplacian spectral gap.
"""

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, generate, structure

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def adjacency(lifts, N, ustar):
    E = build_edges(lifts, N, ustar)
    n = len(lifts)
    A = np.zeros((n, n))
    for i, j in E:
        A[i, j] = A[j, i] = 1.0
    return A, E


def analyse(N, extent=12):
    st = structure(N)
    lifts, par, perp, ustar = generate(N, extent)
    A, E = adjacency(lifts, N, ustar)
    n = len(lifts)
    deg = A.sum(1)

    # coherent: tight-binding spectrum + states
    evals, evecs = np.linalg.eigh(A)
    ipr = (evecs**4).sum(0)                    # per-state inverse participation ratio
    # participation ratio (effective # of sites) = 1/IPR; small -> localized
    pr = 1.0 / ipr

    # incoherent null: random-walk Laplacian spectral gap -> mixing time
    Dinv = np.diag(1.0 / deg)
    Lrw = np.eye(n) - Dinv @ A                 # random-walk Laplacian
    lw = np.sort(np.linalg.eigvals(Lrw).real)
    gap = lw[1]                                 # algebraic connectivity (RW)
    tmix = 1.0 / gap if gap > 1e-9 else np.inf

    # bulk mask (drop boundary) for later per-vertex work
    R = np.hypot(par[:, 0], par[:, 1])
    bulk = R < 0.8 * R.max()

    return dict(N=N, n=n, par=par, evals=evals, evecs=evecs, pr=pr, ipr=ipr,
                deg=deg, tmix=tmix, gap=gap, bulk=bulk, meandeg=deg.mean())


def report(res):
    N, evals, pr = res["N"], res["evals"], res["pr"]
    n = res["n"]
    band = (evals.min(), evals.max())
    # density: coarse histogram of the spectrum
    hist, edges = np.histogram(evals, bins=24)
    # where are the most localized / most extended states?
    order = np.argsort(pr)
    loc_E = evals[order[:5]]
    ext_E = evals[order[-5:]]
    # spectral gaps: largest empty stretches
    d = np.diff(np.sort(evals))
    gi = np.argsort(d)[-4:]
    gaps = sorted([(round(np.sort(evals)[i], 3), round(np.sort(evals)[i+1], 3),
                    round(d[i], 3)) for i in gi], key=lambda t: -t[2])

    print(f"\n{'='*66}\n{NAME[N]} (N={N})  {n} sites  mean deg {res['meandeg']:.3f}")
    print(f"{'='*66}")
    print(f"  spectrum band: [{band[0]:.3f}, {band[1]:.3f}]")
    print(f"  participation ratio (eff. sites): min {pr.min():.1f}  "
          f"median {np.median(pr):.1f}  max {pr.max():.1f}  (of {n})")
    print(f"  most-localized states near E = {np.round(np.sort(loc_E),2).tolist()}")
    print(f"  most-extended  states near E = {np.round(np.sort(ext_E),2).tolist()}")
    print(f"  widest spectral gaps (E1,E2,width): {gaps}")
    print(f"  random-walk mixing time ~ 1/gap = {res['tmix']:.1f} steps "
          f"(RW gap {res['gap']:.4f})")
    # fraction of states that are strongly localized (pr < 5% of n)
    floc = (pr < 0.05 * n).mean()
    print(f"  fraction strongly localized (PR < 5% of sites): {floc:.2%}")


def main():
    results = {}
    for N in (8, 10, 12):
        res = analyse(N, extent=12)
        report(res)
        results[N] = res
    # cross-family one-liners for calibration
    print(f"\n{'-'*66}\ncalibration notes (for the pre-reg knives):")
    for N in (8, 10, 12):
        r = results[N]
        E0 = r["evals"]
        # candidate LDOS window: central band around E=0 where DOS is high
        lo, hi = np.percentile(E0, [40, 60])
        print(f"  {NAME[N]:>9}: central 20% energy window ~ [{lo:.2f},{hi:.2f}]  "
              f"RW mixing ~ {r['tmix']:.0f} steps")
    return results


if __name__ == "__main__":
    main()
