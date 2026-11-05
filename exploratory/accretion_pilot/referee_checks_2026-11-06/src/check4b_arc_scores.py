#!/usr/bin/env python3
"""
check4b_arc_scores.py -- Check 4b: reader scores of matched tile-count arcs.

Pre-registered crossing-vs-parallel classification requires the fork WORM LINE from
check 4a. Check 4a found NO single worm strip in any of the 22 forks (P4a failed), so
the worm line is undefined and the pre-registered crossing/parallel split is NOT
evaluable. We still carry out, and report, the parts that do not depend on a worm line:

  (1) score matched tile-count arcs (K=32, connected, nearest-first BFS) with the frozen
      reader under BOTH conventions (open + closed), on BOTH datasets (49 recovery skins,
      11 jammed bands at the jam checkpoint);
  (2) the A-only FALSIFIER: whether ANY arc uniquely selects A under either convention
      (any such arc falsifies "never A" and is reported prominently);
  (3) an EXPLORATORY (NOT pre-registered) split by overlap with the world's A/B forced-
      closure difference region (from check 4a's diff_regions.json): arcs with a majority
      of tiles in the difference region ("in_diff") vs the rest ("out_diff"). This is a
      well-defined substitute for the (undefined) worm line; it is clearly labelled
      exploratory and is not the pre-registered P4b test.

Writes results/check4b_arc_scores.json.
"""
from __future__ import annotations
import json, math, collections
import rc_common as RC

K = 32
N_SEEDS = 20


def closed_compatible(constraints, windows, hyp_rows):
    """Closed-region feasibility of F intersected with a hypothesis (LP; a zero-area
    point/segment counts). hyp_rows = [[r,i,c],...]."""
    import numpy as np
    from scipy.optimize import linprog
    cm = {(r, i): c for r, i, c in constraints}
    for r, i, c in hyp_rows:
        cm[(r, i)] = max(cm.get((r, i), -math.inf), c)
    A = []; b = []
    for (r, i), c in cm.items():
        nx, ny = windows[r]["normals"][i]; nrm = math.hypot(nx, ny)
        if nrm < 1e-15:
            continue
        A.append([-nx / nrm, -ny / nrm]); b.append(-c / nrm)
    if not A:
        return True
    res = linprog([0, 0], A_ub=np.array(A), b_ub=np.array(b),
                  bounds=[(-50, 50), (-50, 50)], method="highs")
    return res.status == 0


def score_arc(Sstar, cs, arc, payload_hyps=None):
    """Return outcome under open and closed conventions + raw fields."""
    raw, payload = RC.read_tiles(Sstar, cs, arc)
    if raw.get("status") != "reconstructed":
        return dict(status=raw.get("status"), open="unreconstructible", closed="unreconstructible")
    ints = raw.get("intersections", [0, 0])
    Farea = raw.get("area", 0.0)
    # open convention (reader native)
    open_comp = [h for h, v in enumerate(ints) if v > 1e-9]
    open_sel = open_comp[0] if (len(open_comp) == 1 and Farea > 1e-12) else None
    # closed convention
    hyps = payload["hypotheses"]
    closed_comp = [h for h in (0, 1) if closed_compatible(raw["constraints"], payload["windows"], hyps[h])]
    Ffeasible = closed_compatible(raw["constraints"], payload["windows"], [])
    closed_sel = closed_comp[0] if (len(closed_comp) == 1 and Ffeasible) else None

    def label(sel, comp):
        if sel == 1:
            return "B"           # correct
        if sel == 0:
            return "A"           # wrong / falsifier
        if len(comp) >= 2:
            return "ambiguous"
        return "empty_incompatible"
    return dict(status="reconstructed", F_area=Farea, intersections=ints,
                open=label(open_sel, open_comp), closed=label(closed_sel, closed_comp),
                open_selected=open_sel, closed_selected=closed_sel)


def seeds_for(tiles):
    bkeys = list(RC.boundary_edges(tiles))  # not used directly; use boundary tiles by angle
    # boundary tiles = tiles having >=1 boundary leg
    bedges = RC.boundary_edges(tiles)
    bverts = set().union(*[set(e) for e in bedges]) if bedges else set()
    c = RC.centroid(tiles)
    btiles = [t for t in tiles if any(RC.L.key(z) in bverts for z in t[1:])]
    btiles.sort(key=lambda t: math.atan2((RC.tile_centroid(t) - c).imag, (RC.tile_centroid(t) - c).real))
    if not btiles:
        return []
    step = max(1, len(btiles) // N_SEEDS)
    return [RC.dk(btiles[i]) for i in range(0, len(btiles), step)]


def overlap_split(arc, diff_vertex_keys):
    """EXPLORATORY: fraction of arc tiles with a majority of vertices in the A/B diff region."""
    dset = set(diff_vertex_keys)
    nin = 0
    for t in arc:
        vk = [repr(RC.L.key(z)) for z in t[1:]]
        if sum(1 for k in vk if k in dset) >= 2:
            nin += 1
    frac = nin / len(arc) if arc else 0.0
    return ("in_diff" if frac >= 0.5 else "out_diff"), round(frac, 3)


def run_dataset(name, items, diff_regions):
    rows = []
    open_tally = collections.Counter(); closed_tally = collections.Counter()
    expl = {"in_diff": collections.Counter(), "out_diff": collections.Counter()}
    falsifiers = []          # A-selected on a B-committed case (true "never A" falsifier)
    correct_A = []           # A-selected on an A-true case (correct recovery, NOT a falsifier)
    for it in items:
        world = it["world"]; tiles = it["tiles"]; true_opt = it["true_option"]
        Sstar = it["Sstar"]; cs = it["cs"]
        dr = diff_regions.get(str(world))
        for seed in seeds_for(tiles):
            arc = RC.connected_arc(tiles, seed, K)
            if len(arc) < K:
                continue
            sc = score_arc(Sstar, cs, arc)
            open_tally[sc["open"]] += 1; closed_tally[sc["closed"]] += 1
            grp = None; frac = None
            if dr:
                grp, frac = overlap_split(arc, dr["diff_vertex_keys"])
                expl[grp][sc["open"]] += 1
            row = dict(case=it["label"], world=world, true_option=true_opt, seed=str(seed),
                       open=sc["open"], closed=sc["closed"],
                       F_area=sc.get("F_area"), expl_group=grp, expl_in_frac=frac)
            rows.append(row)
            selects_A = (sc["open"] == "A" or sc["closed"] == "A")
            if selects_A and true_opt == "B":
                falsifiers.append(row)
            elif selects_A and true_opt == "A":
                correct_A.append(row)
    return dict(dataset=name, n_arcs=len(rows),
                open_tally=dict(open_tally), closed_tally=dict(closed_tally),
                exploratory_overlap_open={k: dict(v) for k, v in expl.items()},
                n_falsifier_A_on_B_case=len(falsifiers),
                n_correct_A_on_A_case=len(correct_A),
                falsifier_arcs=falsifiers, rows=rows)


def main():
    RC.RESULTS.mkdir(parents=True, exist_ok=True)
    diff_regions = json.loads((RC.RESULTS / "diff_regions.json").read_text())

    # dataset 1: 49 recovery skins (need Sstar/cs per world for the reader payload)
    forks = RC.RD.load_forks()
    rec = []
    for case in RC.load_recovery_cases():
        w = case["world"]
        if w is None or w not in forks:
            continue
        true_opt = {0: "A", 1: "B"}.get(case["true_index"], "?")
        rec.append(dict(label=case["name"], world=w, tiles=case["tiles"], true_option=true_opt,
                        Sstar=forks[w]["Sstar"], cs=forks[w]["cs"]))
    # dataset 2: 11 jammed bands (jam checkpoint) -- all B-committed
    jam = [dict(label=b["case"], world=b["world"], tiles=b["jam_band"], true_option="B",
                Sstar=b["Sstar"], cs=b["cs"]) for b in RC.load_jammed_bands()]

    d1 = run_dataset("recovery_skins_49", rec, diff_regions)
    print(f"[4b] recovery: {d1['n_arcs']} arcs open={d1['open_tally']} closed={d1['closed_tally']} "
          f"| falsifier(A on B-case)={d1['n_falsifier_A_on_B_case']} correctA(on A-case)={d1['n_correct_A_on_A_case']}", flush=True)
    d2 = run_dataset("jammed_bands_11", jam, diff_regions)
    print(f"[4b] jammed:   {d2['n_arcs']} arcs open={d2['open_tally']} closed={d2['closed_tally']} "
          f"| falsifier(A on B-case)={d2['n_falsifier_A_on_B_case']}", flush=True)

    n_fals = d1["n_falsifier_A_on_B_case"] + d2["n_falsifier_A_on_B_case"]
    n_correctA = d1["n_correct_A_on_A_case"] + d2["n_correct_A_on_A_case"]
    summary = dict(
        K=K, worm_line_available=bool(diff_regions and any(v["single_strip"] for v in diff_regions.values())),
        pre_registered_crossing_parallel_evaluable=False,
        reason="check 4a found no single worm strip in any fork (P4a failed); the fork worm line is undefined",
        falsifier_A_on_B_case_total=n_fals,
        correct_A_on_A_case_total=n_correctA,
        never_A_falsified=bool(n_fals > 0),
        note=("A-selections on A-true recovery cases are CORRECT recoveries, not falsifiers; "
              "the never-A falsifier counts only A-selections on B-committed cases"))
    (RC.RESULTS / "check4b_arc_scores.json").write_text(
        json.dumps(dict(summary=summary, recovery=d1, jammed=d2), indent=2, default=float))
    print(f"\n[4b] never-A falsifier (A selected on a B-committed case): {n_fals} -> "
          f"never-A {'FALSIFIED' if n_fals else 'NOT falsified'}")
    print(f"     (A correctly selected on A-true recovery cases: {n_correctA} arcs — not falsifiers)")
    print("     crossing/parallel: NOT evaluable (no worm line from 4a); exploratory overlap split reported instead")
    print("wrote results/check4b_arc_scores.json")


if __name__ == "__main__":
    main()
