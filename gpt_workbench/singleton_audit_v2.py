#!/usr/bin/env python3
"""
GEOMETRY/FEATURE-ONLY six-offset singleton+matching audit AND randomisation-diversity diagnostic
(Work-GPT/Sol authorised, design-only). STRICTLY geometry + physical features + graph combinatorics:
NO perpendicular-space ADDRESS values, NO targets, NO LDOS, NO beta, NO dynamics.

Part A: all NINE configs x ALL SIX frozen offsets, per-patch (not summaries): singleton fraction,
        deterministic k-escalation counts (32->64->full), per-patch feasibility verdict (5% ceiling).
Part B: randomisation-diversity of the NEW stochastic assignment law (independent seeded random edge
        costs per repetition -> min-cost perfect assignment on the frozen kNN-within-motif graph):
        #distinct assignments, fraction of vertices changing destination, source->dest standardised
        feature distance (median/95th/max), vs an unrestricted within-motif derangement.
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
OFFS = [(0.13, 0.37), (0.29, 0.11), (0.41, 0.23), (0.05, 0.47), (0.19, 0.31), (0.37, 0.09)]
SINGLETON_MAX = 0.05
BIG = 1e6


def hull_depth(P):
    h = ConvexHull(P); A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(P @ A.T + b).max(1)


def patch_features(N, ext, off):
    lifts, par, perp, ustar = generate(N, ext, offset=np.array(off))
    n = len(par); E = build_edges(lifts, N, ustar)
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j); adj[j].append(i)
    deg = np.array([len(a) for a in adj], float)
    d = par[[i for i, _ in E]] - par[[j for _, j in E]]
    ell = float(np.median(np.linalg.norm(d, axis=1)))
    db = hull_depth(par); r16 = np.where(db >= 16 * ell)[0]
    st = structure(N); star = st["star"]
    idx = {tuple(r): k for k, r in enumerate(lifts)}
    mkey = []
    for i in range(n):
        sig = []
        for k, s in enumerate(star):
            for sgn in (1, -1):
                if tuple(lifts[i] + sgn * s) in idx:
                    sig.append((k, sgn))
        mkey.append(hash(tuple(sorted(sig))))
    mkey = np.array(mkey)
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
    Fr = F[r16]; Fr = (Fr - Fr.mean(0)) / np.where(Fr.std(0) > 1e-12, Fr.std(0), 1.0)
    return Fr, mkey[r16], len(r16)


def knn_edges(X, k):
    m = len(X); kk = min(k, m - 1)
    _, nbr = cKDTree(X).query(X, k=kk + 1)
    E = [[] for _ in range(m)]
    for a in range(m):
        for col in range(kk + 1):
            b = int(nbr[a][col])
            if b != a:
                E[a].append(b)
    return E


def assign_random(edges, rng):
    """Min-cost perfect assignment with independent random costs on allowed edges. Returns perm or
    None if infeasible on this candidate graph."""
    m = len(edges)
    C = np.full((m, m), BIG)
    for a in range(m):
        for b in edges[a]:
            C[a, b] = rng.random()
    r, c = linear_sum_assignment(C)
    if C[r, c].max() >= BIG:
        return None
    perm = np.empty(m, int); perm[r] = c
    return perm


def feasible_at(X, k):
    e = knn_edges(X, k)
    return assign_random(e, np.random.default_rng(0)) is not None


def audit_patch(Fr, mk):
    groups = {}
    for loc, key in enumerate(mk):
        groups.setdefault(key, []).append(loc)
    n16 = len(mk)
    singl = sum(1 for g in groups.values() if len(g) == 1)
    e32 = e64 = ef = inf = ng = 0
    for key, g in groups.items():
        if len(g) < 2:
            continue
        ng += 1
        gi = np.array(g); X = Fr[gi]
        if feasible_at(X, 32):
            e32 += 1
        elif feasible_at(X, 64):
            e64 += 1
        elif feasible_at(X, len(gi)):
            ef += 1
        else:
            inf += 1
    return singl / n16, ng, e32, e64, ef, inf


def diversity(Fr, mk, reps=40, k=32):
    """Part B: run `reps` random-cost assignments; measure distinctness/locality vs unrestricted."""
    groups = [np.array(g) for g in _grp(mk).values() if len(g) >= 2]
    ss = np.random.SeedSequence(20260831)
    kids = ss.spawn(reps)
    perms = []
    for b in range(reps):
        rng = np.random.default_rng(kids[b])
        full = np.arange(len(mk))
        for gi in groups:
            e = knn_edges(Fr[gi], k)
            p = assign_random(e, rng)
            if p is None:
                e = knn_edges(Fr[gi], len(gi)); p = assign_random(e, rng)
            full[gi] = gi[p]
        perms.append(full)
    P = np.array(perms)                                   # reps x n16 (destinations)
    distinct = len({tuple(row) for row in P})
    # fraction of movable vertices changing destination between consecutive reps
    movable = np.concatenate(groups)
    chg = np.mean([(P[b][movable] != P[b + 1][movable]).mean() for b in range(reps - 1)])
    # source->dest standardised feature distance (constrained)
    def dstats(P1):
        ds = []
        for gi in groups:
            for a in gi:
                ds.append(np.linalg.norm(Fr[a] - Fr[P1[a]]))
        ds = np.array(ds)
        return np.median(ds), np.percentile(ds, 95), ds.max()
    con = np.mean([dstats(P[b]) for b in range(reps)], axis=0)
    # unrestricted within-motif derangement
    rng = np.random.default_rng(7)
    full = np.arange(len(mk))
    for gi in groups:
        pp = rng.permutation(len(gi))
        while np.any(pp == np.arange(len(gi))) and len(gi) > 1:
            pp = rng.permutation(len(gi))
        full[gi] = gi[pp]
    unc = dstats(full)
    return distinct, reps, chg, con, unc


def _grp(mk):
    g = {}
    for loc, key in enumerate(mk):
        g.setdefault(key, []).append(loc)
    return g


def main():
    print("# SIX-OFFSET SINGLETON + MATCHING AUDIT (geometry/feature only; no address/targets)")
    print(f"# 5% ceiling; deterministic k 32->64->full; per-patch (per offset)")
    for name, N, ext in TIERS:
        print(f"\n{name}({N}) e{ext}:")
        verdicts = []
        for off in OFFS:
            Fr, mk, n16 = patch_features(N, ext, off)
            s, ng, e32, e64, ef, inf = audit_patch(Fr, mk)
            ok = (s <= SINGLETON_MAX) and (inf == 0)
            verdicts.append(ok)
            print(f"   off{off}: r16={n16:5d} singl={s:6.2%} groups>=2={ng:4d} "
                  f"k32={e32} k64={e64} full={ef} INF={inf} -> {'FEAS' if ok else 'INFEAS'}")
        print(f"   PATCH VERDICT (all 6 offsets feasible?): "
              f"{'FEASIBLE' if all(verdicts) else 'INFEASIBLE (local perm null)'}")

    # Part B on two representative patches
    print(f"\n{'='*74}\nPart B: randomisation-diversity of the stochastic assignment law\n{'='*74}")
    for name, N, ext in [("golden", 10, 18), ("platinum", 12, 20)]:
        Fr, mk, n16 = patch_features(N, ext, OFFS[0])
        distinct, reps, chg, con, unc = diversity(Fr, mk)
        print(f"{name} e{ext} off{OFFS[0]} ({reps} reps): distinct assignments={distinct}/{reps}  "
              f"mean vtx dest-change between reps={chg:.1%}")
        print(f"   src->dest std feature dist (constrained): median {con[0]:.3f} p95 {con[1]:.3f} "
              f"max {con[2]:.3f}")
        print(f"   src->dest std feature dist (UNRESTRICTED shuffle): median {unc[0]:.3f} "
              f"p95 {unc[1]:.3f} max {unc[2]:.3f}  (should be much larger -> constrained is local)")
    print("DONE_AUDIT")


if __name__ == "__main__":
    main()
