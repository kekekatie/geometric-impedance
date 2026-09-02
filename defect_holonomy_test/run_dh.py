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
from defect_v2 import TerminatingLineDefect

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


def e0b_v2(patch):
    """Gate E0b (protocol §4-v2): terminating grid-line construction. For >=2
    families, check topological closure defect, clean unit edges, tight-loop
    holonomy at 3 radii for w=+-1, and diagnose the healing mechanism."""
    lm = LiftMetric(patch.par_star, patch.perp_star)
    r_patch = float(np.linalg.norm(patch.par, axis=1).max())
    out = []
    for j_star in [0, 1]:
        d = TerminatingLineDefect(patch, j_star=j_star)
        # tight-loop holonomy at three radii
        holos = []
        for radius in [4, 6, 8]:
            loop = ring_loop(d, radius)
            if loop is None:
                continue
            P = positions_of_path(d, loop)
            h, _, res, nover = lm.holonomy(P)
            w = d.winding_number(P)
            holos.append((radius, float(w), h, res, nover))
        # healing mechanism: is the shift field single-valued and boundary-reaching?
        sc = d.shift_count
        rr = np.linalg.norm(d.par0, axis=1)
        shifted = sc > 0
        reaches_boundary = bool(shifted.any() and rr[shifted].max() > 0.9 * r_patch)
        max_holo = max((h for _, _, h, _, _ in holos), default=float("nan"))
        clean_edges = all(nover == 0 for *_, nover in holos) if holos else False
        out.append(dict(
            j_star=j_star, b_perp=np.round(d.b_perp, 4).tolist(),
            b_perp_norm=round(float(np.linalg.norm(d.b_perp)), 4),
            worm_size=d.worm_size, removed=d.removed_size, merged=d.merged,
            core_size=d.core_size, closure_defect_is_burgers=bool(d.closure_ok),
            shift_field_single_valued=bool(set(sc.tolist()) <= {0, 1}),
            shift_region_reaches_boundary=reaches_boundary,
            clean_unit_edges=clean_edges,
            max_tight_loop_holonomy=float(max_holo),
            tight_loops=[dict(r=r, w=w, holo=h, maxres=res, nover=n)
                         for (r, w, h, res, n) in holos]))
    # verdict (consider only instances where tight loops could be formed)
    with_loops = [o for o in out if o["tight_loops"]]
    heals = bool(with_loops) and all(
        o["max_tight_loop_holonomy"] < 1e-9 for o in with_loops)
    topo_ok = all(o["closure_defect_is_burgers"] for o in out)
    clean = bool(with_loops) and all(o["clean_unit_edges"] for o in with_loops)
    if topo_ok and clean and heals:
        verdict = ("TOPOLOGY CORRECT, UNIT-EDGE CLEAN, but PHYSICAL HOLONOMY "
                   "HEALS: on a finite simply-connected patch the single-valued "
                   "shift field carries the obstruction to the free boundary. "
                   "Genuine bulk holonomy needs a non-simply-connected domain "
                   "(toroidal patch / periodic approximant).")
    elif topo_ok and not clean:
        verdict = "topology ok but re-glue not unit-clean -- investigate"
    else:
        verdict = "construction did not realise the topological monodromy"
    return out, verdict, dict(heals_via_boundary_escape=bool(heals and topo_ok))


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
        print(f"[{sub}] v1 defect construction verdict: {verdict}", flush=True)
        v2_rows, v2_verdict, v2_flags = e0b_v2(patch)
        print(f"[{sub}] v2 (terminating grid-line) E0b: {v2_verdict}", flush=True)
        for r in v2_rows:
            print(f"    j*={r['j_star']} b_perp={r['b_perp']} "
                  f"closure=Burgers:{r['closure_defect_is_burgers']} "
                  f"unit_clean:{r['clean_unit_edges']} "
                  f"boundary_escape:{r['shift_region_reaches_boundary']} "
                  f"max_holonomy={r['max_tight_loop_holonomy']:.2e}", flush=True)
        summary["substrates"][sub] = {"E0": e0,
                                      "v1_defect_verdict": verdict,
                                      "v1_defect_flags": flags,
                                      "v1_defect_instances": diag_rows,
                                      "v2_e0b_verdict": v2_verdict,
                                      "v2_e0b_flags": v2_flags,
                                      "v2_e0b_instances": v2_rows}
    summary["runtime_s"] = round(time.time() - t0, 1)
    with open(HERE / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nDONE in {summary['runtime_s']}s -> summary.json", flush=True)


if __name__ == "__main__":
    main()
