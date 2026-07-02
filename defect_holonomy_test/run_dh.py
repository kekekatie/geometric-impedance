#!/usr/bin/env python3
"""
Defect-Holonomy Test -- runner (E0 validation + defect-construction diagnostic).

This runs the mandatory E0 metric validation and an honest diagnostic of the
tile-surgery defect constructions. It does NOT run E1-E4, because those tests are
only meaningful once a construction is shown to carry a verified Burgers vector
while keeping unit-edge classification -- which the constructions implemented
here do not (see FINDINGS.md). Reporting E1-E4 numbers from a construction that
heals or produces classification artifacts would be misleading.
"""

import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "reverse_loop_test"))

import numpy as np
from geometry import Patch
import walker as W
from lift_metric import LiftMetric, positions_of_path
from defect import WoundedPatch, ring_loop

HERE = Path(__file__).parent
(HERE / "results").mkdir(exist_ok=True)
SUBS = ["ammann_beenker", "penrose"]
SEED = 20260702


def e0_validation(patch, n=400):
    """Lift-by-integration must reproduce stored-perp machinery to FP floor."""
    lm = LiftMetric(patch.par_star, patch.perp_star)
    comp = patch.largest_component()
    rng = np.random.default_rng(SEED)
    open_err = []
    loop_holo = []
    for _ in range(n):
        s = W.sample_direct(patch, rng, 16, comp)
        if s is None:
            continue
        S, T, path, _, _ = s
        addr, res, _ = lm.integrate(positions_of_path(patch, path))
        open_err.append(float(np.linalg.norm(addr - (patch.perp[T] - patch.perp[S]))))
    cset = set(comp.tolist())
    for _ in range(n):
        s = W.sample_direct(patch, rng, 14, comp)
        if s is None:
            continue
        S, base, pre, _, _ = s
        loop, _ = W.make_cycle(patch, base, 16, rng, "crossing", cset)
        if loop is None:
            continue
        h, _, _, _ = lm.holonomy(positions_of_path(patch, loop))
        loop_holo.append(h)
    return dict(n_open=len(open_err), max_open_err=max(open_err),
                n_loops=len(loop_holo), max_loop_holonomy=max(loop_holo),
                passed=bool(max(open_err) < 1e-9 and max(loop_holo) < 1e-9))


def defect_diagnostic(patch):
    """Construct dislocations by ray-slit offset re-glue at several cores; measure
    winding-1 holonomy. Report whether the construction (a) heals, (b) quantises
    to b_perp, or (c) yields non-quantised artefact holonomy."""
    lm = LiftMetric(patch.par_star, patch.perp_star)
    cores = [((1.3, 0.7), (1.0, 0.0)), ((-2.1, 3.4), (0.3, 0.95)),
             ((4.0, -1.5), (-0.7, 0.7)), ((-3.5, -2.0), (0.9, -0.2))]
    rows = []
    for (cxy, uxy) in cores:
        wp = WoundedPatch(patch, np.array(cxy), np.array(uxy), offset=1)
        b_perp_norm = float(np.linalg.norm(wp.b_perp))
        holos = []
        for radius in [4, 6, 8, 10]:
            loop = ring_loop(wp, radius)
            if loop is None:
                continue
            P = positions_of_path(wp, loop)
            h, _, _, _ = lm.holonomy(P)
            w = wp.winding_number(P)
            if abs(w - 1) < 0.2:
                holos.append(h)
        holos = np.array(holos) if holos else np.array([np.nan])
        rows.append(dict(core=cxy, cut=uxy, seam_edges=len(wp.seam_edges),
                         core_size=wp.core_size, b_lift=wp.b_lift.tolist(),
                         b_perp_norm=round(b_perp_norm, 4),
                         w1_holonomy_median=float(np.nanmedian(holos)),
                         w1_holonomy_spread=float(np.nanmax(holos) - np.nanmin(holos))))
    # classify construction outcome
    med = np.array([r["w1_holonomy_median"] for r in rows])
    healed = np.all(med < 1e-9)
    # quantised iff holonomy ~ b_perp_norm consistently AND stable across radius
    bpn = np.array([r["b_perp_norm"] for r in rows])
    quantised = bool(np.all(np.abs(med - bpn) < 0.1 * np.maximum(bpn, 1e-9))
                     and np.all([r["w1_holonomy_spread"] < 0.1 for r in rows]))
    if healed:
        verdict = "HEALS (holonomy at FP floor for all instances)"
    elif quantised:
        verdict = "QUANTISED to b_perp (candidate Outcome A -- verify with full E1-E4)"
    else:
        verdict = ("NON-QUANTISED / construction-dependent (holonomy present but "
                   "not equal to b_perp and/or unstable) -- construction artefact, "
                   "not a fair test of H1")
    return rows, verdict, dict(healed=bool(healed), quantised=quantised)


def main():
    t0 = time.time()
    summary = {"config": {"seed": SEED, "radius": 26.0}, "substrates": {}}
    for sub in SUBS:
        patch = Patch(sub, radius=26.0)
        e0 = e0_validation(patch)
        print(f"[{sub}] E0: max_open_err={e0['max_open_err']:.2e} "
              f"max_loop_holonomy={e0['max_loop_holonomy']:.2e} "
              f"passed={e0['passed']}", flush=True)
        if not e0["passed"]:
            print(f"[{sub}] E0 FAILED -- stopping per protocol §5.", flush=True)
            summary["substrates"][sub] = {"E0": e0, "aborted": True}
            continue
        diag_rows, verdict, flags = defect_diagnostic(patch)
        print(f"[{sub}] defect construction verdict: {verdict}", flush=True)
        for r in diag_rows:
            print(f"    core={r['core']} b_lift={r['b_lift']} "
                  f"|b_perp|={r['b_perp_norm']} "
                  f"w1_holonomy={r['w1_holonomy_median']:.3e} "
                  f"(spread {r['w1_holonomy_spread']:.2e})", flush=True)
        summary["substrates"][sub] = {"E0": e0, "defect_verdict": verdict,
                                      "defect_flags": flags,
                                      "defect_instances": diag_rows}
    summary["runtime_s"] = round(time.time() - t0, 1)
    with open(HERE / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nDONE in {summary['runtime_s']}s -> summary.json", flush=True)


if __name__ == "__main__":
    main()
