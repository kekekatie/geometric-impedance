#!/usr/bin/env python3
"""
phase1_arc_readout.py -- Phase 1: contiguous-arc / sub-band readout at the recorded
jams (NO growth mutation).

Although F(whole retained band) is empty at the jam, does historical A/B
information survive in a CONTIGUOUS COMPATIBLE sub-arc? We decompose the jammed
active ring deterministically by perimeter angle (anchored at the dead notch),
score connected sub-arcs with the FROZEN reader under the fork gauge + A/B birth
hypotheses, and report the largest connected compatible fraction and its verdict.

Interpretive caution (stated up front): a SMALLER arc has fewer constraints -> a
larger F -> more likely to overlap BOTH A and B -> 'ambiguous'. A compatible arc
that reads 'B' is only informative if it is large enough to discriminate; small-arc
compatibility is expected and weak. We therefore report, for each arc, F-area and
both intersections, not just the verdict.

Writes results/phase1_arc_readout.json and .csv.
"""
from __future__ import annotations
import json, math, csv
import scar_common as SC
import arc_tools as AT

COMPAT_TOL = 1e-9
SCAN_STEPS = 48
CASES_CORE = [(7, 0), (5, 0)]


def maximal_compatible_scan(state, c, theta0):
    """Grow a connected sub-arc from the side opposite the notch (theta0+pi) and
    find the largest connected compatible one. Returns the scan curve and the max
    compatible (by band-tile fraction)."""
    band = state["band"]; nband = len(band)
    center = theta0 + math.pi
    curve = []
    best = None
    for i in range(1, SCAN_STEPS + 1):
        hw = math.pi * i / SCAN_STEPS
        win = AT.angular_window(band, c, center, hw)
        sc = AT.score_arc(state, win)
        frac = sc["n_tiles"] / nband
        compat = (sc["F_area"] or 0.0) > COMPAT_TOL
        curve.append(dict(half_width=round(hw, 4), n_tiles=sc["n_tiles"],
                          band_fraction=round(frac, 4), F_area=sc["F_area"],
                          outcome=sc["outcome"]))
        if compat and (best is None or sc["n_tiles"] > best["n_tiles"]):
            best = dict(half_width=round(hw, 4), **sc, band_fraction=round(frac, 4))
    return dict(curve=curve, max_compatible=best)


def sectors(state, c, theta0):
    out = []
    center = theta0 + math.pi
    for dtheta, name in [(math.pi / 2, "pi/2"), (math.pi, "pi"), (3 * math.pi / 2, "3pi/2")]:
        win = AT.angular_window(state["band"], c, center, dtheta / 2)
        sc = AT.score_arc(state, win)
        sc["delta_theta"] = name
        sc["band_fraction"] = round(sc["n_tiles"] / len(state["band"]), 4)
        out.append(sc)
    return out


def notch_halves(state, c, theta0):
    out = []
    for name, center in [("cw_from_notch", theta0 + math.pi / 2),
                         ("ccw_from_notch", theta0 - math.pi / 2)]:
        win = AT.angular_window(state["band"], c, center, math.pi / 2)
        sc = AT.score_arc(state, win)
        sc["half"] = name
        sc["band_fraction"] = round(sc["n_tiles"] / len(state["band"]), 4)
        out.append(sc)
    return out


def witness_complement(state):
    """Secondary descriptive check (w7/w5): the connected components remaining when
    the heuristic compatibility-witness deletion footprint (greedy engulfment, from
    the cooperative-rearrangement pilot) is excluded. Reused read-only; skipped if
    unavailable."""
    try:
        import sys
        coop_src = str(SC.HERE.parents[0] / "cooperative_rearrangement_pilot" / "src")
        if coop_src not in sys.path:
            sys.path.insert(0, coop_src)
        import coop_common as CC
        import part3_necessary as P3
        rank = CC.Sl.rank_of(state["band"])
        BC = CC.BandConstraints(state["band"], rank=rank)

        def exterior_cmax_from_vertices(E):
            cmax = {}
            for key, lst in BC.by_key.items():
                for cc, v in lst:
                    if v not in E:
                        cmax[key] = cc; break
            return cmax, E
        BC.exterior_cmax_from_vertices = exterior_cmax_from_vertices
        greedy = P3.greedy_engulfment(BC, state=None)
        vkeys = {tuple(v) for v in greedy.get("selected_vertices", [])}
        foot = {CC.dk(t) for t in state["band"] if any(CC.L.key(z) in vkeys for z in t[1:])}
    except Exception as e:
        return dict(available=False, reason=str(e)[:200])
    remaining = [t for t in state["band"] if SC.dk(t) not in foot]
    comps = AT.connected_components(remaining)
    scored = []
    for comp in sorted(comps, key=len, reverse=True)[:6]:
        sc = AT.score_arc(state, comp)
        scored.append(sc)
    return dict(available=True, n_footprint_tiles=len(foot),
                n_selected_witness_vertices=len(vkeys),
                n_components=len(comps), components=scored)


def analyse(world, si, with_witness):
    state = SC.jam_state(world, si)
    c = AT.centroid(state["band"])
    theta0, _ = AT.notch_theta0(state)
    full = AT.score_arc(state, state["band"])      # whole band (baseline)
    scan = maximal_compatible_scan(state, c, theta0)
    rec = dict(case=f"w{world}-B-s{si}", world=world, si=si, jam_step=state["jam_step"],
               n_band_tiles=len(state["band"]), n_dead_sites=len(state["dead"]),
               n_growable_true_frontier=state["n_growable"],
               theta0=round(theta0, 4),
               whole_band=dict(outcome=full["outcome"], F_area=full["F_area"],
                               intersections=full["intersections"]),
               maximal_compatible_connected_arc=scan["max_compatible"],
               maximal_compatible_scan=scan["curve"],
               sectors=sectors(state, c, theta0),
               notch_halves=notch_halves(state, c, theta0))
    if with_witness:
        rec["witness_complement"] = witness_complement(state)
    return rec


def main(cases=None, with_witness=True):
    SC.RESULTS.mkdir(parents=True, exist_ok=True)
    cases = cases or CASES_CORE
    out = []
    for (w, si) in cases:
        print(f"[phase1] w{w}-B-s{si} ...", flush=True)
        rec = analyse(w, si, with_witness=(with_witness and (w, si) in [(7, 0), (5, 0)]))
        out.append(rec)
        mc = rec["maximal_compatible_connected_arc"]
        print(f"   whole band: {rec['whole_band']['outcome']}; "
              f"max compatible connected arc: "
              f"{'none' if not mc else f'{mc['band_fraction']*100:.0f}% of band, {mc['n_tiles']} tiles, {mc['outcome']}'}",
              flush=True)
    (SC.RESULTS / "phase1_arc_readout.json").write_text(json.dumps(out, indent=2, default=float))
    # flat CSV of the headline per-arc verdicts
    with open(SC.RESULTS / "phase1_arc_readout.csv", "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(["case", "arc_kind", "band_fraction", "n_tiles", "F_area", "outcome", "choice_tile"])
        for rec in out:
            mc = rec["maximal_compatible_connected_arc"]
            if mc:
                wtr.writerow([rec["case"], "maximal_compatible", mc["band_fraction"], mc["n_tiles"],
                              mc["F_area"], mc["outcome"], mc["choice_tile_retention"]])
            for s in rec["sectors"]:
                wtr.writerow([rec["case"], f"sector_{s['delta_theta']}", s["band_fraction"], s["n_tiles"],
                              s["F_area"], s["outcome"], s["choice_tile_retention"]])
            for s in rec["notch_halves"]:
                wtr.writerow([rec["case"], s["half"], s["band_fraction"], s["n_tiles"],
                              s["F_area"], s["outcome"], s["choice_tile_retention"]])
    print("wrote results/phase1_arc_readout.json + .csv")
    return out


if __name__ == "__main__":
    import sys
    if "--all" in sys.argv:
        main(cases=SC.B_JAMS)
    else:
        main()
