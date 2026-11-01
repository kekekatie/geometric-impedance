#!/usr/bin/env python3
"""
part3_firstloss.py -- locate the FIRST loss of compatibility along the replay.

Faithfully replay the recorded world-7 B continuations (both streams; world 5 as
replication) with the frozen growth rules. At each growth STEP, certify
feasibility (feas.classify) of F(full) and F(skin). Find the earliest infeasible
step for each, relate it to the visible jam, and refine the full-patch transition
to the exact triggering tile addition. Pruned-skin feasibility is not assumed
monotone; the per-step gauge (S*-anchored lift, 4-layer rank map) is checked to be
consistent across states.

Outputs ../results/part3_firstloss.json and part3_report.txt.
"""
from __future__ import annotations
import json
from pathlib import Path
import study_common as SC
from study_common import Sl, PC, L
import feas

OUT = Path(__file__).resolve().parent.parent / "results"
CASES = [(7, 0, 23), (7, 1, 23), (5, 0, 42)]


def feas_of(tiles):
    try:
        rank = Sl.rank_of(tiles)
    except AssertionError:
        return dict(cls="unresolved_layers", r=None, layers=None)
    lays = sorted(rank)
    cm = Sl.constraints(tiles, rank)
    cl = feas.classify(cm)
    return dict(cls=cl["cls"], r=cl["r"], dim=cl["dim"], nconstraints=len(cm), layers=lays)


def trace_case(world, si, js):
    forks = SC.P3.load_forks()
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = PC.streams_for(world)[si]
    arm = PC.grow(Sstar, B, stream, 44)
    snaps = arm["snaps"]
    guesses = arm["guesses"]
    steps = []
    first_full = None; first_skin = None
    layers_ref = None; gauge_consistent = True
    for s in range(len(snaps)):
        full = snaps[s]
        ff = feas_of(full)
        skin, _ = PC.skin_of(full)
        fs = feas_of(skin)
        if ff["layers"] is not None:
            if layers_ref is None:
                layers_ref = ff["layers"]
            elif ff["layers"] != layers_ref:
                gauge_consistent = False
        steps.append(dict(step=s, n_full=len(full), n_skin=len(skin),
                          full_cls=ff["cls"], full_r=ff["r"],
                          skin_cls=fs["cls"], skin_r=fs["r"]))
        if first_full is None and ff["cls"] == "infeasible":
            first_full = s
        if first_skin is None and fs["cls"] == "infeasible":
            first_skin = s

    # refine the full-patch transition to the triggering tile
    trigger_tile = None
    if first_full is not None and first_full >= 1:
        prev = snaps[first_full - 1]
        prevkeys = {PC.dk(t) for t in prev}
        added = [t for t in snaps[first_full] if PC.dk(t) not in prevkeys]
        cur = list(prev)
        for i, t in enumerate(added):
            cur = cur + [t]
            if feas_of(cur)["cls"] == "infeasible":
                trigger_tile = dict(index_in_batch=i, of=len(added),
                                    dkey=repr(PC.dk(t)),
                                    centroid=[(sum(t[1:]) / 3).real, (sum(t[1:]) / 3).imag],
                                    step=first_full)
                break

    # skin feasibility monotonicity: does skin ever recover (infeasible -> feasible)?
    skin_recovers = False
    was_infeasible = False
    for st in steps:
        if st["skin_cls"] == "infeasible":
            was_infeasible = True
        elif was_infeasible and st["skin_cls"] in ("positive_area", "lower_dimensional"):
            skin_recovers = True

    return dict(case=f"w{world}-B-s{si}", world=world, stream_idx=si, jam_step=js,
                guesses=guesses, n_steps=len(snaps),
                first_infeasible_full=first_full, first_infeasible_skin=first_skin,
                full_infeasible_before_jam=(first_full is not None and first_full < js),
                trigger_tile=trigger_tile, gauge_consistent=gauge_consistent,
                layers=layers_ref, skin_nonmonotone_recovers=skin_recovers,
                steps=steps)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for (w, si, js) in CASES:
        print(f"[part3] tracing w{w}-B-s{si}...", flush=True)
        r = trace_case(w, si, js)
        out.append(r)
        print(f"   first infeasible: full@{r['first_infeasible_full']} skin@{r['first_infeasible_skin']} "
              f"(jam@{js}); full-before-jam={r['full_infeasible_before_jam']} "
              f"gauge_consistent={r['gauge_consistent']}", flush=True)
    (OUT / "part3_firstloss.json").write_text(json.dumps(out, indent=2, default=float))

    lines = []
    lines.append("Part 3 -- first loss of compatibility along the replay")
    lines.append("Feasibility certified per step for F(full) and F(skin); frozen growth rules.")
    lines.append("")
    lines.append(f"{'case':>10} {'jam':>4} {'1st_inf_full':>12} {'1st_inf_skin':>12} "
                 f"{'before_jam':>10} {'guesses':>12}")
    for r in out:
        lines.append(f"{r['case']:>10} {r['jam_step']:>4} {str(r['first_infeasible_full']):>12} "
                     f"{str(r['first_infeasible_skin']):>12} {str(r['full_infeasible_before_jam']):>10} "
                     f"{str(r['guesses']):>12}")
    lines.append("")
    for r in out:
        tt = r["trigger_tile"]
        lines.append(f"{r['case']}: F(full) first infeasible at step {r['first_infeasible_full']} "
                     f"(visible jam at {r['jam_step']}).")
        if tt:
            lines.append(f"   triggering tile: addition {tt['index_in_batch']+1}/{tt['of']} within step "
                         f"{tt['step']}, centroid ({tt['centroid'][0]:.4f},{tt['centroid'][1]:.4f}).")
        lines.append(f"   gauge consistent across steps: {r['gauge_consistent']} (layers {r['layers']}); "
                     f"skin recovers after infeasible (non-monotone): {r['skin_nonmonotone_recovers']}")
    lines.append("")
    lines.append("Reading: if 'before_jam' is True, the global compatibility region dies BEFORE the engine")
    lines.append("reports its local zero-candidate jam -- the first loss of compatibility precedes the")
    lines.append("visible jam. The triggering tile is the specific commitment that first makes F empty.")
    txt = "\n".join(lines)
    (OUT / "part3_report.txt").write_text(txt + "\n")
    print("\n" + txt)


if __name__ == "__main__":
    main()
