# GEOMETRY-ONLY padding-convergence check: does Voronoi Delta=4 == Delta=6 for core cells?
# Compares per-core-vertex cell AREA and PERIMETER (not just boundedness). No dynamics/address/targets.
import sys
import numpy as np
from scipy.spatial import Voronoi, cKDTree
sys.path.insert(0, "substrates")
from generate_rank4 import generate, build_edges

def patch(N, extent, off):
    lifts, par, perp, ustar = generate(N, extent, offset=np.array(off))
    return par

def cell_area_perim(par):
    """Return dict i-> (area, perim) for bounded Voronoi cells."""
    vor = Voronoi(par)
    out = {}
    for i in range(len(par)):
        reg = vor.regions[vor.point_region[i]]
        if len(reg) == 0 or -1 in reg:
            continue
        V = vor.vertices[reg]
        c = V.mean(0)
        ang = np.arctan2(V[:,1]-c[1], V[:,0]-c[0])
        order = np.argsort(ang)
        P = V[order]
        x, y = P[:,0], P[:,1]
        area = 0.5*abs(np.dot(x, np.roll(y,-1)) - np.dot(y, np.roll(x,-1)))
        perim = np.sum(np.linalg.norm(P - np.roll(P,-1,axis=0), axis=1))
        out[i] = (area, perim)
    return out

CASES = [(8,14,"silver"), (10,18,"golden"), (12,18,"platinum")]
OFFS = [(0.13,0.37),(0.29,0.11)]
print("# padding-convergence: Voronoi cells Delta=4 (core+4) vs Delta=6 (core+6)")
print("# metric: matched CORE vertices bounded in BOTH; max abs & rel diff of area & perimeter")
worst_area_rel = 0.0; worst_perim_rel = 0.0
for N, ext, name in CASES:
    for off in OFFS:
        core = patch(N, ext, off)
        p4 = patch(N, ext+4, off)
        p6 = patch(N, ext+6, off)
        ca4 = cell_area_perim(p4); ca6 = cell_area_perim(p6)
        # match core vertices into each pad by position
        t4 = cKDTree(p4); t6 = cKDTree(p6)
        d4,i4 = t4.query(core, k=1); d6,i6 = t6.query(core, k=1)
        ell = 1.0
        da=[]; dp=[]; ra=[]; rp=[]; nboth=0
        for c in range(len(core)):
            if d4[c] < 1e-6 and d6[c] < 1e-6 and i4[c] in ca4 and i6[c] in ca6:
                a4,pr4 = ca4[i4[c]]; a6,pr6 = ca6[i6[c]]
                nboth += 1
                da.append(abs(a4-a6)); dp.append(abs(pr4-pr6))
                ra.append(abs(a4-a6)/max(a6,1e-12)); rp.append(abs(pr4-pr6)/max(pr6,1e-12))
        mad=max(da) if da else 0; mdp=max(dp) if dp else 0
        mra=max(ra) if ra else 0; mrp=max(rp) if rp else 0
        worst_area_rel=max(worst_area_rel,mra); worst_perim_rel=max(worst_perim_rel,mrp)
        print(f"{name:9s} e{ext} off{off}: core bounded-in-both={nboth:5d} | "
              f"max|dArea|={mad:.2e} (rel {mra:.2e}) | max|dPerim|={mdp:.2e} (rel {mrp:.2e})")
print(f"\nWORST-CASE across all cases: rel area diff = {worst_area_rel:.2e}, "
      f"rel perim diff = {worst_perim_rel:.2e}")
print("DONE_CONVERGE")
