"""
Gap-to-Drift v0.1 — Closing the Mechanism Chain

We've shown: coordination gap → directional balance → walk drift
But never: coordination gap → walk drift directly.

This script runs random walks on BOTH substrates, then shows the
complete causal chain in one pipeline:

  max_angular_gap → directional_balance → perp_space_residue

Also produces the predictor comparison table GPT asked for:
  depth vs boundary_dist vs degree vs max_gap vs balance

And the arrow-convention diagram.
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
OUT  = os.path.join(BASE, "gap_to_drift_v0_1_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75
N_SEEDS = 5
WALKERS_PER_SEED = 15_000
MAX_STEPS = 1024
NEAR_RETURN_THR = 3.0

TYPE_MAP_AB = {8: "A", 7: "B", 6: "C", 5: "D", 4: "E", 3: "F"}
TYPE_MAP_PEN = {7: "A", 6: "B", 5: "C", 4: "D", 3: "E"}


def load_substrate(name):
    if name == "AB":
        verts = pd.read_csv(os.path.join(DATA, "clean_ab_full_raw_lift.csv"))
        edges = pd.read_csv(os.path.join(DATA, "large_ab_v0_6_edges.csv"))
        src_col, tgt_col = "source_index", "target_index"
        type_map = TYPE_MAP_AB
    else:
        verts = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_lift.csv"))
        edges = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_edges.csv"))
        src_col, tgt_col = "source", "target"
        type_map = TYPE_MAP_PEN

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

    return verts, adj_arr, adj_padded, deg, n, type_map


def compute_depth(px, py):
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)
    max_dist = np.max(np.linalg.norm(pts[hull.vertices] - centroid, axis=1))
    dist = np.linalg.norm(pts - centroid, axis=1)
    depth = 1.0 - (dist / (max_dist + 1e-12))
    return np.clip(depth, 0, 1)


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


def compute_vertex_metrics(px, py, adj_arr, n):
    balance_mag = np.zeros(n)
    gap_angle = np.zeros(n)

    for i in range(n):
        nbrs = adj_arr[i]
        k = len(nbrs)
        if k < 2:
            continue

        dx = px[nbrs] - px[i]
        dy = py[nbrs] - py[i]

        # Balance
        lengths = np.sqrt(dx**2 + dy**2)
        mask = lengths > 1e-12
        if mask.sum() == 0:
            continue
        ux = np.zeros_like(dx); uy = np.zeros_like(dy)
        ux[mask] = dx[mask] / lengths[mask]
        uy[mask] = dy[mask] / lengths[mask]
        balance_mag[i] = np.sqrt(ux.mean()**2 + uy.mean()**2)

        # Gap
        angles = np.arctan2(dy, dx)
        angles_sorted = np.sort(angles)
        diffs = np.diff(angles_sorted)
        wrap = (2 * np.pi) - (angles_sorted[-1] - angles_sorted[0])
        gap_angle[i] = max(np.max(diffs), wrap)

    return balance_mag, gap_angle


def run_walks(vx, vy, px, py, adj_padded, deg, interior_idx, seed_base):
    """Run walks, return per-walker: start_idx, perp_residue, phys_dist."""
    all_starts = []
    all_residues = []
    all_phys = []

    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed_base + seed)
        starts = rng.choice(interior_idx, size=WALKERS_PER_SEED, replace=True).astype(np.int32)
        pos = starts.copy()

        for t in range(MAX_STEPS):
            d = deg[pos]
            r = (rng.random(len(pos)) * d).astype(np.int32)
            r = np.minimum(r, d - 1)
            pos = adj_padded[pos, r]

        phys_dist = np.sqrt((vx[pos] - vx[starts])**2 + (vy[pos] - vy[starts])**2)
        perp_residue = np.sqrt((px[pos] - px[starts])**2 + (py[pos] - py[starts])**2)

        all_starts.append(starts)
        all_residues.append(perp_residue)
        all_phys.append(phys_dist)

    return (np.concatenate(all_starts),
            np.concatenate(all_residues),
            np.concatenate(all_phys))


def fit_octagon_boundary_dist(px, py):
    """Compute boundary distance for AB (octagonal window)."""
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)
    hull_pts = pts[hull.vertices] - centroid

    best_rot = 0
    best_score = -1
    for rot_deg in np.arange(0, 45, 0.5):
        rot = np.radians(rot_deg)
        normals = np.array([[np.cos(rot + k * np.pi / 4),
                             np.sin(rot + k * np.pi / 4)] for k in range(8)])
        proj = hull_pts @ normals.T
        max_proj = proj.max(axis=0)
        score = -np.std(max_proj)
        if score > best_score:
            best_score = score
            best_rot = rot

    normals = np.array([[np.cos(best_rot + k * np.pi / 4),
                         np.sin(best_rot + k * np.pi / 4)] for k in range(8)])
    proj = hull_pts @ normals.T
    apothems = proj.max(axis=0)

    pts_c = pts - centroid
    all_proj = pts_c @ normals.T
    edge_dists = apothems[np.newaxis, :] - all_proj
    return edge_dists.min(axis=1)


def fit_decagon_boundary_dist(px, py):
    """Compute boundary distance for Penrose (decagonal window)."""
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)
    hull_pts = pts[hull.vertices] - centroid

    best_rot = 0
    best_score = -1
    for rot_deg in np.arange(0, 36, 0.5):
        rot = np.radians(rot_deg)
        normals = np.array([[np.cos(rot + k * np.pi / 5),
                             np.sin(rot + k * np.pi / 5)] for k in range(10)])
        proj = hull_pts @ normals.T
        max_proj = proj.max(axis=0)
        score = -np.std(max_proj)
        if score > best_score:
            best_score = score
            best_rot = rot

    normals = np.array([[np.cos(best_rot + k * np.pi / 5),
                         np.sin(best_rot + k * np.pi / 5)] for k in range(10)])
    proj = hull_pts @ normals.T
    apothems = proj.max(axis=0)

    pts_c = pts - centroid
    all_proj = pts_c @ normals.T
    edge_dists = apothems[np.newaxis, :] - all_proj
    return edge_dists.min(axis=1)


# ── Main ─────────────────────────────────────────────────────

all_results = []

for sub_name in ["AB", "Penrose"]:
    print(f"\n{'='*60}")
    print(f"  {sub_name}")
    print(f"{'='*60}")

    verts, adj_arr, adj_padded, deg, n, type_map = load_substrate(sub_name)
    vx = verts["x"].values.astype(np.float64)
    vy = verts["y"].values.astype(np.float64)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)

    depth = compute_depth(px, py)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh
    interior_idx = np.where(interior_mask)[0]

    degree = np.array([len(adj_arr[i]) for i in range(n)], dtype=int)
    vertex_type = np.array([type_map.get(d, "X") for d in degree])
    balance_mag, gap_angle = compute_vertex_metrics(px, py, adj_arr, n)
    gap_deg = np.degrees(gap_angle)

    if sub_name == "AB":
        boundary_dist = fit_octagon_boundary_dist(px, py)
    else:
        boundary_dist = fit_decagon_boundary_dist(px, py)

    print(f"  Running walks ({N_SEEDS} seeds × {WALKERS_PER_SEED} walkers)...")
    seed_base = 42 if sub_name == "AB" else 1042
    starts, residues, phys_dists = run_walks(vx, vy, px, py, adj_padded, deg,
                                              interior_idx, seed_base)

    # Filter to near-return walkers
    nr_mask = phys_dists <= NEAR_RETURN_THR
    nr_starts = starts[nr_mask]
    nr_residues = residues[nr_mask]
    print(f"  Near-return walkers (d≤{NEAR_RETURN_THR}): {len(nr_starts)}")

    # Predictors for each near-return walker's START vertex
    start_depth = depth[nr_starts]
    start_balance = balance_mag[nr_starts]
    start_gap = gap_deg[nr_starts]
    start_degree = degree[nr_starts]
    start_bdist = boundary_dist[nr_starts]

    # ── Predictor comparison ─────────────────────────────────
    predictors = {
        "hull_depth": start_depth,
        "boundary_dist": start_bdist,
        "degree": start_degree.astype(float),
        "max_angular_gap": start_gap,
        "directional_balance": start_balance,
    }

    print(f"\n  PREDICTOR COMPARISON (Spearman with perp-space residue):")
    print(f"  {'Predictor':>22s} {'Spearman':>10s} {'p-value':>12s} {'Direction':>10s}")
    print("  " + "-" * 58)
    pred_rows = []
    for name, vals in predictors.items():
        sp, p = spearmanr(vals, nr_residues)
        direction = "↑ more drift" if sp > 0 else "↓ less drift"
        print(f"  {name:>22s} {sp:>10.4f} {p:>12.2e} {direction:>10s}")
        pred_rows.append({
            "substrate": sub_name, "predictor": name,
            "spearman": sp, "p_value": p,
            "abs_spearman": abs(sp),
        })

    all_results.extend(pred_rows)

    # ── The direct chain: gap → residue ──────────────────────
    sp_gap_res, p_gap_res = spearmanr(start_gap, nr_residues)
    sp_bal_res, p_bal_res = spearmanr(start_balance, nr_residues)
    sp_gap_bal, _ = spearmanr(start_gap, start_balance)

    print(f"\n  THE CHAIN:")
    print(f"  gap → balance: Spearman = {sp_gap_bal:.4f}")
    print(f"  balance → residue: Spearman = {sp_bal_res:.4f}")
    print(f"  gap → residue (direct): Spearman = {sp_gap_res:.4f}")

    # Save per-substrate walk data (sampled for manageable size)
    rng = np.random.default_rng(99)
    sample_idx = rng.choice(len(nr_starts), size=min(10000, len(nr_starts)), replace=False)
    walk_df = pd.DataFrame({
        "substrate": sub_name,
        "start_vertex": nr_starts[sample_idx],
        "perp_residue": nr_residues[sample_idx],
        "depth": start_depth[sample_idx],
        "balance": start_balance[sample_idx],
        "gap_deg": start_gap[sample_idx],
        "degree": start_degree[sample_idx],
        "boundary_dist": start_bdist[sample_idx],
        "vertex_type": vertex_type[nr_starts[sample_idx]],
    })
    walk_df.to_csv(os.path.join(OUT, f"{sub_name.lower()}_walk_data.csv"), index=False)

# Save predictor comparison
pred_df = pd.DataFrame(all_results)
pred_df.to_csv(os.path.join(OUT, "predictor_comparison.csv"), index=False)

print(f"\nData saved to {OUT}/")

# ── Figures ──────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load walk data back for plotting
ab_walk = pd.read_csv(os.path.join(OUT, "ab_walk_data.csv"))
pen_walk = pd.read_csv(os.path.join(OUT, "penrose_walk_data.csv"))

# (1) THE CLOSING FIGURE: gap → residue, both substrates
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, (wdf, name, color) in zip(axes, [(ab_walk, "AB", "steelblue"),
                                           (pen_walk, "Penrose", "coral")]):
    ax.hexbin(wdf["gap_deg"], wdf["perp_residue"], gridsize=50,
              cmap="YlOrRd", mincnt=1)
    sp, _ = spearmanr(wdf["gap_deg"], wdf["perp_residue"])
    ax.set_xlabel("Max angular gap (degrees)", fontsize=12)
    ax.set_ylabel("Perp-space residue", fontsize=12)
    ax.set_title(f"{name}: gap → walk residue\nSpearman = {sp:.4f}", fontsize=13)
    plt.colorbar(ax.collections[0], ax=ax, label="Walker count")
plt.suptitle("Fig 1: THE CLOSING LINK — Coordination Gap Directly Predicts Walk Drift",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_gap_to_residue.png"), dpi=150)
plt.close()

# (2) The full chain: gap → balance → residue (3-panel)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for wdf, name, color in [(ab_walk, "AB", "steelblue"), (pen_walk, "Penrose", "coral")]:
    # Panel 1: gap → balance
    sp1, _ = spearmanr(wdf["gap_deg"], wdf["balance"])
    axes[0].scatter(wdf["gap_deg"], wdf["balance"], s=2, alpha=0.15,
                    color=color, label=f"{name} (ρ={sp1:.3f})")
    # Panel 2: balance → residue
    sp2, _ = spearmanr(wdf["balance"], wdf["perp_residue"])
    axes[1].scatter(wdf["balance"], wdf["perp_residue"], s=2, alpha=0.15,
                    color=color, label=f"{name} (ρ={sp2:.3f})")
    # Panel 3: gap → residue
    sp3, _ = spearmanr(wdf["gap_deg"], wdf["perp_residue"])
    axes[2].scatter(wdf["gap_deg"], wdf["perp_residue"], s=2, alpha=0.15,
                    color=color, label=f"{name} (ρ={sp3:.3f})")

axes[0].set_xlabel("Max angular gap (°)"); axes[0].set_ylabel("Directional balance")
axes[0].set_title("Step 1: Gap → Balance", fontsize=12)
axes[0].legend(fontsize=9, markerscale=4)

axes[1].set_xlabel("Directional balance"); axes[1].set_ylabel("Perp-space residue")
axes[1].set_title("Step 2: Balance → Drift", fontsize=12)
axes[1].legend(fontsize=9, markerscale=4)

axes[2].set_xlabel("Max angular gap (°)"); axes[2].set_ylabel("Perp-space residue")
axes[2].set_title("Step 3: Gap → Drift (direct)", fontsize=12)
axes[2].legend(fontsize=9, markerscale=4)

plt.suptitle("Fig 2: The Complete Mechanism Chain — Gap → Balance → Drift",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_mechanism_chain.png"), dpi=150)
plt.close()

# (3) Predictor horse race (both substrates)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB", "Penrose"]):
    pdf = pred_df[pred_df["substrate"] == sub].sort_values("abs_spearman", ascending=True)
    colors = ["#e74c3c" if s > 0 else "#3498db" for s in pdf["spearman"]]
    ax.barh(range(len(pdf)), pdf["abs_spearman"].values,
            color=colors, edgecolor="black", linewidth=0.5, alpha=0.85)
    ax.set_yticks(range(len(pdf)))
    ax.set_yticklabels(pdf["predictor"].values, fontsize=10)
    for i, (absv, rawv) in enumerate(zip(pdf["abs_spearman"], pdf["spearman"])):
        ax.text(absv + 0.01, i, f"{rawv:+.4f}", va="center", fontsize=9)
    ax.set_xlabel("|Spearman| with perp-space residue", fontsize=11)
    ax.set_title(f"{sub}", fontsize=13)
plt.suptitle("Fig 3: Predictor Horse Race — What Best Predicts Walk Drift?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_predictor_horse_race.png"), dpi=150)
plt.close()

# (4) Arrow convention diagram (pedagogical)
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel 1: Balanced vertex (type A)
ax = axes[0]
n_dirs = 8
angles_a = np.linspace(0, 2*np.pi, n_dirs, endpoint=False)
for a in angles_a:
    ax.arrow(0, 0, 0.7*np.cos(a), 0.7*np.sin(a),
             head_width=0.06, head_length=0.04, fc="steelblue", ec="steelblue", linewidth=1.5)
ax.plot(0, 0, "ko", markersize=10, zorder=5)
# Resultant (should be ~zero)
rx = np.mean(np.cos(angles_a))
ry = np.mean(np.sin(angles_a))
ax.arrow(0, 0, rx*2, ry*2, head_width=0.08, head_length=0.05,
         fc="red", ec="red", linewidth=3, zorder=6)
ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
ax.set_aspect("equal")
ax.set_title("Balanced (z=8)\nResultant ≈ 0\nNo drift", fontsize=11, fontweight="bold")
ax.text(0.5, -1.05, "All directions cancel", ha="center", fontsize=9, style="italic")

# Panel 2: Boundary vertex (type F, 3 neighbours clustered)
ax = axes[1]
angles_f = np.array([0.3, 0.9, 1.5])  # clustered in ~120° arc
for a in angles_f:
    ax.arrow(0, 0, 0.7*np.cos(a), 0.7*np.sin(a),
             head_width=0.06, head_length=0.04, fc="steelblue", ec="steelblue", linewidth=1.5)
ax.plot(0, 0, "ko", markersize=10, zorder=5)
# The gap
gap_centre = np.pi + 0.9  # opposite the cluster
gap_arc = np.linspace(1.8, 1.8 + 2*np.pi - 1.2, 50)
ax.plot(0.9*np.cos(gap_arc), 0.9*np.sin(gap_arc), ":", color="gray", linewidth=2)
ax.text(0.9*np.cos(gap_centre), 0.9*np.sin(gap_centre), "GAP\n(270°)",
        ha="center", va="center", fontsize=9, color="gray", fontweight="bold")
# Resultant
rx = np.mean(np.cos(angles_f))
ry = np.mean(np.sin(angles_f))
rmag = np.sqrt(rx**2 + ry**2)
ax.arrow(0, 0, rx*0.9, ry*0.9, head_width=0.08, head_length=0.05,
         fc="red", ec="red", linewidth=3, zorder=6)
ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
ax.set_aspect("equal")
ax.set_title(f"Boundary (z=3)\nResultant = {rmag:.2f}\nStrong drift", fontsize=11, fontweight="bold")
ax.text(0.5, -1.05, "Resultant → neighbours (away from gap)", ha="center", fontsize=9, style="italic")

# Panel 3: What a phason flip does
ax = axes[2]
for a in angles_f:
    ax.arrow(0, 0, 0.7*np.cos(a), 0.7*np.sin(a),
             head_width=0.06, head_length=0.04, fc="steelblue", ec="steelblue", linewidth=1.5)
# Add a "phason flip" neighbour in the gap
flip_angle = gap_centre
ax.arrow(0, 0, 0.7*np.cos(flip_angle), 0.7*np.sin(flip_angle),
         head_width=0.06, head_length=0.04, fc="#2ecc71", ec="#2ecc71",
         linewidth=2, linestyle="-", zorder=4)
ax.text(0.85*np.cos(flip_angle), 0.85*np.sin(flip_angle), "flip\nadds\nthis",
        ha="center", va="center", fontsize=8, color="#2ecc71", fontweight="bold")
ax.plot(0, 0, "ko", markersize=10, zorder=5)
# New resultant (4 neighbours now)
all_a = np.append(angles_f, flip_angle)
rx2 = np.mean(np.cos(all_a))
ry2 = np.mean(np.sin(all_a))
rmag2 = np.sqrt(rx2**2 + ry2**2)
ax.arrow(0, 0, rx2*0.9, ry2*0.9, head_width=0.08, head_length=0.05,
         fc="orange", ec="orange", linewidth=3, zorder=6)
# Show old resultant faded
ax.arrow(0, 0, rx*0.9, ry*0.9, head_width=0.06, head_length=0.04,
         fc="red", ec="red", linewidth=2, alpha=0.3, zorder=5)
ax.set_xlim(-1.2, 1.2); ax.set_ylim(-1.2, 1.2)
ax.set_aspect("equal")
ax.set_title(f"After phason flip (z=3→4)\nResultant: {rmag:.2f} → {rmag2:.2f}\nDrift reduced",
             fontsize=11, fontweight="bold")
ax.text(0.5, -1.05, "Flip fills gap → reduces imbalance", ha="center", fontsize=9, style="italic")

for ax in axes:
    ax.set_xticks([]); ax.set_yticks([])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(False)

plt.suptitle("Fig 4: The Coordination-Gap Mechanism — Balanced, Boundary, and Phason Flip",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_arrow_convention.png"), dpi=150)
plt.close()

# (5) Binned gap → residue curves (both substrates overlaid)
fig, ax = plt.subplots(figsize=(10, 7))
for wdf, name, color, marker in [(ab_walk, "AB", "steelblue", "s"),
                                   (pen_walk, "Penrose", "coral", "o")]:
    n_bins = 20
    gap_vals = wdf["gap_deg"].values
    bin_edges = np.linspace(gap_vals.min(), gap_vals.max(), n_bins + 1)
    bin_centres = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    bin_means = []
    bin_sems = []
    for j in range(n_bins):
        mask = (gap_vals >= bin_edges[j]) & (gap_vals < bin_edges[j+1])
        vals = wdf.loc[mask, "perp_residue"]
        bin_means.append(vals.mean() if len(vals) > 0 else np.nan)
        bin_sems.append(vals.std() / np.sqrt(len(vals)) if len(vals) > 1 else 0)
    ax.errorbar(bin_centres, bin_means, yerr=bin_sems,
                fmt=f"{marker}-", color=color, linewidth=2, markersize=7,
                capsize=3, label=name)

ax.set_xlabel("Max angular gap (degrees)", fontsize=12)
ax.set_ylabel("Mean perp-space residue", fontsize=12)
ax.set_title("Gap Size → Walk Drift (binned, both substrates)", fontsize=14, fontweight="bold")
ax.legend(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_binned_gap_to_residue.png"), dpi=150)
plt.close()


# ── Report ───────────────────────────────────────────────────

report = []
report.append("# Gap-to-Drift v0.1 — Closing the Mechanism Chain\n")
report.append("## Purpose")
report.append("Close the causal chain: coordination gap → directional balance → walk drift.")
report.append("Previous work showed gap→balance and balance→drift separately.")
report.append("This script shows gap→drift directly and provides a predictor comparison.\n")

report.append("## Predictor comparison\n")
report.append(pred_df.to_markdown(index=False))
report.append("")

report.append("\n## Figures\n")
report.append("1. fig_1 — THE CLOSING LINK: gap → residue (hexbin, both substrates)")
report.append("2. fig_2 — Complete chain: gap → balance → drift (3-panel)")
report.append("3. fig_3 — Predictor horse race (bar chart)")
report.append("4. fig_4 — Arrow convention diagram (balanced / boundary / phason flip)")
report.append("5. fig_5 — Binned gap→residue curves (both substrates overlaid)")

with open(os.path.join(OUT, "gap_to_drift_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll figures and report saved to {OUT}/")
print("Done!")
