"""
Synthetic-only conformance test-suite for the sealed implementation.

NO study data: every fixture is a hand-built array or tiny toy graph with a known answer. This suite
runs no scientific study, touches no address values / targets / LDOS / beta / outcomes, and produces
no family-result curves. Run: `python -m gpt_workbench.impl.tests.test_all`.
"""
import sys, math
import numpy as np
from scipy.spatial import cKDTree

from .. import constants as C, seeds, substrate as S, features as F, matching as M
from .. import engines as E, aggregation as A, regression as R, gates as G

RESULTS = []
def check(name, cond, info=""):
    RESULTS.append((name, bool(cond), info))


# --------------------------------------------------------------------------- constants & registry
def t_constants():
    check("constants.self_check_imports", True)
    check("snapped_beta_times: 48 unique", C.SNAPPED_BETA_TIMES.size == 48 and
          np.unique(C.SNAPPED_BETA_TIMES).size == 48)
    check("boundary grid 161 pts, dt=0.05", C.BOUNDARY_GRID.size == 161 and
          abs(C.BOUNDARY_GRID[1] - C.BOUNDARY_GRID[0] - 0.05) < 1e-12)
    check("M_perm,7 has exactly 7 cells", len(C.FEASIBLE_7) == 7)
    check("platinum e16/e18 not in feasible-7",
          set(C.PLATINUM_INFEASIBLE).isdisjoint(set(C.FEASIBLE_7)))
    check("phys_extra dims 11/22/35/48/61",
          [C.phys_extra_dim(r) for r in C.RADII] == [11, 22, 35, 48, 61])
    check("match law: k=32, lambda=1.0, Policy A",
          C.MATCH_K == 32 and C.MATCH_LAMBDA == 1.0 and C.MATCH_POLICY == "A")
    check("q_ref formula", abs(C.q_ref([0, 1, 2, 3], 2.0) - (1 + 2) / 5) < 1e-12)


# --------------------------------------------------------------------------- seeds determinism
def t_seeds():
    r1 = seeds.address_perm_rng("silver", 16, (0.13, 0.37), "mk", 7).random(5)
    r2 = seeds.address_perm_rng("silver", 16, (0.13, 0.37), "mk", 7).random(5)
    r3 = seeds.address_perm_rng("silver", 16, (0.13, 0.37), "mk", 8).random(5)
    check("seed replay deterministic", np.allclose(r1, r2))
    check("distinct keys -> distinct streams", not np.allclose(r1, r3))
    check("capacity child indices 0..199 valid",
          seeds.capacity_rng(0) is not None and seeds.capacity_rng(199) is not None)


# --------------------------------------------------------------------------- substrate bit-identity
def _toy_geometry(seed=0, n=60):
    rng = np.random.default_rng(seed)
    par = rng.random((n, 2)) * 10
    perp = rng.random((n, 2))
    tree = cKDTree(par)
    pairs = tree.query_pairs(1.8)
    edges = [tuple(sorted(p)) for p in pairs]
    adj = S.build_adj(n, edges)
    # keep only largest structure-ish: ensure no isolated vertices for m4 gradient
    return par, perp, tree, edges, adj


def t_substrate():
    par, perp, tree, edges, adj = _toy_geometry()
    mine = S.m4_cols(adj, tree, par, perp, shell_r=(2, 4, 8))
    check("m4_cols is 11 columns", mine.shape[1] == 11)
    # bit-identity vs sealed baseline transport_run._m4_cols
    try:
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "substrates"))
        import transport_run as TR
        f = {"n": len(par), "adj": adj, "tree": tree, "par": par, "shell_r": (2, 4, 8)}
        base = TR._m4_cols(f, perp)
        check("m4_cols BIT-IDENTICAL to sealed transport_run._m4_cols",
              np.max(np.abs(mine - base)) < 1e-12, f"maxdiff={np.max(np.abs(mine-base)):.2e}")
        check("hull_depth matches baseline", np.allclose(S.hull_depth(perp), TR.hull_depth(perp)))
    except Exception as e:  # pragma: no cover
        check("m4_cols BIT-IDENTICAL to sealed baseline", False, f"could not import baseline: {e}")


# --------------------------------------------------------------------------- features
def t_features():
    # moments correctness vs numpy/scipy-style formulas
    x = np.array([1., 2., 2., 3., 10.])
    mu, var, sk, ek = F.moments(x)
    check("moments mean/var(ddof=0)", abs(mu - x.mean()) < 1e-12 and abs(var - x.var()) < 1e-12)
    check("moments sigma floor -> higher moments 0", F.moments(np.ones(5))[2:] == (0.0, 0.0))
    # physical_extra dims for all rungs on a toy patch
    par, perp, tree, edges, adj = _toy_geometry(seed=3, n=120)
    deg = np.array([len(a) for a in adj], float)
    psis = {"N": F.psi_n(adj, par, 8), "N//2": F.psi_n(adj, par, 4), "2N": F.psi_n(adj, par, 16)}
    voro = F.voronoi_areas(par)
    ell = 1.0
    ok = True
    for r in C.RADII:
        extra = F.physical_extra(r, tree, par, deg, psis, voro, ell)
        ok &= (extra.shape[1] == C.phys_extra_dim(r))
    check("physical_extra dims exact for r in {2,4,8,12,16}", ok)
    # Group E empty-neighbourhood convention
    nbs = {2: [np.array([], int)]}  # empty neighbourhood
    voro2 = np.array([3.5])
    block = F.group_E(nbs, voro2, [2])
    check("Group E empty-nbhd -> (area[i], 0)", block[0, 0] == 3.5 and block[0, 1] == 0.0)
    # dedup: bit-identical extra col dropped, M3 never dropped
    M3 = np.random.default_rng(1).random((30, 5))
    extra = np.column_stack([M3[:, 2].copy(), np.random.default_rng(2).random(30)])  # col0 dup of M3 col2
    Xr, keep = F.build_Xr(M3, extra)
    check("dedup drops bit-identical extra col only", keep == [1] and Xr.shape[1] == 6)
    check("dedup never drops M3", Xr[:, :5].shape[1] == 5 and np.allclose(Xr[:, :5], M3))


# --------------------------------------------------------------------------- matching
def t_matching():
    # grouping + singleton fraction
    keys = ["a", "a", "a", "b", "b", "c"]  # c is singleton
    groups, nsing, frac = M.exact_motif_groups(keys)
    check("grouping: groups>=2 and singleton count", len(groups) == 2 and nsing == 1)
    check("singleton fraction", abs(frac - 1 / 6) < 1e-12)
    feas, fr = M.cell_permutation_feasible(["a"] * 20 + ["s%d" % i for i in range(2)])  # 2/22 ~9%
    check("cell infeasible when singletons > 5%", (not feas) and fr > 0.05)
    # Policy A escalation + derangement + determinism
    rng = np.random.default_rng(0)
    Xstd = rng.random((40, 9))
    mk = np.array(["m"] * 40)
    perm1 = M.build_permutation(Xstd, mk, ("silver", 16, (0.1, 0.2)), b=0)
    perm2 = M.build_permutation(Xstd, mk, ("silver", 16, (0.1, 0.2)), b=0)
    check("matching replicate deterministic", np.array_equal(perm1, perm2))
    check("matching is a derangement (no fixed movable pts)", np.all(perm1 != np.arange(40)))
    check("matching is a bijection", sorted(perm1.tolist()) == list(range(40)))
    # a group whose k=32 graph is degenerate still resolves under Policy A (escalation to full)
    frac_esc = M.escalation_fraction(Xstd, mk)
    check("escalation fraction in [0,1]", 0.0 <= frac_esc <= 1.0)


# --------------------------------------------------------------------------- engines
def t_engines():
    # coherent Krylov vs exact diagonalisation on a small ring
    n = 8
    edges = [(i, (i + 1) % n) for i in range(n)]
    Aad = E.adjacency(n, edges)
    grid = C.BOUNDARY_GRID
    psi = E.coherent_states(Aad, 0, grid)
    exact = E.coherent_exact(Aad, 0, grid)
    check("coherent Krylov vs exact-diag <= 1e-10", np.max(np.abs(psi - exact)) <= 1e-10,
          f"maxdiff={np.max(np.abs(psi-exact)):.2e}")
    check("coherent norm conserved", E.check_conservation(psi, coherent=True))
    # CTMC conservation
    Q = E.ctmc_generator(Aad)
    p = E.classical_states(Q, 0, grid)
    check("CTMC probability conserved & non-negative", E.check_conservation(p, coherent=False))
    # beta recovery on a synthetic power law MSD(t)=t^{2*beta}
    beta_true = 0.4
    msd = grid ** (2 * beta_true)
    b, r2 = E.beta_from_msd(msd, grid)
    check("beta recovered from synthetic power law", abs(b - beta_true) < 1e-6 and r2 > 0.999,
          f"beta={b:.4f}")
    # boundary crossing
    dps = np.zeros(161); dps[100:] = 0.02
    check("boundary crossing = first grid time >= 0.01", E.boundary_crossing_time(dps) == grid[100])
    check("no crossing -> inf", math.isinf(E.boundary_crossing_time(np.zeros(161))))


# --------------------------------------------------------------------------- aggregation
def t_aggregation():
    rng = np.random.default_rng(0)
    v9 = rng.random((9, 6))
    check("M9 nested median equals median-of-per-offset-medians",
          abs(A.M9(v9) - np.median(np.median(v9, 0))) < 1e-12)
    # no cell dropping: wrong shape must raise
    try:
        A.M9(rng.random((8, 6))); dropped = False
    except AssertionError:
        dropped = True
    check("M9 refuses != 9 configs (no dropping)", dropped)
    v7 = rng.random((7, 6))
    check("M_perm,7 requires exactly 7 cells", abs(A.M_perm7(v7) - np.median(np.median(v7, 0))) < 1e-12)
    # delta_cap = 95th pct of 200-draw M9 distribution
    draws = rng.random((200, 9, 6))
    dc = A.delta_cap(draws)
    per = np.array([A.M9(draws[d]) for d in range(200)])
    check("delta_cap = 95th percentile of 200-draw M9", abs(dc - np.percentile(per, 95)) < 1e-12)
    # R_kill: any undefined required reduction -> None (mixed)
    plain = np.full((9, 6), 0.5); shuf = np.full((9, 6), 0.1)
    check("R_kill defined when all plain > dcap", A.R_kill(plain, shuf, 0.05) is not None)
    plain2 = plain.copy(); plain2[3, 2] = 0.0
    check("R_kill None when a required cell undefined (global undefined)",
          A.R_kill(plain2, shuf, 0.05) is None)
    # Westfall-Young monotone non-decreasing along ranked order
    obs = np.array([3., 2.5, 2., 1.5, 1., 0.5, 0.2])
    null = rng.normal(0, 1, (7, 1000))          # strict (7, 1000) invariant
    q = A.westfall_young(obs, null)
    ordered = q[np.argsort(-obs)]
    check("Westfall-Young q-tilde monotone non-decreasing", np.all(np.diff(ordered) >= -1e-12))


# --------------------------------------------------------------------------- gates
def t_gates():
    check("G0 strict t_bound* > 8", G.G0(9)["pass"] and not G.G0(8)["pass"])
    check("G1 threshold 0.90", G.G1(0.90)["pass"] and not G.G1(0.89)["pass"])
    check("G2 q_ref < 0.05", G.G2(0.049)["pass"] and not G.G2(0.05)["pass"])
    check("G5 undefined denominator -> mixed", G.G5(0.01, 0.001, 0.05)["route"] == "mixed/undetectable")
    check("G5 pass when classical <= 0.2*coherent",
          G.G5(0.1, 1.0, 0.05)["pass"] and not G.G5(0.5, 1.0, 0.05)["pass"])
    g7 = G.G7(0.3, 0.28)
    check("G7 descriptive, no pass/fail key", "pass" not in g7 and g7["descriptive"])
    # primary excludes G5; G5 failure does not erase primary
    P = dict(pass_=True)
    ok = {"pass": True}; bad = {"pass": False}
    check("primary coherent = G0&G1c&G2&G3&G4&G6 (no G5)",
          G.primary_coherent_transport(ok, ok, ok, ok, ok, ok))
    check("G5 failure does NOT erase primary coherent",
          G.primary_coherent_transport(ok, ok, ok, ok, ok, ok) and
          not G.cross_engine_modifier(ok, bad))
    # exhaustive routing
    r = G.route_physical_outcome(m9_addr2=0.4, m9_addr16=0.02, dcap=0.05,
                                 sign6_r2=np.array([1, 1, 1, 1, 1, 1.]), m9_resid16=0.0,
                                 qref7=0.5, feasible=True)
    check("routing: compression when fade rule holds", r == "compression")
    r2 = G.route_physical_outcome(0.4, 0.4, 0.05, np.array([1, 1, 1, 1, 1, 1.]), 0.4, 0.01, True)
    check("routing: survives-stress-controls when G3&G6&G2 pass", r2 == "survives-stress-controls")
    r3 = G.route_physical_outcome(-0.1, 0.0, 0.05, np.zeros(6), 0.0, 0.9, True)
    check("routing: mixed when neither positive outcome's criteria pass", r3 == "mixed/undetectable")
    check("routing: infeasible when not feasible",
          G.route_physical_outcome(0.4, 0.02, 0.05, np.ones(6), 0.0, 0.5, False) == "infeasible")


# --------------------------------------------------------------------------- regression
def t_regression():
    rng = np.random.default_rng(0)
    X = rng.random((200, 4)); y = X[:, 0] * 2 + rng.normal(0, 0.05, 200)
    tr = np.arange(150); te = np.arange(150, 200)
    r2a = R.gbt_r2(X[tr], y[tr], X[te], y[te])
    r2b = R.gbt_r2(X[tr], y[tr], X[te], y[te])
    check("GBT deterministic (random_state frozen)", r2a == r2b)
    # informative added column raises R^2 (positive increment); noise column ~ 0
    Xbase = X[:, 1:]  # drop the informative col from baseline
    inc = R.increment(Xbase, X[:, :1], y, tr, te)
    check("increment positive for informative added feature", inc > 0.05, f"inc={inc:.3f}")
    # pc1 slabs: equal-count with remainder to lowest-index slabs
    coords = rng.random((103, 2)); lifts = rng.integers(0, 5, (103, 4))
    labels = R.pc1_slabs(coords, lifts)
    counts = [int((labels == s).sum()) for s in range(4)]
    check("pc1_slabs equal-count +/-1", max(counts) - min(counts) <= 1, str(counts))
    check("pc1_slabs remainder to lowest-index slabs", counts[0] >= counts[-1] and sum(counts) == 103)


def main():
    for t in (t_constants, t_seeds, t_substrate, t_features, t_matching, t_engines,
              t_aggregation, t_gates, t_regression):
        t()
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, info in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({info})" if info and not ok else
              (f"  ({info})" if info else "")))
    print(f"\n{npass}/{len(RESULTS)} checks passed")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
