#!/usr/bin/env python3
"""
audit3_witness.py -- Part 3 of the audit: correct the witness interpretation.

For each recorded witness we report, separately:
  * the IIS CONSTRAINTS (rank, facet);
  * their distinct originating VERTICES (the argmax vertex per constraint);
  * the TILES carrying each origin vertex (a vertex belongs to several tiles).

We then test, rather than assert, the three interpretive claims:
  (A) "two tiles pulling in exactly opposite directions" -- check the IIS unit
      normals pairwise; report which witnesses are genuine anti-parallel pairs and
      which are not (e.g. a 3-facet squeeze in one pentagon).
  (B) "the same conflict carried forward unchanged" (equal r* at two times) --
      equal margins do NOT prove persistence. We TRACK the first-infeasible IIS
      keys and their originating vertices forward to the jam state and report
      whether that exact subsystem is still present and still infeasible there.
  (C) uniqueness -- the study tried 4 drop orders. We try 300 random orders and
      report the set of distinct inclusion-minimal witnesses actually seen, so the
      claim becomes "no alternative found in N tested orders" (or lists them).

Also records the corrected repair note: changing EITHER constraint in an IIS
removes THAT witness; it need not resolve other conflicts/other witnesses.

Writes results/audit3_witness.json.
"""
from __future__ import annotations
import json, random
import audit_common as A
from audit_common import Sl, WIN, M, L
import feas
import part4_iis as P4


def origins_and_tiles(tiles):
    rank = Sl.rank_of(tiles)
    cmax, origin, pos, conf = P4.constraints_with_origin(tiles, rank)
    return rank, cmax, origin


def unit_normal(key):
    rk, i = key
    n, h = WIN[rk]
    nx, ny = float(n[i][0]), float(n[i][1])
    nn = (nx * nx + ny * ny) ** 0.5
    return (nx / nn, ny / nn)


def witness_record(tiles, label):
    rec, p = P4.analyse(tiles, label)
    if p is None:
        return dict(label=label, feasibility=rec["feasibility"], note="not infeasible")
    iis = [tuple(k) for k in p["iis"]]
    origin = p["origin"]
    # constraints / vertices / tiles, kept separate
    cons = []
    vset = set()
    for key in iis:
        o = origin[key]
        vkey = tuple(o["vkey"])
        vset.add(vkey)
        tiles_here = P4.tiles_at_vertex(tiles, o["vkey"])
        cons.append(dict(constraint=list(key), origin_vertex=o["vkey"],
                         origin_layer=o["layer"], n_tiles_at_vertex=len(tiles_here),
                         tile_centroids=[t["centroid"] for t in tiles_here]))
    # pairwise anti-parallel
    pairs = []
    for a in range(len(iis)):
        for b in range(a + 1, len(iis)):
            ua, ub = unit_normal(iis[a]), unit_normal(iis[b])
            dot = ua[0] * ub[0] + ua[1] * ub[1]
            pairs.append(dict(keys=[list(iis[a]), list(iis[b])], unit_dot=round(dot, 6),
                              antiparallel=bool(abs(dot + 1) < 1e-9)))
    any_pair = any(pr["antiparallel"] for pr in pairs)
    # uniqueness over many drop orders
    cm = p["cmax"]
    seen = {tuple(iis)}
    keys = list(cm.keys())
    for s in range(300):
        order = list(keys); random.Random(s).shuffle(order)
        seen.add(tuple(P4.iis_deletion(cm, order)))
    distinct = sorted([[list(k) for k in w] for w in seen])
    return dict(label=label, feasibility="infeasible",
                n_constraints_total=len(cm),
                iis=[list(k) for k in iis], iis_size=len(iis),
                n_distinct_origin_vertices=len(vset),
                constraints=cons,
                iis_pairs=pairs,
                opposing_pair_description_valid=bool(len(iis) == 2 and any_pair),
                is_single_pentagon_multifacet=bool(len({k[0] for k in iis}) == 1 and len(iis) >= 2),
                n_drop_orders_tried=301,
                n_distinct_iis_found=len(distinct),
                distinct_iis=distinct,
                uniqueness_wording=("no alternative inclusion-minimal witness found in 301 tested drop orders"
                                    if len(distinct) == 1 else
                                    f"{len(distinct)} distinct inclusion-minimal witnesses found in 301 drop orders"))


def track_forward(world, si, js, fi):
    """Does the first-infeasible IIS (its (rank,facet) keys) remain present and
    jointly infeasible at the jam, and are its origin vertices the same? Equal r*
    alone does not establish this; here we check identities explicitly."""
    arm, full, skin = A.jam_full_and_skin(world, si, js)
    full_fi = arm["snaps"][fi]
    # first-infeasible full IIS
    recA, pA = P4.analyse(full_fi, f"w{world}-first_infeasible_full@{fi}")
    iisA = [tuple(k) for k in pA["iis"]]
    originA = pA["origin"]
    vertsA = {k: tuple(originA[k]["vkey"]) for k in iisA}
    # jam-trigger skin system
    rankB = Sl.rank_of(skin); cmB = Sl.constraints(skin, rankB)
    _, originB, _, _ = P4.constraints_with_origin(skin, rankB)
    # is the step-fi IIS key-set still present in the jam system, still infeasible, same origins?
    present = all(k in cmB for k in iisA)
    sub_infeasible = present and feas.classify({k: cmB[k] for k in iisA})["cls"] == "infeasible"
    same_origins = present and all(k in originB and tuple(originB[k]["vkey"]) == vertsA[k] for k in iisA)
    # also report the jam skin's own reported IIS keys for comparison
    recB, pB = P4.analyse(skin, f"w{world}-jam_trigger_skin@{js}")
    iisB = [tuple(k) for k in pB["iis"]]
    return dict(case=f"w{world}", first_inf_step=fi, jam_step=js,
                iis_first=[list(k) for k in iisA], iis_jam=[list(k) for k in iisB],
                first_iis_keys_present_at_jam=bool(present),
                first_iis_subsystem_infeasible_at_jam=bool(sub_infeasible),
                first_iis_origin_vertices_unchanged_at_jam=bool(same_origins),
                reported_witness_identical=bool(sorted(iisA) == sorted(iisB)))


def main():
    A.RESULTS.mkdir(parents=True, exist_ok=True)
    witnesses = []
    for (w, si, js, fi) in [(7, 0, 23, 9), (5, 0, 42, 17)]:
        arm, full, skin = A.jam_full_and_skin(w, si, js)
        full_fi = arm["snaps"][fi]
        witnesses.append(witness_record(full_fi, f"w{w}-first_infeasible_full@{fi}"))
        witnesses.append(witness_record(skin, f"w{w}-jam_trigger_skin@{js}"))
    tracking = [track_forward(w, si, js, fi) for (w, si, js, fi) in [(7, 0, 23, 9), (5, 0, 42, 17)]]
    report = dict(witnesses=witnesses, cross_time_tracking=tracking,
                  repair_note=("Changing EITHER constraint of an IIS removes THAT witness, not necessarily "
                               "the infeasibility: other IISes may remain. A repair touching both IIS "
                               "locations is sufficient to break that one witness but is neither necessary "
                               "(breaking one suffices for that witness) nor guaranteed to resolve all conflicts."))
    (A.RESULTS / "audit3_witness.json").write_text(json.dumps(report, indent=2, default=float))

    print("=== witnesses: constraints / vertices / tiles / opposing-pair ===")
    for wn in witnesses:
        if wn.get("note"):
            print(f"{wn['label']}: {wn['note']}"); continue
        print(f"{wn['label']}: IIS {wn['iis']} (size {wn['iis_size']}, {wn['n_distinct_origin_vertices']} vertices); "
              f"opposing-pair valid: {wn['opposing_pair_description_valid']}; "
              f"single-pentagon multifacet: {wn['is_single_pentagon_multifacet']}; "
              f"{wn['uniqueness_wording']}")
        for c in wn["constraints"]:
            print(f"      constraint {c['constraint']} <- vertex {c['origin_vertex']} on {c['n_tiles_at_vertex']} tiles")
    print("\n=== cross-time identity tracking (equal r* != same witness) ===")
    for t in tracking:
        print(f"{t['case']}: first-IIS {t['iis_first']} vs jam-IIS {t['iis_jam']}; "
              f"reported witness identical: {t['reported_witness_identical']}; "
              f"first-IIS keys present at jam: {t['first_iis_keys_present_at_jam']}; "
              f"first-IIS subsystem infeasible at jam: {t['first_iis_subsystem_infeasible_at_jam']}; "
              f"origin vertices unchanged: {t['first_iis_origin_vertices_unchanged_at_jam']}")
    print("\nwrote results/audit3_witness.json")


if __name__ == "__main__":
    main()
