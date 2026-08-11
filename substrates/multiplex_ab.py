#!/usr/bin/env python3
"""
Coupled address/transport multiplex on Ammann-Beenker.

Two layers on one node set, so no correspondence has to be invented:

  Layer 1  address    - perpendicular-space coordinates, fixed by the lift
  Layer 2  transport  - the tile-edge graph, perturbed by phason phase

Coupling. An AB edge is a unit step along one lattice axis, so every edge has
|delta perp| = 1 exactly; an edge-distance coupling is therefore degenerate and
cancels under row-normalisation. The address layer instead enters as a potential
on vertices, biasing transport toward the centre of the acceptance window:

    P_ij  proportional to  A_ij * exp(-perp_r_j^2 / (2 sigma^2)),  row-normalised

sigma -> infinity recovers the plain random walk on A.

Nulls. Two, run alongside every measurement:

  shuffle   - permute perp_r across vertices. Identical sparsity, identical
              weight multiset, coupling destroyed. Anything that does not
              survive this was a property of the weight distribution.
  uniform   - sigma -> infinity, the uncoupled walk.

Experiment A sweeps phason phase and measures whether the address channel stays
readable. Experiment B sweeps sigma and measures what the coupling does to
transport.
"""

import argparse
import sys

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigs
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KDTree

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_ab import generate, build_edges
from audit_with_nulls import adjacency, shared_core_labels

BASE_OFFSET = np.array([0.1381, 0.0927])


def substrate(phason=0.0, extent=18):
    """AB patch at a given phason phase (uniform acceptance-window shift).

    A uniform shift is a global phason translation, which maps AB to a locally
    isomorphic AB. It is a symmetry, not a defect-generating perturbation.
    """
    lifts, par, perp = generate(extent, BASE_OFFSET + np.array([phason, 0.0]))
    return lifts, par, perp, build_edges(lifts)


def substrate_disordered(amplitude, extent=18, seed=0):
    """AB patch under random phason DISORDER, which does generate defects.

    Each lattice point gets an independent perturbation of its perpendicular
    coordinate before the acceptance test, so flips occur scattered through the
    patch rather than coherently. This is the strain-field case; the uniform
    shift above is the rigid-translation case.
    """
    import itertools
    from generate_ab import PERP, PAR, octagon_window, _ccw, inside
    window = _ccw(octagon_window())
    rng = np.random.default_rng(seed)
    axis = np.arange(-extent, extent + 1, dtype=np.int32)
    tail = np.array(list(itertools.product(axis, axis, axis)), dtype=np.int32)
    kept = []
    for n0 in axis:
        blk = np.empty((len(tail), 4), dtype=np.int32)
        blk[:, 0] = n0; blk[:, 1:] = tail
        pp = blk @ PERP + BASE_OFFSET
        jitter = rng.normal(0.0, amplitude, pp.shape) if amplitude > 0 else 0.0
        keep = inside(window, pp + jitter)
        if keep.any():
            kept.append(blk[keep])
    lifts = np.concatenate(kept)
    return lifts, lifts @ PAR, lifts @ PERP + BASE_OFFSET, build_edges(lifts)


def edge_jaccard_by_lift(lifts_a, Ea, lifts_b, Eb):
    """Compare edge sets by lift coordinate; row indices shift between phases."""
    A = {(tuple(lifts_a[u]), tuple(lifts_a[v])) for u, v in Ea}
    B = {(tuple(lifts_b[u]), tuple(lifts_b[v])) for u, v in Eb}
    return len(A & B) / len(A | B)


def transition(n, edges, weight, sigma):
    """Row-normalised walk on `edges`, biased by a per-vertex potential."""
    if sigma is None:                        # uncoupled reference
        w = np.ones(n)
    else:
        w = np.exp(-(weight ** 2) / (2.0 * sigma ** 2))
    rows, cols, vals = [], [], []
    for u, v in edges:
        rows += [u, v]
        cols += [v, u]
        vals += [w[v], w[u]]
    P = csr_matrix((vals, (rows, cols)), shape=(n, n))
    rs = np.asarray(P.sum(1)).ravel()
    rs[rs == 0] = 1.0
    return csr_matrix((1.0 / rs, (np.arange(n), np.arange(n))), shape=(n, n)) @ P


def transport_stats(P, par, sources, steps=200):
    """Run the walk from point sources; report spread and localisation.

    Avoids the eigensolver, whose spectrum here is near-degenerate and does not
    converge. Spread is the activation-weighted mean displacement; localisation
    is the inverse participation ratio (higher = more concentrated).
    """
    spreads, iprs = [], []
    for src in sources:
        v = np.zeros(P.shape[0]); v[src] = 1.0
        for _ in range(steps):
            v = v @ P
        tot = v.sum()
        if tot <= 0:
            continue
        w = v / tot
        spreads.append(float((w * np.linalg.norm(par - par[src], axis=1)).sum()))
        iprs.append(float((w ** 2).sum()))
    return float(np.mean(spreads)), float(np.mean(iprs))


def address_auc(perp, active, y, seed=0):
    X = np.column_stack([perp, np.linalg.norm(perp, axis=1)])[active]
    y = np.asarray(y, int)
    if y.sum() < 6 or (1 - y).sum() < 6:
        return float("nan")
    cv = StratifiedKFold(3, shuffle=True, random_state=seed)
    p = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = HistGradientBoostingClassifier(max_iter=200, random_state=0)
        m.fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, p))


def labels_for(par, perp, edges, interior=0.75):
    n = len(par)
    rad = np.linalg.norm(par - par.mean(0), axis=1)
    active = np.sort(np.argsort(rad)[:int(round(interior * n))]).tolist()
    med = float(np.median(np.linalg.norm(par[[u for u, _ in edges]]
                                         - par[[v for _, v in edges]], axis=1)))
    q = KDTree(par).query_radius(par[active], r=3.0 * med)
    seeds = {active[k]: q[k].tolist() for k in range(len(active))}
    y, _, _, _ = shared_core_labels(adjacency(n, edges), active, seeds)
    return active, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=18)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    lifts0, par0, perp0, E0 = substrate(0.0, args.extent)

    print("=" * 78)
    print("A1. Uniform phason shift  (rigid translation of the acceptance window)")
    print("=" * 78)
    print(f"{'shift':>7} {'vertices':>9} {'edge J':>8} {'pos':>5} {'address AUC':>12} {'shuffled':>10}")
    for d in [0.0, 0.01, 0.05, 0.15, 0.30, 0.60]:
        lf, par, perp, E = substrate(d, args.extent)
        active, y = labels_for(par, perp, E)
        ej = edge_jaccard_by_lift(lifts0, E0, lf, E)
        auc = address_auc(perp, active, y)
        sh = address_auc(perp[rng.permutation(len(perp))], active, y)
        print(f"{d:7.2f} {len(par):9d} {ej:8.4f} {int(y.sum()):5d} {auc:12.4f} {sh:10.4f}")

    print()
    print("=" * 78)
    print("A2. Random phason disorder  (independent perp jitter -> scattered defects)")
    print("=" * 78)
    print(f"{'amp':>7} {'vertices':>9} {'edge J':>8} {'pos':>5} {'address AUC':>12} {'shuffled':>10}")
    for a in [0.0, 0.02, 0.05, 0.10, 0.20, 0.40]:
        lf, par, perp, E = substrate_disordered(a, args.extent, seed=args.seed)
        active, y = labels_for(par, perp, E)
        ej = edge_jaccard_by_lift(lifts0, E0, lf, E)
        auc = address_auc(perp, active, y)
        sh = address_auc(perp[rng.permutation(len(perp))], active, y)
        print(f"{a:7.2f} {len(par):9d} {ej:8.4f} {int(y.sum()):5d} {auc:12.4f} {sh:10.4f}")

    print()
    print("=" * 78)
    print("B. Coupled multiplex vs shuffle null  (unperturbed substrate)")
    print("=" * 78)
    n = len(par0)
    pr = np.linalg.norm(perp0, axis=1)
    pr_sh = pr[rng.permutation(n)]
    centre = np.argsort(np.linalg.norm(par0 - par0.mean(0), axis=1))[:400]
    src = rng.choice(centre, 8, replace=False)

    sp_u, ip_u = transport_stats(transition(n, E0, pr, None), par0, src)
    print(f"uncoupled walk (sigma -> inf):  spread {sp_u:.4f}   localisation {ip_u:.3e}")
    print()
    print(f"{'sigma':>7} | {'COUPLED':^26} | {'SHUFFLE NULL':^26} | {'difference':>11}")
    print(f"{'':>7} | {'spread':>12} {'localisation':>13} | {'spread':>12} {'localisation':>13} | {'spread':>11}")
    for sg in [3.0, 1.5, 1.0, 0.7, 0.5]:
        sc, ic = transport_stats(transition(n, E0, pr, sg), par0, src)
        ss, is_ = transport_stats(transition(n, E0, pr_sh, sg), par0, src)
        print(f"{sg:7.2f} | {sc:12.4f} {ic:13.3e} | {ss:12.4f} {is_:13.3e} | {sc-ss:+11.4f}")

    print()
    print("Coupled vs shuffled at matched sigma isolates the address layer:")
    print("identical sparsity, identical weight multiset, correspondence destroyed.")


if __name__ == "__main__":
    main()
