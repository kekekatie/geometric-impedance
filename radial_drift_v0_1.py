"""
Radial drift alignment v0.1

Other Claude's dart: the drift vectors form a rotationally symmetric cloud,
so there's no global compass heading. But is the drift RADIAL — does each
vertex's drift vector point outward from the hull centre toward the boundary?

For each vertex:
1. Its perp-space position vector (from hull centroid to vertex)
2. Its drift vector (mean perp displacement to neighbours)
3. The angle between them

If angles cluster near 0°: drift is radial-outward → the arrow points
boundary-ward → "time happens at the edge" gets its orientation.

Also checks: is there chirality in the Penrose pinwheel?
"""

import os, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr, circmean, circstd
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "radial_drift_v0_1_results")
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


def compute_depth_and_centroid(verts):
    px = verts["perp_x"].values
    py = verts["perp_y"].values
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)
    max_dist = np.max(np.linalg.norm(pts[hull.vertices] - centroid, axis=1))
    dist = np.linalg.norm(pts - centroid, axis=1)
    depth = 1.0 - (dist / (max_dist + 1e-12))
    return np.clip(depth, 0, 1), centroid


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


def angle_between(v1x, v1y, v2x, v2y):
    """Signed angle from v1 to v2, in degrees."""
    dot = v1x * v2x + v1y * v2y
    cross = v1x * v2y - v1y * v2x
    return np.degrees(np.arctan2(cross, dot))


def analyse_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Analysing {name}")
    print(f"{'='*60}")

    verts, adj_arr, n = load_substrate(name)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)
    depth, centroid = compute_depth_and_centroid(verts)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh

    print(f"  Interior vertices: {int(interior_mask.sum())}")
    print(f"  Hull centroid: ({centroid[0]:.4f}, {centroid[1]:.4f})")

    # Position vectors: from centroid to each vertex in perp-space
    pos_x = px - centroid[0]
    pos_y = py - centroid[1]
    pos_mag = np.sqrt(pos_x**2 + pos_y**2)

    # Drift vectors: mean perp displacement to neighbours
    drift_x = np.zeros(n)
    drift_y = np.zeros(n)
    drift_mag = np.zeros(n)
    degree = np.zeros(n, dtype=np.int32)

    for i in range(n):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        degree[i] = len(nbrs)
        dx = px[nbrs] - px[i]
        dy = py[nbrs] - py[i]
        drift_x[i] = dx.mean()
        drift_y[i] = dy.mean()
        drift_mag[i] = np.sqrt(drift_x[i]**2 + drift_y[i]**2)

    # Angle between position vector and drift vector
    alignment_angle = angle_between(pos_x, pos_y, drift_x, drift_y)

    # Radial component of drift: projection of drift onto position unit vector
    pos_ux = np.where(pos_mag > 1e-12, pos_x / pos_mag, 0)
    pos_uy = np.where(pos_mag > 1e-12, pos_y / pos_mag, 0)
    radial_drift = drift_x * pos_ux + drift_y * pos_uy  # positive = outward
    tangential_drift = -drift_x * pos_uy + drift_y * pos_ux  # signed tangential

    # Interior only
    idx = np.where(interior_mask)[0]
    vertex_df = pd.DataFrame({
        "vertex_id": idx,
        "substrate": name,
        "depth": depth[idx],
        "drift_mag": drift_mag[idx],
        "alignment_angle": alignment_angle[idx],
        "radial_drift": radial_drift[idx],
        "tangential_drift": tangential_drift[idx],
        "pos_mag": pos_mag[idx],
        "degree": degree[idx],
    })

    # Filter to vertices with meaningful drift (exclude deep balanced ones)
    has_drift = vertex_df["drift_mag"] > 0.01
    drifters = vertex_df[has_drift]

    # Key stats
    mean_angle_all = circmean(np.radians(drifters["alignment_angle"]), high=np.pi, low=-np.pi)
    std_angle_all = circstd(np.radians(drifters["alignment_angle"]), high=np.pi, low=-np.pi)

    shallow = drifters[drifters["depth"] < 0.3]
    deep = drifters[drifters["depth"] > 0.7]

    # Fraction of vertices where drift is outward (angle within ±90°)
    frac_outward_all = (np.abs(drifters["alignment_angle"]) < 90).mean()
    frac_outward_shallow = (np.abs(shallow["alignment_angle"]) < 90).mean() if len(shallow) > 0 else np.nan
    frac_outward_deep = (np.abs(deep["alignment_angle"]) < 90).mean() if len(deep) > 0 else np.nan

    # Mean radial drift by depth
    mean_radial_shallow = shallow["radial_drift"].mean() if len(shallow) > 0 else np.nan
    mean_radial_deep = deep["radial_drift"].mean() if len(deep) > 0 else np.nan

    # Chirality: mean tangential drift (if nonzero → handedness)
    mean_tangential_all = drifters["tangential_drift"].mean()
    mean_tangential_shallow = shallow["tangential_drift"].mean() if len(shallow) > 0 else np.nan
    mean_tangential_deep = deep["tangential_drift"].mean() if len(deep) > 0 else np.nan

    print(f"  Drifters (mag>0.01): {len(drifters)}")
    print(f"  Fraction outward (all): {frac_outward_all:.4f}")
    print(f"  Fraction outward (shallow): {frac_outward_shallow:.4f}")
    print(f"  Fraction outward (deep): {frac_outward_deep:.4f}")
    print(f"  Mean radial drift (shallow): {mean_radial_shallow:.6f}")
    print(f"  Mean radial drift (deep): {mean_radial_deep:.6f}")
    print(f"  Mean tangential drift (all): {mean_tangential_all:.6f}")
    print(f"  Mean tangential drift (shallow): {mean_tangential_shallow:.6f}")
    print(f"  Mean tangential drift (deep): {mean_tangential_deep:.6f}")

    # Spearman: depth vs radial drift
    sp_radial, sp_p = spearmanr(vertex_df["depth"], vertex_df["radial_drift"])
    sp_tangential, sp_tp = spearmanr(vertex_df["depth"], np.abs(vertex_df["tangential_drift"]))
    print(f"  Spearman(depth, radial_drift) = {sp_radial:.4f} (p={sp_p:.2e})")
    print(f"  Spearman(depth, |tangential_drift|) = {sp_tangential:.4f}")

    # Bin by depth
    vertex_df["depth_bin"] = pd.cut(vertex_df["depth"], bins=N_DEPTH_BINS)
    bin_stats = vertex_df.groupby("depth_bin", observed=True).agg(
        n=("depth", "size"),
        mean_depth=("depth", "mean"),
        mean_radial=("radial_drift", "mean"),
        mean_tangential=("tangential_drift", "mean"),
        mean_abs_tangential=("tangential_drift", lambda x: np.abs(x).mean()),
        frac_outward=("alignment_angle", lambda x: (np.abs(x) < 90).mean()),
        mean_drift_mag=("drift_mag", "mean"),
    ).reset_index()
    bin_stats["substrate"] = name

    stats = {
        "substrate": name,
        "n_drifters": len(drifters),
        "frac_outward_all": frac_outward_all,
        "frac_outward_shallow": frac_outward_shallow,
        "frac_outward_deep": frac_outward_deep,
        "mean_radial_shallow": mean_radial_shallow,
        "mean_radial_deep": mean_radial_deep,
        "mean_tangential_all": mean_tangential_all,
        "mean_tangential_shallow": mean_tangential_shallow,
        "mean_tangential_deep": mean_tangential_deep,
        "spearman_depth_vs_radial": sp_radial,
        "spearman_depth_vs_abs_tangential": sp_tangential,
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

vertex_df.to_csv(os.path.join(OUT, "vertex_radial.csv"), index=False)
bin_df.to_csv(os.path.join(OUT, "depth_bin_radial.csv"), index=False)
stats_df.to_csv(os.path.join(OUT, "radial_stats.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ──────────────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) THE KEY FIGURE: Distribution of alignment angles
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[(vertex_df["substrate"] == sub) & (vertex_df["drift_mag"] > 0.01)]
    shallow = vd[vd["depth"] < 0.3]
    deep = vd[vd["depth"] > 0.7]
    bins = np.linspace(-180, 180, 73)
    if len(shallow) > 0:
        ax.hist(shallow["alignment_angle"], bins=bins, alpha=0.6,
                density=True, label=f"Shallow (<0.3), N={len(shallow)}", color="purple")
    if len(deep) > 0:
        ax.hist(deep["alignment_angle"], bins=bins, alpha=0.6,
                density=True, label=f"Deep (>0.7), N={len(deep)}", color="gold")
    ax.axvline(0, color="red", linewidth=2, linestyle="--", label="Perfect radial outward")
    ax.set_xlabel("Angle between drift and radial direction (degrees)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title(sub, fontsize=14)
    ax.legend(fontsize=9)
    ax.set_xlim(-180, 180)
    s = stats_df[stats_df["substrate"] == sub].iloc[0]
    ax.text(0.02, 0.85, f"Shallow outward: {s['frac_outward_shallow']:.1%}",
            transform=ax.transAxes, fontsize=10, fontweight="bold")
plt.suptitle("(1) THE ALIGNMENT TEST: Do drift vectors point radially outward?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_alignment_angle_distribution.png"), dpi=150)
plt.close()

# (2) Fraction outward vs depth
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(bd["mean_depth"], bd["frac_outward"], "o-",
            linewidth=2.5, markersize=7, color=color)
    ax.axhline(0.5, color="gray", linestyle=":", linewidth=1, label="Random (50%)")
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Fraction of drift vectors pointing outward", fontsize=12)
    ax.set_title(sub, fontsize=14)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1)
plt.suptitle("(2) Outward fraction by depth: where does the radial bias live?",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_fraction_outward_by_depth.png"), dpi=150)
plt.close()

# (3) Radial drift component vs depth (binned)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(bd["mean_depth"], bd["mean_radial"], "o-",
            linewidth=2.5, markersize=7, color=color, label="Radial (outward = positive)")
    ax.plot(bd["mean_depth"], bd["mean_tangential"], "s--",
            linewidth=1.5, markersize=5, color="green", alpha=0.7, label="Tangential (signed)")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean drift component", fontsize=12)
    ax.set_title(sub, fontsize=14)
    ax.legend(fontsize=10)
plt.suptitle("(3) Radial vs tangential drift by depth", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_radial_vs_tangential.png"), dpi=150)
plt.close()

# (4) Scatter: alignment angle vs depth (all vertices)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[(vertex_df["substrate"] == sub) & (vertex_df["drift_mag"] > 0.01)]
    ax.hexbin(vd["depth"], vd["alignment_angle"], gridsize=60,
              cmap="YlOrRd", mincnt=1)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Alignment angle (degrees)", fontsize=12)
    ax.set_title(sub, fontsize=14)
    ax.axhline(0, color="red", linewidth=1, linestyle="--")
    plt.colorbar(ax.collections[0], ax=ax, label="Count")
plt.suptitle("(4) Alignment angle vs depth: where does radial alignment emerge?",
             fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_angle_vs_depth_density.png"), dpi=150)
plt.close()

# (5) THE CHIRALITY TEST: tangential drift by depth
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    bd = bin_df[bin_df["substrate"] == sub]
    ax.plot(bd["mean_depth"], bd["mean_tangential"], "o-",
            linewidth=2.5, markersize=7,
            color="steelblue" if sub == "AB_N30" else "coral")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean tangential drift (signed)", fontsize=12)
    ax.set_title(sub, fontsize=14)
    s = stats_df[stats_df["substrate"] == sub].iloc[0]
    ax.text(0.05, 0.95, f"Mean tangential = {s['mean_tangential_all']:.6f}",
            transform=ax.transAxes, fontsize=10, va="top", fontweight="bold")
plt.suptitle("(5) CHIRALITY TEST: Is there handedness in the drift?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_chirality_tangential.png"), dpi=150)
plt.close()

# (6) Polar histogram of alignment angles (shallow only)
fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                          subplot_kw=dict(projection="polar"))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    vd = vertex_df[(vertex_df["substrate"] == sub) &
                    (vertex_df["drift_mag"] > 0.01) &
                    (vertex_df["depth"] < 0.3)]
    if len(vd) == 0:
        continue
    angles_rad = np.radians(vd["alignment_angle"])
    bins = np.linspace(-np.pi, np.pi, 37)
    counts, _ = np.histogram(angles_rad, bins=bins)
    centers = (bins[:-1] + bins[1:]) / 2
    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.bar(centers, counts, width=np.diff(bins)[0], alpha=0.7, color=color)
    ax.set_title(f"{sub}\n(shallow, depth<0.3)", fontsize=12, pad=15)
    ax.set_theta_zero_location("E")
plt.suptitle("(6) Polar: where do shallow drift vectors point relative to radial?",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_polar_shallow_alignment.png"), dpi=150)
plt.close()

# (7) Substrate comparison: radial drift curves overlaid
fig, ax = plt.subplots(figsize=(10, 6))
for sub, color in [("AB_N30", "steelblue"), ("Penrose_N24", "coral")]:
    bd = bin_df[bin_df["substrate"] == sub]
    ax.plot(bd["mean_depth"], bd["mean_radial"], "o-",
            linewidth=2.5, markersize=7, color=color, label=sub)
ax.axhline(0, color="gray", linewidth=0.8)
ax.set_xlabel("Hull depth", fontsize=12)
ax.set_ylabel("Mean radial drift (positive = outward)", fontsize=12)
ax.set_title("Radial drift: AB vs Penrose", fontsize=14)
ax.legend(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_7_substrate_radial_comparison.png"), dpi=150)
plt.close()


# ── report ───────────────────────────────────────────────────────────

print("\nGenerating report...")

report = ["# Radial drift alignment v0.1\n"]
report.append("## Core question")
report.append("The directional balance test showed shallow vertices have biased drift")
report.append("vectors. Does that bias point RADIALLY OUTWARD toward the hull boundary?")
report.append("If so, the arrow-of-time gets its orientation: boundary-ward.\n")
report.append("Also: is there chirality (handedness) in the Penrose drift structure?\n")

report.append("## Setup")
report.append("- Pure geometry, no walks")
report.append(f"- Interior vertices only ({INTERIOR_FRAC*100:.0f}th percentile)")
report.append("- Alignment angle: angle between vertex's perp-space position vector")
report.append("  (from hull centroid) and its drift vector (mean displacement to neighbours)")
report.append("- 0° = perfect radial outward, ±180° = radial inward")
report.append("- Radial drift: projection of drift onto radial direction (positive = outward)")
report.append("- Tangential drift: perpendicular component (signed → chirality test)\n")

report.append("## Summary\n")
report.append(stats_df.to_markdown(index=False))
report.append("")

report.append("## Key results\n")
for _, s in stats_df.iterrows():
    sub = s["substrate"]
    report.append(f"### {sub}\n")
    report.append(f"  - Fraction outward (all drifters): {s['frac_outward_all']:.1%}")
    report.append(f"  - Fraction outward (shallow <0.3): {s['frac_outward_shallow']:.1%}")
    report.append(f"  - Fraction outward (deep >0.7): {s['frac_outward_deep']:.1%}")
    report.append(f"  - Mean radial drift (shallow): {s['mean_radial_shallow']:.6f}")
    report.append(f"  - Mean radial drift (deep): {s['mean_radial_deep']:.6f}")
    report.append(f"  - Mean tangential (all): {s['mean_tangential_all']:.6f}")
    report.append(f"  - Spearman(depth, radial_drift) = {s['spearman_depth_vs_radial']:.4f}")
    report.append("")

report.append("## Interpretation\n")
report.append("- If shallow vertices point outward: the drift has a radial orientation")
report.append("  → 'boundary-ward' arrow → time/decay concentrated at the edge")
report.append("- If tangential drift is nonzero: chirality → handedness → reflection symmetry broken")
report.append("- If both: the drift is a spiral (outward with rotation)\n")

report.append("## Figures\n")
report.append("1. fig_1 — THE ALIGNMENT TEST: angle distribution (KEY)")
report.append("2. fig_2 — Fraction outward by depth")
report.append("3. fig_3 — Radial vs tangential drift by depth")
report.append("4. fig_4 — Angle vs depth density")
report.append("5. fig_5 — CHIRALITY TEST: tangential drift")
report.append("6. fig_6 — Polar histogram (shallow only)")
report.append("7. fig_7 — Substrate comparison")

with open(os.path.join(OUT, "radial_drift_v0_1_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll done! Results in {OUT}")
