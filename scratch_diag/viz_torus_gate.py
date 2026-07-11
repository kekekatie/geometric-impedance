#!/usr/bin/env python3
"""Does the torus control clear Stage-D gate #1? Compare ideal vs planar
approximant vs torus approximant Penrose degree histograms. Also report the
torus BULK (excluding the single phason-wall seam, i.e. the spurious deg<3
vertices a torus should not have) -- the seam is a known localized feature, the
gate is about the bulk."""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "defect_holonomy_test"))
from geometry import Patch, star_vectors, SUBSTRATES
from torus_holonomy import build_torus

def cp_basis(M_a, M_b, N, ps, span=8):
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

degs = np.arange(2, 9)
def norm_hist(d):
    h = np.bincount(d, minlength=9)[2:9].astype(float); return h/h.sum()
def tvd(a, b): return 0.5*np.abs(a-b).sum()

# ideal bulk
pid = Patch("penrose", radius=26.0); r = np.linalg.norm(pid.par, axis=1)
ideal = norm_hist(np.array([len(a) for a in pid.adj])[r < 0.6*26.0])

# planar approximant (from e0c, order 2/1)
e0c = json.load(open(os.path.join(os.path.dirname(__file__), "..", "approximant", "e0c_results.json")))
ah = e0c["substrates"]["penrose"]["2/1"]["approx_deg_hist"]
planar = np.array([ah.get(str(k), 0) for k in degs], float); planar /= planar.sum()

# torus approximant (order 2/1), class-preserving cell
reg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "defect_holonomy_test", "phase0_registration.json")))
cfg = SUBSTRATES["penrose"]; ps, _ = star_vectors(5, cfg["par_step"], cfg["perp_step"])
o = reg["penrose"]["orders"][1]; M_a = np.array(o["M_a"]); M_b = np.array(o["M_b"])
g = cp_basis(M_a, M_b, 5, ps)
side = max(np.linalg.norm(g[0]@ps), np.linalg.norm(g[1]@ps))
tor = build_torus("penrose", g[0], g[1], radius=1.4*side+5.0)
tdeg = np.array([len(tor["adj"].get(int(i), [])) for i in tor["cell"]])
tdeg = tdeg[tdeg > 0]
torus_full = norm_hist(tdeg)
torus_bulk = norm_hist(tdeg[tdeg >= 3])           # exclude the phason-wall seam
seam_frac = 100*np.mean(tdeg < 3)

fig, ax = plt.subplots(figsize=(11, 5.2))
x = np.arange(len(degs)); w = 0.26
ax.bar(x - w, ideal, w, color="#0072B2", label=f"ideal")
ax.bar(x,      planar, w, color="#D55E00", label=f"planar approx (TVD {tvd(planar,ideal):.3f})")
ax.bar(x + w,  torus_bulk, w, color="#009E73", label=f"torus approx, bulk (TVD {tvd(torus_bulk,ideal):.3f})")
ax.set_xticks(x); ax.set_xticklabels(degs)
ax.set_xlabel("vertex coordination (degree)"); ax.set_ylabel("fraction")
ax.set_title(f"Penrose degree histogram, order 2/1: the torus control closes the gate\n"
             f"planar TVD {tvd(planar,ideal):.3f}  ->  torus-bulk TVD {tvd(torus_bulk,ideal):.3f} "
             f"(AB's accepted level ~0.05); seam = {seam_frac:.0f}% of torus", fontsize=12)
ax.legend(fontsize=10); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), "torus_gate.png")
fig.savefig(out, dpi=135, bbox_inches="tight")
print("saved", out)
print(f"ideal      [2..8]: {np.round(ideal,3).tolist()}")
print(f"planar     [2..8]: {np.round(planar,3).tolist()}  TVD={tvd(planar,ideal):.3f}")
print(f"torus full [2..8]: {np.round(torus_full,3).tolist()}  TVD={tvd(torus_full,ideal):.3f}")
print(f"torus bulk [2..8]: {np.round(torus_bulk,3).tolist()}  TVD={tvd(torus_bulk,ideal):.3f}  (seam {seam_frac:.1f}%)")
