#!/usr/bin/env python3
"""EXPLORATORY (post hoc, after the run): D3 compared half the WIDTH of the difference along the front with the
speed of light, which ../speed_of_light/ measured as REACH from the choice point. Re-run the same worlds (deterministic)
and record, per sibling: reach = max |x| of the difference (edges along the front from the choice point) and the
decided ribbon's reach, each against slice; also how many distinct local situations (sibling size pairs) there are."""
import os, json, collections
from multiprocessing import Pool
import numpy as np
import thread_influence as T

orig = T.analyse
def analyse(sibA, sibB, chosen, line):
    smax, out = orig(sibA, sibB, chosen, line)
    m, u = line; xc = lambda z: ((z - m) * u.conjugate()).real / T.S
    for o, (X, Y, t) in zip(out, ((sibA, sibB, chosen[0]), (sibB, sibA, chosen[1]))):
        j, Rk = T.decided_ribbon(X[0], t, u); ss, rD, rR = [], [], []
        for s in range(1, smax + 1):
            Xs = [w for w, sl in X[1] if sl <= s]; Ys = [w for w, sl in Y[1] if sl <= s]
            ky = {T.D.dkey(w) for w in Ys}; kx = {T.D.dkey(w) for w in Xs}
            yo = [w for w in Ys if T.D.dkey(w) not in kx]
            dl = [w for w in Xs if T.D.dkey(w) not in ky and any(T.L.inside(T.cen(w), *v[1:]) for v in yo)]
            if dl:
                ss.append(s); rD.append(max(abs(xc(T.cen(w))) for w in dl))
                rR.append(max([abs(xc(T.cen(w))) for w in Xs if T.D.dkey(w) in Rk] or [0]))
        o["reach_delta"] = T.slope(ss, rD); o["reach_ribbon"] = T.slope(ss, rR)
    return smax, out
T.analyse = analyse

if __name__ == "__main__":
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(T.world, range(T.N_WORLDS))
    seen = set(); C = []
    for w in W:
        for c in w["choices"]:
            if c["sig"] not in seen and c["n_options"] == 2:
                seen.add(c["sig"]); C.append(c)
    ok = [c for c in C if c["smax"] >= T.MIN_SL]
    rd = [float(np.nanmean([s["reach_delta"] for s in c["sides"]])) for c in ok]
    rr = [float(np.nanmean([s["reach_ribbon"] for s in c["sides"]])) for c in ok]
    sit = len({tuple(sorted(c["sizes"])) for c in C})
    lines = [f"EXPLORATORY reach speeds over {len(ok)} distinct choices with >= {T.MIN_SL} slices "
             f"(distinct local situations, judged by sibling size pairs: about {sit})",
             f"  reach of the difference from the choice point: median {np.median(rd):.2f} edges/slice "
             f"(quartiles {np.quantile(rd, .25):.2f}-{np.quantile(rd, .75):.2f}); speed_of_light found 0.67-1.13, median 0.95",
             f"  reach of the decided ribbon: median {np.nanmedian(rr):.2f} edges/slice",
             f"  ratio difference/ribbon reach: median {np.nanmedian([a / b for a, b in zip(rd, rr) if b > 0.1]):.2f}"]
    print("\n".join(lines)); open(os.path.join(T.RES, "reach_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")
