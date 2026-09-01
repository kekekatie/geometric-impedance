"""
MSD transport workload (MSD_ENDPOINT_MANIFEST_DRAFT.md v8.1 §2-§7).

Operates on SUPPLIED graph patches (synthetic in tests); no study substrates are propagated. Launches
are propagated ONE AT A TIME and reduced on the fly to the scalars MSD(t) and P_strip(t) — the
prohibited (T x V x L) tensor is never materialised. beta uses exactly the 48 snapped points with a
frozen failure route if any required MSD value is nonpositive; G1 is the per-(config,engine) median.
"""
import numpy as np
from . import constants as C
from . import engines as E


def select_launches(slab_labels, pc1_proj, lifts, L=C.LAUNCH_L):
    """Frozen deterministic, spatially-balanced subsample: L/4 = 50 per PCA slab; within each slab
    sort by (PC1 projection, lift lexicographic) and take EVENLY-SPACED indices to the per-slab quota.
    If the common set has < L, use all of it."""
    assert L % C.N_SLABS == 0
    per = L // C.N_SLABS
    n = len(slab_labels)
    if n < L:
        return np.arange(n)
    lifts = np.asarray(lifts)
    chosen = []
    for s in range(C.N_SLABS):
        idx = np.where(slab_labels == s)[0]
        keys = [(float(pc1_proj[i]),) + tuple(int(x) for x in lifts[i]) for i in idx]
        pos = sorted(range(len(idx)), key=lambda k: keys[k])   # sort by (PC1 proj, lift lexicographic)
        order = idx[pos]
        take = np.linspace(0, len(order) - 1, per).round().astype(int)
        chosen.append(order[take])
    return np.sort(np.concatenate(chosen))


def strip_mask(d_bound, ell, w=C.STRIP_W):
    """Boundary strip STRIP = {v : d_bound(v) < w*ell}."""
    return d_bound < w * ell


def beta_with_failure_route(msd_on_grid, grid=C.BOUNDARY_GRID, snapped=C.SNAPPED_BETA_TIMES):
    """beta over exactly the 48 snapped points. Frozen failure route: if any required snapped MSD
    value is nonpositive, return (nan, nan, 'nonpositive-MSD') and do NOT fit."""
    idx = [int(np.argmin(np.abs(grid - t))) for t in snapped]
    assert len(idx) == 48, "beta fit must use exactly the 48 snapped points"
    y = msd_on_grid[idx]
    if np.any(y <= 0):
        return np.nan, np.nan, "nonpositive-MSD"
    b, r2 = E.beta_from_msd(msd_on_grid, grid, snapped)
    return b, r2, "ok"


def _launch_reduce(op, v0, par, strip, coherent, grid=C.BOUNDARY_GRID):
    """Propagate ONE launch (transient T x V state), reduce on the fly to MSD(t) and P_strip(t)."""
    states = E.coherent_states(op, v0, grid) if coherent else E.classical_states(op, v0, grid)
    msd = E.msd_curve(states, par, v0, coherent=coherent)
    pstrip = E.strip_mass(states, strip, coherent=coherent)
    del states                                     # never retained across launches (no T x V x L)
    return msd, pstrip


def run_patch(adj_edges, par, d_bound, ell, launches, batch=C.LAUNCH_BATCH):
    """Run one (config, offset) patch for BOTH engines. Returns per-engine arrays of beta and R2_fit
    over the launches, the earliest boundary crossing seen in this patch (both engines), and the
    per-engine median R2_fit. Launches processed in batches of 50, reduced on the fly."""
    n = len(par)
    A = E.adjacency(n, [tuple(e) for e in adj_edges])
    Q = E.ctmc_generator(A)
    strip = strip_mask(d_bound, ell)
    grid = C.BOUNDARY_GRID
    out = {"coherent": {"beta": [], "r2": [], "status": []},
           "classical": {"beta": [], "r2": [], "status": []}}
    earliest = np.inf
    for start in range(0, len(launches), batch):
        for v0 in launches[start:start + batch]:
            for eng, op, coh in (("coherent", (-1j) * A, True), ("classical", Q, False)):
                msd, pstrip = _launch_reduce(op, int(v0), par, strip, coh, grid)
                dps = pstrip - pstrip[0]
                earliest = min(earliest, E.boundary_crossing_time(dps, grid))
                b, r2, st = beta_with_failure_route(msd, grid)
                out[eng]["beta"].append(b); out[eng]["r2"].append(r2); out[eng]["status"].append(st)
    med = {}
    for eng in ("coherent", "classical"):
        r2s = np.array([x for x in out[eng]["r2"] if not np.isnan(x)])
        med[eng] = float(np.median(r2s)) if r2s.size else np.nan
    return {"per_engine": out, "patch_earliest_crossing": earliest, "median_r2": med}


def global_t_bound_star(patch_results):
    """t_bound* = earliest crossing over EVERY selected launch/config/offset and BOTH engines.
    'no crossing observed' -> +inf (G0 admissible)."""
    return float(min((pr["patch_earliest_crossing"] for pr in patch_results), default=np.inf))


def g1_median_r2_per_config_engine(patch_results_by_config):
    """G1 statistic: per-(config, engine) median R2_fit pooled across that config's six offsets."""
    out = {}
    for cfg, prs in patch_results_by_config.items():
        for eng in ("coherent", "classical"):
            r2s = np.concatenate([[x for x in pr["per_engine"][eng]["r2"] if not np.isnan(x)]
                                  for pr in prs]) if prs else np.array([])
            out[(cfg, eng)] = float(np.median(r2s)) if len(r2s) else np.nan
    return out
