#!/usr/bin/env python3
"""
readout.py -- secondary readout on the ARCHIVE-FREE WORKER bands, reusing Astra's
precommitted geometry-defined 528-window bounded scan
(`audit_2026-11-03/SENSITIVITY_PROTOCOL.md`), applied identically at jam and final.

Selection is label-blind (positive compatibility area > 1e-9, then max tile count,
then the declared centre/width ordering); the historical B label is never a
tie-break. The frozen positive-area reader decision is kept SEPARATE from an
independent box-free closed-region A-feasibility check (zero area != symbolic
emptiness). Only the worker's retained band is used as reader evidence; historical
origin/rank/windows/A-B hypotheses are supplied to the evaluator.
"""
from __future__ import annotations
import json, math, collections
import numpy as np
from scipy.optimize import linprog
import af_common as AF
from af_common import RD, PC, L, D, S, dk
import isolated_worker as IW
import sys as _sys
_rd = str(AF.EB.EFP / "archive-free-reader")
if _rd not in _sys.path:
    _sys.path.insert(0, _rd)
import skin_reader as SR            # noqa: E402  frozen reader, direct read() for speed

CENTRES = [j * math.pi / 3 for j in range(6)]
HALFWIDTHS = [math.pi / 8, math.pi / 4, math.pi / 2, 3 * math.pi / 4]
ANG_TOL = 1e-12
AREA_POS = 1e-9


def centroid(tiles):
    zs = [z for t in tiles for z in t[1:]]
    return sum(zs) / len(zs)


def edge_components(tiles):
    by_edge = collections.defaultdict(list)
    tmap = {}
    for t in tiles:
        tmap[dk(t)] = t
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            by_edge[frozenset((L.key(p), L.key(q)))].append(dk(t))
    adj = collections.defaultdict(set)
    for ts in by_edge.values():
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                adj[ts[i]].add(ts[j]); adj[ts[j]].add(ts[i])
    seen = set(); comps = []
    for start in sorted(tmap):
        if start in seen:
            continue
        comp = set(); stack = [start]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u); comp.add(u); stack.extend(adj[u] - seen)
        comps.append([tmap[d] for d in comp])
    # largest first; ties by lexicographically smallest sorted key tuple
    comps.sort(key=lambda c: (-len(c), tuple(sorted(repr(dk(t)) for t in c))))
    return comps


def window(tiles, c, centre, hw):
    out = []
    for t in tiles:
        a = math.atan2((sum(t[1:]) / 3 - c).imag, (sum(t[1:]) / 3 - c).real)
        d = abs(((a - centre + math.pi) % (2 * math.pi)) - math.pi)
        if d <= hw + ANG_TOL:
            out.append(t)
    return out


def a_feasibility(raw, payload):
    """Box-free closed-region feasibility of the subset's F intersected with the A
    birth hypothesis (numerical, not symbolic). Returns status + axis spans."""
    cm = {(r, i): c for r, i, c in raw["constraints"]}
    for r, i, c in payload["hypotheses"][0]:            # hypothesis A
        cm[(r, i)] = max(cm.get((r, i), -math.inf), c)
    A = []; b = []
    for (r, i), c in sorted(cm.items()):
        nx, ny = payload["windows"][r]["normals"][i]; nrm = math.hypot(nx, ny)
        A.append([-nx / nrm, -ny / nrm]); b.append(-c / nrm)
    A = np.array(A); b = np.array(b)
    rr = linprog([0, 0], A_ub=A, b_ub=b, bounds=[(None, None)] * 2, method="highs",
                 options={"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9})
    spans = []
    if rr.status == 0:
        for obj in ([1, 0], [0, 1]):
            lo = linprog(obj, A_ub=A, b_ub=b, bounds=[(None, None)] * 2, method="highs")
            hi = linprog([-x for x in obj], A_ub=A, b_ub=b, bounds=[(None, None)] * 2, method="highs")
            spans.append(float(-hi.fun - lo.fun) if lo.status == hi.status == 0 else None)
    dim = ("segment" if spans and max(x for x in spans if x is not None) > 1e-7 else "point") \
        if rr.status == 0 else ("infeasible" if rr.status == 2 else "unresolved")
    return dict(status=int(rr.status), dimension=dim, spans=spans)


def score(Sstar, cs, tiles, bkey):
    if not tiles:
        return dict(outcome="empty", n=0)
    payload = RD.build_payload(Sstar, cs, tiles)
    raw = SR.read(payload)          # frozen reader, direct call (== isolated subprocess)
    outcome, detail = RD.classify(raw)
    present = any(dk(t) == bkey for t in tiles)
    rec = dict(n=len(tiles), outcome=outcome, selected=raw.get("selected"),
               F_area=raw.get("area"), intersections=raw.get("intersections"),
               choice_tile_in_subset=bool(present))
    if raw.get("status") == "reconstructed":
        rec["A_closed_feasibility"] = a_feasibility(raw, payload)
    return rec


def run():
    exports = json.loads((AF.INPUT / "worker_band_exports.json").read_text())
    out = []
    tally = collections.Counter()
    for (w, si) in AF.B_JAMS:
        jp = AF.jam_prep(w, si)
        Sstar, cs = jp["Sstar"], jp["cs"]; bkey = dk(cs[1])
        ex = exports[f"w{w}-s{si}"]
        jam_band = [IW.dtile(t) for t in ex["jam"]]
        final_band = [IW.dtile(t) for t in ex["final"]]
        # anchor direction: original jam dead-edge midpoint centroid vs jam band centroid
        jc = centroid(jam_band)
        dmid = sum((e[0] + e[1]) / 2 for e in jp["dead"]) / len(jp["dead"])
        anchor = math.atan2((dmid - jc).imag, (dmid - jc).real)
        for checkpoint, band in [("jam", jam_band), ("final", final_band)]:
            c = centroid(band)
            windows = []
            for j, base in enumerate(CENTRES):
                for hw in HALFWIDTHS:
                    centre = anchor + base
                    comp = edge_components(window(band, c, centre, hw))
                    sel = comp[0] if comp else []
                    sc = score(Sstar, cs, sel, bkey)
                    sc.update(centre_index=j, half_width=round(hw, 4), n_components=len(comp))
                    windows.append(sc)
                    tally[(checkpoint, sc["outcome"])] += 1
            # headline: positive area, then max tiles, then declared order
            cand = [x for x in windows if (x.get("F_area") or 0) > AREA_POS and x["outcome"] in ("correct", "wrong", "ambiguous")]
            cand.sort(key=lambda x: (-(x["n"]), x["centre_index"], x["half_width"]))
            headline = cand[0] if cand else None
            out.append(dict(case=f"w{w}-B-s{si}", checkpoint=checkpoint,
                            headline=headline, n_windows=len(windows), windows=windows))
            print(f"[readout] w{w}-s{si} {checkpoint}: headline "
                  f"{(headline['outcome']+' '+str(headline['n'])+'t') if headline else 'none'}", flush=True)
    AF.RESULTS.mkdir(parents=True, exist_ok=True)
    (AF.RESULTS / "readout.json").write_text(json.dumps(out, indent=2, default=float))
    print("\nscan tally (checkpoint, outcome):", dict(tally))
    print("wrote results/readout.json")


if __name__ == "__main__":
    run()
