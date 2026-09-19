"""
Path-depth profile analysis v0.1

The holonomy proxy v0.1 showed that START depth predicts address residue,
and that this effect scales with loop size in Penrose. This analysis asks
the next question: what happens ALONG the path?

Key question: Do walkers that traverse a larger depth range (dip from deep
to shallow and back) accumulate more perpendicular residue than walkers
that stay at a constant depth level?

If so, "curvature encountered along the path" — not just starting position —
is the relevant quantity. That's closer to real holonomy.
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
OUT  = os.path.join(BASE, "path_depth_profile_v0_1_results")
os.makedirs(OUT, exist_ok=True)

N_SEEDS          = 10
WALKERS_PER_SEED = 20_000
MAX_STEPS        = 1024
NEAR_RETURN_THRESHOLDS = [1.0, 2.0, 3.0]
INTERIOR_FRAC    = 0.75
CONTROL_WALKERS  = 5_000
SAMPLE_PER_SEED  = 2000

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


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


# ── walk with full trajectory ─────────────────────────────────────

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


# ── path depth profile metrics ────────────────────────────────────

def compute_path_profiles(traj, depth, vx, vy, px, py):
    """For each walker, compute depth profile metrics along the full path."""
    n_w, n_t = traj.shape
    n_steps = n_t - 1

    start_depth = depth[traj[:, 0]]
    starts_x, starts_y = vx[traj[:, 0]], vy[traj[:, 0]]
    starts_px, starts_py = px[traj[:, 0]], py[traj[:, 0]]

    # Vectorised depth along path
    depth_profiles = depth[traj]  # (n_w, n_steps+1)

    min_depth = np.min(depth_profiles, axis=1)
    max_depth = np.max(depth_profiles, axis=1)
    mean_depth = np.mean(depth_profiles, axis=1)
    depth_range = max_depth - min_depth

    # Depth excursion: how far below start depth did we go?
    depth_excursion = start_depth - min_depth

    # Number of depth transitions (sign changes in depth derivative)
    depth_diff = np.diff(depth_profiles, axis=1)  # (n_w, n_steps)
    sign_changes = np.sum(np.abs(np.diff(np.sign(depth_diff), axis=1)) > 0, axis=1)

    # Cumulative absolute depth change (how much depth was traversed)
    cum_abs_depth_change = np.sum(np.abs(depth_diff), axis=1)

    # "Dip-and-return" metric: did the walker go shallow and come back deep?
    final_depth = depth[traj[:, -1]]
    dip_return = (depth_excursion > 0.2) & (final_depth > (start_depth - 0.1))

    # Physical near-return
    final_x, final_y = vx[traj[:, -1]], vy[traj[:, -1]]
    phys_dist = np.sqrt((final_x - starts_x)**2 + (final_y - starts_y)**2)

    # Perpendicular residue
    final_px, final_py = px[traj[:, -1]], py[traj[:, -1]]
    perp_residue = np.sqrt((final_px - starts_px)**2 + (final_py - starts_py)**2)

    # Cumulative perpendicular displacement (step-by-step)
    cum_perp = np.zeros(n_w)
    for t in range(1, n_t):
        prev = traj[:, t-1]
        cur = traj[:, t]
        cum_perp += np.sqrt((px[cur] - px[prev])**2 + (py[cur] - py[prev])**2)

    return {
        "start_depth": start_depth,
        "min_depth": min_depth,
        "max_depth": max_depth,
        "mean_depth": mean_depth,
        "depth_range": depth_range,
        "depth_excursion": depth_excursion,
        "sign_changes": sign_changes,
        "cum_abs_depth_change": cum_abs_depth_change,
        "dip_return": dip_return,
        "final_depth": final_depth,
        "phys_dist": phys_dist,
        "perp_residue": perp_residue,
        "cum_perp_path": cum_perp,
    }


# ── main ──────────────────────────────────────────────────────────

def analyse_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Loading {name}")
    print(f"{'='*60}")

    verts, adj_arr, n = load_substrate(name)
    vx = verts["x"].values.astype(np.float64)
    vy = verts["y"].values.astype(np.float64)
    px_arr = verts["perp_x"].values.astype(np.float64)
    py_arr = verts["perp_y"].values.astype(np.float64)
    depth = compute_depth(verts)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_idx = np.where(phys_r <= r_thresh)[0]

    print(f"  Interior nodes: {len(interior_idx)}")

    summary_rows = []
    loop_rows = []

    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        starts = rng.choice(interior_idx, size=WALKERS_PER_SEED, replace=True).astype(np.int32)
        traj = random_walks_full(adj_arr, starts, MAX_STEPS, rng)
        prof = compute_path_profiles(traj, depth, vx, vy, px_arr, py_arr)

        for thr in NEAR_RETURN_THRESHOLDS:
            mask = prof["phys_dist"] <= thr
            nr_n = int(np.sum(mask))
            if nr_n == 0:
                continue

            nr = {k: v[mask] for k, v in prof.items()}

            # Quartile splits on depth_range among near-loops
            if nr_n >= 8:
                dr_q75 = np.percentile(nr["depth_range"], 75)
                dr_q25 = np.percentile(nr["depth_range"], 25)
                high_range = nr["depth_range"] >= dr_q75
                low_range = nr["depth_range"] <= dr_q25

                exc_q75 = np.percentile(nr["depth_excursion"], 75)
                exc_q25 = np.percentile(nr["depth_excursion"], 25)
                high_exc = nr["depth_excursion"] >= exc_q75
                low_exc = nr["depth_excursion"] <= exc_q25

                cum_q75 = np.percentile(nr["cum_abs_depth_change"], 75)
                cum_q25 = np.percentile(nr["cum_abs_depth_change"], 25)
                high_cum = nr["cum_abs_depth_change"] >= cum_q75
                low_cum = nr["cum_abs_depth_change"] <= cum_q25
            else:
                high_range = low_range = np.zeros(nr_n, dtype=bool)
                high_exc = low_exc = np.zeros(nr_n, dtype=bool)
                high_cum = low_cum = np.zeros(nr_n, dtype=bool)

            sp_range, _ = spearmanr(nr["depth_range"], nr["perp_residue"]) if nr_n > 2 else (np.nan, np.nan)
            sp_exc, _ = spearmanr(nr["depth_excursion"], nr["perp_residue"]) if nr_n > 2 else (np.nan, np.nan)
            sp_cum, _ = spearmanr(nr["cum_abs_depth_change"], nr["perp_residue"]) if nr_n > 2 else (np.nan, np.nan)
            sp_start, _ = spearmanr(nr["start_depth"], nr["perp_residue"]) if nr_n > 2 else (np.nan, np.nan)

            dip_mask = nr["dip_return"]
            no_dip_mask = ~nr["dip_return"]

            summary_rows.append({
                "substrate": name, "seed": seed, "threshold": thr,
                "control": "real",
                "n_near_loops": nr_n,
                "mean_perp_residue": np.mean(nr["perp_residue"]),
                "median_perp_residue": np.median(nr["perp_residue"]),
                # Depth range splits
                "mean_residue_high_depth_range": np.mean(nr["perp_residue"][high_range]) if np.sum(high_range) > 0 else np.nan,
                "mean_residue_low_depth_range": np.mean(nr["perp_residue"][low_range]) if np.sum(low_range) > 0 else np.nan,
                # Excursion splits
                "mean_residue_high_excursion": np.mean(nr["perp_residue"][high_exc]) if np.sum(high_exc) > 0 else np.nan,
                "mean_residue_low_excursion": np.mean(nr["perp_residue"][low_exc]) if np.sum(low_exc) > 0 else np.nan,
                # Cumulative depth change splits
                "mean_residue_high_cum_depth": np.mean(nr["perp_residue"][high_cum]) if np.sum(high_cum) > 0 else np.nan,
                "mean_residue_low_cum_depth": np.mean(nr["perp_residue"][low_cum]) if np.sum(low_cum) > 0 else np.nan,
                # Dip-and-return
                "mean_residue_dip_return": np.mean(nr["perp_residue"][dip_mask]) if np.sum(dip_mask) > 0 else np.nan,
                "mean_residue_no_dip": np.mean(nr["perp_residue"][no_dip_mask]) if np.sum(no_dip_mask) > 0 else np.nan,
                "n_dip_return": int(np.sum(dip_mask)),
                "n_no_dip": int(np.sum(no_dip_mask)),
                # Correlations
                "spearman_depth_range_vs_residue": sp_range,
                "spearman_excursion_vs_residue": sp_exc,
                "spearman_cum_depth_vs_residue": sp_cum,
                "spearman_start_depth_vs_residue": sp_start,
                # Means of profile metrics
                "mean_depth_range": np.mean(nr["depth_range"]),
                "mean_depth_excursion": np.mean(nr["depth_excursion"]),
                "mean_cum_abs_depth_change": np.mean(nr["cum_abs_depth_change"]),
            })

            # Sample loop-level data
            nr_indices = np.where(mask)[0]
            n_sample = min(SAMPLE_PER_SEED, nr_n)
            sample_idx = rng.choice(nr_n, size=n_sample, replace=False) if nr_n > n_sample else np.arange(nr_n)
            for i in sample_idx:
                w = nr_indices[i]
                loop_rows.append({
                    "substrate": name, "seed": seed, "threshold": thr,
                    "phys_return_dist": prof["phys_dist"][w],
                    "perp_residue": prof["perp_residue"][w],
                    "start_depth": prof["start_depth"][w],
                    "min_depth": prof["min_depth"][w],
                    "max_depth": prof["max_depth"][w],
                    "depth_range": prof["depth_range"][w],
                    "depth_excursion": prof["depth_excursion"][w],
                    "cum_abs_depth_change": prof["cum_abs_depth_change"][w],
                    "mean_depth": prof["mean_depth"][w],
                    "sign_changes": int(prof["sign_changes"][w]),
                    "dip_return": bool(prof["dip_return"][w]),
                    "cum_perp_path": prof["cum_perp_path"][w],
                })

        print(f"  Seed {seed}/{N_SEEDS-1} done")

    # ── shuffled control ──
    print(f"  Running shuffled controls...")
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed + 10000)
        shuf_idx = rng.permutation(n)
        shuf_px = px_arr[shuf_idx]
        shuf_py = py_arr[shuf_idx]
        shuf_depth = depth[shuf_idx]

        starts = rng.choice(interior_idx, size=CONTROL_WALKERS, replace=True).astype(np.int32)
        traj = random_walks_full(adj_arr, starts, MAX_STEPS, rng)

        # Compute profiles with shuffled depth and perp
        depth_profiles = shuf_depth[traj]
        start_d = depth_profiles[:, 0]
        min_d = np.min(depth_profiles, axis=1)
        depth_range = np.max(depth_profiles, axis=1) - min_d
        depth_exc = start_d - min_d
        cum_abs = np.sum(np.abs(np.diff(depth_profiles, axis=1)), axis=1)

        sx, sy = vx[starts], vy[starts]
        final = traj[:, MAX_STEPS]
        phys_dist = np.sqrt((vx[final] - sx)**2 + (vy[final] - sy)**2)
        perp_residue = np.sqrt((shuf_px[final] - shuf_px[starts])**2 +
                               (shuf_py[final] - shuf_py[starts])**2)

        for thr in NEAR_RETURN_THRESHOLDS:
            mask = phys_dist <= thr
            nr_n = int(np.sum(mask))
            if nr_n == 0:
                continue

            nr_pr = perp_residue[mask]
            nr_dr = depth_range[mask]

            if nr_n >= 8:
                dr_q75 = np.percentile(nr_dr, 75)
                dr_q25 = np.percentile(nr_dr, 25)
                high_range = nr_dr >= dr_q75
                low_range = nr_dr <= dr_q25
            else:
                high_range = low_range = np.zeros(nr_n, dtype=bool)

            sp_range, _ = spearmanr(nr_dr, nr_pr) if nr_n > 2 else (np.nan, np.nan)

            summary_rows.append({
                "substrate": name, "seed": seed, "threshold": thr,
                "control": "SHUFFLED",
                "n_near_loops": nr_n,
                "mean_perp_residue": np.mean(nr_pr),
                "median_perp_residue": np.median(nr_pr),
                "mean_residue_high_depth_range": np.mean(nr_pr[high_range]) if np.sum(high_range) > 0 else np.nan,
                "mean_residue_low_depth_range": np.mean(nr_pr[low_range]) if np.sum(low_range) > 0 else np.nan,
                "mean_residue_high_excursion": np.nan,
                "mean_residue_low_excursion": np.nan,
                "mean_residue_high_cum_depth": np.nan,
                "mean_residue_low_cum_depth": np.nan,
                "mean_residue_dip_return": np.nan,
                "mean_residue_no_dip": np.nan,
                "n_dip_return": 0, "n_no_dip": 0,
                "spearman_depth_range_vs_residue": sp_range,
                "spearman_excursion_vs_residue": np.nan,
                "spearman_cum_depth_vs_residue": np.nan,
                "spearman_start_depth_vs_residue": np.nan,
                "mean_depth_range": np.mean(nr_dr),
                "mean_depth_excursion": np.nan,
                "mean_cum_abs_depth_change": np.nan,
            })

        print(f"  Shuffled seed {seed}/{N_SEEDS-1} done")

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
summary_df.to_csv(os.path.join(OUT, "path_depth_profile_per_seed.csv"), index=False)

loops_df = pd.DataFrame(all_loops)
loops_df.to_csv(os.path.join(OUT, "path_depth_profile_near_loops.csv"), index=False)

real = summary_df[summary_df["control"] == "real"]
agg = real.groupby(["substrate", "threshold"]).mean(numeric_only=True).reset_index()
agg.to_csv(os.path.join(OUT, "path_depth_profile_summary.csv"), index=False)

shuf = summary_df[summary_df["control"] == "SHUFFLED"]
shuf_agg = shuf.groupby(["substrate", "threshold"]).mean(numeric_only=True).reset_index()
shuf_agg.to_csv(os.path.join(OUT, "path_depth_profile_shuffled_summary.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ────────────────────────────────────────────────────────
print("Generating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) Depth range high vs low — residue comparison
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_high_depth_range"], "o-",
            label="High depth range (top 25%)", color="red", linewidth=2)
    ax.plot(d["threshold"], d["mean_residue_low_depth_range"], "s-",
            label="Low depth range (bottom 25%)", color="green", linewidth=2)
    ax.plot(d["threshold"], d["mean_perp_residue"], "^--",
            label="All near-loops", color="gray", linewidth=1)
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=8)
plt.suptitle("(1) Residue by depth range traversed", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_residue_by_depth_range.png"), dpi=150)
plt.close()

# (2) Depth excursion high vs low
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_high_excursion"], "o-",
            label="High excursion (top 25%)", color="darkred", linewidth=2)
    ax.plot(d["threshold"], d["mean_residue_low_excursion"], "s-",
            label="Low excursion (bottom 25%)", color="darkgreen", linewidth=2)
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=8)
plt.suptitle("(2) Residue by depth excursion (how far below start)", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_residue_by_excursion.png"), dpi=150)
plt.close()

# (3) Cumulative depth change high vs low
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_high_cum_depth"], "o-",
            label="High cum. depth change (top 25%)", color="purple", linewidth=2)
    ax.plot(d["threshold"], d["mean_residue_low_cum_depth"], "s-",
            label="Low cum. depth change (bottom 25%)", color="teal", linewidth=2)
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=8)
plt.suptitle("(3) Residue by cumulative depth change along path", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_residue_by_cum_depth.png"), dpi=150)
plt.close()

# (4) Dip-and-return vs no-dip
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    ax.plot(d["threshold"], d["mean_residue_dip_return"], "o-",
            label="Dip & return", color="crimson", linewidth=2)
    ax.plot(d["threshold"], d["mean_residue_no_dip"], "s-",
            label="No significant dip", color="forestgreen", linewidth=2)
    ax.set_xlabel("Near-return threshold")
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=8)
plt.suptitle("(4) Dip-and-return walkers vs non-dipping walkers", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_dip_return.png"), dpi=150)
plt.close()

# (5) Spearman correlations summary
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
metrics = ["spearman_depth_range_vs_residue", "spearman_excursion_vs_residue",
           "spearman_cum_depth_vs_residue", "spearman_start_depth_vs_residue"]
labels = ["Depth range", "Excursion", "Cum. depth Δ", "Start depth"]
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub]
    for thr in NEAR_RETURN_THRESHOLDS:
        row = d[d["threshold"] == thr]
        if len(row) == 0:
            continue
        vals = [row[m].values[0] for m in metrics]
        ax.barh([f"{l}\n(d≤{thr})" for l in labels], vals,
                alpha=0.7, label=f"d≤{thr}")
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Spearman correlation with perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=8)
plt.suptitle("(5) What predicts address residue?", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_spearman_summary.png"), dpi=150)
plt.close()

# (6) Scatter: depth range vs residue from loop-level data
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = loops_df[(loops_df["substrate"] == sub) & (loops_df["threshold"] == 2.0)]
    if len(d) > 0:
        color = "steelblue" if sub == "AB_N30" else "coral"
        ax.scatter(d["depth_range"], d["perp_residue"], alpha=0.1, s=8, color=color)
        if len(d) > 10:
            bins = pd.qcut(d["depth_range"], 10, duplicates="drop")
            binned = d.groupby(bins, observed=True)["perp_residue"].mean()
            bin_centers = d.groupby(bins, observed=True)["depth_range"].mean()
            ax.plot(bin_centers, binned, "k-o", linewidth=2, markersize=6, label="Binned mean")
            ax.legend()
    ax.set_xlabel("Depth range traversed")
    ax.set_ylabel("Perpendicular residue")
    ax.set_title(sub)
plt.suptitle("(6) Residue vs depth range (threshold ≤ 2)", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_scatter_depth_range.png"), dpi=150)
plt.close()

# (7) Real vs shuffled depth-range effect
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    r = agg[agg["substrate"] == sub]
    s = shuf_agg[shuf_agg["substrate"] == sub]
    thrs = r["threshold"].values
    x = np.arange(len(thrs))
    w = 0.2
    ax.bar(x - 1.5*w, r["mean_residue_high_depth_range"].values, w,
           label="Real high range", color="red", alpha=0.7)
    ax.bar(x - 0.5*w, r["mean_residue_low_depth_range"].values, w,
           label="Real low range", color="green", alpha=0.7)
    if "mean_residue_high_depth_range" in s.columns:
        ax.bar(x + 0.5*w, s["mean_residue_high_depth_range"].values, w,
               label="Shuffled high range", color="darkred", alpha=0.4)
        ax.bar(x + 1.5*w, s["mean_residue_low_depth_range"].values, w,
               label="Shuffled low range", color="darkgreen", alpha=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels([f"d≤{t}" for t in thrs])
    ax.set_ylabel("Mean perp residue")
    ax.set_title(sub)
    ax.legend(fontsize=7)
plt.suptitle("(7) Real vs shuffled: depth-range effect", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_7_real_vs_shuffled_depth_range.png"), dpi=150)
plt.close()

print("Figures saved.")

# ── report ─────────────────────────────────────────────────────────
print("Writing report...")
import tabulate

lines = []
lines.append("# Path-depth profile analysis v0.1\n")
lines.append("## Core question")
lines.append("Do walkers that traverse a larger depth range (dip from deep to shallow")
lines.append("and back) accumulate more perpendicular residue than walkers that stay")
lines.append("at a constant depth? Is the 'curvature encountered along the path' a")
lines.append("better predictor than starting position alone?\n")

lines.append("## Setup")
lines.append(f"- Seeds: {N_SEEDS}, Walkers/seed: {WALKERS_PER_SEED}, Steps: {MAX_STEPS}")
lines.append(f"- Near-return thresholds: {NEAR_RETURN_THRESHOLDS}")
lines.append(f"- Shuffled control walkers: {CONTROL_WALKERS}\n")

lines.append("## Path-depth metrics computed")
lines.append("- **depth_range**: max depth - min depth along path")
lines.append("- **depth_excursion**: start depth - min depth (how far below start)")
lines.append("- **cum_abs_depth_change**: total absolute depth change along path")
lines.append("- **dip_return**: walker went >0.2 below start depth but ended near start depth")
lines.append("- **sign_changes**: number of depth direction reversals\n")

lines.append("## Summary (real, mean across seeds)\n")
lines.append(agg.to_markdown(index=False))

lines.append("\n## Shuffled control summary\n")
lines.append(shuf_agg.to_markdown(index=False))

lines.append("\n## Key results\n")
for sub in ["AB_N30", "Penrose_N24"]:
    lines.append(f"### {sub}\n")
    d = agg[agg["substrate"] == sub]
    for _, row in d.iterrows():
        thr = row["threshold"]
        lines.append(f"**d≤{thr}** ({row['n_near_loops']:.0f} near-loops/seed):")
        hi_r = row["mean_residue_high_depth_range"]
        lo_r = row["mean_residue_low_depth_range"]
        if not (np.isnan(hi_r) or np.isnan(lo_r)):
            lines.append(f"  - Depth range high vs low: {hi_r:.4f} vs {lo_r:.4f} (gap: {hi_r-lo_r:.4f})")
        hi_e = row["mean_residue_high_excursion"]
        lo_e = row["mean_residue_low_excursion"]
        if not (np.isnan(hi_e) or np.isnan(lo_e)):
            lines.append(f"  - Excursion high vs low: {hi_e:.4f} vs {lo_e:.4f} (gap: {hi_e-lo_e:.4f})")
        dip = row["mean_residue_dip_return"]
        nodip = row["mean_residue_no_dip"]
        if not (np.isnan(dip) or np.isnan(nodip)):
            lines.append(f"  - Dip-return vs no-dip: {dip:.4f} vs {nodip:.4f} (gap: {dip-nodip:.4f})")
        lines.append(f"  - Spearman(depth_range, residue): {row['spearman_depth_range_vs_residue']:.4f}")
        lines.append(f"  - Spearman(start_depth, residue): {row['spearman_start_depth_vs_residue']:.4f}")
        lines.append("")

lines.append("## Interpretation rules\n")
lines.append("- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.")
lines.append("- This tests whether path-level depth traversal predicts address residue")
lines.append("  beyond what starting depth alone explains.")
lines.append("- If depth_range/excursion adds predictive power beyond start_depth,")
lines.append("  that supports 'curvature encountered along path' as the mechanism.")
lines.append("- If start_depth dominates and path metrics add nothing, the effect is")
lines.append("  positional rather than path-dependent.\n")

lines.append("## Figures\n")
for i, desc in enumerate([
    "Residue by depth range traversed (KEY)",
    "Residue by depth excursion",
    "Residue by cumulative depth change",
    "Dip-and-return vs non-dipping walkers",
    "Spearman correlations summary",
    "Scatter: depth range vs residue",
    "Real vs shuffled depth-range effect",
], 1):
    lines.append(f"{i}. fig_{i}_*.png — {desc}")

with open(os.path.join(OUT, "path_depth_profile_v0_1_report.md"), "w") as f:
    f.write("\n".join(lines))

print("Report written.")
print("\nDone.")
