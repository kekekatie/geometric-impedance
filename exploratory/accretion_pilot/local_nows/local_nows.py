#!/usr/bin/env python3
"""
local_nows.py -- what happens when each part of the front chooses for itself? (PREREGISTRATION.md, frozen before this
file.) 24 fresh seeds, each grown with the GLOBAL patient scheduler and with a LOCAL scheduler (choices wherever a
neighbourhood of radius R has no forced edge, several per slice, spaced >= 2R). Every slice: is the patch dead (F empty)?
`python3 local_nows.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("speed_of_now", "slack"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import speed_of_now as SN
import classify_EXPLORATORY as CL
Sl, L, D, S = SN.Sl, SN.L, SN.D, SN.S
SEED0, N_ADD, N_WORLDS, MAX_SLICES, R = 20261210, 1500, 24, 400, 3.0
RES = os.path.join(HERE, "results")
mid = lambda e: (e[0] + e[1]) / 2


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[216:216 + N_WORLDS]


def dead(P, rank):
    cm = Sl.constraints(P.tris, rank)
    if Sl.area(Sl.region(cm)) > 0:
        return False
    return CL.classify(cm)[0] == "empty"


def run(args):
    k, mode = args
    rng = random.Random(SEED0 + k)
    P = L.Patch(L.seed_patch(centres()[k], 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris)
    status = "ok"; choices = []; died = None; per_slice_choices = []; s = 0
    while len(P.tris) - n0 < N_ADD and s < MAX_SLICES:
        s += 1
        fr = P.frontier(); forced = {}; opened = []; jam = None
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = e; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), (cs[0], e))
            else:
                opened.append(e)
        if jam is not None:
            status = "JAM"; break
        for t, e in forced.values():
            if P.legal(t):
                P.add(t)
        picks = []
        if mode == "GLOBAL":
            if not forced:
                picks = [fr[0]]
        else:
            fm = np.array([mid(e) for _, e in forced.values()]) if forced else np.zeros(0, complex)
            quiet = [e for e in opened if fm.size == 0 or np.min(np.abs(fm - mid(e))) > R * S]
            rng.shuffle(quiet)
            for e in quiet:
                if all(abs(mid(e) - mid(p)) >= 2 * R * S for p in picks):
                    picks.append(e)
        n_ch = 0
        for e in picks:
            ek = frozenset((L.key(e[0]), L.key(e[1])))
            if len(P.edges.get(ek, [])) != 1:
                continue                                    # filled by a forced tile this slice
            cs = SN.ordered(D.candidates(P, *e[:3]))
            if not cs:
                status = "JAM"; break
            t = rng.choice(cs) if len(cs) > 1 else cs[0]
            if P.legal(t):
                P.add(t)
                if len(cs) > 1:
                    n_ch += 1; choices.append(dict(slice=s, z=[mid(e).real / S, mid(e).imag / S]))
        if status == "JAM":
            break
        per_slice_choices.append(n_ch)
        if died is None and dead(P, rank):
            died = s
    jam_z = None
    if status == "JAM":
        jz = mid(jam) if jam is not None else None
        jam_z = None if jz is None else [jz.real / S, jz.imag / S]
    return dict(world=k, mode=mode, status=status, slices=s, tiles=len(P.tris) - n0, died=died, choices=choices,
                max_choices_per_slice=max(per_slice_choices) if per_slice_choices else 0, jam_z=jam_z,
                dead_at_end=dead(P, rank))


def main():
    os.makedirs(RES, exist_ok=True)
    jobs = [(k, m) for k in range(N_WORLDS) for m in ("GLOBAL", "LOCAL")]
    with Pool(4, maxtasksperchild=1) as p:
        out = p.map(run, jobs, chunksize=1)
    json.dump(out, open(os.path.join(RES, "worlds.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    G = {r["world"]: r for r in out if r["mode"] == "GLOBAL"}; Lw = {r["world"]: r for r in out if r["mode"] == "LOCAL"}
    bad = lambda r: r["status"] == "JAM" or r["dead_at_end"]
    nG, nL = sum(map(bad, G.values())), sum(map(bad, Lw.values()))
    lines = [f"GLOBAL: statuses {dict(collections.Counter(r['status'] for r in G.values()))}; dead at end {sum(r['dead_at_end'] for r in G.values())}; "
             f"jammed or dead {nG}/{N_WORLDS}",
             f"LOCAL:  statuses {dict(collections.Counter(r['status'] for r in Lw.values()))}; dead at end {sum(r['dead_at_end'] for r in Lw.values())}; "
             f"jammed or dead {nL}/{N_WORLDS}"]
    n1 = nL >= 6 and nL >= 3 * nG
    lines.append(f"  N1: {'HELD  ' if n1 else 'FAILED'}  LOCAL jammed or dead {nL} (need >= 6) vs GLOBAL {nG} (need LOCAL >= 3x GLOBAL)")
    jl = [r for r in Lw.values() if r["status"] == "JAM"]
    leads = [r["slices"] - r["died"] for r in jl if r["died"] is not None]
    n2 = bool(leads) and np.median(leads) >= 3
    lines.append(f"  N2: {'HELD  ' if n2 else 'FAILED'}  LOCAL jams with F already empty before the jam: {len(leads)}/{len(jl)}; lead (slices) median "
                 f"{np.median(leads) if leads else float('nan')}; leads {sorted(leads)}")
    for nm, D_ in (("GLOBAL", G), ("LOCAL", Lw)):
        lines.append(f"  reported {nm}: choices per world median {np.median([len(r['choices']) for r in D_.values()]):.0f}; slices median "
                     f"{np.median([r['slices'] for r in D_.values()]):.0f}; tiles median {np.median([r['tiles'] for r in D_.values()]):.0f}; "
                     f"max simultaneous choices {max(r['max_choices_per_slice'] for r in D_.values())}; died-at slices {sorted(r['died'] for r in D_.values() if r['died'] is not None)}")
    print("\n".join(lines))
    open(os.path.join(RES, "local_nows_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
