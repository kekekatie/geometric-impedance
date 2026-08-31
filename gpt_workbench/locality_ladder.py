#!/usr/bin/env python3
"""
GEOMETRY/FEATURE-ONLY locality-ladder diagnostic + exact 54-row singleton table (Sol authorised,
design-only). STRICTLY geometry + physical features + graph combinatorics. NO address values, NO
targets, NO LDOS, NO beta, NO study dynamics.

Part A (all 9 configs x 6 offsets): exact per-patch singleton fraction -> singleton_54.csv.
Part B (the 7 permutation-feasible configs x 6 offsets): candidate-k ladder k in {2,4,6,8,12,16,32}.
For every exact-motif group, self forbidden, test each k INDEPENDENTLY (no silent escalation):
does a perfect derangement exist? Then diversity/locality via `reps` independent U(0,1) matchings.
Two cost laws: 'U' (uniform U(0,1) on allowed edges) and 'DW' (distance-weighted additive
stochastic: cost = feature_distance + lambda*U(0,1); lambda = median 1-NN standardised distance,
reported). Report by config and offset -> locality_ladder.csv + printed per-config summary.
"""
import sys
import numpy as np
from scipy.spatial import ConvexHull, cKDTree
from scipy.optimize import linear_sum_assignment
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../substrates")
from generate_rank4 import generate, build_edges, structure

ALL = [("silver", 8, 14), ("silver", 8, 16), ("silver", 8, 18),
       ("golden", 10, 18), ("golden", 10, 20), ("golden", 10, 22),
       ("platinum", 12, 16), ("platinum", 12, 18), ("platinum", 12, 20)]
FEASIBLE = {("silver", 14), ("silver", 16), ("silver", 18),
            ("golden", 18), ("golden", 20), ("golden", 22), ("platinum", 20)}
OFFS = [(0.13, 0.37), (0.29, 0.11), (0.41, 0.23), (0.05, 0.47), (0.19, 0.31), (0.37, 0.09)]
KLAD = [2, 4, 6, 8, 12, 16, 32]
REPS = 12
BIG = 1e6
OUT = __file__.rsplit("/", 1)[0]


def hull_depth(P):
    h = ConvexHull(P); A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(P @ A.T + b).max(1)


def features(N, ext, off):
    lifts, par, perp, ustar = generate(N, ext, offset=np.array(off))
    n = len(par); E = build_edges(lifts, N, ustar)
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j); adj[j].append(i)
    deg = np.array([len(a) for a in adj], float)
    d = par[[i for i, _ in E]] - par[[j for _, j in E]]
    ell = float(np.median(np.linalg.norm(d, axis=1)))
    r16 = np.where(hull_depth(par) >= 16 * ell)[0]
    st = structure(N); star = st["star"]; idx = {tuple(r): k for k, r in enumerate(lifts)}
    mk = []
    for i in range(n):
        sig = []
        for k, s in enumerate(star):
            for sgn in (1, -1):
                if tuple(lifts[i] + sgn * s) in idx:
                    sig.append((k, sgn))
        mk.append(hash(tuple(sorted(sig))))
    mk = np.array(mk)
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
    return Fr, mk[r16], len(r16)


def groups_ge2(mk):
    g = {}
    for loc, key in enumerate(mk):
        g.setdefault(key, []).append(loc)
    return [np.array(v) for v in g.values() if len(v) >= 2], sum(1 for v in g.values() if len(v) == 1)


def cand_edges(X, k):
    m = len(X); kk = min(k, m - 1)
    dist, nbr = cKDTree(X).query(X, k=kk + 1)
    E = [[] for _ in range(m)]; D = [[] for _ in range(m)]
    for a in range(m):
        for c in range(kk + 1):
            b = int(nbr[a][c])
            if b != a:
                E[a].append(b); D[a].append(dist[a][c])
    return E, D


def assign(E, D, rng, law, lam):
    m = len(E); C = np.full((m, m), BIG)
    for a in range(m):
        for b, dd in zip(E[a], D[a]):
            C[a, b] = rng.random() if law == 'U' else dd + lam * rng.random()
    r, c = linear_sum_assignment(C)
    if C[r, c].max() >= BIG:
        return None
    p = np.empty(m, int); p[r] = c; return p


def main():
    fs = open(OUT + "/singleton_54.csv", "w")
    fs.write("family,extent,offx,offy,r16,n_singleton,singleton_frac,n_groups_ge2\n")
    fl = open(OUT + "/locality_ladder.csv", "w")
    fl.write("family,extent,offx,offy,k,law,movable_feasible_frac,groups_fail_frac,"
             "distinct_frac,destchange,con_med,con_p95,con_max,unc_med,unc_p95,ratio_med,ratio_p95,lambda\n")
    print("# LOCALITY LADDER + 54-ROW SINGLETON (geometry/feature only)")
    for name, N, ext in ALL:
        print(f"\n{name}({N}) e{ext}:")
        for off in OFFS:
            Fr, mk, n16 = features(N, ext, off)
            grps, nsingle = groups_ge2(mk)
            fs.write(f"{name},{ext},{off[0]},{off[1]},{n16},{nsingle},{nsingle/n16:.5f},{len(grps)}\n")
            if (name, ext) not in FEASIBLE:
                continue
            movable = np.concatenate(grps) if grps else np.array([], int)
            # DW additive-stochastic law scale: PREDECLARED FIXED lambda = 1.0 in standardised-
            # feature units (the data-driven median-1NN degenerates to 0 because many vertices share
            # identical integer-count features). cost = feature_distance + lambda*U(0,1).
            lam = 1.0
            # unrestricted within-motif derangement distances (reference)
            rng0 = np.random.default_rng(1)
            und = []
            for gi in grps:
                pp = rng0.permutation(len(gi))
                while len(gi) > 1 and np.any(pp == np.arange(len(gi))):
                    pp = rng0.permutation(len(gi))
                for a, dst in zip(gi, gi[pp]):
                    und.append(np.linalg.norm(Fr[a] - Fr[dst]))
            und = np.array(und); unc_med, unc_p95 = np.median(und), np.percentile(und, 95)
            for k in KLAD:
                for law in ('U', 'DW'):
                    ss = np.random.SeedSequence(abs(hash((name, ext, off, k, law))) % (2**32))
                    kids = ss.spawn(REPS)
                    feas_mov = 0; fail = 0; perms = []; con = []
                    for gi in grps:
                        E, D = cand_edges(Fr[gi], k)
                        p0 = assign(E, D, np.random.default_rng(0), law, lam)
                        if p0 is None:
                            fail += 1
                            continue
                        feas_mov += len(gi)
                        greps = []
                        for b in range(REPS):
                            p = assign(E, D, np.random.default_rng(kids[b]), law, lam)
                            greps.append(gi[p])
                            for a_i, dst in zip(range(len(gi)), gi[p]):
                                con.append(np.linalg.norm(Fr[gi[a_i]] - Fr[dst]))
                        perms.append(np.array(greps))
                    con = np.array(con) if con else np.array([0.0])
                    # diversity across reps (concat over feasible groups)
                    if perms:
                        full = np.stack([np.concatenate([perms[g][b] for g in range(len(perms))])
                                         for b in range(REPS)])
                        distinct = len({tuple(r) for r in full}) / REPS
                        chg = np.mean([(full[b] != full[b + 1]).mean() for b in range(REPS - 1)])
                    else:
                        distinct = chg = 0.0
                    cm, cp = np.median(con), np.percentile(con, 95)
                    fl.write(f"{name},{ext},{off[0]},{off[1]},{k},{law},{feas_mov/max(len(movable),1):.4f},"
                             f"{fail/max(len(grps),1):.4f},{distinct:.3f},{chg:.4f},{cm:.4f},{cp:.4f},"
                             f"{con.max():.4f},{unc_med:.4f},{unc_p95:.4f},{cm/max(unc_med,1e-9):.4f},"
                             f"{cp/max(unc_p95,1e-9):.4f},{lam:.4f}\n")
            fs.flush(); fl.flush()
            print(f"   off{off}: done (lambda_DW={lam:.3f})", flush=True)
    fs.close(); fl.close()
    print("\nwrote singleton_54.csv and locality_ladder.csv")
    print("DONE_LADDER")


if __name__ == "__main__":
    main()
