#!/usr/bin/env python3
"""
EXPLORATORY / INTERPRETIVE ablation of the neighbourhood-address (M4) block.
ROADMAP step 5. NOT a sealed, pre-registered study.

Two parts:

  PART A (original) -- group-by-group ablation of the M4 address block: which of
  the four groups (perp mean / perp variance / gradient / hull depth) reproduces
  or is needed for the coherent M4-over-M3 transport increment.

  PART B (added after GPT/Sol's independent audit) -- an OUTCOME-BLIND PHYSICAL-SPREAD
  CONTROL. Sol's point: the "perp variance" columns measure how much the perp field
  spreads across each graph-radius ball, but ANY field spreads across those balls.
  So the fair question is not "does perp variance predict transport" (it does) but
  "does perp variance predict transport BEYOND the same within-ball spread of ordinary
  PHYSICAL fields". We therefore build physical-spread controls over the SAME
  graph-radius 2/4/8 balls and ask what the perp variance (and the full M4) still add
  ON TOP of them.

    control (a): degree variance alone (per-ball var of degree)              -> 3 cols
    control (b): per-ball variances of degree, density, g(1.6), g(2.6),
                 g(4), g(6)  -- the full physical-spread block               -> 18 cols

  Reported as PAIRED leave-one-offset-out fold increments (per fold, so the sign of
  every fold is visible), for: M3 ; perp-variance over M3 ; physical-spread over M3 ;
  perp-variance over (M3 + physical-spread) ; full-M4 over (M3 + physical-spread).

Nothing new is built in the pipeline: PART A/B reuse transport_run's build_features /
assemble / _m4_cols / ball_shells verbatim, the same OFFSETS, bulk mask, codebook +
rng(0), HistGradientBoosting regressor and leave-one-offset-out CV. The physical-spread
columns are computed with transport_run.ball_shells over the identical balls the perp
variance uses, so the only difference between "perp variance" and "physical spread" is
WHICH field's within-ball variance is taken.

This rerun is a cross-engine REPLICATION of Sol's independently-computed residuals
(golden ~ +0.0060 perp-var / +0.0085 full-M4 over physical spread; platinum ~ +0.0173 /
+0.0217, all five folds positive; silver ~ 0, fully absorbed). We implement the control
exactly as Sol specified and report whether this engine's numbers land on Sol's.

Reproduce: python ablation_run.py 8 10 12      (golden is N=10; default runs all)
"""

import platform
import sys

import numpy as np
import scipy
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import transport_run as T  # reuse the sealed harness verbatim

# Plain M4-over-M3 increments this pipeline produced for the sealed transport run,
# used by the EXECUTABLE reproduction check below. These are THIS ENVIRONMENT's
# reproduction of the sealed result; the published sealed headline is golden +0.031,
# platinum +0.089, silver +0.090 (RESULTS_TRANSPORT.md). HistGradientBoosting is
# mildly version-sensitive, so exact agreement is only expected to ~3 decimals
# (Sol observed ~+0.0008 drift on golden between environments); the check tolerance
# is set accordingly.
SEALED_M4_OVER_M3 = {8: 0.0905, 10: 0.0310, 12: 0.0885}
REPRO_TOL = 0.003

# Column layout inside T._m4_cols(...), shell_r = (2, 4, 8):
#   [sm2(0,1) sv2(2) sm4(3,4) sv4(5) sm8(6,7) sv8(8) grad(9) depth(10)]
GROUP_COLS = {
    "perp":  [0, 1, 3, 4, 6, 7],   # shell-averaged perp MEAN
    "var":   [2, 5, 8],            # within-shell perp VARIANCE
    "grad":  [9],
    "depth": [10],
}
ALL_COLS = list(range(11))
GROUPS = ("perp", "var", "grad", "depth")
LEAVE_OUT = {f"M4_no_{g}": [c for c in ALL_COLS if c not in GROUP_COLS[g]]
             for g in GROUPS}
ONLY = {f"M4_only_{g}": GROUP_COLS[g] for g in GROUPS}


def phys_spread_cols(f, field_names):
    """Per-ball variance of each named PHYSICAL scalar field, over the SAME
    graph-radius balls (dd <= r, r in shell_r) that T._m4_cols uses for perp variance.
    field_names is a subset of the six Sol specified; column order is
    field-major then shell-major, fixed and explicit."""
    fields = {
        "deg":  f["deg"],
        "dens": f["dens"],
        "g1.6": f["g_small"][0],
        "g2.6": f["g_small"][1],
        "g4":   f["g_med"][0],
        "g6":   f["g_med"][1],
    }
    n, adj, shell_r = f["n"], f["adj"], f["shell_r"]
    var = {name: {r: np.zeros(n) for r in shell_r} for name in field_names}
    for i in range(n):
        dist = T.ball_shells(adj, i, max(shell_r))
        members = np.array(sorted(dist))
        dd = np.array([dist[v] for v in members])
        for r in shell_r:
            sel = members[dd <= r]
            for name in field_names:
                var[name][r][i] = fields[name][sel].var()
    cols = [var[name][r][:, None] for name in field_names for r in shell_r]
    return np.column_stack(cols)


PHYS_A = ["deg"]                                        # degree variance alone
PHYS_B = ["deg", "dens", "g1.6", "g2.6", "g4", "g6"]    # full physical spread


def check_full_m4(base, blocks):
    """EXECUTABLE, explicit M4-equality check (array_equal + width + column order):
    our reconstructed [M3 | full M4 cols] must equal the sealed assemble() M4 exactly."""
    for b, bl in zip(base, blocks):
        sealed, ours = b["M4"], bl["M4"]
        assert sealed.shape == ours.shape, (
            f"M4 width mismatch: sealed {sealed.shape} vs reconstructed {ours.shape}")
        assert sealed.shape[1] == bl["M3"].shape[1] + 11, (
            f"M4 should be M3 ({bl['M3'].shape[1]}) + 11 address cols, "
            f"got {sealed.shape[1]}")
        assert np.array_equal(sealed, ours), (
            "reconstructed M4 not bit-identical to sealed M4 (order/content)")


def build_blocks(N):
    """Reproduce run_family's setup exactly, then add PART A (group-ablated M4) and
    PART B (physical-spread control) rungs."""
    feats = [T.build_features(N, off) for off in T.OFFSETS]
    bulk_list = [f["bulk"] for f in feats]
    rng = np.random.default_rng(0)
    codebook = {}
    for f in feats:
        for k in f["motif_keys"]:
            codebook.setdefault(k, len(codebook))
    base = [T.assemble(f, codebook, rng) for f in feats]  # sealed M0..M4, controls

    blocks = []
    for f, b in zip(feats, base):
        M3 = b["M3"]
        full_m4 = T._m4_cols(f, f["perp"])                # the exact sealed M4 cols
        perpvar = full_m4[:, GROUP_COLS["var"]]           # perp VARIANCE only
        physA = phys_spread_cols(f, PHYS_A)               # degree variance alone
        physB = phys_spread_cols(f, PHYS_B)               # full physical spread
        rungs = {
            "M3": M3,
            "M4": np.column_stack([M3, full_m4]),
            # PART B rungs
            "M3+perpvar":        np.column_stack([M3, perpvar]),
            "M3+physA":          np.column_stack([M3, physA]),
            "M3+physB":          np.column_stack([M3, physB]),
            "M3+physB+perpvar":  np.column_stack([M3, physB, perpvar]),
            "M3+physB+M4":       np.column_stack([M3, physB, full_m4]),
        }
        # PART A rungs (original group ablation)
        for label, cols in {**LEAVE_OUT, **ONLY}.items():
            rungs[label] = np.column_stack([M3, full_m4[:, cols]])
        blocks.append(rungs)

    check_full_m4(base, blocks)
    return feats, bulk_list, blocks


def held_out_folds(blocks, y, bulk_list, rung):
    """Per-fold leave-one-offset-out R^2 (mirrors transport_run.held_out_r2 exactly --
    same GBT, same CV -- but returns the vector of fold scores so paired per-fold
    increments and their signs are visible)."""
    K = len(blocks)
    scores = np.empty(K)
    for test in range(K):
        Xtr = np.vstack([blocks[o][rung][bulk_list[o]] for o in range(K) if o != test])
        ytr = np.concatenate([y[o][bulk_list[o]] for o in range(K) if o != test])
        Xte = blocks[test][rung][bulk_list[test]]
        yte = y[test][bulk_list[test]]
        mdl = HistGradientBoostingRegressor(**T.GBT)
        mdl.fit(Xtr, ytr)
        scores[test] = r2_score(yte, mdl.predict(Xte))
    return scores


def fmt_paired(name, folds_a, folds_b):
    """Format a paired per-fold increment A-over-B."""
    d = folds_a - folds_b
    allpos = "ALL folds +" if np.all(d > 0) else f"{int((d > 0).sum())}/{len(d)} folds +"
    perfold = " ".join(f"{x:+.4f}" for x in d)
    return f"     {name:34s} mean {d.mean():+.4f}   [{perfold}]   {allpos}"


def report_partA(N, feats, bulk_list, blocks, y_key, label):
    y = ([f["ret"][10] for f in feats] if y_key is None else [f[y_key] for f in feats])
    m3 = held_out_folds(blocks, y, bulk_list, "M3").mean()
    m4 = held_out_folds(blocks, y, bulk_list, "M4").mean()
    I_full = m4 - m3
    print(f"\n  PART A group ablation  [{label}]  M3={m3:+.4f} M4={m4:+.4f} "
          f"full M4-over-M3={I_full:+.4f}")
    print(f"     {'group':7s} {'alone incr':>12s} {'necessity(drop)':>16s}")
    for g in GROUPS:
        only = held_out_folds(blocks, y, bulk_list, f"M4_only_{g}").mean() - m3
        lo = held_out_folds(blocks, y, bulk_list, f"M4_no_{g}").mean() - m3
        print(f"     {g:7s} {only:+12.4f} {I_full - lo:+16.4f}")
    return I_full


def report_partB(N, feats, bulk_list, blocks, y_key, label):
    y = ([f["ret"][10] for f in feats] if y_key is None else [f[y_key] for f in feats])
    F = {r: held_out_folds(blocks, y, bulk_list, r)
         for r in ("M3", "M3+perpvar", "M3+physA", "M3+physB",
                   "M3+physB+perpvar", "M3+physB+M4")}
    print(f"\n  PART B physical-spread control  [{label}]   "
          f"(M3 mean R2 = {F['M3'].mean():+.4f})")
    print(fmt_paired("perp-var over M3", F["M3+perpvar"], F["M3"]))
    print(fmt_paired("phys-spread(a: deg-var) over M3", F["M3+physA"], F["M3"]))
    print(fmt_paired("phys-spread(b: full) over M3", F["M3+physB"], F["M3"]))
    print(fmt_paired("perp-var over (M3+phys-spread b)",
                     F["M3+physB+perpvar"], F["M3+physB"]))
    print(fmt_paired("full-M4 over (M3+phys-spread b)",
                     F["M3+physB+M4"], F["M3+physB"]))


def repro_check(N, I_full):
    exp = SEALED_M4_OVER_M3[N]
    delta = I_full - exp
    ok = abs(delta) <= REPRO_TOL
    print(f"  REPRODUCTION CHECK  {T.NAME[N]}: full M4-over-M3 = {I_full:+.4f} vs "
          f"recorded {exp:+.4f}  (delta {delta:+.4f}, tol {REPRO_TOL})  "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def main(families=(8, 10, 12)):
    print(f"ENVIRONMENT  python {platform.python_version()}  numpy {np.__version__}  "
          f"scipy {scipy.__version__}  scikit-learn {sklearn.__version__}")
    print("(HistGradientBoosting is version-sensitive; expect ~1e-3 fourth-decimal "
          "drift across environments -- see RESULTS_ABLATION.md.)")
    all_ok = True
    for N in families:
        feats, bulk_list, blocks = build_blocks(N)
        nb = sum(int(b.sum()) for b in bulk_list)
        print(f"\n{'='*74}\n{T.NAME[N]} (N={N})  {len(T.OFFSETS)} offsets  "
              f"{nb} bulk vertices\n{'='*74}")
        I_full = report_partA(N, feats, bulk_list, blocks, "ld_primary",
                              "coherent-primary")
        all_ok &= repro_check(N, I_full)
        report_partB(N, feats, bulk_list, blocks, "ld_primary", "coherent-primary")
        report_partB(N, feats, bulk_list, blocks, None, "incoherent-t10 null")
    print(f"\nOVERALL REPRODUCTION: {'PASS' if all_ok else 'FAIL'}")


if __name__ == "__main__":
    fams = tuple(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else (8, 10, 12)
    main(fams)
