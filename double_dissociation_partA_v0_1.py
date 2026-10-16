"""
Double-Dissociation Part A: Seed-level variance on shuffle vs null

Reports per-seed Spearman(depth, radial_drift) for all conditions,
checks whether AB-shuffle and Penrose-shuffle distributions separate,
and confirms null seeds cluster near zero.

Uses the same data pipeline as null_disc_v0_1.py.
"""

import os, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull, Delaunay
from scipy.stats import spearmanr, mannwhitneyu
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "double_dissociation_partA_results")
os.makedirs(OUT, exist_ok=True)

INTERIOR_FRAC = 0.75
N_NULL_SEEDS  = 5
N_SHUF_SEEDS  = 10  # more seeds for tighter spread estimate


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


def compute_spearman(px, py, adj_arr, n, interior_mask=None):
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
    for i in range(n):
        nbrs = adj_arr[i]
        if len(nbrs) == 0:
            continue
        drift_x[i] = (px[nbrs] - px[i]).mean()
        drift_y[i] = (py[nbrs] - py[i]).mean()

    pos_ux = np.where(pos_mag > 1e-12, pos_x / pos_mag, 0)
    pos_uy = np.where(pos_mag > 1e-12, pos_y / pos_mag, 0)
    radial_drift = drift_x * pos_ux + drift_y * pos_uy

    if interior_mask is not None:
        idx = np.where(interior_mask)[0]
    else:
        idx = np.arange(n)

    sp, _ = spearmanr(depth[idx], radial_drift[idx])
    return sp


def generate_null_disc(px, py, n_points, seed):
    rng = np.random.default_rng(seed)
    pts = np.column_stack([px, py])
    hull = ConvexHull(pts)
    hull_pts = pts[hull.vertices]
    xmin, xmax = hull_pts[:, 0].min(), hull_pts[:, 0].max()
    ymin, ymax = hull_pts[:, 1].min(), hull_pts[:, 1].max()
    delaunay = Delaunay(hull_pts)
    collected = []
    while len(collected) < n_points:
        batch = rng.uniform([xmin, ymin], [xmax, ymax], size=(n_points * 2, 2))
        inside = delaunay.find_simplex(batch) >= 0
        collected.extend(batch[inside].tolist())
    collected = np.array(collected[:n_points])
    tri = Delaunay(collected)
    adj = defaultdict(set)
    for simplex in tri.simplices:
        for i in range(3):
            for j in range(i + 1, 3):
                adj[simplex[i]].add(simplex[j])
                adj[simplex[j]].add(simplex[i])
    adj_arr = [np.array(list(adj[i]), dtype=np.int32) for i in range(n_points)]
    return collected[:, 0], collected[:, 1], adj_arr, n_points


# ── Main ──────────────────────────────────────────────────────

results = []

for name in ["AB_N30", "Penrose_N24"]:
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    verts, adj_arr, n = load_substrate(name)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)

    phys_r = np.sqrt((verts["x"].values - verts["x"].median())**2 +
                      (verts["y"].values - verts["y"].median())**2)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh
    n_interior = int(interior_mask.sum())

    # Real (native) baseline
    real_sp = compute_spearman(px, py, adj_arr, n, interior_mask=interior_mask)
    results.append({"substrate": name, "condition": "native", "seed": "—",
                    "spearman": real_sp})
    print(f"  Native: Spearman = {real_sp:.4f}")

    # Null disc seeds
    print(f"  Null disc ({N_NULL_SEEDS} seeds)...")
    for seed in range(N_NULL_SEEDS):
        null_px, null_py, null_adj, null_n = generate_null_disc(
            px, py, n_interior, seed=seed + 100)
        nsp = compute_spearman(null_px, null_py, null_adj, null_n)
        results.append({"substrate": name, "condition": "null_disc",
                        "seed": seed, "spearman": nsp})
        print(f"    Seed {seed}: {nsp:.4f}")

    # Shuffled-perp seeds (more seeds for tighter estimate)
    print(f"  Shuffled perp ({N_SHUF_SEEDS} seeds)...")
    for seed in range(N_SHUF_SEEDS):
        rng = np.random.default_rng(seed + 200)
        perm = rng.permutation(n)
        shuf_px = px[perm]
        shuf_py = py[perm]
        ssp = compute_spearman(shuf_px, shuf_py, adj_arr, n,
                               interior_mask=interior_mask)
        results.append({"substrate": name, "condition": "shuffled_perp",
                        "seed": seed, "spearman": ssp})
        print(f"    Seed {seed}: {ssp:.4f}")


# ── Analysis ──────────────────────────────────────────────────

df = pd.DataFrame(results)
df.to_csv(os.path.join(OUT, "per_seed_table.csv"), index=False)

print("\n" + "="*60)
print("  SEPARATION ANALYSIS")
print("="*60)

report_lines = ["# Double-Dissociation Part A: Seed-Level Variance\n"]

for cond in ["null_disc", "shuffled_perp"]:
    ab_vals = df[(df["substrate"] == "AB_N30") & (df["condition"] == cond)]["spearman"].values
    pen_vals = df[(df["substrate"] == "Penrose_N24") & (df["condition"] == cond)]["spearman"].values

    ab_native = df[(df["substrate"] == "AB_N30") & (df["condition"] == "native")]["spearman"].values[0]
    pen_native = df[(df["substrate"] == "Penrose_N24") & (df["condition"] == "native")]["spearman"].values[0]

    report_lines.append(f"\n## {cond.replace('_', ' ').title()}\n")
    report_lines.append(f"| Substrate | Native | Mean | Std | Min | Max | Retention |")
    report_lines.append(f"|-----------|--------|------|-----|-----|-----|-----------|")

    ab_retention = ab_vals.mean() / ab_native * 100 if ab_native != 0 else 0
    pen_retention = pen_vals.mean() / pen_native * 100 if pen_native != 0 else 0

    report_lines.append(f"| AB | {ab_native:.4f} | {ab_vals.mean():.4f} | {ab_vals.std():.4f} | {ab_vals.min():.4f} | {ab_vals.max():.4f} | {ab_retention:.1f}% |")
    report_lines.append(f"| Penrose | {pen_native:.4f} | {pen_vals.mean():.4f} | {pen_vals.std():.4f} | {pen_vals.min():.4f} | {pen_vals.max():.4f} | {pen_retention:.1f}% |")

    print(f"\n  {cond}:")
    print(f"    AB:      {ab_vals.mean():.4f} ± {ab_vals.std():.4f}  [{ab_vals.min():.4f} – {ab_vals.max():.4f}]  retention {ab_retention:.1f}%")
    print(f"    Penrose: {pen_vals.mean():.4f} ± {pen_vals.std():.4f}  [{pen_vals.min():.4f} – {pen_vals.max():.4f}]  retention {pen_retention:.1f}%")

    # Separation test
    if len(ab_vals) >= 3 and len(pen_vals) >= 3:
        U, p = mannwhitneyu(ab_vals, pen_vals, alternative="two-sided")
        ranges_overlap = ab_vals.max() >= pen_vals.min() and pen_vals.max() >= ab_vals.min()

        sep_str = f"Mann–Whitney U = {U:.0f}, p = {p:.4f}"
        overlap_str = "OVERLAP" if ranges_overlap else "SEPARATED"
        print(f"    Separation: {sep_str}, ranges {overlap_str}")

        report_lines.append(f"\n**Separation:** {sep_str}. Ranges: **{overlap_str}**.")

        if cond == "shuffled_perp":
            report_lines.append(f"\nAB retains {ab_retention:.1f}% of native signal under shuffle.")
            report_lines.append(f"Penrose retains {pen_retention:.1f}% of native signal under shuffle.")
            delta = pen_retention - ab_retention
            report_lines.append(f"Asymmetry: Penrose retains {delta:.1f} percentage points MORE than AB.")
            if not ranges_overlap:
                report_lines.append(f"\n**The AB-vs-Penrose shuffle asymmetry SURVIVES seed variation.** Ranges do not overlap.")
            else:
                report_lines.append(f"\n**WARNING: AB-shuffle and Penrose-shuffle ranges OVERLAP.** The asymmetry may not be robust.")

# Kill conditions
report_lines.append("\n## Kill-condition checks\n")

ab_null = df[(df["substrate"] == "AB_N30") & (df["condition"] == "null_disc")]["spearman"].values
pen_null = df[(df["substrate"] == "Penrose_N24") & (df["condition"] == "null_disc")]["spearman"].values
ab_shuf = df[(df["substrate"] == "AB_N30") & (df["condition"] == "shuffled_perp")]["spearman"].values
pen_shuf = df[(df["substrate"] == "Penrose_N24") & (df["condition"] == "shuffled_perp")]["spearman"].values

null_tight = ab_null.std() < 0.02 and pen_null.std() < 0.02
report_lines.append(f"1. **Null seeds cluster tightly near 0?** AB null std = {ab_null.std():.4f}, Penrose null std = {pen_null.std():.4f}. {'YES — tight cluster.' if null_tight else 'NO — noisy nulls, weakens flat-null claim.'}")

ranges_overlap = ab_shuf.max() >= pen_shuf.min() and pen_shuf.max() >= ab_shuf.min()
report_lines.append(f"2. **AB-shuffle and Penrose-shuffle separate?** AB range [{ab_shuf.min():.4f}–{ab_shuf.max():.4f}], Penrose range [{pen_shuf.min():.4f}–{pen_shuf.max():.4f}]. {'NO — ranges overlap. Asymmetry not robust.' if ranges_overlap else 'YES — clean separation.'}")

report = "\n".join(report_lines)
with open(os.path.join(OUT, "partA_report.md"), "w") as f:
    f.write(report)

print(f"\n\nResults saved to {OUT}/")
print("Done!")
