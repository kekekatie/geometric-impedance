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
from geometry import Patch, window_depth
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
    """LEGACY check (kept for diffing). Fraction of interior vertices whose +P_a
    and +P_b images (when inside the patch) coincide with an existing vertex.

    This is only correct when the naive convergent cell {P_a, P_b} is a true
    period. For Penrose it is NOT: P_a, P_b shift the residue class, so they map
    a point to a differently-windowed (or nonexistent) class and this check
    under-reports (~40-60%). Use periodicity_by_acceptance instead."""
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


def _acceptance_fn(ap):
    """Acceptance predicate of the approximant as a function of the lift alone
    (residue class picks the window; sheared perp must lie inside it). Exact and
    patch-size-independent -- unlike the position check it does not need K+g to
    fall inside the enumerated patch, so arbitrarily long periods are testable."""
    wins = ap._windows(ap.radius)
    N = ap.N
    # single-window substrates (AB) apply one window to every class -- matching
    # PhasonShearApproximant._build, which sets rc=0 for non-Penrose.
    single = next(iter(wins.values())) if len(wins) == 1 else None

    def accepted(K):
        if single is not None:
            nrm, off = single
        else:
            w = wins.get(int(K.sum()) % N)
            if w is None:
                return False
            nrm, off = w
        perp_sh = K @ ap.perp_star - ap.A @ (K @ ap.par_star)
        return bool(window_depth(perp_sh[None, :], nrm, off)[0] > 0)

    return accepted, wins


def _class_preserving_basis(M_a, M_b, N, par_star, span=8):
    """Two shortest independent integer combos a*M_a + b*M_b whose residue-class
    shift sum() vanishes mod N -- i.e. generators of the true period sublattice
    for a per-class-windowed tiling. For Penrose this cell has index 5 (area x5)
    over the naive {M_a, M_b}: you must translate 5x as far to bring every vertex
    home to its own class."""
    sa, sb = int(M_a.sum()) % N, int(M_b.sum()) % N
    cands = []
    for a in range(-span, span + 1):
        for b in range(-span, span + 1):
            if a == 0 and b == 0:
                continue
            if (a * sa + b * sb) % N == 0:
                m = a * M_a + b * M_b
                cands.append((float(np.linalg.norm(m @ par_star)), a, b, m))
    cands.sort(key=lambda t: t[0])
    a0 = b0 = None
    basis = []
    for _, a, b, m in cands:
        if not basis:
            a0, b0, = a, b
            basis.append(m)
        elif a0 * b - b0 * a != 0:          # linearly independent of the first
            basis.append(m)
            break
    return basis


def periodicity_by_acceptance(ap):
    """Fraction of accepted vertices K for which K + g is also accepted, for each
    generator g of the TRUE period cell. Per-class-windowed substrates (Penrose)
    use the class-preserving sublattice; a single-window substrate (AB) uses the
    naive {M_a, M_b}. Returns (min fraction over generators, cell_index)."""
    accepted, wins = _acceptance_fn(ap)
    def _cross2(u, v):
        return float(u[0] * v[1] - u[1] * v[0])
    if len(wins) > 1:
        gens = _class_preserving_basis(ap.M_a, ap.M_b, ap.N, ap.par_star)
        # index of the class-preserving sublattice over the naive cell
        naive_area = abs(_cross2(ap.M_a @ ap.par_star, ap.M_b @ ap.par_star))
        cp_area = abs(_cross2(gens[0] @ ap.par_star, gens[1] @ ap.par_star))
        cell_index = int(round(cp_area / naive_area)) if naive_area else 1
    else:
        gens = [ap.M_a, ap.M_b]
        cell_index = 1
    fracs = [sum(accepted(K + g) for K in ap.K) / max(ap.n, 1) for g in gens]
    return (min(fracs) if fracs else 0.0), cell_index


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
    period_acc, cell_index = periodicity_by_acceptance(ap)
    return ap, dict(
        n=ap.n, largest_comp=int(len(comp)), connected=bool(len(comp) == ap.n),
        edge_star_residual=ap.max_edge_star_residual,
        periodicity=round(period_acc, 4),
        periodicity_naive=round(periodicity_by_position(ap), 4),
        period_cell_index=cell_index,
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
                  f"(naive {res['periodicity_naive']*100:.0f}%, cell x{res['period_cell_index']}) "
                  f"degTVD={res['degree_tvd']:.3f} "
                  f"heal={res['healing_max_holonomy']:.0e}  "
                  f"[{'E0c PASS' if passed else 'CHECK degree/other'}]")
    json.dump(out, open(Path(__file__).parent / "e0c_results.json", "w"), indent=2)
    print("-> e0c_results.json")


if __name__ == "__main__":
    main()
