#!/usr/bin/env python3
"""
Stage A (winding staircase) — the instrument's first honest run.

N1 (phason-sweep null, theorem-grade): sweep the cut offset gamma; on every
resulting IDEAL tiling, the perp-holonomy of every closed loop must sit at the
floating-point floor (Theorem 1: perfection carries no wake). Value is not the
result (theorems don't have off-days) but the proof that the pipeline does not
hallucinate a nonzero winding before anything expensive is built.

Canary F: repeat at >= 3 patch sizes N. A hallucinated plateau would scale with N;
a true null stays at the FP floor independent of N.

KILL: any gamma at any N producing holonomy above ~1e-10 -> STOP. Either the code
is wrong (likely) or Theorem 1 is wrong (the story, if it survives scrutiny).

N2 (slope linearity) is analytic (linear projection -> winding = slope, no
plateaus) and its empirical form travels with the approximant construction (the
next block); noted, not run here.
"""
import sys, json
sys.path.insert(0, "../reverse_loop_test")
sys.path.insert(0, "../defect_holonomy_test")
import numpy as np
from geometry import Patch, SUBSTRATES
import walker as W
from lift_metric import LiftMetric, positions_of_path

SEED = 20260709
N_GAMMA = 40          # phason sweep resolution
N_LOOPS = 60          # closed loops sampled per gamma
RADII = [16.0, 22.0, 28.0]   # >= 3 patch sizes for canary F

def sweep_gamma(substrate, radius, rng):
    cfg = SUBSTRATES[substrate]
    N = cfg["N"]
    base = np.array([0.2, 0.13, 0.37, 0.06, 0.29])[:N]
    base = base - base.sum() / N + 0.5 / N
    direction = np.array([1.0, -1.0, 0.5, -0.5, 0.25])[:N]
    direction = direction - direction.mean()      # keep sum-shift generic
    worst = 0.0
    per_gamma = []
    for t in np.linspace(0.0, 1.0, N_GAMMA):
        gammas = base + t * 0.15 * direction
        p = Patch(substrate, radius=radius, gammas=gammas)
        lm = LiftMetric(p.par_star, p.perp_star)
        comp = p.largest_component()
        cset = set(comp.tolist())
        gmax = 0.0
        made = 0
        for _ in range(N_LOOPS * 4):
            if made >= N_LOOPS:
                break
            s = W.sample_direct(p, rng, 12, comp)
            if s is None:
                continue
            S, base_v, pre, _, _ = s
            loop, _ = W.make_cycle(p, base_v, 14, rng, "crossing", cset)
            if loop is None:
                continue
            h, _, _, _ = lm.holonomy(positions_of_path(p, loop))
            gmax = max(gmax, h)
            made += 1
        per_gamma.append(float(gmax))
        worst = max(worst, gmax)
    return worst, per_gamma

def main():
    rng = np.random.default_rng(SEED)
    report = {"stage": "A", "test": "N1 phason-sweep null + canary F",
              "n_gamma": N_GAMMA, "n_loops": N_LOOPS, "radii": RADII,
              "kill_threshold": 1e-10, "substrates": {}}
    overall_ok = True
    for sub in ["ammann_beenker", "penrose"]:
        report["substrates"][sub] = {"by_radius": {}}
        print(f"=== {sub} : N1 phason sweep ===")
        for r in RADII:
            worst, per = sweep_gamma(sub, r, rng)
            report["substrates"][sub]["by_radius"][str(r)] = dict(
                worst_holonomy=worst, mean_holonomy=float(np.mean(per)))
            ok = worst < 1e-10
            overall_ok &= ok
            print(f"  radius {r:5.1f}: worst closed-loop holonomy over "
                  f"{N_GAMMA} gammas = {worst:.2e}  ({'OK null' if ok else 'KILL!'})")
        # canary F: is the (null) level independent of N?
        worsts = [report["substrates"][sub]["by_radius"][str(r)]["worst_holonomy"]
                  for r in RADII]
        n_indep = max(worsts) < 1e-10
        report["substrates"][sub]["canaryF_N_independent_at_floor"] = bool(n_indep)
        print(f"  canary F: worst across all N = {max(worsts):.2e} -> "
              f"{'FP floor, N-independent (no hallucinated plateau)' if n_indep else 'N-DEPENDENT — investigate'}")
    report["N1_passed"] = bool(overall_ok)
    report["N2_note"] = ("analytic (linear projection -> winding=slope, no "
                         "plateaus); empirical form travels with the approximant "
                         "construction (next block).")
    json.dump(report, open("stage_a_results.json", "w"), indent=2)
    print(f"\nN1 PASSED (instrument does not hallucinate winding): {overall_ok}")
    print("-> stage_a_results.json")

if __name__ == "__main__":
    main()
