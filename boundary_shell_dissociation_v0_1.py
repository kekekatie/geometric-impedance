"""
Double-Dissociation Boundary Shell v0.1

Same 2×2 AUC pipeline as Part B, but on the BOUNDARY SHELL (outermost 25%)
instead of the interior 75%.

Prediction (from other Claude's analysis):
- AB's weave should weaken at the boundary (directions are biased there)
- AB's address should become load-bearing
- Shuffle should finally hurt AB → completing the double dissociation
- The exo/endo split is a boundary phenomenon, not a whole-substrate trait

Kill condition:
- If AB boundary weave is still strong enough to carry identity alone,
  there's no double dissociation — period.
"""

import csv, math, os, random, time, warnings
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KDTree
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "diffusion_texture_stratified_scout_v0_2")
OUT  = os.path.join(BASE, "boundary_shell_dissociation_results")
os.makedirs(OUT, exist_ok=True)

SEED = 20260612
REPS = 10
WEAVE_COLS = ["g_degree", "g_neighbor_degree_mean", "g_local_clustering", "g_hop2_size"]


def load_substrate(name):
    if name == "AB_N30":
        verts = []
        with open(os.path.join(DATA, "clean_ab_full_raw_lift.csv"), encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                verts.append(r)
        edges = []
        with open(os.path.join(DATA, "large_ab_v0_6_edges.csv"), encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                u = int(r["source_index"])
                v = int(r["target_index"])
                if u != v:
                    edges.append((min(u, v), max(u, v)))
        address_cols = ["perp_x", "perp_y", "perp_r", "k_sum_mod4"]
    else:
        verts = []
        with open(os.path.join(DATA, "clean_penrose_full_raw_lift.csv"), encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                verts.append(r)
        edges = []
        with open(os.path.join(DATA, "clean_penrose_full_raw_edges.csv"), encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                u = int(r.get("source_index", r.get("source", 0)))
                v = int(r.get("target_index", r.get("target", 0)))
                if u != v:
                    edges.append((min(u, v), max(u, v)))
        address_cols = ["perp_x", "perp_y", "perp_r", "k_sum_mod5"]
    edges = sorted(set(edges))
    return verts, edges, address_cols


def adjacency(n, edges, active=None):
    active_set = set(range(n)) if active is None else set(active)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if u in active_set and v in active_set:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def graph_features(adj, active_indices):
    n = len(adj)
    active_set = set(active_indices)
    deg = np.array([len(adj[i]) if i in active_set else 0 for i in range(n)], dtype=float)
    neighbor_mean = np.zeros(n, dtype=float)
    clustering = np.zeros(n, dtype=float)
    hop2 = np.zeros(n, dtype=float)
    for i in active_set:
        nbrs = list(adj[i])
        k = len(nbrs)
        if k:
            neighbor_mean[i] = sum(deg[j] for j in nbrs) / k
            two = set(nbrs)
            for j in nbrs:
                two.update(adj[j])
            two.discard(i)
            hop2[i] = len(two)
        if k >= 2:
            links = sum(1 for a_idx in range(k) for b in nbrs[a_idx+1:] if b in adj[nbrs[a_idx]])
            clustering[i] = 2.0 * links / (k * (k - 1))
    return {
        "g_degree": deg,
        "g_neighbor_degree_mean": neighbor_mean,
        "g_local_clustering": clustering,
        "g_hop2_size": hop2,
    }


def retention(adj, seed_set):
    S = set(seed_set)
    if not S:
        return 0.0
    total = sum(len(adj[i]) for i in S)
    internal = sum(sum(1 for j in adj[i] if j in S) for i in S)
    return internal / total if total else 0.0


def graph_ball_radius2(adj, i):
    S = {i}
    S.update(adj[i])
    for j in list(adj[i]):
        S.update(adj[j])
    return S


def top_quartile_strict(scores, active):
    vals = np.array([scores[i] for i in active], dtype=float)
    cutoff = float(np.quantile(vals, 0.75))
    return {i for i in active if scores[i] > cutoff}, cutoff


def regenerate_shared_core_labels(rows, adj, active, euclid_seeds):
    n = len(rows)
    active = list(active)
    graph_scores = np.zeros(n, dtype=float)
    euclid_scores = np.zeros(n, dtype=float)
    packet_scores = np.zeros(n, dtype=float)
    for i in active:
        graph_scores[i] = retention(adj, graph_ball_radius2(adj, i))
        euclid_scores[i] = retention(adj, euclid_seeds.get(i, [i]))
        packet_scores[i] = retention(adj, {i} | set(adj[i]))
    graph_priv, _ = top_quartile_strict(graph_scores, active)
    euclid_priv, _ = top_quartile_strict(euclid_scores, active)
    packet_priv, _ = top_quartile_strict(packet_scores, active)
    shared = graph_priv & euclid_priv & packet_priv
    y = np.array([1 if i in shared else 0 for i in active], dtype=int)
    return y, shared


def cv_metrics(X, y, seed):
    y = np.asarray(y, dtype=int)
    pos, neg = int(y.sum()), int((1-y).sum())
    if pos < 2 or neg < 2:
        return {"auc": float("nan"), "ap": float("nan")}
    n_splits = min(3, pos, neg)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    probs = np.zeros(len(y))
    for train, test in cv.split(X, y):
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=700, class_weight="balanced",
                               solver="liblinear", random_state=seed)
        )
        model.fit(X[train], y[train])
        probs[test] = model.predict_proba(X[test])[:, 1]
    return {
        "auc": float(roc_auc_score(y, probs)),
        "ap": float(average_precision_score(y, probs)),
    }


def double_edge_rewire(edges, attempts, seed):
    rr = random.Random(seed)
    edge_list = list(edges)
    edge_set = set(edge_list)
    accepted = 0
    for _ in range(attempts):
        if len(edge_list) < 2:
            break
        i, j = rr.sample(range(len(edge_list)), 2)
        a, b = edge_list[i]
        c, d = edge_list[j]
        if len({a, b, c, d}) < 4:
            continue
        if rr.random() < 0.5:
            e1, e2 = (min(a, d), max(a, d)), (min(c, b), max(c, b))
        else:
            e1, e2 = (min(a, c), max(a, c)), (min(b, d), max(b, d))
        if e1[0] == e1[1] or e2[0] == e2[1] or e1 == e2:
            continue
        if e1 in edge_set or e2 in edge_set:
            continue
        edge_set.remove(edge_list[i])
        edge_set.remove(edge_list[j])
        edge_set.add(e1)
        edge_set.add(e2)
        edge_list[i] = e1
        edge_list[j] = e2
        accepted += 1
    return sorted(edge_set), accepted


# ── Main ──────────────────────────────────────────────────────

# We run THREE subsets: interior_75, boundary_25, and full patch
# This lets us see the gradient in one experiment

SUBSETS = {
    "interior_75pct": lambda order, n: np.sort(order[:int(round(0.75 * n))]),
    "boundary_25pct": lambda order, n: np.sort(order[int(round(0.75 * n)):]),
    "full_patch": lambda order, n: np.arange(n),
}

all_results = []

for name in ["AB_N30", "Penrose_N24"]:
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    t0 = time.time()

    rows, edges, address_cols = load_substrate(name)
    n = len(rows)
    print(f"  {n} vertices, {len(edges)} edges")

    pts = np.array([[float(r["x"]), float(r["y"])] for r in rows], dtype=float)
    cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
    phys_r = np.sqrt((pts[:, 0] - cx)**2 + (pts[:, 1] - cy)**2)
    order = np.argsort(phys_r)

    adj_native = adjacency(n, edges)
    edge_len = float(np.median([np.linalg.norm(pts[u] - pts[v]) for u, v in edges]))
    euclid_radius = 3.0 * edge_len
    tree = KDTree(pts)

    address_full = np.array([[float(rows[i].get(c, 0)) for c in address_cols]
                             for i in range(n)], dtype=float)

    for subset_name, subset_fn in SUBSETS.items():
        active = subset_fn(order, n).astype(int)
        active_list = active.tolist()
        n_active = len(active)

        print(f"\n  --- {subset_name} (N={n_active}) ---")

        q = tree.query_radius(pts[active_list], r=euclid_radius)
        euclid_seeds = {active_list[pos]: q[pos].tolist() for pos in range(len(active_list))}

        y_identity, native_set = regenerate_shared_core_labels(
            rows, adj_native, active_list, euclid_seeds)
        n_pos = int(y_identity.sum())
        print(f"  Core positives: {n_pos} ({100*n_pos/n_active:.1f}%)")

        if n_pos < 5:
            print(f"  WARNING: too few positives ({n_pos}), skipping this subset")
            continue

        A_native = address_full[active]
        gf_native = graph_features(adj_native, active_list)
        W_native = np.column_stack([gf_native[c][active] for c in WEAVE_COLS])
        H_native = np.column_stack([A_native, W_native])

        # Native baseline
        print(f"  Native baseline...")
        for fs_name, X in [("address", A_native), ("weave", W_native), ("hybrid", H_native)]:
            m = cv_metrics(X, y_identity, SEED + 1)
            auc_val = m["auc"]
            print(f"    {fs_name}: AUC = {auc_val:.4f}")
            all_results.append({
                "substrate": name, "subset": subset_name,
                "perturbation": "native", "replicate": 0,
                "feature_set": fs_name, "auc": auc_val,
            })

        # Rewire
        attempts = 5 * len(edges)
        print(f"  Rewire ({REPS} reps)...")
        for rep in range(REPS):
            t_rep = time.time()
            redges, acc = double_edge_rewire(edges, attempts=attempts, seed=SEED + 81000 + rep)
            adj_rewired = adjacency(n, redges)
            gf_rew = graph_features(adj_rewired, active_list)
            W_rew = np.column_stack([gf_rew[c][active] for c in WEAVE_COLS])
            H_rew = np.column_stack([A_native, W_rew])

            for fs_name, X in [("address", A_native), ("weave", W_rew), ("hybrid", H_rew)]:
                m = cv_metrics(X, y_identity, SEED + 100000 + rep * 10 + hash(fs_name) % 7)
                all_results.append({
                    "substrate": name, "subset": subset_name,
                    "perturbation": "rewire", "replicate": rep,
                    "feature_set": fs_name, "auc": m["auc"],
                })
            print(f"    Rep {rep+1}/{REPS}: {time.time()-t_rep:.1f}s")

        # Shuffle
        print(f"  Shuffle ({REPS} reps)...")
        for rep in range(REPS):
            t_rep = time.time()
            rng = np.random.default_rng(SEED + 200 + rep)
            perm = rng.permutation(n)
            A_shuf = address_full[perm][active]
            H_shuf = np.column_stack([A_shuf, W_native])

            for fs_name, X in [("address", A_shuf), ("weave", W_native), ("hybrid", H_shuf)]:
                m = cv_metrics(X, y_identity, SEED + 300000 + rep * 10 + hash(fs_name) % 7)
                all_results.append({
                    "substrate": name, "subset": subset_name,
                    "perturbation": "shuffle", "replicate": rep,
                    "feature_set": fs_name, "auc": m["auc"],
                })
            print(f"    Rep {rep+1}/{REPS}: {time.time()-t_rep:.1f}s")

    print(f"\n  Total time for {name}: {time.time()-t0:.1f}s")


# ── Analysis ──────────────────────────────────────────────────

print("\n" + "="*60)
print("  RESULTS")
print("="*60)

summary = {}
for r in all_results:
    key = (r["substrate"], r["subset"], r["perturbation"], r["feature_set"])
    summary.setdefault(key, []).append(r["auc"])

# Per-replicate CSV
with open(os.path.join(OUT, "per_replicate_table.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["substrate", "subset", "perturbation",
                                       "replicate", "feature_set", "auc"])
    w.writeheader()
    for r in all_results:
        w.writerow(r)

# Print comparison: interior vs boundary for each substrate
for name in ["AB_N30", "Penrose_N24"]:
    label = "AB" if "AB" in name else "Penrose"
    print(f"\n  {label}:")
    print(f"  {'':12s} | {'Interior 75%':>36s} | {'Boundary 25%':>36s} | {'Full':>36s}")
    print(f"  {'':12s} | {'addr':>8s} {'weave':>8s} {'hybrid':>8s} | {'addr':>8s} {'weave':>8s} {'hybrid':>8s} | {'addr':>8s} {'weave':>8s} {'hybrid':>8s}")
    print("  " + "-"*120)
    for pert in ["native", "rewire", "shuffle"]:
        parts = []
        for subset in ["interior_75pct", "boundary_25pct", "full_patch"]:
            cells = []
            for fs in ["address", "weave", "hybrid"]:
                vals = summary.get((name, subset, pert, fs), [float("nan")])
                cells.append(f"{np.mean(vals):>8.4f}")
            parts.append(" ".join(cells))
        print(f"  {pert:12s} | {parts[0]} | {parts[1]} | {parts[2]}")

# The key test: AB boundary shell under shuffle
print("\n" + "="*60)
print("  THE KEY TEST: Does AB boundary weave weaken?")
print("="*60)

ab_int_weave = np.mean(summary.get(("AB_N30", "interior_75pct", "native", "weave"), [0]))
ab_bnd_weave = np.mean(summary.get(("AB_N30", "boundary_25pct", "native", "weave"), [0]))
ab_int_addr = np.mean(summary.get(("AB_N30", "interior_75pct", "native", "address"), [0]))
ab_bnd_addr = np.mean(summary.get(("AB_N30", "boundary_25pct", "native", "address"), [0]))

print(f"  AB interior weave: {ab_int_weave:.4f}")
print(f"  AB boundary weave: {ab_bnd_weave:.4f}")
print(f"  AB interior address: {ab_int_addr:.4f}")
print(f"  AB boundary address: {ab_bnd_addr:.4f}")

weave_drops = ab_bnd_weave < ab_int_weave - 0.05
addr_stays = ab_bnd_addr > 0.7

if weave_drops:
    print(f"\n  WEAVE WEAKENS AT BOUNDARY (drop of {ab_int_weave - ab_bnd_weave:.4f})")
else:
    print(f"\n  Weave does NOT substantially weaken (drop of {ab_int_weave - ab_bnd_weave:.4f})")

# Check if shuffle now hurts AB at boundary
ab_bnd_native_hybrid = np.mean(summary.get(("AB_N30", "boundary_25pct", "native", "hybrid"), [0]))
ab_bnd_shuffle_hybrid = np.mean(summary.get(("AB_N30", "boundary_25pct", "shuffle", "hybrid"), [0]))
ab_bnd_rewire_hybrid = np.mean(summary.get(("AB_N30", "boundary_25pct", "rewire", "hybrid"), [0]))

pen_bnd_native_hybrid = np.mean(summary.get(("Penrose_N24", "boundary_25pct", "native", "hybrid"), [0]))
pen_bnd_shuffle_hybrid = np.mean(summary.get(("Penrose_N24", "boundary_25pct", "shuffle", "hybrid"), [0]))
pen_bnd_rewire_hybrid = np.mean(summary.get(("Penrose_N24", "boundary_25pct", "rewire", "hybrid"), [0]))

ab_shuf_drop = ab_bnd_native_hybrid - ab_bnd_shuffle_hybrid
ab_rew_drop = ab_bnd_native_hybrid - ab_bnd_rewire_hybrid
pen_shuf_drop = pen_bnd_native_hybrid - pen_bnd_shuffle_hybrid
pen_rew_drop = pen_bnd_native_hybrid - pen_bnd_rewire_hybrid

print(f"\n  Boundary shell hybrid deltas:")
print(f"    AB:      rewire Δ = {-ab_rew_drop:+.4f},  shuffle Δ = {-ab_shuf_drop:+.4f}")
print(f"    Penrose: rewire Δ = {-pen_rew_drop:+.4f},  shuffle Δ = {-pen_shuf_drop:+.4f}")

ab_more_shuffle = ab_shuf_drop > ab_rew_drop
pen_more_rewire = pen_rew_drop > pen_shuf_drop

if ab_more_shuffle and pen_more_rewire:
    print("\n  >>> DOUBLE DISSOCIATION AT THE BOUNDARY! <<<")
    print("  AB drops more under shuffle, Penrose drops more under rewire.")
    print("  The exo/endo split is a boundary phenomenon.")
elif ab_more_shuffle:
    print("\n  AB arm works (drops more under shuffle), Penrose arm doesn't.")
elif pen_more_rewire:
    print("\n  Same as interior: single dissociation (Penrose arm only).")
    print("  AB boundary weave is still strong enough to compensate.")
else:
    print("\n  No dissociation pattern at boundary either.")


# ── Figure 1: The gradient — interior vs boundary vs full ─────

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Interior vs Boundary: Channel AUC Under Perturbation", fontsize=14, fontweight="bold")

for row_idx, name in enumerate(["AB_N30", "Penrose_N24"]):
    label = "AB" if "AB" in name else "Penrose"
    for col_idx, fs in enumerate(["address", "weave", "hybrid"]):
        ax = axes[row_idx, col_idx]

        subsets = ["interior_75pct", "boundary_25pct", "full_patch"]
        x = np.arange(len(subsets))
        width = 0.25

        for p_idx, pert in enumerate(["native", "rewire", "shuffle"]):
            vals = [np.mean(summary.get((name, s, pert, fs), [float("nan")])) for s in subsets]
            colors = ["#4CAF50", "#2196F3", "#FF5722"]
            ax.bar(x + (p_idx - 1) * width, vals, width, label=pert,
                   color=colors[p_idx], alpha=0.8)

        ax.set_ylim(0.4, 1.05)
        ax.set_xticks(x)
        ax.set_xticklabels(["Interior\n75%", "Boundary\n25%", "Full"], fontsize=9)
        ax.set_title(f"{label} — {fs}", fontsize=11, fontweight="bold")
        ax.set_ylabel("Identity AUC" if col_idx == 0 else "")
        ax.axhline(y=0.5, color="grey", linewidth=0.5, linestyle="--")
        if row_idx == 0 and col_idx == 2:
            ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_interior_vs_boundary.png"), dpi=150, bbox_inches="tight")
plt.close()


# ── Figure 2: The 2×2 at boundary only ───────────────────────

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Boundary Shell (Outer 25%): Dissociation Heatmap", fontsize=14, fontweight="bold")

substrates = ["AB_N30", "Penrose_N24"]

for col_idx, fs in enumerate(["hybrid", "address", "weave"]):
    data = np.zeros((2, 3))
    for i, sub in enumerate(substrates):
        for j, pert in enumerate(["native", "rewire", "shuffle"]):
            vals = summary.get((sub, "boundary_25pct", pert, fs), [float("nan")])
            data[i, j] = np.mean(vals)

    im = axes[col_idx].imshow(data, cmap="RdYlGn", vmin=0.4, vmax=1.0, aspect="auto")
    axes[col_idx].set_xticks(range(3))
    axes[col_idx].set_xticklabels(["Native", "Rewire", "Shuffle"], fontsize=10)
    axes[col_idx].set_yticks(range(2))
    axes[col_idx].set_yticklabels(["AB", "Penrose"], fontsize=10)
    axes[col_idx].set_title(f"{fs.title()} AUC", fontsize=12, fontweight="bold")
    for i in range(2):
        for j in range(3):
            val = data[i, j]
            if not np.isnan(val):
                axes[col_idx].text(j, i, f"{val:.3f}", ha="center", va="center",
                                   fontsize=12, fontweight="bold",
                                   color="white" if val < 0.65 else "black")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_boundary_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()


# ── Report ────────────────────────────────────────────────────

report = ["# Boundary Shell Dissociation v0.1\n"]
report.append("## The question")
report.append("Is the exo/endo double dissociation a boundary phenomenon?")
report.append("On the interior, AB's weave is so strong (0.999) that shuffle can't hurt it.")
report.append("If weave weakens at the boundary (where directions are biased), shuffle should")
report.append("finally break AB, completing the double dissociation.\n")

report.append("## Results: Interior vs Boundary\n")
report.append("| Substrate | Subset | Native Addr | Native Weave | Native Hybrid | Rewire Hybrid | Shuffle Hybrid |")
report.append("|-----------|--------|-------------|--------------|---------------|---------------|----------------|")
for name in substrates:
    label = "AB" if "AB" in name else "Penrose"
    for subset in ["interior_75pct", "boundary_25pct", "full_patch"]:
        na = np.mean(summary.get((name, subset, "native", "address"), [float("nan")]))
        nw = np.mean(summary.get((name, subset, "native", "weave"), [float("nan")]))
        nh = np.mean(summary.get((name, subset, "native", "hybrid"), [float("nan")]))
        rh = np.mean(summary.get((name, subset, "rewire", "hybrid"), [float("nan")]))
        sh = np.mean(summary.get((name, subset, "shuffle", "hybrid"), [float("nan")]))
        s_label = subset.replace("_", " ").replace("pct", "%")
        report.append(f"| {label} | {s_label} | {na:.4f} | {nw:.4f} | {nh:.4f} | {rh:.4f} | {sh:.4f} |")

report.append(f"\n## The key test: AB boundary weave")
report.append(f"- Interior weave AUC: {ab_int_weave:.4f}")
report.append(f"- Boundary weave AUC: {ab_bnd_weave:.4f}")
report.append(f"- Drop: {ab_int_weave - ab_bnd_weave:.4f}")

report.append(f"\n## Boundary shell 2×2 (hybrid)")
report.append(f"|          | Rewire Δ | Shuffle Δ |")
report.append(f"|----------|----------|-----------|")
report.append(f"| AB       | {-ab_rew_drop:+.4f}  | {-ab_shuf_drop:+.4f}  |")
report.append(f"| Penrose  | {-pen_rew_drop:+.4f}  | {-pen_shuf_drop:+.4f}  |")

if ab_more_shuffle and pen_more_rewire:
    report.append(f"\n## DOUBLE DISSOCIATION CONFIRMED AT BOUNDARY")
    report.append("AB drops more under shuffle, Penrose drops more under rewire.")
    report.append("The exo/endo split is a boundary phenomenon — same locus as the drift,")
    report.append("same locus as directional balance bias, same edge where 'time happens.'")
else:
    report.append(f"\n## Dissociation pattern: {'single' if pen_more_rewire else 'none'}")
    if not ab_more_shuffle:
        report.append("AB boundary weave still compensates for address knockout.")

with open(os.path.join(OUT, "boundary_shell_report.md"), "w") as f:
    f.write("\n".join(report))

# Summary CSV
with open(os.path.join(OUT, "summary_table.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["substrate", "subset", "perturbation", "address_auc", "weave_auc", "hybrid_auc"])
    for name in substrates:
        for subset in ["interior_75pct", "boundary_25pct", "full_patch"]:
            for pert in ["native", "rewire", "shuffle"]:
                addr = np.mean(summary.get((name, subset, pert, "address"), [float("nan")]))
                weave = np.mean(summary.get((name, subset, pert, "weave"), [float("nan")]))
                hybrid = np.mean(summary.get((name, subset, pert, "hybrid"), [float("nan")]))
                w.writerow([name, subset, pert, f"{addr:.4f}", f"{weave:.4f}", f"{hybrid:.4f}"])

print("\nAll done! Results in", OUT)
