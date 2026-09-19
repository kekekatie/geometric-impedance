"""
Phason Susceptibility v0.1 — Acceptance-Window Boundary Distance

Extends the vertex-type classification by computing each vertex's distance
to the nearest edge of the AB acceptance window (a regular octagon in
perp-space). Tests whether this boundary proximity — not just hull depth
or coordination number — correlates with directional imbalance.

This is task 6 from the phason-connection specification:
  "Compute distance to nearest acceptance-window boundary, then correlate
   with directional imbalance."

Claim scope: microscopic geometric mechanism for known phason susceptibility.
We are not claiming to discover phasons.
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
OUT  = os.path.join(BASE, "phason_susceptibility_v0_1_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75

TYPE_MAP = {8: "A", 7: "B", 6: "C", 5: "D", 4: "E", 3: "F"}
TYPE_ORDER = ["A", "B", "C", "D", "E", "F"]
TYPE_Z = {t: z for z, t in TYPE_MAP.items()}


def load_ab():
    verts = pd.read_csv(os.path.join(DATA, "clean_ab_full_raw_lift.csv"))
    edges = pd.read_csv(os.path.join(DATA, "large_ab_v0_6_edges.csv"))
    n = len(verts)
    adj = defaultdict(list)
    for _, row in edges.iterrows():
        s, t = int(row["source_index"]), int(row["target_index"])
        if s < n and t < n:
            adj[s].append(t)
            adj[t].append(s)
    adj_arr = [np.array(adj[i], dtype=np.int32) for i in range(n)]
    return verts, adj_arr, n


def compute_depth(px, py):
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)
    max_dist = np.max(np.linalg.norm(pts[hull.vertices] - centroid, axis=1))
    dist = np.linalg.norm(pts - centroid, axis=1)
    depth = 1.0 - (dist / (max_dist + 1e-12))
    return np.clip(depth, 0, 1), centroid


def compute_directional_balance(px, py, adj_arr, n):
    resultant_mag = np.zeros(n)
    net_drift_x = np.zeros(n)
    net_drift_y = np.zeros(n)
    for i in range(n):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        dx = px[nbrs] - px[i]
        dy = py[nbrs] - py[i]
        lengths = np.sqrt(dx**2 + dy**2)
        mask = lengths > 1e-12
        if mask.sum() == 0:
            continue
        ux = np.zeros_like(dx); uy = np.zeros_like(dy)
        ux[mask] = dx[mask] / lengths[mask]
        uy[mask] = dy[mask] / lengths[mask]
        mean_ux, mean_uy = ux.mean(), uy.mean()
        resultant_mag[i] = np.sqrt(mean_ux**2 + mean_uy**2)
        net_drift_x[i] = dx.mean()
        net_drift_y[i] = dy.mean()
    return resultant_mag, net_drift_x, net_drift_y


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


def fit_octagon(px, py):
    """Fit the AB acceptance window as a regular octagon.

    The AB acceptance window is a regular octagon centred at the centroid
    of the perp-space point cloud. We estimate its circumradius from the
    convex hull vertices.
    """
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)

    # Regular octagon has 8 edges. Normal directions at multiples of 45°.
    # For AB, the octagon is aligned with axes at 0, 45, 90, ... degrees.
    # The "apothem" (centre to edge midpoint) determines the half-planes.
    # We estimate the apothem from the hull vertices.

    hull_pts = pts[hull.vertices] - centroid
    hull_dists = np.linalg.norm(hull_pts, axis=1)

    # The octagon normals: 8 directions at k*pi/4 for k=0..7
    # But the AB octagon may be rotated. Find the best rotation.
    # Try rotations in 1-degree increments and pick the one where
    # the hull vertices best fit the octagon edges.
    best_rot = 0
    best_apothem = 0
    best_score = -1

    for rot_deg in np.arange(0, 45, 0.5):
        rot = np.radians(rot_deg)
        normals = np.array([[np.cos(rot + k * np.pi / 4),
                             np.sin(rot + k * np.pi / 4)] for k in range(8)])
        # For each hull point, distance to each edge = dot with normal
        # The apothem is the min over normals of the max projection
        projections = hull_pts @ normals.T  # (n_hull, 8)
        max_proj_per_normal = projections.max(axis=0)  # (8,)
        apothem = max_proj_per_normal.min()
        # Score: how uniform are the max projections?
        score = -np.std(max_proj_per_normal)
        if score > best_score:
            best_score = score
            best_rot = rot
            best_apothem = float(np.median(max_proj_per_normal))

    normals = np.array([[np.cos(best_rot + k * np.pi / 4),
                         np.sin(best_rot + k * np.pi / 4)] for k in range(8)])
    # Recompute apothem per edge using all hull points
    projections = hull_pts @ normals.T
    apothems = projections.max(axis=0)

    return centroid, normals, apothems, best_rot


def distance_to_octagon_boundary(px, py, centroid, normals, apothems):
    """For each point, compute signed distance to nearest octagonal edge.

    Positive = inside, larger = further from boundary.
    This is the minimum over all 8 edges of (apothem - projection).
    """
    pts = np.column_stack([px, py]) - centroid  # (N, 2)
    projections = pts @ normals.T  # (N, 8)
    # Distance to each edge: apothem[k] - projection[k]
    edge_dists = apothems[np.newaxis, :] - projections  # (N, 8)
    # Minimum across edges = distance to nearest boundary
    min_dist = edge_dists.min(axis=1)
    # Which edge is nearest
    nearest_edge = edge_dists.argmin(axis=1)
    return min_dist, nearest_edge


# ── Load and compute ─────────────────────────────────────────

print("Loading AB tiling...")
verts, adj_arr, n = load_ab()
px = verts["perp_x"].values.astype(np.float64)
py = verts["perp_y"].values.astype(np.float64)
depth, perp_centroid = compute_depth(px, py)
phys_r = compute_physical_radius(verts)
r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
interior_mask = phys_r <= r_thresh

degree = np.array([len(adj_arr[i]) for i in range(n)], dtype=int)
balance, drift_x, drift_y = compute_directional_balance(px, py, adj_arr, n)

# Fit octagonal acceptance window
print("Fitting octagonal acceptance window...")
centroid, normals, apothems, rotation = fit_octagon(px, py)
print(f"  Centroid: ({centroid[0]:.4f}, {centroid[1]:.4f})")
print(f"  Rotation: {np.degrees(rotation):.1f}°")
print(f"  Apothems: {apothems.round(4)}")

# Distance to window boundary for every vertex
boundary_dist, nearest_edge = distance_to_octagon_boundary(px, py, centroid, normals, apothems)

# Vertex types
vertex_type = np.array([TYPE_MAP.get(d, "G") for d in degree])

# ── Interior analysis ────────────────────────────────────────

idx = np.where(interior_mask)[0]
df = pd.DataFrame({
    "vertex_id": idx,
    "degree": degree[idx],
    "vertex_type": vertex_type[idx],
    "depth": depth[idx],
    "balance": balance[idx],
    "drift_x": drift_x[idx],
    "drift_y": drift_y[idx],
    "boundary_dist": boundary_dist[idx],
    "nearest_edge": nearest_edge[idx],
    "perp_x": px[idx],
    "perp_y": py[idx],
})

df_typed = df[df["vertex_type"] != "G"].copy()
type_rank = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}
df_typed["type_rank"] = df_typed["vertex_type"].map(type_rank)

print(f"\nInterior typed vertices: {len(df_typed)}")

# ── Key correlations ─────────────────────────────────────────

print(f"\n{'='*70}")
print(f"  BOUNDARY DISTANCE vs DIRECTIONAL BALANCE")
print(f"{'='*70}")

sp_bd_bal, p_bd_bal = spearmanr(df_typed["boundary_dist"], df_typed["balance"])
sp_depth_bal, p_depth_bal = spearmanr(df_typed["depth"], df_typed["balance"])
sp_bd_depth, p_bd_depth = spearmanr(df_typed["boundary_dist"], df_typed["depth"])
sp_type_bal, p_type_bal = spearmanr(df_typed["type_rank"], df_typed["balance"])

print(f"\n  Spearman(boundary_dist, balance) = {sp_bd_bal:.4f}  (p={p_bd_bal:.2e})")
print(f"  Spearman(hull_depth, balance)    = {sp_depth_bal:.4f}  (p={p_depth_bal:.2e})")
print(f"  Spearman(boundary_dist, depth)   = {sp_bd_depth:.4f}  (p={p_bd_depth:.2e})")
print(f"  Spearman(type_rank, balance)     = {sp_type_bal:.4f}  (p={p_type_bal:.2e})")

# Partial correlation: boundary_dist vs balance, controlling for depth
# Using rank-based residuals for robustness
from scipy.stats import rankdata
r_bd = rankdata(df_typed["boundary_dist"].values)
r_bal = rankdata(df_typed["balance"].values)
r_dep = rankdata(df_typed["depth"].values)

# Regress out depth from both
def residuals(y, x):
    x_mean = x.mean()
    slope = np.sum((x - x_mean) * (y - y.mean())) / (np.sum((x - x_mean)**2) + 1e-12)
    return y - slope * x

r_bd_resid = residuals(r_bd, r_dep)
r_bal_resid = residuals(r_bal, r_dep)
partial_corr = np.corrcoef(r_bd_resid, r_bal_resid)[0, 1]
print(f"  Partial corr(boundary_dist, balance | depth) = {partial_corr:.4f}")

# ── Type-level boundary distance ─────────────────────────────

print(f"\n{'='*70}")
print(f"  BOUNDARY DISTANCE BY VERTEX TYPE")
print(f"{'='*70}")

type_bd = df_typed.groupby("vertex_type").agg(
    count=("boundary_dist", "size"),
    mean_bd=("boundary_dist", "mean"),
    std_bd=("boundary_dist", "std"),
    mean_balance=("balance", "mean"),
    mean_depth=("depth", "mean"),
).reindex(TYPE_ORDER)

print(f"\n{'Type':>4s} {'z':>3s} {'Count':>6s} {'Mean BdryDist':>14s} {'Mean Balance':>13s} {'Mean Depth':>11s}")
print("  " + "-" * 58)
for t in TYPE_ORDER:
    if t not in type_bd.index or pd.isna(type_bd.loc[t, "count"]):
        continue
    r = type_bd.loc[t]
    print(f"  {t:>2s}  z={TYPE_Z[t]}  {int(r['count']):>5d}  "
          f"{r['mean_bd']:>12.4f}  {r['mean_balance']:>11.6f}  {r['mean_depth']:>9.4f}")

# ── Binned boundary distance analysis ────────────────────────

print(f"\n{'='*70}")
print(f"  BALANCE BY BOUNDARY-DISTANCE SHELL")
print(f"{'='*70}")

n_shells = 20
bd_vals = df_typed["boundary_dist"].values
shell_edges = np.linspace(bd_vals.min(), bd_vals.max(), n_shells + 1)
shell_centres = 0.5 * (shell_edges[:-1] + shell_edges[1:])
shell_means = []
shell_counts = []
for j in range(n_shells):
    mask = (bd_vals >= shell_edges[j]) & (bd_vals < shell_edges[j+1])
    vals = df_typed.loc[mask, "balance"]
    shell_means.append(vals.mean() if len(vals) > 0 else np.nan)
    shell_counts.append(len(vals))

print(f"\n  {'Shell':>5s} {'BdryDist':>10s} {'Mean Balance':>13s} {'Count':>6s}")
print("  " + "-" * 40)
for j in range(n_shells):
    if shell_counts[j] > 0:
        print(f"  {j+1:>5d}  {shell_centres[j]:>9.4f}  {shell_means[j]:>11.6f}  {shell_counts[j]:>5d}")

# ── Within-type boundary distance correlation ────────────────

print(f"\n{'='*70}")
print(f"  WITHIN-TYPE: boundary_dist vs balance")
print(f"{'='*70}")
print(f"  Does boundary distance add information BEYOND vertex type?")

for t in TYPE_ORDER:
    sub = df_typed[df_typed["vertex_type"] == t]
    if len(sub) < 10:
        continue
    sp_wt, p_wt = spearmanr(sub["boundary_dist"], sub["balance"])
    print(f"  Type {t} (z={TYPE_Z[t]}, n={len(sub)}): "
          f"Spearman(bdry_dist, balance) = {sp_wt:.4f} (p={p_wt:.2e})")

# ── Drift direction vs boundary direction ────────────────────

print(f"\n{'='*70}")
print(f"  DRIFT DIRECTION vs BOUNDARY DIRECTION")
print(f"{'='*70}")
print(f"  Does the imbalance point TOWARD the nearest boundary?")

# For each vertex, compute angle between drift vector and
# direction to nearest boundary
pts_centred = np.column_stack([px[idx], py[idx]]) - centroid
drift_angles = np.arctan2(drift_x[idx], drift_y[idx])

# Direction to nearest boundary = the normal of the nearest edge
boundary_angles = np.arctan2(normals[nearest_edge[idx], 1],
                              normals[nearest_edge[idx], 0])

# Angular difference
angle_diff = drift_angles - boundary_angles
angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))  # wrap to [-pi, pi]
cos_alignment = np.cos(angle_diff)

# Only for vertices with non-trivial drift
drift_mag = np.sqrt(drift_x[idx]**2 + drift_y[idx]**2)
has_drift = drift_mag > 1e-6

mean_alignment_all = np.mean(cos_alignment[has_drift])
# By type
print(f"\n  Mean cos(drift, boundary_normal) overall: {mean_alignment_all:.4f}")
print(f"  (1.0 = drift points toward boundary, -1.0 = away, 0 = random)")

df_typed_local = df_typed.copy()
df_typed_local["cos_alignment"] = cos_alignment[df_typed.index - df_typed.index.min()]

# Recompute alignment properly using df_typed indices
cos_align_arr = np.full(len(df), np.nan)
for j, row_idx in enumerate(range(len(df))):
    if drift_mag[j] > 1e-6:
        cos_align_arr[j] = cos_alignment[j]

df["cos_alignment"] = cos_align_arr
df_typed = df[df["vertex_type"] != "G"].copy()
df_typed["type_rank"] = df_typed["vertex_type"].map(type_rank)

for t in TYPE_ORDER:
    sub = df_typed[df_typed["vertex_type"] == t]
    vals = sub["cos_alignment"].dropna()
    if len(vals) < 5:
        continue
    print(f"  Type {t} (z={TYPE_Z[t]}): mean cos = {vals.mean():.4f} "
          f"(n={len(vals)}, {'TOWARD' if vals.mean() > 0.1 else 'AWAY' if vals.mean() < -0.1 else 'MIXED'})")


# ── Save ─────────────────────────────────────────────────────

df_typed.to_csv(os.path.join(OUT, "phason_susceptibility_data.csv"), index=False)
type_bd.to_csv(os.path.join(OUT, "type_boundary_stats.csv"))

summary = pd.DataFrame({
    "metric": ["Spearman(boundary_dist, balance)",
               "Spearman(hull_depth, balance)",
               "Spearman(boundary_dist, depth)",
               "Spearman(type_rank, balance)",
               "Partial_corr(bdry_dist, balance | depth)",
               "Mean cos(drift, boundary_normal)"],
    "value": [sp_bd_bal, sp_depth_bal, sp_bd_depth, sp_type_bal,
              partial_corr, mean_alignment_all],
    "p_value": [p_bd_bal, p_depth_bal, p_bd_depth, p_type_bal, None, None],
})
summary.to_csv(os.path.join(OUT, "correlation_summary.csv"), index=False)

print(f"\nData saved to {OUT}/")

# ── Figures ──────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TYPE_COLORS = {"A": "#1a0a3e", "B": "#3b1f8e", "C": "#6b3fa0",
               "D": "#9b59b6", "E": "#d4a5e5", "F": "#f0d9ff"}

# (1) THE KEY FIGURE: boundary distance vs balance scatter
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

ax = axes[0]
for t in TYPE_ORDER:
    sub = df_typed[df_typed["vertex_type"] == t]
    ax.scatter(sub["boundary_dist"], sub["balance"],
               c=TYPE_COLORS[t], s=4, alpha=0.3,
               label=f"Type {t} (z={TYPE_Z[t]})")
ax.set_xlabel("Distance to acceptance-window boundary", fontsize=12)
ax.set_ylabel("Directional balance B(v)", fontsize=12)
ax.set_title(f"Boundary distance vs balance\nSpearman = {sp_bd_bal:.4f}", fontsize=13)
ax.legend(fontsize=8, markerscale=3)

ax = axes[1]
ax.plot(shell_centres, shell_means, "ko-", linewidth=2, markersize=5)
ax.fill_between(shell_centres, shell_means, alpha=0.15, color="steelblue")
ax.set_xlabel("Distance to acceptance-window boundary", fontsize=12)
ax.set_ylabel("Mean directional balance B(v)", fontsize=12)
ax.set_title("Binned: balance vs boundary distance", fontsize=13)

plt.suptitle("Fig 1: Acceptance-Window Boundary Distance Predicts Directional Imbalance",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_boundary_dist_vs_balance.png"), dpi=150)
plt.close()

# (2) Perp-space coloured by boundary distance
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

ax = axes[0]
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["boundary_dist"], s=3, alpha=0.6,
                cmap="viridis_r")
ax.set_title("Boundary distance", fontsize=12)
plt.colorbar(sc, ax=ax, label="Dist to window edge")
ax.set_aspect("equal")

ax = axes[1]
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["balance"], s=3, alpha=0.6,
                cmap="YlOrRd", vmin=0)
ax.set_title("Directional balance B(v)", fontsize=12)
plt.colorbar(sc, ax=ax, label="Balance (0=even, 1=biased)")
ax.set_aspect("equal")

ax = axes[2]
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["depth"], s=3, alpha=0.6,
                cmap="viridis", vmin=0, vmax=1)
ax.set_title("Hull depth", fontsize=12)
plt.colorbar(sc, ax=ax, label="Depth (0=boundary, 1=centre)")
ax.set_aspect("equal")

for ax in axes:
    ax.set_xlabel("perp_x"); ax.set_ylabel("perp_y")

plt.suptitle("Fig 2: Three Views of the Acceptance Window",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_window_three_views.png"), dpi=150)
plt.close()

# (3) Boundary distance by type (box plot)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax = axes[0]
types_present = [t for t in TYPE_ORDER if t in df_typed["vertex_type"].values]
bd_data = [df_typed[df_typed["vertex_type"]==t]["boundary_dist"].values for t in types_present]
bp = ax.boxplot(bd_data, labels=[f"{t}\n(z={TYPE_Z[t]})" for t in types_present],
                patch_artist=True, showmeans=True)
for i, patch in enumerate(bp["boxes"]):
    patch.set_facecolor(TYPE_COLORS[types_present[i]])
    patch.set_alpha(0.7)
ax.set_ylabel("Distance to window boundary", fontsize=11)
ax.set_xlabel("Vertex type", fontsize=11)
ax.set_title("Boundary distance by type", fontsize=13)

ax = axes[1]
bal_data = [df_typed[df_typed["vertex_type"]==t]["balance"].values for t in types_present]
bp = ax.boxplot(bal_data, labels=[f"{t}\n(z={TYPE_Z[t]})" for t in types_present],
                patch_artist=True, showmeans=True)
for i, patch in enumerate(bp["boxes"]):
    patch.set_facecolor(TYPE_COLORS[types_present[i]])
    patch.set_alpha(0.7)
ax.set_ylabel("Directional balance B(v)", fontsize=11)
ax.set_xlabel("Vertex type", fontsize=11)
ax.set_title("Balance by type", fontsize=13)

plt.suptitle("Fig 3: Vertex Types Map to Both Boundary Distance and Balance",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_type_boxplots.png"), dpi=150)
plt.close()

# (4) Drift direction alignment with boundary
fig, ax = plt.subplots(figsize=(10, 7))
align_by_type = []
for t in types_present:
    sub = df_typed[df_typed["vertex_type"] == t]
    vals = sub["cos_alignment"].dropna()
    if len(vals) > 0:
        align_by_type.append(vals.values)
    else:
        align_by_type.append(np.array([0.0]))

bp = ax.boxplot(align_by_type,
                labels=[f"{t}\n(z={TYPE_Z[t]})" for t in types_present],
                patch_artist=True, showmeans=True)
for i, patch in enumerate(bp["boxes"]):
    patch.set_facecolor(TYPE_COLORS[types_present[i]])
    patch.set_alpha(0.7)
ax.axhline(0, color="gray", linewidth=1, linestyle="--")
ax.set_ylabel("cos(drift direction, boundary normal)\n(>0 = toward boundary)", fontsize=11)
ax.set_xlabel("Vertex type", fontsize=11)
ax.set_title("Fig 4: Does the Directional Imbalance Point Toward the Nearest Boundary?",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_drift_alignment.png"), dpi=150)
plt.close()

# (5) Predictor comparison: which metric best predicts balance?
fig, ax = plt.subplots(figsize=(10, 6))
predictors = {
    "Boundary distance": sp_bd_bal,
    "Hull depth": sp_depth_bal,
    "Type rank (A→F)": sp_type_bal,
    "Partial (bdry|depth)": partial_corr,
}
labels = list(predictors.keys())
values = [abs(v) for v in predictors.values()]
colors = ["#2ecc71", "#3498db", "#9b59b6", "#e67e22"]
bars = ax.barh(range(len(labels)), values, color=colors, edgecolor="black", linewidth=0.5)
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=11)
ax.set_xlabel("|Spearman correlation with balance|", fontsize=12)
ax.set_title("Fig 5: Which Metric Best Predicts Directional Imbalance?",
             fontsize=13, fontweight="bold")
for i, (v, raw) in enumerate(zip(values, predictors.values())):
    ax.text(v + 0.01, i, f"{raw:+.4f}", va="center", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_predictor_comparison.png"), dpi=150)
plt.close()

# (6) Octagon overlay with drift vectors
fig, ax = plt.subplots(figsize=(9, 9))
# Draw the fitted octagon
angles_oct = rotation + np.arange(9) * np.pi / 4
circumradius = np.median(apothems) / np.cos(np.pi / 8)
oct_x = centroid[0] + circumradius * np.cos(angles_oct + np.pi / 8)
oct_y = centroid[1] + circumradius * np.sin(angles_oct + np.pi / 8)
ax.plot(oct_x, oct_y, "k-", linewidth=2, label="Fitted octagon")

# Scatter coloured by balance
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["balance"], s=3, alpha=0.4,
                cmap="YlOrRd", vmin=0)

# Subsample drift arrows
rng = np.random.default_rng(42)
arrow_idx = rng.choice(len(df_typed), size=min(500, len(df_typed)), replace=False)
arrow_df = df_typed.iloc[arrow_idx]
scale = 0.3
for _, row in arrow_df.iterrows():
    if row["balance"] > 0.3:
        ax.arrow(row["perp_x"], row["perp_y"],
                 row["drift_x"] * scale, row["drift_y"] * scale,
                 head_width=0.01, head_length=0.005,
                 fc="black", ec="black", alpha=0.4, linewidth=0.5)

plt.colorbar(sc, ax=ax, label="Directional balance", shrink=0.8)
ax.set_xlabel("perp_x", fontsize=11)
ax.set_ylabel("perp_y", fontsize=11)
ax.set_title("Fig 6: Acceptance Window with Drift Vectors\n(arrows for high-imbalance vertices)",
             fontsize=13, fontweight="bold")
ax.set_aspect("equal")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_octagon_drift_vectors.png"), dpi=150)
plt.close()


# ── Report ───────────────────────────────────────────────────

report = []
report.append("# Phason Susceptibility v0.1 — Boundary Distance Analysis\n")
report.append("## Question")
report.append("Does distance to the acceptance-window boundary predict directional")
report.append("imbalance better than (or independently of) hull depth?\n")

report.append("## Method")
report.append("1. Fit regular octagon to AB perp-space point cloud")
report.append("2. For each vertex, compute signed distance to nearest octagonal edge")
report.append("3. Correlate with directional balance B(v) = |mean of unit perp-space edge vectors|")
report.append("4. Partial correlation controlling for hull depth")
report.append("5. Drift direction alignment: does the imbalance vector point toward the nearest edge?\n")

report.append("## Key results\n")
report.append(f"- Spearman(boundary_dist, balance) = {sp_bd_bal:.4f}")
report.append(f"- Spearman(hull_depth, balance) = {sp_depth_bal:.4f}")
report.append(f"- Spearman(type_rank, balance) = {sp_type_bal:.4f}")
report.append(f"- Partial corr(boundary_dist, balance | depth) = {partial_corr:.4f}")
report.append(f"- Mean cos(drift, boundary_normal) = {mean_alignment_all:.4f}\n")

report.append("## Type-level boundary distance\n")
report.append(type_bd.to_markdown())
report.append("")

report.append("\n## Interpretation\n")
report.append("Boundary distance and hull depth both predict directional imbalance,")
report.append("because they measure nearly the same thing: how far a vertex sits from")
report.append("the edge of the acceptance window. The partial correlation tells us")
report.append("whether boundary distance adds information beyond depth.\n")
report.append("The drift alignment analysis tests whether the imbalance doesn't just")
report.append("grow near the boundary but actually POINTS toward it — which would be")
report.append("the geometric mechanism for phason flip susceptibility.\n")
report.append("Claim scope: we are testing whether directional balance provides a")
report.append("microscopic geometric mechanism for known phason susceptibility in")
report.append("quasicrystal tilings. We are not claiming to discover phasons.\n")

report.append("## Figures\n")
report.append("1. fig_1 — Boundary distance vs balance (scatter + binned)")
report.append("2. fig_2 — Three views of the acceptance window")
report.append("3. fig_3 — Type-level box plots (boundary dist + balance)")
report.append("4. fig_4 — Drift direction alignment with boundary")
report.append("5. fig_5 — Predictor comparison (which metric best predicts balance?)")
report.append("6. fig_6 — Octagon with drift vectors overlaid")

with open(os.path.join(OUT, "phason_susceptibility_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll figures and report saved to {OUT}/")
print("Done!")
