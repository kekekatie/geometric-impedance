"""
Synthetic-only tests for the executable WORKFLOWS (workflows.py, msd.py, production geometry).

NO study data. Every fixture is hand-built with a known answer. A deterministic OLS surrogate drives
the orchestration where an exact/known result is required; a subset also runs the real frozen HGBR to
prove integration. Run: `python -m gpt_workbench.impl.tests.test_workflows`.
"""
import sys
import numpy as np
from scipy.spatial import cKDTree

from .. import constants as C, workflows as W, msd as MSD, substrate as S, aggregation as A, gates as G
from ..regression import make_regressor, gbt_r2

RESULTS = []
def check(name, cond, info=""):
    RESULTS.append((name, bool(cond), info));
def note(name, info=""):
    RESULTS.append((name, True, info))


# ---- deterministic surrogate regressor / R^2 (fast, exact, for known-answer orchestration) ------
class OLSReg:
    def fit(self, X, y):
        Xd = np.column_stack([X, np.ones(len(X))]); self.c = np.linalg.lstsq(Xd, y, rcond=None)[0]; return self
    def predict(self, X):
        return np.column_stack([X, np.ones(len(X))]) @ self.c

def ols_r2(Xtr, ytr, Xte, yte):
    p = OLSReg().fit(Xtr, ytr).predict(Xte)
    ss = np.sum((yte - p) ** 2); st = np.sum((yte - yte.mean()) ** 2)
    return 1 - ss / st if st > 0 else 0.0


# ---- synthetic patch / dataset builder ----------------------------------------------------------
def _toy_graph(n, seed):
    rng = np.random.default_rng(seed)
    par = rng.random((n, 2)) * 6
    tree = cKDTree(par)
    edges = [tuple(sorted(p)) for p in tree.query_pairs(2.2)]
    adj = S.build_adj(n, edges)
    return par, tree, edges, adj


def make_patch(seed, n=18, addr_signal=0.0, capture16=False, infeasible=False):
    """capture16=True: X_r(16) already contains the address signal (so address adds nothing at r=16),
    while X_r(2) does not (address adds at r=2) -> a genuine radius-fade for the compression route."""
    rng = np.random.default_rng(seed)
    par, tree, edges, adj = _toy_graph(n, seed)
    Xbase = rng.normal(size=(n, 4))
    addr_raw = rng.normal(size=(n, 2))
    addr = S.m4_cols(adj, tree, par, addr_raw, shell_r=C.SHELL_R_M4)
    # address signal orthogonalised to Xbase (the part "beyond X_r(2)")
    a_sig = addr[:, 0] - np.column_stack([Xbase, np.ones(n)]) @ np.linalg.lstsq(
        np.column_stack([Xbase, np.ones(n)]), addr[:, 0], rcond=None)[0]
    y = Xbase[:, 0] * 1.0 + addr_signal * a_sig + rng.normal(0, 0.05, n)
    Xr2 = Xbase
    Xr16 = np.column_stack([Xbase, a_sig]) if capture16 else Xbase   # r16 captures address iff fade
    shuf = S.m4_cols(adj, tree, par, addr_raw[rng.permutation(n)], shell_r=C.SHELL_R_M4)
    # motif keys: two big groups; add singletons if infeasible
    keys = np.array(["m0"] * (n // 2) + ["m1"] * (n - n // 2), dtype=object)
    if infeasible:
        keys[:max(1, int(0.1 * n))] = [f"s{i}" for i in range(max(1, int(0.1 * n)))]  # >5% singletons
    slab = np.array([i % C.N_SLABS for i in range(n)])
    Xr = {2: Xr2, 16: Xr16}
    from ..matching import cell_permutation_feasible
    feas = cell_permutation_feasible(keys)[0]
    return {"Xr": Xr, "y": y, "address": addr, "address_raw": addr_raw, "shuf_address": shuf,
            "degree": np.array([len(a) for a in adj], float),
            "voro_area": np.abs(rng.normal(1.0, 0.2, n)),
            "geom": {"adj": adj, "tree": tree, "par": par}, "motif_keys": keys, "slab": slab,
            "match_feat": rng.normal(size=(n, 9)), "feasible": feas}


def make_config(base_seed, **kw):
    return {off: make_patch(base_seed * 100 + i, **kw) for i, off in enumerate(C.OFFSETS)}


def make_dataset(addr_signal=0.0, capture16=False, platinum_infeasible=True, n=18):
    ds = {}
    for k, (fam, N, ext) in enumerate(C.CONFIGS_9):
        inf = platinum_infeasible and (fam == "platinum" and ext in (16, 18))
        ds[(fam, ext)] = make_config(k + 1, n=n, addr_signal=addr_signal, capture16=capture16, infeasible=inf)
    return ds


# ---- residual leakage-safety (the crux) ---------------------------------------------------------
def t_residual_leakage():
    cfg = make_config(7, addr_signal=1.0)
    d0, internals0 = W.residual_increment(cfg, 16, r2_fn=ols_r2, reg_factory=OLSReg, return_internals=True)
    # perturb HELD-OUT values only (y and address of the held-out offset in each fold's view)
    cfg2 = {o: dict(p) for o, p in cfg.items()}
    victim = C.OFFSETS[0]
    cfg2[victim] = dict(cfg[victim]); cfg2[victim]["y"] = cfg[victim]["y"] + 999.0
    cfg2[victim]["address"] = cfg[victim]["address"] + 5.0
    _, internals2 = W.residual_increment(cfg2, 16, r2_fn=ols_r2, reg_factory=OLSReg, return_internals=True)
    # In the fold where the victim IS held out, training rows exclude the victim, so their
    # cross-fitted residuals must be IDENTICAL despite the victim's held-out perturbation (no leakage).
    ok = np.allclose(internals0[victim]["Atr_res"], internals2[victim]["Atr_res"])
    # And the held-out residuals for that fold DO change (they legitimately use the held-out address).
    changed = not np.allclose(internals0[victim]["Ao_res"], internals2[victim]["Ao_res"])
    check("residual: training residuals invariant to held-out perturbation (no leakage)", ok and changed)
    # determinism
    d1 = W.residual_increment(cfg, 16, r2_fn=ols_r2, reg_factory=OLSReg)
    check("residual increment deterministic", np.allclose(d0, d1))
    check("residual increment is a 6-vector", d0.shape == (6,))


def t_parity_scaler_invariance():
    cfg = make_config(11, addr_signal=0.5)
    offs = list(cfg.keys()); o = offs[0]
    _, _, sc0 = W.parity_block(cfg, o, offs, return_scaler=True)
    cfg2 = {oo: dict(p) for oo, p in cfg.items()}
    cfg2[o] = dict(cfg[o]); cfg2[o]["degree"] = cfg[o]["degree"] + 1000.0
    cfg2[o]["voro_area"] = cfg[o]["voro_area"] * 50.0
    _, _, sc2 = W.parity_block(cfg2, o, offs, return_scaler=True)
    check("parity scaler (train-only) invariant to held-out change",
          np.allclose(sc0[0], sc2[0]) and np.allclose(sc0[1], sc2[1]))
    # zero-variance rule -> parity unavailable (None), capacity not substituted
    cfgz = make_config(12);
    for oo in cfgz:
        cfgz[oo]["degree"] = np.ones_like(cfgz[oo]["degree"]); cfgz[oo]["voro_area"] = np.ones_like(cfgz[oo]["voro_area"])
    btr, bo = W.parity_block(cfgz, list(cfgz)[0], list(cfgz))
    check("parity zero-variance -> unavailable (None)", btr is None and bo is None)


# ---- end-to-end orchestrator: predetermined routes ----------------------------------------------
def t_orchestrator_routes():
    # (a) survives-stress-controls: address carries real orthogonal signal; supply small dcap & qref
    ds = make_dataset(addr_signal=4.0, capture16=False, n=60)
    res = W.orchestrate(ds, r=16, r2_fn=ols_r2, reg_factory=OLSReg,
                        permutation={"qref": 0.001}, capacity=(1e-6, None), radius_pair=(2, 16))
    check("orchestrator: 9-config M9 computed (no dropping)", "M9_address" in res)
    check("orchestrator route = survives-stress-controls",
          res["route"] == "survives-stress-controls", res["route"])
    check("orchestrator G7 descriptive (no pass/fail)", "pass" not in res["gates"]["G7"])
    # (b) compression: address predicts at r=2 but is already captured by X_r at r=16 (fade)
    ds2 = make_dataset(addr_signal=4.0, capture16=True, n=60)
    res2 = W.orchestrate(ds2, r=16, r2_fn=ols_r2, reg_factory=OLSReg,
                         permutation={"qref": 0.5}, capacity=(0.02, None), radius_pair=(2, 16))
    check("orchestrator route = compression (fade rule)", res2["route"] == "compression", res2["route"])
    # (c) mixed: no address signal, high dcap
    ds3 = make_dataset(addr_signal=0.0, n=60)
    res3 = W.orchestrate(ds3, r=16, r2_fn=ols_r2, reg_factory=OLSReg,
                         permutation={"qref": 0.9}, capacity=(0.5, None), radius_pair=(2, 16))
    check("orchestrator route = mixed/undetectable when nothing passes",
          res3["route"] == "mixed/undetectable", res3["route"])
    # feasibility membership: exactly 7 feasible in the dataset
    feas = sum(1 for c in ds if ds[c][next(iter(ds[c]))]["feasible"])
    check("dataset has exactly 7 permutation-feasible configs", feas == 7, str(feas))


def t_orchestrator_real_hgbr():
    # prove the FROZEN HGBR integrates in the real workflows (one small config, all four increments)
    cfg = make_config(9, addr_signal=1.0)
    pl = W.plain_increment(cfg, 16, "address", r2_fn=gbt_r2)
    rr = W.residual_increment(cfg, 16, r2_fn=gbt_r2, reg_factory=make_regressor)
    pa = W.parity_increment(cfg, 16, r2_fn=gbt_r2)
    check("frozen HGBR: plain/residual/parity increments are 6-vectors",
          pl.shape == (6,) and rr.shape == (6,) and pa.shape == (6,))


# ---- capacity: exactly 200 draws -> delta_cap ---------------------------------------------------
def t_capacity():
    ds = make_dataset(addr_signal=0.3)
    dcap, per = W.capacity_delta_cap(ds, 16, block_dim=11, n_draws=200, r2_fn=ols_r2)
    check("capacity uses exactly 200 draws", per.size == 200)
    check("delta_cap = 95th percentile of 200 M9 values", abs(dcap - np.percentile(per, 95)) < 1e-12)
    dcap2, _ = W.capacity_delta_cap(ds, 16, 11, 200, ols_r2)
    check("delta_cap deterministic (keyed capacity seeds)", abs(dcap - dcap2) < 1e-12)
    try:
        W.capacity_delta_cap(ds, 16, 11, 100, ols_r2); raised = False
    except AssertionError:
        raised = True
    check("capacity refuses n_draws != 200", raised)


# ---- permutation stress: exactly B=1000, synchronized, q_ref -----------------------------------
def t_permutation_stress():
    # minimal feasible dataset (7 tiny configs) so B=1000 real matching runs in reasonable time
    feas = {}
    for k, (fam, ext) in enumerate(C.FEASIBLE_7):
        feas[(fam, ext)] = make_config(50 + k, n=8, addr_signal=0.6)   # tiny so B=1000 real matching is fast
    out = W.permutation_stress(feas, 16, B=1000, r2_fn=ols_r2)
    check("permutation obs_matrix shape (7,6)", out["obs_matrix"].shape == (7, 6))
    check("permutation null_Mperm7 length 1000", out["null_Mperm7"].size == 1000)
    check("permutation q_ref in (0,1]", 0 < out["qref"] <= 1.0)
    check("permutation obs_T7 shape (7,)", out["obs_T7"].shape == (7,))
    check("permutation null_T7 shape (7,1000)", out["null_T7"].shape == (7, 1000))
    # Westfall-Young consumes exactly (7,1000)
    q = A.westfall_young(out["obs_T7"], out["null_T7"])
    check("Westfall-Young over (7,1000) returns 7 q-tilde", q.shape == (7,))
    # B != 1000 raises
    try:
        W.permutation_stress(feas, 16, B=500, r2_fn=ols_r2); raised = False
    except AssertionError:
        raised = True
    check("permutation refuses B != 1000", raised)


# ---- MSD workload -------------------------------------------------------------------------------
def t_msd():
    # launch selection: 200 balanced across 4 slabs, deterministic
    n = 400
    rng = np.random.default_rng(0)
    slab = np.array([i % 4 for i in range(n)]); proj = rng.random(n); lifts = rng.integers(0, 7, (n, 4))
    sel = MSD.select_launches(slab, proj, lifts, L=200)
    check("select_launches returns 200", sel.size == 200)
    check("select_launches balanced 50/slab", all((slab[sel] == s).sum() == 50 for s in range(4)))
    check("select_launches deterministic", np.array_equal(sel, MSD.select_launches(slab, proj, lifts, 200)))
    # reduce-on-the-fly patch run + global crossing + per-engine median R2
    m = 20
    par2, tree2, edges2, adj2 = _toy_graph(m, 3)
    dbound = S.hull_depth(par2)
    launches = np.arange(min(6, m))
    pr = MSD.run_patch(edges2, par2, dbound, 1.0, launches, batch=50)
    check("run_patch returns per-engine beta/r2", len(pr["per_engine"]["coherent"]["beta"]) == len(launches))
    tstar = MSD.global_t_bound_star([pr])
    check("global t_bound* is finite or +inf", np.isfinite(tstar) or np.isinf(tstar))
    check("G0 uses t_bound* strictly (>8)", G.G0(9)["pass"] and not G.G0(tstar if tstar <= 8 else 7)["pass"])
    # beta failure route: nonpositive MSD at a snapped index
    msd = C.BOUNDARY_GRID ** 0.8; idx = int(np.argmin(np.abs(C.BOUNDARY_GRID - C.SNAPPED_BETA_TIMES[0])))
    msd[idx] = -1.0
    b, r2, st = MSD.beta_with_failure_route(msd)
    check("beta failure route on nonpositive MSD", np.isnan(b) and st == "nonpositive-MSD")
    # grid correspondence assertion
    C.assert_grid_correspondence(C.SNAPPED_BETA_TIMES)
    note("time-list/grid correspondence asserted (48 snapped points)")


# ---- production geometry wiring -----------------------------------------------------------------
def t_geometry():
    # padded super-patch: core points + a surrounding ring; restrict Voronoi to core with correspondence
    rng = np.random.default_rng(1)
    core = rng.random((30, 2)) * 4 + 3          # core in the middle
    ring = np.array([[x, y] for x in np.linspace(-2, 9, 12) for y in (-2, 9)] +
                    [[x, y] for y in np.linspace(-2, 9, 12) for x in (-2, 9)])
    allpts = np.vstack([core, ring])
    core_index = np.arange(len(core))
    areas = S.restrict_voronoi_to_core(allpts, core_index)
    check("padded Voronoi: all core cells bounded", not np.isnan(areas).any() and areas.shape == (30,))
    # Delta/ring param checks
    S.assert_pad_params(4, 3)
    try:
        S.assert_pad_params(3, 3); raised = False
    except AssertionError:
        raised = True
    check("assert_pad_params refuses Delta < 4", raised)
    # convergence
    ok_conv, rel = S.pad_convergence(areas, areas * (1 + 1e-9))
    check("pad convergence within 1e-6", ok_conv, f"rel={rel:.2e}")
    # floors
    try:
        S.assert_floors(399, [150, 150, 150, 150]); raised = False
    except AssertionError:
        raised = True
    check("assert_floors refuses r16 < 400", raised)
    S.assert_floors(581, [148, 150, 141, 142]); note("floors pass at r16>=400, slab>=100")


def main():
    for t in (t_residual_leakage, t_parity_scaler_invariance, t_orchestrator_routes,
              t_orchestrator_real_hgbr, t_capacity, t_permutation_stress, t_msd, t_geometry):
        t()
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, info in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({info})" if info else ""))
    print(f"\n{npass}/{len(RESULTS)} checks passed")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
