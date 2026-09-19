"""
Penrose Vertex-Type & Coordination Gap Analysis v0.1

Runs the same vertex-type classification and coordination-gap analysis
on the Penrose tiling that we ran on AB. Tests whether the gap mechanism
(imbalance anti-aligned with coordination gap, gap size predicts balance)
is universal to projection tilings or specific to AB's octagonal symmetry.

Penrose has 5-fold symmetry, a decagonal acceptance window, and vertex
types with z=3 to z=7 (no z=8). If the mechanism is the same, it tells
us about projection geometry in general. If it differs, the difference
may explain why Penrose lacks AB's address-backup redundancy.
"""

import os, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import spearmanr, kruskal
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "penrose_gap_analysis_v0_1_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75

# Penrose vertex types by coordination (highest to lowest)
# Using letters to parallel the AB convention
PENROSE_TYPE_MAP = {7: "A", 6: "B", 5: "C", 4: "D", 3: "E"}
PENROSE_TYPE_ORDER = ["A", "B", "C", "D", "E"]
PENROSE_TYPE_Z = {t: z for z, t in PENROSE_TYPE_MAP.items()}


def load_penrose():
    verts = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_lift.csv"))
    edges = pd.read_csv(os.path.join(DATA, "clean_penrose_full_raw_edges.csv"))
    n = len(verts)
    adj = defaultdict(list)
    for _, row in edges.iterrows():
        s, t = int(row["source"]), int(row["target"])
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


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


# ── Load ─────────────────────────────────────────────────────

print("Loading Penrose tiling...")
verts, adj_arr, n = load_penrose()
px = verts["perp_x"].values.astype(np.float64)
py = verts["perp_y"].values.astype(np.float64)
depth, perp_centroid = compute_depth(px, py)
phys_r = compute_physical_radius(verts)
r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
interior_mask = phys_r <= r_thresh

degree = np.array([len(adj_arr[i]) for i in range(n)], dtype=int)
vertex_type = np.array([PENROSE_TYPE_MAP.get(d, "X") for d in degree])

print(f"Total vertices: {n}")
print(f"Interior vertices: {int(interior_mask.sum())}")
print(f"\nDegree distribution (all vertices):")
for d in sorted(set(degree)):
    count = (degree == d).sum()
    t = PENROSE_TYPE_MAP.get(d, "X")
    print(f"  degree {d} (type {t}): {count} ({100*count/n:.1f}%)")

# ── Compute gaps and balance ─────────────────────────────────

print("\nComputing coordination gaps and imbalance vectors...")

gap_angle = np.zeros(n)
gap_direction = np.zeros(n)
balance_mag = np.zeros(n)
balance_angle = np.zeros(n)
cos_gap_alignment = np.full(n, np.nan)

for i in range(n):
    nbrs = adj_arr[i]
    k = len(nbrs)
    if k < 2:
        continue

    dx = px[nbrs] - px[i]
    dy = py[nbrs] - py[i]
    angles = np.arctan2(dy, dx)
    angles_sorted = np.sort(angles)

    diffs = np.diff(angles_sorted)
    wrap_gap = (2 * np.pi) - (angles_sorted[-1] - angles_sorted[0])
    all_gaps = np.append(diffs, wrap_gap)

    max_gap_idx = np.argmax(all_gaps)
    gap_angle[i] = all_gaps[max_gap_idx]

    if max_gap_idx < len(angles_sorted) - 1:
        gap_start = angles_sorted[max_gap_idx]
    else:
        gap_start = angles_sorted[-1]
    gap_direction[i] = gap_start + all_gaps[max_gap_idx] / 2
    gap_direction[i] = np.arctan2(np.sin(gap_direction[i]),
                                   np.cos(gap_direction[i]))

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

    if balance_mag[i] > 1e-6:
        angle_diff = balance_angle[i] - gap_direction[i]
        cos_gap_alignment[i] = np.cos(angle_diff)

# ── Build dataframe ──────────────────────────────────────────

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
    "perp_x": px[idx],
    "perp_y": py[idx],
})

df_typed = df[df["vertex_type"] != "X"].copy()
type_rank = {t: i for i, t in enumerate(PENROSE_TYPE_ORDER)}
df_typed["type_rank"] = df_typed["vertex_type"].map(type_rank)
df_has_drift = df_typed[df_typed["balance_mag"] > 1e-6].copy()

print(f"\nInterior typed vertices: {len(df_typed)}")
print(f"Vertices with measurable drift: {len(df_has_drift)}")

# ── TYPE-LEVEL ANALYSIS ─────────────────────────────────────

print(f"\n{'='*70}")
print(f"  PENROSE VERTEX-TYPE CLASSIFICATION")
print(f"{'='*70}")

type_stats = df_typed.groupby("vertex_type").agg(
    count=("depth", "size"),
    mean_depth=("depth", "mean"),
    mean_balance=("balance_mag", "mean"),
    mean_gap_deg=("gap_angle_deg", "mean"),
).reindex(PENROSE_TYPE_ORDER)

print(f"\n{'Type':>4s} {'z':>3s} {'Count':>6s} {'Mean Depth':>11s} {'Mean Balance':>13s} {'Mean Gap°':>10s}")
print("  " + "-" * 52)
for t in PENROSE_TYPE_ORDER:
    if t not in type_stats.index or pd.isna(type_stats.loc[t, "count"]):
        continue
    r = type_stats.loc[t]
    print(f"  {t:>2s}  z={PENROSE_TYPE_Z[t]}  {int(r['count']):>5d}  "
          f"{r['mean_depth']:>9.4f}  {r['mean_balance']:>11.6f}  {r['mean_gap_deg']:>8.1f}°")

# Monotonicity
type_means = type_stats["mean_balance"].dropna().values
monotonic = all(type_means[i] <= type_means[i+1] for i in range(len(type_means)-1))

sp_type_bal, p_type_bal = spearmanr(df_typed["type_rank"], df_typed["balance_mag"])
sp_type_depth, _ = spearmanr(df_typed["type_rank"], df_typed["depth"])
sp_gap_bal, p_gap_bal = spearmanr(df_typed["gap_angle_rad"], df_typed["balance_mag"])

print(f"\n  Monotonic A→E increase in balance: {monotonic}")
print(f"  Spearman(type_rank, balance) = {sp_type_bal:.4f} (p={p_type_bal:.2e})")
print(f"  Spearman(type_rank, depth) = {sp_type_depth:.4f}")
print(f"  Spearman(max_gap, balance) = {sp_gap_bal:.4f} (p={p_gap_bal:.2e})")

groups = [g["balance_mag"].values for _, g in df_typed.groupby("vertex_type") if len(g) > 5]
if len(groups) >= 2:
    H, p_kw = kruskal(*groups)
    print(f"  Kruskal-Wallis H={H:.2f}, p={p_kw:.2e}")

# ── GAP ALIGNMENT ────────────────────────────────────────────

print(f"\n{'='*70}")
print(f"  DOES THE IMBALANCE POINT INTO THE COORDINATION GAP?")
print(f"{'='*70}")

overall_mean_cos = df_has_drift["cos_gap_alignment"].mean()
print(f"\n  Overall mean cos(balance_angle, gap_direction) = {overall_mean_cos:.4f}")
print(f"  (1.0 = into gap, 0.0 = random, -1.0 = away from gap = toward neighbours)")

print(f"\n  {'Type':>4s} {'z':>3s} {'N':>6s} {'Mean cos':>10s} {'Mean gap°':>10s} {'Mean balance':>13s} {'Verdict':>12s}")
print("  " + "-" * 68)
for t in PENROSE_TYPE_ORDER:
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) < 5:
        mc = float("nan")
        verdict = "—"
    else:
        mc = sub["cos_gap_alignment"].mean()
        if mc > 0.3: verdict = "INTO GAP"
        elif mc < -0.3: verdict = "→ NEIGHBOURS"
        else: verdict = "MIXED"
    mg = df_typed[df_typed["vertex_type"] == t]["gap_angle_deg"].mean()
    mb = df_typed[df_typed["vertex_type"] == t]["balance_mag"].mean()
    count = len(sub)
    print(f"  {t:>2s}  z={PENROSE_TYPE_Z[t]}  {count:>5d}  {mc:>8.4f}  {mg:>8.1f}°  {mb:>11.6f}  {verdict:>12s}")

# ── GAP SIZE ANALYSIS ────────────────────────────────────────

print(f"\n{'='*70}")
print(f"  GAP SIZE: EXPECTED vs ACTUAL")
print(f"{'='*70}")

for t in PENROSE_TYPE_ORDER:
    sub = df_typed[df_typed["vertex_type"] == t]
    if len(sub) < 5:
        continue
    z = PENROSE_TYPE_Z[t]
    expected = 360.0 / z
    actual = sub["gap_angle_deg"].mean()
    excess = actual - expected
    print(f"  Type {t} (z={z}): expected {expected:.1f}°, actual {actual:.1f}°, excess {excess:+.1f}°")

# ── CROSS-SUBSTRATE COMPARISON ───────────────────────────────

print(f"\n{'='*70}")
print(f"  CROSS-SUBSTRATE COMPARISON (Penrose vs AB)")
print(f"{'='*70}")

# AB results from prior run (hardcoded for comparison)
ab_results = {
    "A": {"z": 8, "balance": 0.000, "gap": 45.0, "cos": None},
    "B": {"z": 7, "balance": 0.143, "gap": 90.0, "cos": -1.000},
    "C": {"z": 6, "balance": 0.307, "gap": 134.9, "cos": -0.998},
    "D": {"z": 5, "balance": 0.483, "gap": 179.9, "cos": -1.000},
    "E": {"z": 4, "balance": 0.653, "gap": 225.0, "cos": -1.000},
    "F": {"z": 3, "balance": 0.805, "gap": 270.0, "cos": -1.000},
}

print(f"\n  Shared coordination numbers (both substrates have these z values):")
print(f"  {'z':>3s} | {'AB Balance':>11s} {'AB Gap°':>8s} {'AB cos':>8s} | {'Pen Balance':>12s} {'Pen Gap°':>9s} {'Pen cos':>9s}")
print("  " + "-" * 70)
for z in [7, 6, 5, 4, 3]:
    ab_t = {v["z"]: k for k, v in ab_results.items()}.get(z)
    pen_t = {v: k for k, v in PENROSE_TYPE_Z.items()}.get(z)
    if ab_t and pen_t:
        ab = ab_results[ab_t]
        pen_sub = df_typed[df_typed["vertex_type"] == pen_t]
        pen_drift = df_has_drift[df_has_drift["vertex_type"] == pen_t]
        pen_bal = pen_sub["balance_mag"].mean()
        pen_gap = pen_sub["gap_angle_deg"].mean()
        pen_cos = pen_drift["cos_gap_alignment"].mean() if len(pen_drift) > 5 else float("nan")
        ab_cos_str = f"{ab['cos']:.3f}" if ab['cos'] is not None else "—"
        print(f"  z={z} | {ab['balance']:>9.3f}  {ab['gap']:>7.1f}°  {ab_cos_str:>7s} | "
              f"{pen_bal:>10.3f}  {pen_gap:>8.1f}°  {pen_cos:>8.3f}")


# ── Save ─────────────────────────────────────────────────────

df_typed.to_csv(os.path.join(OUT, "penrose_vertex_type_data.csv"), index=False)
type_stats.to_csv(os.path.join(OUT, "penrose_type_summary.csv"))
print(f"\nData saved to {OUT}/")

# ── Figures ──────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TYPE_COLORS = {"A": "#1a0a3e", "B": "#3b1f8e", "C": "#6b3fa0",
               "D": "#d4a5e5", "E": "#f0d9ff"}

# (1) Acceptance window triptych
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

ax = axes[0]
for t in reversed(PENROSE_TYPE_ORDER):
    sub = df_typed[df_typed["vertex_type"] == t]
    ax.scatter(sub["perp_x"], sub["perp_y"], c=TYPE_COLORS[t],
               s=2, alpha=0.5, label=f"Type {t} (z={PENROSE_TYPE_Z[t]})",
               zorder=PENROSE_TYPE_ORDER.index(t)+1)
ax.set_title("Penrose: vertex types", fontsize=12)
ax.legend(fontsize=8, markerscale=4, loc="upper left")
ax.set_aspect("equal")

ax = axes[1]
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["balance_mag"], s=2, alpha=0.5,
                cmap="YlOrRd", vmin=0)
ax.set_title("Penrose: directional balance", fontsize=12)
plt.colorbar(sc, ax=ax, label="Balance B(v)")
ax.set_aspect("equal")

ax = axes[2]
sc = ax.scatter(df_typed["perp_x"], df_typed["perp_y"],
                c=df_typed["depth"], s=2, alpha=0.5,
                cmap="viridis", vmin=0, vmax=1)
ax.set_title("Penrose: hull depth", fontsize=12)
plt.colorbar(sc, ax=ax, label="Depth")
ax.set_aspect("equal")

for ax in axes:
    ax.set_xlabel("perp_x"); ax.set_ylabel("perp_y")

plt.suptitle("Fig 1: Penrose Acceptance Window — Types / Balance / Depth",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_penrose_window_triptych.png"), dpi=150)
plt.close()

# (2) Step function: balance and depth by type
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
types_present = [t for t in PENROSE_TYPE_ORDER if t in df_typed["vertex_type"].values]
positions = range(len(types_present))

ax = axes[0]
means = [df_typed[df_typed["vertex_type"]==t]["balance_mag"].mean() for t in types_present]
stds = [df_typed[df_typed["vertex_type"]==t]["balance_mag"].std() for t in types_present]
counts = [len(df_typed[df_typed["vertex_type"]==t]) for t in types_present]
ax.bar(positions, means, yerr=stds, color=[TYPE_COLORS[t] for t in types_present],
       edgecolor="black", linewidth=0.5, capsize=4, alpha=0.85)
ax.plot(positions, means, "r--", linewidth=2, alpha=0.7, zorder=5)
ax.set_xticks(positions)
ax.set_xticklabels([f"{t}\n(z={PENROSE_TYPE_Z[t]})\nn={c}" for t, c in zip(types_present, counts)], fontsize=9)
ax.set_ylabel("Mean directional balance B(v)", fontsize=11)
ax.set_title("Penrose: balance by type", fontsize=13)

ax = axes[1]
depth_means = [df_typed[df_typed["vertex_type"]==t]["depth"].mean() for t in types_present]
depth_stds = [df_typed[df_typed["vertex_type"]==t]["depth"].std() for t in types_present]
ax.bar(positions, depth_means, yerr=depth_stds,
       color=[TYPE_COLORS[t] for t in types_present],
       edgecolor="black", linewidth=0.5, capsize=4, alpha=0.85)
ax.plot(positions, depth_means, "r--", linewidth=2, alpha=0.7, zorder=5)
ax.set_xticks(positions)
ax.set_xticklabels([f"{t}\n(z={PENROSE_TYPE_Z[t]})" for t in types_present], fontsize=9)
ax.set_ylabel("Mean hull depth", fontsize=11)
ax.set_title("Penrose: depth by type", fontsize=13)

plt.suptitle("Fig 2: Penrose Step Function — Type Maps to Balance and Depth",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_penrose_step_function.png"), dpi=150)
plt.close()

# (3) Gap alignment by type
fig, axes = plt.subplots(1, len(types_present), figsize=(4*len(types_present), 4))
if len(types_present) == 1:
    axes = [axes]
for ax, t in zip(axes, types_present):
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) < 5:
        ax.text(0.5, 0.5, "too few", transform=ax.transAxes, ha="center")
        continue
    ax.hist(sub["cos_gap_alignment"], bins=40, color=TYPE_COLORS[t],
            edgecolor="black", linewidth=0.3, alpha=0.8, density=True)
    ax.axvline(0, color="gray", linewidth=1, linestyle="--")
    ax.axvline(sub["cos_gap_alignment"].mean(), color="red", linewidth=2,
               label=f"mean={sub['cos_gap_alignment'].mean():.3f}")
    ax.set_title(f"Type {t} (z={PENROSE_TYPE_Z[t]})", fontsize=11)
    ax.set_xlabel("cos(balance, gap)")
    ax.legend(fontsize=8)
plt.suptitle("Fig 3: Penrose — Does Imbalance Point Into or Away From Gap?",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_penrose_gap_alignment.png"), dpi=150)
plt.close()

# (4) Gap size vs balance
fig, ax = plt.subplots(figsize=(10, 7))
for t in types_present:
    sub = df_typed[df_typed["vertex_type"] == t]
    ax.scatter(sub["gap_angle_deg"], sub["balance_mag"],
               c=TYPE_COLORS[t], s=4, alpha=0.3,
               label=f"Type {t} (z={PENROSE_TYPE_Z[t]})")
ax.set_xlabel("Largest angular gap (degrees)", fontsize=12)
ax.set_ylabel("Directional balance B(v)", fontsize=12)
ax.set_title(f"Penrose: Gap Size vs Balance (Spearman = {sp_gap_bal:.4f})",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=9, markerscale=3)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_penrose_gap_vs_balance.png"), dpi=150)
plt.close()

# (5) Polar plots
fig, axes = plt.subplots(1, len(types_present), figsize=(4*len(types_present), 4),
                          subplot_kw={"projection": "polar"})
if len(types_present) == 1:
    axes = [axes]
for ax, t in zip(axes, types_present):
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) < 10:
        ax.set_title(f"Type {t} (too few)")
        continue
    angle_diff = sub["balance_angle"].values - sub["gap_direction"].values
    angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))
    n_bins = 36
    hist, bin_edges = np.histogram(angle_diff, bins=n_bins, range=(-np.pi, np.pi))
    bin_centres = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    hist = hist / hist.sum()
    ax.bar(bin_centres, hist, width=2*np.pi/n_bins,
           color=TYPE_COLORS[t], edgecolor="black", linewidth=0.3, alpha=0.7)
    ax.axvline(0, color="red", linewidth=2)
    ax.set_title(f"Type {t} (z={PENROSE_TYPE_Z[t]})\ncos={sub['cos_gap_alignment'].mean():.3f}",
                 fontsize=10, pad=10)
    ax.set_yticklabels([])
plt.suptitle("Fig 5: Penrose Polar — Balance Direction Relative to Gap\n(0° = into gap)",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_penrose_polar.png"), dpi=150)
plt.close()

# (6) CROSS-SUBSTRATE comparison figure
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Balance by z (both substrates)
ax = axes[0]
ab_z = [8, 7, 6, 5, 4, 3]
ab_bal = [0.000, 0.143, 0.307, 0.483, 0.653, 0.805]
pen_z_vals = []
pen_bal_vals = []
for t in types_present:
    z = PENROSE_TYPE_Z[t]
    pen_z_vals.append(z)
    pen_bal_vals.append(df_typed[df_typed["vertex_type"]==t]["balance_mag"].mean())

ax.plot(ab_z, ab_bal, "s-", color="steelblue", linewidth=2, markersize=8, label="AB")
ax.plot(pen_z_vals, pen_bal_vals, "o-", color="coral", linewidth=2, markersize=8, label="Penrose")
ax.set_xlabel("Coordination number z", fontsize=12)
ax.set_ylabel("Mean directional balance", fontsize=12)
ax.set_title("Balance vs coordination", fontsize=13)
ax.legend(fontsize=11)
ax.invert_xaxis()

# Gap size by z
ax = axes[1]
ab_gap = [45.0, 90.0, 134.9, 179.9, 225.0, 270.0]
pen_gap_vals = []
for t in types_present:
    pen_gap_vals.append(df_typed[df_typed["vertex_type"]==t]["gap_angle_deg"].mean())

ax.plot(ab_z, ab_gap, "s-", color="steelblue", linewidth=2, markersize=8, label="AB")
ax.plot(pen_z_vals, pen_gap_vals, "o-", color="coral", linewidth=2, markersize=8, label="Penrose")
ax.set_xlabel("Coordination number z", fontsize=12)
ax.set_ylabel("Largest angular gap (degrees)", fontsize=12)
ax.set_title("Gap size vs coordination", fontsize=13)
ax.legend(fontsize=11)
ax.invert_xaxis()

# Cos alignment by z
ax = axes[2]
ab_cos = [-1.0, -1.0, -0.998, -1.0, -1.0, -1.0]
pen_cos_vals = []
for t in types_present:
    sub = df_has_drift[df_has_drift["vertex_type"] == t]
    if len(sub) > 5:
        pen_cos_vals.append(sub["cos_gap_alignment"].mean())
    else:
        pen_cos_vals.append(float("nan"))

ax.plot(ab_z[1:], ab_cos[1:], "s-", color="steelblue", linewidth=2, markersize=8, label="AB")
ax.plot(pen_z_vals, pen_cos_vals, "o-", color="coral", linewidth=2, markersize=8, label="Penrose")
ax.axhline(-1.0, color="gray", linewidth=1, linestyle="--", alpha=0.5)
ax.axhline(0, color="gray", linewidth=1, linestyle="--", alpha=0.5)
ax.set_xlabel("Coordination number z", fontsize=12)
ax.set_ylabel("Mean cos(balance, gap direction)", fontsize=12)
ax.set_title("Gap alignment vs coordination", fontsize=13)
ax.legend(fontsize=11)
ax.invert_xaxis()
ax.set_ylim(-1.2, 0.5)

plt.suptitle("Fig 6: CROSS-SUBSTRATE COMPARISON — AB (blue) vs Penrose (coral)",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_cross_substrate_comparison.png"), dpi=150)
plt.close()


# ── Report ───────────────────────────────────────────────────

report = []
report.append("# Penrose Vertex-Type & Coordination Gap Analysis v0.1\n")
report.append("## Question")
report.append("Does the coordination-gap mechanism found in AB (imbalance anti-aligned")
report.append("with gap, gap size predicts balance) also hold for Penrose?\n")

report.append("## Penrose type summary\n")
report.append(type_stats.to_markdown())
report.append("")

report.append(f"\n## Key statistics\n")
report.append(f"- Monotonic A→E increase in balance: {monotonic}")
report.append(f"- Spearman(type_rank, balance) = {sp_type_bal:.4f}")
report.append(f"- Spearman(type_rank, depth) = {sp_type_depth:.4f}")
report.append(f"- Spearman(max_gap, balance) = {sp_gap_bal:.4f}")
report.append(f"- Overall cos(balance, gap) = {overall_mean_cos:.4f}")

report.append(f"\n## Figures\n")
report.append("1. fig_1 — Penrose acceptance window triptych")
report.append("2. fig_2 — Step function (balance and depth by type)")
report.append("3. fig_3 — Gap alignment histograms")
report.append("4. fig_4 — Gap size vs balance scatter")
report.append("5. fig_5 — Polar plots of balance relative to gap")
report.append("6. fig_6 — CROSS-SUBSTRATE COMPARISON (AB vs Penrose)")

with open(os.path.join(OUT, "penrose_gap_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll figures and report saved to {OUT}/")
print("Done!")
