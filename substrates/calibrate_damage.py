#!/usr/bin/env python3
"""Is a fixed disorder amplitude the same amount of damage at every perp dim?

The jitter is isotropic in perpendicular space, whose dimension is the variable
under test, so nominal amplitude may not be comparable across n. Measures the
fraction of vertices flipped, which is damage in substrate terms.
"""
import numpy as np, generate_nfold as GN
EXT = {4: 18, 5: 15, 6: 12}
out = open("calibration_results.txt", "w", buffering=1)
def say(s): print(s, flush=True); out.write(s + "\n")

say(f"{'disorder':>9} {'perp 2':>9} {'perp 3':>9} {'perp 4':>9}   (fraction of vertices flipped)")
base = {n: {tuple(r) for r in GN.generate(n, EXT[n], disorder=0.0)[0]} for n in (4, 5, 6)}
for a in (0.05, 0.10, 0.20, 0.30):
    row = []
    for n in (4, 5, 6):
        V = {tuple(r) for r in GN.generate(n, EXT[n], disorder=a, seed=0)[0]}
        row.append(len(base[n] ^ V) / len(base[n] | V))
    say(f"{a:9.2f} " + " ".join(f"{x:9.4f}" for x in row))
out.close()
