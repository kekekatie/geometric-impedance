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
# closed window and no offset, points sitting exactly on a slice boundary are
# accepted twice, once for each neighbouring preimage, and the tiling gains
# spurious edges. A generic offset along the extra directions removes every tie
# and leaves exactly one accepted preimage per point, which `generate` asserts.
EXTRA_OFFSET = (0.0731, 0.0517)


def generate(N, extent, offset=None, disorder=0.0, seed=0, extra_offset=None,
             disorder_extra=False):
    """Rank-4 cut and project. Lifts are Z^4 points; the address is 2D.

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
    ex_off = np.array((EXTRA_OFFSET if extra_offset is None else extra_offset)[:r])
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
        hits = np.zeros(len(a), dtype=np.int8)
        chosen = np.zeros((len(a), r), dtype=np.int64)
        for u, ex in _extra_positions(st, a):
            pp = np.column_stack([gal, ex + ex_off + ex_noise]) if r else gal
            ok = np.all(pp @ st["A"].T <= st["b"], axis=1)
            hits += ok
            if r:
                chosen[ok] = u[ok]
        assert hits.max() <= 1, (N, "point accepted by two preimages")
        keep = hits == 1
        if keep.any():
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
