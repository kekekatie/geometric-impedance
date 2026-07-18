#!/usr/bin/env python3
"""
Stage-1 preregistered transport inference (three-way approved; κ-seal = 10).

Runs the sealed unbiased double-defect walk on every Stage-1 graph family and size,
classifying each trial as HEAL / LOGICAL / CENSORED and reporting unconditional
P_heal, P_logical, P_censored with Wilson 95% intervals. Sparse/zero logical counts
are reported as exact counts + Wilson upper bounds (never "impossible").

Dynamics (sealed §3): each defect carries a lift = pos(node) + Wcell·cell, Wcell∈ℤ²
accumulated from edge windings. Move: pick one defect uniformly, cross a
uniformly-random incident native edge (unbiased). Annihilation (same node): homology
c = Wcell_A − Wcell_B; c=0→HEAL, c≠0→LOGICAL. S_max = 10·N reached → CENSORED.

Seeds: INFERENCE_MASTER_SEED, deterministic per-graph substreams — WHOLLY SEPARATE
from the pilot seeds. No exclusions, no replacement, no post-hoc tuning.
"""

import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from seamless_torus import SeamlessTorus
from controls import build_oblique, build_rewire
from matched_control import build_matched

HERE = Path(__file__).parent
INFERENCE_MASTER_SEED = 31415926           # distinct from PILOT_MASTER_SEED
KAPPA = 10                                 # sealed
INFERENCE_TRIALS = 20000


def _csr_wind(n, directed3):
    outdeg = np.zeros(n, dtype=np.int64)
    for u, v, w in directed3:
        outdeg[u] += 1
    offsets = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(outdeg, out=offsets[1:])
    nbr = np.zeros(offsets[-1], dtype=np.int64)
    wind = np.zeros((offsets[-1], 2), dtype=np.int64)
    fill = offsets[:-1].copy()
    for u, v, w in directed3:
        p = fill[u]; nbr[p] = v; wind[p] = w; fill[u] = p + 1
    return offsets, nbr, wind


def _edges_by_seam(directed3):
    seen = set(); nonseam = []; seam = []
    for u, v, w in directed3:
        a, b = (u, v) if u < v else (v, u)
        wab = tuple(w) if u < v else tuple((-np.array(w)).tolist())
        key = (a, b, wab)
        if key in seen:
            continue
        seen.add(key)
        (nonseam if wab == (0, 0) else seam).append((a, b, wab))
    return nonseam, seam


def _directed3(graph):
    if hasattr(graph, "directed"):
        return [(u, v, tuple(w)) for (u, v, w, dp) in graph.directed], graph.n
    n = graph.get("n_nodes", graph.get("n"))
    return [(u, v, tuple(w)) for (u, v, w) in graph["directed"]], n


def _wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def run_walk(offsets, nbr, wind, nA, nB, WA, WB, S_max, seed):
    """Winding-carrying double-defect walk. Returns (heal, logical, censored)."""
    rng = np.random.default_rng(seed)
    M = nA.shape[0]
    result = np.zeros(M, dtype=np.int8)         # 0 censored, 1 heal, 2 logical
    idx = np.arange(M)
    for _ in range(S_max):
        k = nA.shape[0]
        if k == 0:
            break
        mover = rng.random(k) < 0.5
        cur = np.where(mover, nA, nB)
        deg = offsets[cur + 1] - offsets[cur]
        pick = offsets[cur] + (rng.random(k) * deg).astype(np.int64)
        vn = nbr[pick]; vw = wind[pick]
        nA = np.where(mover, vn, nA)
        nB = np.where(mover, nB, vn)
        mv = mover[:, None]
        WA = WA + np.where(mv, vw, 0)
        WB = WB + np.where(mv, 0, vw)
        hit = nA == nB
        if hit.any():
            c = WA[hit] - WB[hit]
            heal = (c[:, 0] == 0) & (c[:, 1] == 0)
            result[idx[hit]] = np.where(heal, 1, 2)
            keep = ~hit
            nA = nA[keep]; nB = nB[keep]
            WA = WA[keep]; WB = WB[keep]; idx = idx[keep]
    n_heal = int((result == 1).sum())
    n_logical = int((result == 2).sum())
    n_cens = int((result == 0).sum())
    return n_heal, n_logical, n_cens


def infer_graph(graph, name, substrate, N_native, graph_id, start="nonseam"):
    directed3, n = _directed3(graph)
    offsets, nbr, wind = _csr_wind(n, directed3)
    nonseam, seam = _edges_by_seam(directed3)
    edgeset = nonseam if start == "nonseam" else seam
    if len(edgeset) == 0:
        return None
    E = np.array([(a, b) for (a, b, w) in edgeset], dtype=np.int64)
    W0 = np.array([w for (a, b, w) in edgeset], dtype=np.int64)
    ss = np.random.SeedSequence([INFERENCE_MASTER_SEED, graph_id,
                                 0 if start == "nonseam" else 1])
    rng = np.random.default_rng(ss)
    pick = rng.integers(0, len(edgeset), size=INFERENCE_TRIALS)
    coin = rng.random(INFERENCE_TRIALS) < 0.5
    a = E[pick, 0]; b = E[pick, 1]; w0 = W0[pick]
    nA = np.where(coin, a, b).astype(np.int64)
    nB = np.where(coin, b, a).astype(np.int64)
    WA = np.zeros((INFERENCE_TRIALS, 2), dtype=np.int64)
    # B starts at the far endpoint; its lift frame carries the start-edge winding
    WB = np.where(coin[:, None], w0, -w0).astype(np.int64)
    S_max = KAPPA * n
    t0 = time.time()
    heal, logical, cens = run_walk(offsets, nbr, wind, nA, nB, WA, WB,
                                   S_max, ss.spawn(1)[0])
    rt = round(time.time() - t0, 2)
    tot = heal + logical + cens
    p_heal, p_log, p_cen = heal / tot, logical / tot, cens / tot
    return dict(name=name, substrate=substrate, family=name.split("@")[0],
                N=n, N_native=N_native, start=start, trials=tot,
                heal=heal, logical=logical, censored=cens,
                P_heal=round(p_heal, 6), P_logical=round(p_log, 6),
                P_censored=round(p_cen, 6),
                P_logical_wilson=[round(x, 6) for x in _wilson(logical, tot)],
                P_heal_wilson=[round(x, 6) for x in _wilson(heal, tot)],
                P_censored_wilson=[round(x, 6) for x in _wilson(cens, tot)],
                runtime_s=rt)


def main():
    jobs = []
    # (substrate, order_index) natives with available sizes
    natives = [("ammann_beenker", 1), ("ammann_beenker", 2), ("ammann_beenker", 3),
               ("penrose", 1), ("penrose", 2), ("penrose", 3)]
    rows = []
    gid = 0
    manifest = []
    for substrate, oi in natives:
        T = SeamlessTorus(substrate, oi)
        Nn = T.n
        grid = build_oblique(T.P_a, T.P_b, Nn)
        matched = build_matched(substrate, oi, seed=0)
        rewire = build_rewire(T, 2.0, seed=777, max_passes=200)
        # rewire returns dict with 'directed' 3-tuples already
        fam = [
            (T, f"QC@{substrate}"),
            (grid, f"clean_grid@{substrate}"),
            (matched, f"matched_grid@{substrate}"),
            (dict(directed=rewire["directed"], n_nodes=T.n),
             f"rewire@{substrate}"),
        ]
        for g, name in fam:
            r = infer_graph(g, name, substrate, Nn, gid, start="nonseam")
            if r:
                rows.append(r)
                print(f"  [{name} N={r['N']}] heal={r['heal']} "
                      f"logical={r['logical']} cens={r['censored']} "
                      f"P_log={r['P_logical']:.5f} "
                      f"CI={r['P_logical_wilson']} ({r['runtime_s']}s)")
            manifest.append(dict(graph_id=gid, name=name, substrate=substrate,
                                 N=r["N"] if r else None))
            gid += 1
        # seam-start robustness on the QC native only
        rs = infer_graph(T, f"QC@{substrate}", substrate, Nn, gid, start="seam")
        gid += 1
        if rs:
            rows.append(rs)
            print(f"  [QC@{substrate} N={rs['N']} SEAM-start] "
                  f"logical={rs['logical']} P_log={rs['P_logical']:.5f} "
                  f"CI={rs['P_logical_wilson']}")

    out = dict(kappa=KAPPA, inference_master_seed=INFERENCE_MASTER_SEED,
               trials_per_graph=INFERENCE_TRIALS, rows=rows, manifest=manifest,
               pilot_seed_separate=True)
    (HERE / "results").mkdir(exist_ok=True)
    with open(HERE / "results" / "inference_stage1.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    _print_table(rows)
    _comparisons(rows)
    print("\n-> results/inference_stage1.json")
    return out


def _print_table(rows):
    print("\n=== STAGE-1 INFERENCE TABLE (primary non-seam starts) ===")
    hdr = f"{'substrate/family':30} {'N':>5} {'trials':>7} {'heal':>6} " \
          f"{'logi':>5} {'cens':>5} {'P_logical':>10} {'Wilson95':>22}"
    print(hdr)
    for r in rows:
        if r["start"] != "nonseam":
            continue
        ci = r["P_logical_wilson"]
        print(f"{r['name']:30} {r['N']:>5} {r['trials']:>7} {r['heal']:>6} "
              f"{r['logical']:>5} {r['censored']:>5} {r['P_logical']:>10.6f} "
              f"[{ci[0]:.5f},{ci[1]:.5f}]")
    print("\n  seam-start robustness (reported separately):")
    for r in rows:
        if r["start"] == "seam":
            ci = r["P_logical_wilson"]
            print(f"    {r['name']:26} N={r['N']:>5} logical={r['logical']:>4} "
                  f"P_logical={r['P_logical']:.6f} Wilson=[{ci[0]:.5f},{ci[1]:.5f}]")


def _lookup(rows, family, substrate, start="nonseam"):
    for r in rows:
        if r["start"] == start and r["substrate"] == substrate \
                and r["name"].startswith(family):
            return r
    return None


def _comparisons(rows):
    print("\n=== PRE-REGISTERED COMPARATIVE ANALYSES (P_logical, Wilson 95%) ===")
    subs = ["ammann_beenker", "penrose"]
    # group by native N so QC/controls compared at matched N
    by = {}
    for r in rows:
        if r["start"] != "nonseam":
            continue
        by.setdefault((r["substrate"], r["N_native"]), {})[r["family"]] = r
    print("\n 1) QC vs clean crystalline grid  |  2) QC vs defect-matched grid  "
          "|  4) QC vs bounded-rewire")
    for (sub, Nn), fam in sorted(by.items()):
        qc = fam.get("QC"); gr = fam.get("clean_grid")
        mg = fam.get("matched_grid"); rw = fam.get("rewire")
        if not qc:
            continue
        def fmt(r):
            if r is None:
                return "   n/a"
            ci = r["P_logical_wilson"]
            return f"{r['P_logical']:.5f} [{ci[0]:.5f},{ci[1]:.5f}] (k={r['logical']})"
        print(f"  {sub:14} N~{Nn}")
        print(f"      QC            {fmt(qc)}")
        print(f"      clean grid    {fmt(gr)}")
        print(f"      matched grid  {fmt(mg)}")
        print(f"      rewire (2nd)  {fmt(rw)}")
    print("\n 3) Penrose vs AB (QC, nearest matched N):")
    ab = sorted([r for r in rows if r["start"] == "nonseam"
                 and r["family"] == "QC" and r["substrate"] == "ammann_beenker"],
                key=lambda r: r["N"])
    pen = sorted([r for r in rows if r["start"] == "nonseam"
                  and r["family"] == "QC" and r["substrate"] == "penrose"],
                 key=lambda r: r["N"])
    for a in ab:
        p = min(pen, key=lambda r: abs(r["N"] - a["N"]))
        print(f"    AB N={a['N']:>5} P_log={a['P_logical']:.5f} "
              f"{a['P_logical_wilson']}   vs   "
              f"Penrose N={p['N']:>5} P_log={p['P_logical']:.5f} "
              f"{p['P_logical_wilson']}")
    print("\n 5) scaling with N (QC P_logical):")
    for sub in subs:
        pts = sorted([r for r in rows if r["start"] == "nonseam"
                      and r["family"] == "QC" and r["substrate"] == sub],
                     key=lambda r: r["N"])
        s = "  ".join(f"N={r['N']}:{r['P_logical']:.5f}(k={r['logical']})"
                      for r in pts)
        print(f"    {sub:14} {s}")


if __name__ == "__main__":
    main()
