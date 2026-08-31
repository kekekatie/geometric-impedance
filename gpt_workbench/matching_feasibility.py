#!/usr/bin/env python3
"""
GEOMETRY/FEATURE-ONLY matching-feasibility + motif-size diagnostics, and the frozen snapped-time
list (Work-GPT/Sol authorised, design-only). STRICTLY geometry + physical features + graph
combinatorics: NO perpendicular-space ADDRESS values, NO targets, NO LDOS, NO beta, NO dynamics.

For each planned patch (r16 common set): motif-group sizes; singleton fraction; whether a within-
motif one-to-one bijection (derangement) exists using k=32 nearest physical-feature neighbours,
escalating 32 -> 64 -> full same-motif group; and the k-escalation rate. Also generates and asserts
the 48-point beta grid snapped to the 161-point boundary grid.
"""
import sys
import numpy as np
from scipy.spatial import ConvexHull, cKDTree
from scipy.optimize import linear_sum_assignment
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../substrates")
from generate_rank4 import generate, build_edges, structure

TIERS = [("silver", 8, 14), ("silver", 8, 16), ("silver", 8, 18),
         ("golden", 10, 18), ("golden", 10, 20), ("golden", 10, 22),
         ("platinum", 12, 16), ("platinum", 12, 18), ("platinum", 12, 20)]
OFFS = [(0.13, 0.37), (0.29, 0.11), (0.41, 0.23)]      # 3 representative fresh offsets
SINGLETON_MAX = 0.05


def hull_depth(P):
    h = ConvexHull(P); A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(P @ A.T + b).max(1)


def perfect_matching_exists(sub_idx, feats, k):
    """Does a one-to-one derangement exist within this motif group using each vertex's k nearest
    same-group physical-feature neighbours (excluding self)? Min-cost assignment via
    linear_sum_assignment on a cost matrix (allowed kNN edges = feature distance; forbidden = BIG).
    Feasible iff the optimal assignment uses no forbidden edge. A derangement always exists at full
    connectivity for m>=2, so this only ever fails for a k too small."""
    m = len(sub_idx)
    if m < 2:
        return True
    X = feats[sub_idx]
    kk = min(k, m - 1)
    tree = cKDTree(X)
    dist, nbr = tree.query(X, k=kk + 1)
    BIG = 1e6
    C = np.full((m, m), BIG)
    for a in range(m):
        for col in range(kk + 1):
            b = int(nbr[a][col])
            if b != a:                                  # robustly exclude self (handles duplicates)
                C[a, b] = dist[a][col]
    r, c = linear_sum_assignment(C)
    return bool(C[r, c].max() < BIG)


def analyse(N, ext, off):
    lifts, par, perp, ustar = generate(N, ext, offset=np.array(off))
    n = len(par); E = build_edges(lifts, N, ustar)
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j); adj[j].append(i)
    deg = np.array([len(a) for a in adj], float)
    d = par[[i for i, _ in E]] - par[[j for _, j in E]]
    ell = float(np.median(np.linalg.norm(d, axis=1)))
    db = hull_depth(par); r16 = np.where(db >= 16 * ell)[0]

    # motif keys (as in transport_run.py)
    st = structure(N); star = st["star"]
    idx = {tuple(r): k for k, r in enumerate(lifts)}
    mkey = []
    for i in range(n):
        sig = []
        for k, s in enumerate(star):
            for sgn in (1, -1):
                if tuple(lifts[i] + sgn * s) in idx:
                    sig.append((k, sgn))
        mkey.append(tuple(sorted(sig)))
    mkey = np.array([hash(m) for m in mkey])

    # continuous physical features (address-free): deg, dens, g(r), psi_n
    tree = cKDTree(par)
    def g(r): return np.array(tree.query_ball_point(par, r, return_length=True), float)
    psi = {}
    for nn in (N, N // 2, 2 * N):
        v = np.zeros(n)
        for i in range(n):
            if adj[i]:
                th = np.arctan2(par[np.array(adj[i]), 1] - par[i, 1], par[np.array(adj[i]), 0] - par[i, 0])
                v[i] = abs(np.mean(np.exp(1j * nn * th)))
        psi[nn] = v
    F = np.column_stack([deg, g(2.0), g(1.6), g(2.6), g(4.0), g(6.0), psi[N], psi[N // 2], psi[2 * N]])
    # standardise within r16
    Fr = F[r16]; Fr = (Fr - Fr.mean(0)) / np.where(Fr.std(0) > 1e-12, Fr.std(0), 1.0)
    mk = mkey[r16]

    groups = {}
    for local, key in enumerate(mk):
        groups.setdefault(key, []).append(local)
    n16 = len(r16)
    singletons = sum(len(g_) for g_ in groups.values() if len(g_) == 1)
    esc32 = esc64 = escfull = infeasible = 0
    ngroups_ge2 = 0
    for key, g_ in groups.items():
        if len(g_) < 2:
            continue
        ngroups_ge2 += 1
        gi = np.array(g_)
        if perfect_matching_exists(gi, Fr, 32):
            esc32 += 1
        elif perfect_matching_exists(gi, Fr, 64):
            esc64 += 1
        elif perfect_matching_exists(gi, Fr, len(gi)):
            escfull += 1
        else:
            infeasible += 1
    return dict(n16=n16, singl=singletons / n16, nmotif=len(groups),
                maxgrp=max(len(g_) for g_ in groups.values()),
                esc32=esc32, esc64=esc64, escfull=escfull, infeasible=infeasible,
                ngrp=ngroups_ge2)


def main():
    print("# MATCHING-FEASIBILITY + MOTIF-SIZE DIAGNOSTICS (geometry/feature only; no address/targets)")
    print(f"# k escalation 32->64->full; singleton-max {SINGLETON_MAX:.0%}; offsets {OFFS}")
    for name, N, ext in TIERS:
        rows = [analyse(N, ext, o) for o in OFFS]
        s = np.mean([r["singl"] for r in rows]); smax = max(r["singl"] for r in rows)
        e32 = sum(r["esc32"] for r in rows); e64 = sum(r["esc64"] for r in rows)
        ef = sum(r["escfull"] for r in rows); inf = sum(r["infeasible"] for r in rows)
        ng = sum(r["ngrp"] for r in rows)
        verdict = "FEASIBLE" if smax <= SINGLETON_MAX and inf == 0 else "INFEASIBLE(local null)"
        print(f"\n{name}({N}) e{ext}: r16~{rows[0]['n16']}  motif-groups~{rows[0]['nmotif']}  "
              f"max-group~{rows[0]['maxgrp']}")
        print(f"   singleton frac: mean {s:.3%} max {smax:.3%}  (limit {SINGLETON_MAX:.0%})")
        print(f"   groups>=2: {ng}  | k=32 ok: {e32}  k=64: {e64}  full: {ef}  INFEASIBLE: {inf}"
              f"  -> {verdict}")

    # frozen snapped-time list
    print(f"\n{'='*70}\nSNAPPED beta-time list\n{'='*70}")
    beta = np.logspace(np.log10(2.0), np.log10(8.0), 48)
    grid = np.linspace(0.0, 8.0, 161)
    snapped = grid[np.abs(beta[:, None] - grid[None, :]).argmin(1)]
    uniq = len(np.unique(snapped))
    maxerr = float(np.max(np.abs(beta - snapped)))
    print(f"48 log times on [2,8] snapped to 161-pt [0,8] grid: unique={uniq}/48  max|error|={maxerr:.4f}")
    assert uniq == 48, "snapped times not unique!"
    np.savetxt(__file__.rsplit("/", 1)[0] + "/snapped_beta_times.txt", snapped,
               fmt="%.4f", header="48 beta-fit times, snapped to linspace(0,8,161); unique; "
               f"max snap error {maxerr:.4f}")
    print("stored -> gpt_workbench/snapped_beta_times.txt")
    print("DONE_MATCH")


if __name__ == "__main__":
    main()
