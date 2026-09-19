"""
Controlled linger walks v0.1

The confound: in natural random walks, longer lingerers also start deeper.
This experiment forces the linger duration while controlling start depth,
isolating the causal effect of time-at-depth on address recovery.

Walk script (5 phases):
1. START from medium-depth band (0.4-0.6) — controls starting position
2. DISTURB: free random walk for 100 steps — gets the address scrambled
3. DESCEND: biased walk toward deeper neighbours for up to 100 steps
4. LINGER: hold near depth floor for exactly N steps (N varies)
5. ASCEND: biased walk toward shallower neighbours back toward start depth

The ONLY variable is N (linger duration). Everything else is controlled.
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
OUT  = os.path.join(BASE, "controlled_linger_v0_1_results")
os.makedirs(OUT, exist_ok=True)

N_SEEDS          = 10
WALKERS_PER_SEED = 5_000
INTERIOR_FRAC    = 0.75

# Walk phases
DISTURB_STEPS  = 100
DESCEND_BUDGET = 100
ASCEND_BUDGET  = 200
LINGER_DURATIONS = [0, 5, 10, 20, 40, 80, 160]

# Start depth band
START_DEPTH_LO = 0.35
START_DEPTH_HI = 0.65


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

    max_deg = max(len(a) for a in adj_arr)
    adj_padded = np.zeros((n, max_deg), dtype=np.int32)
    deg = np.zeros(n, dtype=np.int32)
    for i, a in enumerate(adj_arr):
        d = len(a)
        deg[i] = d
        if d > 0:
            adj_padded[i, :d] = a

    return verts, adj_padded, deg, n


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


def free_walk_step(pos, adj_padded, deg, rng):
    """One step of unbiased random walk for all walkers (vectorised)."""
    d = deg[pos]
    r = (rng.random(len(pos)) * d).astype(np.int32)
    r = np.minimum(r, d - 1)
    return adj_padded[pos, r]


def biased_walk_step(pos, adj_padded, deg, depth, rng, toward_deep=True):
    """One step biased toward deeper (or shallower) neighbours.
    Pick the neighbour with the best depth; with 30% chance, pick randomly instead
    (so the walker doesn't get perfectly stuck)."""
    n_w = len(pos)
    new_pos = pos.copy()
    random_mask = rng.random(n_w) < 0.3

    # Random step for 30%
    rand_idx = np.where(random_mask)[0]
    if len(rand_idx) > 0:
        d = deg[pos[rand_idx]]
        r = (rng.random(len(rand_idx)) * d).astype(np.int32)
        r = np.minimum(r, d - 1)
        new_pos[rand_idx] = adj_padded[pos[rand_idx], r]

    # Biased step for 70%
    biased_idx = np.where(~random_mask)[0]
    for w in biased_idx:
        p = pos[w]
        d = deg[p]
        if d == 0:
            continue
        nbrs = adj_padded[p, :d]
        nbr_depths = depth[nbrs]
        if toward_deep:
            best = nbrs[np.argmax(nbr_depths)]
        else:
            best = nbrs[np.argmin(nbr_depths)]
        new_pos[w] = best

    return new_pos


def run_controlled_walks(name, verts, adj_padded, deg, depth, px, py, vx, vy,
                         start_nodes, linger_n, seed):
    """Run controlled walks with a specific linger duration."""
    rng = np.random.default_rng(seed * 1000 + linger_n)
    n_w = len(start_nodes)
    pos = start_nodes.copy()

    start_px = px[start_nodes]
    start_py = py[start_nodes]
    start_vx = vx[start_nodes]
    start_vy = vy[start_nodes]
    start_depths = depth[start_nodes]

    # Track trajectory for address residue at each phase boundary
    phase_residues = {}

    # Phase 1: DISTURB — free walk for DISTURB_STEPS
    for _ in range(DISTURB_STEPS):
        pos = free_walk_step(pos, adj_padded, deg, rng)
    disturb_residue = np.sqrt((px[pos] - start_px)**2 + (py[pos] - start_py)**2)
    disturb_depth = depth[pos]
    phase_residues["after_disturb"] = disturb_residue.copy()

    # Phase 2: DESCEND — biased walk toward depth for up to DESCEND_BUDGET steps
    for _ in range(DESCEND_BUDGET):
        pos = biased_walk_step(pos, adj_padded, deg, depth, rng, toward_deep=True)
    descend_residue = np.sqrt((px[pos] - start_px)**2 + (py[pos] - start_py)**2)
    descend_depth = depth[pos]
    phase_residues["after_descend"] = descend_residue.copy()

    # Phase 3: LINGER — stay near depth floor for exactly linger_n steps
    # Biased toward deep (to stay put), but with some randomness
    linger_start_residue = np.sqrt((px[pos] - start_px)**2 + (py[pos] - start_py)**2)
    phase_residues["linger_start"] = linger_start_residue.copy()

    # Track residue every 5 steps during linger for trajectory
    linger_trajectory = []
    for step in range(linger_n):
        pos = biased_walk_step(pos, adj_padded, deg, depth, rng, toward_deep=True)
        if step % 5 == 0 or step == linger_n - 1:
            res = np.sqrt((px[pos] - start_px)**2 + (py[pos] - start_py)**2)
            linger_trajectory.append((step + 1, res.mean(), np.median(res)))

    linger_end_residue = np.sqrt((px[pos] - start_px)**2 + (py[pos] - start_py)**2)
    linger_end_depth = depth[pos]
    phase_residues["linger_end"] = linger_end_residue.copy()

    # Phase 4: ASCEND — biased walk toward shallower (back toward start depth)
    for _ in range(ASCEND_BUDGET):
        pos = biased_walk_step(pos, adj_padded, deg, depth, rng, toward_deep=False)
    ascend_residue = np.sqrt((px[pos] - start_px)**2 + (py[pos] - start_py)**2)
    ascend_depth = depth[pos]
    phase_residues["after_ascend"] = ascend_residue.copy()

    # Physical return distance
    phys_dist = np.sqrt((vx[pos] - start_vx)**2 + (vy[pos] - start_vy)**2)

    return {
        "substrate": name,
        "seed": seed,
        "linger_n": linger_n,
        "n_walkers": n_w,
        "mean_start_depth": float(start_depths.mean()),
        "mean_disturb_depth": float(disturb_depth.mean()),
        "mean_descend_depth": float(descend_depth.mean()),
        "mean_linger_end_depth": float(linger_end_depth.mean()),
        "mean_ascend_depth": float(ascend_depth.mean()),
        "mean_residue_after_disturb": float(disturb_residue.mean()),
        "mean_residue_after_descend": float(descend_residue.mean()),
        "mean_residue_linger_start": float(linger_start_residue.mean()),
        "mean_residue_linger_end": float(linger_end_residue.mean()),
        "mean_residue_after_ascend": float(ascend_residue.mean()),
        "median_residue_after_ascend": float(np.median(ascend_residue)),
        "std_residue_after_ascend": float(ascend_residue.std()),
        "mean_phys_dist_final": float(phys_dist.mean()),
        "frac_near_return_2": float((phys_dist <= 2.0).mean()),
        "frac_near_return_3": float((phys_dist <= 3.0).mean()),
    }, linger_trajectory, phase_residues


def analyse_substrate(name):
    print(f"\n{'='*60}")
    print(f"  Loading {name}")
    print(f"{'='*60}")

    verts, adj_padded, deg, n = load_substrate(name)
    vx = verts["x"].values.astype(np.float64)
    vy = verts["y"].values.astype(np.float64)
    px = verts["perp_x"].values.astype(np.float64)
    py = verts["perp_y"].values.astype(np.float64)
    d = compute_depth(verts)
    phys_r = compute_physical_radius(verts)
    r_thresh = np.percentile(phys_r, INTERIOR_FRAC * 100)
    interior_mask = phys_r <= r_thresh

    # Select start nodes in the medium-depth band
    depth_mask = (d >= START_DEPTH_LO) & (d <= START_DEPTH_HI)
    eligible = np.where(interior_mask & depth_mask)[0]
    print(f"  Interior nodes: {int(interior_mask.sum())}")
    print(f"  Eligible start nodes (depth {START_DEPTH_LO}-{START_DEPTH_HI}): {len(eligible)}")

    summary_rows = []
    linger_traj_rows = []

    for seed in range(N_SEEDS):
        rng_start = np.random.default_rng(seed)
        start_nodes = rng_start.choice(eligible, size=WALKERS_PER_SEED, replace=True).astype(np.int32)

        for linger_n in LINGER_DURATIONS:
            result, traj, phases = run_controlled_walks(
                name, verts, adj_padded, deg, d, px, py, vx, vy,
                start_nodes, linger_n, seed
            )
            summary_rows.append(result)

            for step, mean_r, med_r in traj:
                linger_traj_rows.append({
                    "substrate": name, "seed": seed, "linger_n": linger_n,
                    "linger_step": step, "mean_residue": mean_r, "median_residue": med_r
                })

        print(f"  Seed {seed}/{N_SEEDS-1} done")

    return summary_rows, linger_traj_rows


# ── run ──────────────────────────────────────────────────────────────

all_summary = []
all_traj = []

for sub in ["AB_N30", "Penrose_N24"]:
    s, t = analyse_substrate(sub)
    all_summary.extend(s)
    all_traj.extend(t)

summary_df = pd.DataFrame(all_summary)
summary_df.to_csv(os.path.join(OUT, "controlled_linger_summary.csv"), index=False)

traj_df = pd.DataFrame(all_traj)
traj_df.to_csv(os.path.join(OUT, "controlled_linger_trajectories.csv"), index=False)

# Aggregate across seeds
agg = summary_df.groupby(["substrate", "linger_n"]).mean(numeric_only=True).reset_index()
agg.to_csv(os.path.join(OUT, "controlled_linger_agg.csv"), index=False)

print(f"\nCSVs saved to {OUT}")

# ── key analysis ─────────────────────────────────────────────────────

print("\n--- Controlled linger results ---")
for sub in ["AB_N30", "Penrose_N24"]:
    print(f"\n{sub}:")
    d = agg[agg["substrate"] == sub].sort_values("linger_n")
    for _, row in d.iterrows():
        print(f"  Linger {int(row['linger_n']):>3d} steps: "
              f"residue = {row['mean_residue_after_ascend']:.4f} "
              f"(at linger start: {row['mean_residue_linger_start']:.4f}, "
              f"at linger end: {row['mean_residue_linger_end']:.4f})")

    # Recovery fraction: how much of the post-disturb residue is recovered?
    baseline = d[d["linger_n"] == 0]["mean_residue_after_ascend"].values[0]
    best = d["mean_residue_after_ascend"].min()
    print(f"  No-linger baseline: {baseline:.4f}")
    print(f"  Best recovery: {best:.4f}")
    print(f"  Improvement: {baseline - best:.4f}")


# ── figures ──────────────────────────────────────────────────────────

print("\nGenerating figures...")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (1) THE KEY FIGURE: Final residue vs linger duration (controlled!)
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub].sort_values("linger_n")
    ax.plot(d["linger_n"], d["mean_residue_after_ascend"], "o-",
            linewidth=2.5, markersize=10, color="steelblue" if sub == "AB_N30" else "coral",
            label="Final residue (after ascent)")
    ax.fill_between(d["linger_n"],
                    d["mean_residue_after_ascend"] - d["std_residue_after_ascend"],
                    d["mean_residue_after_ascend"] + d["std_residue_after_ascend"],
                    alpha=0.15)
    ax.plot(d["linger_n"], d["mean_residue_linger_start"], "s--",
            linewidth=1.5, markersize=7, color="gray", alpha=0.7,
            label="Residue at linger start")
    ax.set_xlabel("Forced linger duration (steps at depth)", fontsize=12)
    ax.set_ylabel("Mean address residue", fontsize=12)
    ax.set_title(sub, fontsize=14)
    ax.legend(fontsize=10)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xticks(LINGER_DURATIONS)
    ax.set_xticklabels([str(x) for x in LINGER_DURATIONS])
plt.suptitle("(1) CONTROLLED EXPERIMENT: Does forced linger duration cause address recovery?",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_controlled_linger_vs_residue.png"), dpi=150)
plt.close()

# (2) Phase-by-phase residue: how does the address change through each phase?
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
phases = ["mean_residue_after_disturb", "mean_residue_after_descend",
          "mean_residue_linger_start", "mean_residue_linger_end",
          "mean_residue_after_ascend"]
phase_labels = ["After disturb", "After descend", "Linger start", "Linger end", "After ascent"]

for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub].sort_values("linger_n")
    for _, row in d.iterrows():
        ln = int(row["linger_n"])
        vals = [row[p] for p in phases]
        alpha = 0.3 + 0.7 * (ln / max(LINGER_DURATIONS))
        ax.plot(range(len(phases)), vals, "o-", alpha=alpha, linewidth=1.5,
                label=f"Linger={ln}", markersize=6)
    ax.set_xticks(range(len(phases)))
    ax.set_xticklabels(phase_labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Mean address residue", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=8, ncol=2)
plt.suptitle("(2) Address residue through each walk phase", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_phase_by_phase.png"), dpi=150)
plt.close()

# (3) Depth profile through phases
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
depth_phases = ["mean_start_depth", "mean_disturb_depth", "mean_descend_depth",
                "mean_linger_end_depth", "mean_ascend_depth"]
depth_labels = ["Start", "After disturb", "After descend", "Linger end", "After ascent"]

for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub].sort_values("linger_n")
    for _, row in d.iterrows():
        ln = int(row["linger_n"])
        vals = [row[p] for p in depth_phases]
        alpha = 0.3 + 0.7 * (ln / max(LINGER_DURATIONS))
        ax.plot(range(len(depth_phases)), vals, "o-", alpha=alpha, linewidth=1.5,
                label=f"Linger={ln}", markersize=6)
    ax.set_xticks(range(len(depth_phases)))
    ax.set_xticklabels(depth_labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Mean hull depth", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=8, ncol=2)
plt.suptitle("(3) Hull depth through each walk phase (sanity check)", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_3_depth_through_phases.png"), dpi=150)
plt.close()

# (4) Substrate comparison: controlled S-curve overlaid
fig, ax = plt.subplots(figsize=(10, 6))
for sub, color, marker in [("AB_N30", "steelblue", "o"), ("Penrose_N24", "coral", "s")]:
    d = agg[agg["substrate"] == sub].sort_values("linger_n")
    ax.plot(d["linger_n"], d["mean_residue_after_ascend"], f"{marker}-",
            linewidth=2.5, markersize=10, color=color, label=sub)
ax.set_xlabel("Forced linger duration (steps at depth)", fontsize=12)
ax.set_ylabel("Mean final address residue", fontsize=12)
ax.set_title("Controlled S-curve: AB vs Penrose", fontsize=14)
ax.legend(fontsize=11)
ax.set_xscale("symlog", linthresh=1)
ax.set_xticks(LINGER_DURATIONS)
ax.set_xticklabels([str(x) for x in LINGER_DURATIONS])
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_4_substrate_comparison.png"), dpi=150)
plt.close()

# (5) Linger-phase trajectory: residue during the linger itself
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
traj_agg = traj_df.groupby(["substrate", "linger_n", "linger_step"]).mean(numeric_only=True).reset_index()

for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    for ln in LINGER_DURATIONS:
        if ln == 0:
            continue
        d = traj_agg[(traj_agg["substrate"] == sub) & (traj_agg["linger_n"] == ln)]
        if len(d) == 0:
            continue
        d = d.sort_values("linger_step")
        ax.plot(d["linger_step"], d["mean_residue"], "o-", linewidth=1.5,
                markersize=4, label=f"Linger={ln}")
    ax.set_xlabel("Step within linger phase", fontsize=11)
    ax.set_ylabel("Mean address residue", fontsize=11)
    ax.set_title(sub, fontsize=13)
    ax.legend(fontsize=9)
plt.suptitle("(5) Address residue during the linger phase itself", fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_5_linger_phase_trajectory.png"), dpi=150)
plt.close()

# (6) Normalised improvement: fraction of disturbance recovered
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, sub in zip(axes, ["AB_N30", "Penrose_N24"]):
    d = agg[agg["substrate"] == sub].sort_values("linger_n")
    disturb_res = d["mean_residue_after_disturb"].values
    final_res = d["mean_residue_after_ascend"].values
    # Recovery fraction: how much of the disturbance was undone?
    recovery_frac = 1.0 - (final_res / disturb_res)
    ax.plot(d["linger_n"].values, recovery_frac, "o-", linewidth=2.5, markersize=10,
            color="steelblue" if sub == "AB_N30" else "coral")
    ax.set_xlabel("Forced linger duration (steps at depth)", fontsize=12)
    ax.set_ylabel("Fraction of disturbance recovered", fontsize=12)
    ax.set_title(sub, fontsize=13)
    ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xticks(LINGER_DURATIONS)
    ax.set_xticklabels([str(x) for x in LINGER_DURATIONS])
plt.suptitle("(6) What fraction of address disturbance is recovered by lingering?",
             fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_6_recovery_fraction.png"), dpi=150)
plt.close()


# ── report ───────────────────────────────────────────────────────────

print("\nGenerating report...")

report = ["# Controlled linger walks v0.1\n"]
report.append("## Core question")
report.append("Does forced time at depth CAUSE address recovery, or is the correlation")
report.append("from natural walks confounded by starting depth?\n")

report.append("## Setup")
report.append(f"- Seeds: {N_SEEDS}, Walkers/seed: {WALKERS_PER_SEED}")
report.append(f"- Start depth band: {START_DEPTH_LO}–{START_DEPTH_HI}")
report.append(f"- Disturb phase: {DISTURB_STEPS} free random walk steps")
report.append(f"- Descend phase: {DESCEND_BUDGET} biased-toward-deep steps")
report.append(f"- Linger durations tested: {LINGER_DURATIONS}")
report.append(f"- Ascend phase: {ASCEND_BUDGET} biased-toward-shallow steps")
report.append(f"- Bias: 70% pick deepest/shallowest neighbour, 30% random\n")

report.append("## Summary (mean across seeds)\n")
report.append(agg.to_markdown(index=False))
report.append("")

report.append("## Key results\n")
for sub in ["AB_N30", "Penrose_N24"]:
    d = agg[agg["substrate"] == sub].sort_values("linger_n")
    report.append(f"### {sub}\n")
    for _, row in d.iterrows():
        ln = int(row["linger_n"])
        report.append(f"  - Linger {ln:>3d}: final residue = {row['mean_residue_after_ascend']:.4f} "
                      f"(linger start: {row['mean_residue_linger_start']:.4f}, "
                      f"linger end: {row['mean_residue_linger_end']:.4f})")
    baseline = d[d["linger_n"] == 0]["mean_residue_after_ascend"].values[0]
    best = d["mean_residue_after_ascend"].min()
    best_n = int(d.loc[d["mean_residue_after_ascend"].idxmin(), "linger_n"])
    report.append(f"\n  No-linger baseline: {baseline:.4f}")
    report.append(f"  Best recovery (linger={best_n}): {best:.4f}")
    report.append(f"  Improvement: {baseline - best:.4f}\n")

report.append("## Interpretation rules\n")
report.append("- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.")
report.append("- This is a CONTROLLED EXPERIMENT: start depth is fixed, disturbance")
report.append("  is standardised, the ONLY variable is linger duration.")
report.append("- If linger duration predicts final residue: TIME AT DEPTH directly")
report.append("  causes address recovery. The confound is ruled out.")
report.append("- If linger duration doesn't matter: the natural-walk correlation was")
report.append("  entirely due to starting depth, not lingering.\n")

report.append("## Figures\n")
report.append("1. fig_1 — CONTROLLED residue vs linger duration (THE KEY FIGURE)")
report.append("2. fig_2 — Phase-by-phase residue through the walk")
report.append("3. fig_3 — Hull depth through each phase (sanity check)")
report.append("4. fig_4 — Substrate comparison: controlled S-curves overlaid")
report.append("5. fig_5 — Residue trajectory during the linger phase itself")
report.append("6. fig_6 — Fraction of disturbance recovered vs linger duration")

with open(os.path.join(OUT, "controlled_linger_v0_1_report.md"), "w") as f:
    f.write("\n".join(report))

print(f"\nAll done! Results in {OUT}")
