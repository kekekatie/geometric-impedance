"""
Double-Dissociation Part B: Unified 2×2 table

Same AUC pipeline as the silent-corruption paper, but now with TWO perturbations:
  1. REWIRE: degree-preserving edge swaps (graph scrambled, coords kept)
  2. SHUFFLE: perp-space coordinates randomly permuted (coords scrambled, graph kept)

Reports identity-persistence AUC for address / weave / hybrid features
under both perturbations, both substrates, on the same ruler.

Uses interior_75pct subset to match existing rewire results.
"""

import csv, math, os, random, time, warnings
import numpy as np
from scipy.stats import spearmanr
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
OUT  = os.path.join(BASE, "double_dissociation_partB_results")
os.makedirs(OUT, exist_ok=True)

SEED = 20260612
REPS = 10
INTERIOR_FRAC = 0.75
WEAVE_COLS = ["g_degree", "g_neighbor_degree_mean", "g_local_clustering", "g_hop2_size"]


# ── Data loading ──────────────────────────────────────────────

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

all_results = []

for name in ["AB_N30", "Penrose_N24"]:
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    t0 = time.time()

    rows, edges, address_cols = load_substrate(name)
    n = len(rows)
    print(f"  {n} vertices, {len(edges)} edges")

    # Interior subset
    pts = np.array([[float(r["x"]), float(r["y"])] for r in rows], dtype=float)
    cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
    phys_r = np.sqrt((pts[:, 0] - cx)**2 + (pts[:, 1] - cy)**2)
    order = np.argsort(phys_r)
    active = np.sort(order[:int(round(INTERIOR_FRAC * n))]).astype(int)
    active_list = active.tolist()
    n_active = len(active)
    print(f"  Interior 75%: {n_active} vertices")

    # Native graph
    adj_native = adjacency(n, edges)

    # Euclidean seeds
    edge_len = float(np.median([np.linalg.norm(pts[u] - pts[v]) for u, v in edges]))
    euclid_radius = 3.0 * edge_len
    tree = KDTree(pts)
    q = tree.query_radius(pts[active_list], r=euclid_radius)
    euclid_seeds = {active_list[pos]: q[pos].tolist() for pos in range(len(active_list))}

    # Native identity labels
    y_identity, native_set = regenerate_shared_core_labels(rows, adj_native, active_list, euclid_seeds)
    n_pos = int(y_identity.sum())
    print(f"  Native core: {n_pos} positives ({100*n_pos/n_active:.1f}%)")

    # Native address features
    address_full = np.array([[float(rows[i].get(c, 0)) for c in address_cols] for i in range(n)], dtype=float)
    A_native = address_full[active]

    # Native weave features
    gf_native = graph_features(adj_native, active_list)
    W_native = np.column_stack([gf_native[c][active] for c in WEAVE_COLS])
    H_native = np.column_stack([A_native, W_native])

    # ── Native baseline ──
    print(f"\n  Native baseline...")
    for fs_name, X in [("address", A_native), ("weave", W_native), ("hybrid", H_native)]:
        m = cv_metrics(X, y_identity, SEED + 1)
        print(f"    {fs_name}: AUC = {m['auc']:.4f}")
        all_results.append({
            "substrate": name, "perturbation": "native", "replicate": 0,
            "feature_set": fs_name, "auc": m["auc"],
        })

    # ── Rewire perturbation ──
    print(f"\n  Rewire perturbation ({REPS} reps)...")
    attempts = 5 * len(edges)
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
                "substrate": name, "perturbation": "rewire", "replicate": rep,
                "feature_set": fs_name, "auc": m["auc"],
            })
        dt = time.time() - t_rep
        print(f"    Rep {rep+1}/{REPS}: {dt:.1f}s, acc={acc}")

    # ── Shuffle perturbation ──
    print(f"\n  Shuffle perturbation ({REPS} reps)...")
    for rep in range(REPS):
        t_rep = time.time()
        rng = np.random.default_rng(SEED + 200 + rep)
        perm = rng.permutation(n)

        # Shuffle address features: each vertex gets a different vertex's perp-space coords
        A_shuf = address_full[perm][active]

        # Weave features unchanged (same graph)
        H_shuf = np.column_stack([A_shuf, W_native])

        for fs_name, X in [("address", A_shuf), ("weave", W_native), ("hybrid", H_shuf)]:
            m = cv_metrics(X, y_identity, SEED + 300000 + rep * 10 + hash(fs_name) % 7)
            all_results.append({
                "substrate": name, "perturbation": "shuffle", "replicate": rep,
                "feature_set": fs_name, "auc": m["auc"],
            })
        dt = time.time() - t_rep
        print(f"    Rep {rep+1}/{REPS}: {dt:.1f}s")

    print(f"\n  Total time for {name}: {time.time()-t0:.1f}s")


# ── Analysis ──────────────────────────────────────────────────

df = pd.DataFrame(all_results) if False else None  # avoid pandas dependency

print("\n" + "="*60)
print("  RESULTS SUMMARY")
print("="*60)

# Organize results
summary = {}
for r in all_results:
    key = (r["substrate"], r["perturbation"], r["feature_set"])
    summary.setdefault(key, []).append(r["auc"])

# Write per-replicate CSV
with open(os.path.join(OUT, "per_replicate_table.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["substrate", "perturbation", "replicate", "feature_set", "auc"])
    w.writeheader()
    for r in all_results:
        w.writerow(r)

# Build summary table
summary_rows = []
for (sub, pert, fs), vals in sorted(summary.items()):
    vals = np.array(vals)
    summary_rows.append({
        "substrate": sub, "perturbation": pert, "feature_set": fs,
        "mean_auc": f"{vals.mean():.4f}", "std_auc": f"{vals.std():.4f}",
        "min_auc": f"{vals.min():.4f}", "max_auc": f"{vals.max():.4f}",
        "n_reps": len(vals),
    })

with open(os.path.join(OUT, "summary_table.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
    w.writeheader()
    w.writerows(summary_rows)

# Print the 2×2 table (using hybrid AUC as the single metric)
print("\n  2×2 DISSOCIATION TABLE (hybrid AUC):")
print("  " + "-"*55)
print(f"  {'':20s} | {'Rewire':>12s} | {'Shuffle':>12s} | {'Native':>12s}")
print("  " + "-"*55)
for sub in ["AB_N30", "Penrose_N24"]:
    native_vals = summary.get((sub, "native", "hybrid"), [0])
    rewire_vals = summary.get((sub, "rewire", "hybrid"), [0])
    shuffle_vals = summary.get((sub, "shuffle", "hybrid"), [0])
    native_mean = np.mean(native_vals)
    rewire_mean = np.mean(rewire_vals)
    shuffle_mean = np.mean(shuffle_vals)
    print(f"  {sub:20s} | {rewire_mean:>12.4f} | {shuffle_mean:>12.4f} | {native_mean:>12.4f}")
print("  " + "-"*55)

# Deltas from native
print("\n  DELTAS FROM NATIVE (hybrid AUC):")
print("  " + "-"*45)
print(f"  {'':20s} | {'Rewire Δ':>12s} | {'Shuffle Δ':>12s}")
print("  " + "-"*45)
for sub in ["AB_N30", "Penrose_N24"]:
    native_mean = np.mean(summary.get((sub, "native", "hybrid"), [0]))
    rewire_mean = np.mean(summary.get((sub, "rewire", "hybrid"), [0]))
    shuffle_mean = np.mean(summary.get((sub, "shuffle", "hybrid"), [0]))
    rew_delta = rewire_mean - native_mean
    shuf_delta = shuffle_mean - native_mean
    print(f"  {sub:20s} | {rew_delta:>+12.4f} | {shuf_delta:>+12.4f}")
print("  " + "-"*45)


# ── Figure: 2×2 heatmap ──────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel 1: Raw AUC 2×2
substrates = ["AB_N30", "Penrose_N24"]
perturbations = ["rewire", "shuffle"]
feature_sets = ["address", "weave", "hybrid"]

# Hybrid AUC heatmap
data_hybrid = np.zeros((2, 3))  # substrates × [native, rewire, shuffle]
labels_col = ["Native", "Rewire", "Shuffle"]
for i, sub in enumerate(substrates):
    for j, pert in enumerate(["native", "rewire", "shuffle"]):
        vals = summary.get((sub, pert, "hybrid"), [0])
        data_hybrid[i, j] = np.mean(vals)

im = axes[0].imshow(data_hybrid, cmap="RdYlGn", vmin=0.5, vmax=1.0, aspect="auto")
axes[0].set_xticks(range(3))
axes[0].set_xticklabels(labels_col, fontsize=10)
axes[0].set_yticks(range(2))
axes[0].set_yticklabels(["AB", "Penrose"], fontsize=10)
axes[0].set_title("Hybrid Identity AUC", fontsize=12, fontweight="bold")
for i in range(2):
    for j in range(3):
        axes[0].text(j, i, f"{data_hybrid[i,j]:.3f}", ha="center", va="center",
                     fontsize=12, fontweight="bold",
                     color="white" if data_hybrid[i,j] < 0.7 else "black")

# Panel 2: Address-only AUC
data_addr = np.zeros((2, 3))
for i, sub in enumerate(substrates):
    for j, pert in enumerate(["native", "rewire", "shuffle"]):
        vals = summary.get((sub, pert, "address"), [0])
        data_addr[i, j] = np.mean(vals)

im2 = axes[1].imshow(data_addr, cmap="RdYlGn", vmin=0.5, vmax=1.0, aspect="auto")
axes[1].set_xticks(range(3))
axes[1].set_xticklabels(labels_col, fontsize=10)
axes[1].set_yticks(range(2))
axes[1].set_yticklabels(["AB", "Penrose"], fontsize=10)
axes[1].set_title("Address-Only Identity AUC", fontsize=12, fontweight="bold")
for i in range(2):
    for j in range(3):
        axes[1].text(j, i, f"{data_addr[i,j]:.3f}", ha="center", va="center",
                     fontsize=12, fontweight="bold",
                     color="white" if data_addr[i,j] < 0.7 else "black")

# Panel 3: Weave-only AUC
data_weave = np.zeros((2, 3))
for i, sub in enumerate(substrates):
    for j, pert in enumerate(["native", "rewire", "shuffle"]):
        vals = summary.get((sub, pert, "weave"), [0])
        data_weave[i, j] = np.mean(vals)

im3 = axes[2].imshow(data_weave, cmap="RdYlGn", vmin=0.5, vmax=1.0, aspect="auto")
axes[2].set_xticks(range(3))
axes[2].set_xticklabels(labels_col, fontsize=10)
axes[2].set_yticks(range(2))
axes[2].set_yticklabels(["AB", "Penrose"], fontsize=10)
axes[2].set_title("Weave-Only Identity AUC", fontsize=12, fontweight="bold")
for i in range(2):
    for j in range(3):
        axes[2].text(j, i, f"{data_weave[i,j]:.3f}", ha="center", va="center",
                     fontsize=12, fontweight="bold",
                     color="white" if data_weave[i,j] < 0.7 else "black")

plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_1_dissociation_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()


# ── Figure 2: Delta-from-native bar chart ─────────────────────

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(3)
width = 0.35

for idx, sub in enumerate(substrates):
    label = "AB" if "AB" in sub else "Penrose"
    native_vals = {fs: np.mean(summary.get((sub, "native", fs), [0])) for fs in feature_sets}
    deltas_rew = [np.mean(summary.get((sub, "rewire", fs), [0])) - native_vals[fs] for fs in feature_sets]
    deltas_shuf = [np.mean(summary.get((sub, "shuffle", fs), [0])) - native_vals[fs] for fs in feature_sets]

    offset = -width/2 if idx == 0 else width/2
    bars_r = ax.bar(x*3 + offset, deltas_rew, width, label=f"{label} rewire",
                    color=["#2196F3", "#2196F3", "#2196F3"][idx], alpha=0.7 + 0.3*idx)
    bars_s = ax.bar(x*3 + 1 + offset, deltas_shuf, width, label=f"{label} shuffle",
                    color=["#FF5722", "#FF5722", "#FF5722"][idx], alpha=0.7 + 0.3*idx)

ax.set_ylabel("Delta AUC from Native", fontsize=12)
ax.set_title("Channel Knockout: Delta from Native Baseline", fontsize=14, fontweight="bold")
ax.set_xticks([0, 1, 3, 4, 6, 7])
ax.set_xticklabels(["addr\nrewire", "addr\nshuffle", "weave\nrewire", "weave\nshuffle",
                     "hybrid\nrewire", "hybrid\nshuffle"], fontsize=9)
ax.axhline(y=0, color="black", linewidth=0.5)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig_2_delta_from_native.png"), dpi=150, bbox_inches="tight")
plt.close()


# ── Write the 2×2 CSV ────────────────────────────────────────

with open(os.path.join(OUT, "dissociation_2x2.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["substrate", "perturbation", "address_auc", "weave_auc", "hybrid_auc"])
    for sub in substrates:
        for pert in ["native", "rewire", "shuffle"]:
            addr = np.mean(summary.get((sub, pert, "address"), [0]))
            weave = np.mean(summary.get((sub, pert, "weave"), [0]))
            hybrid = np.mean(summary.get((sub, pert, "hybrid"), [0]))
            w.writerow([sub, pert, f"{addr:.4f}", f"{weave:.4f}", f"{hybrid:.4f}"])


# ── Report ────────────────────────────────────────────────────

report = ["# Double-Dissociation Part B: Unified 2×2 Table\n"]
report.append("## Protocol")
report.append(f"- Interior 75% subset, {REPS} replicates per perturbation")
report.append(f"- Rewire: 5E degree-preserving edge swaps")
report.append(f"- Shuffle: random permutation of perp-space coordinates")
report.append(f"- Metric: cross-validated logistic regression AUC (identity persistence)")
report.append(f"- Same ruler for all four cells\n")

report.append("## 2×2 Table (Hybrid AUC)\n")
report.append("|                | Native | Rewire | Shuffle |")
report.append("|----------------|--------|--------|---------|")
for sub in substrates:
    label = "AB" if "AB" in sub else "Penrose"
    vals = {p: np.mean(summary.get((sub, p, "hybrid"), [0])) for p in ["native", "rewire", "shuffle"]}
    report.append(f"| **{label}** | {vals['native']:.4f} | {vals['rewire']:.4f} | {vals['shuffle']:.4f} |")

report.append("\n## Deltas from Native\n")
report.append("|                | Rewire Δ | Shuffle Δ |")
report.append("|----------------|----------|-----------|")
for sub in substrates:
    label = "AB" if "AB" in sub else "Penrose"
    native = np.mean(summary.get((sub, "native", "hybrid"), [0]))
    rew = np.mean(summary.get((sub, "rewire", "hybrid"), [0])) - native
    shuf = np.mean(summary.get((sub, "shuffle", "hybrid"), [0])) - native
    report.append(f"| **{label}** | {rew:+.4f} | {shuf:+.4f} |")

report.append("\n## Channel-Level Detail\n")
report.append("| Substrate | Perturbation | Address AUC | Weave AUC | Hybrid AUC |")
report.append("|-----------|-------------|-------------|-----------|------------|")
for sub in substrates:
    label = "AB" if "AB" in sub else "Penrose"
    for pert in ["native", "rewire", "shuffle"]:
        addr = np.mean(summary.get((sub, pert, "address"), [0]))
        weave = np.mean(summary.get((sub, pert, "weave"), [0]))
        hybrid = np.mean(summary.get((sub, pert, "hybrid"), [0]))
        report.append(f"| {label} | {pert} | {addr:.4f} | {weave:.4f} | {hybrid:.4f} |")

# Dissociation assessment
report.append("\n## Dissociation Assessment\n")

ab_rew_hybrid = np.mean(summary.get(("AB_N30", "rewire", "hybrid"), [0]))
ab_shuf_hybrid = np.mean(summary.get(("AB_N30", "shuffle", "hybrid"), [0]))
pen_rew_hybrid = np.mean(summary.get(("Penrose_N24", "rewire", "hybrid"), [0]))
pen_shuf_hybrid = np.mean(summary.get(("Penrose_N24", "shuffle", "hybrid"), [0]))

ab_native_h = np.mean(summary.get(("AB_N30", "native", "hybrid"), [0]))
pen_native_h = np.mean(summary.get(("Penrose_N24", "native", "hybrid"), [0]))

ab_rew_drop = ab_native_h - ab_rew_hybrid
ab_shuf_drop = ab_native_h - ab_shuf_hybrid
pen_rew_drop = pen_native_h - pen_rew_hybrid
pen_shuf_drop = pen_native_h - pen_shuf_hybrid

report.append(f"AB drops under rewire: {ab_rew_drop:+.4f}, under shuffle: {ab_shuf_drop:+.4f}")
report.append(f"Penrose drops under rewire: {pen_rew_drop:+.4f}, under shuffle: {pen_shuf_drop:+.4f}")

# Check double dissociation pattern
# Expected: AB drops MORE under shuffle, Penrose drops MORE under rewire
ab_more_shuffle = ab_shuf_drop > ab_rew_drop
pen_more_rewire = pen_rew_drop > pen_shuf_drop

if ab_more_shuffle and pen_more_rewire:
    report.append("\n**DOUBLE DISSOCIATION CONFIRMED:** AB drops more under shuffle (address knockout), Penrose drops more under rewire (weave knockout). The diagonal/off-diagonal pattern holds.")
    # Check symmetry
    magnitude_ratio = abs(ab_shuf_drop - ab_rew_drop) / (abs(pen_rew_drop - pen_shuf_drop) + 1e-12)
    report.append(f"\nAsymmetry magnitude ratio: {magnitude_ratio:.2f} (1.0 = perfectly balanced)")
elif ab_more_shuffle:
    report.append("\n**SINGLE DISSOCIATION (AB arm only):** AB drops more under shuffle, but Penrose does NOT drop more under rewire.")
elif pen_more_rewire:
    report.append("\n**SINGLE DISSOCIATION (Penrose arm only):** Penrose drops more under rewire, but AB does NOT drop more under shuffle.")
else:
    report.append("\n**NO DISSOCIATION:** Neither substrate shows the expected crossover pattern.")

with open(os.path.join(OUT, "partB_report.md"), "w") as f:
    f.write("\n".join(report))

print("\nAll done! Results in", OUT)
