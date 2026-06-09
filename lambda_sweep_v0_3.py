"""
Constraint-aware walk lambda sweep v0.3

Sweeps depth-resistance strength λ across many values for both AB and Penrose,
with multiple seeds per λ, to test whether Penrose naturally passes through
α≈0.553 in a stable way or whether it's just knob-tuning.

Walk model (cost-time / depth-resistance):
  - Neighbour choice is uniform
  - Outward/depth-losing steps have extra waiting-time cost:
    τ = exp(λ × max(0, depth_i - depth_j))
  - Physical MSD is measured against accumulated cost-time, not step count
"""

import os, time, warnings
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from collections import defaultdict

warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "lambda_sweep_v0_3_results")
os.makedirs(OUT, exist_ok=True)

# ── parameters ─────────────────────────────────────────────────────
LAMBDAS     = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20]
N_SEEDS     = 10
WALKERS     = 5_000
MAX_STEPS   = 1024
MEASURE_TIMES = [64, 128, 256, 512, 1024]
INTERIOR_FRAC = 0.75

# ── helpers ────────────────────────────────────────────────────────

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


def compute_physical_radius(verts):
    cx, cy = verts["x"].median(), verts["y"].median()
    return np.sqrt((verts["x"].values - cx)**2 + (verts["y"].values - cy)**2)


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


def cost_time_walks(adj_arr, depth, starts, max_steps, lam, rng):
    """
    Uniform neighbour choice, but outward steps cost extra time.
    τ_step = exp(λ * max(0, depth_i - depth_j))
    Returns: positions at each step, cumulative cost-time at each step.
    """
    n_w = len(starts)
    positions = np.zeros((n_w, max_steps + 1), dtype=np.int32)
    cum_time = np.zeros((n_w, max_steps + 1), dtype=np.float64)
    positions[:, 0] = starts

    for t in range(1, max_steps + 1):
        for w in range(n_w):
            cur = positions[w, t - 1]
            nbrs = adj_arr[cur]
            if len(nbrs) == 0:
                positions[w, t] = cur
                cum_time[w, t] = cum_time[w, t - 1] + 1.0
                continue
            nxt = rng.choice(nbrs)
            depth_loss = max(0.0, depth[cur] - depth[nxt])
            tau = np.exp(lam * depth_loss)
            positions[w, t] = nxt
            cum_time[w, t] = cum_time[w, t - 1] + tau

    return positions, cum_time


def fit_alpha(times_arr, msd_arr):
    mask = (msd_arr > 0) & (times_arr > 0)
    if np.sum(mask) < 2:
        return np.nan, np.nan
    lt = np.log(times_arr[mask])
    lm = np.log(msd_arr[mask])
    coeffs = np.polyfit(lt, lm, 1)
    alpha = coeffs[0]
    ss_res = np.sum((lm - np.polyval(coeffs, lt))**2)
    ss_tot = np.sum((lm - np.mean(lm))**2)
    r2 = 1 - ss_res / (ss_tot + 1e-15)
    return alpha, r2


# ── main sweep ─────────────────────────────────────────────────────

all_rows = []

for sub_name in ["AB_N30", "Penrose_N24"]:
    print(f"\n{'='*60}")
    print(f"  Loading {sub_name}")
    print(f"{'='*60}")

    verts, adj_arr, n = load_substrate(sub_name)
    verts_x = verts["x"].values.astype(np.float64)
    verts_y = verts["y"].values.astype(np.float64)
    depth = compute_depth(verts)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_idx = np.where(phys_r <= r_thresh)[0]

    print(f"  Interior nodes: {len(interior_idx)}")

    for lam in LAMBDAS:
        for seed in range(N_SEEDS):
            rng = np.random.default_rng(seed + lam * 1000)
            starts = rng.choice(interior_idx, size=WALKERS, replace=True).astype(np.int32)

            positions, cum_time = cost_time_walks(adj_arr, depth, starts, MAX_STEPS, lam, rng)

            sx = verts_x[starts]
            sy = verts_y[starts]

            # MSD at each measurement time (in steps), using cost-time as x-axis
            step_msds = []
            step_times_cost = []
            for mt in MEASURE_TIMES:
                cur = positions[:, mt]
                disp2 = (verts_x[cur] - sx)**2 + (verts_y[cur] - sy)**2
                msd = np.mean(disp2)
                mean_cost_t = np.mean(cum_time[:, mt])
                step_msds.append(msd)
                step_times_cost.append(mean_cost_t)

            # Fit alpha against cost-time
            alpha_cost, r2_cost = fit_alpha(np.array(step_times_cost), np.array(step_msds))
            # Also fit against raw steps for comparison
            alpha_steps, r2_steps = fit_alpha(np.array(MEASURE_TIMES, dtype=float), np.array(step_msds))

            # Near-return at final step
            final = positions[:, MAX_STEPS]
            phys_dist = np.sqrt((verts_x[final] - sx)**2 + (verts_y[final] - sy)**2)
            nr_mask = phys_dist <= 2.0
            nr_frac = np.mean(nr_mask)

            perp_x = verts["perp_x"].values
            perp_y = verts["perp_y"].values
            perp_mis = np.sqrt((perp_x[final] - perp_x[starts])**2 +
                               (perp_y[final] - perp_y[starts])**2)
            nr_perp = np.mean(perp_mis[nr_mask]) if np.sum(nr_mask) > 0 else np.nan

            row = {
                "substrate": sub_name,
                "lambda": lam,
                "seed": seed,
                "walkers": WALKERS,
                "alpha_vs_cost_time": alpha_cost,
                "alpha_vs_cost_time_r2": r2_cost,
                "alpha_vs_steps": alpha_steps,
                "alpha_vs_steps_r2": r2_steps,
                "mean_cost_time_at_1024": step_times_cost[-1],
                "msd_phys_at_1024": step_msds[-1],
                "near_return_frac_d2": nr_frac,
                "near_return_mean_perp_mismatch": nr_perp,
                "final_mean_perp_mismatch": np.mean(perp_mis),
            }
            all_rows.append(row)

        print(f"  λ={lam:>4d} done ({N_SEEDS} seeds)")

# ── save ───────────────────────────────────────────────────────────

df = pd.DataFrame(all_rows)
df.to_csv(os.path.join(OUT, "lambda_sweep_per_seed.csv"), index=False)

summary = df.groupby(["substrate", "lambda"]).agg(
    alpha_cost_mean=("alpha_vs_cost_time", "mean"),
    alpha_cost_std=("alpha_vs_cost_time", "std"),
    alpha_cost_r2_mean=("alpha_vs_cost_time_r2", "mean"),
    alpha_steps_mean=("alpha_vs_steps", "mean"),
    alpha_steps_std=("alpha_vs_steps", "std"),
    msd_phys_mean=("msd_phys_at_1024", "mean"),
    mean_cost_time=("mean_cost_time_at_1024", "mean"),
    nr_frac_mean=("near_return_frac_d2", "mean"),
    nr_perp_mean=("near_return_mean_perp_mismatch", "mean"),
    final_perp_mean=("final_mean_perp_mismatch", "mean"),
).reset_index()
summary.to_csv(os.path.join(OUT, "lambda_sweep_summary.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── figures ────────────────────────────────────────────────────────
print("Generating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (a) Alpha vs lambda — the key plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, x_col, title in zip(axes,
    ["alpha_cost_mean", "alpha_steps_mean"],
    ["α vs cost-time", "α vs raw steps"]):
    for sub, color, marker in [("AB_N30", "steelblue", "o"), ("Penrose_N24", "coral", "s")]:
        d = summary[summary["substrate"] == sub]
        std_col = x_col.replace("mean", "std")
        ax.errorbar(d["lambda"], d[x_col], yerr=d[std_col],
                     label=sub, color=color, marker=marker, capsize=3, linewidth=1.5)
    ax.axhline(0.553, color="gray", linestyle="--", linewidth=1, label="α=0.553 target")
    ax.axhline(1.0, color="lightgray", linestyle=":", linewidth=0.8, label="normal diffusion")
    ax.set_xlabel("λ (resistance strength)")
    ax.set_ylabel("Physical diffusion exponent α")
    ax.set_title(title)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.2)

plt.suptitle("(a) Lambda sweep: diffusion exponent vs resistance strength", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_a_alpha_vs_lambda.png"), dpi=150)
plt.close()

# (b) AB vs Penrose gap at each lambda
fig, ax = plt.subplots(figsize=(10, 5))
for x_col, label, color in [("alpha_cost_mean", "vs cost-time", "steelblue"),
                              ("alpha_steps_mean", "vs steps", "coral")]:
    ab = summary[summary["substrate"] == "AB_N30"].set_index("lambda")[x_col]
    pen = summary[summary["substrate"] == "Penrose_N24"].set_index("lambda")[x_col]
    gap = pen - ab
    ax.plot(gap.index, gap.values, marker="o", label=f"Penrose − AB ({label})",
            color=color, linewidth=1.5)
ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)
ax.set_xlabel("λ (resistance strength)")
ax.set_ylabel("Penrose α − AB α")
ax.set_title("(b) Substrate gap: does Penrose consistently sit higher than AB?")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_b_substrate_gap.png"), dpi=150)
plt.close()

# (c) Seed-level scatter at interesting lambdas
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
interesting_lambdas = [8, 10, 12]
for ax, lam in zip(axes, interesting_lambdas):
    for sub, color in [("AB_N30", "steelblue"), ("Penrose_N24", "coral")]:
        d = df[(df["substrate"] == sub) & (df["lambda"] == lam)]
        ax.scatter(d["seed"], d["alpha_vs_cost_time"], color=color, alpha=0.7,
                   label=sub, s=50)
    ax.axhline(0.553, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("Seed")
    ax.set_title(f"λ = {lam}")
    ax.legend(fontsize=8)
axes[0].set_ylabel("α vs cost-time")
plt.suptitle("(c) Per-seed α at key lambda values", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_c_seed_scatter.png"), dpi=150)
plt.close()

# (d) Near-return perp mismatch vs lambda
fig, ax = plt.subplots(figsize=(10, 5))
for sub, color, marker in [("AB_N30", "steelblue", "o"), ("Penrose_N24", "coral", "s")]:
    d = summary[summary["substrate"] == sub]
    ax.plot(d["lambda"], d["nr_perp_mean"], marker=marker, color=color,
            label=sub, linewidth=1.5)
ax.set_xlabel("λ (resistance strength)")
ax.set_ylabel("Near-return mean perp mismatch")
ax.set_title("(d) Address residue on near-return paths vs resistance strength")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_d_nr_perp_vs_lambda.png"), dpi=150)
plt.close()

print("Figures saved.")

# ── report ─────────────────────────────────────────────────────────
print("Writing report...")

lines = []
lines.append("# Lambda sweep v0.3: depth-resistance walk\n")
lines.append("## Setup")
lines.append(f"- Lambda values: {LAMBDAS}")
lines.append(f"- Seeds per lambda: {N_SEEDS}")
lines.append(f"- Walkers per seed: {WALKERS}")
lines.append(f"- Max steps: {MAX_STEPS}")
lines.append(f"- Measurement times: {MEASURE_TIMES}")
lines.append(f"- Interior fraction: {INTERIOR_FRAC}")
lines.append(f"- Walk model: uniform neighbour choice, cost tau = exp(lambda * max(0, depth_i - depth_j))\n")

lines.append("## Summary (mean across seeds)\n")
lines.append(summary.to_markdown(index=False))

lines.append("\n## Key question: does Penrose naturally pass through alpha~0.553?\n")

# Find where each substrate crosses 0.553
for sub in ["AB_N30", "Penrose_N24"]:
    d = summary[summary["substrate"] == sub]
    alphas = d["alpha_cost_mean"].values
    lams = d["lambda"].values
    above = alphas > 0.553
    crossings = np.where(np.diff(above.astype(int)) != 0)[0]
    if len(crossings) > 0:
        idx = crossings[0]
        lam_lo, lam_hi = lams[idx], lams[idx + 1]
        a_lo, a_hi = alphas[idx], alphas[idx + 1]
        lam_cross = lam_lo + (0.553 - a_lo) / (a_hi - a_lo + 1e-12) * (lam_hi - lam_lo)
        lines.append(f"**{sub}** crosses α=0.553 (vs cost-time) near λ≈{lam_cross:.1f} "
                      f"(between λ={lam_lo} [α={a_lo:.3f}] and λ={lam_hi} [α={a_hi:.3f}])")
    else:
        if len(alphas) > 0 and alphas[-1] > 0.553:
            lines.append(f"**{sub}** never drops below α=0.553 in the tested range.")
        else:
            lines.append(f"**{sub}** is below α=0.553 for all tested lambdas (or no clear crossing).")

lines.append("\n## Interpretation rules\n")
lines.append("- This does NOT prove Berry curvature")
lines.append("- This does NOT prove the tiling 'has' alpha=0.553")
lines.append("- It tests whether a depth-resistance walk produces a natural crossing/plateau")
lines.append("- The key evidence would be: Penrose crosses 0.553 with a flatter slope (plateau)")
lines.append("  while AB crosses at a different lambda or with a steeper slope")
lines.append("- If both substrates produce identical curves, the effect is generic to the walk model, not the substrate\n")

lines.append("## Figures\n")
lines.append("- fig_a_alpha_vs_lambda.png -- alpha vs lambda for both substrates (key plot)")
lines.append("- fig_b_substrate_gap.png -- Penrose minus AB gap across lambda")
lines.append("- fig_c_seed_scatter.png -- per-seed alpha at key lambda values")
lines.append("- fig_d_nr_perp_vs_lambda.png -- near-return address mismatch vs lambda")

with open(os.path.join(OUT, "lambda_sweep_v0_3_report.md"), "w") as f:
    f.write("\n".join(lines))

print("Report written.")
print("\nDone.")
