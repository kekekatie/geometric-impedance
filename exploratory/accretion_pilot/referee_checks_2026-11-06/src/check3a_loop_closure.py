#!/usr/bin/env python3
"""
check3a_loop_closure.py -- Check 3a: loop closure on the 11 jammed bands.

For each band, chain the boundary legs into closed vertex loops and sum the RAW
lifted edge increments (+/- e_j from perp_map.edge_dir) around each loop to get the
holonomy H in Z^5. Report b_par = sum H_j PHYS[j] (the physical closure, ~0 for a
closed loop), b_perp = sum H_j PERP[j] (the internal-space holonomy), and the index
component sum(H). Prediction P3a: |b_perp| = 0 (<= 1e-6) on every legal-rhombus loop.

Writes results/check3a_loop_closure.json. Pre-registered.
"""
from __future__ import annotations
import json, math
import rc_common as RC

TOL = 1e-6


def loop_holonomy(loop, pos):
    """Sum raw lifted edge increments around a cyclic vertex-key loop."""
    H = [0, 0, 0, 0, 0]
    n = len(loop); legs = 0; nonleg = 0
    for i in range(n):
        a = loop[i]; b = loop[(i + 1) % n]
        p = pos[a]; q = pos[b]
        if abs(abs(q - p) - RC.S) < 1e-4 * RC.S:
            j, sg = RC.M.edge_dir(p, q)
            H[j] += sg; legs += 1
        else:
            nonleg += 1
    return H, legs, nonleg


def main():
    RC.RESULTS.mkdir(parents=True, exist_ok=True)
    bands = RC.load_jammed_bands()
    out = []
    worst = 0.0; all_zero = True; total_loops = 0
    for b in bands:
        tiles = b["jam_band"]
        _, _, conf = RC.lift_tiles(tiles)
        loops = RC.boundary_loops(tiles)
        loop_recs = []
        for (loop, pos) in loops:
            H, legs, nonleg = loop_holonomy(loop, pos)
            bpar = RC.phys_of(H); bperp = RC.perp_of(H); idx = int(sum(H))
            abperp = abs(bperp)
            worst = max(worst, abperp)
            if abperp > TOL:
                all_zero = False
            loop_recs.append(dict(n_vertices=len(loop), legs=legs, nonleg_steps=nonleg,
                                  H=[int(x) for x in H],
                                  b_par_abs=round(abs(bpar), 9), b_perp_abs=round(abperp, 9),
                                  index_component=idx))
        total_loops += len(loops)
        nz = [r for r in loop_recs if r["b_perp_abs"] > TOL]
        out.append(dict(case=b["case"], world=b["world"], n_tiles=len(tiles),
                        global_lift_conflicts=len(conf), n_boundary_loops=len(loops),
                        max_b_perp_abs=round(max((r["b_perp_abs"] for r in loop_recs), default=0.0), 9),
                        max_b_par_abs=round(max((r["b_par_abs"] for r in loop_recs), default=0.0), 9),
                        n_loops_b_perp_nonzero=len(nz), loops=loop_recs))
        print(f"[3a] {b['case']:>9}: loops={len(loops):>2} conflicts={len(conf)} "
              f"max|b_perp|={out[-1]['max_b_perp_abs']:.2e} max|b_par|={out[-1]['max_b_par_abs']:.2e} "
              f"nonzero_perp_loops={len(nz)}", flush=True)

    summary = dict(n_bands=len(bands), total_loops=total_loops,
                   max_b_perp_abs_all=round(worst, 9), tolerance=TOL,
                   P3a_held=bool(all_zero))
    (RC.RESULTS / "check3a_loop_closure.json").write_text(
        json.dumps(dict(summary=summary, bands=out), indent=2, default=float))
    print(f"\nP3a: max |b_perp| over all {total_loops} loops = {worst:.2e} (tol {TOL}) -> "
          f"{'HELD (b_perp=0 everywhere)' if all_zero else 'FAILED (defect or bug)'}")
    print("wrote results/check3a_loop_closure.json")


if __name__ == "__main__":
    main()
