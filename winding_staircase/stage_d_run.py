#!/usr/bin/env python3
"""Stage D — PRIMARY run: K*(order) up the approximant ladder, both substrates,
standardised natural frequencies (prereg §2 primary), 3-seed averaged, torus
throughout. Saves incrementally. Convergence analysis (flat vs banded) at the end.

Supercell per (substrate, order) chosen so every rung has enough oscillators
(N >~ 250, capped ~1900); K* is size-independent (canary F), so this is safe and
keeps compute bounded. Orders are the convergents k=1..4 (indices 0..3)."""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import stage_d as D

SC = {("ammann_beenker", 0): 6, ("ammann_beenker", 1): 3,
      ("ammann_beenker", 2): 2, ("ammann_beenker", 3): 1,
      ("penrose", 0): 2, ("penrose", 1): 1, ("penrose", 2): 1, ("penrose", 3): 1}
RATIO = {"ammann_beenker": 2**0.5 - 1.0, "penrose": 1.0 / ((1 + 5**0.5) / 2)}
BAND = {"ammann_beenker": (0.352, 0.476), "penrose": (0.525, 0.711)}
OUT = Path(__file__).parent / "stage_d_primary_results.json"


def main():
    results = {"run": "primary (standardised freqs)", "seeds": [1, 2, 3],
               "r_c": 0.5, "supercells": {f"{s}:{o}": SC[(s, o)] for s, o in SC},
               "substrates": {}}
    for sub in ["ammann_beenker", "penrose"]:
        conv = D.REG[sub]["orders"]
        rows = []
        for oi in range(4):
            sc = SC[(sub, oi)]
            depth, ei, ej, N = D.torus_graph(sub, oi, supercell=sc)
            om = D.frequencies(depth, standardise=True)
            t = time.time()
            Kstar, coarse = D.find_Kstar(om, ei, ej, seeds=(1, 2, 3),
                                         T_trans=200, T_avg=200)
            dt = time.time() - t
            rows.append(dict(order=conv[oi]["order"], convergent=conv[oi]["convergent"],
                             supercell=sc, N=int(N), edges=int(len(ei)),
                             Kstar=round(float(Kstar), 4)))
            print(f"{sub[:4]} ord{conv[oi]['order']} ({conv[oi]['convergent']:>5}) "
                  f"sc{sc} N={N:5d}: K*={Kstar:.4f}   ({dt:.0f}s)", flush=True)
            results["substrates"][sub] = rows
            json.dump(results, open(OUT, "w"), indent=2)      # incremental save
        # simple convergence read: successive K* differences and rough ratio
        Ks = np.array([r["Kstar"] for r in rows], float)
        diffs = np.diff(Ks)
        spread = float(Ks.max() - Ks.min())
        ratios = (diffs[1:] / diffs[:-1]).tolist() if np.all(np.abs(diffs[:-1]) > 1e-9) else None
        results["substrates"][sub] = {"ladder": rows, "Kstar_spread": round(spread, 4),
                                      "successive_diffs": [round(d, 4) for d in diffs],
                                      "successive_ratios": ratios,
                                      "registered_ratio": round(RATIO[sub], 4),
                                      "band": BAND[sub]}
        json.dump(results, open(OUT, "w"), indent=2)
        print(f"  -> {sub}: K* spread across ladder = {spread:.4f}; "
              f"registered ratio {RATIO[sub]:.4f}, band {BAND[sub]}\n")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
