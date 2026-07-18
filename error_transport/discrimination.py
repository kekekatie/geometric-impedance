#!/usr/bin/env python3
"""
Stage-1b DISCRIMINATION TEST (labelled follow-up; Stage-1 stays frozen).

Addresses GPT's review of the Stage-1 result (QC ≈ clean grid > random-defect grid):
  (2) matched-defect ENSEMBLE — ~10 independent random realisations per size, so the
      graph (not just the walker) is a statistical unit; report graph-to-graph spread.
  (3) SPATIAL diagnostics of the defect field — trap nearest-neighbour spacing,
      clumpiness, and a number-variance / hyperuniformity ratio.
  (4) HYPERUNIFORM-DEFECT control — a grid whose defect ARRANGEMENT is stamped from
      the native (nearest-position degree transfer), matching spatial organisation,
      not just degree count. Discriminates "defect spacing" from "something more".
  (fit) 1/logN treated as a candidate finite-size description vs alternatives.

Same sealed dynamics and κ=10 as inference.py. No retuning of Stage-1.
"""

import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from scipy.spatial import cKDTree
from seamless_torus import SeamlessTorus
from controls import build_oblique
from matched_control import build_matched
from inference import (run_walk, _csr_wind, _edges_by_seam, _directed3, _wilson,
                       KAPPA)

HERE = Path(__file__).parent
DISCR_MASTER_SEED = 27182818            # distinct from pilot + Stage-1 inference
TRIALS = 8000
N_RANDOM = 10
N_SPATIAL = 4
NATIVES = [("ammann_beenker", 1), ("ammann_beenker", 2), ("ammann_beenker", 3),
           ("penrose", 1), ("penrose", 2), ("penrose", 3)]


def walk_graph(graph, ss, trials=TRIALS):
    directed3, n = _directed3(graph)
    offsets, nbr, wind = _csr_wind(n, directed3)
    nonseam, _ = _edges_by_seam(directed3)
    E = np.array([(a, b) for (a, b, w) in nonseam], dtype=np.int64)
    W0 = np.array([w for (a, b, w) in nonseam], dtype=np.int64)
    rng = np.random.default_rng(ss)
    pick = rng.integers(0, len(nonseam), size=trials)
    coin = rng.random(trials) < 0.5
    a = E[pick, 0]; b = E[pick, 1]; w0 = W0[pick]
    nA = np.where(coin, a, b).astype(np.int64)
    nB = np.where(coin, b, a).astype(np.int64)
    WA = np.zeros((trials, 2), dtype=np.int64)
    WB = np.where(coin[:, None], w0, -w0).astype(np.int64)
    heal, logical, cens = run_walk(offsets, nbr, wind, nA, nB, WA, WB,
                                   KAPPA * n, ss.spawn(1)[0])
    return logical / trials, n


def _degrees_of(graph):
    directed3, n = _directed3(graph)
    from collections import Counter
    deg = Counter(); seen = set()
    for u, v, w in directed3:
        k = (min(u, v), max(u, v),
             tuple(sorted((tuple(w), tuple((-np.array(w)).tolist())))))
        if k in seen:
            continue
        seen.add(k); deg[u] += 1; deg[v] += 1
    return np.array([deg[i] for i in range(n)])


def spatial_stats(node_par, deg, P_a, P_b, rng, trap_deg=3):
    """Diagnostics of the TRAP field (degree<=trap_deg): fraction, nearest-neighbour
    spacing coefficient-of-variation (clumpiness), and number-variance ratio
    sigma^2/<N> in random windows (1=Poisson, <1=hyperuniform/even, >1=clumped)."""
    mask = deg <= trap_deg
    pts = node_par[mask]
    m = len(pts)
    N = len(deg)
    if m < 5:
        return dict(trap_frac=round(m / N, 4), nn_cv=None, numvar_ratio=None, n_traps=m)
    imgs = [pts + a * P_a + b * P_b for a in (-1, 0, 1) for b in (-1, 0, 1)]
    tiled = np.vstack(imgs)
    tree = cKDTree(tiled)
    d, _ = tree.query(pts, k=2)              # self + nearest other
    nn = d[:, 1]
    nn_cv = float(nn.std() / nn.mean())      # high => clumpy (voids + tight pairs)
    cell_area = abs(P_a[0] * P_b[1] - P_a[1] * P_b[0])
    R = 0.20 * np.sqrt(cell_area)
    ncent = 500
    fr = rng.random((ncent, 2))
    centers = fr[:, [0]] * P_a + fr[:, [1]] * P_b
    counts = np.array([len(tree.query_ball_point(c, R)) for c in centers])
    mean_c = counts.mean()
    numvar_ratio = float(counts.var() / mean_c) if mean_c > 0 else None
    return dict(trap_frac=round(m / N, 4), n_traps=m,
                nn_cv=round(nn_cv, 4),
                numvar_ratio=round(numvar_ratio, 4) if numvar_ratio else None)


def _fit_scaling(Ns, Ps):
    """Descriptive fits of P_logical(N): a/logN+b, a/sqrt(N)+b, a*N^-p+b (3 pts)."""
    Ns = np.array(Ns, float); Ps = np.array(Ps, float)
    out = {}
    def lin(x):
        A = np.vstack([x, np.ones_like(x)]).T
        coef, res, *_ = np.linalg.lstsq(A, Ps, rcond=None)
        pred = A @ coef
        ss = float(np.sum((Ps - pred) ** 2))
        return coef.tolist(), round(ss, 8)
    out["a/logN+b"] = dict(zip(["coef", "sse"], lin(1.0 / np.log(Ns))))
    out["a/sqrtN+b"] = dict(zip(["coef", "sse"], lin(1.0 / np.sqrt(Ns))))
    out["a/N+b"] = dict(zip(["coef", "sse"], lin(1.0 / Ns)))
    return out


def main():
    results = []
    for substrate, oi in NATIVES:
        T = SeamlessTorus(substrate, oi)
        n = T.n
        ss0 = np.random.SeedSequence([DISCR_MASTER_SEED, hash((substrate, oi)) % (2**31)])
        rng = np.random.default_rng(ss0)
        qc_deg = T.degrees()
        # QC walk (single deterministic graph)
        p_qc, _ = walk_graph(T, ss0.spawn(1)[0])
        # clean grid
        grid = build_oblique(T.P_a, T.P_b, n)
        p_clean, _ = walk_graph(grid, ss0.spawn(1)[0])
        # RANDOM matched-defect ENSEMBLE
        rand_ps = []
        for r in range(N_RANDOM):
            g = build_matched(substrate, oi, seed=1000 + r)
            p, _ = walk_graph(g, ss0.spawn(1)[0])
            rand_ps.append(p)
        rand_ps = np.array(rand_ps)
        # HYPERUNIFORM (spatial-stamped) matched-defect ENSEMBLE
        spat_ps = []
        spat_stat = None
        for r in range(N_SPATIAL):
            g = build_matched(substrate, oi, seed=2000 + r, spatial_ref=T)
            p, _ = walk_graph(g, ss0.spawn(1)[0])
            spat_ps.append(p)
            if spat_stat is None:
                spat_stat = spatial_stats(g["node_par"], _degrees_of(g),
                                          T.P_a, T.P_b, rng)
        spat_ps = np.array(spat_ps)
        # spatial diagnostics
        one_rand = build_matched(substrate, oi, seed=1000)
        qc_stat = spatial_stats(T.node_par, qc_deg, T.P_a, T.P_b, rng)
        rand_stat = spatial_stats(one_rand["node_par"], _degrees_of(one_rand),
                                  T.P_a, T.P_b, rng)
        row = dict(
            substrate=substrate, order=T.order, convergent=T.convergent, N=n,
            P_QC=round(p_qc, 5), P_QC_wilson=[round(x, 5) for x in
                                              _wilson(int(p_qc * TRIALS), TRIALS)],
            P_clean=round(p_clean, 5),
            P_random_mean=round(float(rand_ps.mean()), 5),
            P_random_graphstd=round(float(rand_ps.std(ddof=1)), 5),
            P_random_min=round(float(rand_ps.min()), 5),
            P_random_max=round(float(rand_ps.max()), 5),
            P_spatial_mean=round(float(spat_ps.mean()), 5),
            P_spatial_graphstd=round(float(spat_ps.std(ddof=1)), 5),
            trap_stats=dict(QC=qc_stat, random=rand_stat, spatial=spat_stat),
        )
        results.append(row)
        print(f"\n=== {substrate} order {T.order} ({T.convergent})  N={n} ===")
        print(f"  P_logical:  QC {row['P_QC']}  clean {row['P_clean']}  "
              f"random {row['P_random_mean']}±{row['P_random_graphstd']} "
              f"[{row['P_random_min']},{row['P_random_max']}]  "
              f"spatial {row['P_spatial_mean']}±{row['P_spatial_graphstd']}")
        print(f"  trap numvar-ratio (1=Poisson,<1=even): "
              f"QC {qc_stat['numvar_ratio']}  random {rand_stat['numvar_ratio']}  "
              f"spatial {spat_stat['numvar_ratio']}   | nn_cv: "
              f"QC {qc_stat['nn_cv']} random {rand_stat['nn_cv']} "
              f"spatial {spat_stat['nn_cv']}")
    # scaling fits per substrate (QC)
    fits = {}
    for sub in ["ammann_beenker", "penrose"]:
        pts = sorted([r for r in results if r["substrate"] == sub],
                     key=lambda r: r["N"])
        fits[sub] = _fit_scaling([r["N"] for r in pts], [r["P_QC"] for r in pts])
    print("\n=== scaling fits (QC P_logical vs N; SSE, lower=better fit) ===")
    for sub, f in fits.items():
        best = min(f, key=lambda k: f[k]["sse"])
        print(f"  {sub}: " + "  ".join(f"{k}:SSE={v['sse']:.2e}"
              for k, v in f.items()) + f"   best={best}")
    out = dict(discr_master_seed=DISCR_MASTER_SEED, trials=TRIALS,
               n_random_realisations=N_RANDOM, n_spatial_realisations=N_SPATIAL,
               kappa=KAPPA, rows=results, scaling_fits=fits)
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "discrimination.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n-> results/discrimination.json")
    return out


if __name__ == "__main__":
    main()
