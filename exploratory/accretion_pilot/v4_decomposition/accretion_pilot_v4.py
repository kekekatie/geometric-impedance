#!/usr/bin/env python3
"""
Accretion pilot v4 -- reader decomposition.

We change ONLY the reader, not the world. v4 imports v2's dynamics
(../v2_saturation/accretion_pilot_v2.py), replays the identical v2 worlds (200
seed pairs, original checkpoints, activation-time-and-count matched control),
captures the FULL per-edge weight snapshot at each checkpoint (retained to
results/edge_snapshots.npz for future reader-only analyses), and decomposes the
history readout to locate where its discrimination comes from:

  presence only     P    = sum s(e)                 over present edges (weight 1)
  original-edge     B_D  = sum s(e)*q_D(w_e)         over present base grid edges
  added-edge        D_D  = sum s(e)*q_D(w_e)         over activated diagonals
  full (v3 reader)  M_D  = B_D + D_D
  departure         R_D  = sum s(e)*(q_D(w_e) - 6)   over present edges

with s(e) the existing coordinate sign and q_D the v3 quantiser, D in {0, 1}.
Algebraic identities asserted per snapshot: M_D = B_D + D_D and M_D = 6*P + R_D.
These are decompositions of the readout, not established mechanisms.

Motivation / correction: at t=10000, 399/400 Growing worlds have all 128
candidate diagonals active (2 missing total), so topology is essentially identical
across worlds; the v3 "topological memory" reading is withdrawn. This run asks
whether the discrimination lives in presence, original-edge weights, or added-edge
weights.

Speculative exploration; not a confirmatory study or a test of cosmology.

Reproduce:
    python accretion_pilot_v4.py
    python accretion_pilot_v4.py --quick     # 20 seeds, 1000 steps
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V2DIR = os.path.join(os.path.dirname(_HERE), "v2_saturation")
_V3DIR = os.path.join(os.path.dirname(_HERE), "v3_precision")
sys.path.insert(0, _V2DIR)
import accretion_pilot_v2 as v2   # noqa: E402

BASE_SEED = v2.BASE_SEED
CONTROL_PLACEMENT_OFFSET = v2.CONTROL_PLACEMENT_OFFSET
CHECKPOINTS = v2.CHECKPOINTS
MODELS = v2.MODELS
PROBE = v2.PROBE
W_MAX = v2.W_MAX
vid = v2.vid
weighted_step = v2.weighted_step
history_edges = v2.history_edges

HIST = {"A": "upper", "B": "lower"}
DELTAS = (0, 1)                       # exact and whole-number quantiser
BOOTSTRAP_CPS = (400, 2000, 10000)
N_CANDIDATES = v2.N_CANDIDATES        # 128

# --- fixed edge universe: base (original) edges then candidate (added) edges ---
_BASE = list(v2.build_base_edges())                       # 144 original edges
_CAND = [e for (_c, e) in v2.build_candidates()]          # 128 candidate edges
UNIVERSE = _BASE + _CAND
N_UNIV = len(UNIVERSE)
IS_ORIGINAL = np.array([True] * len(_BASE) + [False] * len(_CAND))
SIGNS = np.array([v2.edge_midpoint_sign(e) for e in UNIVERSE], dtype=float)
UIDX = {e: i for i, e in enumerate(UNIVERSE)}


def qD(w, delta):
    if delta == 0:
        return w
    return np.floor(w + 0.5)          # Delta = 1 whole-number quantiser


# ---------------------------------------------------------------------------
# Replays that mirror v2 exactly but capture the full weight vector
# ---------------------------------------------------------------------------
def _vec(world):
    v = np.zeros(N_UNIV, dtype=np.float64)     # 0.0 == edge absent
    for e, w in world.weight.items():
        v[UIDX[e]] = w
    return v


def _cap(world, checkpoints, step, out):
    if step in checkpoints:
        out[step] = _vec(world)


def replay_growing(hk, seed, checkpoints, n_steps):
    world = v2.World()
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    events = []
    for u, v in history_edges(hk):
        before = world.n_activations
        world.reinforce(u, v)
        world.grow_from_edge(u, v)
        events.append(world.n_activations - before)
    out = {}
    _cap(world, checkpoints, 0, out)
    vtx = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, vtx, walk_rng)
        before = world.n_activations
        world.reinforce(vtx, nxt)
        world.grow_from_edge(vtx, nxt)
        events.append(world.n_activations - before)
        vtx = nxt
        _cap(world, checkpoints, step, out)
    return out, events


def replay_control(hk, seed, events, checkpoints, n_steps):
    world = v2.World()
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    place_rng = np.random.default_rng(BASE_SEED + seed + CONTROL_PLACEMENT_OFFSET)
    ei, cum = 0, 0
    for u, v in history_edges(hk):
        world.reinforce(u, v)
        k = events[ei]; ei += 1
        world.activate_random(k, place_rng)
        cum += k
        assert world.n_activations == cum
    out = {}
    _cap(world, checkpoints, 0, out)
    vtx = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, vtx, walk_rng)
        world.reinforce(vtx, nxt)
        k = events[ei]; ei += 1
        world.activate_random(k, place_rng)
        cum += k
        vtx = nxt
        assert world.n_activations == cum
        _cap(world, checkpoints, step, out)
    return out


def replay_simple(model, hk, seed, checkpoints, n_steps):
    if model == "Fixed":
        v = _vec(v2.World())
        return {cp: v.copy() for cp in checkpoints}
    world = v2.World()
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    for u, v in history_edges(hk):
        world.reinforce(u, v)
    out = {}
    _cap(world, checkpoints, 0, out)
    vtx = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, vtx, walk_rng)
        world.reinforce(vtx, nxt)
        vtx = nxt
        _cap(world, checkpoints, step, out)
    return out


# ---------------------------------------------------------------------------
# Readers from a weight vector (present == weight>0)
# ---------------------------------------------------------------------------
def readers(vec, delta):
    present = vec > 0.0
    if delta == 0:
        # numerically stable exact sums over present edges, canonical order
        idx = np.nonzero(present)[0]
        P = float(math.fsum(SIGNS[i] for i in idx))
        B = float(math.fsum(SIGNS[i] * vec[i] for i in idx if IS_ORIGINAL[i]))
        D = float(math.fsum(SIGNS[i] * vec[i] for i in idx if not IS_ORIGINAL[i]))
        M = float(math.fsum(SIGNS[i] * vec[i] for i in idx))
        R = float(math.fsum(SIGNS[i] * (vec[i] - 6.0) for i in idx))
        return {"P": P, "B": B, "D": D, "M": M, "R": R}
    # Delta = 1: exact integer arithmetic
    q = np.floor(vec + 0.5).astype(np.int64)
    s = SIGNS.astype(np.int64)
    pres = present
    P = int((s[pres]).sum())
    B = int((s * q * IS_ORIGINAL)[pres].sum())
    D = int((s * q * (~IS_ORIGINAL))[pres].sum())
    M = int((s * q)[pres].sum())
    R = int((s * (q - 6))[pres].sum())
    return {"P": P, "B": B, "D": D, "M": M, "R": R}


def check_identities(vec):
    ok = True
    for delta in DELTAS:
        r = readers(vec, delta)
        if delta == 0:
            ok &= abs(r["M"] - (r["B"] + r["D"])) < 1e-9
            ok &= abs(r["M"] - (6.0 * r["P"] + r["R"])) < 1e-9
        else:
            ok &= r["M"] == r["B"] + r["D"]
            ok &= r["M"] == 6 * r["P"] + r["R"]
    return ok


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def auc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    allv = np.concatenate([a, b])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv), float)
    ranks[order] = np.arange(1, len(allv) + 1)
    _, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts)); np.add.at(sums, inv, ranks)
    ranks = (sums / counts)[inv]
    nA = len(a)
    return float((ranks[:nA].sum() - nA * (nA + 1) / 2.0) / (nA * len(b)))


def paired_frac(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(np.mean((d > 0) * 1.0 + (d == 0) * 0.5))


def tie_frac(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(np.mean(d == 0))


def bal_acc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rA = np.mean((a > 0) * 1.0 + (a == 0) * 0.5)
    rB = np.mean((b < 0) * 1.0 + (b == 0) * 0.5)
    return float((rA + rB) / 2.0)


def boot_auc(a, b, n_boot=2000, seed=101):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = len(a); rng = np.random.default_rng(seed)
    bs = np.array([auc(a[i], b[i]) for i in (rng.integers(0, n, n) for _ in range(n_boot))])
    return auc(a, b), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def boot_auc_diff(a1, b1, a2, b2, n_boot=2000, seed=202):
    a1, b1, a2, b2 = map(lambda x: np.asarray(x, float), (a1, b1, a2, b2))
    n = len(a1); rng = np.random.default_rng(seed)
    pt = auc(a1, b1) - auc(a2, b2)
    bs = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, n)
        bs[k] = auc(a1[idx], b1[idx]) - auc(a2[idx], b2[idx])
    return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--steps", type=int, default=v2.T_SUB)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--outdir", default=_HERE)
    args = ap.parse_args()
    n_seeds = 20 if args.quick else args.seeds
    n_steps = 1000 if args.quick else args.steps
    checkpoints = tuple(cp for cp in CHECKPOINTS if cp <= n_steps)
    results_dir = os.path.join(args.outdir, "results")
    figures_dir = os.path.join(args.outdir, "figures")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # snap[model][hist][cp] = array (n_seeds, N_UNIV)
    snap = {m: {"A": {}, "B": {}} for m in MODELS}
    tmp = {m: {"A": defaultdict(list), "B": defaultdict(list)} for m in MODELS}
    identity_ok = True

    for seed in range(n_seeds):
        for hlabel in ("A", "B"):
            hk = HIST[hlabel]
            g_out, events = replay_growing(hk, seed, checkpoints, n_steps)
            c_out = replay_control(hk, seed, events, checkpoints, n_steps)
            f_out = replay_simple("Fixed", hk, seed, checkpoints, n_steps)
            r_out = replay_simple("Reinforced", hk, seed, checkpoints, n_steps)
            for model, out in (("Growing", g_out), ("Growing-MatchedControl", c_out),
                               ("Fixed", f_out), ("Reinforced", r_out)):
                for cp, vec in out.items():
                    tmp[model][hlabel][cp].append(vec)
                    if seed < 3:                      # spot-check identities
                        identity_ok &= check_identities(vec)
        if (seed + 1) % 25 == 0:
            print(f"  ... {seed + 1}/{n_seeds} seeds")

    for m in MODELS:
        for hl in ("A", "B"):
            for cp in checkpoints:
                snap[m][hl][cp] = np.array(tmp[m][hl][cp], dtype=np.float64)

    print("Per-snapshot algebraic identities (M=B+D and M=6P+R):",
          "PASS" if identity_ok else "FAIL")

    save_snapshots(results_dir, snap, checkpoints, n_seeds)
    validate_vs_v3(results_dir, snap, checkpoints)
    reader_vals = compute_readers(snap, checkpoints)
    write_tables(results_dir, reader_vals, snap, checkpoints, n_seeds, n_steps, identity_ok)
    complete_topology_subset(results_dir, snap, reader_vals, checkpoints)
    make_figure(figures_dir, reader_vals, checkpoints)
    console_summary(reader_vals, checkpoints)
    print(f"\nWrote results/ and figures/ under {args.outdir}")


def save_snapshots(results_dir, snap, checkpoints, n_seeds):
    arrays = {"universe_u": np.array([e[0] for e in UNIVERSE]),
              "universe_v": np.array([e[1] for e in UNIVERSE]),
              "is_original": IS_ORIGINAL, "signs": SIGNS,
              "checkpoints": np.array(checkpoints), "n_seeds": np.array(n_seeds)}
    for m in MODELS:
        for hl in ("A", "B"):
            for cp in checkpoints:
                arrays[f"{m}__{hl}__{cp}"] = snap[m][hl][cp].astype(np.float64)
    path = os.path.join(results_dir, "edge_snapshots.npz")
    np.savez_compressed(path, **arrays)
    print(f"Retained full edge snapshots -> {os.path.basename(path)} "
          f"({os.path.getsize(path) / 1e6:.1f} MB)")


def compute_readers(snap, checkpoints):
    """reader_vals[model][hist][cp][reader_name] = np.array over seeds."""
    rv = {m: {"A": {}, "B": {}} for m in MODELS}
    names = ["P", "B0", "D0", "M0", "R0", "B1", "D1", "M1", "R1"]
    for m in MODELS:
        for hl in ("A", "B"):
            for cp in checkpoints:
                arr = snap[m][hl][cp]
                cols = {n: [] for n in names}
                for vec in arr:
                    r0 = readers(vec, 0)
                    r1 = readers(vec, 1)
                    cols["P"].append(r0["P"])
                    cols["B0"].append(r0["B"]); cols["D0"].append(r0["D"])
                    cols["M0"].append(r0["M"]); cols["R0"].append(r0["R"])
                    cols["B1"].append(r1["B"]); cols["D1"].append(r1["D"])
                    cols["M1"].append(r1["M"]); cols["R1"].append(r1["R"])
                rv[m][hl][cp] = {n: np.array(v, float) for n, v in cols.items()}
    return rv


def validate_vs_v3(results_dir, snap, checkpoints):
    """M0 and M1 must reproduce v3's full-reader values, full coverage."""
    v3raw = os.path.join(_V3DIR, "results", "raw_measured_M.csv")
    lines = ["# v4 reproduction of v3 full reader (M at Delta=0 and Delta=1)"]
    ok = True
    if not os.path.exists(v3raw):
        lines.append(f"# v3 raw_measured_M.csv not found: {v3raw}"); ok = False
    else:
        v3 = {}
        with open(v3raw) as f:
            for r in csv.DictReader(f):
                d = float(r["delta"])
                if d in (0.0, 1.0):
                    v3[(r["model"], int(r["seed"]), r["history"],
                        int(r["checkpoint"]), int(d))] = float(r["M_measured"])
        maxd0 = maxd1 = 0.0; n = 0
        for m in MODELS:
            for hl in ("A", "B"):
                for cp in checkpoints:
                    arr = snap[m][hl][cp]
                    for k, vec in enumerate(arr):
                        m0 = readers(vec, 0)["M"]; m1 = readers(vec, 1)["M"]
                        k0 = (m, k, hl, cp, 0); k1 = (m, k, hl, cp, 1)
                        if k0 in v3:
                            maxd0 = max(maxd0, abs(m0 - v3[k0])); n += 1
                        if k1 in v3:
                            maxd1 = max(maxd1, abs(m1 - v3[k1]))
        ok = (maxd0 < 1e-6) and (maxd1 < 1e-9)
        lines.append(f"# coverage: {n} (model,hist,seed,checkpoint) values")
        lines.append(f"# max|dM| Delta=0 = {maxd0:.3e} (tol 1e-6); "
                     f"Delta=1 = {maxd1:.3e} (tol 1e-9, exact integer); "
                     f"status = {'PASS' if ok else 'FAIL'}")
        lines.append("# measurement reads copies of weights; dynamics/movement/"
                     "growth/RNG are v2's, unchanged.")
    lines.append(f"# overall: {'PASS' if ok else 'CHECK'}")
    with open(os.path.join(results_dir, "validation_vs_v3.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("v3 full-reader reproduction:", "PASS" if ok else "CHECK validation_vs_v3.txt")


READER_SET = [("presence", "P"), ("original_B0", "B0"), ("added_D0", "D0"),
              ("full_M0", "M0"), ("departure_R0", "R0"), ("original_B1", "B1"),
              ("added_D1", "D1"), ("full_M1", "M1"), ("departure_R1", "R1")]


def write_tables(results_dir, rv, snap, checkpoints, n_seeds, n_steps, identity_ok):
    summ = ["model,checkpoint,reader,auc,paired_frac,tie_frac,bal_acc,signed_sep"]
    for m in MODELS:
        for cp in checkpoints:
            for label, key in READER_SET:
                a = rv[m]["A"][cp][key]; b = rv[m]["B"][cp][key]
                summ.append(f"{m},{cp},{label},{auc(a,b):.4f},{paired_frac(a,b):.4f},"
                            f"{tie_frac(a,b):.4f},{bal_acc(a,b):.4f},"
                            f"{np.mean(a)-np.mean(b):.6f}")
    with open(os.path.join(results_dir, "summary_by_reader.csv"), "w") as f:
        f.write("\n".join(summ) + "\n")

    # bootstrap: reader AUCs and Growing-minus-control AUC diffs
    bl = ["quantity,comparison_or_model,reader,checkpoint,point,ci_lo,ci_hi"]
    for cp in [c for c in BOOTSTRAP_CPS if c in checkpoints]:
        for label, key in READER_SET:
            for m in MODELS:
                p, lo, hi = boot_auc(rv[m]["A"][cp][key], rv[m]["B"][cp][key])
                bl.append(f"reader_auc,{m},{label},{cp},{p:.4f},{lo:.4f},{hi:.4f}")
            p, lo, hi = boot_auc_diff(
                rv["Growing"]["A"][cp][key], rv["Growing"]["B"][cp][key],
                rv["Growing-MatchedControl"]["A"][cp][key],
                rv["Growing-MatchedControl"]["B"][cp][key])
            bl.append(f"growing_minus_control_auc,Growing_vs_Control,{label},{cp},"
                      f"{p:.4f},{lo:.4f},{hi:.4f}")
    with open(os.path.join(results_dir, "bootstrap_by_reader.csv"), "w") as f:
        f.write("\n".join(bl) + "\n")

    cfg = {"deltas": list(DELTAS), "checkpoints": list(checkpoints),
           "n_seeds": n_seeds, "n_steps": n_steps, "models": list(MODELS),
           "readers": "P, B_D (original), D_D (added), M_D=B_D+D_D (full), "
                      "R_D=sum s(qw-6); identities M=B+D and M=6P+R asserted",
           "identity_check": "PASS" if identity_ok else "FAIL",
           "v2_commit_dynamics": "cab9254b9d7713a65c314ca81f45c2d378ab60ba",
           "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    with open(os.path.join(results_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)


def complete_topology_subset(results_dir, snap, rv, checkpoints):
    """t=10000: counts of complete worlds + discrimination on complete-only pairs."""
    cp = max(checkpoints)
    lines = ["# Complete-topology subset at t=%d (DESCRIPTIVE, selected after "
             "evolution; not a matched causal comparison)." % cp,
             "# A world is 'complete' iff all %d candidate diagonals are present." % N_CANDIDATES,
             "model,history,n_worlds,n_complete,total_missing_candidates"]
    complete_mask = {}
    for m in MODELS:
        for hl in ("A", "B"):
            arr = snap[m][hl][cp]
            cand_present = (arr[:, ~IS_ORIGINAL] > 0).sum(axis=1)  # per world
            comp = cand_present == N_CANDIDATES
            complete_mask[(m, hl)] = comp
            lines.append(f"{m},{hl},{len(comp)},{int(comp.sum())},"
                         f"{int((N_CANDIDATES - cand_present).sum())}")
    lines.append("")
    lines.append("# Paired discrimination restricted to pairs where BOTH A and B "
                 "worlds are complete:")
    lines.append("model,reader,n_pairs_included,auc,paired_frac,tie_frac,bal_acc,signed_sep")
    for m in MODELS:
        both = complete_mask[(m, "A")] & complete_mask[(m, "B")]
        n_inc = int(both.sum())
        for label, key in [("full_M0", "M0"), ("full_M1", "M1"),
                           ("departure_R0", "R0"), ("departure_R1", "R1"),
                           ("presence", "P")]:
            a = rv[m]["A"][cp][key][both]; b = rv[m]["B"][cp][key][both]
            if n_inc == 0:
                lines.append(f"{m},{label},0,nan,nan,nan,nan,nan"); continue
            lines.append(f"{m},{label},{n_inc},{auc(a,b):.4f},{paired_frac(a,b):.4f},"
                         f"{tie_frac(a,b):.4f},{bal_acc(a,b):.4f},"
                         f"{np.mean(a)-np.mean(b):.6f}")
    with open(os.path.join(results_dir, "complete_topology_subset.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


def make_figure(figures_dir, rv, checkpoints):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cps = list(checkpoints)
    rcolors = {"P": "#9467bd", "B": "#1f77b4", "D": "#ff7f0e",
               "M": "#d62728", "R": "#17becf"}
    mcolors = {"Fixed": "#888888", "Reinforced": "#1f77b4",
               "Growing": "#d62728", "Growing-MatchedControl": "#2ca02c"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    def plot_readers(ax, model, delta):
        suffix = str(delta)
        series = [("presence P", "P"), ("original edges B", "B" + suffix),
                  ("added edges D", "D" + suffix), ("full M", "M" + suffix)]
        for lbl, key in series:
            ys = [auc(rv[model]["A"][cp][key], rv[model]["B"][cp][key]) for cp in cps]
            col = rcolors[key[0]]
            ax.plot(cps, ys, "-o", color=col, label=lbl)
        ax.axhline(0.5, ls="--", color="k", lw=0.8)
        ax.set_xscale("symlog"); ax.set_ylim(0.45, 1.02)
        ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC")
        ax.legend(fontsize=8)

    plot_readers(axes[0, 0], "Growing", 0)
    axes[0, 0].set_title("Growing, EXACT reader (Delta=0): where is the signal?")
    plot_readers(axes[0, 1], "Growing", 1)
    axes[0, 1].set_title("Growing, WHOLE-NUMBER reader (Delta=1)")

    # departure vs full, both deltas, Growing
    ax = axes[1, 0]
    for key, lbl, ls in [("M0", "full M (exact)", "-"), ("R0", "departure R (exact)", "-"),
                         ("M1", "full M (D=1)", "--"), ("R1", "departure R (D=1)", "--")]:
        ys = [auc(rv["Growing"]["A"][cp][key], rv["Growing"]["B"][cp][key]) for cp in cps]
        col = rcolors[key[0]]
        ax.plot(cps, ys, ls, marker="o", color=col, label=lbl)
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.45, 1.02)
    ax.set_title("Growing: full M vs departure-from-saturation R\n"
                 "(near saturation the signal is in R, not in 6P)")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC"); ax.legend(fontsize=8)

    # cross-model: full M (D=1) and presence P
    ax = axes[1, 1]
    for m in MODELS:
        ys = [auc(rv[m]["A"][cp]["M1"], rv[m]["B"][cp]["M1"]) for cp in cps]
        ax.plot(cps, ys, "-o", color=mcolors[m], label=f"{m} full M(D=1)")
    for m in ("Growing", "Growing-MatchedControl"):
        ys = [auc(rv[m]["A"][cp]["P"], rv[m]["B"][cp]["P"]) for cp in cps]
        ax.plot(cps, ys, ":", color=mcolors[m], alpha=0.7, label=f"{m} presence P")
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.45, 1.02)
    ax.set_title("Cross-model: full reader vs presence-only\n(presence -> chance "
                 "late; topology is nearly complete/identical)")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC"); ax.legend(fontsize=7)

    fig.suptitle("v4 reader decomposition: presence / original-edge / added-edge / "
                 "full, over time\n(AUC is not additive; components are correlated)",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(figures_dir, "reader_decomposition_v4.png"), dpi=140)
    plt.close(fig)


def console_summary(rv, checkpoints):
    print("=" * 78)
    print("v4 reader decomposition -- AUC by reader (Growing)")
    for cp in (400, 10000):
        if cp not in checkpoints:
            continue
        print(f"- t={cp}: " + "  ".join(
            f"{lbl.split('_')[0][:4]}({key})={auc(rv['Growing']['A'][cp][key], rv['Growing']['B'][cp][key]):.3f}"
            for lbl, key in [("presence", "P"), ("orig", "B1"), ("added", "D1"),
                             ("full", "M1"), ("dep", "R1")]))
    print("=" * 78)


if __name__ == "__main__":
    main()
