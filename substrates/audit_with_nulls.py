#!/usr/bin/env python3
"""
Fresh-reconstruction audit with the missing null controls.

The v3 audit reports that fresh reconstruction is "weave-led" (AUC ~0.89-0.91)
on both substrates, but runs no null. This script reproduces that number and
then asks the three questions that decide whether it means anything:

  N1  geometry-free control  - same pipeline on a degree-matched configuration
                               model with no tiling ancestry. If the AUC holds
                               up, the number is not about the substrate.
  N2  algebraic leakage      - how much of each top-quartile label component is
                               recoverable from a single weave feature. On a
                               rewired graph packet retention reduces to
                               2/(1 + mean neighbour degree), which is
                               WEAVE_COLS[1].
  N3  leakage ablation       - refit with the degree-family weave features
                               removed, to see what survives.

The identity audit is rerun alongside as a control: it should be unaffected,
since its labels come from the native graph and its address features are
invariant under rewiring.
"""

import argparse
import csv
import math
import os
import random
import time

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KDTree
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

WEAVE_COLS = ["g_degree", "g_neighbor_degree_mean", "g_local_clustering", "g_hop2_size"]
DEGREE_FAMILY = ["g_degree", "g_neighbor_degree_mean", "g_hop2_size"]
ADDRESS_COLS = ["perp_x", "perp_y", "perp_r", "k_sum_mod5"]


# ---------------------------------------------------------------- pipeline
# These reproduce the v3 audit's definitions verbatim so the comparison is fair.

def read_csv_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_edges(path):
    edges = []
    for r in read_csv_rows(path):
        u = int(r.get("source_index", r.get("source", 0)))
        v = int(r.get("target_index", r.get("target", 0)))
        if u != v:
            edges.append((min(u, v), max(u, v)))
    return sorted(set(edges))


def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def graph_features(adj):
    n = len(adj)
    deg = np.array([len(adj[i]) for i in range(n)], dtype=float)
    neighbor_mean = np.zeros(n)
    clustering = np.zeros(n)
    hop2 = np.zeros(n)
    for i in range(n):
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
            links = sum(1 for a in range(k) for b in nbrs[a + 1:] if b in adj[nbrs[a]])
            clustering[i] = 2.0 * links / (k * (k - 1))
    return {"g_degree": deg, "g_neighbor_degree_mean": neighbor_mean,
            "g_local_clustering": clustering, "g_hop2_size": hop2}


def retention(adj, deg, seed):
    S = set(seed)
    if not S:
        return 0.0
    total = sum(deg[i] for i in S)
    internal = sum(1 for i in S for j in adj[i] if j in S)
    return internal / total if total else 0.0


def graph_ball_radius2(adj, i):
    S = {i}
    S.update(adj[i])
    for j in list(adj[i]):
        S.update(adj[j])
    return S


def top_quartile_strict(scores, active):
    cutoff = float(np.quantile(scores[active], 0.75))
    return set(np.asarray(active)[scores[active] > cutoff].tolist())


def shared_core_labels(adj, active, euclid_seeds):
    """The v3 label: intersection of three top-quartile retention sets."""
    n = len(adj)
    deg = np.array([len(adj[i]) for i in range(n)], dtype=float)
    graph_s = np.zeros(n)
    euclid_s = np.zeros(n)
    packet_s = np.zeros(n)
    for i in active:
        graph_s[i] = retention(adj, deg, graph_ball_radius2(adj, i))
        euclid_s[i] = retention(adj, deg, euclid_seeds.get(i, [i]))
        packet_s[i] = retention(adj, deg, {i} | adj[i])
    parts = {
        "graph": top_quartile_strict(graph_s, active),
        "euclid": top_quartile_strict(euclid_s, active),
        "packet": top_quartile_strict(packet_s, active),
    }
    shared = parts["graph"] & parts["euclid"] & parts["packet"]
    y = np.array([1 if i in shared else 0 for i in active], dtype=int)
    return y, shared, parts, {"graph": graph_s, "euclid": euclid_s, "packet": packet_s}


def double_edge_rewire(edges, attempts, seed):
    rr = random.Random(seed)
    edge_list = list(edges)
    edge_set = set(edge_list)
    accepted = 0
    for _ in range(attempts):
        i, j = rr.sample(range(len(edge_list)), 2)
        a, b = edge_list[i]
        c, d = edge_list[j]
        if len({a, b, c, d}) < 4:
            continue
        if rr.random() < 0.5:
            e1, e2 = (min(a, d), max(a, d)), (min(c, b), max(c, b))
        else:
            e1, e2 = (min(a, c), max(a, c)), (min(b, d), max(b, d))
        if e1 == e2 or e1 in edge_set or e2 in edge_set:
            continue
        edge_set.discard(edge_list[i])
        edge_set.discard(edge_list[j])
        edge_set.add(e1)
        edge_set.add(e2)
        edge_list[i], edge_list[j] = e1, e2
        accepted += 1
    return sorted(edge_set), accepted


def configuration_model(degrees, seed):
    """A graph with this degree sequence and no geometric ancestry whatsoever."""
    rng = np.random.default_rng(seed)
    stubs = np.repeat(np.arange(len(degrees)), degrees.astype(int))
    rng.shuffle(stubs)
    edges = set()
    for a, b in zip(stubs[::2], stubs[1::2]):
        if a != b:
            edges.add((int(min(a, b)), int(max(a, b))))
    return sorted(edges)


def cv_auc(X, y, seed):
    y = np.asarray(y, dtype=int)
    pos, neg = int(y.sum()), int((1 - y).sum())
    if pos < 3 or neg < 3:
        return float("nan")
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    probs = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        m = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=700, class_weight="balanced",
                               solver="liblinear", random_state=seed))
        m.fit(X[tr], y[tr])
        probs[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, probs))


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--lift", default=os.path.join(here, "ab_lift.csv"))
    ap.add_argument("--edges", default=os.path.join(here, "ab_edges.csv"))
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--rewire-multiple", type=float, default=5.0)
    ap.add_argument("--interior", type=float, default=0.75)
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--out", default=os.path.join(here, "null_audit_results.csv"))
    args = ap.parse_args()

    t0 = time.time()
    rows = read_csv_rows(args.lift)
    edges = read_edges(args.edges)
    n = len(rows)
    print(f"substrate: {n} vertices, {len(edges)} edges", flush=True)

    pts = np.array([[float(r["x"]), float(r["y"])] for r in rows])
    address = np.array([[float(r[c]) for c in ADDRESS_COLS] for r in rows])

    centre = pts.mean(axis=0)
    radial = np.linalg.norm(pts - centre, axis=1)
    active = np.sort(np.argsort(radial)[:int(round(args.interior * n))]).tolist()
    print(f"interior-{int(args.interior*100)}%: {len(active)} vertices", flush=True)

    med_edge = float(np.median([np.linalg.norm(pts[u] - pts[v]) for u, v in edges]))
    tree = KDTree(pts)
    q = tree.query_radius(pts[active], r=3.0 * med_edge)
    euclid_seeds = {active[k]: q[k].tolist() for k in range(len(active))}

    adj_native = adjacency(n, edges)
    y_identity, native_set, _, _ = shared_core_labels(adj_native, active, euclid_seeds)
    print(f"native shared core: {int(y_identity.sum())} positives", flush=True)

    A = address[active]
    attempts = int(args.rewire_multiple * len(edges))
    degrees = np.array([len(adj_native[i]) for i in range(n)], dtype=float)

    results = []

    def record(**kw):
        results.append(kw)
        print("  " + "  ".join(f"{k}={v}" for k, v in kw.items()), flush=True)

    # Identity audit control: address features, invariant under rewiring.
    record(arm="identity", graph="native", features="address",
           auc=round(cv_auc(A, y_identity, args.seed), 4), rep=-1)

    for rep in range(args.reps):
        print(f"\n--- replicate {rep} ---", flush=True)

        # ---- the real substrate, rewired (what v3 does)
        redges, acc = double_edge_rewire(edges, attempts, args.seed + rep)
        adj_r = adjacency(n, redges)
        gf = graph_features(adj_r)
        W = np.column_stack([gf[c][active] for c in WEAVE_COLS])
        y_fresh, fresh_set, parts, scores = shared_core_labels(adj_r, active, euclid_seeds)

        record(arm="identity", graph="rewired_tiling", features="weave",
               auc=round(cv_auc(W, y_identity, args.seed + rep), 4), rep=rep)
        record(arm="identity", graph="rewired_tiling", features="hybrid",
               auc=round(cv_auc(np.column_stack([A, W]), y_identity, args.seed + rep), 4), rep=rep)
        record(arm="fresh", graph="rewired_tiling", features="weave",
               auc=round(cv_auc(W, y_fresh, args.seed + rep), 4), rep=rep,
               positives=int(y_fresh.sum()))
        record(arm="fresh", graph="rewired_tiling", features="address",
               auc=round(cv_auc(A, y_fresh, args.seed + rep), 4), rep=rep,
               positives=int(y_fresh.sum()))

        # ---- N2: algebraic leakage of the label into a single weave feature
        nbr = gf["g_neighbor_degree_mean"][active]
        packet_lab = np.array([1 if i in parts["packet"] else 0 for i in active])
        graph_lab = np.array([1 if i in parts["graph"] else 0 for i in active])
        record(arm="leakage", graph="rewired_tiling", features="nbr_degree_mean_only",
               target="packet_priv", auc=round(roc_auc_score(packet_lab, -nbr), 4), rep=rep)
        record(arm="leakage", graph="rewired_tiling", features="hop2_only",
               target="graph_priv",
               auc=round(roc_auc_score(graph_lab, -gf["g_hop2_size"][active]), 4), rep=rep)

        # ---- N3: ablation, weave minus the degree family
        keep = [WEAVE_COLS.index(c) for c in WEAVE_COLS if c not in DEGREE_FAMILY]
        record(arm="fresh", graph="rewired_tiling", features="weave_minus_degree_family",
               auc=round(cv_auc(W[:, keep], y_fresh, args.seed + rep), 4), rep=rep)

        # ---- N4: the same ablation on the identity audit. Degree-preserving
        # rewiring leaves the degree family untouched by construction, so a
        # "weave survives scrambling" result may just be the degree sequence.
        record(arm="identity", graph="rewired_tiling", features="weave_minus_degree_family",
               auc=round(cv_auc(W[:, keep], y_identity, args.seed + rep), 4), rep=rep)
        record(arm="identity", graph="rewired_tiling", features="degree_family_only",
               auc=round(cv_auc(W[:, [WEAVE_COLS.index(c) for c in DEGREE_FAMILY]],
                                y_identity, args.seed + rep), 4), rep=rep)

        # ---- N1: geometry-free control, same degree sequence, no tiling ancestry
        cedges = configuration_model(degrees, args.seed + 5000 + rep)
        adj_c = adjacency(n, cedges)
        gf_c = graph_features(adj_c)
        W_c = np.column_stack([gf_c[c][active] for c in WEAVE_COLS])
        y_c, _, _, _ = shared_core_labels(adj_c, active, euclid_seeds)
        record(arm="fresh", graph="config_model_no_geometry", features="weave",
               auc=round(cv_auc(W_c, y_c, args.seed + rep), 4), rep=rep,
               positives=int(y_c.sum()))

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        cols = sorted({k for r in results for k in r})
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(results)

    print(f"\n=== summary (mean AUC over {args.reps} replicates) ===", flush=True)
    seen = {}
    for r in results:
        key = (r["arm"], r["graph"], r["features"])
        seen.setdefault(key, []).append(r["auc"])
    for (arm, graph, feats), vals in seen.items():
        vals = [v for v in vals if not math.isnan(v)]
        print(f"{arm:9s} {graph:26s} {feats:28s} {np.mean(vals):.4f}", flush=True)
    print(f"\nwrote {args.out}   ({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
