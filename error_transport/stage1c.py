#!/usr/bin/env python3
"""
Stage-1C uniform-defect control (labelled additive follow-up; Stage-1/1B FROZEN).

Builds a crystalline control whose TRAP field is genuinely uniform / hyperuniform-like
(blue-noise / Poisson-disk placement), matched to each native's defect count, degree
histogram, nearest-defect spacing, and number variance. Rules + predeclared tolerances
are sealed in STAGE1C_CONTROL_SEAL.md. TRANSPORT RUNS ONLY IF THE SPATIAL-MATCH GATE
PASSES; otherwise the size is reported as a spatial-mismatch STOP with no transport.

Same sealed dynamics, κ=10. Seed 16180339 (distinct from pilot/Stage-1/Stage-1B).
"Hyperuniform-like / suppressed number fluctuations" — strict hyperuniformity NOT
claimed from finite diagnostics.
"""

import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from collections import Counter
from scipy.spatial import cKDTree
from seamless_torus import SeamlessTorus
from matched_control import build_matched
from discrimination import walk_graph, _degrees_of
from inference import _wilson

HERE = Path(__file__).parent
SEED = 16180339
TRIALS = 8000
N_REAL = 10
SCALES = [0.15, 0.20, 0.25]
GATE_SCALE = 0.20
NATIVES = [("ammann_beenker", 1), ("ammann_beenker", 2), ("ammann_beenker", 3),
           ("penrose", 1), ("penrose", 2), ("penrose", 3)]
# predeclared tolerances (STAGE1C_CONTROL_SEAL.md)
TOL_COUNT = 0.05
TOL_HIST_TV = 0.05
TOL_NUMVAR_ABS = 0.12
TOL_NUMVAR_MAX = 0.30
TOL_NN = 0.15


def _tiled(pts, P_a, P_b):
    return np.vstack([pts + a * P_a + b * P_b
                      for a in (-1, 0, 1) for b in (-1, 0, 1)])


def bluenoise_sites(node_par, M, P_a, P_b, rng):
    """Poisson-disk (blue-noise) placement of ~M sites on grid nodes: maximal set
    with torus min-separation r, r binary-searched so |count-M| is minimised."""
    n = len(node_par)
    tiled = _tiled(node_par, P_a, P_b)
    base = np.tile(np.arange(n), 9)
    tree = cKDTree(tiled)
    perm = rng.permutation(n)

    def place(r):
        blocked = np.zeros(n, bool); sites = []
        for idx in perm:
            if blocked[idx]:
                continue
            sites.append(idx)
            for ti in tree.query_ball_point(node_par[idx], r):
                blocked[base[ti]] = True
        return sites

    lo, hi = 1e-3, float(np.sqrt(abs(P_a[0]*P_b[1]-P_a[1]*P_b[0])))
    best = place(lo)
    for _ in range(28):
        r = 0.5 * (lo + hi)
        s = place(r)
        if abs(len(s) - M) < abs(len(best) - M):
            best = s
        if len(s) > M:
            lo = r
        else:
            hi = r
    return np.array(best[:M] if len(best) >= M else best, dtype=int)


def trap_stats(node_par, deg, P_a, P_b, rng, trap_deg=3, ncent=600):
    mask = deg <= trap_deg
    pts = node_par[mask]; m = len(pts); N = len(deg)
    res = dict(trap_frac=round(m / N, 4), n_traps=m)
    if m < 5:
        return {**res, "nn_mean": None, "numvar": {}, "void": None}
    tiled = _tiled(pts, P_a, P_b)
    tree = cKDTree(tiled)
    d, _ = tree.query(pts, k=2)
    nn = d[:, 1]
    res["nn_mean"] = round(float(nn.mean()), 4)
    res["nn_cv"] = round(float(nn.std() / nn.mean()), 4)
    area = abs(P_a[0]*P_b[1]-P_a[1]*P_b[0])
    fr = rng.random((ncent, 2))
    centers = fr[:, [0]] * P_a + fr[:, [1]] * P_b
    nv = {}
    for s in SCALES:
        R = s * np.sqrt(area)
        counts = np.array([len(tree.query_ball_point(c, R)) for c in centers])
        mc = counts.mean()
        nv[str(s)] = round(float(counts.var() / mc), 4) if mc > 0 else None
    res["numvar"] = nv
    # void proxy: largest nearest-trap distance over random probes (biggest empty gap)
    dd, _ = tree.query(centers, k=1)
    res["void"] = round(float(np.percentile(dd, 99)), 4)
    return res


def hist_tv(a, b, keys):
    ca, cb = Counter(a.tolist()), Counter(b.tolist())
    ta, tb = len(a), len(b)
    return 0.5 * sum(abs(ca.get(k, 0) / ta - cb.get(k, 0) / tb) for k in keys)


def build_uniform(substrate, oi, T, qc_deg, rng, seed):
    n_native = T.n
    from controls import build_oblique
    g = build_oblique(T.P_a, T.P_b, n_native)
    n = g["n_nodes"]; node_par = g["node_par"]
    non4 = qc_deg[qc_deg != 4]
    M = len(non4)
    M_grid = int(round(M * n / n_native))          # scale count to grid N
    sites = bluenoise_sites(node_par, M_grid, T.P_a, T.P_b, rng)
    target = np.full(n, 4, dtype=int)
    vals = rng.permutation(non4)
    if len(sites) <= len(vals):
        target[sites] = vals[:len(sites)]
    else:
        target[sites] = rng.choice(non4, size=len(sites))
    gg = build_matched(substrate, oi, seed=seed, target_degrees=target)
    return gg


def main():
    rows = []
    for substrate, oi in NATIVES:
        T = SeamlessTorus(substrate, oi)
        qc_deg = T.degrees()
        ss = np.random.SeedSequence([SEED, hash((substrate, oi)) % (2**31)])
        rng = np.random.default_rng(ss)
        qc_stat = trap_stats(T.node_par, qc_deg, T.P_a, T.P_b, rng)
        keys = sorted(set(qc_deg.tolist()) | {1, 2, 3, 4, 5, 6, 7, 8})
        # build ensemble + spatial stats
        ens = []
        stats = []
        for r in range(N_REAL):
            gg = build_uniform(substrate, oi, T, qc_deg, rng, seed=5000 + r)
            dg = _degrees_of(gg)
            st = trap_stats(gg["node_par"], dg, T.P_a, T.P_b, rng)
            st["_tv"] = hist_tv(dg, qc_deg, keys)
            st["_ndef"] = int((dg != 4).sum())
            stats.append((gg, dg, st))
        # ensemble-mean spatial diagnostics
        ndef_qc = int((qc_deg != 4).sum()) * stats[0][0]["n_nodes"] // T.n \
            if False else int((qc_deg != 4).sum())
        mean_ndef = np.mean([s["_ndef"] for _, _, s in stats])
        mean_tv = np.mean([s["_tv"] for _, _, s in stats])
        mean_nv = np.mean([s["numvar"][str(GATE_SCALE)] for _, _, s in stats
                           if s["numvar"].get(str(GATE_SCALE)) is not None])
        mean_nn = np.mean([s["nn_mean"] for _, _, s in stats if s["nn_mean"]])
        # scale QC count to grid N for T1
        gridN = stats[0][0]["n_nodes"]
        qc_ndef_scaled = int((qc_deg != 4).sum()) * gridN / T.n
        t1 = abs(mean_ndef - qc_ndef_scaled) / qc_ndef_scaled <= TOL_COUNT
        t2 = mean_tv <= TOL_HIST_TV
        qc_nv = qc_stat["numvar"][str(GATE_SCALE)]
        t3 = (abs(mean_nv - qc_nv) <= TOL_NUMVAR_ABS) and (mean_nv <= TOL_NUMVAR_MAX)
        qc_nn = qc_stat["nn_mean"]
        t4 = abs(mean_nn - qc_nn) / qc_nn <= TOL_NN
        gate = bool(t1 and t2 and t3 and t4)
        row = dict(substrate=substrate, order=T.order, convergent=T.convergent,
                   N=gridN, N_native=T.n,
                   QC_numvar=qc_stat["numvar"], QC_nn=qc_nn,
                   QC_ndef=int((qc_deg != 4).sum()),
                   ctrl_numvar_gatescale=round(float(mean_nv), 4),
                   ctrl_numvar_all={s: round(float(np.mean(
                       [st["numvar"][s] for _, _, st in stats
                        if st["numvar"].get(s) is not None])), 4) for s in
                       [str(x) for x in SCALES]},
                   ctrl_nn=round(float(mean_nn), 4),
                   ctrl_ndef=round(float(mean_ndef), 1),
                   ctrl_hist_tv=round(float(mean_tv), 4),
                   gate=dict(T1_count=bool(t1), T2_hist=bool(t2),
                             T3_numvar=bool(t3), T4_nn=bool(t4), PASS=gate))
        print(f"\n=== {substrate} order {T.order} ({T.convergent})  N={gridN} ===")
        print(f"  numvar(s=.20): QC {qc_nv}  uniform-ctrl {mean_nv:.3f}   "
              f"nn: QC {qc_nn} ctrl {mean_nn:.3f}   defcount QC~{qc_ndef_scaled:.0f} "
              f"ctrl {mean_ndef:.0f}  histTV {mean_tv:.3f}")
        print(f"  GATE  T1_count={t1} T2_hist={t2} T3_numvar={t3} T4_nn={t4}  "
              f"-> {'PASS' if gate else 'FAIL (STOP: no transport)'}")
        if gate:
            ps = []
            for (gg, dg, st) in stats:
                p, _ = walk_graph(gg, ss.spawn(1)[0])
                ps.append(p)
            ps = np.array(ps)
            p_qc, _ = walk_graph(T, ss.spawn(1)[0])
            row["transport"] = dict(
                P_uniform_mean=round(float(ps.mean()), 5),
                P_uniform_graphstd=round(float(ps.std(ddof=1)), 5),
                P_uniform_min=round(float(ps.min()), 5),
                P_uniform_max=round(float(ps.max()), 5),
                P_QC=round(float(p_qc), 5))
            print(f"  TRANSPORT (gate passed): uniform-ctrl P_logical "
                  f"{ps.mean():.5f}±{ps.std(ddof=1):.5f}  vs  QC {p_qc:.5f}")
        else:
            row["transport"] = None
            print("  -> spatial match failed; transport NOT run (per seal).")
        rows.append(row)
    out = dict(seed=SEED, trials=TRIALS, n_realisations=N_REAL, kappa=10,
               scales=SCALES, gate_scale=GATE_SCALE, rows=rows)
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "stage1c.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n-> results/stage1c.json")
    return out


if __name__ == "__main__":
    main()
