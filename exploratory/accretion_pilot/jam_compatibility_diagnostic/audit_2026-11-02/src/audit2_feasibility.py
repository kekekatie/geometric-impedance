#!/usr/bin/env python3
"""
audit2_feasibility.py -- Part 2 of the audit: scope and soundness of feas.py.

The engine's compatibility region is  F = { t : n_i . t >= c_i }  with n_i the
frozen window-facet normals (slack.WIN) and c_i = max_v (n_i . perp(k_v) - h)
(slack.constraints). feas.py certifies F via a Chebyshev-centre LP inside a fixed
[-50,50]^2 box. This script checks the pieces the brief asks about:

  (1) BOX INDEPENDENCE. The reported infeasibility must not be an artefact of the
      [-50,50] box. We re-test each case three ways, all box-free or large-box:
        - a box-free Phase-I LP feasibility test (scipy, no box);
        - the Chebyshev radius with the box widened to 1e6;
        - a DIRECT contradiction certificate on the inclusion-minimal infeasible
          subset (IIS) alone, which uses only the IIS half-planes (no box).
  (2) ANTI-PARALLEL check of the 2-constraint witnesses (closed-form 2-half-plane
      contradiction), and the box-free sub-LP for the 3-constraint one.
  (3) COORDINATE FIELD. The scaffolded exact check feas.Q5 assumes Q(sqrt5). We
      read the actual WIN normals and show the binding facet normals carry
      sin(36 deg)/sin(72 deg), whose minimal polynomial over Q has degree 4
      (16 x^4 - 20 x^2 + 5, irreducible), so they are NOT in Q(sqrt5): Q5 is the
      wrong field for an exact certificate.
  (4) SOLVER-FAILURE / BOX caveats. We confirm feas returns 'unresolved' (never
      feasible) when the LP fails, and we demonstrate the fixed box's blind spot
      (a feasible region centred outside [-50,50] would be misread) and show the
      real cases' deep points sit well inside the box.

Writes results/audit2_feasibility.json.
"""
from __future__ import annotations
import json
import numpy as np
from scipy.optimize import linprog
import audit_common as A
from audit_common import Sl, WIN
import feas
import part4_iis as P4


# ---------- box-free feasibility (Phase I), independent of feas.py ----------
def box_free_feasible(rows):
    """rows: [((nx,ny), c)] half-planes n.t >= c (normals as given). Returns a
    dict with a box-free verdict using TWO independent scipy calls:
      - pure feasibility LP (zero objective), bounds free;
      - a deepest-margin LP: max m s.t. n_i.t - m*||n_i|| >= c_i, t free, m<=big.
    No artificial position box is imposed (m is bounded only to keep the LP
    bounded). m*>0 feasible(full-dim), ~0 boundary, <0 infeasible."""
    if not rows:
        return dict(phase1="feasible", margin=float("inf"))
    N = np.array([[nx, ny] for (nx, ny), c in rows], float)
    cc = np.array([c for (nx, ny), c in rows], float)
    nrm = np.linalg.norm(N, axis=1)
    # pure feasibility: n_i.t >= c_i  <=>  -N t <= -c, zero objective, free t
    r1 = linprog(c=[0.0, 0.0], A_ub=-N, b_ub=-cc, bounds=[(None, None)] * 2, method="highs")
    phase1 = "feasible" if r1.status == 0 else ("infeasible" if r1.status == 2 else f"status{r1.status}")
    # deepest margin (signed distance), box-free in position; m bounded in [-1e3,1e3]
    A_ub = np.hstack([-N, (nrm).reshape(-1, 1)])          # -n.t + m*||n|| <= -c
    r2 = linprog(c=[0, 0, -1.0], A_ub=A_ub, b_ub=-cc,
                 bounds=[(None, None), (None, None), (-1e3, 1e3)], method="highs")
    margin = float(r2.x[2]) if r2.status == 0 and r2.x is not None else None
    witness = [float(r2.x[0]), float(r2.x[1])] if r2.status == 0 and r2.x is not None else None
    return dict(phase1=phase1, margin=margin, witness=witness)


def cheby_big_box(cmax, box):
    """feas Chebyshev radius with an arbitrary box (to show the verdict is stable
    as the box grows)."""
    rows = [(r[0], r[1]) for r in feas.rows_from_cmax(cmax)]
    ur = feas._unit(rows)
    res = feas.chebyshev_rows(ur, box=box)
    return None if res["x"] is None else float(res["x"][2])


def iis_rows(cmax, iis):
    """unit-normal half-planes for just the IIS keys."""
    out = []
    for key in iis:
        rk, i = key
        n, h = WIN[rk]
        nx, ny = float(n[i][0]), float(n[i][1])
        nn = (nx * nx + ny * ny) ** 0.5
        out.append(((nx / nn, ny / nn), float(cmax[key]) / nn, key))
    return out


def analyse_case_state(tiles, label):
    rank = Sl.rank_of(tiles)
    cm = Sl.constraints(tiles, rank)
    base = feas.classify(cm)
    rows_all = [(r[0], r[1]) for r in feas.rows_from_cmax(cm)]
    bf = box_free_feasible(rows_all)
    # IIS (reuse the study's own extractor so we audit the same witnesses)
    rec, p = P4.analyse(tiles, label)
    iis = [tuple(k) for k in p["iis"]] if p else []
    iisr = iis_rows(cm, iis)
    # box-free sub-LP on the IIS half-planes alone
    sub_rows = [(u, c) for (u, c, k) in iisr]
    sub = box_free_feasible(sub_rows)
    # pairwise anti-parallel analysis among IIS unit normals
    pair = []
    for a in range(len(iisr)):
        for b in range(a + 1, len(iisr)):
            (ua, ca, ka), (ub, cb, kb) = iisr[a], iisr[b]
            dot = ua[0] * ub[0] + ua[1] * ub[1]
            antiparallel = abs(dot + 1.0) < 1e-9
            # two opposing half-planes u.t>=ca and (-u).t>=cb are jointly empty iff ca+cb>0
            gap = (ca + cb) if antiparallel else None
            pair.append(dict(keys=[list(ka), list(kb)], unit_dot=round(dot, 6),
                             antiparallel=bool(antiparallel),
                             opposing_gap=(round(gap, 6) if gap is not None else None)))
    return dict(label=label, n_tiles=len(tiles), n_constraints=len(cm),
                feas_box50=base["cls"], cheby_r_box50=base["r"], deep_point_box50=base["witness"],
                box_free_phase1=bf["phase1"], box_free_margin=bf["margin"],
                cheby_r_box_1e6=cheby_big_box(cm, 1e6),
                iis=[list(k) for k in iis], iis_size=len(iis),
                iis_box_free_phase1=sub["phase1"], iis_box_free_margin=sub["margin"],
                iis_pairs=pair)


# ---------------------------- coordinate field ----------------------------
def field_report():
    """Read the 20 frozen WIN facet normals and classify each component's field.
    cos/sin of multiples of 36 deg: cos36,cos72,... lie in Q(sqrt5); sin36,sin72
    do not (minimal polynomial 16x^4-20x^2+5 over Q, degree 4)."""
    import math
    def minpoly_quartic_val(x):
        return 16 * x ** 4 - 20 * x ** 2 + 5
    normals = []
    for rk in range(4):
        n, h = WIN[rk]
        for i, (nx, ny) in enumerate(n):
            ang = round(math.degrees(math.atan2(float(ny), float(nx))) % 360, 4)
            # is each component a root of the degree-4 sine poly (=> not in Q(sqrt5))?
            comp_deg4 = [abs(minpoly_quartic_val(abs(float(c)))) < 1e-9 and abs(float(c)) > 1e-9
                         for c in (nx, ny)]
            normals.append(dict(rank=rk, facet=i, angle_deg=ang,
                                nx=float(nx), ny=float(ny),
                                has_degree4_component=any(comp_deg4)))
    s36, s72 = math.sin(math.radians(36)), math.sin(math.radians(72))
    return dict(
        n_normals=len(normals),
        normals=normals,
        sin36=s36, sin72=s72,
        sin36_satisfies_16x4_20x2_5=abs(minpoly_quartic_val(s36)) < 1e-12,
        sin72_satisfies_16x4_20x2_5=abs(minpoly_quartic_val(s72)) < 1e-12,
        quartic_irreducible_over_Q=True,   # proved by hand in AUDIT_REPORT (no rational root / quad factor)
        conclusion=("window facet normals carry sin(36)/sin(72); their minimal polynomial over Q "
                    "has degree 4, so they are NOT in Q(sqrt5). feas.Q5 (Q(sqrt5)) is insufficient "
                    "for an exact certificate; the needed field is Q(cos36,sin36)=Q(zeta_20)^+ (degree 4)."),
        normals_with_degree4_component=sum(1 for d in normals if d["has_degree4_component"]),
    )


# --------------------- solver-failure / box blind-spot ---------------------
def solver_failure_and_box_checks():
    out = {}
    # (a) a simulated LP failure must classify as 'unresolved', never feasible.
    orig = feas.linprog
    class _Res:  # mimic a failed OptimizeResult
        status = 4; x = None; message = "simulated failure"
    try:
        feas.linprog = lambda *a, **k: _Res()
        r = feas.classify_rows([((1, 0), -1), ((-1, 0), -1), ((0, 1), -1), ((0, -1), -1)])
        out["sim_failure_class"] = r["cls"]
        out["sim_failure_not_feasible"] = r["cls"] not in ("positive_area", "lower_dimensional")
    finally:
        feas.linprog = orig
    # (b) fixed-box blind spot: a genuinely feasible region centred at (1000,1000)
    #     is reported infeasible by the BOX=50 certifier (documented limitation).
    far = [((1, 0), 999.0), ((-1, 0), -1001.0), ((0, 1), 999.0), ((0, -1), -1001.0)]  # 999<=x<=1001, 999<=y<=1001
    out["far_region_box50_class"] = feas.classify_rows(far)["cls"]
    out["far_region_box1e6_r"] = (lambda res: None if res["x"] is None else float(res["x"][2]))(
        feas.chebyshev_rows(feas._unit(far), box=1e6))
    out["note"] = ("feas uses a fixed BOX=50; a feasible region lying entirely outside it is misread as "
                   "infeasible. This does not affect the study cases (their deep points sit well inside "
                   "the box; see per-case deep_point_box50), but is a real scope limit of the certifier.")
    return out


def main():
    A.RESULTS.mkdir(parents=True, exist_ok=True)
    cases = []
    for (w, si, js, fi) in [(7, 0, 23, 9), (5, 0, 42, 17)]:
        arm, full, skin = A.jam_full_and_skin(w, si, js)
        full_fi = arm["snaps"][fi]
        cases.append(analyse_case_state(full_fi, f"w{w}-first_infeasible_full@{fi}"))
        cases.append(analyse_case_state(skin, f"w{w}-jam_trigger_skin@{js}"))
    report = dict(cases=cases, field=field_report(), solver_and_box=solver_failure_and_box_checks())
    (A.RESULTS / "audit2_feasibility.json").write_text(json.dumps(report, indent=2, default=float))

    print("=== box independence & witnesses ===")
    for c in cases:
        maxabs = max(abs(v) for v in c["deep_point_box50"]) if c["deep_point_box50"] else None
        print(f"{c['label']}: box50={c['feas_box50']} r={c['cheby_r_box50']:.4e} | "
              f"box-free phase1={c['box_free_phase1']} margin={c['box_free_margin']:.4e} | "
              f"box1e6 r={c['cheby_r_box_1e6']:.4e} | IIS{c['iis']} box-free={c['iis_box_free_phase1']} "
              f"margin={c['iis_box_free_margin']:.4e} | deep|t|<=box: {maxabs:.3f}")
        for p in c["iis_pairs"]:
            print(f"      pair {p['keys']}: unit_dot={p['unit_dot']} antiparallel={p['antiparallel']} "
                  f"opposing_gap={p['opposing_gap']}")
    f = report["field"]
    print("\n=== coordinate field ===")
    print(f"  {f['normals_with_degree4_component']}/{f['n_normals']} frozen WIN normals carry a degree-4 "
          f"(sin 36/72) component; sin36 root of 16x^4-20x^2+5: {f['sin36_satisfies_16x4_20x2_5']}; "
          f"=> not in Q(sqrt5).")
    s = report["solver_and_box"]
    print("\n=== solver failure / box blind-spot ===")
    print(f"  simulated LP failure -> class={s['sim_failure_class']} (not feasible: {s['sim_failure_not_feasible']})")
    print(f"  feasible region at (1000,1000): box50 -> {s['far_region_box50_class']}; "
          f"box1e6 r -> {s['far_region_box1e6_r']:.3f}")
    print("\nwrote results/audit2_feasibility.json")


if __name__ == "__main__":
    main()
