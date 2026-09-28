#!/usr/bin/env python3
"""
gromit_check.py -- are our "dead surfaces" really dead? (PREREGISTRATION.md, frozen before this file.)
A vertex is COMPLETABLE if some legal Penrose vertex star (L.STARS) fits around it with every present corner exactly
in place. A candidate is STRONG if all three of its vertices stay completable. We replay the patient (h = inf) and the
jammed local-decider (h = 0.5, 1, 2) histories of ../local_deciders exactly, and check guess moments and guesses.
`python3 gromit_check.py` runs everything and writes results/gromit_check_report.txt.
"""
from __future__ import annotations
import os, sys, json, math, random
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "local_deciders"))
import local_deciders as LD
L, S = LD.L, LD.S
TOL = 1e-6
WIDTH = {}
for _k, _l in L.corners(L.REF).items():
    for _a, _d, _lab in _l:
        WIDTH[_lab] = _d
STARS = list(L.STARS)
RES = os.path.join(HERE, "results")


def _close(a, b):
    d = (a - b) % (2 * math.pi)
    return d < TOL or d > 2 * math.pi - TOL


def completable(lst):
    if not lst:
        return True
    if sum(d for _, d, _ in lst) > 2 * math.pi + TOL:
        return False
    lst = sorted(lst); a0, _, l0 = lst[0]
    for st in STARS:
        n = len(st)
        for i in range(n):
            if st[i] != l0:
                continue
            a = a0; matched = 0; ok = True
            for j in range(n):
                lab = st[(i + j) % n]; w = WIDTH[lab]
                here = [c for c in lst if _close(c[0], a)]
                if here:
                    if len(here) > 1 or here[0][2] != lab:
                        ok = False; break
                    matched += 1
                else:
                    # no present corner may start strictly inside this filler corner
                    for c in lst:
                        d = (c[0] - a) % (2 * math.pi)
                        if TOL < d < w - TOL:
                            ok = False; break
                    if not ok:
                        break
                a = (a + w) % (2 * math.pi)
            if ok and matched == len(lst):
                return True
    return False


def strong(P, t):
    return all(completable(P.V[k] + extra) for k, extra in L.corners([t]).items())


def replay(h, k):
    """Exact copy of local_deciders.grow(h, k) with instrumentation at guess moments and guesses."""
    rng = random.Random(LD.SEED0 + k)
    seed = L.seed_patch(0j, 3 * S)
    P = L.Patch(seed); n0 = len(P.tris)
    r = 0; status = "ok"; moments = []; guess_strong = []
    while len(P.tris) - n0 < LD.N_ADD:
        r += 1
        if r > LD.STALL:
            status = "STALL"; break
        fr = P.frontier(); forced = {}; multi = []
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                status = "JAM"; break
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), (cs[0], LD.mid(e)))
            else:
                multi.append(e)
        if status == "JAM":
            break
        legal = [(q, t) for q, (t, m) in forced.items() if P.legal(t)]
        if forced and not legal:
            status = "STUCK"; break
        for q, t in legal:
            if len(P.tris) - n0 >= LD.N_ADD:
                break
            if P.legal(t):
                P.add(t)
        if math.isinf(h) and not forced and multi:          # a guess moment of the patient scheduler
            n_strong = [sum(strong(P, t) for t in P.candidates(*e[:3])) for e in fr]
            moments.append(dict(round=r, edges=len(fr), strong_forced=sum(x == 1 for x in n_strong),
                                strong_dead=sum(x == 0 for x in n_strong), at_guess_edge=n_strong[0]))
        fmids = [m for _, m in forced.values()]; made = []
        for e in multi:
            if len(P.tris) - n0 >= LD.N_ADD:
                break
            m = LD.mid(e)
            if math.isinf(h):
                if forced or made:
                    break
            else:
                if any(abs(m - f) < h * S for f in fmids) or any(abs(m - g) < h * S for g in made):
                    continue
            ek = frozenset((L.key(e[0]), L.key(e[1])))
            if len(P.edges.get(ek, [])) != 1:
                continue
            cs = sorted(P.candidates(*e[:3]), key=lambda u: sorted(L.canon(u)[1]))
            if len(cs) < 2:
                continue
            t = rng.choice(cs)
            if not P.legal(t):
                continue
            guess_strong.append(dict(round=r, strong=strong(P, t), n_strong=sum(strong(P, u) for u in cs), n_cands=len(cs)))
            P.add(t); made.append(m)
    z2 = all(L.star(l) in L.STARS for l in P.V.values() if abs(sum(d for _, d, _ in l) - 2 * math.pi) < TOL) if math.isinf(h) else None
    return dict(h=None if math.isinf(h) else h, run=k, status=status, rounds=r, moments=moments, guesses=guess_strong, z2=z2)


def main():
    os.makedirs(RES, exist_ok=True)
    seed = L.seed_patch(0j, 3 * S); Ps = L.Patch(seed)
    z1 = all(completable(l) for l in Ps.V.values())
    tasks = [(math.inf, k) for k in range(8)] + [(h, k) for h in (0.5, 1, 2) for k in range(8)]
    with Pool(4, maxtasksperchild=1) as p:
        R = p.starmap(replay, tasks)
    with open(os.path.join(RES, "replays.jsonl"), "w") as f:
        for r in R:
            f.write(json.dumps(r) + "\n")
    orig = {(json.loads(l)["h"], json.loads(l)["run"]): json.loads(l) for l in open(os.path.join(LD.RES, "runs.jsonl"))}
    same = all(orig[(r["h"], r["run"])]["status"] == r["status"] and orig[(r["h"], r["run"])]["rounds"] == r["rounds"] for r in R)
    pat = [r for r in R if r["h"] is None]; jam = [r for r in R if r["h"] is not None]
    M = [m for r in pat for m in r["moments"]]
    f1_frac = sum(m["strong_forced"] > 0 for m in M) / len(M) if M else float("nan")
    doomed = [r for r in jam if r["status"] == "JAM" and any(not g["strong"] for g in r["guesses"])]
    pg = [g for r in pat for g in r["guesses"]]
    lines = [f"replays reproduce ../local_deciders exactly (status and rounds): {same}",
             f"  Z1: {'PASS' if z1 else 'FAIL'}  every seed-patch vertex is completable",
             f"  Z2: {'PASS' if all(r['z2'] for r in pat) else 'FAIL'}  every complete vertex star in the patient final patches is legal",
             f"  F1: {'HELD  ' if f1_frac >= 0.5 else 'FAILED'}  guess moments where some edge is strong-forced: "
             f"{sum(m['strong_forced'] > 0 for m in M)}/{len(M)} = {f1_frac:.2f} (need >= 0.5)",
             f"  F2: {'HELD  ' if len(doomed) >= 20 else 'FAILED'}  jammed local-decider runs with a non-strong guess before the jam: "
             f"{len(doomed)}/{sum(r['status'] == 'JAM' for r in jam)} (need >= 20 of 24)",
             f"  (reported) patient growth: guesses that were not strong {sum(not g['strong'] for g in pg)}/{len(pg)}; "
             f"guess moments with a strong-dead edge {sum(m['strong_dead'] > 0 for m in M)}/{len(M)}; "
             f"strong candidates at the guessed edge {[m['at_guess_edge'] for m in M]}",
             f"  (reported) guess moments detail: {[(m['round'], m['strong_forced'], m['strong_dead']) for m in M]}"]
    for h in (0.5, 1, 2):
        rs = [r for r in jam if r["h"] == h]
        lines.append(f"  (reported) h = {h}: non-strong guesses per run {[sum(not g['strong'] for g in r['guesses']) for r in rs]} "
                     f"of {[len(r['guesses']) for r in rs]} guesses")
    print("\n".join(lines))
    open(os.path.join(RES, "gromit_check_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
