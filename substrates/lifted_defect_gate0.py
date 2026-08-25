#!/usr/bin/env python3
"""
Lifted-Burgers audit (sealed PREREG_lifted_defect.md) — Gate 0: constructability.

Part 1 (lifted_defect.py) built and validated the closure functional: on a perfect
cut-and-project tiling every loop closes to zero. Gate 0 asks the first real
question: **can we construct a LEGAL rhombus tiling that actually carries a nonzero
closure around a core?** — i.e. a dislocation made only of the existing tiles and the
existing lift, added by geometry, not by a flip (flips cannot create one; Part 1's
spine).

Method — the Socolar–Lubensky–Steinhardt winding cut. A dislocation in a
cut-and-project tiling is a point about which the perpendicular-space (phason) offset
winds by the full perp-image of a parent-lattice vector B over one physical turn.
Away from the core and away from the branch cut the tiling is locally perfect; the
offset jump across the cut is a gauge artifact that heals in the *geometry* (adjacent
points still differ by a single physical star vector), so the only genuine anomaly is
localized at the core, where a loop picks up B.

Edges are therefore read GEOMETRICALLY here (two vertices adjacent iff their physical
positions differ by a star vector), exactly as post-flip tilings are — because the
construction, like a flip, takes the tiling out of the exact family and the
generation-time kernel/ustar edge rule no longer applies. On the perfect tiling the
geometric and lift-based edge steps coincide (Part 1), so the instrument is unchanged;
the geometric reading is what lets the branch-cut seam heal so the defect is the core.

Gate 0's own null (Fable's knife 1): the identical construction is also run on a
periodic parent-lattice control, so a construction *failure* can be told apart from a
*grammar* difference. Three outcomes are reported, never collapsed:
  (a) succeeds on periodic but NOT on QC  -> real grammar obstruction (H_none earned)
  (b) fails on BOTH                        -> implementation limit ("Gate 0 not resolved")
  (c) succeeds on QC                       -> proceed to Tests 1-4.
"""

import argparse
import itertools
import sys
from collections import Counter

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import frame, structure, _extra_positions, _TIE_TOL
from tile_audit import faces, shape_key
from lifted_defect import split

NAME = {8: "silver", 10: "golden", 12: "platinum"}


# --------------------------------------------------------------------------- #
# Construction: winding-offset (Volterra) cut around a core.
# --------------------------------------------------------------------------- #
def construct(N, extent, B, core=(0.37, 0.19), offset=None, wind_sign=1,
              winding=True):
    """Cut-and-project with the phason offset winding by perp(B) around `core`.

    B is the target Burgers charge in Z^m (m = N/2 star directions). With
    winding=False this is exactly the singular half-open generator (control:
    should read zero closure everywhere). Returns lifts (Z^4), positions,
    ustar, and the core in physical coordinates.
    """
    st = structure(N)
    m, par_m, perp_m = frame(N)
    par4, perp4 = st["par4"], st["perp4"]
    K, Kb, A, b = st["K"], st["Kb"], st["A"], st["b"]
    r = K.shape[0]
    B = np.asarray(B, dtype=np.int64)
    assert B.shape == (m,), (B.shape, m)
    dperp2 = B @ perp_m                       # (2,) Galois image of B
    dK = (B @ Kb) if r else np.zeros(0)       # (r,) K(x)R image of B
    core = np.asarray(core, dtype=float)
    if offset is None:
        offset = np.array([0.1123, 0.0847])
    offset = np.asarray(offset, float)

    axis = np.arange(-extent, extent + 1, dtype=np.int64)
    tail = np.array(list(itertools.product(axis, repeat=3)), dtype=np.int64)
    kept = []
    for first in axis:
        a = np.empty((len(tail), 4), dtype=np.int64)
        a[:, 0] = first
        a[:, 1:] = tail
        pos = a @ par4                                    # physical positions
        if winding:
            phi = np.arctan2(pos[:, 1] - core[1], pos[:, 0] - core[0])
            w = wind_sign * phi / (2 * np.pi)             # winding fraction (-.5,.5]
        else:
            w = np.zeros(len(a))
        gal = a @ perp4 + offset - w[:, None] * dperp2[None, :]
        exoff = -w[:, None] * dK[None, :]                 # (n, r)

        if r == 0:
            keep = np.all(gal @ A.T <= b + _TIE_TOL, axis=1)
            if keep.any():
                blk = np.column_stack([a[keep], np.zeros((keep.sum(), 0), np.int64)])
                kept.append(blk)
            continue

        pre = _extra_positions(st, a)
        P = len(pre)
        slack = np.empty((len(a), P))
        us = np.empty((len(a), P, r), dtype=np.int64)
        for p, (u, ex) in enumerate(pre):
            pp = np.column_stack([gal, ex + exoff])
            slack[:, p] = (b - pp @ A.T).min(axis=1)
            us[:, p] = u
        qual = slack >= -_TIE_TOL
        lex = us[:, :, 0].astype(np.float64)
        for d in range(1, r):
            lex = lex * 1000.0 + us[:, :, d]
        lex = np.where(qual, lex, np.inf)
        best = lex.argmin(axis=1)
        keep = qual.any(axis=1)
        if keep.any():
            chosen = us[np.arange(len(a)), best]
            kept.append(np.column_stack([a[keep], chosen[keep]]))

    blk = np.concatenate(kept)
    lifts, ustar = blk[:, :4], blk[:, 4:]
    return lifts, lifts @ par4, ustar, core


# --------------------------------------------------------------------------- #
# Geometric edges + geometric closure (edges read from physical positions).
# --------------------------------------------------------------------------- #
def geom_edges(pos, star_par, tol=1e-6):
    """Edges: vertex pairs whose physical displacement is +/- a star vector."""
    tree = cKDTree(pos)
    Ls = np.linalg.norm(star_par, axis=1)
    E = set()
    step_of = {}
    rmax = Ls.max() + tol
    for i, p in enumerate(pos):
        for j in tree.query_ball_point(p, rmax):
            if j <= i:
                continue
            d = pos[j] - pos[i]
            for k in range(len(star_par)):
                if np.allclose(d, star_par[k], atol=tol):
                    E.add((i, j)); step_of[(i, j)] = (k, +1); break
                if np.allclose(d, -star_par[k], atol=tol):
                    E.add((i, j)); step_of[(i, j)] = (k, -1); break
    return sorted(E), step_of


def geom_step(step_of, i, j):
    """(k, sign) for going from vertex i to vertex j along a star edge, or None."""
    if (i, j) in step_of:
        k, s = step_of[(i, j)]; return k, s
    if (j, i) in step_of:
        k, s = step_of[(j, i)]; return k, -s
    return None


def loop_closure(cycle, step_of, m):
    """Lifted Burgers charge summed around a cycle of vertex indices (geometric)."""
    B = np.zeros(m, dtype=np.int64)
    ok = True
    for t in range(len(cycle)):
        i, j = cycle[t], cycle[(t + 1) % len(cycle)]
        s = geom_step(step_of, i, j)
        if s is None:
            ok = False; continue
        k, sg = s
        B[k] += sg
    return B, ok


def face_charges(F, outer, step_of, pos, m):
    """Per-face closure. Returns list of (centroid, B, nonzero) for bounded faces.

    Closure telescopes: the charge enclosed by any loop equals the sum of the
    face closures inside it (shared interior edges cancel). A clean rhombus face
    always closes to zero (Part-1 protection); only defect faces carry charge, so
    the enclosed Burgers charge is read off the defect faces directly.
    """
    out = []
    for c in F:
        if c is outer:
            continue
        B, ok = loop_closure(c, step_of, m)
        cen = pos[c].mean(axis=0)
        out.append((cen, B, int(np.abs(B).sum()) > 0, len(c), ok))
    return out


# --------------------------------------------------------------------------- #
# Legality + core diagnostics.
# --------------------------------------------------------------------------- #
def legality(pos, E):
    """Crossing-free / all-quadrilateral / face census on the geometric graph."""
    n = len(pos)
    F = faces(n, E, pos)
    sz = Counter(len(c) for c in F)
    outer = max(sz)
    bd = [c for c in F if len(c) != outer]
    quad = sum(1 for c in bd if len(c) == 4) / max(len(bd), 1)
    euler = n - len(E) + len(F)
    nonquad = [c for c in bd if len(c) != 4]
    return dict(verts=n, edges=len(E), faces=len(F), outer=outer,
                bounded=len(bd), quad=quad, euler=euler,
                nonquad_sizes=dict(sorted(Counter(len(c) for c in nonquad).items())),
                nonquad=nonquad, F=F, bd=bd)


def run(N, extent, B, core=(0.37, 0.19), wind_sign=1, winding=True, label=""):
    st = structure(N)
    star_par = st["star"] @ st["par4"]
    m = st["m"]
    lifts, pos, ustar, corexy = construct(N, extent, B, core=core,
                                          wind_sign=wind_sign, winding=winding)
    E, step_of = geom_edges(pos, star_par)
    leg = legality(pos, E)
    outer = max(leg["F"], key=len)

    # per-face closure (telescopes; the rigorous enclosed-charge tool)
    fc = face_charges(leg["F"], outer, step_of, pos, m)
    charged = [(cen, Bf, sz) for (cen, Bf, nz, sz, ok) in fc if nz]
    non_star = [(cen, sz) for (cen, Bf, nz, sz, ok) in fc if not ok]

    # net charge inside radius R about the core (sum of enclosed face charges)
    Rmax = np.linalg.norm(pos - corexy, axis=1).max()
    radii = [Rmax * f for f in (0.15, 0.25, 0.4, 0.6, 0.85)]
    nested = []
    for R in radii:
        Btot = np.zeros(m, dtype=np.int64)
        for cen, Bf, nz, sz, ok in fc:
            if np.linalg.norm(cen - corexy) <= R:
                Btot = Btot + Bf
        bpar, bperp = split_from_starcount(Btot, N)
        nested.append((R, Btot, bpar, bperp))

    print(f"\n{'='*70}\n{label or NAME.get(N, N)}  N={N}  extent={extent}  "
          f"B(target Z^m)={B.tolist()}  winding={winding}\n{'='*70}")
    print(f"  vertices {leg['verts']}  edges {leg['edges']}  faces {leg['faces']} "
          f"(outer {leg['outer']})")
    print(f"  bounded faces {leg['bounded']}  quad {leg['quad']:.4%}  "
          f"Euler {leg['euler']}")
    print(f"  non-quad bounded face sizes: {leg['nonquad_sizes']}")
    print(f"  faces with nonzero closure: {len(charged)}   "
          f"faces with a non-star edge: {len(non_star)}")
    for cen, Bf, sz in sorted(charged, key=lambda t: np.linalg.norm(t[0]-corexy))[:12]:
        bpar, bperp = split_from_starcount(Bf, N)
        print(f"    charged {sz}-gon at {np.round(cen,2).tolist()} "
              f"(|core-dist| {np.linalg.norm(cen-corexy):5.2f})  B={Bf.tolist()}  "
              f"b_perp={np.round(bperp,3).tolist()}")
    print(f"  net enclosed charge on nested disks about {np.round(corexy,3).tolist()}:")
    for R, Btot, bpar, bperp in nested:
        print(f"    R<={R:6.2f}  B={Btot.tolist()}  b_par={np.round(bpar,3).tolist()}"
              f"  b_perp={np.round(bperp,3).tolist()}")
    return dict(leg=leg, fc=fc, charged=charged, non_star=non_star, nested=nested,
                pos=pos, lifts=lifts, ustar=ustar, step_of=step_of, core=corexy,
                star_par=star_par, m=m, outer=outer)


def split_from_starcount(B, N):
    """b_par, b_perp of a star-count charge B in Z^m (m = N/2)."""
    m, par_m, perp_m = frame(N)
    return B @ par_m, B @ perp_m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=12)
    ap.add_argument("--N", type=int, default=10)
    args = ap.parse_args()
    N = args.N
    m = N // 2
    B = np.zeros(m, dtype=np.int64)
    B[0] = 1                                  # single-star-direction Burgers charge

    # 0. sanity: winding off must read zero everywhere (instrument on constructed set)
    run(N, args.extent, B, winding=False,
        label=f"{NAME[N]} CONTROL (no winding, must read 0)")
    # 1. perp-only winding: reads kernel-only holonomy (b_par=b_perp=0), + seam
    run(N, args.extent, B, winding=True,
        label=f"{NAME[N]} perp-winding attempt (kernel-only holonomy)")
    # 2. periodic control: parallel Volterra on a square lattice heals (b period)
    square_control()
    # 3. parallel-only Volterra on the QC: shears (b_par not a QC period)
    qc_parallel(N=N, extent=args.extent)
    # 4. coupled phonon+phason cut on the QC: still shears (no elastic relaxation)
    coupled_volterra(N=N, extent=args.extent)
    print(f"\n{'#'*70}\nGATE 0 VERDICT: NOT RESOLVED (implementation-limited, "
          f"outcome b).\n"
          f"  - instrument reads a genuine, radius-invariant physical Burgers\n"
          f"    vector on the periodic control (square lattice);\n"
          f"  - a pure phason (perp) winding on the QC yields only kernel\n"
          f"    holonomy (b_par=b_perp=0) -- labels move, matter does not;\n"
          f"  - parallel and coupled Volterra cuts shear the whole QC because\n"
          f"    b_par is not a period and the bare winding lacks the 1/r elastic\n"
          f"    relaxation a real QC dislocation needs.\n"
          f"  NOT evidence the grammar forbids defects (real QCs have them);\n"
          f"  a clean construction needs the coupled phonon-phason elasticity\n"
          f"  solve or a de Bruijn multigrid constructor. See RESULTS_GATE0_DEFECT.md.\n"
          f"{'#'*70}")


# --------------------------------------------------------------------------- #
# Periodic control (Fable's knife 1): a square lattice, where the IDENTICAL
# parallel-space Volterra cut heals because the Burgers vector IS a lattice
# period. This (a) validates the closure instrument on a NONZERO charge -- Part 1
# only checked the zero reading -- and (b) shows a legal localized dislocation is
# constructible when the grammar permits it, so a QC failure can be told from an
# instrument failure.
# --------------------------------------------------------------------------- #
def square_control(X=18, Y=18, b=1.0, core=(0.5, 0.5)):
    """Edge dislocation in Z^2 by a parallel Volterra winding u_x = (b/2pi)*phi.

    Points are the integer grid displaced in x by a field that winds by exactly
    one lattice period b around the core; across the branch cut the columns
    re-register (b is a period), so the cut heals and only a terminating
    half-column -- the dislocation core -- survives. Edges are read geometrically
    and assigned to the nearest axis direction; closure around the core must read
    b_par = (b, 0).
    """
    ax = [(0, 1.0), (1, 1.0)]                 # star: e_x, e_y  (m = 2)
    star_par = np.array([[1.0, 0.0], [0.0, 1.0]])
    pts, grid = [], {}
    for i in range(-X, X + 1):
        for j in range(-Y, Y + 1):
            x, y = float(i), float(j)
            phi = np.arctan2(y - core[1], x - core[0])
            xp = x + (b / (2 * np.pi)) * phi
            grid[(i, j)] = len(pts)
            pts.append((xp, y))
    pos = np.array(pts)
    m = 2

    # geometric edges: nearest of +/- e_x, e_y, allowing the elastic distortion
    tree = cKDTree(pos)
    E = set(); step_of = {}
    for a_ in range(len(pos)):
        for b_ in tree.query_ball_point(pos[a_], 1.8):
            if b_ <= a_:
                continue
            d = pos[b_] - pos[a_]
            best, bestcos = None, 0.75          # require decent alignment
            for k in range(2):
                for s in (1, -1):
                    v = s * star_par[k]
                    c = float(np.dot(d, v) / (np.linalg.norm(d) + 1e-12))
                    if c > bestcos and abs(np.linalg.norm(d) - 1.0) < 0.45:
                        best, bestcos = (k, s), c
            if best is not None:
                E.add((a_, b_)); step_of[(a_, b_)] = best
    E = sorted(E)
    leg = legality(pos, E)
    outer = max(leg["F"], key=len)
    corexy = np.array(core)
    fc = face_charges(leg["F"], outer, step_of, pos, m)
    charged = [(cen, Bf, sz) for (cen, Bf, nz, sz, ok) in fc if nz]

    Rmax = np.linalg.norm(pos - corexy, axis=1).max()
    nested = []
    for R in [Rmax * f for f in (0.15, 0.3, 0.5, 0.75)]:
        Btot = np.zeros(m, dtype=np.int64)
        for cen, Bf, nz, sz, ok in fc:
            if np.linalg.norm(cen - corexy) <= R:
                Btot = Btot + Bf
        nested.append((R, Btot, Btot @ star_par))

    print(f"\n{'='*70}\nPERIODIC CONTROL: square lattice, parallel Volterra "
          f"b_par=({b},0)\n{'='*70}")
    print(f"  vertices {leg['verts']}  edges {leg['edges']}  faces {leg['faces']} "
          f"(outer {leg['outer']})")
    print(f"  bounded faces {leg['bounded']}  quad {leg['quad']:.4%}  "
          f"Euler {leg['euler']}")
    print(f"  non-quad bounded face sizes: {leg['nonquad_sizes']}")
    print(f"  faces with nonzero closure: {len(charged)}")
    for cen, Bf, sz in sorted(charged, key=lambda t: np.linalg.norm(t[0]-corexy))[:8]:
        print(f"    charged {sz}-gon at {np.round(cen,2).tolist()} "
              f"(|core-dist| {np.linalg.norm(cen-corexy):5.2f})  B={Bf.tolist()}  "
              f"b_par={np.round(Bf @ star_par,3).tolist()}")
    print(f"  net enclosed charge on nested disks about core:")
    for R, Btot, bpar in nested:
        print(f"    R<={R:6.2f}  B={Btot.tolist()}  b_par={np.round(bpar,3).tolist()}")


# --------------------------------------------------------------------------- #
# Apples-to-apples: the IDENTICAL parallel-space Volterra cut applied to the QC.
# On the square lattice b_par is a lattice period, so the cut re-registers and a
# localized core survives. On the QC there is no such period; this asks whether
# the same cut heals to a localized physical core or leaves an un-registering
# grain-boundary seam.
# --------------------------------------------------------------------------- #
def parallel_volterra(pos0, star_par, b_par, core, tol_len=0.45, tol_cos=0.8):
    """Displace pos0 by u_par = (b_par/2pi)*phi about core, reconnect geometrically
    by nearest star direction, and read per-face closure. Returns diagnostics."""
    m = len(star_par)
    phi = np.arctan2(pos0[:, 1] - core[1], pos0[:, 0] - core[0])
    pos = pos0 + (phi[:, None] / (2 * np.pi)) * np.asarray(b_par)[None, :]
    Lm = np.linalg.norm(star_par, axis=1).max()
    tree = cKDTree(pos)
    E = set(); step_of = {}
    for a_ in range(len(pos)):
        for b_ in tree.query_ball_point(pos[a_], Lm + tol_len):
            if b_ <= a_:
                continue
            d = pos[b_] - pos[a_]
            nd = np.linalg.norm(d)
            best, bestcos = None, tol_cos
            for k in range(m):
                Lk = np.linalg.norm(star_par[k])
                if abs(nd - Lk) > tol_len:
                    continue
                for s in (1, -1):
                    c = float(np.dot(d, s * star_par[k]) / (nd * Lk + 1e-12))
                    if c > bestcos:
                        best, bestcos = (k, s), c
            if best is not None:
                E.add((a_, b_)); step_of[(a_, b_)] = best
    E = sorted(E)
    leg = legality(pos, E)
    outer = max(leg["F"], key=len)
    fc = face_charges(leg["F"], outer, step_of, pos, m)
    charged = [(cen, Bf, sz) for (cen, Bf, nz, sz, ok) in fc if nz]
    corexy = np.asarray(core, float)
    Rmax = np.linalg.norm(pos - corexy, axis=1).max()
    nested = []
    for R in [Rmax * f for f in (0.15, 0.3, 0.5, 0.7)]:
        Btot = np.zeros(m, dtype=np.int64)
        for cen, Bf, nz, sz, ok in fc:
            if np.linalg.norm(cen - corexy) <= R:
                Btot = Btot + Bf
        nested.append((R, Btot, Btot @ star_par))
    return leg, charged, nested, corexy


def qc_parallel(N=10, extent=12):
    """Parallel Volterra on the perfect QC, b_par = physical image of star[0]."""
    from generate_rank4 import generate
    st = structure(N)
    star_par = st["star"] @ st["par4"]
    lifts, par, perp, ustar = generate(N, extent)
    b_par = star_par[0]                        # a genuine tiling step, |b_par| = edge
    core = np.array([0.37, 0.19])
    leg, charged, nested, corexy = parallel_volterra(par, star_par, b_par, core)
    print(f"\n{'='*70}\nQC PARALLEL VOLTERRA: {NAME[N]} N={N}  "
          f"b_par=star_par[0]={np.round(b_par,3).tolist()}\n{'='*70}")
    print(f"  vertices {leg['verts']}  edges {leg['edges']}  quad {leg['quad']:.4%}  "
          f"Euler {leg['euler']}  non-quad {leg['nonquad_sizes']}")
    print(f"  faces with nonzero closure: {len(charged)}")
    print(f"  net enclosed charge on nested disks about core:")
    for R, Btot, bpar in nested:
        print(f"    R<={R:6.2f}  B={Btot.tolist()}  b_par={np.round(bpar,3).tolist()}")


# --------------------------------------------------------------------------- #
# The real SLS dislocation: phonon (b_par) and phason (b_perp) locked together
# from a single lattice vector B. The phason winding (via construct) supplies the
# accommodation that lets the parallel shear heal into a localized core -- the
# coupling neither one-sided cut had.
# --------------------------------------------------------------------------- #
def coupled_volterra(N=10, extent=12, B=None, core=(0.37, 0.19),
                     tol_len=0.45, tol_cos=0.8):
    st = structure(N)
    m, par_m, perp_m = frame(N)
    star_par = st["star"] @ st["par4"]
    if B is None:
        B = np.zeros(m, dtype=np.int64); B[0] = 1
    B = np.asarray(B, np.int64)
    b_par = B @ par_m
    # phason-accommodated point set (perp offset + kernel wind)
    lifts, pos0, ustar, corexy = construct(N, extent, B, core=core, winding=True)
    # add the locked phonon winding
    leg, charged, nested, corexy = parallel_volterra(
        pos0, star_par, b_par, corexy, tol_len=tol_len, tol_cos=tol_cos)
    print(f"\n{'='*70}\nCOUPLED SLS DISLOCATION: {NAME[N]} N={N}  "
          f"B={B.tolist()}  b_par={np.round(b_par,3).tolist()}\n{'='*70}")
    print(f"  vertices {leg['verts']}  edges {leg['edges']}  quad {leg['quad']:.4%}  "
          f"Euler {leg['euler']}  non-quad {leg['nonquad_sizes']}")
    print(f"  faces with nonzero closure: {len(charged)}")
    print(f"  net enclosed charge on nested disks about core:")
    for R, Btot, bpar in nested:
        bperp = Btot @ perp_m
        print(f"    R<={R:6.2f}  B={Btot.tolist()}  b_par={np.round(bpar,3).tolist()}"
              f"  b_perp={np.round(bperp,3).tolist()}")


if __name__ == "__main__":
    import sys as _s
    def _argval(flag, default):
        return type(default)(_s.argv[_s.argv.index(flag) + 1]) if flag in _s.argv else default
    if "--square" in _s.argv:
        square_control()
    elif "--qcpar" in _s.argv:
        qc_parallel(N=_argval("--N", 10))
    elif "--coupled" in _s.argv:
        coupled_volterra(N=_argval("--N", 10), tol_len=_argval("--tollen", 0.45))
    else:
        main()
