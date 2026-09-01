"""
Executable, leakage-safe analysis WORKFLOWS on SUPPLIED data objects (conditional-null v4.1 §2/§4;
physical v7 §4/§5/§6). There is deliberately NO study-data entry point: every function consumes
supplied arrays only. The synthetic test-suite feeds these with hand-built fixtures of known answer.

Data schema (all supplied by the caller; never generated here):
  dataset = { (family, extent): config_data, ... }   # exactly 9 configs
  config_data = { offset: patch, ... }                # exactly 6 offsets
  patch = {
    "Xr": {r: (n, dim) array},    "y": (n,) array,
    "address": (n, 11) array,     "address_raw": (n, 2) array,
    "shuf_address": (n, 11) array,          # sealed stratified-shuffle M4shuf (for G4)
    "classical_address": (n, 11) array,     # CTMC-engine address block (for G5), optional
    "degree": (n,), "voro_area": (n,),      # parity components
    "geom": {"adj":[...], "tree":cKDTree, "par":(n,2)},   # for _m4_cols recompute
    "motif_keys": (n,), "slab": (n,) in 0..3, "match_feat": (n, 9),
    "feasible": bool,                       # permutation feasibility (singletons <= 5%)
  }

Injection: `r2_fn` (default frozen gbt_r2) and `reg_factory` (default frozen HGBR) let tests drive
the ORCHESTRATION deterministically; production uses the frozen defaults.
"""
import numpy as np
from . import constants as C
from .regression import gbt_r2, make_regressor
from .substrate import m4_cols
from .aggregation import M9, M_perm7, R_kill
from . import gates as G


def _offsets(cfg):
    offs = list(cfg.keys())
    assert len(offs) == C.N_OFFSETS, f"a config must have exactly 6 offsets, got {len(offs)}"
    return offs


def _pool(cfg, offs, key, r=None):
    if r is None:
        return np.concatenate([cfg[o][key] for o in offs], axis=0)
    return np.concatenate([cfg[o]["Xr"][r] for o in offs], axis=0)


# --------------------------------------------------------------------------- plain increment
def plain_increment(cfg, r, block="address", r2_fn=gbt_r2):
    """Outer LOO plain increment DR2 = R2([X_r, block]) - R2(X_r) per held-out offset. 6-vector."""
    offs = _offsets(cfg)
    out = []
    for o in offs:
        tr = [t for t in offs if t != o]
        Xtr = _pool(cfg, tr, None, r); ytr = _pool(cfg, tr, "y"); Btr = _pool(cfg, tr, block)
        Xo = cfg[o]["Xr"][r]; yo = cfg[o]["y"]; Bo = cfg[o][block]
        base = r2_fn(Xtr, ytr, Xo, yo)
        aug = r2_fn(np.column_stack([Xtr, Btr]), ytr, np.column_stack([Xo, Bo]), yo)
        out.append(aug - base)
    return np.array(out)


# --------------------------------------------------------------------------- residual-orthogonal
def _crossfit_train_residuals(Xtr, Atr, slabtr, reg_factory):
    """Inner 4-slab cross-fit residuals for TRAINING rows: each row's prediction comes from a
    residualiser fitted on the OTHER slabs pooled across all training offsets (no leakage)."""
    P = np.zeros_like(Atr)
    for c in range(Atr.shape[1]):
        for j in range(C.N_SLABS):
            tr = slabtr != j; te = slabtr == j
            if te.sum() == 0 or tr.sum() == 0:
                continue
            reg = reg_factory().fit(Xtr[tr], Atr[tr, c])
            P[te, c] = reg.predict(Xtr[te])
    return Atr - P


def _outer_residualiser_apply(Xtr, Atr, Xo, Ao, reg_factory):
    """Outer residualiser trained on ALL training rows, applied ONCE to the unseen offset."""
    R = np.zeros_like(Ao)
    for c in range(Atr.shape[1]):
        reg = reg_factory().fit(Xtr, Atr[:, c])
        R[:, c] = Ao[:, c] - reg.predict(Xo)
    return R


def residual_increment(cfg, r, r2_fn=gbt_r2, reg_factory=make_regressor, return_internals=False):
    """Leakage-safe residual-orthogonal address increment at radius r. 6-vector.
    Six outer LOO folds; four simultaneous PCA-slab inner folds across the five training offsets;
    cross-fitted training residuals; outer residualiser applied once to the unseen offset."""
    offs = _offsets(cfg)
    out = []; internals = {}
    for o in offs:
        tr = [t for t in offs if t != o]
        Xtr = _pool(cfg, tr, None, r); ytr = _pool(cfg, tr, "y")
        Atr = _pool(cfg, tr, "address"); slabtr = _pool(cfg, tr, "slab")
        Xo = cfg[o]["Xr"][r]; yo = cfg[o]["y"]; Ao = cfg[o]["address"]
        Atr_res = _crossfit_train_residuals(Xtr, Atr, slabtr, reg_factory)
        Ao_res = _outer_residualiser_apply(Xtr, Atr, Xo, Ao, reg_factory)
        base = r2_fn(Xtr, ytr, Xo, yo)
        aug = r2_fn(np.column_stack([Xtr, Atr_res]), ytr, np.column_stack([Xo, Ao_res]), yo)
        out.append(aug - base)
        if return_internals:
            internals[o] = {"Atr_res": Atr_res, "Ao_res": Ao_res}
    return (np.array(out), internals) if return_internals else np.array(out)


# --------------------------------------------------------------------------- parity workflow
def parity_block(cfg, o, offs, return_scaler=False):
    """(degree, padded-Voronoi-area) field, z-scaled by a scaler fit on POOLED common-set rows of the
    five outer-TRAINING offsets and applied UNCHANGED to the held-out offset, then passed through the
    exact 11-column _m4_cols. Zero-variance/unavailable rule enforced (parity unavailable; capacity is
    NOT substituted). Returns (block_train, block_o[, scaler])."""
    tr = [t for t in offs if t != o]
    Dtr = np.concatenate([np.column_stack([cfg[t]["degree"], cfg[t]["voro_area"]]) for t in tr])
    mu = Dtr.mean(0); sd = Dtr.std(0)
    if np.any(sd < C.MOMENT_SIGMA_FLOOR):
        return (None, None, (mu, sd)) if return_scaler else (None, None)

    def blk(patch):
        scaled = (np.column_stack([patch["degree"], patch["voro_area"]]) - mu) / sd
        g = patch["geom"]
        return m4_cols(g["adj"], g["tree"], g["par"], scaled, shell_r=C.SHELL_R_M4)
    btr = np.concatenate([blk(cfg[t]) for t in tr], axis=0)
    bo = blk(cfg[o])
    return (btr, bo, (mu, sd)) if return_scaler else (btr, bo)


def parity_increment(cfg, r, r2_fn=gbt_r2):
    """Held-out parity increment per offset. 6-vector; np.nan where parity is unavailable (reported)."""
    offs = _offsets(cfg)
    out = []
    for o in offs:
        tr = [t for t in offs if t != o]
        btr, bo = parity_block(cfg, o, offs)
        if btr is None:
            out.append(np.nan); continue
        Xtr = _pool(cfg, tr, None, r); ytr = _pool(cfg, tr, "y")
        Xo = cfg[o]["Xr"][r]; yo = cfg[o]["y"]
        base = r2_fn(Xtr, ytr, Xo, yo)
        aug = r2_fn(np.column_stack([Xtr, btr]), ytr, np.column_stack([Xo, bo]), yo)
        out.append(aug - base)
    return np.array(out)


# --------------------------------------------------------------------------- capacity workflow
def capacity_increment_draw(cfg, r, block_dim, draw_index, r2_fn=gbt_r2):
    """One capacity draw (independently-keyed Gaussian block, same dim as the parity block): the
    complete six-offset held-out increment. 6-vector."""
    from .seeds import capacity_rng
    rng = capacity_rng(draw_index)
    offs = _offsets(cfg)
    out = []
    for o in offs:
        tr = [t for t in offs if t != o]
        Xtr = _pool(cfg, tr, None, r); ytr = _pool(cfg, tr, "y"); Xo = cfg[o]["Xr"][r]; yo = cfg[o]["y"]
        Gtr = rng.normal(size=(len(Xtr), block_dim)); Go = rng.normal(size=(len(Xo), block_dim))
        base = r2_fn(Xtr, ytr, Xo, yo)
        aug = r2_fn(np.column_stack([Xtr, Gtr]), ytr, np.column_stack([Xo, Go]), yo)
        out.append(aug - base)
    return np.array(out)


def capacity_delta_cap(dataset, r, block_dim=11, n_draws=C.CAPACITY_DRAWS, r2_fn=gbt_r2):
    """delta_cap from EXACTLY n_draws independently-keyed Gaussian blocks (physical v7 §6). Each draw
    -> a full M9 (nine configs x six offsets) -> 95th percentile of the n_draws M9 values."""
    assert n_draws == C.CAPACITY_DRAWS, f"capacity requires EXACTLY {C.CAPACITY_DRAWS} draws"
    configs = list(dataset.keys())
    assert len(configs) == 9, "capacity M9 spans exactly nine configs (no dropping)"
    per_draw = [M9(np.array([capacity_increment_draw(dataset[c], r, block_dim, d, r2_fn)
                             for c in configs])) for d in range(n_draws)]
    return float(np.percentile(per_draw, 95)), np.array(per_draw)


# --------------------------------------------------------------------------- permutation workflow
def _permuted_address_block(patch, key_prefix, b, ref_mu, ref_sd):
    """Standardise match-features with the TRAINING-only scaler, permute the raw two-component address
    within motif groups (Policy A), recompute the exact 11-col _m4_cols on the permuted raw field."""
    from .matching import build_permutation
    Xstd = (patch["match_feat"] - ref_mu) / ref_sd
    perm = build_permutation(Xstd, patch["motif_keys"], key_prefix, b)
    g = patch["geom"]
    return m4_cols(g["adj"], g["tree"], g["par"], patch["address_raw"][perm], shell_r=C.SHELL_R_M4)


def _perm_fold_blocks(cfg, o, offs, key_prefix, b):
    """Training and held-out permuted address blocks for outer fold o, constructed SEPARATELY.
    Training-only scaler (pooled five training offsets) applied to both; rep index b synchronised."""
    tr = [t for t in offs if t != o]
    MF = np.concatenate([cfg[t]["match_feat"] for t in tr], axis=0)
    mu = MF.mean(0); sd = np.where(MF.std(0) > 1e-12, MF.std(0), 1.0)
    Bo = _permuted_address_block(cfg[o], (key_prefix, o, "held"), b, mu, sd)
    Btr = np.concatenate([_permuted_address_block(cfg[t], (key_prefix, o, "train", t), b, mu, sd)
                          for t in tr], axis=0)
    return Btr, Bo


def permutation_config_vector(cfg, r, block_fn, r2_fn=gbt_r2):
    """Six-offset address-increment vector for one config. block_fn(o, offs) -> (Btr, Bo); if None the
    real address block is used (the observed statistic)."""
    offs = _offsets(cfg)
    out = []
    for o in offs:
        tr = [t for t in offs if t != o]
        Xtr = _pool(cfg, tr, None, r); ytr = _pool(cfg, tr, "y"); Xo = cfg[o]["Xr"][r]; yo = cfg[o]["y"]
        if block_fn is None:
            Btr = _pool(cfg, tr, "address"); Bo = cfg[o]["address"]
        else:
            Btr, Bo = block_fn(o, offs)
        base = r2_fn(Xtr, ytr, Xo, yo)
        aug = r2_fn(np.column_stack([Xtr, Btr]), ytr, np.column_stack([Xo, Bo]), yo)
        out.append(aug - base)
    return np.array(out)


def permutation_stress(feasible_dataset, r, B=C.B_PERM, r2_fn=gbt_r2):
    """M_perm,7 permutation stress reference over the seven feasible cells. EXACTLY B=1000 reps;
    rep index b synchronised across configs; training and held-out permutations constructed
    separately. Returns dict: obs_matrix(7,6), obs_Mperm7, null_Mperm7(B,), qref, obs_T7(7,),
    null_T7(7,B)."""
    assert B == C.B_PERM, f"permutation stress requires EXACTLY B={C.B_PERM}"
    cells = list(feasible_dataset.keys())
    assert len(cells) == 7, f"M_perm,7 requires exactly 7 feasible cells, got {len(cells)}"
    obs_matrix = np.array([permutation_config_vector(feasible_dataset[c], r, None, r2_fn) for c in cells])
    null_matrix = np.zeros((B, 7, 6))
    for ci, c in enumerate(cells):
        cfg = feasible_dataset[c]
        for b in range(B):
            bf = (lambda o, offs, _cfg=cfg, _c=c, _b=b: _perm_fold_blocks(_cfg, o, offs, str(_c), _b))
            null_matrix[b, ci] = permutation_config_vector(cfg, r, bf, r2_fn)
    obs_Mperm7 = M_perm7(obs_matrix)
    null_Mperm7 = np.array([M_perm7(null_matrix[b]) for b in range(B)])
    return dict(obs_matrix=obs_matrix, obs_Mperm7=obs_Mperm7, null_Mperm7=null_Mperm7,
                qref=C.q_ref_strict(null_Mperm7, obs_Mperm7),
                obs_T7=np.median(obs_matrix, axis=1), null_T7=np.median(null_matrix, axis=2).T)


# --------------------------------------------------------------------------- six-offset orchestrator
def orchestrate(dataset, r=C.REF_RADIUS, r2_fn=gbt_r2, reg_factory=make_regressor,
                permutation=None, capacity=None, g0=None, g1=None, radius_pair=None):
    """Generic six-offset orchestrator on SUPPLIED data (no study-data entry point).
    Fixed nine-config M9 and seven-config M_perm,7 (membership never changed by outcomes; no cell
    removal). Runs plain/residual/parity/capacity increments and assembles G0-G8 inputs + final route.
    `permutation` (a permutation_stress result) and `capacity` (a (delta_cap, per_draw) pair) may be
    supplied precomputed; `g0` (t_bound*) and `g1` (dict cfg->median R2_fit) come from the MSD workload.
    `radius_pair` = (r_small, r_ref) for the compression fade rule (default (2, r))."""
    configs = list(dataset.keys())
    assert len(configs) == 9, f"M9 must span exactly nine configs, got {len(configs)} (no dropping)"
    feasible = {c: dataset[c] for c in configs if dataset[c][next(iter(dataset[c]))].get("feasible", True)}
    assert len(feasible) == 7, f"M_perm,7 must span exactly seven feasible cells, got {len(feasible)}"

    r_small, r_ref = radius_pair or (2, r)
    plain9 = np.array([plain_increment(dataset[c], r_ref, "address", r2_fn) for c in configs])
    plain9_small = np.array([plain_increment(dataset[c], r_small, "address", r2_fn) for c in configs])
    shuf9 = np.array([plain_increment(dataset[c], r_ref, "shuf_address", r2_fn) for c in configs])
    resid9 = np.array([residual_increment(dataset[c], r_ref, r2_fn, reg_factory) for c in configs])
    parity9 = np.array([parity_increment(dataset[c], r_ref, r2_fn) for c in configs])

    if capacity is None:
        dcap, _ = capacity_delta_cap(dataset, r_ref, 11, C.CAPACITY_DRAWS, r2_fn)
    else:
        dcap = capacity[0]
    if permutation is None:
        permutation = permutation_stress(feasible, r_ref, C.B_PERM, r2_fn)

    m9_addr = M9(plain9); m9_addr2 = M9(plain9_small); m9_resid = M9(resid9)
    m9_parity = M9(np.where(np.isnan(parity9), 0.0, parity9))  # descriptive only
    rkill = R_kill(plain9, shuf9, dcap)
    sign6 = np.median(plain9_small, axis=0)     # compression sign-stability is on the r=2 increment

    res = {
        "M9_address": m9_addr, "M9_address_small": m9_addr2, "M9_residual": m9_resid,
        "M9_parity": m9_parity, "delta_cap": dcap, "R_kill": rkill,
        "qref_Mperm7": permutation["qref"],
        "gates": {
            "G2": G.G2(permutation["qref"]), "G3": G.G3(m9_addr, dcap), "G4": G.G4(rkill),
            "G6": G.G6(m9_resid, dcap), "G7": G.G7(m9_addr, m9_parity),
        },
        "route": G.route_physical_outcome(m9_addr2, m9_addr, dcap, sign6, m9_resid,
                                          permutation["qref"], feasible=True),
    }
    if g0 is not None:
        res["gates"]["G0"] = G.G0(g0)
    if g1 is not None:
        res["gates"]["G1"] = {c: G.G1(g1[c]) for c in g1}
    return res
