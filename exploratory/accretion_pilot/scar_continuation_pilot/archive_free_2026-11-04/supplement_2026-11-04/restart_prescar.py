#!/usr/bin/env python3
"""
restart_prescar.py -- spawned-process restart from the ACTUAL pre-scar jam state
(serialized at the TOP of the jam step, before the first scar-tolerant batch), for
all eleven cases.

A fresh worker process is launched receiving ONLY the serialized pre-scar retained
state, and run from the jam step through step 44. Its ordered placement sequence is
compared, step by step, against (a) the full-patch scar comparator and (b) the
uninterrupted band worker over the same steps. The worker never receives full-patch
geometry; the evaluator uses it only to produce the comparator trajectory.
"""
from __future__ import annotations
import sys, json, random
from pathlib import Path
SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
import af_common as AF
from af_common import E, L, dk
import isolated_worker as IW
import scar_continuation as SCN
import verify_supplement as VS   # reuse jam_prep via AF; and nothing else

RESULTS = Path(__file__).resolve().parent / "results"
INPUT = Path(__file__).resolve().parent / "input"


def full_patch_placements(world, si):
    """Ordered placements per step from the audited full-patch scar scheduler."""
    jp = AF.jam_prep(world, si)
    full = L.Patch(list(jp["Sstar"])); full.add(jp["B"])
    rng = random.Random(jp["stream"]); scars = set()
    per = []
    for s in range(1, 45):
        n0 = len(full.tris)
        st, n, k, nw, il = SCN.patient_scar(full, rng, scars, verify_legal=True)
        per.append((s, [repr(dk(t)) for t in full.tris[n0:]]))
        if st == "total_arrest":
            break
    return per, jp["jam_step"]


def uninterrupted_worker_placements(world, si):
    forks = AF.RD.load_forks()
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = AF.PC.streams_for(world)[si]
    skin = E.ActiveSkin(list(Sstar) + [B], radius=2)
    rng = random.Random(stream); scars = set()
    per = []
    for s in range(1, 45):
        skin.additions = []
        st, n, k, nw, il = SCN.patient_scar(skin, rng, scars, verify_legal=True)
        per.append((s, [repr(dk(t)) for t in skin.additions]))
        if st == "total_arrest":
            break
    return per, list(skin.tris)


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    prestates = json.loads((INPUT / "prescar_states.json").read_text())
    out = []
    for (w, si) in AF.B_JAMS:
        state = prestates[f"w{w}-s{si}"]
        full_per, jam_step = full_patch_placements(w, si)
        worker_per, worker_final = uninterrupted_worker_placements(w, si)
        # spawned restart from the pre-scar state: steps jam_step..44
        n_steps = 44 - jam_step + 1
        spawned = IW.run_spawned(state, n_steps)
        spawned_steps = [m for m in spawned if m.get("kind") == "step"]
        spawned_placed = [m["placed"] for m in spawned_steps]              # lists of dkeys (tuples)
        spawned_placed = [[repr(tuple(k)) for k in step] for step in spawned_placed]
        # comparators restricted to jam_step..44
        full_slice = [p for (s, p) in full_per if s >= jam_step]
        worker_slice = [p for (s, p) in worker_per if s >= jam_step]
        match_full = (spawned_placed == full_slice)
        match_worker = (spawned_placed == worker_slice)
        out.append(dict(case=f"w{w}-B-s{si}", jam_step=jam_step,
                        steps_run=[jam_step, jam_step + len(spawned_placed) - 1],
                        n_steps=len(spawned_placed),
                        restart_matches_full_patch=bool(match_full),
                        restart_matches_uninterrupted_worker=bool(match_worker),
                        serialized_band_tiles=len(state["tiles"]),
                        serialized_boundary_edges=len(state["boundary"])))
        print(f"[restart] w{w}-s{si}: from step {jam_step} ({len(spawned_placed)} steps) "
              f"matches_full={match_full} matches_worker={match_worker}", flush=True)
    (RESULTS / "prescar_restart.json").write_text(json.dumps(out, indent=2, default=float))
    print("\nSUMMARY restart==full:", sum(r["restart_matches_full_patch"] for r in out), "/", len(out),
          "| restart==worker:", sum(r["restart_matches_uninterrupted_worker"] for r in out), "/", len(out))
    print("wrote results/prescar_restart.json")


if __name__ == "__main__":
    main()
