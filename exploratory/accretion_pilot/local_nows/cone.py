#!/usr/bin/env python3
"""
cone.py -- causally honest local nows (PREREGISTRATION_cone.md, frozen before this file).
local_nows.py's LOCAL scheduler, but a frontier edge may choose only if its PAST LIGHT CONE over the last H slices holds
no forced placement: no forced tile within c*k + r0 edges of it in slice s-k, k = 0..H. Same 24 seeds; H = 12, 24, 48.
`python3 cone.py` writes results/cone_report.txt and results/cone_worlds.json.
"""
from __future__ import annotations
import os, json, random, collections
from multiprocessing import Pool
import numpy as np
import local_nows as LN
SN, Sl, L, D, S = LN.SN, LN.Sl, LN.L, LN.D, LN.S
C, R0, SPACING, HS = 1.05, 1.0, 6.0, (12, 24, 48)
mid = LN.mid


def run(args):
    k, H = args
    rng = random.Random(LN.SEED0 + k)
    P = L.Patch(L.seed_patch(LN.centres()[k], 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris)
    status = "ok"; choices = []; died = None; died_choices = None; s = 0; hist = []       # hist[i] = forced positions in slice i+1
    while len(P.tris) - n0 < LN.N_ADD and s < LN.MAX_SLICES:
        s += 1
        fr = P.frontier(); forced = {}; opened = []; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), (cs[0], e))
            else:
                opened.append(e)
        if jam:
            status = "JAM"; break
        here = []
        for t, e in forced.values():
            if P.legal(t):
                P.add(t); here.append(sum(t[1:]) / 3)
        hist.append(np.array(here, complex))
        def quiet(e):
            z = mid(e)
            for kk in range(0, min(H, len(hist) - 1) + 1):
                pts = hist[-1 - kk]
                if pts.size and np.min(np.abs(pts - z)) <= (C * kk + R0) * S:
                    return False
            return True
        cand = [e for e in opened if quiet(e)]
        rng.shuffle(cand); picks = []
        for e in cand:
            if all(abs(mid(e) - mid(p)) >= SPACING * S for p in picks):
                picks.append(e)
        # no global fallback: if nothing is quiet, regions simply wait; old activity leaves the cone after H slices
        n_ch = 0
        for e in picks:
            ek = frozenset((L.key(e[0]), L.key(e[1])))
            if len(P.edges.get(ek, [])) != 1:
                continue
            cs = SN.ordered(D.candidates(P, *e[:3]))
            if not cs:
                status = "JAM"; break
            t = rng.choice(cs) if len(cs) > 1 else cs[0]
            if P.legal(t):
                P.add(t)
                if len(cs) > 1:
                    n_ch += 1; choices.append(s)
        if status == "JAM":
            break
        if died is None and LN.dead(P, rank):
            died = s; died_choices = n_ch
    return dict(world=k, H=H, status=status, slices=s, tiles=len(P.tris) - n0, died=died, died_choices=died_choices,
                choices=len(choices), dead_at_end=LN.dead(P, rank))


def main():
    with Pool(4, maxtasksperchild=1) as p:
        out = p.map(run, [(k, H) for H in HS for k in range(LN.N_WORLDS)], chunksize=1)
    json.dump(out, open(os.path.join(LN.RES, "cone_worlds.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    bad = lambda r: r["status"] == "JAM" or r["dead_at_end"]
    counts = {H: sum(bad(r) for r in out if r["H"] == H) for H in HS}
    lines = [f"bad worlds (jammed or dead) out of {LN.N_WORLDS}: " + ", ".join(f"CONE(H={H}): {counts[H]}" for H in HS) +
             "   [for reference: R=24 (faster-than-light radius) 4, GLOBAL 2, R=3 24]"]
    seq = [counts[H] for H in HS]
    lines.append(f"  K1: {'HELD  ' if all(b <= a for a, b in zip(seq, seq[1:])) else 'FAILED'}  non-increasing in H: {seq}")
    lines.append(f"  K2: {'HELD  ' if counts[48] >= 8 else 'FAILED'}  CONE(48) bad {counts[48]}/24 (need >= 8, i.e. clearly worse than R=24's 4)")
    for H in HS:
        W = [r for r in out if r["H"] == H]
        leads = [r["slices"] - r["died"] for r in W if r["status"] == "JAM" and r["died"] is not None]
        lines.append(f"  reported H={H}: statuses {dict(collections.Counter(r['status'] for r in W))}; dead at end {sum(r['dead_at_end'] for r in W)}; "
                     f"slices median {np.median([r['slices'] for r in W]):.0f}; tiles median {np.median([r['tiles'] for r in W]):.0f}; "
                     f"choices median {np.median([r['choices'] for r in W]):.0f}; death-to-jam lead median {np.median(leads) if leads else float('nan')}; "
                     f"choices made in the slice of death {dict(collections.Counter(r['died_choices'] for r in W if r['died'] is not None))}")
    print("\n".join(lines))
    open(os.path.join(LN.RES, "cone_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
