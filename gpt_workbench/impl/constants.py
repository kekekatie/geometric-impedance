"""
Frozen constants registry for the SEALED radius-saturation protocol suite.

Authoritative sources (immutable, sealed at commit 4ec0536; verify with SEAL_RECORD.md):
  - PHYSICAL_RADIUS_MANIFEST_DRAFT.md  v7
  - MSD_ENDPOINT_MANIFEST_DRAFT.md     v8.1
  - CONDITIONAL_NULL_MANIFEST_DRAFT.md v4.1
  - DECISION_GATE_CONCORDANCE.md
  - snapped_beta_times.txt

If this module and the sealed manifests ever disagree, THE MANIFESTS WIN. Every value here is a
transcription of a sealed constant; none may be changed without a dated post-seal amendment record.
This module is import-only and runs NO study dynamics.
"""
import os
import numpy as np

# ---- geometry / population (physical v7 §1, §5) -------------------------------------------------
OFFSETS = [(0.13, 0.37), (0.29, 0.11), (0.41, 0.23), (0.05, 0.47), (0.19, 0.31), (0.37, 0.09)]
N_OFFSETS = 6
ADMISSION_DEPTH_ELL = 16          # evaluated population = d_bound >= 16*ell common interior set
RADII = [2, 4, 8, 12, 16]         # radius ladder S
REF_RADIUS = 16
PHYS_EXTRA_DIM = {2: 11, 4: 22, 8: 35, 12: 48, 16: 61}   # r + 9*m(r)
SINGLETON_MAX = 0.05              # local permutation null infeasible if singleton frac > 5%

# ---- nine family x tier configurations (physical v7 §8) -----------------------------------------
# (family, N-fold, extent).  M9 ALWAYS spans all nine; membership fixed a priori, never dropped.
CONFIGS_9 = [
    ("silver",   8, 14), ("silver",   8, 16), ("silver",   8, 18),
    ("golden",  10, 18), ("golden",  10, 20), ("golden",  10, 22),
    ("platinum",12, 16), ("platinum",12, 18), ("platinum",12, 20),
]
# M_perm,7 = seven permutation-feasible cells (silver x3, golden x3, platinum e20).
# platinum e16/e18 are permutation-null-INFEASIBLE (>5% singletons) and CANNOT pass G2.
FEASIBLE_7 = [(f, e) for (f, _, e) in CONFIGS_9 if not (f == "platinum" and e in (16, 18))]
PLATINUM_INFEASIBLE = [("platinum", 16), ("platinum", 18)]
TIERS = {
    "small":  [("silver", 8, 14), ("golden", 10, 18), ("platinum", 12, 16)],
    "medium": [("silver", 8, 16), ("golden", 10, 20), ("platinum", 12, 18)],
    "large":  [("silver", 8, 18), ("golden", 10, 22), ("platinum", 12, 20)],
}

# ---- regressor (physical v7 §1; frozen for all rungs/controls/families) --------------------------
REGRESSOR = dict(max_depth=3, max_iter=250, learning_rate=0.06,
                 l2_regularization=1.0, random_state=0)

# ---- M3 / feature radii (physical v7 §2/§3; dens = transport_run gcount(2.0)) --------------------
DENS_RADIUS = 2.0
G_SMALL = (1.6, 2.6)
G_MED = (4.0, 6.0)
PSI_ORDERS = ("N", "N//2", "2N")        # resolved per family: N, N//2, 2N
SHELL_R_M4 = (2, 4, 8)                   # graph-distance shells for the 11-col _m4_cols address
MOMENT_SIGMA_FLOOR = 1e-9               # if sigma < floor, skew/exkurt set to 0
DEDUP_TOL = 1e-12                        # drop a physical_extra col only if bit-identical to an M3 col
BIN_TAU = 1e-9                           # Group A right-closed bin tolerance

# ---- padded Voronoi (physical v7 §3a) -----------------------------------------------------------
VORONOI_PAD_DELTA_MIN = 4
VORONOI_PAD_RING_MIN_ELL = 3
VORONOI_CONV_TOL = 1e-6

# ---- inner cross-validation (physical v7 §5) ----------------------------------------------------
N_SLABS = 4
FLOOR_R16 = 400
FLOOR_SLAB = 100

# ---- matching law (conditional-null v4.1 §3/§9; RATIFIED) ---------------------------------------
MATCH_K = 32
MATCH_ESCALATION = [32, 64, "full"]     # Policy A: deterministic 32 -> 64 -> full same-motif group
MATCH_LAMBDA = 1.0
MATCH_POLICY = "A"
MATCH_COST = "feature_distance + lambda * U(0,1)"   # NOT distance * U

# ---- randomisation / capacity (conditional-null v4.1 §4/§5/§6) ----------------------------------
B_PERM = 1000
CAPACITY_DRAWS = 200
SEED_ADDRESS_PERM_ROOT = 20260829       # -> 1000 children
SEED_CAPACITY_ROOT = 20260830           # -> 200 children (indices 0..199)
SEED_LOCALITY_ROOT = 20260829           # blake2b keyed registry (design diagnostic)
# parity has NO seed (deterministic)

# ---- MSD engine grids (MSD v8.1 §4/§5/§6) -------------------------------------------------------
BOUNDARY_GRID = np.linspace(0.0, 8.0, 161)     # dt = 0.05
BOUNDARY_DT = 0.05
STRIP_W = 2                              # boundary strip: d_bound(v) < w*ell
CROSS_THRESHOLD = 0.01                   # boundary crossing: dP_strip >= 0.01
T_BOUND_STRICT = 8                       # G0 admissible iff t_bound* > 8 (strict)
BETA_FIT_INTERVAL = (2.0, 8.0)
LAUNCH_L = 200
LAUNCH_BATCH = 50
KRYLOV_STATE_TOL = 1e-10                 # Krylov vs exact-diag on synthetic graphs
NORM_CONS_TOL = 1e-8
PROB_NEG_TOL = -1e-10

# ---- gates (DECISION_GATE_CONCORDANCE.md; MSD v8.1 §12) ------------------------------------------
G1_R2_MIN = 0.90
G2_QREF_MAX = 0.05
G4_RKILL_MIN = 0.70
G5_CLASSICAL_FRAC = 0.2                  # classical M9,address <= 0.2 * coherent M9,address
RHO_STAR = 0.25                          # classification heuristic (NOT an equivalence margin)
SIGN_STABLE_MIN = 5                      # >= 5/6 offsets positive is supporting

# primary coherent transport claim vs the separate cross-engine modifier (MSD v8.1 §12)
PRIMARY_COHERENT_GATES = ("G0", "G1_coherent", "G2", "G3", "G4", "G6")
CROSS_ENGINE_MODIFIER_GATES = ("G1_classical", "G5")

FROZEN_TOP_LINE_CLAIM = (
    "the address representation predicts heterogeneity in full-spectrum wavepacket spreading "
    "beyond the frozen physical descriptions and controls"
)

# ---- snapped beta-fit times (MSD v8.1 §5; loaded from the sealed artifact) -----------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
SNAPPED_BETA_TIMES_PATH = os.path.join(_HERE, "..", "snapped_beta_times.txt")


def load_snapped_beta_times():
    """Load the 48 frozen snapped beta-fit times from the sealed artifact; assert exactly 48 unique."""
    vals = []
    with open(SNAPPED_BETA_TIMES_PATH) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            vals.append(float(line))
    arr = np.array(vals, float)
    assert arr.size == 48, f"expected 48 snapped beta-times, got {arr.size}"
    assert np.unique(arr).size == 48, "snapped beta-times must be 48 UNIQUE values"
    assert arr.min() >= 2.0 and arr.max() <= 8.0, "snapped beta-times must lie in [2,8]"
    assert np.all(np.diff(arr) > 0), "snapped beta-times must be strictly increasing"
    return arr


SNAPPED_BETA_TIMES = load_snapped_beta_times()


def q_ref(null_vals, obs):
    """Constrained-reference tail q_ref = (1 + #{null >= obs}) / (B+1). Extremeness, NOT significance."""
    null = np.asarray(null_vals, float)
    return (1 + int(np.sum(null >= obs))) / (null.size + 1)


def q_ref_strict(null_vals, obs):
    """q_ref requiring EXACTLY B_PERM (1000) null repetitions (permutation stress gate invariant)."""
    null = np.asarray(null_vals, float)
    assert null.size == B_PERM, f"q_ref requires exactly {B_PERM} null repetitions, got {null.size}"
    return q_ref(null, obs)


def assert_grid_correspondence(times, grid=BOUNDARY_GRID, tol=None):
    """Assert every fit time snaps EXACTLY to a boundary-grid point (within half a grid step)."""
    tol = (BOUNDARY_DT / 2 + 1e-9) if tol is None else tol
    times = np.asarray(times, float)
    nearest = grid[np.argmin(np.abs(grid[None, :] - times[:, None]), axis=1)]
    assert np.all(np.abs(times - nearest) <= tol), "a fit time does not correspond to a grid point"
    return nearest


def phys_extra_dim(r):
    """dim(physical_extra(r)) = r + 9*m(r), m(r) = |{s in RADII : s <= r}|."""
    m = sum(1 for s in RADII if s <= r)
    return r + 9 * m


def _self_check():
    """Frozen-invariant assertions (fail fast at import if the registry is internally inconsistent)."""
    assert len(OFFSETS) == N_OFFSETS == 6
    assert len(CONFIGS_9) == 9
    assert len(FEASIBLE_7) == 7, f"M_perm,7 must have 7 cells, got {len(FEASIBLE_7)}"
    assert set(PLATINUM_INFEASIBLE).isdisjoint(set(FEASIBLE_7))
    assert sum(len(v) for v in TIERS.values()) == 9
    for r, d in PHYS_EXTRA_DIM.items():
        assert phys_extra_dim(r) == d, f"phys_extra_dim({r})={phys_extra_dim(r)} != {d}"
    assert BOUNDARY_GRID.size == 161
    assert abs((BOUNDARY_GRID[1] - BOUNDARY_GRID[0]) - BOUNDARY_DT) < 1e-12
    assert SNAPPED_BETA_TIMES.size == 48 and np.unique(SNAPPED_BETA_TIMES).size == 48
    assert_grid_correspondence(SNAPPED_BETA_TIMES)          # 48 snapped times correspond to grid pts
    assert MATCH_K == 32 and MATCH_LAMBDA == 1.0 and MATCH_POLICY == "A"
    assert B_PERM == 1000 and CAPACITY_DRAWS == 200


_self_check()
