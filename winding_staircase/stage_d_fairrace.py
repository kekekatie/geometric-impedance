#!/usr/bin/env python3
"""
Stage D — the fair race (matched-size). Per the changelog in
STAGE_D_IMPLEMENTATION_PREREG.md: global-sync K* is N-dependent on 2D tori, so we
(i) compare across the ladder at matched-ish N, and (ii) use the N-normalised
connectivity lambda_2 * N -- size-stable, the algebraic connectivity K* proxies --
as the primary discriminator, with matched-N Kuramoto K* as dynamical
confirmation. Standardised frequencies (prereg §2 primary).

Question: up the approximant ladder, is the (size-controlled) sync onset FLAT
(null: local wiring governs) or does it converge at the substrate's registered
shrink ratio into the silver / golden band (D-positive)?
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import eigsh
import stage_d as D

# supercell per (substrate, order_index) targeting N ~ 700-1000 where the cell allows
SC = {("ammann_beenker", 0): 10, ("ammann_beenker", 1): 4,
      ("ammann_beenker", 2): 2,  ("ammann_beenker", 3): 1,
      ("penrose", 0): 3, ("penrose", 1): 2, ("penrose", 2): 1, ("penrose", 3): 1}
N_SEEDS = 3
T_TRANS = T_AVG = 150.0


def lam2(ei, ej, N):
    w = np.ones(len(ei))
    A = coo_matrix((np.concatenate([w, w]),
                    (np.concatenate([ei, ej]), np.concatenate([ej, ei]))),
                   shape=(N, N)).tocsr()
    deg = np.asarray(A.sum(1)).ravel()
    L = diags(deg) - A
    return float(np.sort(eigsh(L, k=2, sigma=0, which="LM",
                               return_eigenvectors=False))[1])


def kstar_avg(omega, ei, ej):
    """K* from find_Kstar, whose r is already averaged over 3 random starts."""
    k, _ = D.find_Kstar(omega, ei, ej, seeds=(1, 2, 3),
                        T_trans=T_TRANS, T_avg=T_AVG)
    return (float(k), 0.0)


def geometric_ratio(vals):
    """Successive shrink ratios of the gaps to the last value (a crude read of
    whether the sequence converges geometrically and at what ratio)."""
    v = np.array(vals, float)
    gaps = np.abs(v - v[-1])[:-1]
    ratios = [gaps[i + 1] / gaps[i] for i in range(len(gaps) - 1) if gaps[i] > 1e-9]
    return ratios


def main():
    reg_ratio = {"ammann_beenker": 2**0.5 - 1, "penrose": 1 / ((1 + 5**0.5) / 2)}
    band = {"ammann_beenker": (0.352, 0.476), "penrose": (0.525, 0.711)}
    out = {"note": "matched-size fair race; lambda2*N primary, Kuramoto K* confirm",
           "registered_ratio": reg_ratio, "bands": band, "substrates": {}}
    for sub in ["ammann_beenker", "penrose"]:
        print(f"\n=== {sub} ===  registered ratio {reg_ratio[sub]:.3f}  "
              f"band {band[sub]}")
        print(f"  {'ord':>3} {'conv':>5} {'N':>5} {'lam2':>8} {'lam2*N':>8} "
              f"{'K*':>7} {'+-':>6}")
        rows = []
        for oi in range(4):
            depth, ei, ej, N = D.torus_graph(sub, oi, supercell=SC[(sub, oi)])
            om = D.frequencies(depth, standardise=True)
            L2 = lam2(ei, ej, N)
            t = time.time()
            ks, kss = kstar_avg(om, ei, ej)
            conv = D.REG[sub]["orders"][oi]["convergent"]
            rows.append(dict(order=oi + 1, convergent=conv, N=int(N),
                             lam2=L2, lam2N=L2 * N, Kstar=ks, Kstar_sd=kss,
                             seconds=round(time.time() - t, 1)))
            print(f"  {oi+1:>3} {conv:>5} {N:>5} {L2:>8.5f} {L2*N:>8.3f} "
                  f"{ks:>7.3f} {kss:>6.3f}", flush=True)
        # convergence reads (orders 2-4; order 1 is the crude 1/1 approximant)
        lam_seq = [r["lam2N"] for r in rows[1:]]
        k_seq = [r["Kstar"] for r in rows[1:]]
        out["substrates"][sub] = dict(
            rows=rows,
            lam2N_ratios=geometric_ratio(lam_seq),
            Kstar_ratios=geometric_ratio(k_seq),
            lam2N_spread_pct=100 * (max(lam_seq) - min(lam_seq)) / np.mean(lam_seq))
        print(f"  lambda2*N (ord2-4): {[round(x,2) for x in lam_seq]}  "
              f"spread {out['substrates'][sub]['lam2N_spread_pct']:.0f}%  "
              f"ratios {[round(x,2) for x in out['substrates'][sub]['lam2N_ratios']]}")
    (Path(__file__).parent / "stage_d_results.json").write_text(json.dumps(out, indent=2))
    print("\n-> stage_d_results.json")


if __name__ == "__main__":
    main()
