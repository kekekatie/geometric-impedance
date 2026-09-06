#!/usr/bin/env python3
"""
v12_contrasts.py -- matched-offset patch contrasts at t=2000 from EXISTING v11
scalar data (read-only; no new trajectories, no tuning, no added seeds).

For each matched offset i (regular#i vs perturbed#i, which share a base offset),
patch memory = ordinary AUC (A vs B) at t=2000 averaged over its 3 history pairs.
Contrast_i = perturbed_i - regular_i; mean over the 3 matched pairs.

Simulation-uncertainty interval CONDITIONAL on these six patches: bootstrap resamples
the 200 seed indices ONCE per replicate and applies the SAME seed set to every cell
(both arms, all pairs), preserving the shared common-random-number dependence across
cells and arms. Patches are NOT resampled -> this interval does not generalise beyond
these three patch pairs.
"""
from __future__ import annotations
import csv, os
from collections import defaultdict
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V11 = os.path.join(os.path.dirname(_HERE), "v11_substrate_pilot", "results",
                    "raw_main.csv")
CP = 2000
NPAIRS = 3
ARMS = ["regular", "perturbed"]


def auc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    allv = np.concatenate([a, b]); order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    s = np.zeros(len(cnt)); np.add.at(s, inv, ranks); ranks = (s / cnt)[inv]
    nA = len(a)
    return float((ranks[:nA].sum() - nA * (nA + 1) / 2) / (nA * len(b)))


def load():
    # V[(arm,patch,pair,history)] = dict seed->S_high  at t=2000
    V = defaultdict(dict)
    with open(_V11) as f:
        for r in csv.DictReader(f):
            if int(r["checkpoint"]) != CP:
                continue
            V[(r["arm"], int(r["patch"]), int(r["pair"]), r["history"])][
                int(r["seed"])] = float(r["S_high"])
    return V


def cell_auc(V, arm, i, pair, seed_idx):
    A = V[(arm, i, pair, "A")]; B = V[(arm, i, pair, "B")]
    seeds = sorted(set(A) & set(B))
    a = np.array([A[s] for s in seeds]); b = np.array([B[s] for s in seeds])
    return auc(a[seed_idx], b[seed_idx])


def patch_auc(V, arm, i, seed_idx):
    return float(np.mean([cell_auc(V, arm, i, p, seed_idx) for p in range(NPAIRS)]))


def main():
    V = load()
    n_seeds = len(set(s for d in V.values() for s in d))
    base_idx = np.arange(n_seeds)

    def contrasts(seed_idx):
        reg = [patch_auc(V, "regular", i, seed_idx) for i in range(3)]
        per = [patch_auc(V, "perturbed", i, seed_idx) for i in range(3)]
        con = [per[i] - reg[i] for i in range(3)]
        return reg, per, con, float(np.mean(con))

    reg0, per0, con0, mean0 = contrasts(base_idx)

    # seed bootstrap (shared across all cells/arms)
    rng = np.random.default_rng(2024)
    B = 4000
    con_bs = np.zeros((B, 3)); mean_bs = np.zeros(B)
    reg_bs = np.zeros((B, 3)); per_bs = np.zeros((B, 3))
    for k in range(B):
        idx = rng.integers(0, n_seeds, n_seeds)
        r, p, c, m = contrasts(idx)
        reg_bs[k] = r; per_bs[k] = p; con_bs[k] = c; mean_bs[k] = m

    def ci(x):
        return float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))

    rows = ["quantity,offset,point,ci_lo,ci_hi"]
    for i in range(3):
        rows.append(f"regular_AUC,{i},{reg0[i]:.4f},{ci(reg_bs[:,i])[0]:.4f},{ci(reg_bs[:,i])[1]:.4f}")
        rows.append(f"perturbed_AUC,{i},{per0[i]:.4f},{ci(per_bs[:,i])[0]:.4f},{ci(per_bs[:,i])[1]:.4f}")
        rows.append(f"contrast_perturbed_minus_regular,{i},{con0[i]:.4f},{ci(con_bs[:,i])[0]:.4f},{ci(con_bs[:,i])[1]:.4f}")
    rows.append(f"mean_contrast,all,{mean0:.4f},{ci(mean_bs)[0]:.4f},{ci(mean_bs)[1]:.4f}")
    out = os.path.join(_HERE, "results", "matched_contrasts_t2000.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("\n".join(rows) + "\n")

    print(f"t={CP} matched-offset contrasts (seed-bootstrap CI, patches fixed; "
          f"n_seeds={n_seeds}, B={B}):")
    for i in range(3):
        lo, hi = ci(con_bs[:, i])
        print(f"  offset {i}: regular {reg0[i]:.3f}  perturbed {per0[i]:.3f}  "
              f"contrast {con0[i]:+.3f} [{lo:+.3f},{hi:+.3f}]")
    lo, hi = ci(mean_bs)
    print(f"  MEAN contrast (perturbed-regular): {mean0:+.4f} [{lo:+.4f},{hi:+.4f}]")
    print(f"  -> wrote {out}")


if __name__ == "__main__":
    main()
