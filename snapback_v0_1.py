"""
Snap-back threshold analysis v0.1

Hypothesis: address recovery at depth isn't gradual — it snaps.
There's a critical number of steps spent at depth below which almost
no recovery happens, and above which recovery is nearly complete.

Tests:
1. Bin dip-and-return walkers by linger duration (steps near minimum depth)
   and plot final residue vs linger duration — look for a step function.
2. Track address residue step-by-step through the dip phase, aligned at the
   minimum depth point — look for a discontinuity in the recovery curve.
3. Compare snap-back dynamics between AB and Penrose.
"""

import os, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "snapback_v0_1_results")
os.makedirs(OUT, exist_ok=True)

N_SEEDS          = 10
WALKERS_PER_SEED = 30_000
MAX_STEPS        = 1024
NEAR_RETURN_THRESHOLDS = [2.0, 3.0]
INTERIOR_FRAC    = 0.75
DIP_THRESHOLD    = 0.15

# For step-by-step tracking, how many steps before/after minimum to record
WINDOW_BEFORE = 200
WINDOW_AFTER  = 400


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


def compute_depth(verts):
    px = verts["perp_x"].values
    py = verts["perp_y"].values
    pts = np.column_stack([px, py])
    try:
        hull = ConvexHull(pts)
        centroid = pts[hull.vertices].mean(axis=0)
        max_dist = np.max(np.linalg.norm(pts[hull.vertices] - centroid, axis=1))
        dist = np.linalg.norm(pts - centroid, axis=1)
        depth = 1.0 - (dist / (max_dist + 1e-12))
        return np.clip(depth, 0, 1)
    except Exception:
        return np.zeros(len(verts))


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


def random_walks_full(adj_arr, starts, max_steps, rng):
    max_deg = max(len(a) for a in adj_arr)
    n_nodes = len(adj_arr)
    adj_padded = np.zeros((n_nodes, max_deg), dtype=np.int32)
    deg = np.zeros(n_nodes, dtype=np.int32)
    for i, a in enumerate(adj_arr):
        d = len(a)
        deg[i] = d
        if d > 0:
            adj_padded[i, :d] = a

    n_w = len(starts)
    traj = np.zeros((n_w, max_steps + 1), dtype=np.int32)
    traj[:, 0] = starts
    pos = starts.copy()
    for t in range(1, max_steps + 1):
        d = deg[pos]
        r = (rng.random(n_w) * d).astype(np.int32)
        r = np.minimum(r, d - 1)
        pos = adj_padded[pos, r]
        traj[:, t] = pos
    return traj


def analyse_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Loading {name}")
    print(f"{'='*60}")

    verts, adj_arr, n = load_substrate(name)
    vx = verts["x"].values.astype(np.float64)
    vy = verts["y"].values.astype(np.float64)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)
    depth = compute_depth(verts)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_idx = np.where(phys_r <= r_thresh)[0]

    print(f"  Interior nodes: {len(interior_idx)}")

    summary_rows = []
    # For aligned curves: accumulate per (substrate, threshold)
    aligned_residue_accum = {}
    aligned_depth_accum = {}
    aligned_counts = {}
    # For linger-bin analysis
    linger_rows = []

    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        starts = rng.choice(interior_idx, size=WALKERS_PER_SEED, replace=True).astype(np.int32)
        traj = random_walks_full(adj_arr, starts, MAX_STEPS, rng)

        depth_profiles = depth[traj]
        perp_x_profiles = px[traj]
        perp_y_profiles = py[traj]

        sx, sy = vx[starts], vy[starts]
        spx, spy = px[starts], py[starts]

        final = traj[:, MAX_STEPS]
        phys_dist = np.sqrt((vx[final] - sx)**2 + (vy[final] - sy)**2)

        for thr in NEAR_RETURN_THRESHOLDS:
            nr_mask = phys_dist <= thr
            nr_indices = np.where(nr_mask)[0]
            if len(nr_indices) == 0:
                continue

            key = (name, thr)
            if key not in aligned_residue_accum:
                window_len = WINDOW_BEFORE + WINDOW_AFTER + 1
                aligned_residue_accum[key] = np.zeros(window_len)
                aligned_depth_accum[key] = np.zeros(window_len)
                aligned_counts[key] = np.zeros(window_len)

            # Vectorised snap-back analysis for all near-return walkers
            nr_depth = depth_profiles[nr_indices]  # (n_nr, steps+1)
            nr_px = perp_x_profiles[nr_indices]
            nr_py = perp_y_profiles[nr_indices]
            nr_spx = spx[nr_indices]
            nr_spy = spy[nr_indices]

            start_d = nr_depth[:, 0]
            min_idx = np.argmin(nr_depth, axis=1)
            min_d = nr_depth[np.arange(len(nr_indices)), min_idx]
            excursion = start_d - min_d
            dip_mask = excursion >= DIP_THRESHOLD
            dip_indices = np.where(dip_mask)[0]

            n_dippers = len(dip_indices)
            for di in dip_indices:
                w_depth = nr_depth[di]
                w_exc = excursion[di]
                w_min_idx = int(min_idx[di])
                w_min_d = min_d[di]

                near_min_thresh = w_min_d + 0.2 * w_exc
                near_min_mask = w_depth <= near_min_thresh
                linger_steps = int(np.sum(near_min_mask))

                runs = np.diff(np.where(np.concatenate(([near_min_mask[0]],
                               near_min_mask[:-1] != near_min_mask[1:],
                               [True])))[0])[::2] if near_min_mask.any() else np.array([0])
                max_consecutive_linger = int(runs.max()) if len(runs) > 0 else 0

                step_residue = np.sqrt((nr_px[di] - nr_spx[di])**2 +
                                       (nr_py[di] - nr_spy[di])**2)

                info = {
                    "linger_steps": linger_steps,
                    "max_consecutive_linger": max_consecutive_linger,
                    "min_idx": w_min_idx,
                    "excursion": float(w_exc),
                    "start_depth": float(start_d[di]),
                    "min_depth": float(w_min_d),
                    "final_residue": float(step_residue[-1]),
                    "residue_at_min": float(step_residue[w_min_idx]),
                    "substrate": name,
                    "seed": seed,
                    "threshold": thr,
                }
                linger_rows.append(info)

                for offset in range(-WINDOW_BEFORE, WINDOW_AFTER + 1):
                    t_idx = w_min_idx + offset
                    if 0 <= t_idx < len(step_residue):
                        arr_idx = offset + WINDOW_BEFORE
                        aligned_residue_accum[key][arr_idx] += step_residue[t_idx]
                        aligned_depth_accum[key][arr_idx] += w_depth[t_idx]
                        aligned_counts[key][arr_idx] += 1

            summary_rows.append({
                "substrate": name, "seed": seed, "threshold": thr,
                "n_near_loops": len(nr_indices), "n_dippers": n_dippers,
            })

        print(f"  Seed {seed}/{N_SEEDS-1} done")

    # Compute mean aligned curves
    aligned_curves = {}
    for key in aligned_residue_accum:
        counts = aligned_counts[key]
        mask = counts > 0
        mean_res = np.full(len(counts), np.nan)
        mean_dep = np.full(len(counts), np.nan)
        mean_res[mask] = aligned_residue_accum[key][mask] / counts[mask]
        mean_dep[mask] = aligned_depth_accum[key][mask] / counts[mask]
        aligned_curves[key] = (mean_res, mean_dep)

    return summary_rows, linger_rows, aligned_curves


# ── run ──────────────────────────────────────────────────────────────

all_summary = []
all_linger = []
all_curves = {}

for sub in ["AB_N30", "Penrose_N24"]:
    s, l, c = analyse_substrate(sub)
    all_summary.extend(s)
    all_linger.extend(l)
    all_curves.update(c)

summary_df = pd.DataFrame(all_summary)
summary_df.to_csv(os.path.join(OUT, "snapback_summary.csv"), index=False)

linger_df = pd.DataFrame(all_linger)
linger_df.to_csv(os.path.join(OUT, "snapback_linger.csv"), index=False)

print(f"\nCSVs saved to {OUT}")
print(f"Total dippers across all seeds/substrates/thresholds: {len(linger_df)}")

# ── analysis: linger duration bins ───────────────────────────────────

print("\n--- Linger duration analysis ---")

LINGER_BINS = [1, 5, 10, 20, 40, 80, 160, 320, 1025]
LINGER_LABELS = ["1-4", "5-9", "10-19", "20-39", "40-79", "80-159", "160-319", "320+"]

bin_rows = []
for sub in ["AB_N30", "Penrose_N24"]:
    for thr in NEAR_RETURN_THRESHOLDS:
        mask = (linger_df["substrate"] == sub) & (linger_df["threshold"] == thr)
        df = linger_df[mask]
        if len(df) == 0:
            continue
        df = df.copy()
        df["linger_bin"] = pd.cut(df["linger_steps"], bins=LINGER_BINS,
                                   labels=LINGER_LABELS, right=False)
        for label in LINGER_LABELS:
            bin_mask = df["linger_bin"] == label
            n_bin = int(bin_mask.sum())
            if n_bin == 0:
                continue
            bin_rows.append({
                "substrate": sub, "threshold": thr, "linger_bin": label,
                "n": n_bin,
                "mean_residue": df.loc[bin_mask, "final_residue"].mean(),
                "median_residue": df.loc[bin_mask, "final_residue"].median(),
                "std_residue": df.loc[bin_mask, "final_residue"].std(),
                "mean_excursion": df.loc[bin_mask, "excursion"].mean(),
                "mean_start_depth": df.loc[bin_mask, "start_depth"].mean(),
            })
        sp, sp_p = spearmanr(df["linger_steps"], df["final_residue"])
        print(f"  {sub} d≤{thr}: Spearman(linger, residue) = {sp:.4f} (p={sp_p:.4f}), N={len(df)}")

        # Also: consecutive linger
        sp_c, sp_c_p = spearmanr(df["max_consecutive_linger"], df["final_residue"])
        print(f"    Spearman(consecutive_linger, residue) = {sp_c:.4f} (p={sp_c_p:.4f})")

bin_df = pd.DataFrame(bin_rows)
bin_df.to_csv(os.path.join(OUT, "snapback_linger_bins.csv"), index=False)

# ── Detect threshold: biggest drop in mean residue between bins ──────

print("\n--- Snap-back threshold detection ---")
threshold_rows = []
for sub in ["AB_N30", "Penrose_N24"]:
    for thr in NEAR_RETURN_THRESHOLDS:
        bd = bin_df[(bin_df["substrate"] == sub) & (bin_df["threshold"] == thr)]
        if len(bd) < 2:
            continue
        residues = bd["mean_residue"].values
        labels = bd["linger_bin"].values
        diffs = np.diff(residues)
        max_drop_idx = np.argmin(diffs)
        threshold_rows.append({
            "substrate": sub, "threshold": thr,
            "biggest_drop_from": labels[max_drop_idx],
            "biggest_drop_to": labels[max_drop_idx + 1],
            "drop_magnitude": float(diffs[max_drop_idx]),
            "residue_before": float(residues[max_drop_idx]),
            "residue_after": float(residues[max_drop_idx + 1]),
        })
        print(f"  {sub} d≤{thr}: biggest residue drop between "
              f"'{labels[max_drop_idx]}' ({residues[max_drop_idx]:.4f}) → "
              f"'{labels[max_drop_idx + 1]}' ({residues[max_drop_idx + 1]:.4f}), "
              f"Δ = {diffs[max_drop_idx]:.4f}")

threshold_df = pd.DataFrame(threshold_rows)
threshold_df.to_csv(os.path.join(OUT, "snapback_threshold_detection.csv"), index=False)

# ── figures ──────────────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) THE KEY FIGURE: Residue vs linger duration bins
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    for thr in NEAR_RETURN_THRESHOLDS:
        bd = bin_df[(bin_df["substrate"] == sub) & (bin_df["threshold"] == thr)]
        if len(bd) == 0:
            continue
        x = np.arange(len(bd))
        ax.plot(x, bd["mean_residue"].values, "o-", linewidth=2.5, markersize=9,
                label=f"d≤{thr} (mean)")
        ax.fill_between(x,
                        bd["mean_residue"].values - bd["std_residue"].values,
                        bd["mean_residue"].values + bd["std_residue"].values,
                        alpha=0.15)
        ax.set_xticks(x)
        ax.set_xticklabels(bd["linger_bin"].values, rotation=45, ha="right", fontsize=9)
    ax.set_xlabel("Steps spent near minimum depth", fontsize=11)
    ax.set_ylabel("Mean final address residue", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=10)
    ax.axhline(1.0, color="gray", linestyle=":", linewidth=0.8, label="_nolegend_")
plt.suptitle("(1) Does address residue drop sharply at a critical linger duration?",
             fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_linger_vs_residue.png"), dpi=150)
plt.close()

# (2) THE ALIGNED CURVE: Step-by-step residue aligned at minimum depth
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
time_axis = np.arange(-WINDOW_BEFORE, WINDOW_AFTER + 1)
for col, sub in enumerate(["AB_N30", "Penrose_N24"]):
    for row, thr in enumerate(NEAR_RETURN_THRESHOLDS):
        ax = axes[row, col]
        key = (sub, thr)
        if key not in all_curves:
            continue
        mean_res, mean_dep = all_curves[key]

        color_res = "steelblue" if sub == "AB_N30" else "coral"
        ax.plot(time_axis, mean_res, color=color_res, linewidth=1.5, label="Address residue")
        ax.set_ylabel("Address residue", color=color_res, fontsize=10)
        ax.tick_params(axis="y", labelcolor=color_res)

        ax2 = ax.twinx()
        ax2.plot(time_axis, mean_dep, color="green", linewidth=1, alpha=0.6, label="Hull depth")
        ax2.set_ylabel("Hull depth", color="green", fontsize=10)
        ax2.tick_params(axis="y", labelcolor="green")

        ax.axvline(0, color="red", linewidth=1.5, linestyle="--", alpha=0.7, label="Min depth")
        ax.set_xlabel("Steps relative to minimum depth point", fontsize=10)
        ax.set_title(f"{sub}, d≤{thr}", fontsize=12)
        ax.legend(loc="upper left", fontsize=8)

plt.suptitle("(2) Address residue trajectory through the dip (aligned at minimum)",
             fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_aligned_residue_trajectory.png"), dpi=150)
plt.close()

# (3) Residue at minimum vs final residue — does the address change DURING the dip?
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    for thr in NEAR_RETURN_THRESHOLDS:
        mask = (linger_df["substrate"] == sub) & (linger_df["threshold"] == thr)
        df = linger_df[mask]
        if len(df) == 0:
            continue
        ax.scatter(df["residue_at_min"], df["final_residue"],
                   alpha=0.05, s=5, label=f"d≤{thr}")
        ax.plot([0, df["residue_at_min"].max()], [0, df["residue_at_min"].max()],
                "k--", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Address residue AT minimum depth", fontsize=11)
    ax.set_ylabel("Final address residue (end of walk)", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=10)
plt.suptitle("(3) Does the address recover AFTER the minimum, or was it already good?",
             fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_residue_at_min_vs_final.png"), dpi=150)
plt.close()

# (4) Consecutive linger vs total linger — which matters more?
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    mask = (linger_df["substrate"] == sub) & (linger_df["threshold"] == 3.0)
    df = linger_df[mask]
    if len(df) == 0:
        continue
    # Bin by total linger
    df = df.copy()
    df["linger_bin"] = pd.cut(df["linger_steps"], bins=LINGER_BINS,
                               labels=LINGER_LABELS, right=False)
    df["consec_bin"] = pd.cut(df["max_consecutive_linger"], bins=LINGER_BINS,
                               labels=LINGER_LABELS, right=False)
    total_means = df.groupby("linger_bin", observed=True)["final_residue"].mean()
    consec_means = df.groupby("consec_bin", observed=True)["final_residue"].mean()

    x1 = np.arange(len(total_means))
    x2 = np.arange(len(consec_means))
    ax.plot(x1, total_means.values, "o-", linewidth=2, color="teal",
            label="Total steps near min", markersize=8)
    ax.plot(x2, consec_means.values, "s--", linewidth=2, color="purple",
            label="Max consecutive steps near min", markersize=8)
    all_labels = sorted(set(total_means.index.tolist() + consec_means.index.tolist()))
    ax.set_xticks(np.arange(max(len(total_means), len(consec_means))))
    longer = total_means if len(total_means) >= len(consec_means) else consec_means
    ax.set_xticklabels(longer.index.tolist(), rotation=45, ha="right", fontsize=9)
    ax.set_xlabel("Steps near minimum depth", fontsize=11)
    ax.set_ylabel("Mean final address residue", fontsize=11)
    ax.set_title(f"{sub}, d≤3.0", fontsize=13)
    ax.legend(fontsize=10)
plt.suptitle("(4) Total vs consecutive linger time: which predicts recovery?",
             fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_total_vs_consecutive_linger.png"), dpi=150)
plt.close()

# (5) Substrate comparison: snap-back curve overlaid
fig, axes = plt.subplots(1, len(NEAR_RETURN_THRESHOLDS), figsize=(14, 6))
if len(NEAR_RETURN_THRESHOLDS) == 1:
    axes = [axes]
for ax, thr in zip(axes, NEAR_RETURN_THRESHOLDS):
    for sub, color in [("AB_N30", "steelblue"), ("Penrose_N24", "coral")]:
        bd = bin_df[(bin_df["substrate"] == sub) & (bin_df["threshold"] == thr)]
        if len(bd) == 0:
            continue
        x = np.arange(len(bd))
        ax.plot(x, bd["mean_residue"].values, "o-", linewidth=2.5, markersize=9,
                color=color, label=sub)
        ax.set_xticks(x)
        ax.set_xticklabels(bd["linger_bin"].values, rotation=45, ha="right", fontsize=9)
    ax.set_xlabel("Steps spent near minimum depth", fontsize=11)
    ax.set_ylabel("Mean final address residue", fontsize=11)
    ax.set_title(f"d≤{thr}", fontsize=13)
    ax.legend(fontsize=10)
    ax.axhline(1.0, color="gray", linestyle=":", linewidth=0.8)
plt.suptitle("(5) Snap-back curve: AB vs Penrose", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_substrate_snapback_comparison.png"), dpi=150)
plt.close()

# (6) Normalised residue recovery curve — residue as fraction of max, vs linger
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    for thr in NEAR_RETURN_THRESHOLDS:
        bd = bin_df[(bin_df["substrate"] == sub) & (bin_df["threshold"] == thr)]
        if len(bd) < 2:
            continue
        vals = bd["mean_residue"].values
        # Normalise: 0 = lowest residue, 1 = highest
        vmin, vmax = vals.min(), vals.max()
        if vmax > vmin:
            normed = (vals - vmin) / (vmax - vmin)
        else:
            normed = np.zeros_like(vals)
        x = np.arange(len(bd))
        ax.plot(x, normed, "o-", linewidth=2.5, markersize=9, label=f"d≤{thr}")
        ax.set_xticks(x)
        ax.set_xticklabels(bd["linger_bin"].values, rotation=45, ha="right", fontsize=9)
    ax.set_xlabel("Steps spent near minimum depth", fontsize=11)
    ax.set_ylabel("Normalised residue (0=best, 1=worst)", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=10)
    ax.axhline(0.5, color="gray", linestyle=":", linewidth=0.8)
plt.suptitle("(6) Normalised recovery curve — is there a step function?", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_normalised_recovery_curve.png"), dpi=150)
plt.close()


# ── report ───────────────────────────────────────────────────────────

print("\nGenerating report...")

report = ["# Snap-back threshold analysis v0.1\n"]
report.append("## Hypothesis")
report.append("Address recovery at depth isn't gradual — it snaps. There's a critical")
report.append("number of steps spent at depth below which almost no recovery happens,")
report.append("and above which recovery is nearly complete.\n")

report.append("## Setup")
report.append(f"- Seeds: {N_SEEDS}, Walkers/seed: {WALKERS_PER_SEED}, Steps: {MAX_STEPS}")
report.append(f"- Near-return thresholds: {NEAR_RETURN_THRESHOLDS}")
report.append(f"- Dip threshold: excursion > {DIP_THRESHOLD}")
report.append(f"- Linger: steps within 20% of excursion above minimum depth")
report.append(f"- Aligned window: {WINDOW_BEFORE} steps before, {WINDOW_AFTER} after minimum\n")

report.append("## Linger duration bins\n")
report.append(bin_df.to_markdown(index=False))
report.append("")

report.append("## Snap-back threshold detection\n")
if len(threshold_df) > 0:
    report.append(threshold_df.to_markdown(index=False))
else:
    report.append("No thresholds detected.")
report.append("")

report.append("## Key results\n")
for sub in ["AB_N30", "Penrose_N24"]:
    report.append(f"### {sub}\n")
    for thr in NEAR_RETURN_THRESHOLDS:
        mask = (linger_df["substrate"] == sub) & (linger_df["threshold"] == thr)
        df = linger_df[mask]
        if len(df) == 0:
            continue
        sp, sp_p = spearmanr(df["linger_steps"], df["final_residue"])
        sp_c, sp_c_p = spearmanr(df["max_consecutive_linger"], df["final_residue"])
        report.append(f"**d≤{thr}** ({len(df)} dippers across {N_SEEDS} seeds):")
        report.append(f"  - Spearman(linger_steps, residue): {sp:.4f} (p={sp_p:.4f})")
        report.append(f"  - Spearman(consecutive_linger, residue): {sp_c:.4f} (p={sp_c_p:.4f})")

        bd = bin_df[(bin_df["substrate"] == sub) & (bin_df["threshold"] == thr)]
        if len(bd) >= 2:
            report.append(f"  - Shortest linger ({bd.iloc[0]['linger_bin']}): "
                         f"residue = {bd.iloc[0]['mean_residue']:.4f}")
            report.append(f"  - Longest linger ({bd.iloc[-1]['linger_bin']}): "
                         f"residue = {bd.iloc[-1]['mean_residue']:.4f}")
            td = threshold_df[(threshold_df["substrate"] == sub) &
                             (threshold_df["threshold"] == thr)]
            if len(td) > 0:
                report.append(f"  - Biggest drop: {td.iloc[0]['biggest_drop_from']} → "
                             f"{td.iloc[0]['biggest_drop_to']} "
                             f"(Δ = {td.iloc[0]['drop_magnitude']:.4f})")
        report.append("")

report.append("## Interpretation rules\n")
report.append("- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.")
report.append("- Tests whether address recovery shows a phase-transition-like")
report.append("  threshold in linger duration at minimum depth.")
report.append("- If there IS a sharp threshold: the stable core needs a minimum")
report.append("  'soak time' before the address resets — like a phase transition.")
report.append("- If recovery is gradual: no threshold, just continuous improvement")
report.append("  with more time at depth.\n")

report.append("## Figures\n")
report.append("1. fig_1_*.png — Residue vs linger duration bins (THE KEY FIGURE)")
report.append("2. fig_2_*.png — Step-by-step residue trajectory aligned at minimum depth")
report.append("3. fig_3_*.png — Residue at minimum vs final residue")
report.append("4. fig_4_*.png — Total vs consecutive linger comparison")
report.append("5. fig_5_*.png — Substrate comparison: snap-back curves overlaid")
report.append("6. fig_6_*.png — Normalised recovery curve (is it a step function?)")

with open(os.path.join(OUT, "snapback_v0_1_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll done! Results in {OUT}")
