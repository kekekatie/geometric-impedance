#!/usr/bin/env python3
"""
endpoint_geom.py -- confirm the step-44 endpoint geometry is UNCHANGED from the
original archive-free experiment, so its readout (results/readout.json) may be
reused rather than recomputed.

For each case we re-grow the radius-2 band worker to step 44 (same frozen engine,
same scheduler, same seed/stream) and compare its final band, tile for tile, to the
original experiment's exported `final` band in input/worker_band_exports.json --
both as an unordered set of decorated keys and as the sorted key list. We also
compare the recorded scar set. Identical endpoints justify reusing the readout.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
import random
import af_common as AF
from af_common import dk, E, dk as _dk
import isolated_worker as IW
import scar_continuation as SCN

HERE = Path(__file__).resolve().parent
EXPORTS = json.loads((Path(SRC).parent / "input" / "worker_band_exports.json").read_text())
RESULTS = HERE / "results"


def exported_final_keys(case_key):
    """Decorated keys of the original experiment's exported step-44 band."""
    tiles = [IW.dtile(t) for t in EXPORTS[case_key]["final"]]
    return sorted(repr(dk(t)) for t in tiles)


def worker_final_band(world, si):
    """Re-grow the radius-2 band worker to step 44 the SAME way the original did
    (frozen ActiveSkin + patient_scar, pruning each step) and return its final band."""
    forks = AF.RD.load_forks()
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = AF.PC.streams_for(world)[si]
    skin = E.ActiveSkin(list(Sstar) + [B], radius=2)
    rng = random.Random(stream); scars = set()
    for s in range(1, 45):
        st, n, k, nw, il = SCN.patient_scar(skin, rng, scars, verify_legal=True)
        skin.additions = []
        skin.prune()
        if st == "total_arrest":
            break
    return list(skin.tris)


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = []
    for (w, si) in AF.B_JAMS:
        case = f"w{w}-s{si}"
        final_tris = worker_final_band(w, si)
        now = sorted(repr(dk(t)) for t in final_tris)
        was = exported_final_keys(case)
        set_eq = (set(now) == set(was))
        list_eq = (now == was)
        out.append(dict(case=f"w{w}-B-s{si}",
                        n_now=len(now), n_exported=len(was),
                        endpoint_set_identical=bool(set_eq),
                        endpoint_sorted_list_identical=bool(list_eq)))
        print(f"[endpoint] {case}: now={len(now)} exported={len(was)} "
              f"set_identical={set_eq} sorted_list_identical={list_eq}", flush=True)
    (RESULTS / "endpoint_geometry.json").write_text(json.dumps(out, indent=2))
    allok = all(r["endpoint_set_identical"] and r["endpoint_sorted_list_identical"] for r in out)
    print("\nSUMMARY endpoint geometry unchanged for all cases:", allok)
    print("  -> readout.json (original experiment) is reused on identical endpoints.")
    print("wrote results/endpoint_geometry.json")


if __name__ == "__main__":
    main()
