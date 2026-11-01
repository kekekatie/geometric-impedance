#!/usr/bin/env python3
"""
part4_iis.py -- extract an inclusion-minimal infeasible subset (IIS) of the
compatibility constraints and map it back to tiles / vertices / window edges.

The compatibility system is <=20 half-planes (4 layer ranks x 5 window edges),
each the tightest over the vertices in that rank. For an infeasible state we:
  * record, per constraint (rk,i), the originating vertex (the argmax) and the
    tiles that contain it (provenance; ties retained);
  * find an IIS by the deletion filter (drop a constraint; keep it dropped if the
    remainder stays infeasible). Inclusion-minimal, NOT minimum-cardinality.
  * find alternative IIS witnesses by re-running under different drop orders
    (non-uniqueness is expected and reported).

States examined for world 7 (replication: world 5): the first-infeasible full
patch (Part 3) and the jam-trigger skin. Outputs ../results/part4_iis.json and
a provenance dump used by part4_figures.py.
"""
from __future__ import annotations
import json
from pathlib import Path
import study_common as SC
from study_common import Sl, PC, L, M, WIN
import feas

OUT = Path(__file__).resolve().parent.parent / "results"


def constraints_with_origin(tiles, rank):
    """Replicates slack.constraints but records the argmax vertex per (rk,i)."""
    K, pos, conf = M.lift(tiles)
    cmax = {}
    origin = {}
    for v, k in K.items():
        rk = rank[int(k.sum())]
        z = M.perp(k)
        n, h = WIN[rk]
        for i, (nx, ny) in enumerate(n):
            c = nx * z.real + ny * z.imag - float(h)
            if c > cmax.get((rk, i), -1e18) + 1e-15:
                cmax[(rk, i)] = c
                origin[(rk, i)] = dict(vkey=list(v), layer=int(k.sum()), rank=int(rk),
                                       k=[int(x) for x in k], perp=[z.real, z.imag])
    return cmax, origin, pos, conf


def iis_deletion(cmax, order=None):
    """Inclusion-minimal infeasible subset via deletion filter."""
    assert feas.classify(cmax)["cls"] == "infeasible", "state is not infeasible"
    keys = list(cmax.keys()) if order is None else list(order)
    keep = dict(cmax)
    for key in keys:
        if key not in keep:
            continue
        trial = {k: v for k, v in keep.items() if k != key}
        if trial and feas.classify(trial)["cls"] == "infeasible":
            keep = trial   # key is not needed for infeasibility -> drop it
    return sorted(keep.keys())


def tiles_at_vertex(tiles, vkey):
    tv = tuple(vkey)
    out = []
    for t in tiles:
        if any(list(L.key(z)) == list(tv) for z in t[1:]):
            out.append(dict(shape=int(t[0]),
                            centroid=[(sum(t[1:]) / 3).real, (sum(t[1:]) / 3).imag]))
    return out


def analyse(tiles, label):
    rank = Sl.rank_of(tiles)
    cmax, origin, pos, conf = constraints_with_origin(tiles, rank)
    cls = feas.classify(cmax)
    rec = dict(label=label, n_tiles=len(tiles), n_constraints=len(cmax),
               feasibility=cls["cls"], chebyshev_r=cls["r"], lift_conflicts=len(conf))
    if cls["cls"] != "infeasible":
        rec["note"] = "not infeasible; no IIS extracted"
        return rec, None
    # primary IIS + two alternative drop orders
    iis0 = iis_deletion(cmax)
    import random
    alt = []
    for seed in (1, 2, 3):
        order = list(cmax.keys()); random.Random(seed).shuffle(order)
        alt.append(iis_deletion(cmax, order))
    uniq_iis = sorted({tuple(x) for x in [iis0] + alt})
    rec["iis_primary"] = [list(k) for k in iis0]
    rec["iis_size"] = len(iis0)
    rec["iis_alternatives"] = [[list(k) for k in a] for a in uniq_iis]
    rec["iis_is_unique"] = (len(uniq_iis) == 1)
    # provenance for the primary IIS
    prov = []
    for key in iis0:
        o = origin[key]
        prov.append(dict(constraint=list(key), window_rank=key[0], window_edge=key[1],
                         origin_vertex=o["vkey"], origin_layer=o["layer"],
                         origin_perp=o["perp"],
                         tiles_at_origin=tiles_at_vertex(tiles, o["vkey"])))
    rec["iis_provenance"] = prov
    # distinct originating vertices
    vset = {tuple(p["origin_vertex"]) for p in prov}
    rec["n_distinct_origin_vertices"] = len(vset)
    rec["origin_vertices"] = [list(v) for v in sorted(vset)]
    return rec, dict(cmax=cmax, origin=origin, iis=iis0, prov=prov)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    forks = SC.P3.load_forks()
    results = []
    provdump = {}
    for (w, si, js, first_inf) in [(7, 0, 23, 9), (5, 0, 42, 17)]:
        B = forks[w]["cs"][1]; stream = PC.streams_for(w)[si]
        arm = PC.grow(forks[w]["Sstar"], B, stream, 44)
        snaps = arm["snaps"]
        # state A: first-infeasible full patch
        recA, pA = analyse(snaps[first_inf], f"w{w}-first_infeasible_full@{first_inf}")
        # state B: jam-trigger retained skin
        skin, _ = PC.skin_of(snaps[-1])
        recB, pB = analyse(skin, f"w{w}-jam_trigger_skin@{js}")
        results += [recA, recB]
        if pA: provdump[recA["label"]] = _ser(pA)
        if pB: provdump[recB["label"]] = _ser(pB)
        print(f"w{w}: first-infeasible IIS size {recA.get('iis_size')} "
              f"({recA.get('n_distinct_origin_vertices')} vertices); "
              f"jam-skin IIS size {recB.get('iis_size')} "
              f"({recB.get('n_distinct_origin_vertices')} vertices)", flush=True)

    (OUT / "part4_iis.json").write_text(json.dumps(results, indent=2, default=float))
    (OUT / "part4_provenance.json").write_text(json.dumps(provdump, indent=2, default=float))

    lines = ["Part 4 -- inclusion-minimal infeasible subset (IIS) of compatibility constraints", ""]
    for r in results:
        if "iis_size" not in r:
            lines.append(f"{r['label']}: {r['feasibility']} (no IIS)")
            continue
        lines.append(f"{r['label']}: {r['feasibility']} r*={r['chebyshev_r']:.4e}")
        lines.append(f"   IIS size {r['iis_size']} constraints from {r['n_distinct_origin_vertices']} "
                     f"distinct originating vertices; IIS unique: {r['iis_is_unique']} "
                     f"(alternatives found: {len(r['iis_alternatives'])})")
        lines.append(f"   constraints: {r['iis_primary']}")
    lines.append("")
    lines.append("An IIS is inclusion-minimal (every constraint in it is needed for THAT subset's")
    lines.append("infeasibility), not minimum-cardinality, and not unique; it is a witness, not a proven")
    lines.append("causal repair target. Provenance (origin vertex + tiles) is in part4_provenance.json.")
    (OUT / "part4_report.txt").write_text("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))


def _ser(p):
    return dict(iis=[list(k) for k in p["iis"]],
                origin={f"{k[0]},{k[1]}": v for k, v in p["origin"].items()},
                prov=p["prov"])


if __name__ == "__main__":
    main()
