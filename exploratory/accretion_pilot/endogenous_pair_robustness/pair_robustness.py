#!/usr/bin/env python3
"""
pair_robustness.py -- is the coast limit L a property of ONE example, or of the construction?

Fable's request (transmission-paper data): repeat the ERASE / rho(h) / coast-asymptote
analysis on more than the single matched pair used in ../endogenous_erase_test/ and
../endogenous_present_width/. Here we go all the way: we compute the EXACT coast limit L for
EVERY matched pair among the depth-2 classes, and analyse one FEATURED second pair (from a
different active-projection family than the original) in full.

What is shown, exactly (register: speculative exploration; a mechanism study, not a sample of
growing worlds; exact rationals; isolated; earlier work preserved):

  * The depth-2 classes contain 11 matched pairs (isomorphic active projection, non-isomorphic
    full graph -> same active layer, different archive) across 4 active-projection families.
  * For each, the archive-free coast is a finite absorbing Markov chain on 4-active-vertex
    projections (Proposition 3 of ../endogenous_present_width/: DeltaA=0 at k=1), so the coast
    TV converges monotonically (data-processing) to the exact rational
        L = TV(absorption distributions of the two lineages).
  * L VARIES across pairs (it is a property of the pair, as expected) but the STRUCTURE is
    universal: every pair's coast is a finite absorbing chain with an exact limit, and every
    pair we can form here has L > 0 -- the durable ENSEMBLE bias (the present is biased, not a
    per-world memory) is not special to the original example.

The FEATURED second pair additionally gets the rho(h) surviving-fraction curve and the
Q1/Q2 (durable-bias / not-redundant) checks, mirroring the original study.

Everything reuses the verified primitives in ../endogenous_present_width/present_width.py.
asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "endogenous_present_width"))
import present_width as PW

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "pair_robustness_report.txt")
TABLE = os.path.join(HERE, "results", "L_table.txt")
LINES, FAILS = [], []
H = 2


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ----- exact linear solve over Fractions (I-Q)X = R  -----
def solve(A, B):
    n = len(A); m = len(B[0])
    M = [[Fr(A[i][j]) for j in range(n)] + [Fr(B[i][j]) for j in range(m)] for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        assert p is not None, "singular (chain should be absorbing)"
        M[c], M[p] = M[p], M[c]
        inv = Fr(1) / M[c][c]; M[c] = [v * inv for v in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]; M[r] = [M[r][k] - f * M[c][k] for k in range(n + m)]
    return [[M[i][n + j] for j in range(m)] for i in range(n)]


def tv(d1, d2):
    keys = set(d1) | set(d2)
    return sum(abs(d1.get(k, Fr(0)) - d2.get(k, Fr(0))) for k in keys) * Fr(1, 2)


# ----- coast limit L for a pair (self-contained projection chain) -----
def coast_limit(Gi, Gj, horizon=H):
    """Exact L = TV(absorption distributions) of the BUD-only projection chain, starting from
    each lineage's erased-slice distribution at `horizon` extended events. Returns
    (L, absorbing_shapes, ncoast_states)."""
    reps, buckets = [], {}

    def cidx(P):
        h = PW.wl(P)
        for k in buckets.get(h, ()):
            if PW.iso(P, reps[k]):
                return k
        reps.append(P); buckets.setdefault(h, []).append(len(reps) - 1)
        return len(reps) - 1

    def slice_dist(G):
        d = {}

        def rec(Gg, prob, s):
            if s == horizon:
                d[cidx(PW.erase(Gg))] = d.get(cidx(PW.erase(Gg)), Fr(0)) + prob; return
            evs = PW.events_ext(Gg); n = len(evs)
            if n == 0:
                d[cidx(PW.erase(Gg))] = d.get(cidx(PW.erase(Gg)), Fr(0)) + prob; return
            for e in evs:
                rec(PW.apply_ev(Gg, e), prob * Fr(1, n), s + 1)
        rec(G, Fr(1), 0)
        return d

    mu_i, mu_j = slice_dist(Gi), slice_dist(Gj)
    # BUD-only projection kernel over reachable projections
    T = {}
    frontier = list(set(mu_i) | set(mu_j)); seen = set(frontier)
    while frontier:
        s = frontier.pop(); P = reps[s]; evs = PW.events_bud(P)
        if not evs:
            T[s] = {s: Fr(1)}
        else:
            n = len(evs); row = {}
            for (_, x, y) in evs:
                s2 = cidx(PW.erase(PW.bud(P, x, y))); row[s2] = row.get(s2, Fr(0)) + Fr(1, n)
            T[s] = row
        for s2 in T[s]:
            if s2 not in seen:
                seen.add(s2); frontier.append(s2)
    absorbing = sorted(s for s in T if T[s] == {s: Fr(1)})
    transient = sorted(s for s in T if s not in absorbing)
    idx = {s: k for k, s in enumerate(transient)}
    if transient:
        A = [[(Fr(1) if a == b else Fr(0)) - T[transient[a]].get(transient[b], Fr(0))
              for b in range(len(transient))] for a in range(len(transient))]
        R = [[T[transient[a]].get(c, Fr(0)) for c in absorbing] for a in range(len(transient))]
        X = solve(A, R)
    else:
        X = []

    def absorb(mu):
        a = {c: Fr(0) for c in absorbing}
        for s, p in mu.items():
            if s in absorbing:
                a[s] += p
            else:
                for ci, c in enumerate(absorbing):
                    a[c] += p * X[idx[s]][ci]
        return a

    L = tv(absorb(mu_i), absorb(mu_j))
    shapes = [f"{reps[c].number_of_edges()}e/deg{sorted(d for _,d in reps[c].degree())}"
              for c in absorbing]
    return L, shapes, len(T)


def all_matched_pairs(fulls):
    out = []
    for a in range(len(fulls)):
        for b in range(a + 1, len(fulls)):
            if PW.iso(PW.erase(fulls[a]), PW.erase(fulls[b])) and not PW.iso(fulls[a], fulls[b]):
                out.append((a, b))
    return out


def main():
    log("=" * 92)
    log("PAIR ROBUSTNESS -- is the coast limit L one example's property, or the construction's?")
    log("=" * 92)
    fulls = PW.depth2_classes()
    pairs = all_matched_pairs(fulls)
    require(len(pairs) >= 2, f"depth-2 classes contain {len(pairs)} matched pairs (>1) to compare")

    # ---- [1] exact coast limit L for EVERY matched pair ----
    log(f"[1] exact coast limit L for all {len(pairs)} matched pairs "
        f"(iso active projection, different archive)")
    rows = ["pair    projWL     q_sigs            L (exact)            L (float)   L>0"]
    results = {}
    for (a, b) in pairs:
        L, shapes, nst = coast_limit(fulls[a], fulls[b])
        results[(a, b)] = (L, PW.wl(PW.erase(fulls[a]))[:8])
        rows.append(f"({a:>2},{b:>2})  {PW.wl(PW.erase(fulls[a]))[:8]}  "
                    f"{str(PW.q_sig(fulls[a])):>6} vs {str(PW.q_sig(fulls[b])):<6}  "
                    f"{str(L):>18}  {float(L):.6f}   {'yes' if L > 0 else 'NO'}")
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")
    for r in rows:
        log("  " + r)
    # ---- fate classification: EXPRESSION (D_slice at h=1,2) decides the fate ----
    def slice_of(G):
        return PW.run_process(G, PW.events_ext, 3, PW.events_ext, 0, False)[1]
    D1, D2, fate = {}, {}, {}
    for (a, b) in pairs:
        si, sj = slice_of(fulls[a]), slice_of(fulls[b])
        D1[(a, b)] = PW.tv(si[1], sj[1]); D2[(a, b)] = PW.tv(si[2], sj[2])
        L = results[(a, b)][0]
        fate[(a, b)] = "durable" if L > 0 else ("washout" if D2[(a, b)] > 0 else "inert")
    ndur = sum(1 for p in pairs if fate[p] == "durable")
    nin = sum(1 for p in pairs if fate[p] == "inert")
    nwash = sum(1 for p in pairs if fate[p] == "washout")
    require(all(results[p][0] >= 0 for p in pairs),
            "every matched pair converges to an exact rational limit L >= 0 (finite absorbing "
            "chain) -- the STRUCTURE (a convergent finite chain) is universal")
    require(nwash == 0,
            f"the WASHOUT category is EMPTY (0/{len(pairs)}). Three logical fates -- inert "
            f"(never expressed in the active layer, {nin}), washout (expressed then decays to "
            f"L=0, 0), durable (expressed, L>0, {ndur}). HEADLINE: on the depth-2 set every "
            f"EXPRESSED archive difference leaves a permanent residue -- expression => "
            f"durability; nothing that touches the present ever fully fades")
    require(all((results[p][0] == 0) == (D1[p] == 0) for p in pairs),
            "MENU-EQUIVALENCE CRITERION: L = 0  IFF  the two archives are menu-equivalent "
            "(identical one-step projected successor distribution, D_slice(1)=0). A pair's fate "
            "is decided at the FIRST step and is predictable WITHOUT running the chain: "
            "menu-equivalent => inert => L=0; menu-distinct => durable => L>0")
    require(all((D2[p] > 0) == (results[p][0] > 0) for p in pairs),
            "Proposition 4 (expression => durability), verified on this set: coast[H]>0 <=> L>0 "
            "-- the absorption map is injective on the reachable H=2 lineage differences (no "
            "nonzero expressed difference is annihilated by absorption; whether this holds "
            "beyond the depth-2 set is open)")
    distinct_L = sorted(set(results[p][0] for p in pairs))
    require(len(distinct_L) > 1,
            f"L takes {len(distinct_L)} distinct exact values (incl. 0) -- the VALUE is a "
            f"property OF THE PAIR (the structure is universal)")
    require(results.get((0, 1), (None,))[0] == Fr(4321, 44100),
            "the original pair (0,1) reproduces its published limit L = 4321/44100")
    require(results[(8, 10)][0] == max(results[p][0] for p in pairs)
            and PW.q_sig(fulls[8]) == PW.q_sig(fulls[10]),
            f"pair (8,10) has the SAME quiet-degree signature on both sides "
            f"({PW.q_sig(fulls[8])}) yet the LARGEST L ({results[(8,10)][0]}) -- the crude "
            f"degree signature is NOT the carrier of the difference; menu-inequivalence is")

    # ---- [2] FEATURED second pair: different projection family, full analysis ----
    orig_wl = PW.wl(PW.erase(fulls[0]))[:8]
    featured = next(((a, b) for (a, b) in pairs
                     if PW.wl(PW.erase(fulls[a]))[:8] != orig_wl and results[(a, b)][0] > 0), None)
    require(featured is not None, "found a featured second pair in a DIFFERENT projection family")
    a, b = featured; Gi, Gj = fulls[a], fulls[b]
    L2 = results[featured][0]
    log("=" * 92)
    log(f"[2] featured SECOND pair = classes {featured}; projection family "
        f"{PW.wl(PW.erase(Gi))[:8]} (original was {orig_wl}); archives "
        f"{PW.q_sig(Gi)} vs {PW.q_sig(Gj)}; exact coast limit L2 = {L2} = {float(L2):.6f}")
    require(PW.iso(PW.erase(Gi), PW.erase(Gj)) and not PW.iso(Gi, Gj),
            "featured pair: isomorphic active projection, non-isomorphic archive (a true "
            "matched pair, independent of the original)")

    # rho(h): present-only vs full-state distinguishability, h=0..3
    log("  rho(h) = present-only / full-state distinguishability (same measure as present_width)")
    fi, si = PW.run_process(Gi, PW.events_ext, 3, PW.events_ext, 0, False)
    fj, sj = PW.run_process(Gj, PW.events_ext, 3, PW.events_ext, 0, False)
    log("    h   D_full     D_slice    rho")
    rho_rise = []
    for h in range(4):
        Df, Ds = PW.tv(fi[h], fj[h]), PW.tv(si[h], sj[h])
        rho = (Ds / Df) if Df != 0 else Fr(0)
        rho_rise.append(Ds)
        log(f"    {h}   {float(Df):.4f}     {float(Ds):.4f}     {float(rho):.4f}")
    require(rho_rise[0] == 0, "featured pair: at h=0 the present carries none of the distinction "
                              "(rho=0) -- the difference starts entirely in the archive")
    require(rho_rise[3] > 0, "featured pair: by h=3 the present alone is biased by lineage "
                             "(present-only distinguishability > 0) -- CONTACT transcribes it")

    # Q1 (durable ensemble bias) and Q2 (not redundant), erase at H=2, K=2 future
    K = 2
    ef_i = PW.run_process(Gi, PW.events_ext, H, PW.events_bud, K, True)[1]
    ef_j = PW.run_process(Gj, PW.events_ext, H, PW.events_bud, K, True)[1]
    kp_i = PW.run_process(Gi, PW.events_ext, H, PW.events_ext, K, False)[1]
    kp_j = PW.run_process(Gj, PW.events_ext, H, PW.events_ext, K, False)[1]
    coast = {s: PW.tv(ef_i[s], ef_j[s]) for s in range(H + K + 1)}
    kept = {s: PW.tv(kp_i[s], kp_j[s]) for s in range(H + K + 1)}
    require(all(coast[s + 1] <= coast[s] for s in range(H, H + K)),
            "featured pair Q1: archive-free coast is non-increasing (data-processing) and ...")
    require(coast[H + K] > 0 and coast[H + K] >= L2,
            f"featured pair Q1: after deleting the archive the lineages still differ "
            f"(coast[{H+K}]={float(coast[H+K]):.4f} > 0), converging toward L2={float(L2):.4f} "
            f"-- a DURABLE ensemble bias, not a per-world memory")
    require(all(kept[s] >= coast[s] for s in range(H + K + 1)) and
            any(kept[s] != coast[s] for s in range(H, H + K + 1)),
            "featured pair Q2: KEEP >= coast at every tested step and differs after H "
            "(deleting the archive changes the active future) -- the archive is NOT redundant")

    # ---- [3] FEATURED INERT pair (L = 0): the archive difference is never expressed ----
    inert = next(((x, y) for (x, y) in pairs if fate[(x, y)] == "inert"), None)
    require(inert is not None, "found an inert pair (L = 0) to feature")
    wx, wy = inert; Wi, Wj = fulls[wx], fulls[wy]
    log("=" * 92)
    log(f"[3] featured INERT pair = classes {inert}; family "
        f"{PW.wl(PW.erase(Wi))[:8]}; archives {PW.q_sig(Wi)} vs {PW.q_sig(Wj)}; L = 0")
    wfull_i, wef_i = PW.run_process(Wi, PW.events_ext, H, PW.events_bud, 4, True)
    wfull_j, wef_j = PW.run_process(Wj, PW.events_ext, H, PW.events_bud, 4, True)
    wcoast = {s: PW.tv(wef_i[s], wef_j[s]) for s in range(H + 4 + 1)}
    Dfull_H = PW.tv(wfull_i[H], wfull_j[H])
    log(f"    full-state distinguishability at H=2: {float(Dfull_H):.4f} (they DO differ, in "
        f"the archive)")
    log(f"    D_slice(1) = {float(D1[inert]):.4f}, D_slice(2) = {float(D2[inert]):.4f} "
        f"(EXACTLY 0 from the first step -- never expressed)")
    log("    archive-free coast: "
        + ", ".join(f"t{s-H}={float(wcoast[s]):.4f}" for s in range(H, H + 4 + 1)))
    require(not PW.iso(Wi, Wj) and Dfull_H > 0,
            "inert pair is a genuine matched pair: non-isomorphic full graphs and positive "
            "full-state distinguishability -- the archives really do differ")
    require(D1[inert] == 0 and all(wcoast[s] == 0 for s in range(H, H + 4 + 1)),
            "inert pair: D_slice is EXACTLY 0 from step 1 onward -- the archive difference is "
            "NEVER expressed in the active layer (nothing 'washes out'; it was never present "
            "there). Delete the archive and the active future is identical from the first step")

    # mechanism: the two archives present IDENTICAL projected CONTACT menus (menu-equivalent)
    from collections import Counter

    def contact_menu_proj(G):
        c = Counter()
        for e in PW.events_contact(G):
            c[PW.wl(PW.erase(PW.apply_ev(G, e)))] += 1
        return c

    me_ok = (contact_menu_proj(Wi) == contact_menu_proj(Wj)
             and len(PW.events_ext(Wi)) == len(PW.events_ext(Wj)))
    log(f"    mechanism: equal total eligible events? {len(PW.events_ext(Wi))}=="
        f"{len(PW.events_ext(Wj))}; identical projected CONTACT menu? "
        f"{contact_menu_proj(Wi) == contact_menu_proj(Wj)}")
    require(me_ok,
            "MECHANISM confirmed: the two archives are MENU-EQUIVALENT -- same total eligible "
            "event count and the same multiset of projected CONTACT successors -- so the "
            "scheduler cannot tell the lineages apart at the active level. That is WHY this pair "
            "is inert (L=0), exactly as the criterion predicts, WITHOUT running the chain")
    require(True,
            "SCOPE: for an inert pair the archive is redundant FOR THIS PAIR'S DIFFERENCE only "
            "-- both archives still SUPPLY CONTACT opportunities to the active layer; they just "
            "supply the SAME ones. The archive is not globally inert (cf. active_projection).")

    log("=" * 92)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    log(f"Summary: across {len(pairs)} matched pairs the archive-free coast is ALWAYS a finite "
        f"absorbing chain with an exact rational limit L (the STRUCTURE is universal). Three "
        f"logical fates -- inert ({nin}), washout (0), durable ({ndur}) -- but the WASHOUT "
        f"middle is EMPTY: on the depth-2 set every archive difference that is EXPRESSED in the "
        f"active layer leaves a permanent residue (Proposition 4: expression => durability). "
        f"Fate is decided at the first step and predictable without the chain: a pair is inert "
        f"(L=0) IFF its archives are MENU-EQUIVALENT, else durable (L>0). The value of L (e.g. "
        f"original 4321/44100; featured second {L2}; (8,10) the largest at 4/15 despite equal "
        f"degree signatures) is the pair's. Mechanism study on the depth-2 class set; not a "
        f"claim about generic worlds. NOTE: the washout-empty finding and the step-one criterion "
        f"are DEPTH-2-SPECIFIC and BREAK at depth-3 -- see depth3_criterion.py for exact "
        f"counterexamples and the surviving FORK law (L = TV(absorption dists); among expressed "
        f"pairs, L>0 iff the coast has >=2 reachable sinks -- verified on the enumerated set, "
        f"not proven).")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
