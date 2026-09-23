#!/usr/bin/env python3
"""
v14_run.py -- freeze distant starts (original geometry only), reproduce v13 original-S
visitor scores as an exact gate, then run matched distant-start visitors on the retained
v13 frozen worlds. No evolution replay; frozen weights read from v13 snapshots.
"""
from __future__ import annotations
import csv, json, os, time
import numpy as np
import v14_lib as V
import v13_lib as L

RES = os.path.join(V._HERE, "results")
os.makedirs(RES, exist_ok=True)
ARMS = ["regular", "perturbed"]
BUD = V.BUDGETS


def load_v13_scores():
    ref = {}
    with open(os.path.join(V._V13, "results", "visitor_scores.csv")) as f:
        for r in csv.DictReader(f):
            ref[(r["arm"], int(r["patch"]), int(r["pair"]), r["history"],
                 int(r["seed"]), int(r["replicate"]), int(r["budget"]))] = r
    return ref


def main():
    t0 = time.time()
    offsets, patches, hists, coeffs = L.frozen_setup()
    v13ref = load_v13_scores()

    # -------- 1. reconstruct + verify geometry, freeze distant starts ----------
    geo_ok = True; geo_dev = 0.0
    starts = {}          # (arm,i,j) -> vertex or None
    start_rows = ["arm,patch,pair,eligible,vertex,dist_pathA,dist_pathB,dist_union,"
                  "dist_S,boundary_dist,degree,x,y,n_eligible,max_dU"]
    start_json = {}
    ineligible = []
    for arm in ARMS:
        for i in range(3):
            sub = patches[(arm, i)]
            d = V.load_patch_snapshot(arm, i)
            ok, dev = V.verify_geometry(sub, d)
            geo_ok = geo_ok and ok; geo_dev = max(geo_dev, dev if dev != float("inf") else 1e9)
            # coeff arrays must match reconstruction (alignment of tags)
            orig, cand, idx = L.patch_edge_index(sub)
            for j in range(V.N_PAIRS):
                cj = coeffs[(arm, i)][j]
                arr = np.array([cj[e] for e in cand])
                if not np.allclose(arr, d[f"coeff_{j}"]):
                    geo_ok = False
            for j in range(V.N_PAIRS):
                h = hists[(arm, i)][j]
                v, info = V.select_distant_start(sub, h["pathA"], h["pathB"])
                starts[(arm, i, j)] = v
                start_json[f"{arm}_{i}_{j}"] = info
                if v is None:
                    ineligible.append((arm, i, j))
                    start_rows.append(f"{arm},{i},{j},0,,,,,,,,,,{info['n_eligible']},"
                                      f"{info['max_dU']}")
                else:
                    start_rows.append(
                        f"{arm},{i},{j},1,{info['vertex']},{info['dist_pathA']},"
                        f"{info['dist_pathB']},{info['dist_union']},{info['dist_S']},"
                        f"{info['boundary_dist']},{info['degree']},{info['x']},"
                        f"{info['y']},{info['n_eligible']},{info['max_dU']}")
    # freeze/save selections BEFORE any visitor outcome
    open(os.path.join(RES, "distant_starts.csv"), "w").write("\n".join(start_rows) + "\n")
    json.dump(start_json, open(os.path.join(RES, "distant_starts.json"), "w"), indent=2)
    print(f"frozen distant starts: {len(starts)} cells, "
          f"{len(ineligible)} ineligible; geo_ok={geo_ok} dev={geo_dev:.2e}", flush=True)

    # -------- 2. visitor runs: original-S (gate) + distant (matched streams) ----
    fs = open(os.path.join(RES, "scores_main.csv"), "w")
    fs.write("arm,patch,pair,history,seed,replicate,budget,start,S_local,global_S_high,"
             "diags_seen,frac_present,frac_high_seen,arrived,arrival_step\n")
    fn = open(os.path.join(RES, "scores_null.csv"), "w")
    fn.write("arm,patch,pair,seed,replicate,budget,start,S_local_null\n")

    gate_max = 0.0; gate_n = 0; gate_ok = True
    imm_ok = True

    for arm in ARMS:
        ac = 0 if arm == "regular" else 1
        for i in range(3):
            sub = patches[(arm, i)]
            d = V.load_patch_snapshot(arm, i)
            orig, cand, idx = L.patch_edge_index(sub)
            for j in range(V.N_PAIRS):
                h = hists[(arm, i)][j]; coeff = coeffs[(arm, i)][j]
                S = h["S"]; dstart = starts[(arm, i, j)]
                punion = set(int(x) for x in h["pathA"]) | set(int(x) for x in h["pathB"])
                for hk in ("A", "B"):
                    hc = 0 if hk == "A" else 1
                    for seed in range(V.NSEED):
                        fw = V.frozen_from_snapshot(d, orig, cand, j, hk, seed)
                        gsh = fw.global_s_high()
                        # immutability: reconstructed global == snapshot-implied global
                        widx = ((((ac * 3 + i) * 3 + j) * 2 + hc) * V.NSEED + seed)
                        for r in range(V.REPLICATES):
                            base_seed = V.VISIT_BASE + widx * V.REPLICATES + r
                            # --- original S (reproduce v13 exactly) ---
                            rng = np.random.default_rng(base_seed)
                            enc, cov, arr, astep = V.visit_track(fw, S, BUD, rng, punion)
                            for b in BUD:
                                sl_ = V.score_enc(enc[b], coeff, fw)
                                cv = cov[b]
                                fs.write(f"{arm},{i},{j},{hk},{seed},{r},{b},orig,"
                                         f"{sl_:.5f},{gsh:.5f},{cv['diags']},"
                                         f"{cv['frac_present']:.4f},"
                                         f"{cv['frac_high_seen']:.4f},"
                                         f"{int(arr[b])},{astep if astep is not None else -1}\n")
                                rr = v13ref.get((arm, i, j, hk, seed, r, b))
                                if rr:
                                    gate_max = max(gate_max, abs(sl_ - float(rr["S_local"])),
                                                   abs(gsh - float(rr["global_S_high"])))
                                    gate_n += 1
                                    if cv["diags"] != int(rr["diags_seen"]):
                                        gate_ok = False
                            # --- distant start (matched stream: same seed) ---
                            if dstart is not None:
                                rng2 = np.random.default_rng(base_seed)
                                enc2, cov2, arr2, astep2 = V.visit_track(
                                    fw, dstart, BUD, rng2, punion)
                                for b in BUD:
                                    sl2 = V.score_enc(enc2[b], coeff, fw)
                                    cv2 = cov2[b]
                                    fs.write(f"{arm},{i},{j},{hk},{seed},{r},{b},distant,"
                                             f"{sl2:.5f},{gsh:.5f},{cv2['diags']},"
                                             f"{cv2['frac_present']:.4f},"
                                             f"{cv2['frac_high_seen']:.4f},"
                                             f"{int(arr2[b])},"
                                             f"{astep2 if astep2 is not None else -1}\n")
                        # round-trip immutability: rebuild fw again, global must match
                        fw2 = V.frozen_from_snapshot(d, orig, cand, j, hk, seed)
                        if abs(fw2.global_s_high() - gsh) > 1e-12:
                            imm_ok = False
            # ---- null worlds (reuse frozen weights; orig + distant per pair) ----
            nidx_base = (ac * 3 + i) * V.NSEED
            for j in range(V.N_PAIRS):
                coeff = coeffs[(arm, i)][j]; S = hists[(arm, i)][0]["S"]
                dstart = starts[(arm, i, j)]
                punion = (set(int(x) for x in hists[(arm, i)][j]["pathA"]) |
                          set(int(x) for x in hists[(arm, i)][j]["pathB"]))
                for seed in range(V.NSEED):
                    fw = V.frozen_from_snapshot(d, orig, cand, j, "null", seed)
                    nidx = nidx_base + seed
                    for r in range(V.REPLICATES):
                        base_seed = V.VISIT_BASE + 7_000_000 + nidx * V.REPLICATES + r
                        rng = np.random.default_rng(base_seed)
                        enc, cov, arr, astep = V.visit_track(fw, S, BUD, rng, punion)
                        for b in BUD:
                            fn.write(f"{arm},{i},{j},{seed},{r},{b},orig,"
                                     f"{V.score_enc(enc[b], coeff, fw):.5f}\n")
                        if dstart is not None:
                            rng2 = np.random.default_rng(base_seed)
                            enc2, cov2, arr2, astep2 = V.visit_track(
                                fw, dstart, BUD, rng2, punion)
                            for b in BUD:
                                fn.write(f"{arm},{i},{j},{seed},{r},{b},distant,"
                                         f"{V.score_enc(enc2[b], coeff, fw):.5f}\n")
            print(f"  done {arm}#{i}  elapsed {(time.time()-t0)/60:.1f} min", flush=True)

    fs.close(); fn.close()
    gate_ok = gate_ok and (gate_max < 1e-6) and gate_n > 0

    val = ["# v14 validation",
           f"# geometry reconstruction == snapshot: {'PASS' if geo_ok else 'FAIL'} "
           f"(max coord dev {geo_dev:.2e}; coeff alignment checked)",
           f"# original-S visitor reproduces v13 scores: "
           f"{'PASS' if gate_ok else 'FAIL'} (max|d|={gate_max:.2e} over {gate_n} values)",
           f"# frozen-state immutability (round-trip global): "
           f"{'PASS' if imm_ok else 'FAIL'}",
           f"# ineligible cells (no distant start): {len(ineligible)} {ineligible}",
           f"# runtime_min = {(time.time()-t0)/60:.1f}"]
    allpass = geo_ok and gate_ok and imm_ok
    val.append(f"# ALL GATES: {'PASS' if allpass else 'FAIL'}")
    open(os.path.join(RES, "validation_v14.txt"), "w").write("\n".join(val) + "\n")
    json.dump({"nseed": V.NSEED, "replicates": V.REPLICATES, "budgets": BUD,
               "primary": V.PRIMARY, "min_boundary": 2, "ineligible": ineligible,
               "runtime_min": round((time.time() - t0) / 60, 1)},
              open(os.path.join(RES, "run_config.json"), "w"), indent=2)
    open(os.path.join(RES, "V14_DONE"), "w").write("done\n")
    print("\n".join(val))
    print(f"V14 RUN DONE in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
