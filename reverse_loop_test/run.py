#!/usr/bin/env python3
"""
Reverse-Loop Test -- orchestrator.

Runs the sensitivity control, Experiment 1 (spliced-loop equivalence),
Experiment 2 (closed-loop holonomy) and the Experiment 3 analysis layer, for
both substrates, then writes results/, figures/, summary.json and the raw
material for FINDINGS.md.

Usage:
    python3 run.py --pilot        # 5% pilot + runtime extrapolation, no figures
    python3 run.py --n 1000       # full run at N matched sets per substrate
"""

import argparse
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr

import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from geometry import Patch, SUBSTRATES
import experiments as E
import stats as ST

HERE = Path(__file__).parent
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

# ---- pre-registered configuration ---------------------------------------- #
CONFIG = dict(
    radius=22.0,
    L_direct=12,               # standard transit length
    n_zones=4,
    interior_frac=0.6,         # sample starts from interior to avoid boundary
    sensitivity_n=500,
    equiv_margin_frac=0.05,    # bounds = +-0.05 * d_zone (Cohen's d units)
    seed=20260702,
)
SUBSTRATE_ORDER = ["ammann_beenker", "penrose"]
COLORS = {"C0": "#444444", "C1": "#1b7837", "C2": "#2166ac", "C3": "#b2182b"}


def make_patch(substrate):
    p = Patch(substrate, radius=CONFIG["radius"], n_zones=CONFIG["n_zones"])
    r = np.linalg.norm(p.par, axis=1)
    comp_all = p.largest_component()
    mask = np.zeros(p.n, dtype=bool)
    mask[comp_all] = True
    interior = np.where(mask & (r < CONFIG["interior_frac"] * CONFIG["radius"]))[0]
    return p, interior


# ------------------------------------------------------------------------- #
# Analysis
# ------------------------------------------------------------------------- #

def analyse_exp1(df, d_zone, sigma_ref, substrate):
    """
    C1/C2/C3 x tier x start_zone vs C0, using the *matched-set* design: each
    conditioned walker is paired with the C0 walker sharing its S,T (same
    matched_id). Paired-difference TOST against +-0.05*d_zone (raw units), plus
    a two-sample KS on distribution shape and Cohen's d with CI.
    """
    margin = CONFIG["equiv_margin_frac"] * d_zone * sigma_ref
    c0 = df[df.condition == "C0"].set_index("matched_id")["final_residue"]
    out = []
    conditions = ["C1", "C2", "C3"]
    tiers = ["0.5x", "1x", "2x", "4x"]
    zones = sorted(df.start_zone.unique())
    for cond in conditions:
        for tier in tiers:
            for zone in ["ALL"] + list(zones):
                sub = df[(df.condition == cond) & (df.tier == tier)]
                if zone != "ALL":
                    sub = sub[sub.start_zone == zone]
                if len(sub) < 5:
                    continue
                a = sub.final_residue.to_numpy()
                b = sub.matched_id.map(c0).to_numpy()   # paired C0 residue
                diffs = a - b
                d, dlo, dhi = ST.cohen_d_ci(a, b, seed=1)
                t = ST.tost_one_sample(diffs, -margin, margin)
                ks = ST.ks_test(a, b)
                out.append(dict(
                    substrate=substrate, experiment="exp1", condition=cond,
                    tier=tier, start_zone=zone, n_pairs=len(a),
                    mean_cond=float(a.mean()), mean_ref=float(b.mean()),
                    paired_diff_mean=float(diffs.mean()),
                    paired_diff_max_abs=float(np.abs(diffs).max()),
                    cohen_d=d, d_ci_lo=dlo, d_ci_hi=dhi,
                    tost_p=t["p_tost"], equiv_margin_raw=margin,
                    equivalent=t["equivalent"], ks_stat=ks["ks_stat"],
                    ks_p=ks["ks_p"]))
    return out


def analyse_exp2(df, d_zone, sigma_ref, substrate):
    """Per (condition,tier): equivalence of loop holonomy to 0, and which loop
    property predicts the (tiny) residual."""
    margin_raw = CONFIG["equiv_margin_frac"] * d_zone * sigma_ref
    out = []
    conds = ["C4", "C5_in_zone", "C5_crossing", "C5_deep_dip"]
    tiers = ["0.5x", "1x", "2x", "4x"]
    for cond in conds:
        for tier in ["ALL"] + tiers:
            sub = df[df.condition == cond]
            if tier != "ALL":
                sub = sub[sub.tier == tier]
            h = sub.loop_holonomy.to_numpy()
            if len(h) < 5:
                continue
            # one-sample equivalence of mean(h) to 0 within +-margin_raw
            t = ST.tost_one_sample(h, -margin_raw, margin_raw)
            row = dict(substrate=substrate, experiment="exp2", condition=cond,
                       tier=tier, n=len(h),
                       holonomy_mean=t["mean"], holonomy_max=float(np.abs(h).max()),
                       holonomy_sd=float(h.std(ddof=1)) if len(h) > 1 else 0.0,
                       tost_p=t["p_tost"],
                       margin_raw=margin_raw, equivalent=bool(t["equivalent"]))
            # which loop property predicts residual (Spearman)
            if tier == "ALL" and len(sub) > 20:
                for prop in ["loop_len", "loop_depth_range",
                             "loop_zone_crossings"]:
                    rho = spearmanr(sub[prop], np.abs(h)).correlation
                    row[f"rho_{prop}"] = float(rho) if rho == rho else 0.0
            out.append(row)
    return out


def analyse_exp3(df, substrate):
    """At FIXED final position (matched set), does transit history predict
    residue? Within-matched-set demeaning removes the endpoint, leaving only
    route variation. Report R^2 / partial correlation."""
    out = []
    g = df.groupby("matched_id")
    res_dm = df.final_residue - g.final_residue.transform("mean")
    for prop in ["max_transit_depth", "zone_crossings", "path_len",
                 "min_transit_depth"]:
        prop_dm = df[prop] - g[prop].transform("mean")
        # correlation of within-set-demeaned residue vs demeaned covariate
        mask = prop_dm.abs() > 1e-12
        if mask.sum() < 10:
            r = 0.0
        else:
            r = np.corrcoef(prop_dm[mask], res_dm[mask])[0, 1]
            if r != r:
                r = 0.0
        out.append(dict(substrate=substrate, experiment="exp3",
                        covariate=prop, partial_r=float(r),
                        partial_r2=float(r * r),
                        residue_within_set_sd=float(res_dm.std())))
    return out


# ------------------------------------------------------------------------- #
# Figures
# ------------------------------------------------------------------------- #

def fig_distribution_overlay(exp1):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, sub in zip(axes, SUBSTRATE_ORDER):
        d = exp1[exp1.substrate == sub]
        d = d[d.tier.isin(["1x", "0x"])]
        bins = np.linspace(0, max(0.01, d.final_residue.max()), 40)
        # decreasing linewidth so the (perfectly superimposed) curves are all
        # visible as nested outlines -- the coincidence IS the result.
        for cond, lw in zip(["C0", "C1", "C2", "C3"], [6.0, 4.0, 2.5, 1.2]):
            vals = d[d.condition == cond].final_residue
            if len(vals) == 0:
                continue
            ax.hist(vals, bins=bins, histtype="step", density=True, lw=lw,
                    color=COLORS[cond], label=cond, alpha=0.9)
        ax.set_title(f"{sub}: final residue, C1-C3 (1x) vs C0 "
                     "(curves superimposed)")
        ax.set_xlabel("address residue  ||perp(T)-perp(S)||")
        ax.set_ylabel("density")
        ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_a_residue_distribution_overlay.png", dpi=130)
    plt.close(fig)


def fig_residue_vs_pathlength(exp1):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, sub in zip(axes, SUBSTRATE_ORDER):
        d = exp1[exp1.substrate == sub]
        for cond in ["C0", "C1", "C2", "C3"]:
            dd = d[d.condition == cond]
            if len(dd) == 0:
                continue
            grp = dd.groupby("tier").agg(
                pl=("path_len", "mean"), res=("final_residue", "mean"),
                sd=("final_residue", "std"))
            grp = grp.sort_values("pl")
            ax.errorbar(grp.pl, grp.res, yerr=grp.sd, marker="o", lw=2,
                        color=COLORS[cond], label=cond, capsize=3)
        ax.set_title(f"{sub}: residue vs total path length")
        ax.set_xlabel("total path length (edges)")
        ax.set_ylabel("mean address residue")
        ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_b_residue_vs_pathlength.png", dpi=130)
    plt.close(fig)


def fig_exp2_holonomy(exp2raw):
    props = ["loop_len", "loop_depth_range", "loop_zone_crossings"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for i, sub in enumerate(SUBSTRATE_ORDER):
        d = exp2raw[exp2raw.substrate == sub]
        for j, prop in enumerate(props):
            ax = axes[i, j]
            for cond in ["C4", "C5_in_zone", "C5_crossing", "C5_deep_dip"]:
                dd = d[d.condition == cond]
                if len(dd) == 0:
                    continue
                ax.scatter(dd[prop], dd.loop_holonomy, s=6, alpha=0.4,
                           label=cond)
            ax.set_title(f"{sub}: loop holonomy vs {prop}")
            ax.set_xlabel(prop)
            ax.set_ylabel("loop holonomy ||sum d perp||")
            if i == 0 and j == 0:
                ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_c_exp2_holonomy.png", dpi=130)
    plt.close(fig)


def fig_exp3_transit(exp1, sensitivity):
    """Fixed-endpoint invariance: within each matched set the endpoint is fixed,
    so the four conditions vary max transit depth widely yet land on identical
    residue -- each set is a horizontal line. Contrast with the sensitivity
    trend (endpoint depth genuinely moves residue)."""
    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, sub in zip(axes, SUBSTRATE_ORDER):
        d = exp1[exp1.substrate == sub]
        ids = d.matched_id.unique()
        pick = rng.choice(ids, size=min(45, len(ids)), replace=False)
        for mid in pick:
            g = d[d.matched_id == mid]
            ax.plot(g.max_transit_depth, g.final_residue, "-", lw=0.8,
                    color="#2166ac", alpha=0.35)
        ax.scatter([], [], color="#2166ac",
                   label="one matched set (fixed endpoint)")
        # sensitivity: residue as endpoint depth changes (the real effect)
        pz = sensitivity[sub]["per_zone_means"]
        xr = d.max_transit_depth
        zx = np.linspace(xr.min(), xr.max(), len(pz))
        ax.plot(zx, pz, "s--", color="#b2182b", lw=2.5,
                label="residue vs ENDPOINT depth (sensitivity)")
        ax.set_title(f"{sub}: residue vs max transit depth\n"
                     "(each set flat; endpoint depth is what moves residue)")
        ax.set_xlabel("max transit depth during route")
        ax.set_ylabel("address residue")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_d_exp3_transit_depth.png", dpi=130)
    plt.close(fig)


# ------------------------------------------------------------------------- #
# Main
# ------------------------------------------------------------------------- #

def run(n_sets, pilot=False, make_figs=True):
    t_start = time.time()
    seed = CONFIG["seed"]
    summary = dict(config=CONFIG, substrates={}, timing={})
    all_exp1_rows, all_exp2_rows = [], []
    exp1_cmp, exp2_cmp, exp3_cmp = [], [], []
    sensitivity = {}

    for si, sub in enumerate(SUBSTRATE_ORDER):
        tsub = time.time()
        patch, interior = make_patch(sub)
        rng = np.random.default_rng(seed + 1000 * si)

        # -- sensitivity control (mandatory, first) --
        shallow, deep, per_zone = E.sensitivity_dzone(
            patch, rng, CONFIG["sensitivity_n"], CONFIG["L_direct"], interior)
        d_zone = abs(ST.cohen_d(shallow, deep))
        _, dz_lo, dz_hi = ST.cohen_d_ci(shallow, deep, seed=2)
        pooled_sd = np.sqrt(((len(shallow) - 1) * shallow.var(ddof=1) +
                             (len(deep) - 1) * deep.var(ddof=1)) /
                            (len(shallow) + len(deep) - 2))
        _, dz_p = ST.welch_t(shallow, deep)
        sensitivity[sub] = dict(d_zone=float(d_zone), d_zone_ci=[dz_lo, dz_hi],
                                d_zone_p=float(dz_p), sigma_ref=float(pooled_sd),
                                per_zone_means=per_zone,
                                margin_d=CONFIG["equiv_margin_frac"] * d_zone,
                                margin_raw=CONFIG["equiv_margin_frac"] * d_zone
                                * float(pooled_sd))
        print(f"[{sub}] sensitivity d_zone={d_zone:.3f} "
              f"(CI {dz_lo:.3f},{dz_hi:.3f}, p={dz_p:.1e}) "
              f"margin=+-{CONFIG['equiv_margin_frac']*d_zone:.4f} d", flush=True)

        # -- experiments --
        e1_rows, made1 = E.run_experiment1(patch, sub, rng, n_sets,
                                           CONFIG["L_direct"], interior)
        e2_rows, made2 = E.run_experiment2(patch, sub, rng, n_sets,
                                           CONFIG["L_direct"], interior)
        all_exp1_rows += e1_rows
        all_exp2_rows += e2_rows

        df1 = pd.DataFrame(e1_rows)
        df2 = pd.DataFrame(e2_rows)
        exp1_cmp += analyse_exp1(df1, d_zone, pooled_sd, sub)
        exp2_cmp += analyse_exp2(df2, d_zone, pooled_sd, sub)
        exp3_cmp += analyse_exp3(df1, sub)

        # mechanism-chain cross-check (gap -> balance -> residue)
        c0 = df1[df1.condition == "C0"]
        gap = c0.T_depth.to_numpy()
        bal = c0.directional_balance.to_numpy()
        res = c0.final_residue.to_numpy()
        summary["substrates"][sub] = dict(
            patch_vertices=int(patch.n), patch_edges=int(len(patch.edges)),
            interior_pool=int(len(interior)),
            matched_sets_exp1=int(made1), loops_exp2=int(made2),
            sensitivity=sensitivity[sub],
            gammas=patch.gammas.tolist(),
            mechanism_spearman=dict(
                gap_to_residue=float(spearmanr(gap, res).correlation),
                balance_to_residue=float(spearmanr(bal, res).correlation),
                gap_to_balance=float(spearmanr(gap, bal).correlation)),
        )
        summary["timing"][sub] = round(time.time() - tsub, 1)
        print(f"[{sub}] Exp1 sets={made1} rows={len(e1_rows)} | "
              f"Exp2 loops={made2} rows={len(e2_rows)} | "
              f"{summary['timing'][sub]}s", flush=True)

    df1_all = pd.DataFrame(all_exp1_rows)
    df2_all = pd.DataFrame(all_exp2_rows)

    # -- Benjamini-Hochberg across the full comparison grid --
    cmp1 = pd.DataFrame(exp1_cmp)
    if len(cmp1):
        cmp1["tost_p_bh"] = ST.benjamini_hochberg(cmp1.tost_p.to_numpy())
        cmp1["ks_p_bh"] = ST.benjamini_hochberg(cmp1.ks_p.to_numpy())
    cmp2 = pd.DataFrame(exp2_cmp)
    cmp3 = pd.DataFrame(exp3_cmp)

    # -- write results --
    if len(df1_all):
        df1_all.to_csv(RESULTS / "experiment1_walkers.csv", index=False)
    if len(df2_all):
        df2_all.to_csv(RESULTS / "experiment2_walkers.csv", index=False)
    if len(cmp1):
        cmp1.to_csv(RESULTS / "experiment1_equivalence.csv", index=False)
    if len(cmp2):
        cmp2.to_csv(RESULTS / "experiment2_holonomy.csv", index=False)
    if len(cmp3):
        cmp3.to_csv(RESULTS / "experiment3_transit.csv", index=False)

    # -- headline verdicts --
    summary["headline"] = build_headline(cmp1, cmp2, cmp3, sensitivity)
    summary["runtime_min"] = round((time.time() - t_start) / 60, 2)
    summary["n_sets"] = n_sets
    with open(HERE / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    if make_figs and len(df1_all):
        fig_distribution_overlay(df1_all)
        fig_residue_vs_pathlength(df1_all)
        fig_exp2_holonomy(df2_all)
        fig_exp3_transit(df1_all, sensitivity)
        print("figures written", flush=True)

    print(f"\nDONE in {summary['runtime_min']} min. "
          f"Headline: {json.dumps(summary['headline'], indent=2, default=str)}")
    return summary


def build_headline(cmp1, cmp2, cmp3, sensitivity):
    h = {}
    for sub in SUBSTRATE_ORDER:
        c1 = cmp1[cmp1.substrate == sub] if len(cmp1) else cmp1
        c2 = cmp2[cmp2.substrate == sub] if len(cmp2) else cmp2
        c3 = cmp3[cmp3.substrate == sub] if len(cmp3) else cmp3
        exp1_all_equiv = bool(c1.equivalent.all()) if len(c1) else None
        exp1_max_absd = float(c1.cohen_d.abs().max()) if len(c1) else None
        c4 = c2[c2.condition == "C4"] if len(c2) else c2
        c5 = c2[c2.condition.str.startswith("C5")] if len(c2) else c2
        c4_equiv = bool(c4.equivalent.all()) if len(c4) else None
        c5_equiv = bool(c5.equivalent.all()) if len(c5) else None
        c4_maxhol = float(c4.holonomy_max.max()) if len(c4) else None
        c5_maxhol = float(c5.holonomy_max.max()) if len(c5) else None
        exp3_max_r2 = float(c3.partial_r2.max()) if len(c3) else None
        # residue variation within a matched set (fixed endpoint). If this is at
        # machine precision, any partial-r on it is float noise, not physics.
        exp3_within_sd = float(c3.residue_within_set_sd.max()) if len(c3) else None
        # interpretation
        outcome = classify_outcome(exp1_all_equiv, c4_equiv, c5_equiv,
                                    exp3_max_r2, exp3_within_sd)
        h[sub] = dict(
            d_zone=sensitivity[sub]["d_zone"],
            exp1_all_conditions_equivalent=exp1_all_equiv,
            exp1_max_abs_cohen_d=exp1_max_absd,
            exp2_C4_cancels=c4_equiv, exp2_C4_max_holonomy=c4_maxhol,
            exp2_C5_cancels=c5_equiv, exp2_C5_max_holonomy=c5_maxhol,
            exp3_max_transit_partial_r2=exp3_max_r2,
            exp3_residue_within_set_sd=exp3_within_sd,
            outcome=outcome)
    return h


def classify_outcome(exp1_equiv, c4_equiv, c5_equiv, exp3_max_r2,
                     exp3_within_sd):
    if exp1_equiv is None:
        return "undetermined"
    # Exp 3 is null if residue is constant within a matched set to machine
    # precision (fixed endpoint => no transit-history channel), regardless of
    # the correlation computed on that ~1e-15 noise.
    exp3_null = ((exp3_within_sd is not None and exp3_within_sd < 1e-9) or
                 (exp3_max_r2 is None) or (exp3_max_r2 < 0.01))
    if exp1_equiv and c4_equiv and c5_equiv and exp3_null:
        return ("A: full equivalence -- positional (not historical) confirmed "
                "at full strength")
    if exp1_equiv and c4_equiv and (not c5_equiv):
        return ("B: open-path equivalence but structured closed-loop residual "
                "-- holonomy")
    if not exp3_null:
        return ("C: transit-history dependence at fixed endpoint -- mechanism "
                "incomplete as stated")
    return "mixed -- inspect comparison tables"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--nofigs", action="store_true")
    args = ap.parse_args()
    if args.pilot:
        n = max(20, int(0.05 * args.n))
        t0 = time.time()
        run(n, pilot=True, make_figs=False)
        dt = time.time() - t0
        print(f"\n[PILOT] {n} sets/substrate took {dt:.1f}s. "
              f"Projected full N={args.n}: ~{dt * args.n / n / 60:.1f} min "
              f"(linear extrapolation).")
    else:
        run(args.n, pilot=False, make_figs=not args.nofigs)
