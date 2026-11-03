#!/usr/bin/env python3
"""
phase3_post_readout.py -- Phase 3: post-continuation readout (global + arc).

At the final checkpoint of the scar-tolerant continuation (step 44 or total
arrest), run the frozen GLOBAL reader on the surviving retained boundary band, and
the Phase-1 CONTIGUOUS-ARC reader on the maximal connected compatible sub-arc
(connected components only, so lifts are single-valued). Track the choice-tile (B)
fate separately. Figures for w7-B-s0 and w5-B-s0.

Writes results/phase3_post_readout.json and .csv.
"""
from __future__ import annotations
import json, csv, math
import scar_common as SC
import arc_tools as AT
import scar_continuation as SCN

SCAN_STEPS = 32
COMPAT_TOL = 1e-9


def scar_centroid_angle(res, c):
    """notch anchor theta0 for the final band = centroid angle of the scar-edge
    midpoints (the pinned defect region)."""
    pts = []
    for ek in res["scars"]:
        zs = [complex(*v) for v in ek]
        pts.append(sum(zs) / len(zs))
    if not pts:
        return 0.0
    m = sum(pts) / len(pts)
    return math.atan2((m - c).imag, (m - c).real)


def maximal_compatible(state_like, band, c, theta0):
    nband = len(band)
    center = theta0 + math.pi
    best = None
    for i in range(1, SCAN_STEPS + 1):
        hw = math.pi * i / SCAN_STEPS
        win = AT.angular_window(band, c, center, hw)
        sc = AT.score_arc(state_like, win)
        if (sc["F_area"] or 0.0) > COMPAT_TOL and (best is None or sc["n_tiles"] > best["n_tiles"]):
            best = dict(half_width=round(hw, 4), band_fraction=round(sc["n_tiles"] / nband, 4), **sc)
    return best


def analyse(world, si):
    res = SCN.scar_grow(world, si, steps=44, record_illegal=False)
    # a lightweight "state" object for the frozen reader (fork gauge + hypotheses)
    state_like = dict(Sstar=res["Sstar"], cs=res["cs"], B=res["B"], band=res["band"])
    # (1) global reader on the final retained band
    g = AT.score_arc(state_like, res["band"])
    # (2) arc reader on the maximal compatible connected sub-arc of the final band
    c = AT.centroid(res["band"]); theta0 = scar_centroid_angle(res, c)
    mc = maximal_compatible(state_like, res["band"], c, theta0)
    # (3) choice-tile fate
    bkey = SC.dk(res["B"])
    still = bkey in {SC.dk(t) for t in res["band"]}
    fate = "still_retained" if still else "departed_by_pruning"
    return dict(case=f"w{world}-B-s{si}", world=world, si=si,
                jam_step=res["jam_step"], final_step=res["final_step"],
                reached_step_44=res["reached_44"], total_arrest=res["total_arrest"],
                n_band_tiles_final=len(res["band"]), n_scar_edges=res["n_scars"],
                global_reader=dict(outcome=g["outcome"], F_area=g["F_area"],
                                   intersections=g["intersections"]),
                maximal_compatible_arc=(None if not mc else dict(
                    band_fraction=mc["band_fraction"], n_tiles=mc["n_tiles"],
                    F_area=mc["F_area"], outcome=mc["outcome"],
                    intersections=mc["intersections"],
                    choice_tile_retention=mc["choice_tile_retention"])),
                choice_tile_fate=fate, choice_departs_step=res["choice_departs_step"]), res


def main(cases=None):
    SC.RESULTS.mkdir(parents=True, exist_ok=True)
    cases = cases or SC.B_JAMS
    out = []
    for (w, si) in cases:
        print(f"[phase3] w{w}-B-s{si} ...", flush=True)
        rec, _ = analyse(w, si)
        out.append(rec)
        mc = rec["maximal_compatible_arc"]
        print(f"   final band {rec['n_band_tiles_final']} tiles; global reader {rec['global_reader']['outcome']}; "
              f"max compatible arc {'none' if not mc else f'{mc['band_fraction']*100:.0f}% {mc['outcome']}'}; "
              f"choice-tile {rec['choice_tile_fate']}", flush=True)
    (SC.RESULTS / "phase3_post_readout.json").write_text(json.dumps(out, indent=2, default=float))
    with open(SC.RESULTS / "phase3_post_readout.csv", "w", newline="") as f:
        wtr = csv.writer(f)
        cols = ["case", "jam_step", "final_step", "n_band_tiles_final", "n_scar_edges",
                "global_outcome", "max_arc_fraction", "max_arc_outcome", "choice_tile_fate"]
        wtr.writerow(cols)
        for r in out:
            mc = r["maximal_compatible_arc"]
            wtr.writerow([r["case"], r["jam_step"], r["final_step"], r["n_band_tiles_final"],
                          r["n_scar_edges"], r["global_reader"]["outcome"],
                          mc["band_fraction"] if mc else "", mc["outcome"] if mc else "",
                          r["choice_tile_fate"]])
    print("wrote results/phase3_post_readout.json + .csv")
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--core":
        main(cases=[(7, 0), (5, 0)])
    else:
        main()
