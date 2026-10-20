#!/usr/bin/env python3
"""
carry_forward.py -- what if a world never jams? (PREREGISTRATION.md, frozen before this file.)
local_nows.py's schedulers on the same 24 seeds, except that an edge with no legal tile gets a LEAST-BAD tile: one that
fits geometrically and turns the fewest legal corners illegal. Defects (illegal vertices) are tracked every slice.
`python3 carry_forward.py` runs LOCAL (R = 3) and GLOBAL and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, random, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "local_nows"))
import local_nows as LN
SN, L, D, S = LN.SN, LN.L, LN.D, LN.S
N_ADD, MAX_SLICES, R = 1500, 300, 3.0
RES = os.path.join(HERE, "results")
mid = LN.mid


def geom_ok(P, k, extra):
    """vertex_ok without the label checks: angles fit, no overlapping corners."""
    lst = sorted(P.V[k] + extra); n = len(lst)
    tot = sum(d for _, d, _ in lst)
    if tot > 2 * math.pi + 1e-6:
        return False
    if abs(tot - 2 * math.pi) < 1e-6:
        return True
    wrap = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
    start = next((i for i in range(n) if abs(wrap(lst[i - 1][0] + lst[i - 1][1] - lst[i][0])) > 1e-6), None)
    if start is None:
        return False
    seq = lst[start:] + lst[:start]
    for i in range(1, n):
        pa, pd, _ = seq[i - 1]
        if wrap(seq[i][0] - (pa + pd)) < -1e-6:
            return False
    return True


def geom_legal(P, t):
    c = sum(t[1:]) / 3
    for u in P.tris:
        if abs(u[1] - c) < 3 * L.SCALE_LEN and (L.inside(c, *u[1:]) or any(L.inside(z, *u[1:]) for z in t[1:])):
            return False
    if L.canon(t) in {L.canon(u) for u in P.edges.get(frozenset((L.key(t[1]), L.key(t[2]))), [])}:
        return False
    return all(geom_ok(P, k, v) for k, v in L.corners([t]).items())


def relaxed(P, p, q, r):
    out = {}
    for (c, o), (tc, A, B, C) in L.TEMPL.items():
        Pp = {"A": A, "B": B, "C": C}
        for X, Y, Z in (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"), ("B", "A", "C"), ("C", "B", "A"), ("A", "C", "B")):
            x, y, z = Pp[X], Pp[Y], Pp[Z]
            if abs(abs(y - x) - abs(q - p)) > 1e-6:
                continue
            a = (q - p) / (y - x); zz = p + a * (z - x)
            if L.orient(p, q, zz) * L.orient(p, q, r) >= 0:
                continue
            img = {X: p, Y: q, Z: zz}; nt = (tc, img["A"], img["B"], img["C"])
            if geom_legal(P, nt):
                out[D.dkey(nt)] = nt
    return list(out.values())


def badness(P, t):
    return sum(1 for k, v in L.corners([t]).items() if P.vertex_ok(k, []) and not P.vertex_ok(k, v))


def defects(P):
    return [k for k in P.V if not P.vertex_ok(k, [])]


def run(args):
    k, mode = args
    rng = random.Random(LN.SEED0 + k)
    P = L.Patch(L.seed_patch(LN.centres()[k], 3 * S)); n0 = len(P.tris)
    status = "ok"; s = 0; n_bad = 0; n_choice = 0; trace = []
    while len(P.tris) - n0 < N_ADD and s < MAX_SLICES:
        s += 1
        fr = P.frontier(); forced = {}; opened = []; stuck = []
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                stuck.append(e)
            elif len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), (cs[0], e))
            else:
                opened.append(e)
        for t, e in forced.values():
            if P.legal(t):
                P.add(t)
        is_open = lambda e: len(P.edges.get(frozenset((L.key(e[0]), L.key(e[1]))), [])) == 1
        for e in stuck:                                     # carry on instead of jamming
            if not is_open(e):
                continue
            cs = D.candidates(P, *e[:3])
            if cs:
                if len(cs) == 1 and P.legal(cs[0]):
                    P.add(cs[0])
                continue
            rs = relaxed(P, *e[:3])
            if not rs:
                continue
            sc = [badness(P, t) for t in rs]; best = [t for t, b in zip(rs, sc) if b == min(sc)]
            P.add(rng.choice(SN.ordered(best))); n_bad += 1
        picks = []
        if mode == "GLOBAL":
            if not forced and not stuck and fr:
                picks = [fr[0]]
        else:
            fm = np.array([mid(e) for _, e in forced.values()]) if forced else np.zeros(0, complex)
            quiet = [e for e in opened if fm.size == 0 or np.min(np.abs(fm - mid(e))) > R * S]
            rng.shuffle(quiet)
            for e in quiet:
                if all(abs(mid(e) - mid(p)) >= 2 * R * S for p in picks):
                    picks.append(e)
        for e in picks:
            if not is_open(e):
                continue
            cs = SN.ordered(D.candidates(P, *e[:3]))
            if len(cs) >= 2:
                t = rng.choice(cs)
                if P.legal(t):
                    P.add(t); n_choice += 1
        dk = defects(P)
        fverts = {L.key(z) for e in P.frontier() for z in e[:2]}
        trace.append((s, len(P.tris) - n0, len(dk), sum(1 for v in dk if v in fverts)))
        if trace[-1][1] == (trace[-2][1] if len(trace) > 1 else -1):
            status = "STALLED"; break
    dk = defects(P)
    pts = np.array([complex(*v) for v in dk]) / S
    elong = None
    if len(pts) >= 10:
        X = np.c_[pts.real - pts.real.mean(), pts.imag - pts.imag.mean()]
        w, _ = np.linalg.eigh(X.T @ X / len(pts)); elong = float(math.sqrt(w[-1] / max(w[0], 1e-12)))
    fverts = {L.key(z) for e in P.frontier() for z in e[:2]}
    return dict(world=k, mode=mode, status=status, slices=s, tiles=len(P.tris) - n0, least_bad=n_bad, choices=n_choice,
                defects=len(dk), frontier_defects=sum(1 for v in dk if v in fverts), elongation=elong, trace=trace,
                defect_pts=[[p.real, p.imag] for p in pts])


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        out = p.map(run, [(k, m) for m in ("LOCAL", "GLOBAL") for k in range(LN.N_WORLDS)], chunksize=1)
    json.dump(out, open(os.path.join(RES, "worlds.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    lines = []
    for mode in ("LOCAL", "GLOBAL"):
        W = [r for r in out if r["mode"] == mode]
        used = [r for r in W if r["least_bad"] > 0]
        reached = sum(r["tiles"] >= N_ADD for r in W)
        carried = sum(r["frontier_defects"] > 0 for r in used)
        el = [r["elongation"] for r in W if r["elongation"] is not None]
        lines.append(f"{mode}: statuses {dict(collections.Counter(r['status'] for r in W))}; reached {N_ADD} tiles {reached}/{len(W)}; "
                     f"used least-bad {len(used)}/{len(W)}")
        if mode == "LOCAL":
            lines.append(f"  M1: {'HELD  ' if reached >= 20 else 'FAILED'}  reached {N_ADD} added tiles in {reached}/24 (need >= 20)")
            lines.append(f"  M2: {'HELD  ' if used and carried >= 0.5 * len(used) else 'FAILED'}  defects still on the frontier at the end in {carried}/{len(used)} "
                         f"(need >= 50%)")
            lines.append(f"  M3: {'HELD  ' if el and sum(e >= 3 for e in el) >= 0.5 * len(el) else 'FAILED'}  elongation >= 3 in {sum(e >= 3 for e in el)}/{len(el)} "
                         f"worlds with >= 10 defects (need >= 50%); elongations {sorted(round(e, 1) for e in el)}")
        lines.append(f"  reported {mode}: least-bad per world median {np.median([r['least_bad'] for r in W]):.0f} (share of tiles median "
                     f"{np.median([r['least_bad'] / max(r['tiles'], 1) for r in W]):.3f}); defects median {np.median([r['defects'] for r in W]):.0f}; "
                     f"frontier defects at end median {np.median([r['frontier_defects'] for r in W]):.0f}; choices median {np.median([r['choices'] for r in W]):.0f}")
        thirds = []
        for r in used:
            tr = r["trace"]
            if len(tr) >= 30:
                a, b, c = (tr[len(tr) // 3][3], tr[2 * len(tr) // 3][3], tr[-1][3])
                thirds.append((a, b, c))
        if thirds:
            lines.append(f"  reported {mode}: frontier defects at 1/3, 2/3, end of the run (median) "
                         f"{np.median([t[0] for t in thirds]):.0f}, {np.median([t[1] for t in thirds]):.0f}, {np.median([t[2] for t in thirds]):.0f}")
    print("\n".join(lines))
    open(os.path.join(RES, "carry_forward_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
