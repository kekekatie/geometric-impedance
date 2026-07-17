#!/usr/bin/env python3
"""
Geometry-matched controls for the error-transport experiment (construction +
validation only; no walkers, no transport).

  * C -- oblique-Z^2 periodic control (sec.4.C): a crystalline 4-regular grid on
    the SAME real period cell {P_a, P_b} as the native torus, sized to match the
    native node count and chosen to minimise grid-cell anisotropy. Exact winding
    labels; mean degree exactly 4 (matching the rhombus-tiling mean by Euler).
    The primary A/B contrast: periodic vs aperiodic, geometry held; the residual
    is degree *variance* (grid is 4-regular, aperiodic has a degree distribution).

  * D -- bounded-length local rewire (sec.4.D): degree-preserving double-edge
    swaps on the native torus restricted to a length cutoff. A construction-only
    cutoff ladder {1.25,1.5,1.75,2.0}; pick the smallest cutoff meeting the
    scrambling target (>=80% edge replacement) while preserving degree sequence,
    connectedness, no dup/self edges, unambiguous winding, and no edge spanning
    more than one torus cell. Diagnostics only -- never transport outcomes.
"""

import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from collections import deque, Counter
from seamless_torus import SeamlessTorus

HERE = Path(__file__).parent


# ======================================================================
#  C -- oblique-Z^2 periodic control
# ======================================================================
def build_oblique(P_a, P_b, target_n):
    """Oblique periodic grid r_ij = (i/m)P_a + (j/n)P_b on the cell {P_a,P_b},
    4-neighbour periodic. m,n minimise anisotropy |P_a|/m vs |P_b|/n subject to
    m*n ~ target_n. Returns node positions, directed winding-labelled edges."""
    la, lb = np.linalg.norm(P_a), np.linalg.norm(P_b)
    # minimise grid-cell anisotropy |P_a|/m vs |P_b|/n (primary) subject to
    # m*n ~ target_n within 5% (secondary). Isotropic target: m ~ sqrt(N|P_a|/|P_b|).
    best = None
    m0 = max(2, int(round(np.sqrt(target_n * la / lb))))
    for m in range(max(2, m0 - 6), m0 + 7):
        for n in (round(target_n / m), int(target_n // m), int(np.ceil(target_n / m))):
            n = max(2, int(n))
            if abs(m * n - target_n) > 0.06 * target_n:
                continue
            aniso = abs((la / m) - (lb / n))
            score = (round(aniso, 4), abs(m * n - target_n))
            if best is None or score < best[0]:
                best = (score, m, n)
    _, m, n = best
    pos = {}
    idx = {}
    for i in range(m):
        for j in range(n):
            idx[(i, j)] = len(idx)
            pos[(i, j)] = (i / m) * P_a + (j / n) * P_b
    directed = []
    for i in range(m):
        for j in range(n):
            u = idx[(i, j)]
            # +i neighbour (wrap in a -> winding (1,0) when i+1==m)
            for di, dj, wi, wj in [(1, 0, None, 0), (-1, 0, None, 0),
                                   (0, 1, 0, None), (0, -1, 0, None)]:
                ii = i + di; jj = j + dj
                w = np.array([0, 0])
                if ii >= m:
                    ii -= m; w[0] += 1
                elif ii < 0:
                    ii += m; w[0] -= 1
                if jj >= n:
                    jj -= n; w[1] += 1
                elif jj < 0:
                    jj += n; w[1] -= 1
                v = idx[(ii, jj)]
                directed.append((u, v, tuple(w.tolist())))
    node_par = np.array([pos[k] for k in sorted(idx, key=lambda k: idx[k])])
    return dict(m=m, n=n, n_nodes=len(idx), node_par=node_par,
                directed=directed, P_a=P_a, P_b=P_b, la=la, lb=lb)


def _validate_graph(n, directed, node_par, P_a, P_b, expected_mean_deg=None,
                    max_edge_len=None):
    """Shared validation battery (winding integrity + graph integrity)."""
    res = {"n_nodes": n}
    # antisymmetry / self-loops / dupes
    dset = {}
    self_loops = 0; dup = 0
    for u, v, w in directed:
        if u == v:
            self_loops += 1
        key = (u, v, tuple(w))
        if key in dset:
            dup += 1
        dset[key] = True
    antisym = 0
    for (u, v, w) in dset:
        if (v, u, tuple((-np.array(w)).tolist())) not in dset:
            antisym += 1
    res["self_loops"] = self_loops
    res["duplicate_directed_edges"] = dup
    res["reverse_winding_antisymmetry"] = bool(antisym == 0)
    res["antisymmetry_violations"] = antisym
    # degree
    deg = Counter()
    seen = set()
    for u, v, w in directed:
        k = (min(u, v), max(u, v), tuple(sorted((tuple(w),
             tuple((-np.array(w)).tolist())))))
        if k in seen:
            continue
        seen.add(k); deg[u] += 1; deg[v] += 1
    degv = np.array([deg[i] for i in range(n)])
    res["mean_degree"] = round(float(degv.mean()), 4)
    res["degree_hist"] = dict(sorted(Counter(degv.tolist()).items()))
    # connectivity
    adj = [[] for _ in range(n)]
    for u, v, w in directed:
        adj[u].append(v)
    vis = np.zeros(n, bool); dq = deque([0]); vis[0] = True; c = 1
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if not vis[v]:
                vis[v] = True; c += 1; dq.append(v)
    res["connected"] = bool(c == n)
    # fundamental-cycle winding closure (both generators appear)
    lift = {0: np.zeros(2, int)}; dq = deque([0])
    dmap = {}
    for u, v, w in directed:
        dmap.setdefault(u, []).append((v, np.array(w)))
    while dq:
        u = dq.popleft()
        for v, w in dmap.get(u, []):
            if v not in lift:
                lift[v] = lift[u] + w; dq.append(v)
    cyc = set()
    for u, v, w in directed:
        if u in lift and v in lift:
            h = tuple((lift[u] + np.array(w) - lift[v]).tolist())
            if h != (0, 0):
                cyc.add(h)
    res["closure_both_generators"] = bool(
        any(a != 0 for a, b in cyc) and any(b != 0 for a, b in cyc))
    res["distinct_cycle_windings"] = len(cyc)
    # winding well-defined & bounded: each edge's physical displacement matches
    # node_par[v] + w.(P_a,P_b) - node_par[u]; report the max edge length and
    # that no edge spans more than one cell (|w| entries in {-1,0,1}).
    maxlen = 0.0; multicell = 0
    for u, v, w in directed:
        disp = node_par[v] + w[0] * P_a + w[1] * P_b - node_par[u]
        maxlen = max(maxlen, float(np.linalg.norm(disp)))
        if max(abs(w[0]), abs(w[1])) > 1:
            multicell += 1
    res["max_edge_length"] = round(maxlen, 4)
    res["edges_spanning_multiple_cells"] = multicell
    ok = (res["reverse_winding_antisymmetry"] and self_loops == 0 and dup == 0
          and res["connected"] and res["closure_both_generators"]
          and multicell == 0)
    if expected_mean_deg is not None:
        ok = ok and abs(res["mean_degree"] - expected_mean_deg) < 1e-9
    if max_edge_len is not None:
        ok = ok and res["max_edge_length"] <= max_edge_len + 1e-9
    res["GATE_PASS"] = bool(ok)
    return res


def validate_oblique(substrate, order_index, verbose=True):
    T = SeamlessTorus(substrate, order_index)
    g = build_oblique(T.P_a, T.P_b, T.n)
    res = _validate_graph(g["n_nodes"], g["directed"], g["node_par"],
                          T.P_a, T.P_b, expected_mean_deg=4.0)
    res.update(substrate=substrate, order=T.order, convergent=T.convergent,
               control="oblique_Z2", native_n=T.n, grid_m=g["m"], grid_n=g["n"],
               grid_cell_a=round(g["la"] / g["m"], 4),
               grid_cell_b=round(g["lb"] / g["n"], 4),
               anisotropy=round(abs(g["la"] / g["m"] - g["lb"] / g["n"]), 4))
    if verbose:
        print(f"\n=== oblique-Z2 control  {substrate} order {res['order']} "
              f"({res['convergent']}) ===")
        print(f"  native N={T.n}  ->  grid {g['m']}x{g['n']}={g['n_nodes']}  "
              f"cell steps a={res['grid_cell_a']} b={res['grid_cell_b']} "
              f"(anisotropy {res['anisotropy']})")
        for name, key in [("reverse-winding antisymmetry",
                           "reverse_winding_antisymmetry"),
                          ("connected", "connected"),
                          ("closure both generators", "closure_both_generators"),
                          ("mean degree == 4", None)]:
            if key:
                ok = res[key]; d = res.get("antisymmetry_violations", "")
            else:
                ok = abs(res["mean_degree"] - 4.0) < 1e-9; d = res["mean_degree"]
            print(f"  [{'PASS' if ok else 'FAIL'}] {name} ({d})")
        print(f"  no multi-cell edges: {res['edges_spanning_multiple_cells']==0} "
              f"| GATE {'PASS' if res['GATE_PASS'] else 'FAIL'}")
    return res


# ======================================================================
#  D -- bounded-length local rewire (cutoff ladder, construction diagnostics)
# ======================================================================
_OFFSETS = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]


def _edge_wind_len(node_par, P_a, P_b, u, v):
    """Shortest torus displacement u->v: winding w in {-1,0,1}^2 minimising the
    physical edge length. Returns (w, length)."""
    d0 = node_par[v] - node_par[u]
    best_w = None; best_l = 1e18
    for wa, wb in _OFFSETS:
        d = d0 + wa * P_a + wb * P_b
        L = float(np.hypot(d[0], d[1]))
        if L < best_l:
            best_l = L; best_w = (wa, wb)
    return best_w, best_l


def build_rewire(T, cutoff, target_replace=0.8, seed=0, max_passes=400):
    """Degree-preserving double-edge swaps on the native seamless torus, each new
    edge required to be <= cutoff (native edge length = 1). Winding recomputed as
    the shortest torus representative (kept within one cell). Construction only."""
    rng = np.random.default_rng(seed)
    node_par = T.node_par; P_a, P_b = T.P_a, T.P_b
    # native canonical undirected edges (u<v, winding u->v)
    edges = []
    eset = set()          # (u,v,w) canonical
    pairset = set()       # frozenset{u,v}
    for u, v, w, dp in T.directed:
        a, b = (u, v) if u < v else (v, u)
        wab = tuple(w) if u < v else tuple((-np.array(w)).tolist())
        key = (a, b, wab)
        if key in eset:
            continue
        eset.add(key); edges.append([a, b, wab]); pairset.add(frozenset((a, b)))
    E = len(edges)
    native_set = set(eset)
    n_swaps = 0
    attempts = 0
    stall = 0
    stall_limit = 40 * E          # converged: no accepted swap in a long while
    max_attempts = max_passes * E
    while attempts < max_attempts and stall < stall_limit:
        attempts += 1
        stall += 1
        i, j = rng.integers(0, E), rng.integers(0, E)
        if i == j:
            continue
        a, b, _ = edges[i]; c, d, _ = edges[j]
        if len({a, b, c, d}) < 4:
            continue
        # two possible reconnections; pick one at random
        if rng.random() < 0.5:
            n1, n2 = (a, d), (c, b)
        else:
            n1, n2 = (a, c), (b, d)
        (u1, v1), (u2, v2) = n1, n2
        if frozenset((u1, v1)) in pairset or frozenset((u2, v2)) in pairset:
            continue
        w1, L1 = _edge_wind_len(node_par, P_a, P_b, u1, v1)
        w2, L2 = _edge_wind_len(node_par, P_a, P_b, u2, v2)
        if L1 > cutoff or L2 > cutoff:
            continue
        # commit: remove old, add new (canonicalise)
        pairset.discard(frozenset((a, b))); pairset.discard(frozenset((c, d)))
        pairset.add(frozenset((u1, v1))); pairset.add(frozenset((u2, v2)))

        def canon(u, v, w):
            return (u, v, w) if u < v else (v, u, tuple((-np.array(w)).tolist()))
        edges[i] = list(canon(u1, v1, w1))
        edges[j] = list(canon(u2, v2, w2))
        n_swaps += 1
        stall = 0
        if n_swaps % E == 0:
            cur = set((e[0], e[1], e[2]) for e in edges)
            repl = 1.0 - len(cur & native_set) / E
            if repl >= target_replace:
                break
    cur = set((e[0], e[1], e[2]) for e in edges)
    replaced = 1.0 - len(cur & native_set) / E
    directed = []
    for a, b, w in edges:
        directed.append((a, b, tuple(w)))
        directed.append((b, a, tuple((-np.array(w)).tolist())))
    return dict(directed=directed, replaced=replaced, n_swaps=n_swaps,
                E=E, cutoff=cutoff)


def validate_rewire(substrate, order_index, verbose=True):
    T = SeamlessTorus(substrate, order_index)
    native_deg = T.degrees()
    ladder = [1.25, 1.5, 1.75, 2.0]
    rows = []
    chosen = None
    for cutoff in ladder:
        g = build_rewire(T, cutoff, seed=12345)
        res = _validate_graph(T.n, g["directed"], T.node_par, T.P_a, T.P_b,
                              max_edge_len=cutoff)
        # degree sequence preserved?
        deg = Counter()
        seen = set()
        for u, v, w in g["directed"]:
            k = (min(u, v), max(u, v), tuple(sorted((tuple(w),
                 tuple((-np.array(w)).tolist())))))
            if k in seen:
                continue
            seen.add(k); deg[u] += 1; deg[v] += 1
        degv = np.array([deg[i] for i in range(T.n)])
        deg_preserved = bool(np.array_equal(np.sort(degv), np.sort(native_deg)))
        row = dict(cutoff=cutoff, replaced=round(g["replaced"], 4),
                   n_swaps=g["n_swaps"],
                   degree_seq_preserved=deg_preserved,
                   connected=res["connected"],
                   antisymmetry=res["reverse_winding_antisymmetry"],
                   no_self_dup=(res["self_loops"] == 0 and
                                res["duplicate_directed_edges"] == 0),
                   multicell=res["edges_spanning_multiple_cells"],
                   max_len=res["max_edge_length"],
                   closure=res["closure_both_generators"])
        ok = (row["replaced"] >= 0.80 and deg_preserved and res["connected"]
              and res["reverse_winding_antisymmetry"] and row["no_self_dup"]
              and res["edges_spanning_multiple_cells"] == 0
              and res["closure_both_generators"])
        row["meets_criteria"] = bool(ok)
        rows.append(row)
        if ok and chosen is None:
            chosen = cutoff
    out = dict(substrate=substrate, order=T.order, convergent=T.convergent,
               control="bounded_local_rewire", native_n=T.n,
               chosen_cutoff=chosen, ladder=rows)
    if verbose:
        print(f"\n=== bounded-local-rewire  {substrate} order {T.order} "
              f"({T.convergent}) ===  N={T.n}")
        print("  cutoff  replaced  swaps  degseq  conn  antisym  self/dup  "
              "multicell  maxlen  -> meets")
        for r in rows:
            print(f"   {r['cutoff']:<5} {r['replaced']:>7.1%} {r['n_swaps']:>6} "
                  f"  {str(r['degree_seq_preserved']):>5} "
                  f"{str(r['connected']):>5} {str(r['antisymmetry']):>6} "
                  f"  {str(r['no_self_dup']):>5}   {r['multicell']:>6}   "
                  f"{r['max_len']:>5}  -> {r['meets_criteria']}")
        print(f"  chosen (smallest meeting >=80% + all constraints): {chosen}")
    return out


if __name__ == "__main__":
    out = {"oblique_Z2": [], "bounded_local_rewire": []}
    for sub, oi in [("ammann_beenker", 2), ("ammann_beenker", 3),
                    ("penrose", 2), ("penrose", 3)]:
        out["oblique_Z2"].append(validate_oblique(sub, oi))
    for sub, oi in [("ammann_beenker", 2), ("penrose", 2)]:
        out["bounded_local_rewire"].append(validate_rewire(sub, oi))
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "controls_validation.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n-> results/controls_validation.json")
