#!/usr/bin/env python3
"""
run_experiment.py -- archive-free scar continuation: full 11-case comparison +
isolation/cold-restart/metadata controls + band exports for readout.

For each recorded B-jam: run the audited full-patch scar scheduler (evaluator) and
the archive-free radius-2 ActiveSkin worker in lockstep from the same seed/stream;
record exact-equivalence, first divergence, progress, and scar-tissue growth.
Export each worker jam/final retained band for the secondary readout. Run the
spawned-process isolation, cold-restart, and metadata-audit controls on w7/w5.
"""
from __future__ import annotations
import json, math
import af_common as AF
from af_common import PC, L, dk
import scar_skin as SK
import isolated_worker as IW


def band_extent(tiles, frontier_edges):
    """How far the retained band reaches from the true frontier (in S), and the
    retained count -- the 'scar tissue' measure. frontier_edges: list of (p,q,r,t)."""
    pts = [z for e in frontier_edges for z in e[:2]]
    if not pts or not tiles:
        return dict(n_tiles=len(tiles), max_reach_S=None, mean_reach_S=None)
    reaches = []
    for t in tiles:
        c = sum(t[1:]) / 3
        reaches.append(min(abs(c - v) for v in pts) / AF.S)
    return dict(n_tiles=len(tiles), max_reach_S=round(max(reaches), 3),
                mean_reach_S=round(sum(reaches) / len(reaches), 3))


def etiles(tiles):
    return [IW.etile(t) for t in tiles]


def main():
    AF.RESULTS.mkdir(parents=True, exist_ok=True)
    AF.INPUT.mkdir(parents=True, exist_ok=True)
    cases = []
    exports = {}
    for (w, si) in AF.B_JAMS:
        print(f"[run] w{w}-s{si} ...", flush=True)
        jp = AF.jam_prep(w, si)
        jam_band = jp["band"]                       # frozen retained band at the jam checkpoint
        lk = SK.run_lockstep(w, si, steps=44)
        # final true-frontier edges from the worker boundary
        final_frontier = sorted(lk["worker_boundary"].values(),
                                key=lambda e: (abs((e[0] + e[1]) / 2), L.key((e[0] + e[1]) / 2)))
        tissue_final = band_extent(lk["worker_band"], final_frontier)
        tissue_jam = band_extent(jam_band, L.Patch(list(jp["full_jam"])).frontier())
        # retained-count trajectory (scar tissue grows)
        retained_traj = [(r["step"], r["worker_retained"], r["full_tiles"], r["frontier"], r["worker_scars"])
                         for r in lk["rows"]]
        rec = dict(case=f"w{w}-B-s{si}", world=w, si=si, stream=lk["stream"],
                   jam_step=lk["jam_step"], final_step=lk["final_step"],
                   reached_44=lk["reached_44"],
                   exact_equivalence=lk["exact_equivalence"],
                   first_divergence=lk["first_divergence"],
                   illegal_worker_placements=lk["illegal_worker"],
                   n_full_tiles_final=len(lk["full"]),
                   n_worker_band_final=len(lk["worker_band"]),
                   retained_fraction_final=round(len(lk["worker_band"]) / len(lk["full"]), 4),
                   n_true_frontier_edges_final=len(final_frontier),
                   n_scars_final=len(lk["worker_scars"]),
                   scar_tissue_jam=tissue_jam, scar_tissue_final=tissue_final,
                   retained_trajectory=retained_traj,
                   rows=lk["rows"])
        cases.append(rec)
        exports[f"w{w}-s{si}"] = dict(jam=etiles(jam_band), final=etiles(lk["worker_band"]),
                                      full_final=etiles(lk["full"]),
                                      scars=lk["worker_scars"], jam_step=lk["jam_step"])
        print(f"   exact_equiv={rec['exact_equivalence']} reached44={rec['reached_44']} "
              f"illegal={rec['illegal_worker_placements']} band {rec['n_worker_band_final']}/"
              f"{rec['n_full_tiles_final']} ({rec['retained_fraction_final']*100:.0f}%) "
              f"scars={rec['n_scars_final']} max_reach={tissue_final['max_reach_S']}S", flush=True)

    (AF.RESULTS / "comparison.json").write_text(json.dumps(cases, indent=2, default=float))
    (AF.INPUT / "worker_band_exports.json").write_text(json.dumps(exports, default=float))

    # ---------------- controls (w7, w5) ----------------
    controls = {}
    for (w, si) in [(7, 0), (5, 0)]:
        jam = AF.jam_prep(w, si)["jam_step"]
        wt = SK.worker_trace(w, si, steps=44, serialize_at=jam)
        in_proc_post = [row["placed"] for row in wt["trace"] if row["step"] > jam]
        snap = wt["snapshot"]
        # spawned-process isolation: worker in a separate process, only the serialized state
        spawned = IW.run_spawned(snap, 44 - jam)
        spawned_post = [m["placed"] for m in spawned if m.get("kind") == "step"]
        spawned_ok = (spawned_post == in_proc_post)
        # cold restart in-process
        skin2 = IW.rebuild_skin(snap); rng2 = IW.rebuild_rng(snap); scars2 = IW.rebuild_scars(snap)
        cold = []
        for s in range(jam + 1, 45):
            m = SK.worker_step(skin2, rng2, scars2); cold.append(m["placed"])
            if m["status"] == "total_arrest":
                break
        cold_ok = (cold == in_proc_post)
        # metadata audit
        allowed = {"schema", "radius", "tiles", "boundary", "rng_state", "scars", "fields"}
        meta_ok = (set(snap) == allowed)
        controls[f"w{w}-s{si}"] = dict(
            jam_step=jam, post_jam_steps=len(in_proc_post),
            spawned_process_isolation_matches=bool(spawned_ok),
            cold_restart_matches=bool(cold_ok),
            metadata_fields=sorted(set(snap)),
            metadata_only_declared_fields=bool(meta_ok),
            serialized_band_tiles=len(snap["tiles"]),
            serialized_boundary_edges=len(snap["boundary"]))
        print(f"[control] w{w}-s{si}: spawned_isolation={spawned_ok} cold_restart={cold_ok} metadata_ok={meta_ok}",
              flush=True)
    (AF.RESULTS / "controls.json").write_text(json.dumps(controls, indent=2, default=float))

    n_equiv = sum(1 for c in cases if c["exact_equivalence"])
    print(f"\nSUMMARY: {n_equiv}/{len(cases)} cases EXACT-EQUIVALENT to the full-patch scheduler; "
          f"all reached 44: {all(c['reached_44'] for c in cases)}; "
          f"total illegal worker placements: {sum(c['illegal_worker_placements'] for c in cases)}")
    print("wrote results/comparison.json, results/controls.json, input/worker_band_exports.json")


if __name__ == "__main__":
    main()
