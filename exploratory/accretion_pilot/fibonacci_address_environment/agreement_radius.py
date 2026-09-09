#!/usr/bin/env python3
"""
agreement_radius.py -- extension of the Fibonacci address<->environment study (same chain,
same exact Z[tau] arithmetic).  For pairs of sites with IDENTICAL E_2 environments but
DIFFERENT internal addresses, find the first radius r at which their ordered neighbourhoods
differ, and match it against the successive acceptance-window partitions.

Exact backbone:
  * distinct sites have DISTINCT internal addresses q = m + n*tau'  (tau' irrational), so no
    two distinct sites are environment-identical at all radii;
  * the window partitions REFINE monotonically:  boundaries(r) subset boundaries(r+1);
  * therefore two same-E_2 sites agree for all r < r* and first differ at r*, where r* is
    exactly the refinement level at which a window boundary first falls between their two
    (distinct) internal addresses.
  * finite patch: if no difference appears up to the truncation-limited radius, report
    "unresolved within the available patch" -- NOT "identical forever".

No dynamics, no new rules.  asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys
import fibonacci_cutproject as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "agreement_report.txt")
LINES, FAILS = [], []


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


pts = F.generate(46)
N = len(pts)
g = F.gaps_of(pts)
_bnd_cache = {}


def boundaries(r):
    if r not in _bnd_cache:
        _bnd_cache[r] = F.region_boundaries(r)
    return _bnd_cache[r]


def env(i, r):
    if i - r < 0 or i + r > N - 1:
        return None                       # neighbourhood truncated
    return tuple(g[i - r:i + r])


def rmax(i):
    return min(i, N - 1 - i)


def cell(q, r):
    b = boundaries(r)
    return max(k for k in range(len(b) - 1) if b[k] <= q)


def first_disagreement(i, j):
    """Return (r_star, agrees_through, resolved). r_star = first r with env differing;
    if never within min rmax -> unresolved (resolved=False, agrees_through=that rmax)."""
    R = min(rmax(i), rmax(j))
    for r in range(2, R + 1):
        if env(i, r) != env(j, r):
            return r, r - 1, True
    return None, R, False


def sep_boundary(i, j, r):
    """The NEW window boundary (exact) that separates q_i, q_j at level r but not at r-1.
    Cells differ iff a boundary b satisfies lo < b <= hi (half-open, matching the cell rule
    'index = max k with b[k] <= q'); a boundary may coincide with a site's own address."""
    qi, qj = pts[i][1], pts[j][1]
    lo, hi = (qi, qj) if qi < qj else (qj, qi)
    new = [b for b in boundaries(r) if b not in boundaries(r - 1)]
    return [b for b in new if (lo < b) and (b <= hi)]


def main():
    log("=" * 80)
    log("[0] exact backbone")
    # distinct sites -> distinct internal addresses
    qs = [pts[i][1] for i in range(N)]
    inj = len({(q.a, q.b) for q in qs}) == N
    require(inj, "distinct sites have DISTINCT internal addresses (q injective) -> no two "
                 "distinct sites can be environment-identical at ALL radii")
    # partitions refine monotonically
    mono = True
    for r in range(2, 7):
        Br, Br1 = set(map(repr, boundaries(r))), set(map(repr, boundaries(r + 1)))
        if not Br.issubset(Br1):
            mono = False
    require(mono, "window partitions refine monotonically: boundaries(r) ⊆ boundaries(r+1)")

    # --- same-E_2 pairs; verify env-difference (chain) <=> cell-difference (partition) ---
    log("=" * 80)
    log("[1] for every same-E_2 pair: (env equal at r) <=> (same window cell at r), all r")
    r0 = 2
    idx = [i for i in range(N) if rmax(i) >= r0]
    pairs = []
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            i, j = idx[a], idx[b]
            if env(i, r0) == env(j, r0):
                pairs.append((i, j))
    equiv_ok = True; checked = 0
    for (i, j) in pairs:
        R = min(rmax(i), rmax(j))
        for r in range(r0, R + 1):
            same_env = env(i, r) == env(j, r)
            same_cell = cell(pts[i][1], r) == cell(pts[j][1], r)
            checked += 1
            if same_env != same_cell:
                equiv_ok = False
    require(equiv_ok, f"neighbourhood agreement <=> window-cell agreement at every radius "
                      f"({checked} (pair,r) checks over {len(pairs)} same-E_2 pairs)")

    # r* and separating boundary consistency
    rstar_ok = True
    for (i, j) in pairs:
        rs, thru, res = first_disagreement(i, j)
        if res:
            # at r*-1 same cell, at r* different cell, and a new boundary sits between
            if not (cell(pts[i][1], rs - 1) == cell(pts[j][1], rs - 1)
                    and cell(pts[i][1], rs) != cell(pts[j][1], rs)
                    and len(sep_boundary(i, j, rs)) >= 1):
                rstar_ok = False
    require(rstar_ok, "where resolved, r* is exactly the refinement level whose NEW window "
                      "boundary first falls between the two internal addresses")

    # --- three examples with progressively longer agreement ---
    log("=" * 80)
    log("[2] three examples: identical E_2, progressively longer agreement (increasing r*)")
    resolved = []
    unresolved = []
    for (i, j) in pairs:
        rs, thru, res = first_disagreement(i, j)
        dq = abs((pts[i][1] - pts[j][1]).real())
        dp = abs((pts[i][0] - pts[j][0]).real())
        (resolved if res else unresolved).append((rs, thru, dq, dp, i, j))
    # pick one pair at each of the smallest few distinct r* values
    by_r = {}
    for rec in resolved:
        by_r.setdefault(rec[0], rec)          # first (arbitrary) representative per r*
    chosen = [by_r[r] for r in sorted(by_r)][:3]
    for (rs, thru, dq, dp, i, j) in chosen:
        sb = sep_boundary(i, j, rs)
        log(f"  agree through r={thru}, first differ at r*={rs}: "
            f"E_{thru}(i)=E_{thru}(j); E_{rs}(i)={''.join(env(i,rs))} != "
            f"E_{rs}(j)={''.join(env(j,rs))}")
        log(f"       |Δq|={dq:.6f}  |Δp|={dp:.4f}  separating window boundary at "
            f"q={[round(b.real(),6) for b in sb]}  (new at partition level r={rs})")
    require(len(chosen) >= 3 and [c[0] for c in chosen] == sorted(c[0] for c in chosen)
            and len(set(c[0] for c in chosen)) == 3,
            "exhibited three pairs with strictly increasing first-disagreement radius r*")

    # --- honest truncation case ---
    log("=" * 80)
    log("[3] truncation-limited pairs: 'unresolved within the available patch' (not forever)")
    if unresolved:
        unresolved.sort(key=lambda t: (-t[1], t[2]))   # longest agreement, then closest
        rs, thru, dq, dp, i, j = unresolved[0]
        log(f"  closest-address unresolved pair: agrees through r={thru} (patch limit), "
            f"|Δq|={dq:.6f}, |Δp|={dp:.4f}")
        log(f"  -> UNRESOLVED WITHIN THE AVAILABLE PATCH; addresses are distinct (Δq>0), so a "
            f"longer chain WOULD separate them at some finite r. Not 'identical forever'.")
        require(dq > 0, "unresolved pair still has distinct internal addresses (would "
                        "separate in a larger patch)")
    else:
        log("  (no same-E_2 pair went unresolved within this patch; all separated by their "
            "truncation-limited radius)")
        require(True, "no unresolved pair in this patch (reported as-is)")

    log("=" * 80)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
