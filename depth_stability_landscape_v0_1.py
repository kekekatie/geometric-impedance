"""
Depth-stability landscape v0.1

No walks. Pure geometry. For every vertex in the tiling, measure:
1. Its hull depth
2. Address mismatch with its neighbours (mean perpendicular-space distance
   to neighbours' perp coordinates)

This maps the static landscape that all the walk-based results have been
probing indirectly. If depth predicts neighbour-address mismatch, the
stability gradient is a geometric fact about the tiling, not a dynamical
effect of random walks.
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
OUT  = os.path.join(BASE, "depth_stability_landscape_v0_1_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75
N_DEPTH_BINS  = 50


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


def analyse_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Analysing {name}")
    print(f"{'='*60}")

    verts, adj_arr, n = load_substrate(name)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)
    depth = compute_depth(verts)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh

    print(f"  Total vertices: {n}")
    print(f"  Interior vertices: {int(interior_mask.sum())}")

    # For every vertex: mean perp-space distance to neighbours
    mean_nbr_mismatch = np.zeros(n)
    max_nbr_mismatch = np.zeros(n)
    std_nbr_mismatch = np.zeros(n)
    mean_nbr_depth_diff = np.zeros(n)
    degree = np.zeros(n, dtype=np.int32)

    for i in range(n):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        degree[i] = len(nbrs)
        dx = px[nbrs] - px[i]
        dy = py[nbrs] - py[i]
        dists = np.sqrt(dx**2 + dy**2)
        mean_nbr_mismatch[i] = dists.mean()
        max_nbr_mismatch[i] = dists.max()
        std_nbr_mismatch[i] = dists.std() if len(dists) > 1 else 0.0
        mean_nbr_depth_diff[i] = np.abs(depth[nbrs] - depth[i]).mean()

    # Build vertex-level dataframe (interior only)
    idx = np.where(interior_mask)[0]
    vertex_df = pd.DataFrame({
        "vertex_id": idx,
        "substrate": name,
        "depth": depth[idx],
        "mean_nbr_mismatch": mean_nbr_mismatch[idx],
        "max_nbr_mismatch": max_nbr_mismatch[idx],
        "std_nbr_mismatch": std_nbr_mismatch[idx],
        "mean_nbr_depth_diff": mean_nbr_depth_diff[idx],
        "degree": degree[idx],
        "perp_x": px[idx],
        "perp_y": py[idx],
    })

    # Bin by depth
    vertex_df["depth_bin"] = pd.cut(vertex_df["depth"], bins=N_DEPTH_BINS)
    bin_stats = vertex_df.groupby("depth_bin", observed=True).agg(
        n=("depth", "size"),
        mean_depth=("depth", "mean"),
        mean_mismatch=("mean_nbr_mismatch", "mean"),
        median_mismatch=("mean_nbr_mismatch", "median"),
        std_mismatch=("mean_nbr_mismatch", "std"),
        mean_max_mismatch=("max_nbr_mismatch", "mean"),
        mean_depth_diff=("mean_nbr_depth_diff", "mean"),
        mean_degree=("degree", "mean"),
    ).reset_index()
    bin_stats["substrate"] = name

    # Correlations
    sp_depth_mismatch, sp_p = spearmanr(vertex_df["depth"], vertex_df["mean_nbr_mismatch"])
    sp_depth_max, _ = spearmanr(vertex_df["depth"], vertex_df["max_nbr_mismatch"])
    sp_depth_std, _ = spearmanr(vertex_df["depth"], vertex_df["std_nbr_mismatch"])

    print(f"  Spearman(depth, mean_nbr_mismatch) = {sp_depth_mismatch:.4f} (p={sp_p:.2e})")
    print(f"  Spearman(depth, max_nbr_mismatch)  = {sp_depth_max:.4f}")
    print(f"  Spearman(depth, std_nbr_mismatch)  = {sp_depth_std:.4f}")
    print(f"  Mean mismatch at depth<0.2: {vertex_df[vertex_df['depth']<0.2]['mean_nbr_mismatch'].mean():.6f}")
    print(f"  Mean mismatch at depth>0.8: {vertex_df[vertex_df['depth']>0.8]['mean_nbr_mismatch'].mean():.6f}")

    stats = {
        "substrate": name,
        "n_interior": len(vertex_df),
        "spearman_depth_vs_mean_mismatch": sp_depth_mismatch,
        "spearman_p": sp_p,
        "spearman_depth_vs_max_mismatch": sp_depth_max,
        "spearman_depth_vs_std_mismatch": sp_depth_std,
        "mean_mismatch_shallow": vertex_df[vertex_df["depth"] < 0.2]["mean_nbr_mismatch"].mean(),
        "mean_mismatch_mid": vertex_df[(vertex_df["depth"] >= 0.4) & (vertex_df["depth"] <= 0.6)]["mean_nbr_mismatch"].mean(),
        "mean_mismatch_deep": vertex_df[vertex_df["depth"] > 0.8]["mean_nbr_mismatch"].mean(),
        "overall_mean_mismatch": vertex_df["mean_nbr_mismatch"].mean(),
        "overall_std_mismatch": vertex_df["mean_nbr_mismatch"].std(),
    }

    return vertex_df, bin_stats, stats


# ── run ──────────────────────────────────────────────────────────────

all_vertices = []
all_bins = []
all_stats = []

for sub in ["AB_N30", "Penrose_N24"]:
    vdf, bdf, stats = analyse_substrate(sub)
    all_vertices.append(vdf)
    all_bins.append(bdf)
    all_stats.append(stats)

vertex_df = pd.concat(all_vertices, ignore_index=True)
bin_df = pd.concat(all_bins, ignore_index=True)
stats_df = pd.DataFrame(all_stats)

vertex_df.to_csv(os.path.join(OUT, "vertex_landscape.csv"), index=False)
bin_df.to_csv(os.path.join(OUT, "depth_bin_stats.csv"), index=False)
stats_df.to_csv(os.path.join(OUT, "landscape_stats.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ──────────────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# (1) THE KEY FIGURE: Depth vs mean neighbour address mismatch (binned)
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(bd["mean_depth"], bd["mean_mismatch"], "o-",
            linewidth=2.5, markersize=7, color=color)
    ax.fill_between(bd["mean_depth"],
                    bd["mean_mismatch"] - bd["std_mismatch"],
                    bd["mean_mismatch"] + bd["std_mismatch"],
                    alpha=0.15, color=color)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean neighbour address mismatch", fontsize=12)
    ax.set_title(sub, fontsize=14)
    sp = stats_df[stats_df["substrate"] == sub]["spearman_depth_vs_mean_mismatch"].values[0]
    ax.text(0.05, 0.95, f"Spearman = {sp:.4f}", transform=ax.transAxes,
            fontsize=11, va="top", fontweight="bold")
plt.suptitle("(1) THE LANDSCAPE: How does address stability change with depth?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_depth_vs_mismatch.png"), dpi=150)
plt.close()

# (2) Scatter: depth vs mismatch (all vertices, density plot)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[vertex_df["substrate"] == sub]
    ax.hexbin(vd["depth"], vd["mean_nbr_mismatch"], gridsize=60,
              cmap="YlOrRd", mincnt=1)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean neighbour address mismatch", fontsize=12)
    ax.set_title(sub, fontsize=14)
    plt.colorbar(ax.collections[0], ax=ax, label="Vertex count")
plt.suptitle("(2) Vertex-level density: depth vs address mismatch", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_depth_mismatch_density.png"), dpi=150)
plt.close()

# (3) Substrate comparison: overlaid binned curves
fig, ax = plt.subplots(figsize=(10, 6))
for sub, color, marker in [("AB_N30", "steelblue", "o"), ("Penrose_N24", "coral", "s")]:
    bd = bin_df[bin_df["substrate"] == sub]
    ax.plot(bd["mean_depth"], bd["mean_mismatch"], f"{marker}-",
            linewidth=2.5, markersize=7, color=color, label=sub)
ax.set_xlabel("Hull depth", fontsize=12)
ax.set_ylabel("Mean neighbour address mismatch", fontsize=12)
ax.set_title("Depth-stability landscape: AB vs Penrose", fontsize=14)
ax.legend(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_substrate_comparison.png"), dpi=150)
plt.close()

# (4) Max neighbour mismatch vs depth (is the worst-case also depth-dependent?)
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(bd["mean_depth"], bd["mean_max_mismatch"], "o-",
            linewidth=2, markersize=6, color=color, label="Max mismatch")
    ax.plot(bd["mean_depth"], bd["mean_mismatch"], "s--",
            linewidth=1.5, markersize=5, color=color, alpha=0.5, label="Mean mismatch")
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Neighbour address mismatch", fontsize=12)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=10)
plt.suptitle("(4) Mean vs max neighbour mismatch by depth", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_max_vs_mean_mismatch.png"), dpi=150)
plt.close()

# (5) Depth gradient: how much does depth change between neighbours?
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(bd["mean_depth"], bd["mean_depth_diff"], "o-",
            linewidth=2.5, markersize=7, color=color)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean |depth difference| with neighbours", fontsize=12)
    ax.set_title(sub, fontsize=13)
plt.suptitle("(5) Depth gradient: how steep is the landscape at each depth?", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_depth_gradient.png"), dpi=150)
plt.close()

# (6) Perp-space map coloured by mismatch (spatial view)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[vertex_df["substrate"] == sub]
    sc = ax.scatter(vd["perp_x"], vd["perp_y"], c=vd["mean_nbr_mismatch"],
                    s=1, cmap="viridis", alpha=0.6)
    ax.set_xlabel("perp_x", fontsize=11)
    ax.set_ylabel("perp_y", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.set_aspect("equal")
    plt.colorbar(sc, ax=ax, label="Mean nbr mismatch")
plt.suptitle("(6) Perpendicular-space map coloured by address stability", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_perp_space_stability_map.png"), dpi=150)
plt.close()

# (7) Degree vs mismatch (control: is this just a degree effect?)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[vertex_df["substrate"] == sub]
    deg_groups = vd.groupby("degree").agg(
        mean_mismatch=("mean_nbr_mismatch", "mean"),
        mean_depth=("depth", "mean"),
        n=("depth", "size"),
    ).reset_index()
    ax.bar(deg_groups["degree"], deg_groups["mean_mismatch"],
           color="steelblue" if sub == "AB_N30" else "coral", alpha=0.7)
    ax2 = ax.twinx()
    ax2.plot(deg_groups["degree"], deg_groups["mean_depth"], "ko-",
             linewidth=1.5, markersize=5, label="Mean depth")
    ax2.set_ylabel("Mean depth", fontsize=10)
    ax2.legend(loc="upper right", fontsize=9)
    ax.set_xlabel("Vertex degree", fontsize=11)
    ax.set_ylabel("Mean neighbour mismatch", fontsize=11)
    ax.set_title(sub, fontsize=13)
plt.suptitle("(7) Is mismatch just a degree effect? (control)", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_7_degree_control.png"), dpi=150)
plt.close()


# ── report ───────────────────────────────────────────────────────────

print("\nGenerating report...")

report = ["# Depth-stability landscape v0.1\n"]
report.append("## Core question")
report.append("Is the depth → address stability relationship a static geometric fact,")
report.append("visible vertex-by-vertex without any random walks?\n")

report.append("## Setup")
report.append("- No walks. No seeds. No randomness.")
report.append(f"- Interior vertices only (physical radius ≤ {INTERIOR_FRAC*100:.0f}th percentile)")
report.append(f"- Depth bins: {N_DEPTH_BINS}")
report.append("- For each vertex: mean perp-space distance to each neighbour's perp coordinates\n")

report.append("## Summary\n")
report.append(stats_df.to_markdown(index=False))
report.append("")

report.append("## Depth-binned statistics\n")
report.append(bin_df.to_markdown(index=False))
report.append("")

report.append("## Key results\n")
for _, s in stats_df.iterrows():
    sub = s["substrate"]
    report.append(f"### {sub}\n")
    report.append(f"  - Spearman(depth, mean_mismatch) = {s['spearman_depth_vs_mean_mismatch']:.4f} (p={s['spearman_p']:.2e})")
    report.append(f"  - Shallow (depth<0.2): mean mismatch = {s['mean_mismatch_shallow']:.6f}")
    report.append(f"  - Mid (0.4-0.6): mean mismatch = {s['mean_mismatch_mid']:.6f}")
    report.append(f"  - Deep (depth>0.8): mean mismatch = {s['mean_mismatch_deep']:.6f}")
    if s['mean_mismatch_deep'] > 0:
        ratio = s['mean_mismatch_shallow'] / s['mean_mismatch_deep']
        report.append(f"  - Shallow/deep ratio: {ratio:.2f}x")
    report.append("")

report.append("## Interpretation rules\n")
report.append("- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.")
report.append("- No walks involved — this is pure tiling geometry.")
report.append("- If depth predicts neighbour mismatch: the stability landscape is a")
report.append("  static geometric fact, not a dynamical walk effect.")
report.append("- The controlled linger experiment (v0.1) showed address residue is")
report.append("  instantaneous and positional. This test maps that landscape directly.\n")

report.append("## Figures\n")
report.append("1. fig_1 — THE KEY: Depth vs mean neighbour mismatch (binned)")
report.append("2. fig_2 — Vertex-level density plot")
report.append("3. fig_3 — Substrate comparison overlaid")
report.append("4. fig_4 — Max vs mean mismatch by depth")
report.append("5. fig_5 — Depth gradient steepness")
report.append("6. fig_6 — Perp-space map coloured by stability")
report.append("7. fig_7 — Degree control (is mismatch just a degree effect?)")

with open(os.path.join(OUT, "depth_stability_landscape_v0_1_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll done! Results in {OUT}")
