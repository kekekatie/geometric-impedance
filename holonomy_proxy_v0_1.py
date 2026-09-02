"""
Holonomy proxy v0.1 — near-loop address residue analysis.

When a path nearly closes in physical space, how much perpendicular/address
displacement remains? Does this scale with loop area? Does depth exposure
predict it? Does Penrose show a stronger effect than AB?
"""

import os, time, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr, zscore
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "holonomy_proxy_v0_1_results")
os.makedirs(OUT, exist_ok=True)

# ── parameters ─────────────────────────────────────────────────────
N_SEEDS          = 10
WALKERS_PER_SEED = 20_000
MAX_STEPS        = 1024
NEAR_RETURN_THRESHOLDS = [1.0, 2.0, 3.0]
INTERIOR_FRAC    = 0.75
CONTROL_WALKERS  = 5_000
SAMPLE_LOOPS_PER_SEED = 2000  # cap saved near-loop rows per seed

# ── loading ────────────────────────────────────────────────────────

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


def compute_texture(verts, adj_arr):
    px = verts["perp_x"].values
    py = verts["perp_y"].values
    scores = np.zeros(len(verts))
    for i in range(len(verts)):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        diffs = np.sqrt((px[nbrs] - px[i])**2 + (py[nbrs] - py[i])**2)
        scores[i] = np.std(diffs) if len(diffs) > 1 else diffs[0]
    z = zscore(scores, nan_policy='omit')
    return np.nan_to_num(z, 0.0)


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


# ── walk + full trajectory recording ──────────────────────────────

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


def loop_area_proxy(traj_x, traj_y):
    """Shoelace formula for signed area of the polygon formed by the path."""
    n = len(traj_x)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n - 1):
        area += traj_x[i] * traj_y[i + 1] - traj_x[i + 1] * traj_y[i]
    area += traj_x[-1] * traj_y[0] - traj_x[0] * traj_y[-1]
    return area / 2.0


# ── main analysis ─────────────────────────────────────────────────

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
    texture = compute_texture(verts, adj_arr)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_idx = np.where(phys_r <= r_thresh)[0]

    print(f"  Interior nodes: {len(interior_idx)}")
    print(f"  Computing walks...")

    summary_rows = []
    loop_rows = []

    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        starts = rng.choice(interior_idx, size=WALKERS_PER_SEED, replace=True).astype(np.int32)
        traj = random_walks_full(adj_arr, starts, MAX_STEPS, rng)

        sx, sy = vx[starts], vy[starts]
        spx, spy = px[starts], py[starts]
        start_depth = depth[starts]
        start_texture = texture[starts]

        # Final positions
        final = traj[:, MAX_STEPS]
        fx, fy = vx[final], vy[final]
        fpx, fpy = px[final], py[final]
        phys_dist = np.sqrt((fx - sx)**2 + (fy - sy)**2)
        perp_disp_x = fpx - spx
        perp_disp_y = fpy - spy
        perp_disp_mag = np.sqrt(perp_disp_x**2 + perp_disp_y**2)

        # Per-walker path stats
        min_depth_visited = np.zeros(WALKERS_PER_SEED)
        mean_depth_visited = np.zeros(WALKERS_PER_SEED)
        visited_shallow = np.zeros(WALKERS_PER_SEED, dtype=bool)
        shallow_thresh = np.percentile(depth[interior_idx], 25)

        for w in range(WALKERS_PER_SEED):
            path_depths = depth[traj[w, :]]
            min_depth_visited[w] = np.min(path_depths)
            mean_depth_visited[w] = np.mean(path_depths)
            visited_shallow[w] = np.any(path_depths <= shallow_thresh)

        # Cumulative perp path for signed displacement
        cum_perp_x = np.zeros(WALKERS_PER_SEED)
        cum_perp_y = np.zeros(WALKERS_PER_SEED)
        for t in range(1, MAX_STEPS + 1):
            prev_nodes = traj[:, t - 1]
            cur_nodes = traj[:, t]
            cum_perp_x += px[cur_nodes] - px[prev_nodes]
            cum_perp_y += py[cur_nodes] - py[prev_nodes]

        for thr in NEAR_RETURN_THRESHOLDS:
            mask = phys_dist <= thr
            nr_n = int(np.sum(mask))
            if nr_n == 0:
                summary_rows.append({
                    "substrate": name, "seed": seed, "threshold": thr,
                    "n_walkers": WALKERS_PER_SEED, "n_near_loops": 0,
                    "mean_perp_residue": np.nan, "median_perp_residue": np.nan,
                    "std_perp_residue": np.nan,
                    "mean_signed_perp_x": np.nan, "mean_signed_perp_y": np.nan,
                    "mean_loop_area": np.nan, "median_loop_area": np.nan,
                    "spearman_area_vs_residue": np.nan,
                    "spearman_area_vs_residue_p": np.nan,
                    "spearman_start_depth_vs_residue": np.nan,
                    "spearman_min_depth_vs_residue": np.nan,
                    "mean_residue_deep_start": np.nan,
                    "mean_residue_shallow_start": np.nan,
                    "mean_residue_visited_shallow": np.nan,
                    "mean_residue_not_visited_shallow": np.nan,
                    "spearman_pathlen_vs_residue": np.nan,
                })
                continue

            nr_perp = perp_disp_mag[mask]
            nr_signed_x = cum_perp_x[mask]
            nr_signed_y = cum_perp_y[mask]
            nr_start_depth = start_depth[mask]
            nr_min_depth = min_depth_visited[mask]
            nr_visited_shallow = visited_shallow[mask]

            # Loop area for near-loops
            nr_indices = np.where(mask)[0]
            areas = np.zeros(nr_n)
            for i, w in enumerate(nr_indices):
                path_x = vx[traj[w, :]]
                path_y = vy[traj[w, :]]
                areas[i] = abs(loop_area_proxy(path_x, path_y))

            # Depth splits
            depth_med = np.median(nr_start_depth)
            deep_mask = nr_start_depth >= depth_med
            shallow_mask = nr_start_depth < depth_med

            # Correlations
            sp_area, sp_area_p = spearmanr(areas, nr_perp) if nr_n > 2 else (np.nan, np.nan)
            sp_sdepth, _ = spearmanr(nr_start_depth, nr_perp) if nr_n > 2 else (np.nan, np.nan)
            sp_mdepth, _ = spearmanr(nr_min_depth, nr_perp) if nr_n > 2 else (np.nan, np.nan)

            summary_rows.append({
                "substrate": name, "seed": seed, "threshold": thr,
                "n_walkers": WALKERS_PER_SEED, "n_near_loops": nr_n,
                "mean_perp_residue": np.mean(nr_perp),
                "median_perp_residue": np.median(nr_perp),
                "std_perp_residue": np.std(nr_perp),
                "mean_signed_perp_x": np.mean(nr_signed_x),
                "mean_signed_perp_y": np.mean(nr_signed_y),
                "mean_loop_area": np.mean(areas),
                "median_loop_area": np.median(areas),
                "spearman_area_vs_residue": sp_area,
                "spearman_area_vs_residue_p": sp_area_p,
                "spearman_start_depth_vs_residue": sp_sdepth,
                "spearman_min_depth_vs_residue": sp_mdepth,
                "mean_residue_deep_start": np.mean(nr_perp[deep_mask]) if np.sum(deep_mask) > 0 else np.nan,
                "mean_residue_shallow_start": np.mean(nr_perp[shallow_mask]) if np.sum(shallow_mask) > 0 else np.nan,
                "mean_residue_visited_shallow": np.mean(nr_perp[nr_visited_shallow]) if np.sum(nr_visited_shallow) > 0 else np.nan,
                "mean_residue_not_visited_shallow": np.mean(nr_perp[~nr_visited_shallow]) if np.sum(~nr_visited_shallow) > 0 else np.nan,
                "spearman_pathlen_vs_residue": np.nan,  # all same path length here
            })

            # Sample loop-level rows
            n_sample = min(SAMPLE_LOOPS_PER_SEED, nr_n)
            sample_idx = rng.choice(nr_n, size=n_sample, replace=False) if nr_n > n_sample else np.arange(nr_n)
            for i in sample_idx:
                w = nr_indices[i]
                loop_rows.append({
                    "substrate": name, "seed": seed, "threshold": thr,
                    "walker_id": int(w),
                    "phys_return_dist": phys_dist[w],
                    "perp_residue": perp_disp_mag[w],
                    "signed_perp_x": cum_perp_x[w],
                    "signed_perp_y": cum_perp_y[w],
                    "loop_area": areas[i],
                    "start_depth": start_depth[w],
                    "min_depth_visited": min_depth_visited[w],
                    "mean_depth_visited": mean_depth_visited[w],
                    "visited_shallow": bool(visited_shallow[w]),
                    "start_texture": start_texture[w],
                })

        print(f"  Seed {seed}/{N_SEEDS-1} done")

    # ── shuffled control ──
    print(f"  Running shuffled controls...")
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed + 10000)
        shuf_idx = rng.permutation(n)
        shuf_px = px[shuf_idx]
        shuf_py = py[shuf_idx]

        starts = rng.choice(interior_idx, size=CONTROL_WALKERS, replace=True).astype(np.int32)
        traj = random_walks_full(adj_arr, starts, MAX_STEPS, rng)

        sx, sy = vx[starts], vy[starts]
        final = traj[:, MAX_STEPS]
        phys_dist = np.sqrt((vx[final] - sx)**2 + (vy[final] - sy)**2)
        perp_disp_mag = np.sqrt((shuf_px[final] - shuf_px[starts])**2 +
                                (shuf_py[final] - shuf_py[starts])**2)

        for thr in NEAR_RETURN_THRESHOLDS:
            mask = phys_dist <= thr
            nr_n = int(np.sum(mask))
            summary_rows.append({
                "substrate": name, "seed": seed, "threshold": thr,
                "n_walkers": CONTROL_WALKERS, "n_near_loops": nr_n,
                "mean_perp_residue": np.mean(perp_disp_mag[mask]) if nr_n > 0 else np.nan,
                "median_perp_residue": np.median(perp_disp_mag[mask]) if nr_n > 0 else np.nan,
                "std_perp_residue": np.std(perp_disp_mag[mask]) if nr_n > 0 else np.nan,
                "mean_signed_perp_x": np.nan, "mean_signed_perp_y": np.nan,
                "mean_loop_area": np.nan, "median_loop_area": np.nan,
                "spearman_area_vs_residue": np.nan,
                "spearman_area_vs_residue_p": np.nan,
                "spearman_start_depth_vs_residue": np.nan,
                "spearman_min_depth_vs_residue": np.nan,
                "mean_residue_deep_start": np.nan,
                "mean_residue_shallow_start": np.nan,
                "mean_residue_visited_shallow": np.nan,
                "mean_residue_not_visited_shallow": np.nan,
                "spearman_pathlen_vs_residue": np.nan,
            })
            # tag as shuffled
            summary_rows[-1]["control"] = "SHUFFLED"

        print(f"  Shuffled seed {seed}/{N_SEEDS-1} done")

    # Tag real rows
    for row in summary_rows:
        if "control" not in row:
            row["control"] = "real"

    return summary_rows, loop_rows


# ── run ────────────────────────────────────────────────────────────

all_summary = []
all_loops = []

for sub in ["AB_N30", "Penrose_N24"]:
    s, l = analyse_substrate(sub)
    all_summary.extend(s)
    all_loops.extend(l)

# ── save CSVs ──────────────────────────────────────────────────────

summary_df = pd.DataFrame(all_summary)
summary_df.to_csv(os.path.join(OUT, "holonomy_proxy_v0_1_per_seed.csv"), index=False)

loops_df = pd.DataFrame(all_loops)
loops_df.to_csv(os.path.join(OUT, "holonomy_proxy_v0_1_near_loops.csv"), index=False)

# Aggregate summary
real = summary_df[summary_df["control"] == "real"]
agg = real.groupby(["substrate", "threshold"]).agg(
    n_near_loops_mean=("n_near_loops", "mean"),
    mean_perp_residue=("mean_perp_residue", "mean"),
    median_perp_residue=("median_perp_residue", "mean"),
    std_perp_residue=("std_perp_residue", "mean"),
    mean_loop_area=("mean_loop_area", "mean"),
    spearman_area_vs_residue=("spearman_area_vs_residue", "mean"),
    spearman_area_vs_residue_p=("spearman_area_vs_residue_p", "mean"),
    spearman_start_depth_vs_residue=("spearman_start_depth_vs_residue", "mean"),
    spearman_min_depth_vs_residue=("spearman_min_depth_vs_residue", "mean"),
    mean_residue_deep_start=("mean_residue_deep_start", "mean"),
    mean_residue_shallow_start=("mean_residue_shallow_start", "mean"),
    mean_residue_visited_shallow=("mean_residue_visited_shallow", "mean"),
    mean_residue_not_visited_shallow=("mean_residue_not_visited_shallow", "mean"),
).reset_index()
agg.to_csv(os.path.join(OUT, "holonomy_proxy_v0_1_summary.csv"), index=False)

shuf = summary_df[summary_df["control"] == "SHUFFLED"]
shuf_agg = shuf.groupby(["substrate", "threshold"]).agg(
    n_near_loops_mean=("n_near_loops", "mean"),
    mean_perp_residue=("mean_perp_residue", "mean"),
    median_perp_residue=("median_perp_residue", "mean"),
).reset_index()
shuf_agg.to_csv(os.path.join(OUT, "holonomy_proxy_v0_1_shuffled_summary.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ────────────────────────────────────────────────────────
print("Generating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) AB vs Penrose near-loop perpendicular residue
fig, ax = plt.subplots(figsize=(10, 6))
for sub, color, marker in [("AB_N30", "steelblue", "o"), ("Penrose_N24", "coral", "s")]:
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_perp_residue"], marker=marker, color=color,
            label=f"{sub} (real)", linewidth=2, markersize=8)
    sd = shuf_agg[shuf_agg["substrate"] == sub]
    ax.plot(sd["threshold"], sd["mean_perp_residue"], marker=marker, color=color,
            label=f"{sub} (shuffled)", linewidth=1.5, linestyle="--", alpha=0.5)
ax.set_xlabel("Near-return threshold (physical distance)")
ax.set_ylabel("Mean perpendicular residue")
ax.set_title("(1) Near-loop address residue: AB vs Penrose")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_residue_by_substrate.png"), dpi=150)
plt.close()

# (2) Residue by start-depth group
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_deep_start"], "o-", label="Deep start", color="navy")
    ax.plot(d["threshold"], d["mean_residue_shallow_start"], "s-", label="Shallow start", color="orange")
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend()
plt.suptitle("(2) Residue by start depth", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_residue_by_start_depth.png"), dpi=150)
plt.close()

# (3) Residue by min-depth visited (shallow exposure)
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_visited_shallow"], "o-",
            label="Visited shallow", color="red")
    ax.plot(d["threshold"], d["mean_residue_not_visited_shallow"], "s-",
            label="Stayed deep", color="green")
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend()
plt.suptitle("(3) Residue by shallow-depth exposure", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_residue_by_shallow_exposure.png"), dpi=150)
plt.close()

# (4) Residue vs loop area (scatter from loop-level data)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = loops_df[(loops_df["substrate"] == sub) & (loops_df["threshold"] == 2.0)]
    if len(d) > 0:
        ax.scatter(d["loop_area"], d["perp_residue"], alpha=0.15, s=10, color="steelblue" if sub == "AB_N30" else "coral")
        if len(d) > 10:
            bins = pd.qcut(d["loop_area"], 10, duplicates="drop")
            binned = d.groupby(bins, observed=True)["perp_residue"].mean()
            bin_centers = d.groupby(bins, observed=True)["loop_area"].mean()
            ax.plot(bin_centers, binned, "k-o", linewidth=2, markersize=6, label="Binned mean")
            ax.legend()
    ax.set_xlabel("Loop area (shoelace proxy)")
    ax.set_ylabel("Perpendicular residue")
    ax.set_title(sub)
plt.suptitle("(4) Residue vs loop area (threshold ≤ 2)", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_residue_vs_area.png"), dpi=150)
plt.close()

# (5) Real vs shuffled control
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    r = agg[agg["substrate"] == sub]
    s = shuf_agg[shuf_agg["substrate"] == sub]
    x = np.arange(len(r))
    w = 0.35
    ax.bar(x - w/2, r["mean_perp_residue"].values, w, label="Real", color="steelblue" if sub == "AB_N30" else "coral")
    ax.bar(x + w/2, s["mean_perp_residue"].values, w, label="Shuffled", color="gray")
    ax.set_xticks(x)
    ax.set_xticklabels([f"d≤{t}" for t in r["threshold"].values])
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend()
plt.suptitle("(5) Real vs shuffled control", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_real_vs_shuffled.png"), dpi=150)
plt.close()

print("Figures saved.")

# ── report ─────────────────────────────────────────────────────────
print("Writing report...")
import tabulate

lines = []
lines.append("# Holonomy proxy v0.1: near-loop address residue\n")
lines.append("## Setup")
lines.append(f"- Seeds: {N_SEEDS}")
lines.append(f"- Walkers per seed: {WALKERS_PER_SEED}")
lines.append(f"- Max steps: {MAX_STEPS}")
lines.append(f"- Near-return thresholds: {NEAR_RETURN_THRESHOLDS}")
lines.append(f"- Interior fraction: {INTERIOR_FRAC}")
lines.append(f"- Shuffled control walkers: {CONTROL_WALKERS}\n")

lines.append("## Core question")
lines.append("When a path nearly closes in physical space, how much perpendicular/address ")
lines.append("displacement remains? Does this scale with loop area? Is it depth-dependent? ")
lines.append("Does Penrose show a stronger effect than AB?\n")

lines.append("## Summary (real, mean across seeds)\n")
lines.append(agg.to_markdown(index=False))

lines.append("\n## Shuffled control summary\n")
lines.append(shuf_agg.to_markdown(index=False))

lines.append("\n## Key comparisons\n")
for thr in NEAR_RETURN_THRESHOLDS:
    ab_r = agg[(agg["substrate"] == "AB_N30") & (agg["threshold"] == thr)]
    pen_r = agg[(agg["substrate"] == "Penrose_N24") & (agg["threshold"] == thr)]
    ab_s = shuf_agg[(shuf_agg["substrate"] == "AB_N30") & (shuf_agg["threshold"] == thr)]
    pen_s = shuf_agg[(shuf_agg["substrate"] == "Penrose_N24") & (shuf_agg["threshold"] == thr)]
    if len(ab_r) > 0 and len(pen_r) > 0:
        lines.append(f"### Threshold d ≤ {thr}")
        lines.append(f"- AB real: {ab_r['mean_perp_residue'].values[0]:.4f}, "
                      f"Penrose real: {pen_r['mean_perp_residue'].values[0]:.4f}")
        if len(ab_s) > 0 and len(pen_s) > 0:
            lines.append(f"- AB shuffled: {ab_s['mean_perp_residue'].values[0]:.4f}, "
                          f"Penrose shuffled: {pen_s['mean_perp_residue'].values[0]:.4f}")
        lines.append(f"- AB area-residue Spearman: {ab_r['spearman_area_vs_residue'].values[0]:.4f}, "
                      f"Penrose: {pen_r['spearman_area_vs_residue'].values[0]:.4f}")
        lines.append(f"- AB deep vs shallow start: {ab_r['mean_residue_deep_start'].values[0]:.4f} vs "
                      f"{ab_r['mean_residue_shallow_start'].values[0]:.4f}")
        lines.append(f"- Penrose deep vs shallow start: {pen_r['mean_residue_deep_start'].values[0]:.4f} vs "
                      f"{pen_r['mean_residue_shallow_start'].values[0]:.4f}")
        lines.append("")

lines.append("## Interpretation rules\n")
lines.append("- This is NOT Berry curvature.")
lines.append("- This does NOT prove quantum holonomy.")
lines.append("- This does NOT chase alpha~0.553.")
lines.append("- This is a classical discrete holonomy proxy: physical near-closure with hidden/address non-closure.")
lines.append("- If shuffled control destroys the signal: strong evidence the effect depends on actual perpendicular-space geometry.")
lines.append("- If the signal remains after shuffling: probably a graph/random-walk artifact, not geometric holonomy.\n")

lines.append("## Figures\n")
lines.append("1. fig_1_residue_by_substrate.png — AB vs Penrose near-loop perpendicular residue")
lines.append("2. fig_2_residue_by_start_depth.png — residue by start-depth group")
lines.append("3. fig_3_residue_by_shallow_exposure.png — residue by min-depth-visited group")
lines.append("4. fig_4_residue_vs_area.png — residue vs loop-area proxy")
lines.append("5. fig_5_real_vs_shuffled.png — real vs shuffled control")

with open(os.path.join(OUT, "holonomy_proxy_v0_1_report.md"), "w") as f:
    f.write("\n".join(lines))

print("Report written.")
print("\nDone.")
