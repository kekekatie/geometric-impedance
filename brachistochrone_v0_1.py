"""
Brachistochrone dip profile analysis v0.1

Among dip-and-return near-loop walkers (which already have low residue),
does the SHAPE of the depth dip predict how clean the address recovery is?

Key metrics:
- Dip asymmetry: fast descent vs fast ascent
- Dip sharpness: V-dip (brief minimum) vs U-dip (lingering at minimum)
- Dip timing: early dip vs late dip
- Natural gradient following: do smooth-gradient walkers recover better?
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
OUT  = os.path.join(BASE, "brachistochrone_v0_1_results")
os.makedirs(OUT, exist_ok=True)

N_SEEDS          = 10
WALKERS_PER_SEED = 30_000
MAX_STEPS        = 1024
NEAR_RETURN_THRESHOLDS = [2.0, 3.0]
INTERIOR_FRAC    = 0.75
DIP_THRESHOLD    = 0.15
SAMPLE_PER_SEED  = 3000

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
    n_w = len(starts)
    traj = np.zeros((n_w, max_steps + 1), dtype=np.int32)
    traj[:, 0] = starts
    pos = starts.copy()
    for t in range(1, max_steps + 1):
        for w in range(n_w):
            nbrs = adj_arr[pos[w]]
            if len(nbrs) > 0:
                pos[w] = rng.choice(nbrs)
            traj[w, t] = pos[w]
    return traj


def analyse_dip_shape(depth_profile):
    """Characterise the shape of the depth dip for a single walker."""
    n = len(depth_profile)
    start_d = depth_profile[0]
    min_idx = np.argmin(depth_profile)
    min_d = depth_profile[min_idx]
    final_d = depth_profile[-1]
    excursion = start_d - min_d

    if excursion < DIP_THRESHOLD:
        return None

    # Dip asymmetry: descent steps vs ascent steps
    descent_steps = min_idx
    ascent_steps = n - 1 - min_idx
    if descent_steps + ascent_steps == 0:
        asymmetry = 0.0
    else:
        asymmetry = (ascent_steps - descent_steps) / (descent_steps + ascent_steps)
    # asymmetry > 0 = fast descent, slow return (brachistochrone-like)
    # asymmetry < 0 = slow descent, fast return
    # asymmetry ~ 0 = symmetric

    # Dip timing: where in the walk did the minimum occur? (0=start, 1=end)
    dip_timing = min_idx / (n - 1) if n > 1 else 0.5

    # Dip sharpness: fraction of path spent within 20% of the minimum depth
    near_min_thresh = min_d + 0.2 * excursion
    steps_near_min = np.sum(depth_profile <= near_min_thresh)
    dip_sharpness = 1.0 - (steps_near_min / n)
    # high sharpness = V-dip (brief minimum), low sharpness = U-dip (lingering)

    # Depth recovery: how much of the excursion was recovered?
    recovery = (final_d - min_d) / (excursion + 1e-12)

    # Gradient smoothness: how smooth was the descent?
    if descent_steps > 1:
        descent_profile = depth_profile[:min_idx + 1]
        descent_diffs = np.diff(descent_profile)
        descent_smoothness = 1.0 - np.std(descent_diffs) / (np.abs(np.mean(descent_diffs)) + 1e-12)
    else:
        descent_smoothness = 0.0

    if ascent_steps > 1:
        ascent_profile = depth_profile[min_idx:]
        ascent_diffs = np.diff(ascent_profile)
        ascent_smoothness = 1.0 - np.std(ascent_diffs) / (np.abs(np.mean(ascent_diffs)) + 1e-12)
    else:
        ascent_smoothness = 0.0

    return {
        "descent_steps": descent_steps,
        "ascent_steps": ascent_steps,
        "asymmetry": asymmetry,
        "dip_timing": dip_timing,
        "dip_sharpness": dip_sharpness,
        "excursion": excursion,
        "min_depth": min_d,
        "recovery": np.clip(recovery, 0, 2),
        "descent_smoothness": descent_smoothness,
        "ascent_smoothness": ascent_smoothness,
        "start_depth": start_d,
        "final_depth": final_d,
    }


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
    dip_rows = []

    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        starts = rng.choice(interior_idx, size=WALKERS_PER_SEED, replace=True).astype(np.int32)
        traj = random_walks_full(adj_arr, starts, MAX_STEPS, rng)

        depth_profiles = depth[traj]
        sx, sy = vx[starts], vy[starts]
        spx, spy = px[starts], py[starts]

        final = traj[:, MAX_STEPS]
        phys_dist = np.sqrt((vx[final] - sx)**2 + (vy[final] - sy)**2)
        perp_residue = np.sqrt((px[final] - spx)**2 + (py[final] - spy)**2)

        for thr in NEAR_RETURN_THRESHOLDS:
            nr_mask = phys_dist <= thr
            nr_indices = np.where(nr_mask)[0]
            nr_n = len(nr_indices)
            if nr_n == 0:
                continue

            # Analyse dip shapes for all near-return walkers
            dip_data = []
            for w in nr_indices:
                shape = analyse_dip_shape(depth_profiles[w])
                if shape is not None:
                    shape["perp_residue"] = perp_residue[w]
                    shape["phys_dist"] = phys_dist[w]
                    shape["walker_id"] = int(w)
                    dip_data.append(shape)

            n_dippers = len(dip_data)
            if n_dippers < 5:
                continue

            dip_df = pd.DataFrame(dip_data)

            # Asymmetry splits: brachistochrone-like (fast drop) vs anti-brachy (slow drop)
            asym_med = dip_df["asymmetry"].median()
            brachy_like = dip_df["asymmetry"] > 0.1   # fast descent, slow return
            anti_brachy = dip_df["asymmetry"] < -0.1   # slow descent, fast return
            symmetric = (dip_df["asymmetry"] >= -0.1) & (dip_df["asymmetry"] <= 0.1)

            # Sharpness splits
            sharp_med = dip_df["dip_sharpness"].median()
            v_dip = dip_df["dip_sharpness"] > dip_df["dip_sharpness"].quantile(0.75)
            u_dip = dip_df["dip_sharpness"] < dip_df["dip_sharpness"].quantile(0.25)

            # Timing splits
            early_dip = dip_df["dip_timing"] < 0.33
            mid_dip = (dip_df["dip_timing"] >= 0.33) & (dip_df["dip_timing"] <= 0.66)
            late_dip = dip_df["dip_timing"] > 0.66

            # Correlations
            sp_asym, sp_asym_p = spearmanr(dip_df["asymmetry"], dip_df["perp_residue"])
            sp_sharp, _ = spearmanr(dip_df["dip_sharpness"], dip_df["perp_residue"])
            sp_timing, _ = spearmanr(dip_df["dip_timing"], dip_df["perp_residue"])
            sp_recovery, _ = spearmanr(dip_df["recovery"], dip_df["perp_residue"])
            sp_desc_smooth, _ = spearmanr(dip_df["descent_smoothness"], dip_df["perp_residue"])
            sp_asc_smooth, _ = spearmanr(dip_df["ascent_smoothness"], dip_df["perp_residue"])
            sp_excursion, _ = spearmanr(dip_df["excursion"], dip_df["perp_residue"])

            def safe_mean(series, mask):
                vals = series[mask]
                return vals.mean() if len(vals) > 0 else np.nan

            summary_rows.append({
                "substrate": name, "seed": seed, "threshold": thr,
                "n_near_loops": nr_n, "n_dippers": n_dippers,
                "mean_residue_all_dippers": dip_df["perp_residue"].mean(),
                # Asymmetry splits
                "mean_residue_brachy": safe_mean(dip_df["perp_residue"], brachy_like),
                "mean_residue_anti_brachy": safe_mean(dip_df["perp_residue"], anti_brachy),
                "mean_residue_symmetric": safe_mean(dip_df["perp_residue"], symmetric),
                "n_brachy": int(brachy_like.sum()),
                "n_anti_brachy": int(anti_brachy.sum()),
                "n_symmetric": int(symmetric.sum()),
                # Sharpness splits
                "mean_residue_v_dip": safe_mean(dip_df["perp_residue"], v_dip),
                "mean_residue_u_dip": safe_mean(dip_df["perp_residue"], u_dip),
                # Timing splits
                "mean_residue_early_dip": safe_mean(dip_df["perp_residue"], early_dip),
                "mean_residue_mid_dip": safe_mean(dip_df["perp_residue"], mid_dip),
                "mean_residue_late_dip": safe_mean(dip_df["perp_residue"], late_dip),
                "n_early": int(early_dip.sum()),
                "n_mid": int(mid_dip.sum()),
                "n_late": int(late_dip.sum()),
                # Correlations
                "spearman_asymmetry_vs_residue": sp_asym,
                "spearman_asymmetry_p": sp_asym_p,
                "spearman_sharpness_vs_residue": sp_sharp,
                "spearman_timing_vs_residue": sp_timing,
                "spearman_recovery_vs_residue": sp_recovery,
                "spearman_descent_smooth_vs_residue": sp_desc_smooth,
                "spearman_ascent_smooth_vs_residue": sp_asc_smooth,
                "spearman_excursion_vs_residue": sp_excursion,
                # Means of shape metrics
                "mean_asymmetry": dip_df["asymmetry"].mean(),
                "mean_sharpness": dip_df["dip_sharpness"].mean(),
                "mean_timing": dip_df["dip_timing"].mean(),
                "mean_excursion": dip_df["excursion"].mean(),
                "mean_recovery": dip_df["recovery"].mean(),
            })

            # Sample dip-level rows
            n_sample = min(SAMPLE_PER_SEED, n_dippers)
            sample_idx = rng.choice(n_dippers, size=n_sample, replace=False) if n_dippers > n_sample else np.arange(n_dippers)
            for i in sample_idx:
                row = dip_data[i].copy()
                row["substrate"] = name
                row["seed"] = seed
                row["threshold"] = thr
                dip_rows.append(row)

        print(f"  Seed {seed}/{N_SEEDS-1} done")

    return summary_rows, dip_rows


# ── run ────────────────────────────────────────────────────────────

all_summary = []
all_dips = []
for sub in ["AB_N30", "Penrose_N24"]:
    s, d = analyse_substrate(sub)
    all_summary.extend(s)
    all_dips.extend(d)

summary_df = pd.DataFrame(all_summary)
summary_df.to_csv(os.path.join(OUT, "brachistochrone_per_seed.csv"), index=False)

dips_df = pd.DataFrame(all_dips)
dips_df.to_csv(os.path.join(OUT, "brachistochrone_dip_samples.csv"), index=False)

agg = summary_df.groupby(["substrate", "threshold"]).mean(numeric_only=True).reset_index()
agg.to_csv(os.path.join(OUT, "brachistochrone_summary.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ────────────────────────────────────────────────────────
print("Generating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) THE KEY FIGURE: Brachistochrone vs anti-brachistochrone vs symmetric
fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_brachy"], "o-",
            label="Fast drop, slow return", color="crimson", linewidth=2.5, markersize=9)
    ax.plot(d["threshold"], d["mean_residue_symmetric"], "D-",
            label="Symmetric dip", color="goldenrod", linewidth=2, markersize=8)
    ax.plot(d["threshold"], d["mean_residue_anti_brachy"], "s-",
            label="Slow drop, fast return", color="navy", linewidth=2.5, markersize=9)
    ax.plot(d["threshold"], d["mean_residue_all_dippers"], "^--",
            label="All dippers", color="gray", linewidth=1, markersize=7)
    ax.set_xlabel("Near-return threshold", fontsize=11)
    ax.set_ylabel("Mean perp residue", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=9)
plt.suptitle("(1) Does dip shape predict address recovery?", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_brachy_vs_anti.png"), dpi=150)
plt.close()

# (2) V-dip vs U-dip
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_v_dip"], "o-",
            label="V-dip (sharp, brief minimum)", color="purple", linewidth=2)
    ax.plot(d["threshold"], d["mean_residue_u_dip"], "s-",
            label="U-dip (broad, lingering minimum)", color="teal", linewidth=2)
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=9)
plt.suptitle("(2) Sharp V-dip vs broad U-dip", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_v_vs_u_dip.png"), dpi=150)
plt.close()

# (3) Dip timing: early vs mid vs late
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_early_dip"], "o-",
            label="Early dip (< 33%)", color="forestgreen", linewidth=2)
    ax.plot(d["threshold"], d["mean_residue_mid_dip"], "D-",
            label="Mid dip (33-66%)", color="goldenrod", linewidth=2)
    ax.plot(d["threshold"], d["mean_residue_late_dip"], "s-",
            label="Late dip (> 66%)", color="firebrick", linewidth=2)
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=9)
plt.suptitle("(3) When does the dip happen?", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_dip_timing.png"), dpi=150)
plt.close()

# (4) Spearman correlation summary
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
metrics = [
    ("spearman_asymmetry_vs_residue", "Asymmetry\n(+ve = brachy)"),
    ("spearman_sharpness_vs_residue", "Sharpness\n(V vs U)"),
    ("spearman_timing_vs_residue", "Timing\n(early vs late)"),
    ("spearman_recovery_vs_residue", "Recovery\n(depth regained)"),
    ("spearman_descent_smooth_vs_residue", "Descent\nsmoothness"),
    ("spearman_ascent_smooth_vs_residue", "Ascent\nsmoothness"),
    ("spearman_excursion_vs_residue", "Excursion\n(dip depth)"),
]
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    for thr in NEAR_RETURN_THRESHOLDS:
        d = agg[(agg["substrate"] == sub) & (agg["threshold"] == thr)]
        if len(d) == 0:
            continue
        vals = [d[m].values[0] for m, _ in metrics]
        labels = [l for _, l in metrics]
        y_pos = np.arange(len(labels))
        ax.barh(y_pos, vals, alpha=0.7, label=f"d≤{thr}")
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Spearman correlation with perp residue")
    ax.set_title(sub, fontsize=12)
    ax.legend(fontsize=9)
plt.suptitle("(4) What shape features predict address recovery?", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_spearman_shape.png"), dpi=150)
plt.close()

# (5) Scatter: asymmetry vs residue
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = dips_df[(dips_df["substrate"] == sub) & (dips_df["threshold"] == 2.0)]
    if len(d) > 0:
        color = "steelblue" if sub == "AB_N30" else "coral"
        ax.scatter(d["asymmetry"], d["perp_residue"], alpha=0.1, s=8, color=color)
        if len(d) > 20:
            bins = pd.qcut(d["asymmetry"], 10, duplicates="drop")
            binned = d.groupby(bins, observed=True)["perp_residue"].mean()
            centers = d.groupby(bins, observed=True)["asymmetry"].mean()
            ax.plot(centers, binned, "k-o", linewidth=2, markersize=6, label="Binned mean")
            ax.legend()
    ax.axvline(0, color="gray", linestyle=":", linewidth=0.8)
    ax.set_xlabel("Asymmetry (+ve = fast drop, slow return)")
    ax.set_ylabel("Perpendicular residue")
    ax.set_title(sub)
plt.suptitle("(5) Asymmetry vs residue (threshold ≤ 2)", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_asymmetry_scatter.png"), dpi=150)
plt.close()

# (6) Substrate comparison: Penrose vs AB shape sensitivity
fig, ax = plt.subplots(figsize=(10, 6))
shape_metrics = ["spearman_asymmetry_vs_residue", "spearman_sharpness_vs_residue",
                 "spearman_timing_vs_residue", "spearman_recovery_vs_residue",
                 "spearman_excursion_vs_residue"]
shape_labels = ["Asymmetry", "Sharpness", "Timing", "Recovery", "Excursion"]
thr_use = 3.0
ab = agg[(agg["substrate"] == "AB_N30") & (agg["threshold"] == thr_use)]
pen = agg[(agg["substrate"] == "Penrose_N24") & (agg["threshold"] == thr_use)]
if len(ab) > 0 and len(pen) > 0:
    x = np.arange(len(shape_labels))
    w = 0.35
    ab_vals = [abs(ab[m].values[0]) for m in shape_metrics]
    pen_vals = [abs(pen[m].values[0]) for m in shape_metrics]
    ax.bar(x - w/2, ab_vals, w, label="AB_N30", color="steelblue")
    ax.bar(x + w/2, pen_vals, w, label="Penrose_N24", color="coral")
    ax.set_xticks(x)
    ax.set_xticklabels(shape_labels)
    ax.set_ylabel("|Spearman correlation|")
    ax.set_title(f"(6) Shape sensitivity: AB vs Penrose (d≤{thr_use})")
    ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_substrate_shape_sensitivity.png"), dpi=150)
plt.close()

print("Figures saved.")

# ── report ─────────────────────────────────────────────────────────
print("Writing report...")
import tabulate

lines = []
lines.append("# Brachistochrone dip profile analysis v0.1\n")
lines.append("## The hypothesis")
lines.append("The dip from stable/deep to unstable/shallow and back is like a brachistochrone:")
lines.append("fast drop, gradual return. If the shape of the dip matters for address recovery,")
lines.append("then the geometry is acting as an engine — the asymmetry drives reconstruction.\n")

lines.append("## Setup")
lines.append(f"- Seeds: {N_SEEDS}, Walkers/seed: {WALKERS_PER_SEED}, Steps: {MAX_STEPS}")
lines.append(f"- Near-return thresholds: {NEAR_RETURN_THRESHOLDS}")
lines.append(f"- Dip threshold: excursion > {DIP_THRESHOLD}")
lines.append(f"- Asymmetry: (ascent_steps - descent_steps) / total")
lines.append(f"  - Positive = fast descent, slow return (brachistochrone-like)")
lines.append(f"  - Negative = slow descent, fast return")
lines.append(f"  - Near zero = symmetric\n")

lines.append("## Summary (mean across seeds)\n")
lines.append(agg.to_markdown(index=False))

lines.append("\n## Key results\n")
for sub in ["AB_N30", "Penrose_N24"]:
    lines.append(f"### {sub}\n")
    d = agg[agg["substrate"] == sub]
    for _, row in d.iterrows():
        thr = row["threshold"]
        lines.append(f"**d≤{thr}** ({row['n_dippers']:.0f} dippers/seed):")
        lines.append(f"  - Brachistochrone (fast drop): {row['mean_residue_brachy']:.4f}")
        lines.append(f"  - Symmetric: {row['mean_residue_symmetric']:.4f}")
        lines.append(f"  - Anti-brachistochrone (slow drop): {row['mean_residue_anti_brachy']:.4f}")
        lines.append(f"  - V-dip vs U-dip: {row['mean_residue_v_dip']:.4f} vs {row['mean_residue_u_dip']:.4f}")
        lines.append(f"  - Early vs mid vs late dip: {row['mean_residue_early_dip']:.4f} / {row['mean_residue_mid_dip']:.4f} / {row['mean_residue_late_dip']:.4f}")
        lines.append(f"  - Spearman(asymmetry, residue): {row['spearman_asymmetry_vs_residue']:.4f} (p={row['spearman_asymmetry_p']:.4f})")
        lines.append(f"  - Spearman(recovery, residue): {row['spearman_recovery_vs_residue']:.4f}")
        lines.append("")

lines.append("## Interpretation\n")
lines.append("- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.")
lines.append("- Tests whether depth-dip SHAPE predicts address recovery quality.")
lines.append("- The brachistochrone hypothesis: fast drop + slow return = best recovery.")
lines.append("- If shape matters: the geometry IS the engine (asymmetry drives reconstruction).")
lines.append("- If shape doesn't matter: only whether you dipped matters, not how.\n")

lines.append("## Figures\n")
for i, desc in enumerate([
    "Brachistochrone vs anti-brachistochrone vs symmetric (KEY)",
    "V-dip vs U-dip (sharp vs broad)",
    "Dip timing (early vs mid vs late)",
    "Spearman correlation summary for all shape features",
    "Scatter: asymmetry vs residue",
    "Substrate comparison: shape sensitivity AB vs Penrose",
], 1):
    lines.append(f"{i}. fig_{i}_*.png — {desc}")

with open(os.path.join(OUT, "brachistochrone_v0_1_report.md"), "w") as f:
    f.write("\n".join(lines))

print("Report written.")
print("\nDone.")
