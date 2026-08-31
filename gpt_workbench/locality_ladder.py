#!/usr/bin/env python3
"""
GEOMETRY/FEATURE-ONLY locality-ladder diagnostic + exact 54-row singleton table.
STRICTLY geometry + physical features + graph combinatorics. NO address values, NO targets, NO
LDOS, NO beta, NO study dynamics. Design-only; not part of the scientific record until reviewed.

Sol 3rd-pass REPRODUCIBILITY REPAIR (this file). Fixes, in order of Sol's list:
 1. STABLE SEED REGISTRY. Every RNG is addressed by an explicit key tuple through `rng(*key)`,
    seeded by blake2b(SEED_ROOT | key) -> int. Python's salted built-in hash() is used NOWHERE
    (neither for seeds nor for motif keys). Reproducible across processes and machines.
 2. REAL lambda SWEEP {0.25, 0.5, 1.0, 2.0}, executed in code, written to locality_final.csv.
 3. REPLICATED, PAIRED unrestricted derangements: for each rep b, the same rep index drives BOTH
    the constrained DW matching and an unrestricted within-motif derangement; the locality ratio is
    formed per-rep (paired) then aggregated over reps. (No single reference draw.)
 4. FROZEN INFEASIBILITY POLICY for groups with no perfect assignment at k=32 (~1.4% of movable
    vertices). NO silent dropping. Policy A (FROZEN, matches conditional-null manifest s3):
    deterministic escalation k=32 -> 64 -> full same-motif group (a derangement always exists at
    full for group size >=2). Policy B (reported for contrast): hold such groups as fixed points
    (non-permutable, like singletons). Both are computed and reported.
 5. `partner_turnover`: mean over consecutive rep pairs of the fraction of movable vertices assigned
    a DIFFERENT partner between the two repetitions (renamed from the old ambiguous "dest-change").
 6. FINAL CANDIDATE confirmed with REPS_FINAL = 40 stable-seeded repetitions.
 7. ABSOLUTE standardized move distances (median / p95 / max) AND paired ratios, with the
    aggregation rule stated explicitly (see AGGREGATION below).
 8. FEATURES reconciled EXACTLY to the conditional-null manifest M3 continuous physical family:
    [dens=g(2.0), deg, g(1.6), g(2.6), g(4.0), g(6.0), psi_N, psi_{N/2}, psi_{2N}] (9 features).
    Edge-length moments are excluded (degenerate on unit-rhombus edges, physical manifest s3); the
    motif one-hot is excluded (constant within an exact-motif group). `dens` is transport_run.py's
    gcount(2.0); the earlier script's "g(2.0)" was exactly this and is renamed for clarity.
 9. AGGREGATION (removes pooled-vs-patch ambiguity). Within a (patch, rep): pool the standardized
    move distances over ALL movable vertices, take median/p95/max -> per-rep patch stats. Across the
    40 reps (within a patch): take the median of each -> per-patch stats (the CSV rows). The report's
    HEADLINE across patches is the nested median: median over the 6 offsets, then over the 7 configs
    (the M_perm,7 construction); a pooled-over-all-42-patches figure is reported alongside, labelled.

Outputs: singleton_54.csv (Part A), locality_ladder.csv (Part B k-ladder), locality_final.csv
(Part C: 40-rep lambda-sweep final candidate with policy A/B, absolute + paired-ratio stats).
"""
import sys, hashlib
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
LAMBDAS = [0.25, 0.5, 1.0, 2.0]      # Sol item 2: real, committed sweep
KFINAL = 32
REPS_LADDER = 12                     # diagnostic context for the k-ladder feasibility table
REPS_FINAL = 40                      # Sol item 6: final-candidate confirmation
ESCALATION = [32, 64, "full"]        # Sol item 4, Policy A (frozen)
BIG = 1e6
OUT = __file__.rsplit("/", 1)[0]

# ----- Sol item 1: explicit stable seed registry (no salted hash()) --------------------------------
SEED_ROOT = 20260829                 # locality-ladder RNG root (documented)
def _seed(*key):
    payload = "|".join(repr(x) for x in (SEED_ROOT, *key)).encode()
    return int.from_bytes(hashlib.blake2b(payload, digest_size=16).digest(), "big")
def rng(*key):
    return np.random.default_rng(_seed(*key))


def hull_depth(P):
    h = ConvexHull(P); A, b = h.equations[:, :-1], h.equations[:, -1]
    return -(P @ A.T + b).max(1)


def features(N, ext, off):
    """Reconciled M3 continuous physical family (Sol item 8), standardised on the r16 common set."""
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
    # canonical motif key = sorted multiset of incident (star-line, sign) — EXACT tuple, not hash()
    mk = []
    for i in range(n):
        sig = []
        for k, s in enumerate(star):
            for sgn in (1, -1):
                if tuple(lifts[i] + sgn * s) in idx:
                    sig.append((k, sgn))
        mk.append(tuple(sorted(sig)))
    tree = cKDTree(par)
    def g(r): return np.array(tree.query_ball_point(par, r, return_length=True), float)
    dens = g(2.0)                                        # transport_run.py: dens = gcount(2.0)
    psi = {}
    for nn in (N, N // 2, 2 * N):
        v = np.zeros(n)
        for i in range(n):
            if adj[i]:
                a = np.array(adj[i])
                th = np.arctan2(par[a, 1] - par[i, 1], par[a, 0] - par[i, 0])
                v[i] = abs(np.mean(np.exp(1j * nn * th)))
        psi[nn] = v
    # EXACT reconciled feature order: dens, deg, g(1.6), g(2.6), g(4.0), g(6.0), psi_N, psi_{N/2}, psi_{2N}
    F = np.column_stack([dens, deg, g(1.6), g(2.6), g(4.0), g(6.0), psi[N], psi[N // 2], psi[2 * N]])
    Fr = F[r16]
    Fr = (Fr - Fr.mean(0)) / np.where(Fr.std(0) > 1e-12, Fr.std(0), 1.0)
    return Fr, [mk[i] for i in r16], len(r16)


def groups_ge2(mk):
    g = {}
    for loc, key in enumerate(mk):
        g.setdefault(key, []).append(loc)
    return [np.array(v) for v in g.values() if len(v) >= 2], sum(1 for v in g.values() if len(v) == 1)


def cand_edges(X, k):
    """k nearest same-group physical-feature neighbours (self excluded). k='full' => complete."""
    m = len(X)
    if k == "full":
        E = [[b for b in range(m) if b != a] for a in range(m)]
        D = [[float(np.linalg.norm(X[a] - X[b])) for b in range(m) if b != a] for a in range(m)]
        return E, D
    kk = min(k, m - 1)
    dist, nbr = cKDTree(X).query(X, k=kk + 1)
    E = [[] for _ in range(m)]; D = [[] for _ in range(m)]
    for a in range(m):
        for c in range(kk + 1):
            b = int(nbr[a][c])
            if b != a:
                E[a].append(b); D[a].append(float(dist[a][c]))
    return E, D


def assign(E, D, r, law, lam):
    """min-cost perfect derangement in the candidate graph; None if none exists."""
    m = len(E); C = np.full((m, m), BIG)
    for a in range(m):
        for b, dd in zip(E[a], D[a]):
            C[a, b] = r.random() if law == 'U' else dd + lam * r.random()
    rows, cols = linear_sum_assignment(C)
    if C[rows, cols].max() >= BIG:
        return None
    p = np.empty(m, int); p[rows] = cols; return p


def feasible_at(E):
    """Structural feasibility: does a perfect derangement exist in candidate graph E? (rng-free)"""
    m = len(E); C = np.full((m, m), BIG)
    for a in range(m):
        for b in E[a]:
            C[a, b] = 1.0
    rows, cols = linear_sum_assignment(C)
    return C[rows, cols].max() < BIG


def unrestricted_derangement(gi_len, r):
    """within-motif derangement over ALL same-motif vertices (no candidate-graph restriction)."""
    pp = r.permutation(gi_len)
    while gi_len > 1 and np.any(pp == np.arange(gi_len)):
        pp = r.permutation(gi_len)
    return pp


# ---------------------------------------------------------------------------------------------------
def run_ladder(fl, cache):
    """Part B: reproducible k-ladder feasibility + diversity (REPS_LADDER)."""
    for name, N, ext in ALL:
        if (name, ext) not in FEASIBLE:
            continue
        for off in OFFS:
            Fr, mk, n16 = cache[(name, ext, off)]
            grps, _ = groups_ge2(mk)
            movable = int(sum(len(g) for g in grps))
            for k in KLAD:
                for law in ('U', 'DW'):
                    feas_mov = 0; fail = 0; reps_perm = []; con = []
                    for gi in grps:
                        E, D = cand_edges(Fr[gi], k)
                        if not feasible_at(E):
                            fail += 1
                            continue
                        feas_mov += len(gi)
                        greps = []
                        for b in range(REPS_LADDER):
                            r = rng(name, ext, off, k, law, 1000, b, "ladder")
                            p = assign(E, D, r, law, 1.0)
                            greps.append(gi[p])
                            con.extend(np.linalg.norm(Fr[gi] - Fr[gi[p]], axis=1))
                        reps_perm.append(np.array(greps))
                    if reps_perm:
                        full = np.stack([np.concatenate([rp[b] for rp in reps_perm])
                                         for b in range(REPS_LADDER)])
                        distinct = len({tuple(x) for x in full}) / REPS_LADDER
                        turnover = float(np.mean([(full[b] != full[b + 1]).mean()
                                                  for b in range(REPS_LADDER - 1)]))
                    else:
                        distinct = turnover = 0.0
                    con = np.array(con) if con else np.array([0.0])
                    fl.write(f"{name},{ext},{off[0]},{off[1]},{k},{law},"
                             f"{feas_mov/max(movable,1):.4f},{fail/max(len(grps),1):.4f},"
                             f"{distinct:.3f},{turnover:.4f},{np.median(con):.4f},"
                             f"{np.percentile(con,95):.4f},{con.max():.4f}\n")
            fl.flush()
            print(f"   ladder {name} e{ext} off{off} done", flush=True)


def run_final(ff, cache):
    """Part C: 40-rep lambda-sweep at k=32 with policy A/B, absolute + paired-ratio locality."""
    for name, N, ext in ALL:
        if (name, ext) not in FEASIBLE:
            continue
        for off in OFFS:
            Fr, mk, n16 = cache[(name, ext, off)]
            grps, _ = groups_ge2(mk)
            movable = int(sum(len(g) for g in grps))
            # ---- policy A: freeze k_used per group by deterministic escalation (Sol item 4) ----
            group_k = []; escalated = 0; feas32 = 0
            for gi in grps:
                E32, _ = cand_edges(Fr[gi], KFINAL)
                if feasible_at(E32):
                    group_k.append(KFINAL); feas32 += len(gi); continue
                ku = None
                for kk in ESCALATION[1:]:                       # 64, then full
                    E, _ = cand_edges(Fr[gi], kk)
                    if feasible_at(E):
                        ku = kk; break
                group_k.append(ku if ku is not None else "full")
                escalated += len(gi)
            frac_esc = escalated / max(movable, 1)
            movable_feasible_A = 1.0                            # escalation guarantees feasibility
            movable_feasible_B = feas32 / max(movable, 1)       # hold-fixed leaves escalated as fixed
            for lam in LAMBDAS:
                for policy in ("A", "B"):
                    # per-rep pooled absolute stats + per-rep paired ratio (Sol items 3,5,7,9)
                    con_med = []; con_p95 = []; con_max = []
                    unc_med = []; unc_p95 = []; unc_max = []
                    ratio_med = []; ratio_p95 = []
                    turn_accum = []
                    prev_full = None
                    for b in range(REPS_FINAL):
                        cvals = []; uvals = []; dest = []
                        for gi, ku in zip(grps, group_k):
                            if policy == "B" and ku != KFINAL:
                                # held fixed: contributes zero-move vertices to neither stat pool
                                dest.extend(list(gi)); continue
                            E, D = cand_edges(Fr[gi], ku)
                            rc = rng(name, ext, off, KFINAL, "DW", int(lam * 1000), b, policy, "con")
                            p = assign(E, D, rc, "DW", lam)
                            cvals.extend(np.linalg.norm(Fr[gi] - Fr[gi[p]], axis=1))
                            dest.extend(list(gi[p]))
                            # paired unrestricted derangement, same rep index b
                            ru = rng(name, ext, off, KFINAL, "UNR", int(lam * 1000), b, policy, "unr")
                            pp = unrestricted_derangement(len(gi), ru)
                            uvals.extend(np.linalg.norm(Fr[gi] - Fr[gi[pp]], axis=1))
                        cvals = np.array(cvals) if cvals else np.array([0.0])
                        uvals = np.array(uvals) if uvals else np.array([0.0])
                        con_med.append(np.median(cvals)); con_p95.append(np.percentile(cvals, 95))
                        con_max.append(cvals.max())
                        unc_med.append(np.median(uvals)); unc_p95.append(np.percentile(uvals, 95))
                        unc_max.append(uvals.max())
                        ratio_med.append(np.median(cvals) / max(np.median(uvals), 1e-9))
                        ratio_p95.append(np.percentile(cvals, 95) / max(np.percentile(uvals, 95), 1e-9))
                        dest = np.array(dest)
                        if prev_full is not None:
                            turn_accum.append(float((dest != prev_full).mean()))
                        prev_full = dest
                    mf = movable_feasible_A if policy == "A" else movable_feasible_B
                    ff.write(f"{name},{ext},{off[0]},{off[1]},{lam},{policy},{mf:.4f},{frac_esc:.4f},"
                             f"{np.mean(turn_accum):.4f},"
                             f"{np.median(con_med):.4f},{np.median(con_p95):.4f},{np.median(con_max):.4f},"
                             f"{np.median(unc_med):.4f},{np.median(unc_p95):.4f},{np.median(unc_max):.4f},"
                             f"{np.median(ratio_med):.4f},{np.median(ratio_p95):.4f},{REPS_FINAL}\n")
            ff.flush()
            print(f"   final {name} e{ext} off{off} done (esc={frac_esc:.4f})", flush=True)


def main():
    # Features computed ONCE per patch (geometry-only), reused across parts A/B/C.
    cache = {}
    with open(OUT + "/singleton_54.csv", "w") as fs:
        fs.write("family,extent,offx,offy,r16,n_singleton,singleton_frac,n_groups_ge2\n")
        for name, N, ext in ALL:
            for off in OFFS:
                Fr, mk, n16 = features(N, ext, off)
                cache[(name, ext, off)] = (Fr, mk, n16)
                grps, nsingle = groups_ge2(mk)
                fs.write(f"{name},{ext},{off[0]},{off[1]},{n16},{nsingle},{nsingle/n16:.5f},{len(grps)}\n")
                fs.flush()
        print("wrote singleton_54.csv (features cached)", flush=True)
    # Part B — reproducible k-ladder
    with open(OUT + "/locality_ladder.csv", "w") as fl:
        fl.write("family,extent,offx,offy,k,law,movable_feasible_frac,groups_fail_frac,"
                 "distinct_frac,partner_turnover,abs_med,abs_p95,abs_max\n")
        print("# k-ladder (reproducible seeds, REPS=%d)" % REPS_LADDER, flush=True)
        run_ladder(fl, cache)
    # Part C — 40-rep lambda-sweep final candidate
    with open(OUT + "/locality_final.csv", "w") as ff:
        ff.write("family,extent,offx,offy,lambda,policy,movable_feasible_frac,frac_escalated,"
                 "partner_turnover,abs_con_med,abs_con_p95,abs_con_max,abs_unc_med,abs_unc_p95,"
                 "abs_unc_max,ratio_med_paired,ratio_p95_paired,reps\n")
        print("# final candidate k=32 lambda-sweep (REPS=%d, paired unrestricted)" % REPS_FINAL, flush=True)
        run_final(ff, cache)
    print("DONE_LADDER", flush=True)


if __name__ == "__main__":
    main()
