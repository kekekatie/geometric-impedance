#!/usr/bin/env python3
"""
E0c — seamless phason-shear approximant substrate validation.

Checks, per substrate and convergent order, BEFORE the approximant is used as a
control or cut into:
  1. connectivity
  2. seamlessness: every edge an exact unit star (residual at FP floor)
  3. periodicity: interior vertices repeat under +P_a and +P_b (position-based,
     so it is not fooled by the enumeration-box edge)
  4. degree-histogram match to the ideal tiling (the B5 mandatory check)
  5. healing (theorem-echo): contractible closed loops carry zero holonomy
     (ideal positions => Theorem 1 heals; if this fails the pipeline leaks)
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reverse_loop_test"))
sys.path.insert(0, str(Path(__file__).parent.parent / "defect_holonomy_test"))
import numpy as np
from collections import Counter
from scipy.spatial import cKDTree
from phason_shear import PhasonShearApproximant
from geometry import Patch
from lift_metric import LiftMetric, positions_of_path
import walker as W

RADIUS = 14.0


def closed_loop(ap, start, steps, rng):
    path = [start]; prev = -1
    for _ in range(steps):
        nb = [v for v in ap.adj[path[-1]] if v != prev] or list(ap.adj[path[-1]])
        if not nb:
            return None
        prev = path[-1]; path.append(int(rng.choice(nb)))
    _, par = W.bfs(ap, path[-1]); back = W.reconstruct_path(par, path[-1], start)
    if back is None:
        return None
    return path + back[1:]


def periodicity_by_position(ap):
    """Fraction of interior vertices whose +P_a and +P_b images (when inside the
    patch) coincide with an existing vertex."""
    tree = cKDTree(ap.par)
    r = np.linalg.norm(ap.par, axis=1)
    Rp = 0.55 * ap.radius
    ok = tot = 0
    for i in np.where(r < Rp)[0]:
        for P in (ap.P_a, ap.P_b):
            tgt = ap.par[i] + P
            if np.linalg.norm(tgt) < ap.radius - 1.0:
                d, _ = tree.query(tgt)
                tot += 1; ok += (d < 1e-6)
    return ok / max(tot, 1)


def validate(substrate, order_index):
    ap = PhasonShearApproximant(substrate, order_index, radius=RADIUS)
    comp = ap.largest_component()
    deg = np.array([len(a) for a in ap.adj])
    rin = np.linalg.norm(ap.par, axis=1); inr = rin < 0.55 * ap.radius
    di = Patch(substrate, radius=RADIUS + 2)
    dr = np.linalg.norm(di.par, axis=1)
    ideg = np.array([len(a) for a in di.adj])[dr < 0.55 * ap.radius]
    ah = Counter(deg[inr].tolist()); ih = Counter(ideg.tolist())
    allk = sorted(set(ah) | set(ih))
    af = np.array([ah.get(k, 0) for k in allk], float)
    iff = np.array([ih.get(k, 0) for k in allk], float)
    af /= af.sum(); iff /= iff.sum()
    tvd = 0.5 * np.abs(af - iff).sum()
    # healing
    lm = LiftMetric(ap.par_star, ap.perp_star); rng = np.random.default_rng(0)
    hmax = 0.0; nl = 0
    for _ in range(400):
        st = int(rng.choice(comp))
        loop = closed_loop(ap, st, int(rng.integers(6, 14)), rng)
        if loop is None or loop[0] != loop[-1]:
            continue
        h, _, _, _ = lm.holonomy(positions_of_path(ap, loop))
        hmax = max(hmax, h); nl += 1
        if nl >= 150:
            break
    return ap, dict(
        n=ap.n, largest_comp=int(len(comp)), connected=bool(len(comp) == ap.n),
        edge_star_residual=ap.max_edge_star_residual,
        periodicity=round(periodicity_by_position(ap), 4),
        interior_mean_degree=round(float(deg[inr].mean()), 3),
        ideal_mean_degree=round(float(ideg.mean()), 3),
        degree_tvd=round(float(tvd), 4),
        approx_deg_hist={int(k): int(v) for k, v in sorted(ah.items())},
        ideal_deg_hist={int(k): int(v) for k, v in sorted(ih.items())},
        healing_max_holonomy=float(hmax), healing_loops=nl)


def main():
    out = {"radius": RADIUS, "substrates": {}}
    for sub in ["ammann_beenker", "penrose"]:
        out["substrates"][sub] = {}
        n_orders = len(json.load(open(Path(__file__).parent.parent /
                       "defect_holonomy_test" / "phase0_registration.json")
                       )[sub]["orders"])
        for oi in range(min(4, n_orders)):
            ap, res = validate(sub, oi)
            out["substrates"][sub][ap.convergent] = res
            passed = (res["connected"] and res["edge_star_residual"] < 1e-10
                      and res["periodicity"] > 0.999
                      and res["healing_max_holonomy"] < 1e-9)
            print(f"{sub[:4]} ord{ap.order} ({ap.convergent}): n={res['n']:5d} "
                  f"conn={res['connected']} seam={res['edge_star_residual']:.0e} "
                  f"period={res['periodicity']*100:.1f}% "
                  f"degTVD={res['degree_tvd']:.3f} "
                  f"heal={res['healing_max_holonomy']:.0e}  "
                  f"[{'E0c PASS' if passed else 'CHECK degree/other'}]")
    json.dump(out, open(Path(__file__).parent / "e0c_results.json", "w"), indent=2)
    print("-> e0c_results.json")


if __name__ == "__main__":
    main()
