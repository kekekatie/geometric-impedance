#!/usr/bin/env python3
"""Stage-D gate #1 across the FULL k=1..4 ladder, both substrates, on the torus.
For each order: build the torus control (Penrose wrapped by the class-preserving
5x cell; AB by its naive cell -- single window, any period valid), measure the
bulk (seam-excluded) degree histogram vs the ideal, report TVD. A valid control
sequence needs small, non-growing bulk TVD across all orders."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "defect_holonomy_test"))
from geometry import Patch, star_vectors, SUBSTRATES
from torus_holonomy import build_torus

def cp_basis(M_a, M_b, N, ps, span=10):
    sa, sb = int(M_a.sum()) % N, int(M_b.sum()) % N
    c = []
    for a in range(-span, span+1):
        for b in range(-span, span+1):
            if a == 0 and b == 0: continue
            if (a*sa+b*sb) % N == 0:
                m = a*M_a+b*M_b; c.append((float(np.linalg.norm(m@ps)), a, b, m))
    c.sort(key=lambda t: t[0]); a0=b0=None; bas=[]
    for _, a, b, m in c:
        if not bas: a0,b0=a,b; bas.append(m)
        elif a0*b-b0*a != 0: bas.append(m); break
    return bas

def norm_hist(d):
    h = np.bincount(d, minlength=9)[2:9].astype(float)
    return h/h.sum() if h.sum() else h

def tvd(a, b): return 0.5*np.abs(a-b).sum()

def ideal_bulk(substrate):
    p = Patch(substrate, radius=26.0); r = np.linalg.norm(p.par, axis=1)
    return norm_hist(np.array([len(a) for a in p.adj])[r < 0.6*26.0])

reg = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                     "defect_holonomy_test", "phase0_registration.json")))
RADIUS_CAP = 85.0
results = {}
for sub in ["ammann_beenker", "penrose"]:
    cfg = SUBSTRATES[sub]; N = cfg["N"]
    ps, _ = star_vectors(N, cfg["par_step"], cfg["perp_step"])
    ideal = ideal_bulk(sub)
    print(f"\n=== {sub} ===   ideal bulk [2..8]={np.round(ideal,3).tolist()}")
    rows = []
    for o in reg[sub]["orders"][:4]:
        M_a = np.array(o["M_a"]); M_b = np.array(o["M_b"])
        if sub == "penrose":
            g = cp_basis(M_a, M_b, N, ps)
        else:
            g = [M_a, M_b]                      # single window -> naive cell valid
        side = max(np.linalg.norm(g[0] @ ps), np.linalg.norm(g[1] @ ps))
        radius = 1.35*side + 5.0
        if radius > RADIUS_CAP:
            print(f"  order {o['order']} ({o['convergent']:>5}): SKIP (cell needs "
                  f"radius {radius:.0f} > cap {RADIUS_CAP:.0f})")
            rows.append((o['order'], o['convergent'], None, None, None))
            continue
        tor = build_torus(sub, g[0], g[1], radius=radius)
        tdeg = np.array([len(tor["adj"].get(int(i), [])) for i in tor["cell"]])
        tdeg = tdeg[tdeg > 0]
        full = tvd(norm_hist(tdeg), ideal)
        bulk = tvd(norm_hist(tdeg[tdeg >= 3]), ideal)
        seam = 100*np.mean(tdeg < 3)
        rows.append((o['order'], o['convergent'], bulk, full, seam))
        print(f"  order {o['order']} ({o['convergent']:>5}): cell={len(tor['cell']):5d} "
              f"maxdeg={tdeg.max()} bulk_TVD={bulk:.3f} full_TVD={full:.3f} seam={seam:.1f}%")
    results[sub] = rows

json.dump(results, open(os.path.join(os.path.dirname(__file__),
          "torus_sequence_results.json"), "w"), indent=2)
print("\n-> torus_sequence_results.json")
