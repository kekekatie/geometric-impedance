#!/usr/bin/env python3
"""
Accretion pilot v3 -- finite-precision readout.

We change ONLY the reader, not the world. v3 imports v2's dynamics
(../v2_saturation/accretion_pilot_v2.py) and replays the identical trajectories
(same World, same rules, same seeds, same RNG streams, same
activation-time-and-count matched control), capturing the weight of every present
edge at each v2 checkpoint. It then reads those weights through a deterministic
quantiser at several resolutions and recomputes the history contrast M.

    w_read = Delta * floor(w / Delta + 0.5)      (Delta = 0 -> exact weight)
    Delta  in { 0, 0.001, 0.01, 0.1, 0.5, 1.0 }  (absolute, on the 1..6 scale)

For Delta > 0 the measured contrast is  M = Delta * (integer sum of signed bin
counts); the sign is computed in exact integer arithmetic so float rounding
cannot manufacture a residual sign.

Measurement never alters weights, movement, growth, or random streams. A
validation gate reproduces v2's exact-reader M per seed before any degraded
reading is analysed.

Speculative exploration; not a confirmatory study or a test of cosmology.

Reproduce:
    python accretion_pilot_v3.py
    python accretion_pilot_v3.py --quick    # 20 seeds, 1000 steps
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

# --- import v2 dynamics unchanged ------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_V2DIR = os.path.join(os.path.dirname(_HERE), "v2_saturation")
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

# --- v3 reader configuration (declared before execution) -------------------
DELTAS = (0.0, 0.001, 0.01, 0.1, 0.5, 1.0)
BOOTSTRAP_CPS = (400, 2000, 10000)
HIST = {"A": "upper", "B": "lower"}


# ---------------------------------------------------------------------------
# The imperfect reader
# ---------------------------------------------------------------------------
def measured_M(weight, delta):
    """History contrast from quantised weights, canonical order, exact sign.

    weight: dict edge_key -> weight (present edges only).
    For delta > 0: M = delta * sum_e sign(e) * round_half_up(w/delta), the sum
    an exact Python integer. For delta == 0: fsum over canonical edge order.
    """
    items = sorted(weight.items())                     # canonical edge order
    if delta == 0.0:
        return math.fsum(v2.edge_midpoint_sign(e) * w for e, w in items)
    acc = 0                                             # exact integer
    for e, w in items:
        s = v2.edge_midpoint_sign(e)
        if s == 0.0:
            continue
        n = math.floor(w / delta + 0.5)                # round-half-up bin count
        acc += int(s) * n
    return delta * acc


def read_all_deltas(weight):
    return {d: measured_M(weight, d) for d in DELTAS}


# ---------------------------------------------------------------------------
# Replays that mirror v2 exactly but capture weights (no RNG consumed by reads)
# ---------------------------------------------------------------------------
def _capture(world, checkpoints, step, out):
    if step in checkpoints:
        out[step] = read_all_deltas(world.weight)


def replay_growing(history_kind, seed, checkpoints, n_steps):
    world = v2.World()
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    events = []
    for u, v in history_edges(history_kind):
        before = world.n_activations
        world.reinforce(u, v)
        world.grow_from_edge(u, v)
        events.append(world.n_activations - before)
    out = {}
    _capture(world, checkpoints, 0, out)
    vtx = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, vtx, walk_rng)
        before = world.n_activations
        world.reinforce(vtx, nxt)
        world.grow_from_edge(vtx, nxt)
        events.append(world.n_activations - before)
        vtx = nxt
        _capture(world, checkpoints, step, out)
    return out, events


def replay_control(history_kind, seed, events, checkpoints, n_steps):
    world = v2.World()
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    place_rng = np.random.default_rng(BASE_SEED + seed + CONTROL_PLACEMENT_OFFSET)
    ei, cum = 0, 0
    for u, v in history_edges(history_kind):
        world.reinforce(u, v)
        k = events[ei]; ei += 1
        world.activate_random(k, place_rng)
        cum += k
        assert world.n_activations == cum
    out = {}
    _capture(world, checkpoints, 0, out)
    vtx = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, vtx, walk_rng)
        world.reinforce(vtx, nxt)
        k = events[ei]; ei += 1
        world.activate_random(k, place_rng)
        cum += k
        vtx = nxt
        assert world.n_activations == cum
        _capture(world, checkpoints, step, out)
    return out


def replay_simple(model, history_kind, seed, checkpoints, n_steps):
    if model == "Fixed":
        snap = read_all_deltas(v2.World().weight)
        return {cp: dict(snap) for cp in checkpoints}
    world = v2.World()                                  # Reinforced
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    for u, v in history_edges(history_kind):
        world.reinforce(u, v)
    out = {}
    _capture(world, checkpoints, 0, out)
    vtx = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, vtx, walk_rng)
        world.reinforce(vtx, nxt)
        vtx = nxt
        _capture(world, checkpoints, step, out)
    return out


# ---------------------------------------------------------------------------
# Statistics on measured M
# ---------------------------------------------------------------------------
def auc(mA, mB):
    mA, mB = np.asarray(mA, float), np.asarray(mB, float)
    allv = np.concatenate([mA, mB])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv), float)
    ranks[order] = np.arange(1, len(allv) + 1)
    _, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts)); np.add.at(sums, inv, ranks)
    ranks = (sums / counts)[inv]
    nA = len(mA)
    return float((ranks[:nA].sum() - nA * (nA + 1) / 2.0) / (nA * len(mB)))


def paired_frac(mA, mB):
    d = np.asarray(mA, float) - np.asarray(mB, float)
    return float(np.mean((d > 0) * 1.0 + (d == 0) * 0.5))


def tie_frac(mA, mB):
    d = np.asarray(mA, float) - np.asarray(mB, float)
    return float(np.mean(d == 0))


def balanced_accuracy(mA, mB):
    """Single-world decoder: A if M>0, B if M<0, half credit if 0. Balanced."""
    mA, mB = np.asarray(mA, float), np.asarray(mB, float)
    recall_A = np.mean((mA > 0) * 1.0 + (mA == 0) * 0.5)
    recall_B = np.mean((mB < 0) * 1.0 + (mB == 0) * 0.5)
    return float((recall_A + recall_B) / 2.0)


def bootstrap_auc_diff(A1, B1, A2, B2, n_boot=2000, seed=888):
    A1, B1, A2, B2 = map(lambda x: np.asarray(x, float), (A1, B1, A2, B2))
    point = auc(A1, B1) - auc(A2, B2)
    n = len(A1)
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[k] = auc(A1[idx], B1[idx]) - auc(A2[idx], B2[idx])
    return point, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


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

    # data[model][hlabel][cp][delta] = list over seeds of measured M
    data = {m: {"A": defaultdict(lambda: defaultdict(list)),
                "B": defaultdict(lambda: defaultdict(list))} for m in MODELS}

    for seed in range(n_seeds):
        for hlabel in ("A", "B"):
            hk = HIST[hlabel]
            g_out, events = replay_growing(hk, seed, checkpoints, n_steps)
            c_out = replay_control(hk, seed, events, checkpoints, n_steps)
            f_out = replay_simple("Fixed", hk, seed, checkpoints, n_steps)
            r_out = replay_simple("Reinforced", hk, seed, checkpoints, n_steps)
            for model, out in (("Growing", g_out),
                               ("Growing-MatchedControl", c_out),
                               ("Fixed", f_out), ("Reinforced", r_out)):
                for cp, dmap in out.items():
                    for d, m in dmap.items():
                        data[model][hlabel][cp][d].append(m)
        if (seed + 1) % 25 == 0:
            print(f"  ... {seed + 1}/{n_seeds} seeds")

    validate_vs_v2(results_dir, data, checkpoints)
    write_tables(results_dir, data, checkpoints, n_seeds, n_steps)
    make_figure(figures_dir, data, checkpoints)
    console_summary(data, checkpoints)
    print(f"\nWrote results/ and figures/ under {args.outdir}")


def validate_vs_v2(results_dir, data, checkpoints):
    """Exact reader (Delta=0) M must reproduce v2's saved M, per seed."""
    v2raw = os.path.join(_V2DIR, "results", "raw_metrics.csv")
    lines = ["# v3 exact-reader (Delta=0) reproduction of v2 M, per seed"]
    ok = True
    if not os.path.exists(v2raw):
        lines.append(f"# v2 raw_metrics.csv not found: {v2raw}")
        ok = False
    else:
        v2M = {}
        with open(v2raw) as f:
            for r in csv.DictReader(f):
                v2M[(r["model"], int(r["seed"]), r["history"],
                     int(r["checkpoint"]))] = float(r["M"])
        max_diff, n = 0.0, 0
        for model in MODELS:
            for hlabel in ("A", "B"):
                for cp in checkpoints:
                    xs = data[model][hlabel][cp][0.0]
                    for k, m in enumerate(xs):
                        key = (model, k, hlabel, cp)
                        if key in v2M:
                            max_diff = max(max_diff, abs(m - v2M[key])); n += 1
        ok = max_diff < 1e-4
        lines.append(f"# compared {n} exact-M values; max_abs_diff = {max_diff:.3e}; "
                     f"tolerance 1e-4 (v2 CSV rounding); "
                     f"status = {'PASS' if ok else 'FAIL'}")
        lines.append("# measurement reads copies of weights only; dynamics, "
                     "movement, growth and RNG streams are v2's, unchanged.")
    lines.append(f"# overall: {'PASS' if ok else 'CHECK'}")
    with open(os.path.join(results_dir, "validation_vs_v2.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("v2 exact-reader reproduction:", "PASS" if ok else "CHECK validation_vs_v2.txt")


def write_tables(results_dir, data, checkpoints, n_seeds, n_steps):
    # raw measured M
    raw = ["model,seed,history,checkpoint,delta,M_measured"]
    for model in MODELS:
        for hlabel in ("A", "B"):
            for cp in checkpoints:
                for d in DELTAS:
                    for k, m in enumerate(data[model][hlabel][cp][d]):
                        raw.append(f"{model},{k},{hlabel},{cp},{d},{m:.10g}")
    with open(os.path.join(results_dir, "raw_measured_M.csv"), "w") as f:
        f.write("\n".join(raw) + "\n")

    # summary per (model, checkpoint, delta)
    summ = ["model,checkpoint,delta,auc,paired_frac,tie_frac,signed_sep,balanced_acc"]
    for model in MODELS:
        for cp in checkpoints:
            for d in DELTAS:
                mA = data[model]["A"][cp][d]
                mB = data[model]["B"][cp][d]
                summ.append(f"{model},{cp},{d},{auc(mA, mB):.4f},"
                            f"{paired_frac(mA, mB):.4f},{tie_frac(mA, mB):.4f},"
                            f"{np.mean(mA) - np.mean(mB):.6f},"
                            f"{balanced_accuracy(mA, mB):.4f}")
    with open(os.path.join(results_dir, "summary_by_resolution.csv"), "w") as f:
        f.write("\n".join(summ) + "\n")

    # between-model AUC differences with bootstrap, per resolution
    bl = ["comparison,checkpoint,delta,auc_diff,ci_lo,ci_hi"]
    for m1, m2 in (("Growing", "Growing-MatchedControl"), ("Growing", "Reinforced")):
        for cp in [c for c in BOOTSTRAP_CPS if c in checkpoints]:
            for d in DELTAS:
                p, lo, hi = bootstrap_auc_diff(
                    data[m1]["A"][cp][d], data[m1]["B"][cp][d],
                    data[m2]["A"][cp][d], data[m2]["B"][cp][d])
                bl.append(f"{m1}_vs_{m2},{cp},{d},{p:.4f},{lo:.4f},{hi:.4f}")
    with open(os.path.join(results_dir, "bootstrap_auc_diffs_by_resolution.csv"), "w") as f:
        f.write("\n".join(bl) + "\n")

    cfg = {"deltas": list(DELTAS), "checkpoints": list(checkpoints),
           "n_seeds": n_seeds, "n_steps": n_steps, "models": list(MODELS),
           "reader": "w_read = delta*floor(w/delta+0.5); delta=0 exact; "
                     "sign via exact integer bin sums",
           "v2_commit_dynamics": "cab9254b9d7713a65c314ca81f45c2d378ab60ba",
           "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    with open(os.path.join(results_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)


def make_figure(figures_dir, data, checkpoints):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"Fixed": "#888888", "Reinforced": "#1f77b4",
              "Growing": "#d62728", "Growing-MatchedControl": "#2ca02c"}
    early = 400 if 400 in checkpoints else checkpoints[min(3, len(checkpoints) - 1)]
    late = checkpoints[-1]
    rows = [("early (t=%d)" % early, early), ("late (t=%d)" % late, late)]
    xlabels = ["exact" if d == 0 else f"{d:g}" for d in DELTAS]
    x = np.arange(len(DELTAS))

    fig, axes = plt.subplots(2, 3, figsize=(17, 9.5))
    metric_fns = [("Discrimination AUC (measured M)", auc, (0.45, 1.02), 0.5),
                  ("Single-world balanced accuracy", balanced_accuracy, (0.45, 1.02), 0.5),
                  ("Paired tie fraction (M_A == M_B)", tie_frac, (-0.03, 1.03), None)]
    for ri, (rlabel, cp) in enumerate(rows):
        for ci, (title, fn, ylim, chance) in enumerate(metric_fns):
            ax = axes[ri, ci]
            for model in MODELS:
                ys = [fn(data[model]["A"][cp][d], data[model]["B"][cp][d])
                      for d in DELTAS]
                ax.plot(x, ys, "-o", color=colors[model], label=model)
            # exact-readout reference (Delta=0 value) as a dashed horizontal line
            for model in MODELS:
                y0 = fn(data[model]["A"][cp][DELTAS[0]], data[model]["B"][cp][DELTAS[0]])
                ax.axhline(y0, color=colors[model], ls=":", lw=0.6, alpha=0.5)
            if chance is not None:
                ax.axhline(chance, color="k", ls="--", lw=0.8)
            ax.set_xticks(x); ax.set_xticklabels(xlabels)
            ax.set_ylim(*ylim)
            ax.set_title(f"{rlabel}: {title}", fontsize=10)
            ax.set_xlabel("weight-read resolution  Delta")
            if ci == 0:
                ax.legend(fontsize=7)
    fig.suptitle("v3 finite-precision readout: history discrimination vs weight "
                 "resolution\n(dotted lines = each model's exact-reader reference; "
                 "dashed = chance)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(figures_dir, "discrimination_vs_resolution_v3.png"), dpi=140)
    plt.close(fig)


def console_summary(data, checkpoints):
    print("=" * 78)
    print("v3 finite-precision readout -- AUC(measured M) by resolution")
    hdr = "  " + " ".join(f"D={d:g}".rjust(8) for d in DELTAS)
    for cp in (400, 10000):
        if cp not in checkpoints:
            continue
        print(f"- checkpoint t={cp}:")
        print("  model".ljust(26) + hdr)
        for model in MODELS:
            vals = " ".join(f"{auc(data[model]['A'][cp][d], data[model]['B'][cp][d]):8.3f}"
                            for d in DELTAS)
            print(f"  {model:24s} {vals}")
    print("=" * 78)


if __name__ == "__main__":
    main()
