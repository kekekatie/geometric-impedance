"""
Perp-space directional balance v0.1

The landscape test showed every edge has identical perp-space magnitude (1.0).
The depth effect on walk residue must come from how perp-space DIRECTIONS
are distributed at each vertex. This test measures:

For each vertex:
1. Compute the perp-space displacement vectors to all neighbours
2. Measure their directional balance (do they cancel or align?)
3. Compare directional balance vs hull depth
4. Test whether directional balance predicts walk residue better than depth

If deep vertices have more balanced directions (vectors pointing in all
directions, cancelling each other), that directly explains why walks from
depth produce less perp-space drift.
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
OUT  = os.path.join(BASE, "directional_balance_v0_1_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75
N_DEPTH_BINS  = 50

# For the walk validation
N_SEEDS = 5
WALKERS_PER_SEED = 10_000
MAX_STEPS = 1024
NEAR_RETURN_THRESHOLDS = [2.0, 3.0]


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

    max_deg = max(len(a) for a in adj_arr)
    adj_padded = np.zeros((n, max_deg), dtype=np.int32)
    deg = np.zeros(n, dtype=np.int32)
    for i, a in enumerate(adj_arr):
        d = len(a)
        deg[i] = d
        if d > 0:
            adj_padded[i, :d] = a

    return verts, adj_arr, adj_padded, deg, n


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


def compute_directional_balance(px, py, adj_arr, n):
    """For each vertex, compute how balanced its perp-space edge directions are.

    Metrics:
    - resultant_magnitude: |mean of unit direction vectors|. 0 = perfectly balanced, 1 = all same direction
    - direction_entropy: entropy of angular distribution (higher = more balanced)
    - mean_perp_vector: the actual mean perp displacement vector (net drift direction)
    """
    resultant_mag = np.zeros(n)
    resultant_x = np.zeros(n)
    resultant_y = np.zeros(n)
    direction_spread = np.zeros(n)
    degree = np.zeros(n, dtype=np.int32)

    for i in range(n):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        degree[i] = len(nbrs)

        # Perp-space displacement vectors to neighbours
        dx = px[nbrs] - px[i]
        dy = py[nbrs] - py[i]

        # Normalise to unit vectors
        lengths = np.sqrt(dx**2 + dy**2)
        mask = lengths > 1e-12
        if mask.sum() == 0:
            continue
        ux = np.zeros_like(dx)
        uy = np.zeros_like(dy)
        ux[mask] = dx[mask] / lengths[mask]
        uy[mask] = dy[mask] / lengths[mask]

        # Resultant vector (mean of unit vectors)
        mean_ux = ux.mean()
        mean_uy = uy.mean()
        resultant_mag[i] = np.sqrt(mean_ux**2 + mean_uy**2)
        resultant_x[i] = mean_ux
        resultant_y[i] = mean_uy

        # Angular spread: std of angles
        angles = np.arctan2(uy[mask], ux[mask])
        if len(angles) > 1:
            # Circular standard deviation
            S = np.mean(np.sin(angles))
            C = np.mean(np.cos(angles))
            R = np.sqrt(S**2 + C**2)
            direction_spread[i] = np.sqrt(-2 * np.log(R + 1e-12)) if R < 1 else 0.0
        else:
            direction_spread[i] = 0.0

        # Also compute using raw (non-normalised) vectors for net drift
        resultant_x[i] = dx.mean()
        resultant_y[i] = dy.mean()

    # Recompute resultant_mag from raw vectors (net perp drift per step)
    net_drift = np.sqrt(resultant_x**2 + resultant_y**2)

    return resultant_mag, net_drift, direction_spread, resultant_x, resultant_y, degree


def analyse_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Analysing {name}")
    print(f"{'='*60}")

    verts, adj_arr, adj_padded, deg_arr, n = load_substrate(name)
    vx = verts["x"].values.astype(np.float64)
    vy = verts["y"].values.astype(np.float64)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)
    depth = compute_depth(verts)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh

    print(f"  Total vertices: {n}")
    print(f"  Interior vertices: {int(interior_mask.sum())}")

    # Compute directional balance for all vertices
    resultant_mag, net_drift, dir_spread, res_x, res_y, degree = \
        compute_directional_balance(px, py, adj_arr, n)

    # Build vertex dataframe (interior only)
    idx = np.where(interior_mask)[0]
    vertex_df = pd.DataFrame({
        "vertex_id": idx,
        "substrate": name,
        "depth": depth[idx],
        "resultant_mag": resultant_mag[idx],
        "net_drift": net_drift[idx],
        "direction_spread": dir_spread[idx],
        "resultant_x": res_x[idx],
        "resultant_y": res_y[idx],
        "degree": degree[idx],
    })

    # Key correlations
    sp_depth_resultant, sp_p1 = spearmanr(vertex_df["depth"], vertex_df["resultant_mag"])
    sp_depth_drift, sp_p2 = spearmanr(vertex_df["depth"], vertex_df["net_drift"])
    sp_depth_spread, sp_p3 = spearmanr(vertex_df["depth"], vertex_df["direction_spread"])

    print(f"  Spearman(depth, resultant_mag) = {sp_depth_resultant:.4f} (p={sp_p1:.2e})")
    print(f"  Spearman(depth, net_drift)     = {sp_depth_drift:.4f} (p={sp_p2:.2e})")
    print(f"  Spearman(depth, dir_spread)    = {sp_depth_spread:.4f} (p={sp_p3:.2e})")

    # Bin by depth
    vertex_df["depth_bin"] = pd.cut(vertex_df["depth"], bins=N_DEPTH_BINS)
    bin_stats = vertex_df.groupby("depth_bin", observed=True).agg(
        n=("depth", "size"),
        mean_depth=("depth", "mean"),
        mean_resultant=("resultant_mag", "mean"),
        mean_drift=("net_drift", "mean"),
        mean_spread=("direction_spread", "mean"),
        mean_degree=("degree", "mean"),
    ).reset_index()
    bin_stats["substrate"] = name

    # Shallow vs deep comparison
    shallow = vertex_df[vertex_df["depth"] < 0.2]
    deep = vertex_df[vertex_df["depth"] > 0.8]
    mid = vertex_df[(vertex_df["depth"] >= 0.4) & (vertex_df["depth"] <= 0.6)]

    print(f"  Shallow (depth<0.2): mean resultant = {shallow['resultant_mag'].mean():.6f}, "
          f"mean drift = {shallow['net_drift'].mean():.6f}")
    print(f"  Mid (0.4-0.6):       mean resultant = {mid['resultant_mag'].mean():.6f}, "
          f"mean drift = {mid['net_drift'].mean():.6f}")
    print(f"  Deep (depth>0.8):    mean resultant = {deep['resultant_mag'].mean():.6f}, "
          f"mean drift = {deep['net_drift'].mean():.6f}")

    stats = {
        "substrate": name,
        "n_interior": len(vertex_df),
        "spearman_depth_vs_resultant": sp_depth_resultant,
        "spearman_depth_vs_drift": sp_depth_drift,
        "spearman_depth_vs_spread": sp_depth_spread,
        "mean_resultant_shallow": shallow["resultant_mag"].mean(),
        "mean_resultant_mid": mid["resultant_mag"].mean(),
        "mean_resultant_deep": deep["resultant_mag"].mean(),
        "mean_drift_shallow": shallow["net_drift"].mean(),
        "mean_drift_mid": mid["net_drift"].mean(),
        "mean_drift_deep": deep["net_drift"].mean(),
    }

    # ── Walk validation: does directional balance predict walk residue? ──

    print(f"\n  Running walk validation ({N_SEEDS} seeds, {WALKERS_PER_SEED} walkers)...")
    walk_rows = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        interior_idx = np.where(interior_mask)[0]
        starts = rng.choice(interior_idx, size=WALKERS_PER_SEED, replace=True).astype(np.int32)

        # Vectorised walk
        pos = starts.copy()
        for t in range(MAX_STEPS):
            d = deg_arr[pos]
            r = (rng.random(len(pos)) * d).astype(np.int32)
            r = np.minimum(r, d - 1)
            pos = adj_padded[pos, r]

        phys_dist = np.sqrt((vx[pos] - vx[starts])**2 + (vy[pos] - vy[starts])**2)
        perp_residue = np.sqrt((px[pos] - px[starts])**2 + (py[pos] - py[starts])**2)

        for thr in NEAR_RETURN_THRESHOLDS:
            nr_mask = phys_dist <= thr
            nr_idx = np.where(nr_mask)[0]
            if len(nr_idx) < 10:
                continue

            start_depths = depth[starts[nr_idx]]
            start_resultant = resultant_mag[starts[nr_idx]]
            start_drift = net_drift[starts[nr_idx]]
            start_spread = dir_spread[starts[nr_idx]]
            residues = perp_residue[nr_idx]

            sp_d, _ = spearmanr(start_depths, residues)
            sp_r, _ = spearmanr(start_resultant, residues)
            sp_dr, _ = spearmanr(start_drift, residues)
            sp_sp, _ = spearmanr(start_spread, residues)

            walk_rows.append({
                "substrate": name, "seed": seed, "threshold": thr,
                "n_near_loops": len(nr_idx),
                "spearman_depth_vs_residue": sp_d,
                "spearman_resultant_vs_residue": sp_r,
                "spearman_drift_vs_residue": sp_dr,
                "spearman_spread_vs_residue": sp_sp,
            })

        print(f"    Seed {seed}/{N_SEEDS-1} done")

    walk_df = pd.DataFrame(walk_rows)
    walk_agg = walk_df.groupby(["substrate", "threshold"]).mean(numeric_only=True).reset_index()

    print(f"\n  Walk validation results:")
    for _, row in walk_agg.iterrows():
        print(f"    d≤{row['threshold']}: depth→residue = {row['spearman_depth_vs_residue']:.4f}, "
              f"resultant→residue = {row['spearman_resultant_vs_residue']:.4f}, "
              f"drift→residue = {row['spearman_drift_vs_residue']:.4f}, "
              f"spread→residue = {row['spearman_spread_vs_residue']:.4f}")

    return vertex_df, bin_stats, stats, walk_df, walk_agg


# ── run ──────────────────────────────────────────────────────────────

all_vertices = []
all_bins = []
all_stats = []
all_walks = []
all_walk_agg = []

for sub in ["AB_N30", "Penrose_N24"]:
    vdf, bdf, stats, wdf, wagg = analyse_substrate(sub)
    all_vertices.append(vdf)
    all_bins.append(bdf)
    all_stats.append(stats)
    all_walks.append(wdf)
    all_walk_agg.append(wagg)

vertex_df = pd.concat(all_vertices, ignore_index=True)
bin_df = pd.concat(all_bins, ignore_index=True)
stats_df = pd.DataFrame(all_stats)
walk_df = pd.concat(all_walks, ignore_index=True)
walk_agg = pd.concat(all_walk_agg, ignore_index=True)

vertex_df.to_csv(os.path.join(OUT, "vertex_balance.csv"), index=False)
bin_df.to_csv(os.path.join(OUT, "depth_bin_balance.csv"), index=False)
stats_df.to_csv(os.path.join(OUT, "balance_stats.csv"), index=False)
walk_df.to_csv(os.path.join(OUT, "walk_validation.csv"), index=False)
walk_agg.to_csv(os.path.join(OUT, "walk_validation_agg.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ──────────────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) THE KEY FIGURE: Depth vs resultant magnitude (directional balance)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(bd["mean_depth"], bd["mean_resultant"], "o-",
            linewidth=2.5, markersize=7, color=color)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean resultant magnitude\n(0=balanced, 1=all same direction)", fontsize=11)
    ax.set_title(sub, fontsize=14)
    sp = stats_df[stats_df["substrate"] == sub]["spearman_depth_vs_resultant"].values[0]
    ax.text(0.05, 0.95, f"Spearman = {sp:.4f}", transform=ax.transAxes,
            fontsize=11, va="top", fontweight="bold")
plt.suptitle("(1) DIRECTIONAL BALANCE: Do deep vertices have more balanced perp-space directions?",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_depth_vs_directional_balance.png"), dpi=150)
plt.close()

# (2) Net drift vs depth
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(bd["mean_depth"], bd["mean_drift"], "o-",
            linewidth=2.5, markersize=7, color=color)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean net perp-space drift per step", fontsize=11)
    ax.set_title(sub, fontsize=14)
    sp = stats_df[stats_df["substrate"] == sub]["spearman_depth_vs_drift"].values[0]
    ax.text(0.05, 0.95, f"Spearman = {sp:.4f}", transform=ax.transAxes,
            fontsize=11, va="top", fontweight="bold")
plt.suptitle("(2) NET DRIFT: Do shallow vertices push the address in one direction?",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_depth_vs_net_drift.png"), dpi=150)
plt.close()

# (3) Scatter: depth vs resultant (all vertices)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[vertex_df["substrate"] == sub]
    ax.hexbin(vd["depth"], vd["resultant_mag"], gridsize=60,
              cmap="YlOrRd", mincnt=1)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Resultant magnitude", fontsize=12)
    ax.set_title(sub, fontsize=14)
    plt.colorbar(ax.collections[0], ax=ax, label="Count")
plt.suptitle("(3) Vertex-level density: depth vs directional balance", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_depth_balance_density.png"), dpi=150)
plt.close()

# (4) THE PREDICTION HORSE RACE: which predicts walk residue better?
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
predictors = ["spearman_depth_vs_residue", "spearman_resultant_vs_residue",
              "spearman_drift_vs_residue", "spearman_spread_vs_residue"]
pred_labels = ["Depth", "Resultant\n(direction balance)", "Net drift", "Direction\nspread"]

for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    wa = walk_agg[walk_agg["substrate"] == sub]
    for _, row in wa.iterrows():
        thr = row["threshold"]
        vals = [row[p] for p in predictors]
        y_pos = np.arange(len(pred_labels))
        ax.barh(y_pos, vals, alpha=0.7, label=f"d≤{thr}")
    ax.set_yticks(np.arange(len(pred_labels)))
    ax.set_yticklabels(pred_labels, fontsize=10)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Spearman correlation with walk residue", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=10)
plt.suptitle("(4) HORSE RACE: What predicts walk residue best?", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_predictor_horse_race.png"), dpi=150)
plt.close()

# (5) Perp-space map coloured by directional balance
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[vertex_df["substrate"] == sub]
    sc = ax.scatter(vd["resultant_x"], vd["resultant_y"],
                    c=vd["depth"], s=2, cmap="viridis", alpha=0.5)
    ax.set_xlabel("Mean perp displacement X", fontsize=11)
    ax.set_ylabel("Mean perp displacement Y", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.set_aspect("equal")
    plt.colorbar(sc, ax=ax, label="Hull depth")
plt.suptitle("(5) Perp-space drift vectors coloured by depth", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_drift_vectors_by_depth.png"), dpi=150)
plt.close()

# (6) Substrate comparison: balance curves overlaid
fig, ax = plt.subplots(figsize=(10, 6))
for sub, color, marker in [("AB_N30", "steelblue", "o"), ("Penrose_N24", "coral", "s")]:
    bd = bin_df[bin_df["substrate"] == sub]
    ax.plot(bd["mean_depth"], bd["mean_resultant"], f"{marker}-",
            linewidth=2.5, markersize=7, color=color, label=sub)
ax.set_xlabel("Hull depth", fontsize=12)
ax.set_ylabel("Mean resultant magnitude (directional balance)", fontsize=12)
ax.set_title("Directional balance landscape: AB vs Penrose", fontsize=14)
ax.legend(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_substrate_comparison.png"), dpi=150)
plt.close()

# (7) Degree vs directional balance (control)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[vertex_df["substrate"] == sub]
    deg_groups = vd.groupby("degree").agg(
        mean_resultant=("resultant_mag", "mean"),
        mean_depth=("depth", "mean"),
        n=("depth", "size"),
    ).reset_index()
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.bar(deg_groups["degree"], deg_groups["mean_resultant"],
           color=color, alpha=0.7, label="Resultant mag")
    ax2 = ax.twinx()
    ax2.plot(deg_groups["degree"], deg_groups["mean_depth"], "ko-",
             linewidth=1.5, markersize=5, label="Mean depth")
    ax2.set_ylabel("Mean depth", fontsize=10)
    ax2.legend(loc="upper right", fontsize=9)
    ax.set_xlabel("Vertex degree", fontsize=11)
    ax.set_ylabel("Mean resultant magnitude", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(loc="upper left", fontsize=9)
plt.suptitle("(7) Directional balance by degree (control)", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_7_degree_vs_balance.png"), dpi=150)
plt.close()


# ── report ───────────────────────────────────────────────────────────

print("\nGenerating report...")

report = ["# Perp-space directional balance v0.1\n"]
report.append("## Core question")
report.append("The landscape test showed every edge has the same perp-space magnitude.")
report.append("Does the DIRECTION of perp-space edges vary with depth? Do deep vertices")
report.append("have more balanced directional options (explaining the walk cancellation effect)?\n")

report.append("## Setup")
report.append("- No walks for the main analysis (pure geometry)")
report.append(f"- Walk validation: {N_SEEDS} seeds, {WALKERS_PER_SEED} walkers/seed, {MAX_STEPS} steps")
report.append(f"- Interior vertices only ({INTERIOR_FRAC*100:.0f}th percentile)")
report.append(f"- Depth bins: {N_DEPTH_BINS}\n")

report.append("## Directional balance metrics")
report.append("- **Resultant magnitude**: |mean of unit direction vectors to neighbours|.")
report.append("  0 = perfectly balanced (vectors cancel), 1 = all point same way")
report.append("- **Net drift**: |mean of raw perp displacement vectors|.")
report.append("  Expected perp-space displacement per random step from this vertex")
report.append("- **Direction spread**: circular std of edge angles in perp-space\n")

report.append("## Summary\n")
report.append(stats_df.to_markdown(index=False))
report.append("")

report.append("## Walk validation: predictor horse race\n")
report.append(walk_agg.to_markdown(index=False))
report.append("")

report.append("## Key results\n")
for _, s in stats_df.iterrows():
    sub = s["substrate"]
    report.append(f"### {sub}\n")
    report.append(f"  - Spearman(depth, resultant) = {s['spearman_depth_vs_resultant']:.4f}")
    report.append(f"  - Spearman(depth, net_drift) = {s['spearman_depth_vs_drift']:.4f}")
    report.append(f"  - Shallow resultant: {s['mean_resultant_shallow']:.6f}")
    report.append(f"  - Mid resultant: {s['mean_resultant_mid']:.6f}")
    report.append(f"  - Deep resultant: {s['mean_resultant_deep']:.6f}")
    report.append(f"  - Shallow drift: {s['mean_drift_shallow']:.6f}")
    report.append(f"  - Deep drift: {s['mean_drift_deep']:.6f}")
    report.append("")

report.append("## Interpretation\n")
report.append("- If resultant decreases with depth: deep vertices have more balanced")
report.append("  perp-space directions → walks from depth cancel more → less residue")
report.append("- If resultant is flat: directional balance doesn't explain the depth effect")
report.append("- Horse race: if balance/drift predicts walk residue better than depth,")
report.append("  it's the more fundamental variable\n")

report.append("## Figures\n")
report.append("1. fig_1 — Depth vs directional balance (THE KEY)")
report.append("2. fig_2 — Depth vs net drift")
report.append("3. fig_3 — Density plot: depth vs balance")
report.append("4. fig_4 — HORSE RACE: which predicts walk residue best?")
report.append("5. fig_5 — Drift vectors in perp-space, coloured by depth")
report.append("6. fig_6 — Substrate comparison")
report.append("7. fig_7 — Degree control")

with open(os.path.join(OUT, "directional_balance_v0_1_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll done! Results in {OUT}")
