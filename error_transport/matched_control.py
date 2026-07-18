#!/usr/bin/env python3
"""
Defect-matched crystalline control (GPT review, pre-pilot task).

Purpose: separate GENERIC WEAK DISORDER from ORGANISED quasicrystalline wiring.
Start from the clean oblique-Z^2 crystalline torus and inject a DISPERSED burden of
local defects chosen to approximately match each native phason-shear substrate's
  * node count N;
  * mean degree / edge-deficit (merged-face fraction);
  * degree histogram;
  * dispersed (non-wall) spatial distribution of defects;
  * connectivity and winding validity.
It deliberately does NOT imitate Penrose/AB motifs. The question it poses:

  does a ~5% burden of distributed weak disorder produce the same transport effect
  even WITHOUT quasicrystalline organisation?

Key design choice: a target degree is sampled from the native degree histogram and
assigned to grid nodes AT RANDOM -> defects are dispersed by construction (no wall,
no motif). Targets are realised by SHORT local edge edits (add/remove) with a length
cutoff, so every edge stays within one torus cell and winding stays well-defined.

Construction + validation only. No walkers, no transport, no pilot.
"""

import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from collections import deque, Counter
from scipy.spatial import cKDTree
from seamless_torus import SeamlessTorus
from controls import build_oblique, _edge_wind_len, _validate_graph

HERE = Path(__file__).parent


def _short_candidates(node_par, P_a, P_b, cutoff):
    """All node pairs within torus-distance cutoff, via a 3x3 tiling KDTree."""
    n = len(node_par)
    imgs = []
    tags = []
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            imgs.append(node_par + a * P_a + b * P_b)
            tags.append(np.full(n, 0))          # placeholder
    tiled = np.vstack(imgs)
    base_idx = np.tile(np.arange(n), 9)
    tree = cKDTree(node_par)
    tree2 = cKDTree(tiled)
    pairs = tree.query_ball_tree(tree2, r=cutoff)
    cand = {}
    for u in range(n):
        for ti in pairs[u]:
            v = base_idx[ti]
            if v == u:
                continue
            w, L = _edge_wind_len(node_par, P_a, P_b, u, v)
            if L <= cutoff and max(abs(w[0]), abs(w[1])) <= 1:
                cand.setdefault(u, {})[v] = (w, L)
    return cand


def build_matched(substrate, order_index, cutoff=2.2, seed=0, rounds=6,
                  spatial_ref=None, target_degrees=None):
    """Defect-matched crystalline control. Default: target degrees sampled from the
    native histogram and assigned to grid nodes AT RANDOM (dispersed weak disorder).
    If `spatial_ref` is a SeamlessTorus, each grid node instead inherits the degree
    of its spatially-nearest native node — transferring the native's DEFECT
    ARRANGEMENT (hyperuniform-like) onto the grid (the discrimination control)."""
    T = SeamlessTorus(substrate, order_index)
    native_deg = T.degrees()
    native_mean = float(native_deg.mean())
    g = build_oblique(T.P_a, T.P_b, T.n)
    n = g["n_nodes"]
    node_par = g["node_par"]
    P_a, P_b = T.P_a, T.P_b
    rng = np.random.default_rng(seed)

    # current edges: canonical (u<v) -> winding
    edges = {}
    for u, v, w in g["directed"]:
        a, b = (u, v) if u < v else (v, u)
        wab = tuple(w) if u < v else tuple((-np.array(w)).tolist())
        edges[(a, b)] = wab
    deg = np.array([0] * n)
    for (a, b) in edges:
        deg[a] += 1; deg[b] += 1

    # target degree sequence
    if target_degrees is not None:
        # explicit target (Stage-1C: blue-noise-placed defect sites + histogram)
        target = np.asarray(target_degrees, dtype=int).copy()
    elif spatial_ref is not None:
        # SPATIAL stamp: each grid node inherits the degree of the nearest native
        # node (torus-aware via 3x3 tiling) -> transfers the native defect ARRANGEMENT
        ref = spatial_ref
        ref_deg = ref.degrees()
        imgs = [ref.node_par + a * P_a + b * P_b
                for a in (-1, 0, 1) for b in (-1, 0, 1)]
        tiled = np.vstack(imgs)
        base = np.tile(np.arange(ref.n), 9)
        tree = cKDTree(tiled)
        _, ti = tree.query(node_par, k=1)
        target = ref_deg[base[ti]].astype(int)
    else:
        target = rng.choice(native_deg, size=n, replace=True).astype(int)
    # pin the mean/edge-deficit: adjust a few targets so sum(target) is even and
    # matches the native mean as closely as the grid allows. Skipped for explicit
    # target_degrees (Stage-1C) to preserve the blue-noise placement — the final
    # edge-count pin still enforces the native mean.
    want_sum = int(round(native_mean * n))
    want_sum -= want_sum % 2
    if target_degrees is None:
        while target.sum() > want_sum:
            i = rng.integers(n)
            if target[i] > 1:
                target[i] -= 1
        while target.sum() < want_sum:
            i = rng.integers(n)
            if target[i] < 8:
                target[i] += 1

    cand = _short_candidates(node_par, P_a, P_b, cutoff)

    def has_edge(u, v):
        return (min(u, v), max(u, v)) in edges

    for _ in range(rounds):
        order = rng.permutation(n)
        # removals for surplus nodes
        for u in order:
            while deg[u] > target[u]:
                nbrs = [v for v in range(n) if has_edge(u, v)]
                if not nbrs:
                    break
                # prefer removing toward a partner that is also surplus, keep >=1
                surplus_nbrs = [v for v in nbrs if deg[v] > target[v]]
                pick = surplus_nbrs if surplus_nbrs else nbrs
                v = pick[rng.integers(len(pick))]
                if deg[u] <= 1 or deg[v] <= 1:
                    break
                del edges[(min(u, v), max(u, v))]
                deg[u] -= 1; deg[v] -= 1
        # additions for deficit nodes (short candidates only). Prefer partners
        # that also want edges; fall back to any partner below the native cap so
        # high-degree targets can be realised.
        cap = int(native_deg.max())
        for u in order:
            if deg[u] >= target[u]:
                continue
            opts = [v for v in cand.get(u, {})
                    if deg[v] < cap and not has_edge(u, v)]
            opts.sort(key=lambda v: (deg[v] >= target[v], cand[u][v][1]))
            for v in opts:
                if deg[u] >= target[u]:
                    break
                w, L = cand[u][v]
                a, b = (u, v) if u < v else (v, u)
                edges[(a, b)] = w if u < v else tuple((-np.array(w)).tolist())
                deg[u] += 1; deg[v] += 1

    # connectivity repair: join components with the shortest available candidate
    def components():
        adj = {i: [] for i in range(n)}
        for (a, b) in edges:
            adj[a].append(b); adj[b].append(a)
        seen = np.zeros(n, bool); comps = []
        for s in range(n):
            if seen[s]:
                continue
            comp = []; dq = deque([s]); seen[s] = True
            while dq:
                x = dq.popleft(); comp.append(x)
                for y in adj[x]:
                    if not seen[y]:
                        seen[y] = True; dq.append(y)
            comps.append(comp)
        return comps

    comps = components()
    while len(comps) > 1:
        comps.sort(key=len)
        small = set(comps[0]); joined = False
        for u in comps[0]:
            for v in cand.get(u, {}):
                if v not in small and not has_edge(u, v):
                    w, L = cand[u][v]
                    a, b = (u, v) if u < v else (v, u)
                    edges[(a, b)] = w if u < v else tuple((-np.array(w)).tolist())
                    deg[u] += 1; deg[v] += 1; joined = True
                    break
            if joined:
                break
        if not joined:      # fall back: connect to nearest node in another comp
            u = comps[0][0]
            others = [x for x in range(n) if x not in small]
            d = np.linalg.norm(node_par[others] - node_par[u], axis=1)
            v = others[int(np.argmin(d))]
            w, L = _edge_wind_len(node_par, P_a, P_b, u, v)
            a, b = (u, v) if u < v else (v, u)
            edges[(a, b)] = w if u < v else tuple((-np.array(w)).tolist())
            deg[u] += 1; deg[v] += 1
        comps = components()

    # pin the edge count (hence mean degree / edge-deficit) to the native target,
    # preserving connectivity.
    cap = int(native_deg.max())
    want_edges = want_sum // 2

    def is_connected():
        adj = {i: [] for i in range(n)}
        for (a, b) in edges:
            adj[a].append(b); adj[b].append(a)
        seen = np.zeros(n, bool); dq = deque([0]); seen[0] = True; c = 1
        while dq:
            x = dq.popleft()
            for y in adj[x]:
                if not seen[y]:
                    seen[y] = True; c += 1; dq.append(y)
        return c == n

    # top-up: add short edges toward want_edges
    if len(edges) < want_edges:
        order = list(rng.permutation(n))
        for u in order:
            if len(edges) >= want_edges:
                break
            for v in sorted(cand.get(u, {}), key=lambda v: cand[u][v][1]):
                if len(edges) >= want_edges:
                    break
                if deg[u] < cap and deg[v] < cap and not (
                        (min(u, v), max(u, v)) in edges):
                    w, L = cand[u][v]
                    a, b = (u, v) if u < v else (v, u)
                    edges[(a, b)] = w if u < v else tuple((-np.array(w)).tolist())
                    deg[u] += 1; deg[v] += 1
    # trim: remove edges (between higher-degree nodes) toward want_edges,
    # keeping the graph connected
    if len(edges) > want_edges:
        keys = sorted(edges, key=lambda e: -(deg[e[0]] + deg[e[1]]))
        for (a, b) in keys:
            if len(edges) <= want_edges:
                break
            if deg[a] <= 2 or deg[b] <= 2:
                continue
            w = edges.pop((a, b))
            if is_connected():
                deg[a] -= 1; deg[b] -= 1
            else:
                edges[(a, b)] = w      # revert: was a bridge

    directed = []
    for (a, b), w in edges.items():
        directed.append((a, b, tuple(w)))
        directed.append((b, a, tuple((-np.array(w)).tolist())))
    return dict(T=T, n=n, node_par=node_par, directed=directed,
                native_deg=native_deg, target=target, P_a=P_a, P_b=P_b,
                grid_m=g["m"], grid_n=g["n"])


def _dispersion_chi2(node_par, defect_mask, P_a, P_b, G=6):
    """Coarse GxG binning of defect nodes over the cell; chi-square vs uniform.
    Low/moderate chi2 (p not tiny) => dispersed, no wall."""
    Mcell = np.array([P_a, P_b]).T
    frac = (np.linalg.inv(Mcell) @ node_par.T).T % 1.0
    bins = (np.clip((frac * G).astype(int), 0, G - 1))
    binid = bins[:, 0] * G + bins[:, 1]
    ndef = defect_mask.sum()
    if ndef == 0:
        return 0.0, 1.0
    counts = np.bincount(binid[defect_mask], minlength=G * G)
    exp = ndef / (G * G)
    chi2 = float(((counts - exp) ** 2 / exp).sum())
    # also the max single-bin share (a wall would spike one bin)
    max_share = float(counts.max() / ndef)
    return round(chi2, 2), round(max_share, 3)


def validate_matched(substrate, order_index, verbose=True, seed=0):
    m = build_matched(substrate, order_index, seed=seed)
    T = m["T"]; n = m["n"]; node_par = m["node_par"]
    res = _validate_graph(n, m["directed"], node_par, m["P_a"], m["P_b"])
    # degree stats
    deg = Counter(); seen = set()
    for u, v, w in m["directed"]:
        k = (min(u, v), max(u, v),
             tuple(sorted((tuple(w), tuple((-np.array(w)).tolist())))))
        if k in seen:
            continue
        seen.add(k); deg[u] += 1; deg[v] += 1
    degv = np.array([deg[i] for i in range(n)])
    native = m["native_deg"]

    def norm_hist(d, keys):
        c = Counter(d.tolist()); tot = len(d)
        return {k: round(c.get(k, 0) / tot, 4) for k in keys}
    keys = sorted(set(degv.tolist()) | set(native.tolist()))
    hm = norm_hist(degv, keys); hn = norm_hist(native, keys)
    tv = round(0.5 * sum(abs(hm[k] - hn[k]) for k in keys), 4)   # total variation
    # defect dispersion (defect = degree != 4)
    defect_mask = (degv != 4)
    chi2, max_share = _dispersion_chi2(node_par, defect_mask, m["P_a"], m["P_b"])
    nat_defect = (native != 4)
    nchi2, nmax = _dispersion_chi2(T.node_par, nat_defect, T.P_a, T.P_b)

    res.update(
        substrate=substrate, order=T.order, convergent=T.convergent,
        control="defect_matched_grid", grid_m=m["grid_m"], grid_n=m["grid_n"],
        native_n=T.n, matched_n=n,
        native_mean_degree=round(float(native.mean()), 4),
        matched_mean_degree=round(float(degv.mean()), 4),
        native_deg_hist=dict(sorted(Counter(native.tolist()).items())),
        matched_deg_hist=dict(sorted(Counter(degv.tolist()).items())),
        degree_hist_total_variation=tv,
        native_defect_frac=round(float(nat_defect.mean()), 4),
        matched_defect_frac=round(float(defect_mask.mean()), 4),
        matched_defect_dispersion_chi2=chi2,
        matched_defect_max_bin_share=max_share,
        native_defect_dispersion_chi2=nchi2,
        native_defect_max_bin_share=nmax,
    )
    ok = (res["reverse_winding_antisymmetry"] and res["self_loops"] == 0
          and res["duplicate_directed_edges"] == 0 and res["connected"]
          and res["closure_both_generators"]
          and res["edges_spanning_multiple_cells"] == 0
          and abs(res["matched_mean_degree"] - res["native_mean_degree"]) < 0.05
          and res["degree_hist_total_variation"] < 0.10
          and res["matched_defect_max_bin_share"] < 0.15)
    res["GATE_PASS"] = bool(ok)
    if verbose:
        print(f"\n=== defect-matched grid  {substrate} order {T.order} "
              f"({T.convergent}) ===  grid {m['grid_m']}x{m['grid_n']}={n} "
              f"(native {T.n})")
        print(f"  mean degree  matched {res['matched_mean_degree']}  vs native "
              f"{res['native_mean_degree']}   (deficit target)")
        print(f"  degree hist TV distance {tv}  (want < 0.10)")
        print(f"    native : {res['native_deg_hist']}")
        print(f"    matched: {res['matched_deg_hist']}")
        print(f"  defect frac  matched {res['matched_defect_frac']} vs native "
              f"{res['native_defect_frac']}")
        print(f"  dispersion (no wall): matched chi2 {chi2} max-bin {max_share} | "
              f"native chi2 {nchi2} max-bin {nmax}")
        print(f"  winding: antisym {res['reverse_winding_antisymmetry']} | "
              f"connected {res['connected']} | closure "
              f"{res['closure_both_generators']} | no multi-cell "
              f"{res['edges_spanning_multiple_cells']==0}")
        print(f"  ->  GATE {'PASS' if res['GATE_PASS'] else 'FAIL'}")
    return res


if __name__ == "__main__":
    out = {"defect_matched_grid": []}
    for sub, oi in [("ammann_beenker", 2), ("ammann_beenker", 3),
                    ("penrose", 2), ("penrose", 3)]:
        out["defect_matched_grid"].append(validate_matched(sub, oi))
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "matched_control_validation.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n-> results/matched_control_validation.json")
