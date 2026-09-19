#!/usr/bin/env python3
"""
Defect-Holonomy v3 -- E4 (torus crown jewel) + E2 (price list).

The clean venue for rigid-edge holonomy is the approximant TORUS, for the reason
the ideal-lattice theorem (verify_holonomy_theorem.py) makes precise: a
contractible loop is physically closed (pi_par(m)=0) so it heals; a
NON-contractible loop is NOT physically closed on the plane (pi_par(m)=P_a != 0),
so the theorem's hypothesis does not bind, its net lift is a period vector
m in <M_a, M_b>, and its holonomy is the IDEAL perp of that lift -- the registered
Phase-0 quantum.

Construction (no surgery needed -- zero-surgery crown jewel):
  * take ideal quasicrystal vertices whose physical position lies in one
    approximant unit cell (spanned by P_a=pi_par(M_a), P_b=pi_par(M_b));
  * wrap edges across the cell boundary by nearest-vertex matching (the seam
    mismatch is the frozen phason wall -- an approximant is imperfect by
    construction);
  * edge type = ideal star (classified against the substrate's own stars, FP
    floor); perp increment = IDEAL perp_star (the split convention).
Holonomy of any closed torus loop = pi_perp(net lift), quantised on pi_perp(S).
"""

import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reverse_loop_test"))
import numpy as np
import collections
from scipy.spatial import cKDTree
from geometry import Patch, star_vectors, SUBSTRATES

HERE = Path(__file__).parent


def build_torus(substrate, M_a, M_b, radius=11.0, wrap_tol=0.25):
    cfg = SUBSTRATES[substrate]
    par_star, perp_star = star_vectors(cfg["N"], cfg["par_step"], cfg["perp_step"])
    N = cfg["N"]
    P_a, P_b = M_a @ par_star, M_b @ par_star
    Mcell = np.array([P_a, P_b]).T
    Minv = np.linalg.inv(Mcell)
    pt = Patch(substrate, radius=radius)
    K, par = pt.K, pt.par
    frac = (Minv @ par.T).T
    incell = np.all((frac >= -1e-9) & (frac < 1 - 1e-9), axis=1)
    cell = np.where(incell)[0]
    tree = cKDTree(par[cell])
    lift_of = {tuple(K[i]): i for i in range(pt.n)}
    eye = np.eye(N, dtype=int)
    adj = {}
    seam = 0
    max_seam_res = 0.0
    for i in cell:
        for j in range(N):
            for s in (1, -1):
                gi = lift_of.get(tuple(K[i] + s * eye[j]))
                if gi is None:
                    continue
                fp = Minv @ par[gi]
                shift = Mcell @ np.floor(fp + 1e-9)
                wrapped = par[gi] - shift
                d, idx = tree.query(wrapped)
                if d > wrap_tol:
                    continue
                if np.any(np.abs(np.floor(fp + 1e-9)) > 0):
                    seam += 1
                    max_seam_res = max(max_seam_res, d)
                # perp increment = IDEAL perp star of type j (split convention)
                adj.setdefault(i, []).append((cell[idx], s * perp_star[j]))
    return dict(cell=cell, adj=adj, par_star=par_star, perp_star=perp_star,
                seam_edges=seam, max_seam_res=float(max_seam_res),
                q_a=M_a @ perp_star, q_b=M_b @ perp_star)


def fundamental_holonomies(tor):
    """Holonomies of all fundamental cycles (BFS tree + non-tree edges)."""
    adj = tor["adj"]
    cell = tor["cell"]
    root = int(cell[0])
    acc = {root: np.zeros(2)}
    order = [root]
    dq = collections.deque([root])
    while dq:
        u = dq.popleft()
        for v, dp in adj.get(u, []):
            if v not in acc:
                acc[v] = acc[u] + dp
                order.append(v)
                dq.append(v)
    holos = []
    seen = set()
    for u in order:
        for v, dp in adj.get(u, []):
            key = tuple(sorted((u, v)))
            if key in seen:
                continue
            seen.add(key)
            if v in acc:
                h = acc[u] + dp - acc[v]
                if np.linalg.norm(h) > 1e-6:
                    holos.append(np.linalg.norm(h))
    return np.array(holos)


def run():
    reg = json.load(open(HERE / "phase0_registration.json"))
    results = {"note": "E4 torus quantisation + E2 price-list scaling vs "
                       "Phase-0 registered quanta. All numbers predicted before "
                       "construction.", "substrates": {}}
    for sub in ["ammann_beenker", "penrose"]:
        orders = reg[sub]["orders"]
        reg_ratio = reg[sub]["asymptotic_shrink_ratio_derived"]
        rows = []
        prev = None
        cfg = SUBSTRATES[sub]
        pstar, _ = star_vectors(cfg["N"], cfg["par_step"], cfg["perp_step"])
        for o in orders[:4]:
            M_a = np.array(o["M_a"]); M_b = np.array(o["M_b"])
            registered = o["quantum_norm_a"]
            # size the patch so the approximant unit cell fits
            side = max(np.linalg.norm(M_a @ pstar), np.linalg.norm(M_b @ pstar))
            radius = max(11.0, 1.7 * side + 4.0)
            tor = build_torus(sub, M_a, M_b, radius=radius)
            holos = fundamental_holonomies(tor)
            if len(holos) == 0:
                continue
            measured = float(np.min(holos))          # the fundamental quantum
            hit = abs(measured - registered) < 0.02 * max(registered, 0.05)
            ratio = (measured / prev) if prev else None
            rows.append(dict(order=o["order"], convergent=o["convergent"],
                             cell_vertices=int(len(tor["cell"])),
                             seam_edges=tor["seam_edges"],
                             registered_quantum=round(registered, 6),
                             measured_quantum=round(measured, 6),
                             hits_registered=bool(hit),
                             measured_ratio_vs_prev=(round(ratio, 5) if ratio else None)))
            prev = measured
        all_hit = all(r["hits_registered"] for r in rows)
        results["substrates"][sub] = dict(
            registered_shrink_ratio=round(reg_ratio, 5),
            all_orders_hit_registered=bool(all_hit), price_list=rows)
        print(f"\n=== {sub} ===  registered shrink ratio {reg_ratio:.5f}")
        print("  order  conv   cell  registered  measured   hit   ratio")
        for r in rows:
            print(f"    {r['order']}    {r['convergent']:>5} {r['cell_vertices']:4d}   "
                  f"{r['registered_quantum']:.6f}  {r['measured_quantum']:.6f}  "
                  f"{str(r['hits_registered']):>5}  "
                  f"{('%.5f'%r['measured_ratio_vs_prev']) if r['measured_ratio_vs_prev'] else '  -- '}")
        print(f"  ALL ORDERS HIT REGISTERED QUANTA: {all_hit}")
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "v3_torus_pricelist.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\n-> results/v3_torus_pricelist.json")
    return results


if __name__ == "__main__":
    run()
