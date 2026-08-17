#!/usr/bin/env python3
"""
Rank-4 congruence-window quasicrystals: 8-, 10- and 12-fold, all at
perpendicular dimension 2, all with the complete N-fold star.

Two earlier families each failed one requirement. The Z^4 cyclotomic family
matched perpendicular dimension but its edge rule ("differ by one basis vector")
is basis-dependent: it spans the complete octagonal star only because zeta_8^4 =
-1, and amputates the 10- and 12-fold stars, leaving the 10-fold substrate with
664 crossing edges and no face structure. The Z^m family carries complete stars
and tiles properly, but its extra perpendicular coordinates are not inert, so
perpendicular dimension genuinely differs.

This construction fails neither, because the extra dimensions were never real.
Z[zeta_N] has rank 4 for N = 8, 10, 12. The star has m = N/2 directions, and the
relation lattice K = ker(Z^m -> Z[zeta_N]) has rank m - 4 = 0, 1, 2, spanned by
the shifts of the cyclotomic polynomial's coefficients:

    N =  8   Phi_8  = x^4 + 1          degree 5 > m = 4    K = 0        1 class
    N = 10   Phi_10 = x^4-x^3+x^2-x+1  (1,-1,1,-1,1)       K rank 1     5 classes
    N = 12   Phi_12 = x^4 - x^2 + 1    (1,0,-1,0,1) + shift  K rank 2   9 classes

Because K is orthogonal to both the parallel plane and the Galois-conjugate
plane, the "extra" perpendicular coordinates of a lattice point are fixed by its
class modulo K. They are a finite label, not a continuum. So the acceptance
window is a union of pieces in a 2-dimensional perpendicular space, indexed by a
congruence class of the rank-4 point - which is exactly what Penrose's four
pentagons have always been.

The number of window pieces is then a mechanism variable forced by the
arithmetic rather than imposed by hand.
"""

import argparse
import itertools
import sys

import numpy as np
from scipy.spatial import ConvexHull

sys.path.insert(0, __file__.rsplit("/", 1)[0])

GALOIS = {8: 3, 10: 3, 12: 5}
# Coefficients of Phi_N, low order first.
PHI = {8: [1, 0, 0, 0, 1], 10: [1, -1, 1, -1, 1], 12: [1, 0, -1, 0, 1]}


def frame(N):
    """Star directions, parallel and Galois-perpendicular frames in Z^m."""
    m = N // 2
    g = GALOIS[N]
    k = np.arange(m)
    par = np.column_stack([np.cos(2 * np.pi * k / N), np.sin(2 * np.pi * k / N)])
    perp = np.column_stack([np.cos(2 * np.pi * g * k / N),
                            np.sin(2 * np.pi * g * k / N)])
    return m, par, perp


def kernel(N):
    """Integer basis of ker(Z^m -> Z[zeta_N]), as rows. Empty when m = 4."""
    m = N // 2
    phi = PHI[N]
    rows = [[0] * s + phi + [0] * (m - len(phi) - s)
            for s in range(m - len(phi) + 1)]
    K = np.array(rows, dtype=np.int64) if rows else np.zeros((0, m), dtype=np.int64)
    if len(K):
        m_, par, perp = frame(N)
        assert np.allclose(K @ par, 0, atol=1e-9), N
        assert np.allclose(K @ perp, 0, atol=1e-9), N
    assert K.shape == (m - 4, m), (N, K.shape)
    return K


def reduce_powers(N):
    """zeta_N^k for k = 0..m-1 written in the basis 1, zeta, zeta^2, zeta^3."""
    m = N // 2
    phi = PHI[N]
    tail = -np.array(phi[:4], dtype=np.int64)          # zeta^4 = -(phi0..phi3)
    out = [np.eye(4, dtype=np.int64)[0]]
    for _ in range(1, m):
        w = np.roll(out[-1], 1)
        c = w[0]
        w = w.copy()
        w[0] = 0
        out.append(w + c * tail)
    return np.array(out)                                # m x 4


def structure(N):
    """Everything the rank-4 acceptance test needs.

    Returns star (m x 4 integer steps), par4/perp4 (4 x 2 frames in the rank-4
    basis), the class functional and modulus, and the zonotope facets in the
    (2 + rank K)-dimensional perpendicular space.
    """
    m, par_m, perp_m = frame(N)
    K = kernel(N)
    S = reduce_powers(N)
    par4 = np.linalg.lstsq(S.astype(float), par_m, rcond=None)[0]
    perp4 = np.linalg.lstsq(S.astype(float), perp_m, rcond=None)[0]
    assert np.allclose(S @ par4, par_m, atol=1e-9)
    assert np.allclose(S @ perp4, perp_m, atol=1e-9)

    G = (K @ K.T).astype(float) if len(K) else np.zeros((0, 0))
    # Class functional on Z^4: pad a to Z^m with zeros, then apply K.
    chi = K[:, :4].astype(np.int64) if len(K) else np.zeros((0, 4), dtype=np.int64)
    mod = np.round(np.diag(G)).astype(np.int64) if len(K) else np.zeros(0, dtype=np.int64)
    if len(K):
        assert np.allclose(G, np.diag(np.diag(G))), (N, G)   # orthogonal basis

    # Orthonormal basis of K (x) R, and the zonotope of the projected m-cube in
    # perpendicular space = Galois plane (+) K (x) R.
    Kb = np.linalg.qr(K.T.astype(float))[0] if len(K) else np.zeros((m, 0))
    B = np.column_stack([perp_m, Kb])                    # m x (2 + rank K)
    signs = np.array(list(itertools.product([-0.5, 0.5], repeat=m)))
    hull = ConvexHull(signs @ B)
    A, b = hull.equations[:, :-1], -hull.equations[:, -1]
    return dict(m=m, star=S, par4=par4, perp4=perp4, K=K, Kb=Kb, G=G,
                chi=chi, mod=mod, A=A, b=b, classes=int(round(np.prod(mod))) if len(K) else 1)


def _extra_positions(st, a):
    """Perpendicular coordinates along K (x) R for every preimage of a.

    Preimages of a in Z^m differ by K, so the integer functional u = K n runs
    over u0 + G z. Each u gives extra perpendicular position K^T G^-1 u,
    expressed in the orthonormal basis Kb.
    """
    K, G, Kb, mod = st["K"], st["G"], st["Kb"], st["mod"]
    if not len(K):
        return [(np.zeros((len(a), 0), dtype=np.int64), np.zeros((len(a), 0)))]
    u0 = a @ st["chi"].T                                  # n x rank
    # The offset z must be centred per point, not swept over a fixed absolute
    # range. u0 grows linearly with distance from the origin, so a fixed span
    # stops containing the relevant preimage beyond some radius and the patch
    # silently saturates - N = 12 froze at 561 vertices for extents 22, 26 and
    # 30. Reduce u0 into the symmetric residue range first, then look only at
    # immediate neighbours.
    base = u0 - mod * np.rint(u0 / mod).astype(np.int64)
    Gi = np.linalg.inv(G)
    out = []
    for dz in itertools.product([-1, 0, 1], repeat=len(K)):
        u = base + np.array(dz, dtype=np.int64) * mod
        out.append((u, (u @ Gi @ K.astype(float)) @ Kb))
    return out


# The zonotope's extent along each extra direction exactly equals the spacing
# between successive preimages of the same rank-4 point (measured ratio 1.0000
# for N = 10 and both directions of N = 12). That is the marginal case: with a
# closed window and no offset, a point sitting exactly on a slice boundary lands
# on the shared facet of two neighbouring preimages and is accepted twice, so
# the tiling gains spurious edges.
#
# There are two ways to break the tie. A GENERIC OFFSET along the extra
# directions removes every tie by moving the cut - but it slices the zonotope at
# arbitrary levels, producing near-degenerate slivers (52 points in one 10-fold
# class) and strongly heterogeneous local environments. That makes the
# congruence class predict vertex degree and hence retention, so the class stops
# being inert. This is what voided the first headline run; see RANK4_HEADLINE.md.
#
# The SINGULAR CONVENTION is the fix Penrose itself uses: take the natural window
# sections (no offset, ex_off = 0) and break the exact ties with a deterministic
# HALF-OPEN rule - a boundary point is awarded to exactly one of its neighbouring
# preimages by a fixed key (the lexicographically smallest congruence label u).
# The cut is never moved, so the pieces stay balanced, as Penrose's four pentagons
# are. This is `generate`'s default. The old generic offset is kept below only so
# the defective substrate can still be reproduced for comparison figures.
EXTRA_OFFSET = (0.0731, 0.0517)

# Tolerance for "exactly on the commensurate boundary". The extra-direction ties
# are exact to floating point (the lattice lands on the facet plane to ~1e-10),
# while the Galois coordinates carry a generic offset and never tie systematically,
# so a band this tight catches every real tie and no spurious near-miss.
_TIE_TOL = 1e-7


def generate(N, extent, offset=None, disorder=0.0, seed=0, extra_offset=None,
             disorder_extra=False):
    """Rank-4 cut and project. Lifts are Z^4 points; the address is 2D.

    By default the extra (K x R) directions use the singular convention: no
    offset, with exact boundary ties broken half-open by awarding the point to
    the preimage with the smallest congruence label. Passing `extra_offset`
    explicitly (e.g. EXTRA_OFFSET) restores the old generic-offset behaviour,
    which manufactures class slivers and is retained only for comparison.

    `disorder` jitters the two Galois perpendicular coordinates before the
    acceptance test. With `disorder_extra`, the coordinates along K (x) R are
    jittered too, which lets a point be accepted through a different preimage -
    a congruence-class flip. The extra noise is drawn once per candidate point
    and shared across that point's preimages, since it models a perturbation of
    the point rather than of the bookkeeping.
    """
    st = structure(N)
    r = st["K"].shape[0]
    if offset is None:
        offset = np.array([0.1123, 0.0847])
    singular = extra_offset is None                      # the fixed default
    ex_off = np.zeros(r) if singular else np.array(extra_offset[:r])
    rng = np.random.default_rng(seed)

    axis = np.arange(-extent, extent + 1, dtype=np.int64)
    tail = np.array(list(itertools.product(axis, repeat=3)), dtype=np.int64)
    kept = []
    for first in axis:
        a = np.empty((len(tail), 4), dtype=np.int64)
        a[:, 0] = first
        a[:, 1:] = tail
        gal = a @ st["perp4"] + np.asarray(offset)
        if disorder > 0:
            gal = gal + rng.normal(0.0, disorder, gal.shape)
        ex_noise = (rng.normal(0.0, disorder, (len(a), r))
                    if (disorder > 0 and disorder_extra and r) else 0.0)

        if r == 0:
            keep = np.all(gal @ st["A"].T <= st["b"], axis=1)
            if keep.any():
                kept.append(a[keep].astype(np.int64))
            continue

        pre = _extra_positions(st, a)                     # list of (u, ex)
        P = len(pre)
        # Slack = how far inside the window each preimage sits (>= 0 inside).
        slack = np.empty((len(a), P))
        us = np.empty((len(a), P, r), dtype=np.int64)
        for p, (u, ex) in enumerate(pre):
            pp = np.column_stack([gal, ex + ex_off + ex_noise])
            slack[:, p] = (st["b"] - pp @ st["A"].T).min(axis=1)
            us[:, p] = u

        if singular:
            # Half-open: accept inside-or-on-boundary, then, among a point's
            # qualifying preimages, keep the one with the smallest label u. A
            # strictly interior point has a single qualifier; only exact-boundary
            # ties present several, and they are resolved deterministically.
            qual = slack >= -_TIE_TOL
            lex = us[:, :, 0].astype(np.float64)
            for d in range(1, r):
                lex = lex * 1000.0 + us[:, :, d]
            lex = np.where(qual, lex, np.inf)
            best = lex.argmin(axis=1)
            keep = qual.any(axis=1)
        else:
            # Old closed test: the generic offset guarantees at most one hit.
            ok = slack >= 0.0
            hits = ok.sum(axis=1)
            assert hits.max() <= 1, (N, "point accepted by two preimages")
            best = ok.argmax(axis=1)
            keep = hits == 1

        if keep.any():
            chosen = us[np.arange(len(a)), best]
            kept.append(np.column_stack([a[keep], chosen[keep]]))

    if kept:
        blk = np.concatenate(kept)
        lifts, ustar = blk[:, :4], blk[:, 4:]
    else:
        lifts = np.zeros((0, 4), dtype=np.int64)
        ustar = np.zeros((0, r), dtype=np.int64)
    return lifts, lifts @ st["par4"], lifts @ st["perp4"] + np.asarray(offset), ustar


def build_edges(lifts, N, ustar=None):
    """Edges along the complete N-fold star.

    A rank-4 step by zeta^k is necessary but not sufficient. Two accepted points
    may differ by zeta^k while their accepted preimages in Z^m differ by e_k
    *plus a kernel element*, which is not an edge of the tiling. The extra
    functional u = K n must therefore advance by exactly K e_k as well; without
    that check the 12-fold graph picks up spurious edges and its mean degree
    rises above the ~4 that any quadrangulation must have.
    """
    st = structure(N)
    K = st["K"]
    idx = {tuple(r): i for i, r in enumerate(lifts)}
    E = set()
    for i, row in enumerate(lifts):
        for k, s in enumerate(st["star"]):
            j = idx.get(tuple(row + s))
            if j is None:
                continue
            if len(K) and not np.array_equal(ustar[j] - ustar[i], K[:, k]):
                continue
            E.add((min(i, j), max(i, j)))
    return sorted(E)


def classes_of(lifts, N):
    st = structure(N)
    if not len(st["K"]):
        return np.zeros(len(lifts), dtype=np.int64)
    u = (lifts @ st["chi"].T) % st["mod"]
    w = np.concatenate([[1], np.cumprod(st["mod"])[:-1]])
    return u @ w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=10)
    args = ap.parse_args()
    for N in (8, 10, 12):
        st = structure(N)
        lifts, par, perp, ustar = generate(N, args.extent)
        E = build_edges(lifts, N, ustar)
        deg = np.zeros(len(lifts), int)
        for u, v in E:
            deg[u] += 1
            deg[v] += 1
        L = np.linalg.norm(par[[u for u, _ in E]] - par[[v for _, v in E]], axis=1)
        ang = np.degrees(np.arctan2(*(st["star"] @ st["par4"]).T[::-1])) % 180
        cl = classes_of(lifts, N)
        print(f"N={N:>3}  m={st['m']}  rank K={st['K'].shape[0]}  "
              f"classes={st['classes']}  occupied={len(set(cl.tolist()))}")
        print(f"       vertices {len(lifts):6d}  edges {len(E):6d}  "
              f"mean deg {deg.mean():.3f}  edge lengths {len(set(np.round(L,6)))}")
        print(f"       star lines {sorted(np.unique(np.round(ang,3)))}")


if __name__ == "__main__":
    main()
