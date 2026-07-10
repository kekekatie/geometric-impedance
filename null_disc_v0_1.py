"""
Null-disc control v0.1

The critical test: is the inward radial drift just a trivial consequence
of being inside a bounded shape? Or does the quasicrystal structure add
something a featureless disc can't?

Three comparisons:
1. REAL TILING: the actual quasicrystal (our existing measurement)
2. NULL DISC: random uniform points in the same hull shape, Delaunay-connected
3. SHUFFLED PERP: same tiling graph, perp-space coordinates randomly shuffled

If real ≈ null disc → drift is just boundary bookkeeping
If real ≠ null disc → the quasicrystal structure matters
"""

import os, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull, Delaunay
from scipy.stats import spearmanr
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "null_disc_v0_1_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75
N_DEPTH_BINS  = 40
N_NULL_SEEDS  = 5


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


def compute_radial_drift_profile(px, py, adj_arr, n, n_bins=N_DEPTH_BINS,
                                  interior_mask=None):
    """Compute depth and radial drift for a set of points with adjacency."""
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    centroid = pts[hull.vertices].mean(axis=0)
    max_dist = np.max(np.linalg.norm(pts[hull.vertices] - centroid, axis=1))
    dist = np.linalg.norm(pts - centroid, axis=1)
    depth = np.clip(1.0 - (dist / (max_dist + 1e-12)), 0, 1)

    pos_x = px - centroid[0]
    pos_y = py - centroid[1]
    pos_mag = np.sqrt(pos_x**2 + pos_y**2)

    drift_x = np.zeros(n)
    drift_y = np.zeros(n)
    drift_mag = np.zeros(n)

    for i in range(n):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        dx = px[nbrs] - px[i]
        dy = py[nbrs] - py[i]
        drift_x[i] = dx.mean()
        drift_y[i] = dy.mean()
        drift_mag[i] = np.sqrt(drift_x[i]**2 + drift_y[i]**2)

    pos_ux = np.where(pos_mag > 1e-12, pos_x / pos_mag, 0)
    pos_uy = np.where(pos_mag > 1e-12, pos_y / pos_mag, 0)
    radial_drift = drift_x * pos_ux + drift_y * pos_uy

    if interior_mask is not None:
        idx = np.where(interior_mask)[0]
    else:
        idx = np.arange(n)

    df = pd.DataFrame({
        "depth": depth[idx],
        "radial_drift": radial_drift[idx],
        "drift_mag": drift_mag[idx],
    })
    df["depth_bin"] = pd.cut(df["depth"], bins=n_bins)
    binned = df.groupby("depth_bin", observed=True).agg(
        mean_depth=("depth", "mean"),
        mean_radial=("radial_drift", "mean"),
        mean_drift_mag=("drift_mag", "mean"),
        n=("depth", "size"),
    ).reset_index()

    sp, sp_p = spearmanr(df["depth"], df["radial_drift"])

    return binned, sp, df


def generate_null_disc(px, py, n_points, seed):
    """Generate random uniform points inside the convex hull of (px, py)."""
    rng = np.random.default_rng(seed)
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    hull_pts = pts[hull.vertices]

    # Bounding box
    xmin, xmax = hull_pts[:, 0].min(), hull_pts[:, 0].max()
    ymin, ymax = hull_pts[:, 1].min(), hull_pts[:, 1].max()

    # Rejection sampling inside hull
    delaunay = Delaunay(hull_pts)
    collected = []
    while len(collected) < n_points:
        batch = rng.uniform(
            [xmin, ymin], [xmax, ymax],
            size=(n_points * 2, 2)
        )
        inside = delaunay.find_simplex(batch) >= 0
        collected.extend(batch[inside].tolist())
    collected = np.array(collected[:n_points])

    # Connect via Delaunay triangulation
    tri = Delaunay(collected)
    adj = defaultdict(set)
    for simplex in tri.simplices:
        for i in range(3):
            for j in range(i + 1, 3):
                adj[simplex[i]].add(simplex[j])
                adj[simplex[j]].add(simplex[i])
    adj_arr = [np.array(list(adj[i]), dtype=np.int32) for i in range(n_points)]

    return collected[:, 0], collected[:, 1], adj_arr, n_points


def analyse_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Analysing {name}")
    print(f"{'='*60}")

    verts, adj_arr, n = load_substrate(name)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)

    from functools import reduce
    phys_r = np.sqrt((verts["x"].values - verts["x"].median())**2 +
                      (verts["y"].values - verts["y"].median())**2)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh

    # 1. Real tiling
    print("  Computing real tiling profile...")
    real_binned, real_sp, real_df = compute_radial_drift_profile(
        px, py, adj_arr, n, interior_mask=interior_mask)
    real_binned["model"] = "real"
    real_binned["substrate"] = name
    print(f"    Spearman(depth, radial) = {real_sp:.4f}")

    # 2. Null disc (multiple seeds)
    print(f"  Computing null disc profiles ({N_NULL_SEEDS} seeds)...")
    null_binneds = []
    null_sps = []
    n_interior = int(interior_mask.sum())
    for seed in range(N_NULL_SEEDS):
        null_px, null_py, null_adj, null_n = generate_null_disc(
            px, py, n_interior, seed=seed + 100)
        nb, nsp, _ = compute_radial_drift_profile(
            null_px, null_py, null_adj, null_n)
        nb["model"] = f"null_disc_s{seed}"
        nb["substrate"] = name
        null_binneds.append(nb)
        null_sps.append(nsp)
        print(f"    Seed {seed}: Spearman = {nsp:.4f}")

    # Average null disc
    null_all = pd.concat(null_binneds)
    null_avg = null_all.groupby("mean_depth").agg(
        mean_radial=("mean_radial", "mean"),
        mean_drift_mag=("mean_drift_mag", "mean"),
    ).reset_index()

    # 3. Shuffled perp (same graph, shuffled perp coordinates)
    print(f"  Computing shuffled-perp profiles ({N_NULL_SEEDS} seeds)...")
    shuf_binneds = []
    shuf_sps = []
    for seed in range(N_NULL_SEEDS):
        rng = np.random.default_rng(seed + 200)
        perm = rng.permutation(n)
        shuf_px = px[perm]
        shuf_py = py[perm]
        sb, ssp, _ = compute_radial_drift_profile(
            shuf_px, shuf_py, adj_arr, n, interior_mask=interior_mask)
        sb["model"] = f"shuffled_s{seed}"
        sb["substrate"] = name
        shuf_binneds.append(sb)
        shuf_sps.append(ssp)
        print(f"    Seed {seed}: Spearman = {ssp:.4f}")

    return {
        "real_binned": real_binned,
        "real_sp": real_sp,
        "null_binneds": null_binneds,
        "null_sps": null_sps,
        "null_avg": null_avg,
        "shuf_binneds": shuf_binneds,
        "shuf_sps": shuf_sps,
    }


# ── run ──────────────────────────────────────────────────────────────

results = {}
for sub in ["AB_N30", "Penrose_N24"]:
    results[sub] = analyse_substrate(sub)

# ── figures ──────────────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) THE KEY FIGURE: Real vs null disc vs shuffled
fig, axes = plt.subplots(1, 2, figsize=(14, 7))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    r = results[sub]

    # Real tiling
    rb = r["real_binned"]
    ax.plot(rb["mean_depth"], rb["mean_radial"], "o-",
            linewidth=3, markersize=8, color="crimson", label="Real quasicrystal", zorder=5)

    # Null discs (individual + average)
    for i, nb in enumerate(r["null_binneds"]):
        label = "Null disc (random uniform)" if i == 0 else None
        ax.plot(nb["mean_depth"], nb["mean_radial"], "-",
                linewidth=1, color="gray", alpha=0.4, label=label)

    # Shuffled perp
    for i, sb in enumerate(r["shuf_binneds"]):
        label = "Shuffled perp coords" if i == 0 else None
        ax.plot(sb["mean_depth"], sb["mean_radial"], "--",
                linewidth=1, color="steelblue", alpha=0.4, label=label)

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean radial drift (negative = inward)", fontsize=12)
    ax.set_title(f"{sub}\nReal Spearman = {r['real_sp']:.3f}, "
                 f"Null = {np.mean(r['null_sps']):.3f}, "
                 f"Shuffled = {np.mean(r['shuf_sps']):.3f}",
                 fontsize=12)
    ax.legend(fontsize=9, loc="lower right")

plt.suptitle("(1) THE NULL TEST: Is the inward drift just 'bounded shapes have middles'?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_real_vs_null_vs_shuffled.png"), dpi=150)
plt.close()

# (2) Zoomed comparison: real minus null
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    r = results[sub]
    rb = r["real_binned"]

    # Average null
    null_avg = r["null_avg"]

    # Merge on nearest depth
    merged_depths = rb["mean_depth"].values
    null_radials = np.interp(merged_depths, null_avg["mean_depth"].values,
                              null_avg["mean_radial"].values)
    residual = rb["mean_radial"].values - null_radials

    color = "steelblue" if sub == "AB_N30" else "coral"
    ax.plot(merged_depths, residual, "o-", linewidth=2.5, markersize=7, color=color)
    ax.axhline(0, color="gray", linewidth=1, linestyle=":")
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Real drift − Null drift (residual)", fontsize=12)
    ax.set_title(sub, fontsize=14)
    ax.text(0.05, 0.95, "Above 0 = real is LESS inward than null\nBelow 0 = real is MORE inward",
            transform=ax.transAxes, fontsize=9, va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

plt.suptitle("(2) What does the quasicrystal add beyond a plain disc?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_real_minus_null.png"), dpi=150)
plt.close()

# (3) Spearman comparison bar chart
fig, ax = plt.subplots(figsize=(10, 6))
subs = ["AB_N30", "Penrose_N24"]
x = np.arange(len(subs))
width = 0.25

real_sps = [results[s]["real_sp"] for s in subs]
null_sps = [np.mean(results[s]["null_sps"]) for s in subs]
shuf_sps = [np.mean(results[s]["shuf_sps"]) for s in subs]

ax.bar(x - width, real_sps, width, label="Real quasicrystal", color="crimson")
ax.bar(x, null_sps, width, label="Null disc", color="gray")
ax.bar(x + width, shuf_sps, width, label="Shuffled perp", color="steelblue")
ax.set_xticks(x)
ax.set_xticklabels(subs, fontsize=12)
ax.set_ylabel("Spearman(depth, radial drift)", fontsize=12)
ax.legend(fontsize=11)
ax.set_title("(3) Correlation strength: Real vs Null vs Shuffled", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_spearman_comparison.png"), dpi=150)
plt.close()

# (4) Drift magnitude comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    r = results[sub]
    rb = r["real_binned"]
    ax.plot(rb["mean_depth"], rb["mean_drift_mag"], "o-",
            linewidth=2.5, markersize=7, color="crimson", label="Real")
    for i, nb in enumerate(r["null_binneds"]):
        label = "Null disc" if i == 0 else None
        ax.plot(nb["mean_depth"], nb["mean_drift_mag"], "-",
                linewidth=1, color="gray", alpha=0.4, label=label)
    for i, sb in enumerate(r["shuf_binneds"]):
        label = "Shuffled" if i == 0 else None
        ax.plot(sb["mean_depth"], sb["mean_drift_mag"], "--",
                linewidth=1, color="steelblue", alpha=0.4, label=label)
    ax.set_xlabel("Hull depth", fontsize=12)
    ax.set_ylabel("Mean drift magnitude", fontsize=12)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=9)
plt.suptitle("(4) Drift magnitude: does the quasicrystal drift more or less?",
             fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_drift_magnitude_comparison.png"), dpi=150)
plt.close()


# ── report ───────────────────────────────────────────────────────────

print("\nGenerating report...")

report = ["# Null-disc control v0.1\n"]
report.append("## Core question")
report.append("Is the inward radial drift just 'bounded shapes have middles'?")
report.append("Or does the quasicrystal structure add something beyond that?\n")

report.append("## Setup")
report.append("Three models compared:")
report.append("1. **Real quasicrystal**: actual tiling with real perp-space coordinates")
report.append("2. **Null disc**: random uniform points in same hull shape, Delaunay-connected")
report.append(f"3. **Shuffled perp**: same tiling graph, perp coordinates randomly permuted")
report.append(f"- {N_NULL_SEEDS} seeds each for null and shuffled\n")

report.append("## Key results\n")
for sub in ["AB_N30", "Penrose_N24"]:
    r = results[sub]
    report.append(f"### {sub}\n")
    report.append(f"  - Real Spearman(depth, radial): {r['real_sp']:.4f}")
    report.append(f"  - Null disc Spearman (mean): {np.mean(r['null_sps']):.4f} "
                  f"(range: {min(r['null_sps']):.4f}–{max(r['null_sps']):.4f})")
    report.append(f"  - Shuffled Spearman (mean): {np.mean(r['shuf_sps']):.4f} "
                  f"(range: {min(r['shuf_sps']):.4f}–{max(r['shuf_sps']):.4f})")
    report.append("")

report.append("## Interpretation\n")
report.append("- If real ≈ null disc: drift is trivial boundary bookkeeping")
report.append("- If real ≠ null disc: quasicrystal structure adds genuine signal")
report.append("- Shuffled perp tests whether the structured arrangement of perp")
report.append("  coordinates matters beyond the graph topology\n")

report.append("## Figures\n")
report.append("1. fig_1 — THE KEY: Real vs null disc vs shuffled (overlaid)")
report.append("2. fig_2 — Residual: real minus null (what's left after subtracting boundary effect)")
report.append("3. fig_3 — Spearman comparison bar chart")
report.append("4. fig_4 — Drift magnitude comparison")

with open(os.path.join(OUT, "null_disc_v0_1_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll done! Results in {OUT}")
