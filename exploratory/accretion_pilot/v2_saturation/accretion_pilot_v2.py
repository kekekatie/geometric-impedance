#!/usr/bin/env python3
"""
Accretion pilot v2 -- timing-matched control + run toward saturation.

Bounded follow-up to v1 (../accretion_pilot/). Two changes only (see
DESIGN_NOTE_v2.md); everything else -- world, histories, rules, thresholds,
probe, observables, the original 200 seed pairs -- is unchanged and untuned.

  Change 1: the matched-resource control is now ACTIVATION-TIME-AND-COUNT
            matched. It replays Growing's per-event activation counts event by
            event (including during the imposed history), placing edges at random
            among canonically sorted inactive candidates with a separate stable
            RNG. Order at every event: traverse -> reinforce -> activate. Counts
            only, never Growing's edge identities. Cumulative counts asserted
            equal after every corresponding event.

  Change 2: subsequent evolution extended to 10,000 steps; checkpoints at
            0,100,200,400,1000,2000,5000,10000 (measurement only -- they do not
            affect the trajectory; verified on a fixture).

New observables: unused growth capacity (frac candidates inactive), weight
headroom mean(6-w), normalised memory contrast M/total_weight.

Speculative exploration, not a confirmatory study or a test of cosmology.

Single reproduction command:
    python accretion_pilot_v2.py
Add --quick for a fast smoke run (20 seeds, 1000 steps).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
from collections import deque, defaultdict

import numpy as np

# ---------------------------------------------------------------------------
# Fixed configuration -- identical to v1 except T_SUB and CHECKPOINTS.
# ---------------------------------------------------------------------------
GRID_N = 9
W0 = 1.0
ALPHA = 0.5
W_MAX = 6.0
THETA_GROW = 4.0
W_INIT = 1.0
GROW_BUDGET = 128
N_HISTORY_PASSES = 3
PROBE = (4, 4)
HOP_BUDGET = 4
PATH_LEN = 4
T_SUB = 10_000
CHECKPOINTS = (0, 100, 200, 400, 1000, 2000, 5000, 10000)
BASE_SEED = 20260905
CONTROL_PLACEMENT_OFFSET = 777_777
MODELS = ("Fixed", "Reinforced", "Growing", "Growing-MatchedControl")
N_CANDIDATES = 2 * (GRID_N - 1) * (GRID_N - 1)   # 128
BOOTSTRAP_CPS = (400, 2000, 10000)               # where paired diffs are reported


# ---------------------------------------------------------------------------
# Geometry helpers (identical to v1)
# ---------------------------------------------------------------------------
def vid(r, c):
    return r * GRID_N + c


def rc(v):
    return divmod(v, GRID_N)


def ekey(u, v):
    return (u, v) if u < v else (v, u)


def build_base_edges():
    edges = []
    for r in range(GRID_N):
        for c in range(GRID_N):
            if c + 1 < GRID_N:
                edges.append(ekey(vid(r, c), vid(r, c + 1)))
            if r + 1 < GRID_N:
                edges.append(ekey(vid(r, c), vid(r + 1, c)))
    return edges


def build_candidates():
    cands = []
    for i in range(GRID_N - 1):
        for j in range(GRID_N - 1):
            cell = (i, j)
            cands.append((cell, ekey(vid(i, j), vid(i + 1, j + 1))))
            cands.append((cell, ekey(vid(i, j + 1), vid(i + 1, j))))
    return cands


def cell_base_edges(i, j):
    return [
        ekey(vid(i, j), vid(i, j + 1)),
        ekey(vid(i + 1, j), vid(i + 1, j + 1)),
        ekey(vid(i, j), vid(i + 1, j)),
        ekey(vid(i, j + 1), vid(i + 1, j + 1)),
    ]


def edge_midpoint_sign(e):
    (ra, ca), (rb, cb) = rc(e[0]), rc(e[1])
    mi, mj = (ra + rb) / 2.0, (ca + cb) / 2.0
    if mj > mi:
        return 1.0
    if mj < mi:
        return -1.0
    return 0.0


def staircase(kind):
    r, c = 0, 0
    verts = [vid(r, c)]
    for _ in range(GRID_N - 1):
        if kind == "upper":
            c += 1; verts.append(vid(r, c))
            r += 1; verts.append(vid(r, c))
        else:
            r += 1; verts.append(vid(r, c))
            c += 1; verts.append(vid(r, c))
    return verts


# ---------------------------------------------------------------------------
# The world (v1 dynamics; activate_random now uses a canonically sorted pool)
# ---------------------------------------------------------------------------
class World:
    def __init__(self):
        self.base_edges = build_base_edges()
        self.candidates = build_candidates()
        self.weight = {e: W0 for e in self.base_edges}
        self.adj = defaultdict(list)
        for u, v in self.base_edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.active = set()
        self.inactive = {e for (_, e) in self.candidates}
        self.edge_cells = defaultdict(list)
        for i in range(GRID_N - 1):
            for j in range(GRID_N - 1):
                for be in cell_base_edges(i, j):
                    self.edge_cells[be].append((i, j))
        self.cell_cands = defaultdict(list)
        for cell, e in self.candidates:
            self.cell_cands[cell].append(e)
        self.base_edge_set = set(self.base_edges)
        self.n_activations = 0

    def reinforce(self, u, v):
        e = ekey(u, v)
        self.weight[e] += ALPHA * (W_MAX - self.weight[e])

    def _activate(self, e):
        if e not in self.inactive or self.n_activations >= GROW_BUDGET:
            return False
        self.inactive.discard(e)
        self.active.add(e)
        self.weight[e] = W_INIT
        u, v = e
        self.adj[u].append(v)
        self.adj[v].append(u)
        self.n_activations += 1
        return True

    def local_activity(self, cell):
        i, j = cell
        return sum(self.weight[be] - W0 for be in cell_base_edges(i, j))

    def grow_from_edge(self, u, v):
        """Local, label-blind growth from the just-worn base edge."""
        e = ekey(u, v)
        if e not in self.base_edge_set:
            return
        for cell in self.edge_cells[e]:
            if self.local_activity(cell) >= THETA_GROW:
                for cand in self.cell_cands[cell]:
                    if cand in self.inactive:
                        self._activate(cand)

    def activate_random(self, k, rng):
        """Activate k random inactive candidates from a canonically sorted pool."""
        if k <= 0:
            return
        pool = sorted(self.inactive)            # canonical order -> stable RNG
        k = min(k, len(pool))
        idx = rng.choice(len(pool), size=k, replace=False)
        for e in idx:
            self._activate(pool[e])

    # ---- readouts (current graph + weights only) ---------------------------
    def memory_M(self):
        return sum(edge_midpoint_sign(e) * w for e, w in self.weight.items())

    def total_weight(self):
        return sum(self.weight.values())

    def frac_inactive(self):
        return len(self.inactive) / N_CANDIDATES

    def headroom(self):
        return float(np.mean([W_MAX - w for w in self.weight.values()]))

    def frac_saturated(self):
        """Fraction of present edges rounded exactly to W_MAX in float64."""
        return float(np.mean([w == W_MAX for w in self.weight.values()]))

    def structural_access(self, source, hop_budget):
        seen = {source: 0}
        q = deque([source])
        count = 0
        while q:
            x = q.popleft()
            if seen[x] == hop_budget:
                continue
            for y in self.adj[x]:
                if y not in seen:
                    seen[y] = seen[x] + 1
                    count += 1
                    q.append(y)
        return count

    def effective_alternatives(self, source, path_len):
        hent, trans = {}, {}
        for v in self.adj:
            nb = self.adj[v]
            ws = np.array([self.weight[ekey(v, u)] for u in nb], dtype=float)
            s = ws.sum()
            if s <= 0:
                hent[v] = 0.0; trans[v] = []; continue
            p = ws / s
            hent[v] = float(-(p * np.log(p)).sum())
            trans[v] = list(zip(nb, p))
        pi = defaultdict(float); pi[source] = 1.0
        H = 0.0
        for _ in range(path_len):
            H += sum(prob * hent[v] for v, prob in pi.items())
            nxt = defaultdict(float)
            for v, prob in pi.items():
                for u, pvu in trans[v]:
                    nxt[u] += prob * pvu
            pi = nxt
        return math.exp(H)

    def snapshot(self):
        M = self.memory_M()
        tw = self.total_weight()
        return {
            "M": M,
            "M_norm": M / tw if tw > 0 else 0.0,
            "struct_access": self.structural_access(vid(*PROBE), HOP_BUDGET),
            "eff_alt": self.effective_alternatives(vid(*PROBE), PATH_LEN),
            "edge_count": len(self.weight),
            "total_weight": tw,
            "n_active": self.n_activations,
            "frac_inactive": self.frac_inactive(),
            "headroom": self.headroom(),
            "frac_saturated": self.frac_saturated(),
        }


# ---------------------------------------------------------------------------
# Dynamics (identical walk sampler and RNG seeding as v1)
# ---------------------------------------------------------------------------
def weighted_step(world, v, rng):
    nb = world.adj[v]
    ws = np.array([world.weight[ekey(v, u)] for u in nb], dtype=float)
    p = ws / ws.sum()
    return nb[rng.choice(len(nb), p=p)]


def history_edges(history_kind):
    verts = staircase(history_kind)
    seq = list(zip(verts[:-1], verts[1:]))
    return seq * N_HISTORY_PASSES          # 3 passes -> 48 traversal events


def run_growing(history_kind, seed, checkpoints, n_steps):
    """Growing model. Returns (snapshots, per_event_activation_counts)."""
    world = World()
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    events = []                             # activations per event

    for u, v in history_edges(history_kind):        # traverse->reinforce->activate
        before = world.n_activations
        world.reinforce(u, v)
        world.grow_from_edge(u, v)
        events.append(world.n_activations - before)

    out = {}
    if 0 in checkpoints:
        out[0] = world.snapshot()
    v = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, v, walk_rng)
        before = world.n_activations
        world.reinforce(v, nxt)
        world.grow_from_edge(v, nxt)
        events.append(world.n_activations - before)
        v = nxt
        if step in checkpoints:
            out[step] = world.snapshot()
    return out, events


def run_control(history_kind, seed, events, checkpoints, n_steps):
    """Activation-time-and-count matched control: replay `events` exactly."""
    world = World()
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    place_rng = np.random.default_rng(BASE_SEED + seed + CONTROL_PLACEMENT_OFFSET)
    ei, cum = 0, 0

    for u, v in history_edges(history_kind):        # traverse->reinforce->activate
        world.reinforce(u, v)
        k = events[ei]; ei += 1
        world.activate_random(k, place_rng)
        cum += k
        assert world.n_activations == cum, "history activation-count mismatch"

    out = {}
    if 0 in checkpoints:
        out[0] = world.snapshot()
    v = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, v, walk_rng)
        world.reinforce(v, nxt)
        k = events[ei]; ei += 1
        world.activate_random(k, place_rng)
        cum += k
        v = nxt
        assert world.n_activations == cum, f"step {step} activation-count mismatch"
        if step in checkpoints:
            out[step] = world.snapshot()
    return out


def run_simple(model, history_kind, seed, checkpoints, n_steps):
    """Fixed or Reinforced. Fixed never changes the graph -> filled analytically."""
    if model == "Fixed":
        snap = World().snapshot()
        return {cp: dict(snap) for cp in checkpoints}
    world = World()                                  # Reinforced
    walk_rng = np.random.default_rng(BASE_SEED + seed)
    for u, v in history_edges(history_kind):
        world.reinforce(u, v)
    out = {}
    if 0 in checkpoints:
        out[0] = world.snapshot()
    v = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, v, walk_rng)
        world.reinforce(v, nxt)
        v = nxt
        if step in checkpoints:
            out[step] = world.snapshot()
    return out


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def paired_stats(mA, mB):
    mA, mB = np.asarray(mA, float), np.asarray(mB, float)
    d = mA - mB
    frac = float(np.mean((d > 0) * 1.0 + (d == 0) * 0.5))
    ties = float(np.mean(d == 0))
    sd = d.std(ddof=1)
    if sd > 1e-12:
        dz = float(d.mean() / sd)
    else:
        dz = float("inf") if abs(d.mean()) > 1e-12 else 0.0
    allv = np.concatenate([mA, mB])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv), float)
    ranks[order] = np.arange(1, len(allv) + 1)
    _, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts)); np.add.at(sums, inv, ranks)
    ranks = (sums / counts)[inv]
    nA = len(mA)
    auc = (ranks[:nA].sum() - nA * (nA + 1) / 2.0) / (nA * len(mB))
    return {"frac": frac, "dz": dz, "auc": float(auc), "ties": ties}


def auc_from(mA, mB):
    return paired_stats(mA, mB)["auc"]


def bootstrap_seed_pairs(raw, model, metric, cp, agg, n_boot=2000, seed=12345):
    """Bootstrap a per-model statistic by resampling whole A/B seed pairs.

    agg('A_vals','B_vals') -> scalar.  Returns (point, lo, hi).
    """
    A = np.array([s[metric] for s in raw[model]["A"][cp]], float)
    B = np.array([s[metric] for s in raw[model]["B"][cp]], float)
    n = len(A)
    rng = np.random.default_rng(seed)
    point = agg(A, B)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[b] = agg(A[idx], B[idx])
    return point, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def bootstrap_paired_diff(raw, mdl1, mdl2, metric, cp, n_boot=2000, seed=999):
    """Paired between-model difference (mdl1 - mdl2), pooled over A,B per seed.

    Resamples whole seed pairs. Returns (mean_diff, lo, hi).
    """
    def pooled(model):
        A = np.array([s[metric] for s in raw[model]["A"][cp]], float)
        B = np.array([s[metric] for s in raw[model]["B"][cp]], float)
        return (A + B) / 2.0
    d = pooled(mdl1) - pooled(mdl2)
    n = len(d)
    rng = np.random.default_rng(seed)
    boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(d.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def bootstrap_auc_diff(raw, mdl1, mdl2, cp, n_boot=2000, seed=888):
    """Difference in memory AUC between two models, resampling seed pairs."""
    def cols(model):
        return (np.array([s["M"] for s in raw[model]["A"][cp]], float),
                np.array([s["M"] for s in raw[model]["B"][cp]], float))
    a1, b1 = cols(mdl1); a2, b2 = cols(mdl2)
    point = auc_from(a1, b1) - auc_from(a2, b2)
    n = len(a1)
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[k] = auc_from(a1[idx], b1[idx]) - auc_from(a2[idx], b2[idx])
    return point, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


# ---------------------------------------------------------------------------
# Fixture: checkpoints must not change the trajectory
# ---------------------------------------------------------------------------
def fixture_checkpoint_invariance():
    """Two checkpoint lists must give identical final state (Growing + control)."""
    n = 300
    cps_a = (0, n)
    cps_b = (0, 50, 123, 200, n)
    ok = True
    for hk in ("upper", "lower"):
        gA, evA = run_growing(hk, 7, cps_a, n)
        gB, evB = run_growing(hk, 7, cps_b, n)
        ok &= (evA == evB)
        for key in ("M", "total_weight", "n_active", "eff_alt", "struct_access",
                    "frac_inactive", "headroom"):
            ok &= abs(gA[n][key] - gB[n][key]) < 1e-9
        cA = run_control(hk, 7, evA, cps_a, n)
        cB = run_control(hk, 7, evB, cps_b, n)
        for key in ("M", "total_weight", "n_active", "eff_alt", "struct_access"):
            ok &= abs(cA[n][key] - cB[n][key]) < 1e-9
    return ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--steps", type=int, default=T_SUB)
    ap.add_argument("--quick", action="store_true",
                    help="fast smoke run: 20 seeds, 1000 steps")
    ap.add_argument("--outdir", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    n_seeds = 20 if args.quick else args.seeds
    n_steps = 1000 if args.quick else args.steps
    checkpoints = tuple(cp for cp in CHECKPOINTS if cp <= n_steps)

    results_dir = os.path.join(args.outdir, "results")
    figures_dir = os.path.join(args.outdir, "figures")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    print("Fixture (checkpoints do not change trajectory):",
          "PASS" if fixture_checkpoint_invariance() else "FAIL")

    raw = {m: {"A": defaultdict(list), "B": defaultdict(list)} for m in MODELS}
    hist_map = {"A": "upper", "B": "lower"}

    for seed in range(n_seeds):
        for hlabel in ("A", "B"):
            hk = hist_map[hlabel]
            # Growing first, to capture the per-event activation schedule.
            g_out, events = run_growing(hk, seed, checkpoints, n_steps)
            for cp, snap in g_out.items():
                raw["Growing"][hlabel][cp].append(snap)
            c_out = run_control(hk, seed, events, checkpoints, n_steps)
            for cp, snap in c_out.items():
                raw["Growing-MatchedControl"][hlabel][cp].append(snap)
            for model in ("Fixed", "Reinforced"):
                s_out = run_simple(model, hk, seed, checkpoints, n_steps)
                for cp, snap in s_out.items():
                    raw[model][hlabel][cp].append(snap)
        if (seed + 1) % 25 == 0:
            print(f"  ... {seed + 1}/{n_seeds} seeds")

    ref = World().snapshot()
    write_tables(results_dir, raw, ref, checkpoints, n_seeds, n_steps)
    validate_against_v1(results_dir, raw, checkpoints)
    make_figure(figures_dir, raw, ref, checkpoints)
    console_summary(raw, ref, checkpoints)
    print(f"\nWrote results/ and figures/ under {args.outdir}")


def write_tables(results_dir, raw, ref, checkpoints, n_seeds, n_steps):
    # raw metrics
    cols = ["M", "M_norm", "struct_access", "eff_alt", "edge_count",
            "total_weight", "n_active", "frac_inactive", "headroom",
            "frac_saturated"]
    rows = ["model,seed,history,checkpoint," + ",".join(cols)]
    for model in MODELS:
        for hlabel in ("A", "B"):
            for cp in checkpoints:
                for k, s in enumerate(raw[model][hlabel][cp]):
                    vals = ",".join(f"{s[c]:.6f}" if isinstance(s[c], float)
                                    else str(s[c]) for c in cols)
                    rows.append(f"{model},{k},{hlabel},{cp},{vals}")
    with open(os.path.join(results_dir, "raw_metrics.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")

    # memory summary
    mem = ["model,checkpoint,mean_M_A,mean_M_B,mean_absM_norm,frac_A_gt_B,d_z,auc,tie_frac"]
    for model in MODELS:
        for cp in checkpoints:
            mA = [s["M"] for s in raw[model]["A"][cp]]
            mB = [s["M"] for s in raw[model]["B"][cp]]
            mn = [abs(s["M_norm"]) for s in raw[model]["A"][cp]] + \
                 [abs(s["M_norm"]) for s in raw[model]["B"][cp]]
            st = paired_stats(mA, mB)
            mem.append(f"{model},{cp},{np.mean(mA):.4f},{np.mean(mB):.4f},"
                       f"{np.mean(mn):.6f},{st['frac']:.4f},{st['dz']:.4f},"
                       f"{st['auc']:.4f},{st['ties']:.4f}")
    with open(os.path.join(results_dir, "summary_memory.csv"), "w") as f:
        f.write("\n".join(mem) + "\n")

    # opportunity + capacity summary (pooled over A,B)
    opp = ["model,checkpoint,struct_access_mean,struct_access_sd,eff_alt_mean,"
           "eff_alt_sd,edge_count_mean,total_weight_mean,n_active_mean,"
           "frac_inactive_mean,headroom_mean,d_struct_access,d_eff_alt"]
    for model in MODELS:
        for cp in checkpoints:
            pool = raw[model]["A"][cp] + raw[model]["B"][cp]
            sa = np.array([s["struct_access"] for s in pool], float)
            ea = np.array([s["eff_alt"] for s in pool], float)
            ec = np.array([s["edge_count"] for s in pool], float)
            tw = np.array([s["total_weight"] for s in pool], float)
            na = np.array([s["n_active"] for s in pool], float)
            fi = np.array([s["frac_inactive"] for s in pool], float)
            hr = np.array([s["headroom"] for s in pool], float)
            opp.append(f"{model},{cp},{sa.mean():.4f},{sa.std(ddof=1):.4f},"
                       f"{ea.mean():.4f},{ea.std(ddof=1):.4f},{ec.mean():.4f},"
                       f"{tw.mean():.4f},{na.mean():.4f},{fi.mean():.6f},"
                       f"{hr.mean():.6f},{sa.mean()-ref['struct_access']:.4f},"
                       f"{ea.mean()-ref['eff_alt']:.4f}")
    with open(os.path.join(results_dir, "summary_opportunity_capacity.csv"), "w") as f:
        f.write("\n".join(opp) + "\n")

    # bootstrap paired between-model differences
    bl = ["comparison,metric,checkpoint,point_estimate,ci_lo,ci_hi"]
    pairs = [("Growing", "Growing-MatchedControl"), ("Growing", "Reinforced")]
    for m1, m2 in pairs:
        for cp in [c for c in BOOTSTRAP_CPS if c in checkpoints]:
            p, lo, hi = bootstrap_auc_diff(raw, m1, m2, cp)
            bl.append(f"{m1}_vs_{m2},memory_AUC_diff,{cp},{p:.4f},{lo:.4f},{hi:.4f}")
            for metric, name in [("eff_alt", "eff_alt_diff"),
                                 ("struct_access", "struct_access_diff"),
                                 ("M_norm", "absM_norm_diff")]:
                if metric == "M_norm":
                    # compare |M_norm| pooled
                    def agg_abs(model):
                        A = np.abs([s["M_norm"] for s in raw[model]["A"][cp]])
                        B = np.abs([s["M_norm"] for s in raw[model]["B"][cp]])
                        return (A + B) / 2.0
                    d = agg_abs(m1) - agg_abs(m2)
                    rng = np.random.default_rng(555)
                    boots = np.array([d[rng.integers(0, len(d), len(d))].mean()
                                      for _ in range(2000)])
                    bl.append(f"{m1}_vs_{m2},{name},{cp},{d.mean():.6f},"
                              f"{np.percentile(boots,2.5):.6f},"
                              f"{np.percentile(boots,97.5):.6f}")
                else:
                    p, lo, hi = bootstrap_paired_diff(raw, m1, m2, metric, cp)
                    bl.append(f"{m1}_vs_{m2},{name},{cp},{p:.4f},{lo:.4f},{hi:.4f}")
    with open(os.path.join(results_dir, "bootstrap_paired_differences.csv"), "w") as f:
        f.write("\n".join(bl) + "\n")

    # config / environment
    cfg = {
        "grid_n": GRID_N, "alpha": ALPHA, "w_max": W_MAX, "theta_grow": THETA_GROW,
        "w_init": W_INIT, "n_history_passes": N_HISTORY_PASSES, "probe": PROBE,
        "hop_budget": HOP_BUDGET, "path_len": PATH_LEN, "t_sub": n_steps,
        "checkpoints": list(checkpoints), "base_seed": BASE_SEED,
        "n_seeds": n_seeds, "models": list(MODELS),
        "control": "activation-time-and-count matched (event-by-event incl. history)",
        "pairing": "common random numbers; bootstrap resamples whole A/B seed pairs",
        "reference_initial": ref,
        "env": {"python": platform.python_version(), "numpy": np.__version__},
    }
    with open(os.path.join(results_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)


def validate_against_v1(results_dir, raw, checkpoints):
    """Reproduce v1 per-seed exactly for Fixed/Reinforced/Growing.

    v1 ran 400 subsequent steps with checkpoints {0,100,200,400}. Because the
    walk sampler and RNG seeding are unchanged, v2 must match v1 seed-by-seed at
    every shared checkpoint (to float tolerance) for these three models. The
    revised control is expected to differ (timing fix) and is not checked here.
    """
    v1_path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results", "raw_metrics.csv")
    lines = ["# Per-seed exact reproduction of v1 (Fixed/Reinforced/Growing)"]
    all_ok = True
    if not os.path.exists(v1_path):
        lines.append(f"# v1 raw_metrics.csv not found; skipped ({v1_path})")
        all_ok = False
    else:
        # v1[(model,seed,history,cp)] = {col: value}
        v1 = {}
        with open(v1_path) as f:
            hdr = f.readline().strip().split(",")
            for ln in f:
                p = ln.strip().split(",")
                key = (p[0], int(p[1]), p[2], int(p[3]))
                v1[key] = dict(zip(hdr[4:], map(float, p[4:])))
        shared_cps = [c for c in checkpoints if c in (0, 100, 200, 400)]
        checkcols = ["M", "struct_access", "eff_alt", "edge_count",
                     "total_weight", "n_active"]
        max_diff = 0.0
        n_cmp = 0
        for model in ("Fixed", "Reinforced", "Growing"):
            for hlabel in ("A", "B"):
                for cp in shared_cps:
                    seeds_here = raw[model][hlabel][cp]
                    for k, s in enumerate(seeds_here):
                        key = (model, k, hlabel, cp)
                        if key not in v1:
                            continue
                        for col in checkcols:
                            d = abs(float(s[col]) - v1[key][col])
                            max_diff = max(max_diff, d)
                            n_cmp += 1
        ok = max_diff < 1e-6
        all_ok = ok
        lines.append(f"# compared {n_cmp} per-seed values across shared checkpoints "
                     f"{shared_cps}")
        lines.append(f"# max_abs_diff = {max_diff:.3e}   tolerance = 1e-6   "
                     f"status = {'PASS' if ok else 'FAIL'}")
        lines.append(f"# NOTE: Growing-MatchedControl intentionally differs from v1 "
                     f"(timing fix); v1 control retained in ../results/.")
    lines.append(f"# overall_reproduction: {'PASS' if all_ok else 'CHECK'}")
    with open(os.path.join(results_dir, "validation_vs_v1.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("v1 per-seed reproduction (Fixed/Reinforced/Growing):",
          "PASS" if all_ok else "CHECK validation_vs_v1.txt")


def make_figure(figures_dir, raw, ref, checkpoints):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"Fixed": "#888888", "Reinforced": "#1f77b4",
              "Growing": "#d62728", "Growing-MatchedControl": "#2ca02c"}
    cps = list(checkpoints)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    def series(model, metric, absval=False):
        ys = []
        for cp in cps:
            pool = raw[model]["A"][cp] + raw[model]["B"][cp]
            v = np.array([abs(s[metric]) if absval else s[metric] for s in pool])
            ys.append(v)
        return ys

    # (0,0) memory magnitude: mean |M_norm|
    ax = axes[0, 0]
    for model in MODELS:
        ys = series(model, "M_norm", absval=True)
        m = [y.mean() for y in ys]; sd = [y.std(ddof=1) for y in ys]
        ax.plot(cps, m, "-o", color=colors[model], label=model)
        ax.fill_between(cps, np.array(m)-sd, np.array(m)+sd, color=colors[model], alpha=0.12)
    ax.set_xscale("symlog"); ax.set_title("Memory magnitude: mean |M / total_weight|")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("|M_norm|"); ax.legend(fontsize=8)

    # (0,1) memory discriminability: frac and AUC
    ax = axes[0, 1]
    for model in MODELS:
        frac = [paired_stats([s["M"] for s in raw[model]["A"][cp]],
                             [s["M"] for s in raw[model]["B"][cp]])["frac"] for cp in cps]
        ax.plot(cps, frac, "-o", color=colors[model], label=model)
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.4, 1.03)
    ax.set_title("Memory discriminability: frac(M_A > M_B)\n(paired A-vs-B, not "
                 "single-world accuracy)")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("frac(M_A > M_B)")
    ax.legend(fontsize=8)

    # (0,2) numerical saturation: fraction of edges exactly at W_MAX (float64)
    ax = axes[0, 2]
    for model in ("Reinforced", "Growing", "Growing-MatchedControl"):
        fs = [np.mean([s["frac_saturated"] for s in raw[model]["A"][cp]] +
                      [s["frac_saturated"] for s in raw[model]["B"][cp]]) for cp in cps]
        ax.plot(cps, fs, "-o", color=colors[model], label=model)
    ax.set_xscale("symlog"); ax.set_ylim(-0.03, 1.03)
    ax.set_title("Numerical saturation: frac of present edges == 6.0\n"
                 "(float64 rounding; note aggregate M_A==M_B ties stay ~0)")
    ax.set_xlabel("subsequent step (symlog)")
    ax.set_ylabel("fraction of edges at W_MAX")
    ax.legend(fontsize=8)

    # (1,0) opportunity: effective alternatives
    ax = axes[1, 0]
    for model in MODELS:
        ys = series(model, "eff_alt")
        m = [y.mean() for y in ys]; sd = [y.std(ddof=1) for y in ys]
        ax.plot(cps, m, "-o", color=colors[model], label=model)
        ax.fill_between(cps, np.array(m)-sd, np.array(m)+sd, color=colors[model], alpha=0.12)
    ax.axhline(ref["eff_alt"], ls="--", color="k", lw=0.8, label="initial")
    ax.set_xscale("symlog")
    ax.set_title("Opportunity: effective alternatives exp(H)\n(walk diversity incl. "
                 "backtracking; not destinations)")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("effective # 4-step routes")
    ax.legend(fontsize=8)

    # (1,1) opportunity: structural access
    ax = axes[1, 1]
    for model in MODELS:
        ys = series(model, "struct_access")
        m = [y.mean() for y in ys]; sd = [y.std(ddof=1) for y in ys]
        ax.plot(cps, m, "-o", color=colors[model], label=model)
        ax.fill_between(cps, np.array(m)-sd, np.array(m)+sd, color=colors[model], alpha=0.12)
    ax.axhline(ref["struct_access"], ls="--", color="k", lw=0.8, label="initial")
    ax.set_xscale("symlog")
    ax.set_title("Opportunity: structural access\nvertices within 4 hops of probe")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("reachable vertices")
    ax.legend(fontsize=8)

    # (1,2) remaining capacity: frac inactive + headroom
    ax = axes[1, 2]
    for model in ("Reinforced", "Growing", "Growing-MatchedControl"):
        fi = [np.mean([s["frac_inactive"] for s in raw[model]["A"][cp]] +
                      [s["frac_inactive"] for s in raw[model]["B"][cp]]) for cp in cps]
        ax.plot(cps, fi, "-o", color=colors[model], label=f"{model} (frac inactive)")
    ax2 = ax.twinx()
    for model in ("Reinforced", "Growing", "Growing-MatchedControl"):
        hr = [np.mean([s["headroom"] for s in raw[model]["A"][cp]] +
                      [s["headroom"] for s in raw[model]["B"][cp]]) for cp in cps]
        ax2.plot(cps, hr, "--", color=colors[model], alpha=0.6)
    ax.set_xscale("symlog")
    ax.set_title("Remaining capacity\nsolid: frac candidates inactive; dashed: mean "
                 "weight headroom (6-w)")
    ax.set_xlabel("subsequent step (symlog)")
    ax.set_ylabel("fraction of candidates inactive")
    ax2.set_ylabel("mean headroom (6 - w)")
    ax.legend(fontsize=7, loc="center left")

    fig.suptitle("Accretion pilot v2: memory, opportunity and remaining capacity "
                 f"toward saturation (timing-matched control; "
                 f"{len(raw['Growing']['A'][checkpoints[0]])} seed pairs)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(figures_dir, "memory_opportunity_capacity_v2.png"), dpi=140)
    plt.close(fig)


def console_summary(raw, ref, checkpoints):
    print("=" * 74)
    print("v2 summary (timing-matched control) -- key checkpoints")
    def line(label, fn):
        print(f"  {label:24s} " + "  ".join(
            f"t={cp}:{fn(cp)}" for cp in checkpoints))
    print("- Memory frac(M_A>M_B):")
    for model in MODELS:
        line(model, lambda cp, m=model: f"{paired_stats([s['M'] for s in raw[m]['A'][cp]],[s['M'] for s in raw[m]['B'][cp]])['frac']:.3f}")
    print("- Memory tie fraction (M_A==M_B exactly):")
    for model in ("Reinforced", "Growing", "Growing-MatchedControl"):
        line(model, lambda cp, m=model: f"{paired_stats([s['M'] for s in raw[m]['A'][cp]],[s['M'] for s in raw[m]['B'][cp]])['ties']:.3f}")
    print("- Effective alternatives exp(H) mean (initial %.1f):" % ref["eff_alt"])
    for model in MODELS:
        line(model, lambda cp, m=model: f"{np.mean([s['eff_alt'] for s in raw[m]['A'][cp]]+[s['eff_alt'] for s in raw[m]['B'][cp]]):.0f}")
    print("- Frac candidates inactive:")
    for model in ("Growing", "Growing-MatchedControl"):
        line(model, lambda cp, m=model: f"{np.mean([s['frac_inactive'] for s in raw[m]['A'][cp]]+[s['frac_inactive'] for s in raw[m]['B'][cp]]):.3f}")
    print("=" * 74)


if __name__ == "__main__":
    main()
