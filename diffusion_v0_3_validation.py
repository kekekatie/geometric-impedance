"""
Diffusion–texture address-transport v0.3 validation run.

Tests whether local perpendicular-space texture/depth predicts
address-space residue on near-return physical paths, across many
walkers and multiple seeds, with shuffled controls.
"""

import os, sys, time, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ── paths ──────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "diffusion_v0_3_results")
os.makedirs(OUT, exist_ok=True)

# ── parameters ─────────────────────────────────────────────────────
N_SEEDS          = 10
WALKERS_PER_GROUP = 20_000
TIMES            = [64, 128, 256, 512, 1024]
NEAR_RETURN_THRESHOLDS = [1.0, 2.0, 3.0]
INTERIOR_FRAC    = 0.75
QUARTILE         = 0.25
CONTROL_WALKERS  = 5_000  # fewer for shuffled control

# ── helpers ────────────────────────────────────────────────────────

def load_substrate(name):
    if name == "AB_N30":
        verts = pd.read_csv(os.path.join(DATA, "clean_ab_full_raw_lift.csv"))
        edges = pd.read_csv(os.path.join(DATA, "large_ab_v0_6_edges.csv"))
        src_col, tgt_col = "source_index", "target_index"
    else:
        verts = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_lift.csv"))
        edges = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_edges.csv"))
        src_col, tgt_col = "source", "target"

    n = len(verts)
    adj = defaultdict(list)
    for _, row in edges.iterrows():
        s, t = int(row[src_col]), int(row[tgt_col])
        if s < n and t < n:
            adj[s].append(t)
            adj[t].append(s)

    adj_arr = [np.array(adj[i], dtype=np.int32) for i in range(n)]
    return verts, adj_arr, n


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


def compute_perp_hull_depth(verts):
    px = verts["perp_x"].values
    py = verts["perp_y"].values
    pts = np.column_stack([px, py])
    try:
        hull = ConvexHull(pts)
        from scipy.spatial import Delaunay
        deln = Delaunay(pts[hull.vertices])
        centroid = pts[hull.vertices].mean(axis=0)
        max_dist = np.max(np.linalg.norm(pts[hull.vertices] - centroid, axis=1))
        dist_from_centroid = np.linalg.norm(pts - centroid, axis=1)
        depth = 1.0 - (dist_from_centroid / (max_dist + 1e-12))
        return np.clip(depth, 0, 1)
    except Exception:
        return np.zeros(len(verts))


def compute_texture_score(verts, adj_arr):
    px = verts["perp_x"].values
    py = verts["perp_y"].values
    scores = np.zeros(len(verts))
    for i in range(len(verts)):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        diffs = np.sqrt((px[nbrs] - px[i])**2 + (py[nbrs] - py[i])**2)
        scores[i] = np.std(diffs) if len(diffs) > 1 else diffs[0]
    from scipy.stats import zscore
    z = zscore(scores, nan_policy='omit')
    return np.nan_to_num(z, 0.0)


def random_walks(adj_arr, starts, n_steps, rng):
    n_walkers = len(starts)
    positions = starts.copy()
    trajectories = np.zeros((n_walkers, n_steps + 1), dtype=np.int32)
    trajectories[:, 0] = starts
    for t in range(1, n_steps + 1):
        for w in range(n_walkers):
            nbrs = adj_arr[positions[w]]
            if len(nbrs) > 0:
                positions[w] = rng.choice(nbrs)
            trajectories[w, t] = positions[w]
    return trajectories


def analyse_walks(trajectories, verts_x, verts_y, perp_x, perp_y, times, thresholds):
    n_walkers = trajectories.shape[0]
    start_nodes = trajectories[:, 0]
    sx = verts_x[start_nodes]
    sy = verts_y[start_nodes]
    sp_x = perp_x[start_nodes]
    sp_y = perp_y[start_nodes]

    results = {}
    max_t = trajectories.shape[1] - 1

    for t in times:
        if t > max_t:
            continue
        cur_nodes = trajectories[:, t]
        cx = verts_x[cur_nodes]
        cy = verts_y[cur_nodes]
        cp_x = perp_x[cur_nodes]
        cp_y = perp_y[cur_nodes]

        phys_disp = np.sqrt((cx - sx)**2 + (cy - sy)**2)
        perp_disp = np.sqrt((cp_x - sp_x)**2 + (cp_y - sp_y)**2)
        phys_msd = np.mean(phys_disp**2)

        for thr in thresholds:
            mask = phys_disp <= thr
            nr_frac = np.mean(mask)
            nr_n = int(np.sum(mask))
            nr_mean_perp = np.mean(perp_disp[mask]) if nr_n > 0 else np.nan
            nr_median_perp = np.median(perp_disp[mask]) if nr_n > 0 else np.nan
            results[(t, thr)] = {
                "phys_msd": phys_msd,
                "near_return_frac": nr_frac,
                "near_return_n": nr_n,
                "near_return_mean_perp_mismatch": nr_mean_perp,
                "near_return_median_perp_mismatch": nr_median_perp,
            }

    # cumulative perp path length for tortuosity at max measured time
    max_measured = max(t for t in times if t <= max_t)
    cum_perp = np.zeros(n_walkers)
    for t in range(1, max_measured + 1):
        prev = trajectories[:, t - 1]
        cur = trajectories[:, t]
        cum_perp += np.sqrt((perp_x[cur] - perp_x[prev])**2 +
                            (perp_y[cur] - perp_y[prev])**2)
    net_perp = np.sqrt((perp_x[trajectories[:, max_measured]] - sp_x)**2 +
                       (perp_y[trajectories[:, max_measured]] - sp_y)**2)
    tort = cum_perp / (net_perp + 1e-12)
    results["tortuosity"] = {
        "median": float(np.median(tort)),
        "p90": float(np.percentile(tort, 90)),
        "mean": float(np.mean(tort)),
    }
    results["final_perp_mismatch_all"] = float(np.mean(net_perp))

    return results


def fit_diffusion_exponent(trajectories, verts_x, verts_y, times):
    start_nodes = trajectories[:, 0]
    sx = verts_x[start_nodes]
    sy = verts_y[start_nodes]
    max_t = trajectories.shape[1] - 1
    valid_times = [t for t in times if t <= max_t]
    if len(valid_times) < 2:
        return np.nan, np.nan

    log_t = []
    log_msd = []
    for t in valid_times:
        cur = trajectories[:, t]
        disp2 = (verts_x[cur] - sx)**2 + (verts_y[cur] - sy)**2
        msd = np.mean(disp2)
        if msd > 0:
            log_t.append(np.log(t))
            log_msd.append(np.log(msd))

    if len(log_t) < 2:
        return np.nan, np.nan
    coeffs = np.polyfit(log_t, log_msd, 1)
    alpha = coeffs[0]
    ss_res = np.sum((np.array(log_msd) - np.polyval(coeffs, log_t))**2)
    ss_tot = np.sum((np.array(log_msd) - np.mean(log_msd))**2)
    r2 = 1 - ss_res / (ss_tot + 1e-15)
    return alpha, r2


# ── main run ───────────────────────────────────────────────────────

def run_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Loading {name}")
    print(f"{'='*60}")
    t0 = time.time()

    verts, adj_arr, n = load_substrate(name)
    verts_x = verts["x"].values.astype(np.float64)
    verts_y = verts["y"].values.astype(np.float64)
    perp_x_orig = verts["perp_x"].values.astype(np.float64)
    perp_y_orig = verts["perp_y"].values.astype(np.float64)

    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior = phys_r <= r_thresh

    print(f"  Computing texture and depth scores...")
    texture = compute_texture_score(verts, adj_arr)
    depth = compute_perp_hull_depth(verts)

    interior_idx = np.where(interior)[0]
    tex_int = texture[interior_idx]
    dep_int = depth[interior_idx]

    tex_hi_thresh = np.percentile(tex_int, 100 * (1 - QUARTILE))
    tex_lo_thresh = np.percentile(tex_int, 100 * QUARTILE)
    dep_hi_thresh = np.percentile(dep_int, 100 * (1 - QUARTILE))
    dep_lo_thresh = np.percentile(dep_int, 100 * QUARTILE)

    groups = {
        "all_interior75": interior_idx,
        "texture_high_q25": interior_idx[(tex_int >= tex_hi_thresh)],
        "texture_low_q25": interior_idx[(tex_int <= tex_lo_thresh)],
        "depth_high_q25": interior_idx[(dep_int >= dep_hi_thresh)],
        "depth_low_q25": interior_idx[(dep_int <= dep_lo_thresh)],
        "texture_high_depth_high": interior_idx[(tex_int >= tex_hi_thresh) & (dep_int >= dep_hi_thresh)],
        "texture_low_depth_low": interior_idx[(tex_int <= tex_lo_thresh) & (dep_int <= dep_lo_thresh)],
    }

    print(f"  Group sizes: " + ", ".join(f"{k}={len(v)}" for k, v in groups.items()))
    print(f"  Setup took {time.time()-t0:.1f}s")

    max_steps = max(TIMES)
    all_rows = []
    per_seed_rows = []
    timeseries_rows = []

    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        print(f"\n  Seed {seed}/{N_SEEDS-1}...")

        for gname, candidates in groups.items():
            n_walk = min(WALKERS_PER_GROUP, len(candidates))
            starts = rng.choice(candidates, size=n_walk, replace=True).astype(np.int32)

            traj = random_walks(adj_arr, starts, max_steps, rng)
            res = analyse_walks(traj, verts_x, verts_y, perp_x_orig, perp_y_orig,
                                TIMES, NEAR_RETURN_THRESHOLDS)
            alpha, r2 = fit_diffusion_exponent(traj, verts_x, verts_y, TIMES)

            start_tex = texture[starts]
            final_nodes = traj[:, max_steps]
            final_perp_mis = np.sqrt((perp_x_orig[final_nodes] - perp_x_orig[starts])**2 +
                                     (perp_y_orig[final_nodes] - perp_y_orig[starts])**2)
            sp_tex, _ = spearmanr(start_tex, final_perp_mis)
            start_dep = depth[starts]
            sp_dep, _ = spearmanr(start_dep, final_perp_mis)

            row = {
                "substrate": name, "group": gname, "seed": seed,
                "candidate_count": len(candidates), "walkers": n_walk,
                "alpha_phys_msd": alpha, "alpha_phys_r2": r2,
                "tortuosity_median": res["tortuosity"]["median"],
                "tortuosity_p90": res["tortuosity"]["p90"],
                "final_perp_mismatch_mean": res["final_perp_mismatch_all"],
                "spearman_texture_vs_perp": sp_tex,
                "spearman_depth_vs_perp": sp_dep,
            }
            for thr in NEAR_RETURN_THRESHOLDS:
                t_max = max(t for t in TIMES if t <= max_steps)
                key = (t_max, thr)
                if key in res:
                    row[f"nr_frac_t{t_max}_d{thr}"] = res[key]["near_return_frac"]
                    row[f"nr_n_t{t_max}_d{thr}"] = res[key]["near_return_n"]
                    row[f"nr_mean_perp_t{t_max}_d{thr}"] = res[key]["near_return_mean_perp_mismatch"]
                    row[f"nr_median_perp_t{t_max}_d{thr}"] = res[key]["near_return_median_perp_mismatch"]
            per_seed_rows.append(row)

            for t in TIMES:
                if t > max_steps:
                    continue
                for thr in NEAR_RETURN_THRESHOLDS:
                    key = (t, thr)
                    if key in res:
                        timeseries_rows.append({
                            "substrate": name, "group": gname, "seed": seed,
                            "time": t, "threshold": thr,
                            "phys_msd": res[key]["phys_msd"],
                            "near_return_frac": res[key]["near_return_frac"],
                            "near_return_n": res[key]["near_return_n"],
                            "near_return_mean_perp": res[key]["near_return_mean_perp_mismatch"],
                            "near_return_median_perp": res[key]["near_return_median_perp_mismatch"],
                        })

    # ── shuffled control ──
    print(f"\n  Running shuffled control...")
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed + 10000)
        shuf_idx = rng.permutation(n)
        shuf_perp_x = perp_x_orig[shuf_idx]
        shuf_perp_y = perp_y_orig[shuf_idx]

        for gname in ["all_interior75", "texture_high_q25", "texture_low_q25"]:
            candidates = groups[gname]
            n_walk = min(CONTROL_WALKERS, len(candidates))
            starts = rng.choice(candidates, size=n_walk, replace=True).astype(np.int32)
            traj = random_walks(adj_arr, starts, max_steps, rng)
            res = analyse_walks(traj, verts_x, verts_y, shuf_perp_x, shuf_perp_y,
                                TIMES, NEAR_RETURN_THRESHOLDS)
            alpha, r2 = fit_diffusion_exponent(traj, verts_x, verts_y, TIMES)

            row = {
                "substrate": name, "group": f"SHUFFLED_{gname}", "seed": seed,
                "candidate_count": len(candidates), "walkers": n_walk,
                "alpha_phys_msd": alpha, "alpha_phys_r2": r2,
                "tortuosity_median": res["tortuosity"]["median"],
                "tortuosity_p90": res["tortuosity"]["p90"],
                "final_perp_mismatch_mean": res["final_perp_mismatch_all"],
                "spearman_texture_vs_perp": np.nan,
                "spearman_depth_vs_perp": np.nan,
            }
            t_max = max(t for t in TIMES if t <= max_steps)
            for thr in NEAR_RETURN_THRESHOLDS:
                key = (t_max, thr)
                if key in res:
                    row[f"nr_frac_t{t_max}_d{thr}"] = res[key]["near_return_frac"]
                    row[f"nr_n_t{t_max}_d{thr}"] = res[key]["near_return_n"]
                    row[f"nr_mean_perp_t{t_max}_d{thr}"] = res[key]["near_return_mean_perp_mismatch"]
                    row[f"nr_median_perp_t{t_max}_d{thr}"] = res[key]["near_return_median_perp_mismatch"]
            per_seed_rows.append(row)

    return per_seed_rows, timeseries_rows


# ── run both substrates ───────────────────────────────────────────

all_per_seed = []
all_timeseries = []

for sub in ["AB_N30", "Penrose_N24"]:
    ps, ts = run_substrate(sub)
    all_per_seed.extend(ps)
    all_timeseries.extend(ts)

# ── save CSVs ──────────────────────────────────────────────────────

per_seed_df = pd.DataFrame(all_per_seed)
per_seed_df.to_csv(os.path.join(OUT, "v0_3_per_seed.csv"), index=False)

ts_df = pd.DataFrame(all_timeseries)
ts_df.to_csv(os.path.join(OUT, "v0_3_timeseries.csv"), index=False)

# summary: mean across seeds
real_mask = ~per_seed_df["group"].str.startswith("SHUFFLED")
summary = per_seed_df[real_mask].groupby(["substrate", "group"]).mean(numeric_only=True).reset_index()
summary.to_csv(os.path.join(OUT, "v0_3_summary.csv"), index=False)

shuf_summary = per_seed_df[~real_mask].groupby(["substrate", "group"]).mean(numeric_only=True).reset_index()
shuf_summary.to_csv(os.path.join(OUT, "v0_3_shuffled_summary.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ────────────────────────────────────────────────────────
print("Generating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def make_figures(per_seed_df, ts_df, out_dir):
    real = per_seed_df[~per_seed_df["group"].str.startswith("SHUFFLED")]
    shuf = per_seed_df[per_seed_df["group"].str.startswith("SHUFFLED")]

    nr_col = "nr_mean_perp_t1024_d2.0"
    if nr_col not in real.columns:
        nr_col = [c for c in real.columns if c.startswith("nr_mean_perp_t") and "_d2.0" in c]
        nr_col = nr_col[0] if nr_col else None

    # (a) near-return mismatch by group and substrate
    if nr_col:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
            d = real[real["substrate"] == sub]
            groups_ordered = ["all_interior75", "texture_high_q25", "texture_low_q25",
                              "depth_high_q25", "depth_low_q25",
                              "texture_high_depth_high", "texture_low_depth_low"]
            groups_present = [g for g in groups_ordered if g in d["group"].values]
            means = [d[d["group"]==g][nr_col].mean() for g in groups_present]
            sds = [d[d["group"]==g][nr_col].std() for g in groups_present]
            ax.barh(range(len(groups_present)), means, xerr=sds, capsize=3, color="steelblue", alpha=0.8)
            ax.set_yticks(range(len(groups_present)))
            ax.set_yticklabels(groups_present, fontsize=8)
            ax.set_xlabel("Near-return mean perp mismatch (d≤2)")
            ax.set_title(sub)
        plt.suptitle("(a) Near-return address mismatch by group", fontsize=13)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "fig_a_near_return_mismatch.png"), dpi=150)
        plt.close()

    # (b) high vs low texture gap across seeds
    if nr_col:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
        for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
            d = real[real["substrate"] == sub]
            hi = d[d["group"]=="texture_high_q25"].set_index("seed")[nr_col]
            lo = d[d["group"]=="texture_low_q25"].set_index("seed")[nr_col]
            gap = hi - lo
            ax.bar(gap.index, gap.values, color="coral", alpha=0.8)
            ax.axhline(0, color="black", linewidth=0.5)
            ax.set_xlabel("Seed")
            ax.set_ylabel("High − Low texture mismatch gap")
            ax.set_title(sub)
        plt.suptitle("(b) Texture high–low mismatch gap across seeds", fontsize=13)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "fig_b_texture_gap_by_seed.png"), dpi=150)
        plt.close()

    # (c) physical MSD exponent by group
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
        d = real[real["substrate"] == sub]
        groups_ordered = ["all_interior75", "texture_high_q25", "texture_low_q25",
                          "depth_high_q25", "depth_low_q25"]
        groups_present = [g for g in groups_ordered if g in d["group"].values]
        means = [d[d["group"]==g]["alpha_phys_msd"].mean() for g in groups_present]
        sds = [d[d["group"]==g]["alpha_phys_msd"].std() for g in groups_present]
        ax.barh(range(len(groups_present)), means, xerr=sds, capsize=3, color="seagreen", alpha=0.8)
        ax.set_yticks(range(len(groups_present)))
        ax.set_yticklabels(groups_present, fontsize=8)
        ax.set_xlabel("Physical diffusion exponent α")
        ax.set_title(sub)
    plt.suptitle("(c) Physical MSD exponent by group", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig_c_alpha_by_group.png"), dpi=150)
    plt.close()

    # (d) shuffled control comparison
    if nr_col:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
        for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
            labels = []
            vals = []
            errs = []
            for gname in ["all_interior75", "texture_high_q25", "texture_low_q25"]:
                r = real[(real["substrate"]==sub) & (real["group"]==gname)]
                s = shuf[(shuf["substrate"]==sub) & (shuf["group"]==f"SHUFFLED_{gname}")]
                if nr_col in r.columns and len(r) > 0:
                    labels.append(gname)
                    vals.append(r[nr_col].mean())
                    errs.append(r[nr_col].std())
                    labels.append(f"SHUF_{gname[:8]}")
                    vals.append(s[nr_col].mean() if len(s) > 0 else 0)
                    errs.append(s[nr_col].std() if len(s) > 0 else 0)
            colors = ["steelblue" if not l.startswith("SHUF") else "gray" for l in labels]
            ax.barh(range(len(labels)), vals, xerr=errs, capsize=3, color=colors, alpha=0.8)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(labels, fontsize=7)
            ax.set_xlabel("Near-return mean perp mismatch (d≤2)")
            ax.set_title(sub)
        plt.suptitle("(d) Real vs shuffled-control comparison", fontsize=13)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "fig_d_shuffled_control.png"), dpi=150)
        plt.close()

    print("Figures saved.")


make_figures(per_seed_df, ts_df, OUT)

# ── markdown report ────────────────────────────────────────────────
print("Writing report...")

def write_report(summary, shuf_summary, per_seed_df, out_dir):
    nr_col = "nr_mean_perp_t1024_d2.0"
    if nr_col not in summary.columns:
        nr_col = [c for c in summary.columns if c.startswith("nr_mean_perp_t") and "_d2.0" in c]
        nr_col = nr_col[0] if nr_col else "nr_mean_perp_t1024_d2.0"

    lines = []
    lines.append("# Diffusion–texture address-transport v0.3 validation\n")
    lines.append("## Setup")
    lines.append(f"- Seeds: {N_SEEDS}")
    lines.append(f"- Walkers per group per seed: {WALKERS_PER_GROUP}")
    lines.append(f"- Shuffled-control walkers: {CONTROL_WALKERS}")
    lines.append(f"- Times: {TIMES}")
    lines.append(f"- Near-return thresholds: {NEAR_RETURN_THRESHOLDS}")
    lines.append(f"- Interior fraction: {INTERIOR_FRAC}")
    lines.append(f"- Quartile cutoff: {QUARTILE}\n")

    lines.append("## Summary (mean across seeds)\n")
    lines.append(summary.to_markdown(index=False))

    lines.append("\n## Shuffled control summary\n")
    lines.append(shuf_summary.to_markdown(index=False))

    real = per_seed_df[~per_seed_df["group"].str.startswith("SHUFFLED")]
    lines.append("\n## Key comparisons\n")
    for sub in ["AB_N30", "Penrose_N24"]:
        d = real[real["substrate"] == sub]
        hi = d[d["group"]=="texture_high_q25"][nr_col].values
        lo = d[d["group"]=="texture_low_q25"][nr_col].values
        if len(hi) > 0 and len(lo) > 0:
            gap_mean = np.mean(hi) - np.mean(lo)
            gap_seeds = [h - l for h, l in zip(hi, lo)]
            pos_seeds = sum(1 for g in gap_seeds if g > 0)
            lines.append(f"**{sub} texture high−low gap:** {gap_mean:.4f} "
                          f"(positive in {pos_seeds}/{len(gap_seeds)} seeds)")

    lines.append("\n## Interpretation\n")
    lines.append("This is a classical address-transport proxy. It does not claim Berry curvature, "
                 "does not claim α≈0.553, and should be read as testing whether texture-rich regions "
                 "statistically produce more address residue on near-return paths.\n")
    lines.append("The key question: is the texture high–low gap stable across seeds, and does "
                 "Penrose show a stronger or more stable effect than AB? If the gap disappears "
                 "under shuffled controls or is inconsistent across seeds, the effect is not robust.\n")

    lines.append("## Figures\n")
    lines.append("- `fig_a_near_return_mismatch.png` — near-return address mismatch by group")
    lines.append("- `fig_b_texture_gap_by_seed.png` — high vs low texture gap across seeds")
    lines.append("- `fig_c_alpha_by_group.png` — physical MSD exponent by group")
    lines.append("- `fig_d_shuffled_control.png` — real vs shuffled-control comparison\n")

    with open(os.path.join(out_dir, "v0_3_report.md"), "w") as f:
        f.write("\n".join(lines))

    print("Report written.")


write_report(summary, shuf_summary, per_seed_df, OUT)

print("\n✓ v0.3 validation complete.")
