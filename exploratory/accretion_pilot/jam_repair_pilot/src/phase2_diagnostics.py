#!/usr/bin/env python3
"""
phase2_diagnostics.py -- Phase 2: small, descriptive geometry diagnostic.

Pre-committed in protocol/PHASE2_DIAGNOSTICS.md. Three diagnostics on the paired
A/B fork states, kept distinct from the true windows and the finite hulls:

  D1  retained compatibility area  (birth F0; after_first FA, FB; ratios pA,pB)
  D2  F-centroid displacement birth->after_first  (dA, dB)   [offset-space length]
  D3  F-centroid eccentricity from the offset origin (eA, eB) [offset-space length]

plus descriptive labels: committed-tile shape (0/1) and mean hull depth of the
committed tile's vertices (depth "stands in for local pattern").

DEVIATION FROM PRE-COMMITMENT (dated 2026-11-01, recorded, not hidden): D3's
"window-stack centre" is realised as the offset-space origin (0,0) -- the centre
of the Penrose acceptance windows in the zeta^{2j} perp map -- rather than an
averaged pentagon centroid; the depth proxy is reported as a descriptive label
rather than a third diagnostic, keeping the diagnostic count at three.

Descriptive only: no model, no causal claim, streams not independent. The +0.749
inward-alignment statistic (different population) is not used.

Outputs under ../results/phase2/: diagnostics.json, phase2_report.txt.
"""
from __future__ import annotations
import json, pickle, math
from pathlib import Path
import numpy as np
import pilot_common as PC
from pilot_common import Sl, CD, M, L

OUT = Path(__file__).resolve().parent.parent / "results" / "phase2"
FORKS = Path(__file__).resolve().parent.parent / "results" / "baseline" / "forks.pkl"

# worlds where B jammed in >=1 stream (from Phase 1 / saved records)
B_JAM_WORLDS = {5, 7, 15, 19, 21, 28, 29}


def load_forks():
    data = pickle.loads(FORKS.read_bytes())
    out = {}
    for w, d in data.items():
        out[w] = dict(
            Sstar=[(int(t[0]),) + tuple(t[1:]) for t in d["Sstar"]],
            cs=[(int(c[0]),) + tuple(c[1:]) for c in d["cs"]],
        )
    return out


def poly_centroid(poly):
    """Area-weighted centroid of a 2D polygon (list of (x,y)). None if degenerate."""
    if len(poly) < 3:
        return None
    A = 0.0; cx = 0.0; cy = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        A += cross; cx += (x0 + x1) * cross; cy += (y0 + y1) * cross
    if abs(A) < 1e-18:
        return None
    A *= 0.5
    return (cx / (6 * A), cy / (6 * A))


def region_of(cm):
    return Sl.region(cm)


def diagnostics_for_fork(world, Sstar, cs):
    rank = Sl.rank_of(Sstar)
    A, B = cs[0], cs[1]
    cm0 = Sl.constraints(Sstar, rank)
    reg0 = region_of(cm0)
    F0 = float(Sl.area(reg0))
    cen0 = poly_centroid(reg0)

    res = dict(world=world, F0=F0, cen0=cen0, shapeA=int(A[0]), shapeB=int(B[0]))
    for tag, c in (("A", A), ("B", B)):
        cm = CD.after_first(Sstar, c, rank)
        reg = region_of(cm)
        area = float(Sl.area(reg))
        cen = poly_centroid(reg)
        p = (area / F0) if F0 > 1e-12 else None
        # D2 displacement from birth centroid
        d = None
        if cen is not None and cen0 is not None:
            d = math.hypot(cen[0] - cen0[0], cen[1] - cen0[1])
        # D3 eccentricity from offset origin
        e = math.hypot(cen[0], cen[1]) if cen is not None else None
        # depth label: mean hull depth of the committed tile's vertices on the
        # after_first patch (depth 1=deep/central, 0=hull boundary; <10 pts -> none)
        depth = _tile_depth(Sstar, c)
        res[tag] = dict(F=area, p=p, disp=d, ecc=e, depth=depth, empty=(area <= 1e-12))
    # paired differences
    res["dF"] = res["A"]["F"] - res["B"]["F"]
    res["dp"] = (None if (res["A"]["p"] is None or res["B"]["p"] is None)
                 else res["A"]["p"] - res["B"]["p"])
    res["ddisp"] = (None if (res["A"]["disp"] is None or res["B"]["disp"] is None)
                    else res["A"]["disp"] - res["B"]["disp"])
    res["decc"] = (None if (res["A"]["ecc"] is None or res["B"]["ecc"] is None)
                   else res["A"]["ecc"] - res["B"]["ecc"])
    return res


def _tile_depth(Sstar, c):
    """after_first patch is base + c + one patient step; approximate the committed
    tile's depth using the base+c lift's per-layer hull (descriptive label)."""
    try:
        patch = list(Sstar) + [c]
        K, pos, conf = M.lift(patch)
        dep, areas, layers = M.depths(K)
        vals = [dep[L.key(z)] for z in c[1:] if L.key(z) in dep]
        return float(np.mean(vals)) if vals else None
    except Exception:
        return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    forks = load_forks()
    rows = []
    for w in sorted(forks):
        r = diagnostics_for_fork(w, forks[w]["Sstar"], forks[w]["cs"])
        r["B_jammed"] = (w in B_JAM_WORLDS)
        rows.append(r)
    (OUT / "diagnostics.json").write_text(json.dumps(rows, indent=2, default=float))

    # grouped descriptive summary
    def group(pred):
        return [r for r in rows if pred(r)]
    jam = group(lambda r: r["B_jammed"])
    surv = group(lambda r: not r["B_jammed"])

    def med(xs):
        xs = [x for x in xs if x is not None]
        return float(np.median(xs)) if xs else None

    lines = []
    lines.append("Phase 2 -- descriptive geometry diagnostic on paired A/B fork states")
    lines.append(f"forks: {len(rows)}   B-jammed forks: {sorted(B_JAM_WORLDS)} (n={len(jam)}); "
                 f"B-survived (n={len(surv)})")
    lines.append("Units: offset/perp-space (dimensionless areas, offset-space lengths). Descriptive only.")
    lines.append("")
    lines.append(f"{'world':>5} {'Bjam':>4} {'F0':>8} {'pA':>6} {'pB':>6} {'dp(A-B)':>8} "
                 f"{'eccA':>7} {'eccB':>7} {'shA':>3} {'shB':>3}")
    for r in rows:
        lines.append(f"{r['world']:>5} {str(r['B_jammed']):>4} {r['F0']:>8.4f} "
                     f"{_f(r['A']['p']):>6} {_f(r['B']['p']):>6} {_f(r['dp']):>8} "
                     f"{_f(r['A']['ecc']):>7} {_f(r['B']['ecc']):>7} "
                     f"{r['shapeA']:>3} {r['shapeB']:>3}")
    lines.append("")
    lines.append("Group medians (B-jammed vs B-survived); paired A-B within fork:")
    for name, g in (("B-jammed", jam), ("B-survived", surv)):
        lines.append(f"  [{name}] median pA={med([r['A']['p'] for r in g])}, "
                     f"pB={med([r['B']['p'] for r in g])}, "
                     f"median (pA-pB)={med([r['dp'] for r in g])}, "
                     f"median (eccA-eccB)={med([r['decc'] for r in g])}, "
                     f"median (dispA-dispB)={med([r['ddisp'] for r in g])}")
    lines.append("")
    # shape contingency
    from collections import Counter
    shapes = Counter((r['shapeA'], r['shapeB'], r['B_jammed']) for r in rows)
    lines.append("committed-tile shape (A,B) x B_jammed contingency:")
    for k, v in sorted(shapes.items()):
        lines.append(f"  shapeA={k[0]} shapeB={k[1]} B_jammed={k[2]}: {v}")
    lines.append("")
    lines.append("Caveats: 22 forks, streams not independent; these are paired descriptive")
    lines.append("differences, not a predictive model. No causal arrow from any diagnostic to jamming.")

    txt = "\n".join(lines)
    (OUT / "phase2_report.txt").write_text(txt + "\n")
    print(txt)
    print(f"\nwrote {OUT}/diagnostics.json and phase2_report.txt")


def _f(x):
    return "   .  " if x is None else f"{x:.3f}"


if __name__ == "__main__":
    main()
