#!/usr/bin/env python3
"""
Runtime-only pilot: choose one global cap kappa in S_max = kappa*N.

SEALED RULES: see PILOT_SEAL.md. This script is BLIND to outcomes by construction —
it tracks only the two defects' NODE positions and the annihilation step (a hitting
time). It never accumulates lifts or winding, so P_heal / P_logical cannot be and are
not computed. Output is restricted to cap-selection diagnostics:
  kappa | max censoring across eligible largest graphs | per-graph censoring | runtime.

Pilot trajectories are permanently excluded from all inference (dedicated seeds).
"""

import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from seamless_torus import SeamlessTorus
from controls import build_oblique
from matched_control import build_matched

HERE = Path(__file__).parent
PILOT_MASTER_SEED = 20250718
KAPPA_LADDER = [5, 10, 20, 40, 80]
PILOT_TRIALS = 4000


def _csr(n, directed3):
    """CSR incident-neighbour structure from 3-tuple directed edges (u,v,w)."""
    outdeg = np.zeros(n, dtype=np.int64)
    for u, v, w in directed3:
        outdeg[u] += 1
    offsets = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(outdeg, out=offsets[1:])
    nbr = np.zeros(offsets[-1], dtype=np.int64)
    fill = offsets[:-1].copy()
    for u, v, w in directed3:
        nbr[fill[u]] = v; fill[u] += 1
    return offsets, nbr


def _nonseam_edges(directed3):
    """Canonical undirected native edges with winding (0,0) (primary start set)."""
    seen = set(); out = []
    for u, v, w in directed3:
        if tuple(w) != (0, 0):
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in seen:
            continue
        seen.add((a, b)); out.append((a, b))
    return np.array(out, dtype=np.int64)


def _directed3(graph):
    """Normalise a graph's directed edges to 3-tuples (u,v,w)."""
    if hasattr(graph, "directed"):          # SeamlessTorus
        return [(u, v, tuple(w)) for (u, v, w, dp) in graph.directed], graph.n
    n = graph.get("n_nodes", graph.get("n"))
    return [(u, v, tuple(w)) for (u, v, w) in graph["directed"]], n


def run_walk(offsets, nbr, nA0, nB0, S_max, seed):
    """Vectorised unbiased double-defect walk. Returns annihilation step per trial
    (S_max+1 == censored). Tracks NODES only — no lifts, no winding, no outcome."""
    rng = np.random.default_rng(seed)
    nA = nA0.copy(); nB = nB0.copy()
    M = len(nA)
    ann = np.full(M, S_max + 1, dtype=np.int64)
    idx = np.arange(M)
    for step in range(1, S_max + 1):
        k = nA.shape[0]
        if k == 0:
            break
        mover = rng.random(k) < 0.5
        cur = np.where(mover, nA, nB)
        deg = offsets[cur + 1] - offsets[cur]
        pick = offsets[cur] + (rng.random(k) * deg).astype(np.int64)
        newnode = nbr[pick]
        nA = np.where(mover, newnode, nA)
        nB = np.where(mover, nB, newnode)
        hit = nA == nB
        if hit.any():
            ann[idx[hit]] = step
            keep = ~hit
            nA = nA[keep]; nB = nB[keep]; idx = idx[keep]
    return ann


def pilot_graph(graph_id, name, graph, seed):
    directed3, n = _directed3(graph)
    offsets, nbr = _csr(n, directed3)
    edges = _nonseam_edges(directed3)
    ss = np.random.SeedSequence([PILOT_MASTER_SEED, graph_id])
    rng = np.random.default_rng(ss)
    pick = rng.integers(0, len(edges), size=PILOT_TRIALS)
    coin = rng.random(PILOT_TRIALS) < 0.5
    e = edges[pick]
    nA0 = np.where(coin, e[:, 0], e[:, 1])
    nB0 = np.where(coin, e[:, 1], e[:, 0])
    S_max = KAPPA_LADDER[-1] * n
    t0 = time.time()
    ann = run_walk(offsets, nbr, nA0, nB0, S_max,
                   seed=ss.spawn(1)[0])
    rt = time.time() - t0
    cens = {k: float(np.mean(ann > k * n)) for k in KAPPA_LADDER}
    med = int(np.median(ann[ann <= S_max])) if np.any(ann <= S_max) else -1
    return dict(graph_id=graph_id, name=name, n=n, trials=PILOT_TRIALS,
                censoring=cens, median_annih_step=med, runtime_s=round(rt, 2))


def main():
    print("Building eligible largest primary graphs (secondary rewires excluded)...")
    T_ab = SeamlessTorus("ammann_beenker", 3)      # phason-shear AB, N=1355
    T_pen = SeamlessTorus("penrose", 3)            # phason-shear Penrose, N=1700
    grid = build_oblique(T_pen.P_a, T_pen.P_b, T_pen.n)         # clean grid ~1694
    matched = build_matched("penrose", 3, seed=0)              # matched grid ~1694
    graphs = [
        (0, "phason_shear_AB", T_ab),
        (1, "phason_shear_Penrose", T_pen),
        (2, "clean_oblique_grid", grid),
        (3, "defect_matched_grid", matched),
    ]
    rows = []
    for gid, name, g in graphs:
        r = pilot_graph(gid, name, g, seed=gid)
        rows.append(r)
        print(f"  [{name}] N={r['n']} trials={r['trials']} "
              f"median-annih={r['median_annih_step']} runtime={r['runtime_s']}s")
    # worst-case (max) censoring across eligible graphs at each kappa
    maxcens = {k: max(r["censoring"][k] for r in rows) for k in KAPPA_LADDER}
    chosen = None
    for k in KAPPA_LADDER:
        if maxcens[k] <= 0.05:
            chosen = k
            break
    total_rt = round(sum(r["runtime_s"] for r in rows), 2)
    print("\n=== CAP-SELECTION TABLE (censoring only; no outcome breakdown) ===")
    print(f"  {'kappa':>6} | {'max censoring':>14} | per-graph censoring")
    for k in KAPPA_LADDER:
        pg = "  ".join(f"{r['name'][:14]}:{100*r['censoring'][k]:4.1f}%" for r in rows)
        star = "  <- SELECTED" if k == chosen else ""
        print(f"  {k:>6} | {100*maxcens[k]:13.2f}% | {pg}{star}")
    print(f"\n  total pilot runtime: {total_rt}s over {len(rows)} graphs "
          f"x {PILOT_TRIALS} trials")
    if chosen is None:
        print("\n  *** NO candidate kappa reaches <=5% censoring on the worst-case "
              "largest graph. STOP and return for review (do NOT improvise). ***")
    else:
        print(f"\n  SELECTED kappa = {chosen}  (smallest with worst-case "
              f"censoring <= 5%);  S_max = {chosen}*N")
    out = dict(pilot_master_seed=PILOT_MASTER_SEED, kappa_ladder=KAPPA_LADDER,
               pilot_trials=PILOT_TRIALS, graphs=rows,
               max_censoring=maxcens, chosen_kappa=chosen,
               selection_rule="smallest kappa with worst-case largest-graph "
                              "censoring <= 5%",
               pilot_data_excluded_from_inference=True)
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "pilot_cap_selection.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n-> results/pilot_cap_selection.json")
    return out


if __name__ == "__main__":
    main()
