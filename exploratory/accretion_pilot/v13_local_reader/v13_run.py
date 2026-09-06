#!/usr/bin/env python3
"""
v13_run.py -- replay v11 worlds to t=2000, save aligned snapshots (validated vs v11
scalars), round-trip, and run the passive tagged visitor. Writes visitor scores +
coverage + global reader per world. No mutation of frozen worlds.
"""
from __future__ import annotations
import csv, json, os, time
import numpy as np
import v13_lib as L

RES = os.path.join(L._HERE, "results")
SNAP = os.path.join(RES, "snapshots")
os.makedirs(SNAP, exist_ok=True)
NSEED = 50
REPLICATES = 5
BUD = L.BUDGETS


def load_v11_scalars():
    ref = {}
    with open(os.path.join(L._V11, "results", "raw_main.csv")) as f:
        for r in csv.DictReader(f):
            if int(r["checkpoint"]) == L.CHECKPOINT and int(r["seed"]) < NSEED:
                ref[(r["arm"], int(r["patch"]), int(r["pair"]), r["history"],
                     int(r["seed"]))] = r
    return ref


def main():
    t0 = time.time()
    offsets, patches, hists, coeffs = L.frozen_setup()
    ref = load_v11_scalars()
    val_lines = ["# v13 replay validation vs v11 t=2000 scalars"]
    maxd = 0.0; nval = 0
    fx_full = True; rt_ok = True

    fscore = open(os.path.join(RES, "visitor_scores.csv"), "w")
    fscore.write("arm,patch,pair,history,seed,replicate,budget,S_local,"
                 "global_S_high,diags_seen,frac_present,frac_high_seen\n")
    fnull = open(os.path.join(RES, "visitor_null.csv"), "w")
    fnull.write("arm,patch,pair,seed,replicate,budget,S_local_null\n")

    for key in patches:
        arm, i = key
        sub = patches[key]
        orig, cand, idx = L.patch_edge_index(sub)
        arch = {"pos_x": np.array([sub.pos[v][0] for v in range(sub.V)]),
                "pos_y": np.array([sub.pos[v][1] for v in range(sub.V)]),
                "orig_u": np.array([e[0] for e in orig]),
                "orig_v": np.array([e[1] for e in orig]),
                "cand_u": np.array([e[0] for e in cand]),
                "cand_v": np.array([e[1] for e in cand])}
        cand_key = cand
        # coefficient dicts per pair (keyed by edge key) + aligned vectors
        for j in range(L.N_PAIRS):
            c = coeffs[key][j]
            arch[f"coeff_{j}"] = np.array([c[e] for e in cand])
            h = hists[key][j]
            arch[f"pathA_{j}"] = np.array(h["pathA"])
            arch[f"pathB_{j}"] = np.array(h["pathB"])
            arch[f"S_{j}"] = np.array([h["S"]])

        # --- main worlds: replay, snapshot, validate, round-trip, visit ---
        for j in range(L.N_PAIRS):
            h = hists[key][j]; coeff = coeffs[key][j]
            for hk, path in (("A", h["pathA"]), ("B", h["pathB"])):
                for seed in range(NSEED):
                    w = L.replay(sub, path, seed)
                    sc = L.scalars(w, coeff, h["S"])
                    rr = ref.get((arm, i, j, hk, seed))
                    if rr:
                        for col in ["S_high", "n_active", "frac_active", "headroom",
                                    "total_weight", "struct_access", "eff_alt"]:
                            maxd = max(maxd, abs(sc[col] - float(rr[col]))); nval += 1
                    vec = L.weight_vector(w, orig, cand, idx)
                    arch[f"w_{j}_{hk}_{seed}"] = vec
                    # round-trip: reconstruct from vector, verify global == world S_high
                    fw = L.FrozenWorld(orig, cand_key, vec, arch[f"coeff_{j}"])
                    if abs(fw.global_s_high() - sc["S_high"]) > 1e-6:
                        rt_ok = False
                    full = sum(fw.coeff[d] for d in fw.is_diag if L.qround(fw.w[d]) == 6)
                    if abs(full - fw.global_s_high()) > 1e-9:
                        fx_full = False
                    gsh = fw.global_s_high()
                    ac = 0 if arm == "regular" else 1
                    hc = 0 if hk == "A" else 1
                    widx = ((((ac * 3 + i) * 3 + j) * 2 + hc) * NSEED + seed)
                    for r in range(REPLICATES):
                        rng = np.random.default_rng(L.VISIT_BASE + widx * REPLICATES + r)
                        enc, cov = L.visit_encounters(fw, h["S"], BUD, rng)
                        for b in BUD:
                            sl_ = L.score_enc(enc[b], coeff, fw)
                            cv = cov[b]
                            fscore.write(f"{arm},{i},{j},{hk},{seed},{r},{b},{sl_:.5f},"
                                         f"{gsh:.5f},{cv['diags']},{cv['frac_present']:.4f},"
                                         f"{cv['frac_high_seen']:.4f}\n")
        # --- null worlds: one per (patch,seed), reused across 3 readers ---
        S0 = hists[key][0]["S"]
        coeff_dicts = [coeffs[key][j] for j in range(L.N_PAIRS)]
        for seed in range(NSEED):
            wn = L.replay_nohistory(sub, S0, seed)
            vec = L.weight_vector(wn, orig, cand, idx)
            arch[f"nw_{seed}"] = vec
            fw = L.FrozenWorld(orig, cand_key, vec, arch["coeff_0"])
            ac = 0 if arm == "regular" else 1
            nidx = (ac * 3 + i) * NSEED + seed
            for r in range(REPLICATES):
                rng = np.random.default_rng(
                    L.VISIT_BASE + 7_000_000 + nidx * REPLICATES + r)
                enc, cov = L.visit_encounters(fw, S0, BUD, rng)
                for j in range(L.N_PAIRS):
                    for b in BUD:
                        sl_ = L.score_enc(enc[b], coeff_dicts[j], fw)
                        fnull.write(f"{arm},{i},{j},{seed},{r},{b},{sl_:.5f}\n")
        np.savez_compressed(os.path.join(SNAP, f"{arm}_{i}.npz"), **arch)
        print(f"  done {arm}#{i}  elapsed {(time.time()-t0)/60:.1f} min", flush=True)

    fscore.close(); fnull.close()
    val_lines.append(f"# replay scalar max|d| = {maxd:.3e} over {nval} values "
                     f"(tol 1e-4) -> {'PASS' if maxd < 1e-4 else 'FAIL'}")
    val_lines.append(f"# fixture full-obs==global: {'PASS' if fx_full else 'FAIL'}")
    val_lines.append(f"# round-trip frozen==world S_high: {'PASS' if rt_ok else 'FAIL'}")
    val_lines.append(f"# runtime_min = {(time.time()-t0)/60:.1f}")
    allpass = (maxd < 1e-4) and fx_full and rt_ok
    val_lines.append(f"# ALL GATES: {'PASS' if allpass else 'FAIL'}")
    with open(os.path.join(RES, "validation_v13.txt"), "w") as f:
        f.write("\n".join(val_lines) + "\n")
    with open(os.path.join(RES, "run_config.json"), "w") as f:
        json.dump({"nseed": NSEED, "replicates": REPLICATES, "budgets": BUD,
                   "checkpoint": L.CHECKPOINT, "offsets": offsets,
                   "runtime_min": round((time.time() - t0) / 60, 1)}, f, indent=2)
    open(os.path.join(RES, "V13_DONE"), "w").write("done\n")
    print("\n".join(val_lines))
    print(f"V13 RUN DONE in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
