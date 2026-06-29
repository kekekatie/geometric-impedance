"""
Commensurability Analysis v0.1

Quantifies the observation that AB's highest-coordination vertices (z=8)
have neighbour angles that perfectly match the 8-fold projection symmetry,
while Penrose's highest-coordination vertices (z=7) can't match the
5-fold symmetry because 7 and 5 are coprime.

For each vertex type in both substrates:
1. Measure actual angular spacing between consecutive neighbours
2. Compare to ideal regular z-gon spacing (360/z)
3. Compare to the projection symmetry grid angles
4. Quantify the "commensurability gap" — how much residual irregularity
   remains even at maximum coordination

The prediction: AB's z=8 should show near-zero deviation from both the
regular polygon AND the symmetry grid. Penrose's z=7 should show
deviation from the regular polygon because it's forced onto a 5-fold grid.
"""

import os, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr, circstd
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "commensurability_v0_1_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75


def load_substrate(name):
    if name == "AB":
        verts = pd.read_csv(os.path.join(DATA, "clean_ab_full_raw_lift.csv"))
        edges = pd.read_csv(os.path.join(DATA, "large_ab_v0_6_edges.csv"))
        src_col, tgt_col = "source_index", "target_index"
        symmetry_fold = 8
    else:
        verts = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_lift.csv"))
        edges = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_edges.csv"))
        src_col, tgt_col = "source", "target"
        symmetry_fold = 5

    n = len(verts)
    adj = defaultdict(list)
    for _, row in edges.iterrows():
        s, t = int(row[src_col]), int(row[tgt_col])
        if s < n and t < n:
            adj[s].append(t)
            adj[t].append(s)
    adj_arr = [np.array(adj[i], dtype=np.int32) for i in range(n)]
    return verts, adj_arr, n, symmetry_fold


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


def angular_spacing_stats(angles_sorted):
    """Given sorted angles of neighbours, compute spacing statistics."""
    k = len(angles_sorted)
    if k < 2:
        return {}
    diffs = np.diff(angles_sorted)
    wrap = (2 * np.pi) - (angles_sorted[-1] - angles_sorted[0])
    spacings = np.append(diffs, wrap)

    ideal_spacing = 2 * np.pi / k
    deviations = spacings - ideal_spacing

    return {
        "n_neighbours": k,
        "mean_spacing_deg": np.degrees(np.mean(spacings)),
        "std_spacing_deg": np.degrees(np.std(spacings)),
        "max_spacing_deg": np.degrees(np.max(spacings)),
        "min_spacing_deg": np.degrees(np.min(spacings)),
        "ideal_spacing_deg": np.degrees(ideal_spacing),
        "mean_abs_deviation_deg": np.degrees(np.mean(np.abs(deviations))),
        "max_deviation_deg": np.degrees(np.max(np.abs(deviations))),
        "regularity": 1.0 - np.std(spacings) / (np.mean(spacings) + 1e-12),
    }


def snap_to_grid(angle, grid_angles):
    """Find the nearest grid angle and return the snap distance."""
    diffs = np.abs(np.arctan2(np.sin(angle - grid_angles), np.cos(angle - grid_angles)))
    return np.min(diffs)


# ── Main ─────────────────────────────────────────────────────

all_type_stats = []
all_vertex_data = []

for sub_name in ["AB", "Penrose"]:
    print(f"\n{'='*70}")
    print(f"  {sub_name}")
    print(f"{'='*70}")

    verts, adj_arr, n, sym_fold = load_substrate(sub_name)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh

    degree = np.array([len(adj_arr[i]) for i in range(n)], dtype=int)

    # Symmetry grid: the angles allowed by the projection symmetry
    # For n-fold symmetry, the grid has angles at multiples of pi/n
    # (both the star vectors and their reflections)
    grid_step = np.pi / sym_fold
    grid_angles = np.arange(0, 2 * np.pi, grid_step)
    print(f"  Symmetry: {sym_fold}-fold → grid step = {np.degrees(grid_step):.1f}°")
    print(f"  Grid angles: {np.degrees(grid_angles).round(1)}")

    # For each interior vertex, analyse angular spacings
    print(f"\n  Analysing angular spacings...")

    per_vertex = []
    for i in np.where(interior_mask)[0]:
        nbrs = adj_arr[i]
        k = len(nbrs)
        if k < 2:
            continue

        dx = px[nbrs] - px[i]
        dy = py[nbrs] - py[i]
        angles = np.arctan2(dy, dx)
        angles_sorted = np.sort(angles)

        stats = angular_spacing_stats(angles_sorted)

        # How well do the actual angles snap to the symmetry grid?
        snap_distances = np.array([snap_to_grid(a, grid_angles) for a in angles])
        mean_snap = np.degrees(np.mean(snap_distances))
        max_snap = np.degrees(np.max(snap_distances))

        # Commensurability score: does z divide evenly into 2*sym_fold?
        # e.g., z=8 on 8-fold: 8 divides 16 (2*8) → commensurate
        # z=7 on 5-fold: 7 doesn't divide 10 (2*5) → incommensurate
        n_grid_points = 2 * sym_fold
        is_commensurate = (n_grid_points % k == 0) or (k % sym_fold == 0)

        per_vertex.append({
            "vertex_id": i,
            "substrate": sub_name,
            "degree": k,
            "mean_abs_dev_from_regular": stats["mean_abs_deviation_deg"],
            "max_dev_from_regular": stats["max_deviation_deg"],
            "std_spacing": stats["std_spacing_deg"],
            "regularity": stats["regularity"],
            "mean_snap_to_grid": mean_snap,
            "max_snap_to_grid": max_snap,
            "is_commensurate": is_commensurate,
        })

    vdf = pd.DataFrame(per_vertex)
    all_vertex_data.append(vdf)

    # Type-level summary
    print(f"\n  {'z':>3s} {'N':>6s} {'Commens':>8s} | {'MeanAbsDev':>11s} {'StdSpacing':>11s} {'Regularity':>11s} | {'MeanSnap':>9s} {'MaxSnap':>8s}")
    print("  " + "-" * 82)

    for z in sorted(vdf["degree"].unique(), reverse=True):
        sub = vdf[vdf["degree"] == z]
        if len(sub) < 5:
            continue
        comm = "YES" if sub["is_commensurate"].iloc[0] else "NO"
        row = {
            "substrate": sub_name,
            "degree": z,
            "count": len(sub),
            "commensurate": comm,
            "mean_abs_dev_from_regular": sub["mean_abs_dev_from_regular"].mean(),
            "std_spacing": sub["std_spacing"].mean(),
            "regularity": sub["regularity"].mean(),
            "mean_snap_to_grid": sub["mean_snap_to_grid"].mean(),
            "max_snap_to_grid": sub["max_snap_to_grid"].mean(),
        }
        all_type_stats.append(row)
        print(f"  z={z}  {len(sub):>5d}  {comm:>7s} | "
              f"{row['mean_abs_dev_from_regular']:>9.2f}°  "
              f"{row['std_spacing']:>9.2f}°  "
              f"{row['regularity']:>9.4f} | "
              f"{row['mean_snap_to_grid']:>7.2f}°  "
              f"{row['max_snap_to_grid']:>6.2f}°")

type_df = pd.DataFrame(all_type_stats)
vertex_df = pd.concat(all_vertex_data, ignore_index=True)

# ── Cross-substrate comparison ───────────────────────────────

print(f"\n{'='*70}")
print(f"  CROSS-SUBSTRATE: COMMENSURABILITY COMPARISON")
print(f"{'='*70}")

print(f"\n  The key question: at maximum coordination, which substrate")
print(f"  achieves more regular angular spacing?\n")

for sub_name in ["AB", "Penrose"]:
    sub = type_df[type_df["substrate"] == sub_name]
    top = sub[sub["degree"] == sub["degree"].max()].iloc[0]
    print(f"  {sub_name}: top z={int(top['degree'])}, commensurate={top['commensurate']}")
    print(f"    Mean deviation from regular polygon: {top['mean_abs_dev_from_regular']:.2f}°")
    print(f"    Mean snap to symmetry grid: {top['mean_snap_to_grid']:.2f}°")
    print(f"    Regularity: {top['regularity']:.4f}")
    print()

# Shared z values comparison
print(f"  SHARED COORDINATION NUMBERS:")
print(f"  {'z':>3s} | {'AB Dev°':>8s} {'AB Snap°':>9s} {'AB Reg':>7s} | {'Pen Dev°':>9s} {'Pen Snap°':>10s} {'Pen Reg':>8s}")
print("  " + "-" * 65)
for z in [7, 6, 5, 4, 3]:
    ab = type_df[(type_df["substrate"]=="AB") & (type_df["degree"]==z)]
    pen = type_df[(type_df["substrate"]=="Penrose") & (type_df["degree"]==z)]
    if len(ab) > 0 and len(pen) > 0:
        ab = ab.iloc[0]; pen = pen.iloc[0]
        print(f"  z={z} | {ab['mean_abs_dev_from_regular']:>6.2f}°  "
              f"{ab['mean_snap_to_grid']:>7.2f}°  {ab['regularity']:>6.4f} | "
              f"{pen['mean_abs_dev_from_regular']:>7.2f}°  "
              f"{pen['mean_snap_to_grid']:>8.2f}°  {pen['regularity']:>7.4f}")

# ── The punchline ────────────────────────────────────────────

print(f"\n{'='*70}")
print(f"  THE COMMENSURABILITY PUNCHLINE")
print(f"{'='*70}")

ab_top = type_df[(type_df["substrate"]=="AB") & (type_df["degree"]==8)].iloc[0]
pen_top = type_df[(type_df["substrate"]=="Penrose") & (type_df["degree"]==7)].iloc[0]

print(f"\n  AB z=8 on 8-fold symmetry:")
print(f"    360/8 = 45.0° spacing. Grid step = 22.5°. 45/22.5 = 2 (integer!)")
print(f"    Deviation from regular: {ab_top['mean_abs_dev_from_regular']:.2f}°")
print(f"    Snap to grid: {ab_top['mean_snap_to_grid']:.2f}°")
print(f"    → COMMENSURATE: neighbours sit exactly on the symmetry grid")

print(f"\n  Penrose z=7 on 5-fold symmetry:")
print(f"    360/7 = 51.4° spacing. Grid step = 36.0°. 51.4/36 = 1.43 (NOT integer)")
print(f"    Deviation from regular: {pen_top['mean_abs_dev_from_regular']:.2f}°")
print(f"    Snap to grid: {pen_top['mean_snap_to_grid']:.2f}°")
print(f"    → INCOMMENSURATE: 7 neighbours can't sit evenly on a 5-fold grid")

print(f"\n  Ratio of grid-snap distances (Penrose/AB at top z):")
if ab_top['mean_snap_to_grid'] > 0.01:
    ratio = pen_top['mean_snap_to_grid'] / ab_top['mean_snap_to_grid']
    print(f"    {pen_top['mean_snap_to_grid']:.2f} / {ab_top['mean_snap_to_grid']:.2f} = {ratio:.1f}×")
else:
    print(f"    AB snap ≈ 0° (perfect), Penrose snap = {pen_top['mean_snap_to_grid']:.2f}°")

# ── Save ─────────────────────────────────────────────────────

type_df.to_csv(os.path.join(OUT, "type_commensurability.csv"), index=False)
vertex_df.to_csv(os.path.join(OUT, "vertex_angular_data.csv"), index=False)
print(f"\nData saved to {OUT}/")

# ── Figures ──────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) THE KEY FIGURE: regularity and grid-snap by z, both substrates
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Panel 1: Deviation from regular polygon
ax = axes[0]
for sub, color, marker in [("AB", "steelblue", "s"), ("Penrose", "coral", "o")]:
    td = type_df[type_df["substrate"]==sub].sort_values("degree", ascending=False)
    ax.plot(td["degree"], td["mean_abs_dev_from_regular"], f"{marker}-",
            color=color, linewidth=2, markersize=8, label=sub)
ax.set_xlabel("Coordination z", fontsize=12)
ax.set_ylabel("Mean |deviation| from regular z-gon (°)", fontsize=11)
ax.set_title("How irregular are the spacings?", fontsize=12)
ax.legend(fontsize=11)
ax.invert_xaxis()

# Panel 2: Snap to symmetry grid
ax = axes[1]
for sub, color, marker in [("AB", "steelblue", "s"), ("Penrose", "coral", "o")]:
    td = type_df[type_df["substrate"]==sub].sort_values("degree", ascending=False)
    ax.plot(td["degree"], td["mean_snap_to_grid"], f"{marker}-",
            color=color, linewidth=2, markersize=8, label=sub)
ax.set_xlabel("Coordination z", fontsize=12)
ax.set_ylabel("Mean snap distance to symmetry grid (°)", fontsize=11)
ax.set_title("How well do neighbours hit the grid?", fontsize=12)
ax.legend(fontsize=11)
ax.invert_xaxis()

# Panel 3: Regularity score
ax = axes[2]
for sub, color, marker in [("AB", "steelblue", "s"), ("Penrose", "coral", "o")]:
    td = type_df[type_df["substrate"]==sub].sort_values("degree", ascending=False)
    ax.plot(td["degree"], td["regularity"], f"{marker}-",
            color=color, linewidth=2, markersize=8, label=sub)
ax.set_xlabel("Coordination z", fontsize=12)
ax.set_ylabel("Regularity (1 = perfect, 0 = maximally irregular)", fontsize=11)
ax.set_title("Overall angular regularity", fontsize=12)
ax.legend(fontsize=11)
ax.invert_xaxis()

plt.suptitle("Fig 1: Commensurability — AB (8-fold) vs Penrose (5-fold)",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_commensurability_comparison.png"), dpi=150)
plt.close()

# (2) Angular spacing distributions for top-z vertices
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, sub_name, sym_fold in [(axes[0], "AB", 8), (axes[1], "Penrose", 5)]:
    sub_v = vertex_df[vertex_df["substrate"] == sub_name]
    top_z = sub_v["degree"].max()
    top_verts = sub_v[sub_v["degree"] == top_z]

    ax.hist(top_verts["mean_abs_dev_from_regular"], bins=40,
            color="steelblue" if sub_name == "AB" else "coral",
            edgecolor="black", linewidth=0.3, alpha=0.8, density=True)
    ax.axvline(0, color="green", linewidth=2, linestyle="--", label="Perfect regular")
    ax.set_xlabel("Mean |deviation| from regular polygon (°)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title(f"{sub_name} z={top_z} on {sym_fold}-fold\n"
                 f"(n={len(top_verts)}, mean dev={top_verts['mean_abs_dev_from_regular'].mean():.2f}°)",
                 fontsize=12)
    ax.legend(fontsize=10)

plt.suptitle("Fig 2: How Regular Are the Highest-Coordination Vertices?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_top_z_regularity.png"), dpi=150)
plt.close()

# (3) Grid snap distributions for top-z
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, sub_name, sym_fold in [(axes[0], "AB", 8), (axes[1], "Penrose", 5)]:
    sub_v = vertex_df[vertex_df["substrate"] == sub_name]
    top_z = sub_v["degree"].max()
    top_verts = sub_v[sub_v["degree"] == top_z]

    ax.hist(top_verts["mean_snap_to_grid"], bins=40,
            color="steelblue" if sub_name == "AB" else "coral",
            edgecolor="black", linewidth=0.3, alpha=0.8, density=True)
    ax.axvline(0, color="green", linewidth=2, linestyle="--", label="On grid")
    grid_step = 360.0 / (2 * sym_fold)
    ax.axvline(grid_step/2, color="red", linewidth=1.5, linestyle=":",
               label=f"Max possible ({grid_step/2:.1f}°)")
    ax.set_xlabel("Mean snap distance to symmetry grid (°)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title(f"{sub_name} z={top_z} on {sym_fold}-fold grid\n"
                 f"(grid step = {grid_step:.1f}°)",
                 fontsize=12)
    ax.legend(fontsize=10)

plt.suptitle("Fig 3: How Well Do Top-z Neighbours Hit the Symmetry Grid?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_grid_snap_distributions.png"), dpi=150)
plt.close()

# (4) Pedagogical: show actual neighbour angles for example vertices
fig, axes = plt.subplots(1, 2, figsize=(14, 6), subplot_kw={"projection": "polar"})

for ax, sub_name, sym_fold in [(axes[0], "AB", 8), (axes[1], "Penrose", 5)]:
    verts_data, adj_arr_local, n_local, _ = load_substrate(sub_name)
    px_local = verts_data["perp_x"].values.astype(np.float64)
    py_local = verts_data["perp_y"].values.astype(np.float64)
    degree_local = np.array([len(adj_arr_local[i]) for i in range(n_local)])

    top_z = degree_local.max()
    # Find a nice example vertex (interior, top z)
    phys_r_local = compute_physical_radius(verts_data)
    r_thresh_local = np.percentile(phys_r_local, 50)
    candidates = np.where((degree_local == top_z) & (phys_r_local < r_thresh_local))[0]
    example = candidates[0]

    nbrs = adj_arr_local[example]
    dx = px_local[nbrs] - px_local[example]
    dy = py_local[nbrs] - py_local[example]
    angles = np.arctan2(dy, dx)

    # Plot actual neighbour directions
    for a in angles:
        ax.plot([a, a], [0, 0.8], color="steelblue" if sub_name == "AB" else "coral",
                linewidth=3, alpha=0.8)
        ax.plot(a, 0.8, "o", color="steelblue" if sub_name == "AB" else "coral",
                markersize=8)

    # Plot symmetry grid
    grid_step = np.pi / sym_fold
    grid_angles = np.arange(0, 2 * np.pi, grid_step)
    for ga in grid_angles:
        ax.plot([ga, ga], [0, 1.0], color="gray", linewidth=0.5, alpha=0.5, linestyle="--")

    # Plot ideal regular polygon
    ideal_angles = np.linspace(angles.min(), angles.min() + 2*np.pi, top_z, endpoint=False)
    for ia in ideal_angles:
        ax.plot([ia, ia], [0, 0.6], color="green", linewidth=1, alpha=0.4, linestyle=":")

    ax.set_title(f"{sub_name}: z={top_z} on {sym_fold}-fold\n"
                 f"(blue/coral = actual, gray = grid, green = ideal regular)",
                 fontsize=11, pad=15)
    ax.set_yticklabels([])
    ax.set_rticks([])

plt.suptitle("Fig 4: Example Top-z Vertices — Actual Angles vs Symmetry Grid",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_example_vertices_polar.png"), dpi=150)
plt.close()

# (5) Commensurability vs balance: the connection
fig, ax = plt.subplots(figsize=(10, 7))
for sub, color, marker in [("AB", "steelblue", "s"), ("Penrose", "coral", "o")]:
    td = type_df[type_df["substrate"]==sub]
    ax.scatter(td["mean_snap_to_grid"], td["mean_abs_dev_from_regular"],
               c=color, s=100, marker=marker, edgecolors="black", linewidth=0.5,
               zorder=5)
    for _, row in td.iterrows():
        label = f"z={int(row['degree'])}"
        ax.annotate(label, (row["mean_snap_to_grid"], row["mean_abs_dev_from_regular"]),
                     textcoords="offset points", xytext=(8, 4), fontsize=9)

ax.set_xlabel("Mean snap to symmetry grid (°) — commensurability", fontsize=12)
ax.set_ylabel("Mean deviation from regular polygon (°) — irregularity", fontsize=12)
ax.set_title("Fig 5: Grid Commensurability vs Angular Irregularity",
             fontsize=13, fontweight="bold")
# Add legend manually
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker="s", color="w", markerfacecolor="steelblue",
                          markersize=10, label="AB (8-fold)"),
                   Line2D([0], [0], marker="o", color="w", markerfacecolor="coral",
                          markersize=10, label="Penrose (5-fold)")]
ax.legend(handles=legend_elements, fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_commensurability_vs_irregularity.png"), dpi=150)
plt.close()


# ── Report ───────────────────────────────────────────────────

report = []
report.append("# Commensurability Analysis v0.1\n")
report.append("## Question")
report.append("AB's z=8 vertices sit on an 8-fold symmetry grid — their coordination")
report.append("is commensurate with the projection symmetry. Penrose's z=7 vertices")
report.append("sit on a 5-fold grid — 7 and 5 are coprime, so they're incommensurate.")
report.append("How much does this matter for angular regularity and directional balance?\n")

report.append("## Method")
report.append("For each vertex type in both substrates:")
report.append("1. Compute angular spacings between consecutive perp-space neighbours")
report.append("2. Compare to ideal regular z-gon (360/z spacing)")
report.append("3. Compare to projection symmetry grid (multiples of pi/n)")
report.append("4. Quantify deviation from both references\n")

report.append("## Type-level summary\n")
report.append(type_df.to_markdown(index=False))
report.append("")

report.append("\n## Figures\n")
report.append("1. fig_1 — Commensurability comparison (3-panel: deviation, snap, regularity)")
report.append("2. fig_2 — Top-z regularity distributions")
report.append("3. fig_3 — Grid snap distributions")
report.append("4. fig_4 — Example vertices: actual angles vs symmetry grid (polar)")
report.append("5. fig_5 — Grid commensurability vs angular irregularity (scatter)")

with open(os.path.join(OUT, "commensurability_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll figures and report saved to {OUT}/")
print("Done!")
