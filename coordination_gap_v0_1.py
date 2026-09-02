"""
Coordination Gap Analysis v0.1

Tests whether the directional imbalance vector points toward the GAP
in a vertex's coordination shell — the angular sector where neighbours
are missing compared to a fully-coordinated (type A, z=8) vertex.

Motivation: boundary vertices (type F, z=3) have 5 "missing" directions
compared to a type A vertex. If the balance vector points into that gap,
it identifies exactly where a phason flip would add the missing neighbour.

This is a Claude-initiated tangent from the phason susceptibility results,
where drift direction was random relative to the nearest window EDGE
(cos alignment ~0.001) but might not be random relative to the
coordination GAP.
"""

import os, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr, circmean
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "coordination_gap_v0_1_results")
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


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


def compute_depth(px, py):
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)
    max_dist = np.max(np.linalg.norm(pts[hull.vertices] - centroid, axis=1))
    dist = np.linalg.norm(pts - centroid, axis=1)
    depth = 1.0 - (dist / (max_dist + 1e-12))
    return np.clip(depth, 0, 1)


# ── Load ─────────────────────────────────────────────────────

print("Loading AB tiling...")
verts, adj_arr, n = load_ab()
px = verts["perp_x"].values.astype(np.float64)
py = verts["perp_y"].values.astype(np.float64)
depth = compute_depth(px, py)
phys_r = compute_physical_radius(verts)
r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
interior_mask = phys_r <= r_thresh

degree = np.array([len(adj_arr[i]) for i in range(n)], dtype=int)
vertex_type = np.array([TYPE_MAP.get(d, "G") for d in degree])

# ── For each vertex, compute: ────────────────────────────────
# 1. Perp-space angles to all neighbours
# 2. The largest angular gap in the coordination shell
# 3. The direction of the gap centre
# 4. The directional imbalance vector (resultant of unit vectors)
# 5. Whether the imbalance points INTO the gap

print("Computing coordination gaps and imbalance vectors...")

gap_angle = np.zeros(n)        # size of largest angular gap (radians)
gap_direction = np.zeros(n)    # angle pointing into centre of largest gap
balance_mag = np.zeros(n)      # |resultant of unit vectors|
balance_angle = np.zeros(n)    # direction of resultant
cos_gap_alignment = np.full(n, np.nan)  # cos(balance_angle - gap_direction)
n_gaps_above_expected = np.zeros(n, dtype=int)  # gaps larger than 2pi/z

for i in range(n):
    nbrs = adj_arr[i]
    k = len(nbrs)
    if k < 2:
        continue

    # Perp-space displacements to neighbours
    dx = px[nbrs] - px[i]
    dy = py[nbrs] - py[i]

    # Angles to neighbours in perp-space
    angles = np.arctan2(dy, dx)
    angles_sorted = np.sort(angles)

    # Angular gaps between consecutive neighbours (circular)
    diffs = np.diff(angles_sorted)
    wrap_gap = (2 * np.pi) - (angles_sorted[-1] - angles_sorted[0])
    all_gaps = np.append(diffs, wrap_gap)

    # Largest gap
    max_gap_idx = np.argmax(all_gaps)
    gap_angle[i] = all_gaps[max_gap_idx]

    # Direction into the centre of the largest gap
    if max_gap_idx < len(angles_sorted) - 1:
        gap_start = angles_sorted[max_gap_idx]
    else:
        gap_start = angles_sorted[-1]
    gap_direction[i] = gap_start + all_gaps[max_gap_idx] / 2
    # Normalise to [-pi, pi]
    gap_direction[i] = np.arctan2(np.sin(gap_direction[i]),
                                   np.cos(gap_direction[i]))

    # Expected gap for a perfectly regular z-gon
    expected_gap = 2 * np.pi / k
    n_gaps_above_expected[i] = int(np.sum(all_gaps > expected_gap * 1.5))

    # Directional imbalance (resultant of unit vectors)
    lengths = np.sqrt(dx**2 + dy**2)
    mask = lengths > 1e-12
    if mask.sum() == 0:
        continue
    ux = np.zeros_like(dx); uy = np.zeros_like(dy)
    ux[mask] = dx[mask] / lengths[mask]
    uy[mask] = dy[mask] / lengths[mask]
    mean_ux, mean_uy = ux.mean(), uy.mean()
    balance_mag[i] = np.sqrt(mean_ux**2 + mean_uy**2)
    balance_angle[i] = np.arctan2(mean_uy, mean_ux)

    # Alignment: does the imbalance point INTO the gap?
    if balance_mag[i] > 1e-6:
        angle_diff = balance_angle[i] - gap_direction[i]
        cos_gap_alignment[i] = np.cos(angle_diff)

# ── Build interior dataframe ─────────────────────────────────

idx = np.where(interior_mask)[0]
df = pd.DataFrame({
    "vertex_id": idx,
    "degree": degree[idx],
    "vertex_type": vertex_type[idx],
    "depth": depth[idx],
    "balance_mag": balance_mag[idx],
    "balance_angle": balance_angle[idx],
    "gap_angle_rad": gap_angle[idx],
    "gap_angle_deg": np.degrees(gap_angle[idx]),
    "gap_direction": gap_direction[idx],
    "cos_gap_alignment": cos_gap_alignment[idx],
    "n_oversized_gaps": n_gaps_above_expected[idx],
})

df_typed = df[df["vertex_type"] != "G"].copy()
df_has_drift = df_typed[df_typed["balance_mag"] > 1e-6].copy()

# Also add perp coords for plotting
df_typed["perp_x"] = px[df_typed["vertex_id"].values]
df_typed["perp_y"] = py[df_typed["vertex_id"].values]
df_has_drift["perp_x"] = px[df_has_drift["vertex_id"].values]
df_has_drift["perp_y"] = py[df_has_drift["vertex_id"].values]

print(f"Interior typed vertices: {len(df_typed)}")
print(f"Vertices with measurable drift: {len(df_has_drift)}")

# ── THE KEY RESULT ───────────────────────────────────────────

print(f"\n{'='*70}")
print(f"  DOES THE IMBALANCE POINT INTO THE COORDINATION GAP?")
print(f"{'='*70}")

overall_mean_cos = df_has_drift["cos_gap_alignment"].mean()
print(f"\n  Overall mean cos(balance_angle, gap_direction) = {overall_mean_cos:.4f}")
print(f"  (1.0 = points straight into gap, 0.0 = random, -1.0 = away from gap)")

# By type
print(f"\n  {'Type':>4s} {'z':>3s} {'N':>6s} {'Mean cos':>10s} {'Mean gap°':>10s} {'Mean balance':>13s} {'Verdict':>10s}")
print("  " + "-" * 64)
for t in TYPE_ORDER:
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) < 5:
        mc = float("nan")
        verdict = "—"
    else:
        mc = sub["cos_gap_alignment"].mean()
        if mc > 0.3:
            verdict = "INTO GAP"
        elif mc < -0.3:
            verdict = "AWAY"
        else:
            verdict = "MIXED"
    mg = df_typed[df_typed["vertex_type"] == t]["gap_angle_deg"].mean()
    mb = df_typed[df_typed["vertex_type"] == t]["balance_mag"].mean()
    count = len(sub)
    print(f"  {t:>2s}  z={TYPE_Z[t]}  {count:>5d}  {mc:>8.4f}  {mg:>8.1f}°  {mb:>11.6f}  {verdict:>10s}")

# Correlation: gap size vs balance magnitude
sp_gap_bal, p_gap_bal = spearmanr(df_typed["gap_angle_rad"], df_typed["balance_mag"])
print(f"\n  Spearman(max_gap_size, balance_mag) = {sp_gap_bal:.4f} (p={p_gap_bal:.2e})")

# Correlation: cos alignment vs balance magnitude
sp_cos_bal, p_cos_bal = spearmanr(df_has_drift["cos_gap_alignment"],
                                   df_has_drift["balance_mag"])
print(f"  Spearman(cos_alignment, balance_mag) = {sp_cos_bal:.4f} (p={p_cos_bal:.2e})")
print(f"  (do vertices with MORE imbalance also point MORE into their gap?)")

# Gap size by type
print(f"\n{'='*70}")
print(f"  GAP SIZE ANALYSIS")
print(f"{'='*70}")

for t in TYPE_ORDER:
    sub = df_typed[df_typed["vertex_type"] == t]
    if len(sub) < 5:
        continue
    z = TYPE_Z[t]
    expected = 360.0 / z
    actual = sub["gap_angle_deg"].mean()
    excess = actual - expected
    print(f"  Type {t} (z={z}): expected gap {expected:.1f}°, "
          f"actual max gap {actual:.1f}°, excess {excess:+.1f}°")


# ── Save ─────────────────────────────────────────────────────

df_typed.to_csv(os.path.join(OUT, "coordination_gap_data.csv"), index=False)
print(f"\nData saved to {OUT}/")

# ── Figures ──────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TYPE_COLORS = {"A": "#1a0a3e", "B": "#3b1f8e", "C": "#6b3fa0",
               "D": "#9b59b6", "E": "#d4a5e5", "F": "#f0d9ff"}

# (1) THE KEY FIGURE: cos alignment distribution by type
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
for ax, t in zip(axes.flat, TYPE_ORDER):
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) < 5:
        ax.text(0.5, 0.5, f"Type {t}\ntoo few", transform=ax.transAxes,
                ha="center", va="center")
        continue
    ax.hist(sub["cos_gap_alignment"], bins=40, color=TYPE_COLORS[t],
            edgecolor="black", linewidth=0.3, alpha=0.8, density=True)
    ax.axvline(0, color="gray", linewidth=1, linestyle="--")
    ax.axvline(sub["cos_gap_alignment"].mean(), color="red",
               linewidth=2, linestyle="-", label=f"mean={sub['cos_gap_alignment'].mean():.3f}")
    ax.set_title(f"Type {t} (z={TYPE_Z[t]}, n={len(sub)})", fontsize=12)
    ax.set_xlabel("cos(balance, gap direction)")
    ax.legend(fontsize=9)
plt.suptitle("Fig 1: Does the Imbalance Vector Point Into the Coordination Gap?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_gap_alignment_by_type.png"), dpi=150)
plt.close()

# (2) Gap size vs balance magnitude
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax = axes[0]
for t in TYPE_ORDER:
    sub = df_typed[df_typed["vertex_type"] == t]
    ax.scatter(sub["gap_angle_deg"], sub["balance_mag"],
               c=TYPE_COLORS[t], s=4, alpha=0.3,
               label=f"Type {t} (z={TYPE_Z[t]})")
ax.set_xlabel("Largest angular gap (degrees)", fontsize=12)
ax.set_ylabel("Directional balance B(v)", fontsize=12)
ax.set_title(f"Gap size vs balance\nSpearman = {sp_gap_bal:.4f}", fontsize=13)
ax.legend(fontsize=8, markerscale=3)

ax = axes[1]
types_present = [t for t in TYPE_ORDER if t in df_typed["vertex_type"].values]
gap_data = [df_typed[df_typed["vertex_type"]==t]["gap_angle_deg"].values
            for t in types_present]
bp = ax.boxplot(gap_data,
                tick_labels=[f"{t}\n(z={TYPE_Z[t]})" for t in types_present],
                patch_artist=True, showmeans=True)
for i, patch in enumerate(bp["boxes"]):
    patch.set_facecolor(TYPE_COLORS[types_present[i]])
    patch.set_alpha(0.7)
# Add expected gap lines
for i, t in enumerate(types_present):
    expected = 360.0 / TYPE_Z[t]
    ax.plot([i + 0.6, i + 1.4], [expected, expected], "r--", linewidth=1.5)
ax.set_ylabel("Largest angular gap (degrees)", fontsize=11)
ax.set_xlabel("Vertex type", fontsize=11)
ax.set_title("Max gap by type\n(red dashed = expected for regular polygon)", fontsize=12)

plt.suptitle("Fig 2: Coordination Gap Size Predicts Balance Magnitude",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_gap_size_vs_balance.png"), dpi=150)
plt.close()

# (3) Polar plot: for each type, show the distribution of
# (balance_angle - gap_direction) — if clustered near 0, drift points into gap
fig, axes = plt.subplots(2, 3, figsize=(14, 10), subplot_kw={"projection": "polar"})
for ax, t in zip(axes.flat, TYPE_ORDER):
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) < 10:
        ax.set_title(f"Type {t} (too few)")
        continue
    angle_diff = sub["balance_angle"].values - sub["gap_direction"].values
    angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

    n_bins = 36
    hist, bin_edges = np.histogram(angle_diff, bins=n_bins, range=(-np.pi, np.pi))
    bin_centres = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    # Normalise
    hist = hist / hist.sum()

    bars = ax.bar(bin_centres, hist, width=2*np.pi/n_bins,
                  color=TYPE_COLORS[t], edgecolor="black", linewidth=0.3, alpha=0.7)
    # Mark 0 direction (= into the gap)
    ax.axvline(0, color="red", linewidth=2, linestyle="-")
    ax.set_title(f"Type {t} (z={TYPE_Z[t]})\nmean cos={sub['cos_gap_alignment'].mean():.3f}",
                 fontsize=11, pad=10)
    ax.set_yticklabels([])

plt.suptitle("Fig 3: Polar Distribution of Balance Direction Relative to Gap\n"
             "(0° = pointing into gap, red line)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_polar_gap_alignment.png"), dpi=150)
plt.close()

# (4) Perp-space map with gap directions and balance directions
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Subsample for arrow clarity
rng = np.random.default_rng(42)
arrow_sub = df_has_drift[df_has_drift["balance_mag"] > 0.3]
if len(arrow_sub) > 600:
    arrow_sub = arrow_sub.sample(600, random_state=42)

ax = axes[0]
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["gap_angle_deg"], s=2, alpha=0.3, cmap="YlOrRd")
scale = 0.08
for _, row in arrow_sub.iterrows():
    ax.arrow(row["perp_x"], row["perp_y"],
             scale * np.cos(row["balance_angle"]),
             scale * np.sin(row["balance_angle"]),
             head_width=0.008, head_length=0.004,
             fc="blue", ec="blue", alpha=0.5, linewidth=0.4)
plt.colorbar(sc, ax=ax, label="Largest gap (degrees)")
ax.set_title("Balance vectors (blue) on gap-coloured window", fontsize=12)
ax.set_aspect("equal")
ax.set_xlabel("perp_x"); ax.set_ylabel("perp_y")

ax = axes[1]
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["cos_gap_alignment"], s=2, alpha=0.3,
                cmap="RdBu", vmin=-1, vmax=1)
plt.colorbar(sc, ax=ax, label="cos(balance, gap)\n(blue=into gap, red=away)")
ax.set_title("Gap alignment across the window", fontsize=12)
ax.set_aspect("equal")
ax.set_xlabel("perp_x"); ax.set_ylabel("perp_y")

plt.suptitle("Fig 4: Balance Vectors and Gap Alignment in Perp-Space",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_perp_space_gap_alignment.png"), dpi=150)
plt.close()

# (5) Summary bar chart: mean cos alignment by type
fig, ax = plt.subplots(figsize=(10, 6))
means = []
stds = []
ns = []
for t in types_present:
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) >= 5:
        means.append(sub["cos_gap_alignment"].mean())
        stds.append(sub["cos_gap_alignment"].std() / np.sqrt(len(sub)))
        ns.append(len(sub))
    else:
        means.append(0)
        stds.append(0)
        ns.append(0)

bars = ax.bar(range(len(types_present)), means, yerr=stds,
              color=[TYPE_COLORS[t] for t in types_present],
              edgecolor="black", linewidth=0.5, capsize=5, alpha=0.85)
ax.axhline(0, color="gray", linewidth=1, linestyle="--")
ax.set_xticks(range(len(types_present)))
ax.set_xticklabels([f"Type {t}\n(z={TYPE_Z[t]})\nn={c}" for t, c in zip(types_present, ns)],
                    fontsize=9)
ax.set_ylabel("Mean cos(balance direction, gap direction)\n(>0 = into gap)", fontsize=11)
ax.set_title("Fig 5: Imbalance-Gap Alignment by Vertex Type",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_alignment_summary.png"), dpi=150)
plt.close()


# ── Report ───────────────────────────────────────────────────

report = []
report.append("# Coordination Gap Analysis v0.1\n")
report.append("## Question")
report.append("The phason susceptibility analysis showed drift direction is RANDOM")
report.append("relative to the nearest acceptance-window edge. But is it random")
report.append("relative to the GAP in the vertex's coordination shell?\n")
report.append("A type F vertex (z=3) has 5 'missing' directions compared to type A (z=8).")
report.append("If the imbalance vector points into the angular sector where neighbours")
report.append("are absent, it identifies exactly where a phason flip would add a neighbour.\n")

report.append("## Method")
report.append("1. For each vertex, compute angles to all neighbours in perp-space")
report.append("2. Find the largest angular gap in the coordination shell")
report.append("3. Compute the gap centre direction")
report.append("4. Compute the directional imbalance vector (resultant of unit vectors)")
report.append("5. Measure cos(balance_angle - gap_direction)")
report.append("   1.0 = points into gap, 0.0 = random, -1.0 = away from gap\n")

report.append("## Key results\n")
report.append(f"- Overall mean cos(balance, gap) = {overall_mean_cos:.4f}")
report.append(f"- Spearman(max_gap_size, balance_mag) = {sp_gap_bal:.4f}")
report.append(f"- Spearman(cos_alignment, balance_mag) = {sp_cos_bal:.4f}\n")

report.append("## Figures\n")
report.append("1. fig_1 — Cos alignment histograms by type")
report.append("2. fig_2 — Gap size vs balance magnitude")
report.append("3. fig_3 — Polar plots: balance direction relative to gap")
report.append("4. fig_4 — Perp-space map with vectors and alignment")
report.append("5. fig_5 — Summary: mean alignment by type")

with open(os.path.join(OUT, "coordination_gap_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll figures and report saved to {OUT}/")
print("Done!")
