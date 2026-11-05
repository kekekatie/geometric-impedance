#!/usr/bin/env python3
"""
check3b_offset_profile.py -- Check 3b: local offset profile on the 11 jammed bands.

Slide an arc of K=32 tiles (angular order, step 1, cyclic) around each band. At each
position compute the reader F-region's Chebyshev centre (best-fit local offset) and
radius. Classify the centre-vs-angle profile as step / ramp / mixed by the fixed
criterion (window k=3; step if >=0.50 of total variation concentrated, ramp if <=0.25).
Report step locations relative to dead sites and scars, and step directions relative to
the 5 worm directions. Writes results/check3b_offset_profile.json. Pre-registered.
"""
from __future__ import annotations
import json, math, cmath
import rc_common as RC

K = 32
STEP = 1
KWIN = 3
STEP_FRAC = 0.50
RAMP_FRAC = 0.25
STEP_LOC_FRAC = 0.25        # a "step" position carries >= this fraction of TV


def angular_order(tiles):
    c = RC.centroid(tiles)
    return sorted(tiles, key=lambda t: math.atan2((RC.tile_centroid(t) - c).imag,
                                                   (RC.tile_centroid(t) - c).real)), c


def arc_mean_angle(arc, c):
    v = sum((RC.tile_centroid(t) - c) for t in arc) / len(arc)
    return math.degrees(math.atan2(v.imag, v.real)) % 360.0


def main():
    RC.RESULTS.mkdir(parents=True, exist_ok=True)
    bands = RC.load_jammed_bands()
    out = []
    for b in bands:
        tiles = b["jam_band"]
        order, c = angular_order(tiles)
        n = len(order)
        positions = []
        for i in range(0, n, STEP):
            arc = [order[(i + j) % n] for j in range(K)]
            raw, payload = RC.read_tiles(b["Sstar"], b["cs"], arc)
            rec = dict(index=i, angle=round(arc_mean_angle(arc, c), 2),
                       reconstructed=(raw.get("status") == "reconstructed"))
            if raw.get("status") == "reconstructed":
                centre, radius, st = RC.chebyshev_centre(raw["constraints"], payload["windows"])
                rec.update(F_area=raw.get("area"), cheb_status=st,
                           centre=centre, radius=radius)
            positions.append(rec)

        # sequence of defined centres (F reconstructed, chebyshev ok, radius>0)
        defined = [(p["index"], p["angle"], complex(*p["centre"]))
                   for p in positions
                   if p.get("centre") and p.get("cheb_status") == "ok" and (p.get("radius") or 0) > 1e-9]
        jumps = []
        for k in range(len(defined)):
            i0, a0, z0 = defined[k]
            i1, a1, z1 = defined[(k + 1) % len(defined)]
            jumps.append(abs(z1 - z0))
        TV = sum(jumps)
        # largest KWIN-window sum of consecutive jumps (cyclic)
        Wk = 0.0
        m = len(jumps)
        if m:
            Wk = max(sum(jumps[(s + d) % m] for d in range(min(KWIN, m))) for s in range(m))
        frac = (Wk / TV) if TV > 1e-12 else 0.0
        if TV <= 1e-12:
            cls = "flat"
        elif frac >= STEP_FRAC:
            cls = "step"
        elif frac <= RAMP_FRAC:
            cls = "ramp"
        else:
            cls = "mixed"

        # step positions: jump >= STEP_LOC_FRAC * TV
        step_positions = []
        for k in range(len(defined)):
            if TV > 1e-12 and jumps[k] >= STEP_LOC_FRAC * TV:
                i0, a0, z0 = defined[k]; i1, a1, z1 = defined[(k + 1) % len(defined)]
                disp = z1 - z0
                widx, resid = RC.nearest_worm(disp) if abs(disp) > 1e-12 else (None, None)
                step_positions.append(dict(at_angle=a0, to_angle=a1, jump=round(jumps[k], 4),
                                           jump_frac_of_TV=round(jumps[k] / TV, 3),
                                           disp=[disp.real, disp.imag],
                                           disp_worm_index=(int(widx) if widx is not None else None),
                                           disp_worm_residual_deg=(round(float(resid), 2) if resid is not None else None)))
        # dead-site + scar angular locations for context
        bc = c
        dead_angles = sorted({round(math.degrees(math.atan2(((e[0] + e[1]) / 2 - bc).imag,
                                                            ((e[0] + e[1]) / 2 - bc).real)) % 360, 1)
                              for e in b["dead"]})
        out.append(dict(case=b["case"], world=b["world"], n_tiles=n, K=K,
                        n_positions=len(positions), n_defined=len(defined),
                        total_variation=round(TV, 4), Wk=round(Wk, 4),
                        concentration_frac=round(frac, 3), classification=cls,
                        n_steps=len(step_positions), steps=step_positions,
                        dead_site_angles=dead_angles,
                        profile=[dict(angle=p["angle"], centre=p.get("centre"),
                                      radius=p.get("radius"), defined=(p.get("cheb_status") == "ok"))
                                 for p in positions]))
        print(f"[3b] {b['case']:>9}: pos={len(positions)} defined={len(defined)} "
              f"TV={TV:.3f} frac={frac:.2f} -> {cls}  steps={len(step_positions)}", flush=True)

    tally = {}
    for r in out:
        tally[r["classification"]] = tally.get(r["classification"], 0) + 1
    summary = dict(n_bands=len(bands), K=K, kwin=KWIN,
                   step_frac=STEP_FRAC, ramp_frac=RAMP_FRAC, classification_tally=tally)
    (RC.RESULTS / "check3b_offset_profile.json").write_text(
        json.dumps(dict(summary=summary, bands=out), indent=2, default=float))
    print(f"\n[3b] classification tally: {tally}")
    print("wrote results/check3b_offset_profile.json")


if __name__ == "__main__":
    main()
