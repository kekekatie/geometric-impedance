#!/usr/bin/env python3
"""
Large Penrose v0.2: Full-strength 5E audit matching AB v0.8 protocol.
K.T. Niedzwiecki - Claude Code execution

This runs the full apples-to-apples Penrose validation:
- 28,719 vertices, 54,695 edges
- 5E rewiring attempts per replicate (5 × 54,695 = 273,475)
- 10 replicates
- Subsets: full patch, interior-75% (skip interior-50% due to tiny positive counts)
- Identity persistence + fresh reconstruction audits
"""

import csv
import math
import os
import random
import time
from collections import defaultdict

import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KDTree

# Configuration
BASE = "C:/Users/Karen/Downloads"
OUT_PREFIX = os.path.join(BASE, "large_penrose_v0_2_5E")
SEED = 20260530
REPS = 10
SUBSETS = ["full_28719", "interior_75pct"]

# Weave feature columns
WEAVE_COLS = ["g_degree", "g_neighbor_degree_mean", "g_local_clustering", "g_hop2_size"]

print(f"[{time.strftime('%H:%M:%S')}] Large Penrose v0.2 5E Audit starting...", flush=True)


def read_lift(path):
    """Read Penrose lift CSV."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_edges(path):
    """Read edges, converting source/target to source_index/target_index format."""
    edges = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            # Handle both column naming conventions
            u = int(r.get("source_index", r.get("source", 0)))
            v = int(r.get("target_index", r.get("target", 0)))
            if u != v:
                edges.append((min(u, v), max(u, v)))
    return sorted(set(edges))


def adjacency(n, edges, active=None):
    """Build adjacency list."""
    active_set = set(range(n)) if active is None else set(active)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if u in active_set and v in active_set:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def graph_features(adj, active_indices=None):
    """Compute weave features from adjacency."""
    n = len(adj)
    active_set = set(range(n)) if active_indices is None else set(active_indices)
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


def native_edge_length(rows, edges):
    """Median edge length."""
    pts = np.array([[float(r["x"]), float(r["y"])] for r in rows], dtype=float)
    return float(np.median([np.linalg.norm(pts[u] - pts[v]) for u, v in edges]))


def euclidean_seed_lists(rows, radius, centers, candidates=None):
    """Build Euclidean neighborhood seeds."""
    pts = np.array([[float(r["x"]), float(r["y"])] for r in rows], dtype=float)
    centers = list(centers)
    candidates = list(range(len(rows))) if candidates is None else list(candidates)
    tree = KDTree(pts[candidates])
    q = tree.query_radius(pts[centers], r=radius)
    return {centers[pos]: [candidates[j] for j in q[pos]] for pos in range(len(centers))}


def retention(adj, seed):
    """Conductance retention score."""
    S = set(seed)
    if not S:
        return 0.0
    total = sum(len(adj[i]) for i in S)
    internal = sum(sum(1 for j in adj[i] if j in S) for i in S)
    return internal / total if total else 0.0


def graph_ball_radius2(adj, i):
    """Graph ball of radius 2."""
    S = {i}
    S.update(adj[i])
    for j in list(adj[i]):
        S.update(adj[j])
    return S


def top_quartile_strict(scores, active):
    """Strict top-quartile membership."""
    vals = np.array([scores[i] for i in active], dtype=float)
    cutoff = float(np.quantile(vals, 0.75))
    return {i for i in active if scores[i] > cutoff}, cutoff


def regenerate_shared_core_labels(rows, adj, active, euclid_seeds):
    """Regenerate conductance-retention labels on current graph."""
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
    return {
        "y": y,
        "shared_set": shared,
        "priv_counts": {"graph": len(graph_priv), "euclidean": len(euclid_priv), "packet": len(packet_priv), "shared": len(shared)},
    }


def double_edge_rewire(edges, attempts, seed):
    """Degree-preserving double-edge swap."""
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
        old1, old2 = edge_list[i], edge_list[j]
        if e1 in edge_set or e2 in edge_set:
            continue
        edge_set.remove(old1)
        edge_set.remove(old2)
        edge_set.add(e1)
        edge_set.add(e2)
        edge_list[i] = e1
        edge_list[j] = e2
        accepted += 1
    return sorted(edge_set), accepted


def edge_jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a or b else 1.0


def label_jaccard(set_a, set_b):
    return len(set_a & set_b) / len(set_a | set_b) if set_a or set_b else 1.0


def native_core_retention(native_set, current_set):
    return len(native_set & current_set) / len(native_set) if native_set else float("nan")


def cv_metrics(X, y, seed):
    """Cross-validated logistic regression."""
    y = np.asarray(y, dtype=int)
    pos, neg = int(y.sum()), int((1-y).sum())
    if pos < 2 or neg < 2:
        return {"auc": float("nan"), "ap": float("nan"), "n": len(y), "positives": pos}
    n_splits = min(3, pos, neg)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    probs = np.zeros(len(y))
    for train, test in cv.split(X, y):
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=700, class_weight="balanced", solver="liblinear", random_state=seed)
        )
        model.fit(X[train], y[train])
        probs[test] = model.predict_proba(X[test])[:, 1]
    return {
        "auc": float(roc_auc_score(y, probs)),
        "ap": float(average_precision_score(y, probs)),
        "n": len(y),
        "positives": pos
    }


def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            clean = {}
            for k in fieldnames:
                v = r.get(k, "")
                if isinstance(v, float):
                    clean[k] = "" if math.isnan(v) else f"{v:.6f}"
                else:
                    clean[k] = v
            w.writerow(clean)


def append_csv(path, rows, fieldnames):
    exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        for r in rows:
            clean = {}
            for k in fieldnames:
                v = r.get(k, "")
                if isinstance(v, float):
                    clean[k] = "" if math.isnan(v) else f"{v:.6f}"
                else:
                    clean[k] = v
            w.writerow(clean)


# ============ MAIN EXECUTION ============

print(f"[{time.strftime('%H:%M:%S')}] Loading Penrose substrate...", flush=True)
t0 = time.time()

# Load data
rows = read_lift(os.path.join(BASE, "clean_penrose_full_raw_lift.csv"))
edges = read_edges(os.path.join(BASE, "clean_penrose_full_raw_edges.csv"))
n = len(rows)

print(f"[{time.strftime('%H:%M:%S')}] Loaded {n} vertices, {len(edges)} edges", flush=True)

# Compute physical radius for interior subsets
pts = np.array([[float(r["x"]), float(r["y"])] for r in rows], dtype=float)
cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
phys_r = np.sqrt((pts[:, 0] - cx)**2 + (pts[:, 1] - cy)**2)
order = np.argsort(phys_r)

# Define subsets
subset_defs = {
    "full_28719": np.arange(n, dtype=int),
    "interior_75pct": np.sort(order[:int(round(0.75 * n))]).astype(int),
}

# Build address feature matrix (Penrose-specific)
# Address cols: perp_x, perp_y, perp_r, k_sum_mod5
address_cols = ["perp_x", "perp_y", "perp_r", "k_sum_mod5"]
address_full = np.array([[float(rows[i].get(c, 0)) for c in address_cols] for i in range(n)], dtype=float)

# Native setup
adj_native = adjacency(n, edges)
edge_len = native_edge_length(rows, edges)
euclid_radius = 3.0 * edge_len

print(f"[{time.strftime('%H:%M:%S')}] Median edge length: {edge_len:.4f}, Euclidean seed radius: {euclid_radius:.4f}", flush=True)

# Results storage
verification_rows = []
replicate_rows = []
rep_fields = [
    "subset", "replicate", "audit_mode", "feature_set",
    "n", "positives", "auc", "ap",
    "fresh_positive_count", "fresh_label_jaccard_vs_native", "fresh_native_core_retention",
    "edge_jaccard", "accepted_swaps"
]

# Rewiring params
attempts = 5 * len(edges)
print(f"[{time.strftime('%H:%M:%S')}] Rewiring: {attempts} attempts per replicate, {REPS} replicates", flush=True)

# Process each subset
for subset_name in SUBSETS:
    active = subset_defs[subset_name]
    active_list = active.tolist()

    print(f"\n[{time.strftime('%H:%M:%S')}] === Processing {subset_name} (N={len(active)}) ===", flush=True)

    # Build Euclidean seeds for this subset
    euclid_seeds = euclidean_seed_lists(rows, euclid_radius, active_list, candidates=range(n))

    # Native labels for this subset
    regen_native = regenerate_shared_core_labels(rows, adj_native, active_list, euclid_seeds)
    y_identity = regen_native["y"]
    native_set = regen_native["shared_set"]

    verification_rows.append({
        "subset": subset_name,
        "active_n": len(active),
        "native_core": int(y_identity.sum()),
        "graph_priv": regen_native["priv_counts"]["graph"],
        "euclid_priv": regen_native["priv_counts"]["euclidean"],
        "packet_priv": regen_native["priv_counts"]["packet"],
        "rewire_attempts": attempts,
        "replicates": REPS,
    })

    print(f"[{time.strftime('%H:%M:%S')}] Native core: {int(y_identity.sum())} positives", flush=True)

    # Address features for this subset
    A = address_full[active]

    # Static identity-address row (doesn't change across replicates)
    m_addr_static = cv_metrics(A, y_identity, SEED + 11)
    replicate_rows.append({
        "subset": subset_name, "replicate": -1, "audit_mode": "identity_persistence",
        "feature_set": "address", "n": m_addr_static["n"], "positives": m_addr_static["positives"],
        "auc": m_addr_static["auc"], "ap": m_addr_static["ap"],
        "fresh_positive_count": float("nan"), "fresh_label_jaccard_vs_native": float("nan"),
        "fresh_native_core_retention": float("nan"), "edge_jaccard": float("nan"), "accepted_swaps": float("nan")
    })

    print(f"[{time.strftime('%H:%M:%S')}] Static identity address AUC: {m_addr_static['auc']:.4f}", flush=True)

    # Run replicates
    for rep in range(REPS):
        t_rep = time.time()

        # Degree-preserving rewiring
        redges, acc = double_edge_rewire(edges, attempts=attempts, seed=SEED + 81000 + rep)
        adj = adjacency(n, redges)

        # Compute weave features on rewired graph
        gf = graph_features(adj)
        W = np.column_stack([gf[c][active] for c in WEAVE_COLS])
        H = np.column_stack([A, W])  # Hybrid = address + weave

        # Fresh labels on rewired graph
        regen_fresh = regenerate_shared_core_labels(rows, adj, active_list, euclid_seeds)
        y_fresh = regen_fresh["y"]
        fresh_set = regen_fresh["shared_set"]

        ej = edge_jaccard(edges, redges)
        meta = {
            "fresh_positive_count": int(y_fresh.sum()),
            "fresh_label_jaccard_vs_native": label_jaccard(native_set, fresh_set),
            "fresh_native_core_retention": native_core_retention(native_set, fresh_set),
            "edge_jaccard": ej,
            "accepted_swaps": acc,
        }

        # Run all audit combinations
        tasks = [
            ("identity_persistence", "weave", W, y_identity),
            ("identity_persistence", "hybrid", H, y_identity),
            ("fresh_reconstruction", "address", A, y_fresh),
            ("fresh_reconstruction", "weave", W, y_fresh),
            ("fresh_reconstruction", "hybrid", H, y_fresh),
        ]

        for audit, fs, X, y in tasks:
            m = cv_metrics(X, y, SEED + 100000 + rep * 100 + hash(fs) % 97)
            row = {
                "subset": subset_name, "replicate": rep, "audit_mode": audit,
                "feature_set": fs, "n": m["n"], "positives": m["positives"],
                "auc": m["auc"], "ap": m["ap"],
            }
            row.update(meta)
            replicate_rows.append(row)

        print(f"[{time.strftime('%H:%M:%S')}] Rep {rep+1}/{REPS}: acc={acc}, edgeJ={ej:.4f}, fresh={int(y_fresh.sum())}, time={time.time()-t_rep:.1f}s", flush=True)

# Write results
write_csv(OUT_PREFIX + "_verification.csv", verification_rows)
write_csv(OUT_PREFIX + "_replicates.csv", replicate_rows, rep_fields)

# Summarize
print(f"\n[{time.strftime('%H:%M:%S')}] Computing summary statistics...", flush=True)

summary_rows = []
grouped = defaultdict(list)
for r in replicate_rows:
    if r["replicate"] >= 0:  # Skip static rows
        key = (r["subset"], r["audit_mode"], r["feature_set"])
        grouped[key].append(r)

for (subset, audit, fs), vals in sorted(grouped.items()):
    row = {"subset": subset, "audit_mode": audit, "feature_set": fs, "replicates": len(vals)}
    for metric in ["auc", "ap", "fresh_label_jaccard_vs_native", "fresh_native_core_retention", "edge_jaccard"]:
        arr = [v[metric] for v in vals if isinstance(v[metric], (int, float)) and not math.isnan(v[metric])]
        row[f"{metric}_mean"] = sum(arr) / len(arr) if arr else float("nan")
        row[f"{metric}_sd"] = (sum((x - row[f"{metric}_mean"])**2 for x in arr) / (len(arr) - 1))**0.5 if len(arr) > 1 else 0.0
    summary_rows.append(row)

write_csv(OUT_PREFIX + "_summary.csv", summary_rows)

# Compact table for paper
compact_rows = []
for subset in SUBSETS:
    row = {"subset": subset}
    # Get verification info
    ver = next((v for v in verification_rows if v["subset"] == subset), {})
    row["active_n"] = ver.get("active_n", "")
    row["native_core"] = ver.get("native_core", "")

    # Get static identity address
    static = next((r for r in replicate_rows if r["subset"] == subset and r["replicate"] == -1), {})
    row["identity_address_auc"] = static.get("auc", float("nan"))

    # Get summary metrics
    for audit in ["identity_persistence", "fresh_reconstruction"]:
        short = "identity" if audit == "identity_persistence" else "fresh"
        for fs in ["weave", "hybrid"]:
            s = next((r for r in summary_rows if r["subset"] == subset and r["audit_mode"] == audit and r["feature_set"] == fs), {})
            row[f"{short}_{fs}_auc"] = s.get("auc_mean", float("nan"))
            row[f"{short}_{fs}_auc_sd"] = s.get("auc_sd", float("nan"))

    # Fresh address
    s = next((r for r in summary_rows if r["subset"] == subset and r["audit_mode"] == "fresh_reconstruction" and r["feature_set"] == "address"), {})
    row["fresh_address_auc"] = s.get("auc_mean", float("nan"))
    row["fresh_native_jaccard"] = s.get("fresh_label_jaccard_vs_native_mean", float("nan"))
    row["native_core_retention"] = s.get("fresh_native_core_retention_mean", float("nan"))
    row["edge_jaccard"] = s.get("edge_jaccard_mean", float("nan"))

    compact_rows.append(row)

write_csv(OUT_PREFIX + "_compact.csv", compact_rows)

# Generate report
print(f"\n[{time.strftime('%H:%M:%S')}] Writing report...", flush=True)

with open(OUT_PREFIX + "_report.md", "w", encoding="utf-8") as f:
    f.write("# Large Penrose v0.2: Full-strength 5E validation\n\n")
    f.write("Apples-to-apples matched validation for the Silent Relational Corruption paper.\n")
    f.write("This matches the AB v0.8 protocol: 5E rewiring, 10 replicates.\n\n")

    f.write("## Inputs\n\n")
    f.write(f"- Vertices: {n}\n")
    f.write(f"- Edges: {len(edges)}\n")
    f.write(f"- Rewiring attempts per replicate: {attempts}\n")
    f.write(f"- Replicates: {REPS}\n")
    f.write(f"- Address features: {', '.join(address_cols)}\n")
    f.write(f"- Weave features: {', '.join(WEAVE_COLS)}\n\n")

    f.write("## Verification\n\n")
    f.write("| subset | active N | native core | graph priv | euclid priv | packet priv |\n")
    f.write("|---|---:|---:|---:|---:|---:|\n")
    for v in verification_rows:
        f.write(f"| {v['subset']} | {v['active_n']} | {v['native_core']} | {v['graph_priv']} | {v['euclid_priv']} | {v['packet_priv']} |\n")

    f.write("\n## Compact Results\n\n")
    f.write("AUC values are means over rewired replicates.\n\n")
    f.write("| subset | active N | native core | identity address | identity weave | identity hybrid | fresh address | fresh weave | fresh hybrid | fresh/native Jaccard | native-core retention |\n")
    f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    for c in compact_rows:
        def fmt(v):
            return f"{v:.3f}" if isinstance(v, float) and not math.isnan(v) else str(v)
        f.write(f"| {c['subset']} | {c['active_n']} | {c['native_core']} | {fmt(c['identity_address_auc'])} | {fmt(c['identity_weave_auc'])} | {fmt(c['identity_hybrid_auc'])} | {fmt(c['fresh_address_auc'])} | {fmt(c['fresh_weave_auc'])} | {fmt(c['fresh_hybrid_auc'])} | {fmt(c['fresh_native_jaccard'])} | {fmt(c['native_core_retention'])} |\n")

    f.write("\n## Interpretation\n\n")
    f.write("This full-strength 5E audit provides apples-to-apples comparison with AB v0.8.\n\n")
    f.write("Key questions:\n")
    f.write("1. Does Penrose remain weave-led for identity persistence (not address-led like AB)?\n")
    f.write("2. Does fresh reconstruction remain weave-led on both substrates?\n")
    f.write("3. Is the interior subset well-behaved (enough positives for reliable CV)?\n\n")
    f.write("## Cautions\n\n")
    f.write("- This is a classical substrate diagnostic, not a quantum code simulation.\n")
    f.write("- The interior subset uses radial distance from center; a boundary-distance metric might be better.\n")

elapsed = time.time() - t0
print(f"\n[{time.strftime('%H:%M:%S')}] DONE in {elapsed/60:.1f} minutes", flush=True)
print(f"Results saved to: {OUT_PREFIX}_*.csv", flush=True)
