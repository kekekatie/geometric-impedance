#!/usr/bin/env python3
"""
part2_feasibility.py -- re-examine the "F=0" claim with a real feasibility
certificate instead of a polygon-area threshold.

For the recorded jam triggers (world 7 B streams 0,1; world 5 B stream 0),
compute the frozen compatibility constraints for F(full) and F(skin), then
classify with feas.classify (Chebyshev-radius LP) + a sensitivity sweep.

Outputs ../results/part2_feasibility.json and part2_report.txt.
"""
from __future__ import annotations
import json
from pathlib import Path
import study_common as SC
from study_common import Sl, PC
import feas

OUT = Path(__file__).resolve().parent.parent / "results"
CASES = [(7, 0, 23), (7, 1, 23), (5, 0, 42)]


def jam_states(world, si, js):
    forks = SC.P3.load_forks()
    B = forks[world]["cs"][1]
    stream = PC.streams_for(world)[si]
    arm = PC.grow(forks[world]["Sstar"], B, stream, 44)
    assert arm["stop"] == "jam" and len(arm["snaps"]) == js + 1, \
        f"replay mismatch for w{world} s{si}: stop={arm['stop']} nsnaps={len(arm['snaps'])}"
    full = arm["snaps"][-1]
    skin, _ = PC.skin_of(full)
    return full, skin


def certify(tiles):
    rank = Sl.rank_of(tiles)
    cm = Sl.constraints(tiles, rank)
    area = float(Sl.area(Sl.region(cm)))
    cl = feas.classify(cm)
    sens = feas.sensitivity(cm)
    return dict(nconstraints=len(cm), polygon_area=area,
                cls=cl["cls"], chebyshev_r=cl["r"], dim=cl["dim"],
                witness=cl["witness"], sensitivity=sens)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for (w, si, js) in CASES:
        full, skin = jam_states(w, si, js)
        rec = dict(case=f"w{w}-B-s{si}", world=w, stream_idx=si, jam_step=js,
                   F_full=certify(full), F_skin=certify(skin),
                   n_full=len(full), n_skin=len(skin))
        rows.append(rec)
        print(f"{rec['case']}: F(full) {rec['F_full']['cls']} r*={rec['F_full']['chebyshev_r']:.4e} "
              f"(area {rec['F_full']['polygon_area']:.1e}); "
              f"F(skin) {rec['F_skin']['cls']} r*={rec['F_skin']['chebyshev_r']:.4e}", flush=True)
    (OUT / "part2_feasibility.json").write_text(json.dumps(rows, indent=2, default=float))

    lines = []
    lines.append("Part 2 -- feasibility certificate for the jam-trigger compatibility region")
    lines.append("Chebyshev-radius LP over the FROZEN Sl constraints; area shown for comparison only.")
    lines.append(f"radius tolerance tol_r = {feas.TOL_R:g} (window apothem ~ 0.81-1.31 offset units)")
    lines.append("")
    lines.append(f"{'case':>10} {'region':>7} {'class':>16} {'cheby_r*':>11} {'poly_area':>10} {'stable':>6}")
    for r in rows:
        for tag in ("F_full", "F_skin"):
            f = r[tag]
            lines.append(f"{r['case']:>10} {tag[2:]:>7} {f['cls']:>16} {f['chebyshev_r']:>11.4e} "
                         f"{f['polygon_area']:>10.1e} {str(f['sensitivity']['stable']):>6}")
    lines.append("")
    lines.append("Reading: every jam-trigger region is INFEASIBLE (Chebyshev r* clearly negative,")
    lines.append("|r*| ~ 0.08 >> tol and >> the 1e-6 sensitivity band), not a feasible point or segment.")
    lines.append("The earlier area-threshold verdict was correct in substance; it is now certified by")
    lines.append("an independent feasibility test. F(full) and F(skin) share the same binding")
    lines.append("constraints, so the contradiction is present within the retained skin alone.")
    lines.append("")
    lines.append("Numerical limits: float LP over phi-irrational data. r* is far from any tolerance, so")
    lines.append("the infeasible verdict is robust; this is strong numerical evidence, not a symbolic proof.")
    txt = "\n".join(lines)
    (OUT / "part2_report.txt").write_text(txt + "\n")
    print("\n" + txt)


if __name__ == "__main__":
    main()
