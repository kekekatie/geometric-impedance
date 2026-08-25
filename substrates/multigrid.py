#!/usr/bin/env python3
"""
De Bruijn multigrid constructor for the rank-4 families (8-, 10-, 12-fold).

This is the combinatorial route to the lifted-defect audit's Gate 0. The
cut-and-project generator (`generate_rank4.py`) makes the perfect tiling by an
acceptance test; a defect then needs an elastic relaxation we did not solve
(see RESULTS_GATE0_DEFECT.md). The multigrid builds the *same* tilings as the
dual of m = N/2 line grids, where every face is a rhombus BY CONSTRUCTION -- so a
terminating grid line yields an all-rhombus tiling with an isolated core and no
elasticity to solve.

STEP 1 (DONE, validated): build the *perfect* dual and prove the bridge --
that a multigrid vertex lives in our existing lift world. A dual vertex is labelled
by its integer grid-index vector K in Z^m; its rank-4 lift is a = K @ S (S =
reduce_powers), its position is K @ par_m, and an edge steps K by a single unit
e_j = one star direction. So the Part-1 closure instrument (`lifted_defect.closure`,
which reads star steps off the Z^4 lift) applies unchanged. Gate: the dual is 100%
rhombi and every face closes to zero. Confirmed on all three families (`validate`).

STEP 2 (attempted; the crux found, not yet passed). Three constructions are kept
here as the record: `dual_defect` (offset winding by phi/2pi), `dual_defect_sampled`
(region sampling), `dual_defect_exact` (a terminating half-line with an explicit
slip row). All produce exact/near-exact rhombi but read ZERO closure. The reason is
structural and now proven: any construction that assigns each vertex a *single-valued*
index K(r) has closure that telescopes to zero on every loop -- a single-valued lift
forbids a Burgers charge by construction. A genuine dislocation needs a non-rhombus
CORE FACE whose boundary steps sum to b_k, which requires a *forced* matching
mismatch (a Sum-gamma winding), and that reintroduces the branch-cut seam / kernel
holonomy seen in `lifted_defect_gate0.py`. A generic terminating half-line just heals
trivially. So the clean combinatorial dislocation needs explicit local tile surgery
(cut a wedge, close it with a non-rhombus core), not an index formula. See
RESULTS_GATE0_DEFECT.md for the standing Gate-0 verdict (outcome b, not resolved).
The bridge (Step 1) stands as a reusable second generator regardless.
"""

import argparse
import itertools
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import frame, reduce_powers, structure
from tile_audit import faces, shape_key
from lifted_defect import closure

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def default_gamma(m, seed=0):
    """Generic grid intercepts summing to 0 (singularity-free, no triple lines)."""
    rng = np.random.default_rng(seed)
    g = rng.uniform(0.1, 0.4, m)
    return g - g.mean()


def dual(N, L=8, R=None, gamma=None, seed=0):
    """Perfect de Bruijn dual tiling.

    Returns lifts (Z^4), positions, index-vectors K (Z^m), edges, and rhombi
    (4-cycles of vertex indices). Grid family j has lines r . n_j + gamma_j in Z,
    with n_j the j-th star direction; each pairwise line intersection contributes
    one rhombus with corners K + {0,1} e_p + {0,1} e_q.
    """
    m, par_m, perp_m = frame(N)
    S = reduce_powers(N)                      # m x 4  (Z^m -> Z^4 ring reduction)
    n = par_m                                 # m grid normals (unit star dirs)
    if gamma is None:
        gamma = default_gamma(m, seed)
    if R is None:
        R = L * 0.9

    vidx = {}                                 # index-vector tuple -> vertex id
    Ks = []

    def vid(K):
        t = tuple(int(x) for x in K)
        if t not in vidx:
            vidx[t] = len(Ks)
            Ks.append(np.array(t, dtype=np.int64))
        return vidx[t]

    rhombi = []
    for p in range(m):
        for q in range(p + 1, m):
            M = np.array([n[p], n[q]])
            det = M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0]
            if abs(det) < 1e-9:
                continue
            Minv = np.linalg.inv(M)
            for Kp in range(-L, L + 1):
                for Kq in range(-L, L + 1):
                    r = Minv @ np.array([Kp - gamma[p], Kq - gamma[q]])
                    if np.hypot(*r) > R:
                        continue
                    K = np.ceil(r @ n.T + gamma - 1e-9).astype(np.int64)
                    K[p], K[q] = Kp, Kq
                    ep = np.zeros(m, np.int64); ep[p] = 1
                    eq = np.zeros(m, np.int64); eq[q] = 1
                    corners = [vid(K), vid(K + ep), vid(K + ep + eq), vid(K + eq)]
                    rhombi.append(corners)

    K = np.array(Ks)
    lifts = K @ S
    pos = K @ par_m
    E = set()
    for c in rhombi:
        for t in range(4):
            i, j = c[t], c[(t + 1) % 4]
            E.add((min(i, j), max(i, j)))
    return dict(lifts=lifts, pos=pos, K=K, edges=sorted(E), rhombi=rhombi,
                S=S, m=m, par_m=par_m, perp_m=perp_m)


def validate(N, L=8):
    st = structure(N)
    d = dual(N, L=L)
    lifts, pos, S, m = d["lifts"], d["pos"], d["S"], d["m"]
    star = st["star"]

    # (1) every generated rhombus must close to zero under the Part-1 instrument
    worst = 0
    nonstar = 0
    for c in d["rhombi"]:
        B, ok = closure(c, lifts, star, m)
        if not ok:
            nonstar += 1
        worst = max(worst, int(np.abs(B).max()))

    # (2) all faces of the interior embedding are rhombi (drop the outer boundary)
    F = faces(len(pos), d["edges"], pos)
    sz = Counter(len(c) for c in F)
    outer = max(sz)
    bd = [c for c in F if len(c) != outer]
    quad = sum(1 for c in bd if len(c) == 4) / max(len(bd), 1)
    shapes = len(Counter(shape_key(c, pos) for c in bd if len(c) == 4))

    # (3) every face closes to zero too (independent of my rhombus bookkeeping)
    fworst = 0
    for c in bd:
        B, ok = closure(c, lifts, star, m)
        fworst = max(fworst, int(np.abs(B).max()))

    print(f"\n{NAME[N]:>9} (N={N}, m={m})  L={L}")
    print(f"   vertices {len(pos)}  edges {len(d['edges'])}  rhombi {len(d['rhombi'])}")
    print(f"   distinct rhombus shapes: {shapes}   bounded faces {len(bd)}  "
          f"quad {quad:.4%}")
    print(f"   max |closure| over generated rhombi: {worst}   non-star: {nonstar}")
    print(f"   max |closure| over traced faces    : {fworst}")
    ok = worst == 0 and fworst == 0 and nonstar == 0 and quad == 1.0
    print(f"   -> bridge holds (rhombi + zero closure): {'YES' if ok else 'NO'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=8)
    args = ap.parse_args()
    allok = True
    for N in (8, 10, 12):
        allok &= validate(N, L=args.L)
    print(f"\n{'ALL BRIDGES HOLD' if allok else 'BRIDGE FAILED'}")


# --------------------------------------------------------------------------- #
# STEP 2: the terminating-line defect. One grid family's offset winds by 1 around
# the core (gamma_k -> gamma_k + phi/2pi), inserting a single terminating line.
# Vertex positions stay exact integer combinations K @ par_m, so faces stay exact
# rhombi; the monodromy of the winding family's index around the core is a genuine
# physical Burgers vector b_par = par_m[k]. Its own Gate 0 discipline: legality
# (100% rhombi) + radius-invariant enclosed charge, against a periodic control.
# --------------------------------------------------------------------------- #
def dual_defect(N, L=8, kfam=0, wind=1, core=(0.37, 0.19), gamma=None, seed=0,
                iters=12):
    m, par_m, perp_m = frame(N)
    S = reduce_powers(N)
    n = par_m
    if gamma is None:
        gamma = default_gamma(m, seed)
    core = np.asarray(core, float)
    R = L * 0.9

    def gk(r):
        return gamma[kfam] + wind * np.arctan2(r[1] - core[1], r[0] - core[0]) / (2 * np.pi)

    def Kvec(r):
        g = gamma.astype(float).copy()
        g[kfam] = gk(r)
        return np.ceil(r @ n.T + g - 1e-9).astype(np.int64)

    vidx, Ks = {}, []

    def vid(K):
        t = tuple(int(x) for x in K)
        if t not in vidx:
            vidx[t] = len(Ks)
            Ks.append(np.array(t, dtype=np.int64))
        return vidx[t]

    rhombi = []
    for p in range(m):
        for q in range(p + 1, m):
            M = np.array([n[p], n[q]])
            det = M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0]
            if abs(det) < 1e-9:
                continue
            Minv = np.linalg.inv(M)
            wound = kfam in (p, q)
            for Kp in range(-L, L + 1):
                for Kq in range(-L, L + 1):
                    r = Minv @ np.array([Kp - gamma[p], Kq - gamma[q]])
                    if wound:
                        for _ in range(iters):
                            bp = Kp - (gk(r) if p == kfam else gamma[p])
                            bq = Kq - (gk(r) if q == kfam else gamma[q])
                            r = Minv @ np.array([bp, bq])
                    if np.hypot(*(r - 0)) > R:
                        continue
                    K = Kvec(r)
                    K[p], K[q] = Kp, Kq
                    ep = np.zeros(m, np.int64); ep[p] = 1
                    eq = np.zeros(m, np.int64); eq[q] = 1
                    rhombi.append([vid(K), vid(K + ep), vid(K + ep + eq), vid(K + eq)])

    K = np.array(Ks)
    lifts = K @ S
    pos = K @ par_m
    E = set()
    for c in rhombi:
        for t in range(4):
            i, j = c[t], c[(t + 1) % 4]
            E.add((min(i, j), max(i, j)))
    return dict(lifts=lifts, pos=pos, K=K, edges=sorted(E), rhombi=rhombi,
                S=S, m=m, par_m=par_m, perp_m=perp_m, core=core, kfam=kfam)


def measure_defect(N, L=8, kfam=0, wind=1, core=(0.37, 0.19), tag=""):
    st = structure(N)
    star = st["star"]
    d = dual_defect(N, L=L, kfam=kfam, wind=wind, core=core)
    lifts, pos, m = d["lifts"], d["pos"], d["m"]
    par_m, perp_m = d["par_m"], d["perp_m"]
    corexy = d["core"]

    F = faces(len(pos), d["edges"], pos)
    sz = Counter(len(c) for c in F)
    outer = max(sz)
    bd = [c for c in F if len(c) != outer]
    quad = sum(1 for c in bd if len(c) == 4) / max(len(bd), 1)
    nonquad = dict(sorted(Counter(len(c) for c in bd if len(c) != 4).items()))

    # per-face closure (Z^m), enclosed charge on nested disks
    fc = []
    for c in bd:
        B, ok = closure(c, lifts, star, m)
        cen = pos[c].mean(axis=0)
        fc.append((cen, B, ok))
    charged = [(cen, B) for cen, B, ok in fc if np.abs(B).sum() > 0]
    Rmax = np.linalg.norm(pos - corexy, axis=1).max()
    nested = []
    for Rf in (0.2, 0.35, 0.5, 0.7):
        Rr = Rmax * Rf
        Btot = np.zeros(m, np.int64)
        for cen, B, ok in fc:
            if np.linalg.norm(cen - corexy) <= Rr:
                Btot = Btot + B
        nested.append((Rr, Btot, Btot @ par_m, Btot @ perp_m))

    print(f"\n{'='*70}\n{tag or NAME[N]}  N={N}  kfam={kfam}  wind={wind}  "
          f"b_par target=par_m[{kfam}]={np.round(par_m[kfam],3).tolist()}\n{'='*70}")
    print(f"  vertices {len(pos)}  edges {len(d['edges'])}  bounded faces {len(bd)}")
    print(f"  quad {quad:.4%}   non-quad face sizes {nonquad}")
    print(f"  charged faces: {len(charged)}")
    for cen, B in sorted(charged, key=lambda t: np.linalg.norm(t[0]-corexy))[:8]:
        print(f"    at {np.round(cen,2).tolist()} (dist {np.linalg.norm(cen-corexy):5.2f})"
              f"  B={B.tolist()}  b_par={np.round(B@par_m,3).tolist()}  "
              f"b_perp={np.round(B@perp_m,3).tolist()}")
    print(f"  net enclosed charge on nested disks about core:")
    for Rr, Btot, bpar, bperp in nested:
        print(f"    R<={Rr:6.2f}  B={Btot.tolist()}  b_par={np.round(bpar,3).tolist()}"
              f"  b_perp={np.round(bperp,3).tolist()}")
    return d


# --------------------------------------------------------------------------- #
# STEP 2b: defected dual by region sampling (robust across the slip line).
# A dislocation = one family-k half-line (a ray from the core). The region index
# K_k gains +1 on crossing that ray, so crossing it the dual vertex jumps by n_k:
# the ray dualizes to an inserted row of rhombi that terminates at the core, i.e.
# a genuine dislocation with b_par = par_m[k]. Regions are read by sampling K(r)
# on a fine grid (no per-intersection corner bookkeeping, so the slip line cannot
# leave a seam of holes); vertices are unique index-vectors, edges are unit steps.
# --------------------------------------------------------------------------- #
def dual_defect_sampled(N, L=8, kfam=0, core=(0.30, 0.11), gamma=None, seed=0,
                        h=0.06, defect=True, c0=0.5):
    m, par_m, perp_m = frame(N)
    S = reduce_powers(N)
    n = par_m
    if gamma is None:
        gamma = default_gamma(m, seed).astype(float)
    R = L * 0.9
    tk = np.array([-n[kfam, 1], n[kfam, 0]])          # along family-k lines
    core = np.asarray(core, float)
    # put the core exactly on the half-line r.n_k + gamma_k = c0 (mod 1 -> c0)
    core = core + (c0 - (core @ n[kfam] + gamma[kfam])) * n[kfam]

    def Kvec(r):
        K = np.ceil(r @ n.T + gamma - 1e-9).astype(np.int64)
        if defect:
            s = (r - core) @ tk
            above = (r @ n[kfam] + gamma[kfam]) > c0
            if above and s >= 0:
                K[kfam] += 1
        return K

    # sample regions on a fine grid over the disk
    xs = np.arange(-R, R + h, h)
    gx, gy = np.meshgrid(xs, xs)
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    pts = pts[np.hypot(pts[:, 0], pts[:, 1]) <= R]
    vidx, Ks = {}, []
    for r in pts:
        t = tuple(int(x) for x in Kvec(r))
        if t not in vidx:
            vidx[t] = len(Ks)
            Ks.append(t)
    K = np.array(Ks, dtype=np.int64)
    pos = K @ par_m
    lifts = K @ S

    # edges: index-vectors differing by exactly one unit step (a star edge)
    kset = set(map(tuple, K.tolist()))
    E = set()
    for idx, kk in enumerate(K):
        for j in range(m):
            for s in (1, -1):
                nb = tuple((kk + s * np.eye(m, dtype=np.int64)[j]).tolist())
                jdx = vidx.get(nb)
                if jdx is not None:
                    E.add((min(idx, jdx), max(idx, jdx)))
    return dict(lifts=lifts, pos=pos, K=K, edges=sorted(E), S=S, m=m,
                par_m=par_m, perp_m=perp_m, core=core, kfam=kfam)


def measure_sampled(N, L=8, kfam=0, defect=True, tag="", h=0.06):
    st = structure(N)
    star = st["star"]
    d = dual_defect_sampled(N, L=L, kfam=kfam, defect=defect, h=h)
    lifts, pos, m = d["lifts"], d["pos"], d["m"]
    par_m, perp_m, corexy = d["par_m"], d["perp_m"], d["core"]

    F = faces(len(pos), d["edges"], pos)
    outer = max(F, key=len)
    bd = [c for c in F if c is not outer]
    quad = sum(1 for c in bd if len(c) == 4) / max(len(bd), 1)
    nonquad = dict(sorted(Counter(len(c) for c in bd if len(c) != 4).items()))

    fc = []
    for c in bd:
        B, ok = closure(c, lifts, star, m)
        fc.append((pos[c].mean(axis=0), B, ok, len(c)))
    charged = [(cen, B, sz) for cen, B, ok, sz in fc if np.abs(B).sum() > 0]
    Rmax = np.linalg.norm(pos - corexy, axis=1).max()
    nested = []
    for f in (0.2, 0.35, 0.5, 0.7):
        Rr = Rmax * f
        Btot = np.zeros(m, np.int64)
        for cen, B, ok, sz in fc:
            if np.linalg.norm(cen - corexy) <= Rr:
                Btot = Btot + B
        nested.append((Rr, Btot, Btot @ par_m, Btot @ perp_m))

    print(f"\n{'='*70}\n{tag or NAME[N]}  N={N}  kfam={kfam}  defect={defect}  "
          f"b_par target=par_m[{kfam}]={np.round(par_m[kfam],3).tolist()}\n{'='*70}")
    print(f"  vertices {len(pos)}  edges {len(d['edges'])}  bounded faces {len(bd)}")
    print(f"  quad {quad:.4%}   non-quad face sizes {nonquad}")
    print(f"  charged faces: {len(charged)}")
    for cen, B, sz in sorted(charged, key=lambda t: np.linalg.norm(t[0]-corexy))[:8]:
        print(f"    charged {sz}-gon at {np.round(cen,2).tolist()} "
              f"(dist {np.linalg.norm(cen-corexy):5.2f})  B={B.tolist()}  "
              f"b_par={np.round(B@par_m,3).tolist()}  b_perp={np.round(B@perp_m,3).tolist()}")
    print(f"  net enclosed charge on nested disks about core:")
    for Rr, Btot, bpar, bperp in nested:
        print(f"    R<={Rr:6.2f}  B={Btot.tolist()}  b_par={np.round(bpar,3).tolist()}"
              f"  b_perp={np.round(bperp,3).tolist()}")
    return d




# --------------------------------------------------------------------------- #
# STEP 2c: EXACT defected dual via a half-line (ray). Keeps the exact
# intersection construction (so faces are exact rhombi) but (i) counts regions
# with a family-k half-line that exists only for s=(r-core).t_k >= 0, so K_k gains
# +1 across the ray, and (ii) explicitly generates the slip-row rhombi where the
# half-line crosses the other families -- the rhombi the pure winding left as
# holes. The ray dualizes to one inserted row terminating at the core; a loop
# around the core then closes to b_par = par_m[k]. This is the real construction.
# --------------------------------------------------------------------------- #
def dual_defect_exact(N, L=8, kfam=0, core=(0.30, 0.11), gamma=None, seed=0,
                      c0=0.5, defect=True):
    m, par_m, perp_m = frame(N)
    S = reduce_powers(N)
    n = par_m
    if gamma is None:
        gamma = default_gamma(m, seed).astype(float)
    R = L * 0.9
    tk = np.array([-n[kfam, 1], n[kfam, 0]])
    core = np.asarray(core, float)
    core = core + (c0 - (core @ n[kfam] + gamma[kfam])) * n[kfam]   # core on the ray
    eye = np.eye(m, dtype=np.int64)

    def extra(r):
        if not defect:
            return 0
        return int(((r @ n[kfam] + gamma[kfam]) > c0) and ((r - core) @ tk >= 0))

    def Kvec(r):
        K = np.ceil(r @ n.T + gamma - 1e-9).astype(np.int64)
        K[kfam] += extra(r)
        return K

    vidx, Ks = {}, []

    def vid(K):
        t = tuple(int(x) for x in K)
        if t not in vidx:
            vidx[t] = len(Ks); Ks.append(t)
        return vidx[t]

    rhombi = []
    # (i) integer-integer intersections
    for p in range(m):
        for q in range(p + 1, m):
            M = np.array([n[p], n[q]]); det = M[0, 0]*M[1, 1] - M[0, 1]*M[1, 0]
            if abs(det) < 1e-9:
                continue
            Minv = np.linalg.inv(M)
            for Kp in range(-L, L + 1):
                for Kq in range(-L, L + 1):
                    r = Minv @ np.array([Kp - gamma[p], Kq - gamma[q]])
                    if np.hypot(*r) > R:
                        continue
                    K = Kvec(r)
                    if p != kfam:
                        K[p] = Kp
                    if q != kfam:
                        K[q] = Kq
                    rhombi.append([vid(K), vid(K + eye[p]),
                                   vid(K + eye[p] + eye[q]), vid(K + eye[q])])
    # (ii) slip row: half-line (family k at offset c0) crossing family p, s >= 0
    if defect:
        for p in range(m):
            if p == kfam:
                continue
            M = np.array([n[kfam], n[p]]); det = M[0, 0]*M[1, 1] - M[0, 1]*M[1, 0]
            if abs(det) < 1e-9:
                continue
            Minv = np.linalg.inv(M)
            for Kp in range(-L, L + 1):
                r = Minv @ np.array([c0 - gamma[kfam], Kp - gamma[p]])
                if np.hypot(*r) > R or (r - core) @ tk < 0:
                    continue
                rbb = r - 1e-6 * (n[kfam] + n[p])       # just below the ray and line p
                K0 = Kvec(rbb)                           # correct ceils for that region
                rhombi.append([vid(K0), vid(K0 + eye[p]),
                               vid(K0 + eye[p] + eye[kfam]), vid(K0 + eye[kfam])])

    K = np.array(Ks, dtype=np.int64)
    lifts = K @ S
    pos = K @ par_m
    E = set()
    for c in rhombi:
        for t in range(4):
            i, j = c[t], c[(t + 1) % 4]
            if i != j:
                E.add((min(i, j), max(i, j)))
    return dict(lifts=lifts, pos=pos, K=K, edges=sorted(E), rhombi=rhombi,
                S=S, m=m, par_m=par_m, perp_m=perp_m, core=core, kfam=kfam)


def measure_exact(N, L=8, kfam=0, defect=True, tag=""):
    st = structure(N); star = st["star"]
    d = dual_defect_exact(N, L=L, kfam=kfam, defect=defect)
    lifts, pos, m = d["lifts"], d["pos"], d["m"]
    par_m, perp_m, corexy = d["par_m"], d["perp_m"], d["core"]

    # closure on each generated rhombus (exact) and via traced faces
    rworst = max(int(np.abs(closure(c, lifts, star, m)[0]).max()) for c in d["rhombi"])
    F = faces(len(pos), d["edges"], pos)
    outer = max(F, key=len)
    bd = [c for c in F if c is not outer]
    quad = sum(1 for c in bd if len(c) == 4) / max(len(bd), 1)
    nonquad = dict(sorted(Counter(len(c) for c in bd if len(c) != 4).items()))
    fc = [(pos[c].mean(0), *closure(c, lifts, star, m), len(c)) for c in bd]
    charged = [(cen, B, sz) for cen, B, ok, sz in fc if np.abs(B).sum() > 0]
    Rmax = np.linalg.norm(pos - corexy, axis=1).max()
    nested = []
    for f in (0.2, 0.35, 0.5, 0.7):
        Rr = Rmax * f
        Btot = sum((B for cen, B, ok, sz in fc
                    if np.linalg.norm(cen - corexy) <= Rr), np.zeros(m, np.int64))
        nested.append((Rr, Btot, Btot @ par_m, Btot @ perp_m))

    print(f"\n{'='*70}\n{tag or NAME[N]}  N={N}  kfam={kfam}  defect={defect}  "
          f"b_par target=par_m[{kfam}]={np.round(par_m[kfam],3).tolist()}\n{'='*70}")
    print(f"  vertices {len(pos)}  edges {len(d['edges'])}  bounded faces {len(bd)}")
    print(f"  quad {quad:.4%}   non-quad face sizes {nonquad}   "
          f"max|rhombus closure| {rworst}")
    print(f"  charged faces: {len(charged)}")
    for cen, B, sz in sorted(charged, key=lambda t: np.linalg.norm(t[0]-corexy))[:8]:
        print(f"    charged {sz}-gon at {np.round(cen,2).tolist()} "
              f"(dist {np.linalg.norm(cen-corexy):5.2f})  B={B.tolist()}  "
              f"b_par={np.round(B@par_m,3).tolist()}  b_perp={np.round(B@perp_m,3).tolist()}")
    print(f"  net enclosed charge on nested disks about core:")
    for Rr, Btot, bpar, bperp in nested:
        print(f"    R<={Rr:6.2f}  B={Btot.tolist()}  b_par={np.round(bpar,3).tolist()}"
              f"  b_perp={np.round(bperp,3).tolist()}")
    return d

if __name__ == "__main__":
    if "--exact" in sys.argv:
        _N = int(sys.argv[sys.argv.index("--N") + 1]) if "--N" in sys.argv else 10
        _L = int(sys.argv[sys.argv.index("--L") + 1]) if "--L" in sys.argv else 8
        measure_exact(_N, L=_L, defect=("--perfect" not in sys.argv))
    elif "--sampled" in sys.argv:
        _N = int(sys.argv[sys.argv.index("--N") + 1]) if "--N" in sys.argv else 10
        _L = int(sys.argv[sys.argv.index("--L") + 1]) if "--L" in sys.argv else 8
        measure_sampled(_N, L=_L, defect=("--perfect" not in sys.argv))
    elif "--defect" in sys.argv:
        _N = int(sys.argv[sys.argv.index("--N") + 1]) if "--N" in sys.argv else 10
        _L = int(sys.argv[sys.argv.index("--L") + 1]) if "--L" in sys.argv else 9
        measure_defect(_N, L=_L)
    else:
        main()
