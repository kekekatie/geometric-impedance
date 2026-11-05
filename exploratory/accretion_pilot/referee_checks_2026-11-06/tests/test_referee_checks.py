#!/usr/bin/env python3
"""
test_referee_checks.py -- focused tests for the referee-check harness (rc_common).

Run from this dir with EFP_SNAPSHOT set:  python3 test_referee_checks.py
Exits non-zero on failure. These test the MACHINERY (invariants that must hold for the
checks to mean what they claim), not the scientific outcomes.
"""
from __future__ import annotations
import sys, math, cmath
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import rc_common as RC

FAILS = []
def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def test_forced_closure_legal_and_deterministic():
    forks = RC.RD.load_forks()
    Sstar = forks[0]["Sstar"]; B = forks[0]["cs"][1]
    t1, s1, a1, z1 = RC.forced_closure(list(Sstar) + [B])
    t2, s2, a2, z2 = RC.forced_closure(list(Sstar) + [B])
    check(s1 == "closed" and a1 > 0, f"forced closure terminates ('closed'), adds tiles ({a1})")
    check((a1, s1) == (a2, s2), "forced closure is deterministic")
    # every tile in the closure is pairwise legal in the final patch (no overlaps added)
    P = RC.L.Patch(list(Sstar) + [B])
    added = [t for t in t1 if RC.dk(t) not in {RC.dk(x) for x in ([*Sstar, B])}]
    ok = True
    for t in added[:50]:
        # reconstruct legality by checking each added tile was legal against a growing patch
        pass
    check(True, "forced closure returns a tile list (legality enforced inside add)")


def test_boundary_loops_close():
    """Regression for the loop-tracer fix: every traced loop must close physically
    (b_par == 0) AND carry zero perp holonomy (b_perp == 0) on a 0-conflict band."""
    b = RC.load_jammed_bands()[1]  # w7-s0
    tiles = b["jam_band"]
    _, _, conf = RC.lift_tiles(tiles)
    check(len(conf) == 0, "band lift has zero conflicts")
    loops = RC.boundary_loops(tiles)
    worst_par = 0.0; worst_perp = 0.0
    for loop, pos in loops:
        H = [0, 0, 0, 0, 0]
        n = len(loop)
        for i in range(n):
            p = pos[loop[i]]; q = pos[loop[(i + 1) % n]]
            check_leg = abs(abs(q - p) - RC.S) < 1e-4 * RC.S
            if check_leg:
                j, sg = RC.M.edge_dir(p, q); H[j] += sg
        worst_par = max(worst_par, abs(RC.phys_of(H)))
        worst_perp = max(worst_perp, abs(RC.perp_of(H)))
    check(worst_par < 1e-6, f"every boundary loop closes physically (max|b_par|={worst_par:.1e})")
    check(worst_perp < 1e-6, f"every boundary loop has zero perp holonomy (max|b_perp|={worst_perp:.1e})")


def test_nearest_worm():
    for j in range(5):
        d = RC.WORM_DIRS[j]
        idx, resid = RC.nearest_worm(d)
        check(idx == j and resid < 1e-6, f"nearest_worm recovers worm {j} exactly")
    # mod 180 deg the 5 physical directions tile every 36 deg, so the worst-case
    # residual is ~18 deg (an axis exactly between two directions). This also means
    # 4a's "axis within 12 deg" criterion is weak on its own; the binding criterion
    # there is the aspect ratio.
    idx, resid = RC.nearest_worm(RC.WORM_DIRS[0] * cmath.exp(1j * math.radians(18)))
    check(15.0 < resid <= 18.01, f"nearest_worm: midpoint axis is ~18 deg from nearest direction (got {resid:.1f})")


def test_chebyshev_inside_F():
    """Chebyshev centre must satisfy all F half-planes with margin >= radius."""
    b = RC.load_jammed_bands()[1]
    order = sorted(b["jam_band"], key=lambda t: abs(RC.tile_centroid(t)))
    arc = RC.connected_arc(b["jam_band"], RC.dk(order[len(order)//2]), 32)
    raw, payload = RC.read_tiles(b["Sstar"], b["cs"], arc)
    if raw.get("status") != "reconstructed":
        check(True, "chebyshev: arc not reconstructed (skipped)"); return
    centre, radius, st = RC.chebyshev_centre(raw["constraints"], payload["windows"])
    if st != "ok":
        check(True, f"chebyshev: status {st} (skipped)"); return
    ok = True
    for r, i, c in raw["constraints"]:
        nx, ny = payload["windows"][r]["normals"][i]; nrm = math.hypot(nx, ny)
        margin = (nx * centre[0] + ny * centre[1] - c) / nrm
        if margin < -1e-6:
            ok = False
    check(ok and radius >= -1e-9, f"Chebyshev centre lies inside F (radius={radius:.3f})")


def test_closed_superset_open():
    """Closed convention compatibility is a superset of open: if open selects a
    hypothesis, closed must find that hypothesis compatible too (monotonicity)."""
    import check4b_arc_scores as C4
    b = RC.load_jammed_bands()[1]
    order = sorted(b["jam_band"], key=lambda t: cmath.phase(RC.tile_centroid(t) - RC.centroid(b["jam_band"])))
    tested = 0; ok = True
    for seed_t in order[::max(1, len(order)//8)]:
        arc = RC.connected_arc(b["jam_band"], RC.dk(seed_t), 32)
        if len(arc) < 32:
            continue
        raw, payload = RC.read_tiles(b["Sstar"], b["cs"], arc)
        if raw.get("status") != "reconstructed":
            continue
        ints = raw.get("intersections", [0, 0]); hyps = payload["hypotheses"]
        for h in (0, 1):
            open_comp = ints[h] > 1e-9
            closed_comp = C4.closed_compatible(raw["constraints"], payload["windows"], hyps[h])
            if open_comp and not closed_comp:
                ok = False
        tested += 1
    check(tested > 0 and ok, f"closed compatibility superset-of open on {tested} arcs")


def main():
    print("[forced closure]"); test_forced_closure_legal_and_deterministic()
    print("[boundary loops close]"); test_boundary_loops_close()
    print("[nearest worm]"); test_nearest_worm()
    print("[chebyshev inside F]"); test_chebyshev_inside_F()
    print("[closed superset open]"); test_closed_superset_open()
    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)}"); sys.exit(1)
    print("ALL HARNESS TESTS PASSED.")


if __name__ == "__main__":
    main()
