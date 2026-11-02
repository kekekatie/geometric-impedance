#!/usr/bin/env python3
"""
export_state.py -- Part 1: export the self-contained retained-state input for the
cooperative-rearrangement pilot, from the AUDITED world-7 B continuation, stream
0, at its recorded jam (step 23).

Two files are written:

  input/retained_state.json   SEARCH-VISIBLE. The retained boundary band tiles,
      the true growth frontier (with edge ownership p,q,r,owner), the inner
      (pruning-exposed) boundary, the true-frontier dead sites, the gauge/rank
      map, the edge length, and the compatibility-witness origin vertices
      (computed from the FROZEN constraints of the jammed geometry -- a geometric
      property of the retained state, not historical information). No deleted
      interior tiles. No growth history. No A/B identity.

  input/evaluator_historical.json   EVALUATOR-ONLY. The fork S*, the A/B options
      cs, the committed choice (B = index 1) and its tile key, and the stream.
      Used ONLY by the Part-5 evaluator (the frozen reader). MUST NOT be read by
      candidate generation or selection.

Reproduces the audited jam (315 band tiles, 2 dead sites, infeasible r*).
"""
from __future__ import annotations
import json
import coop_common as CC
from coop_common import Sl, PC, L, D, M, S, WIN
import feas
import part4_iis as P4

W, SI, JS, FIRST_INF = 7, 0, 23, 9


def main():
    CC.INPUT.mkdir(parents=True, exist_ok=True)
    forks = PC_load()
    Sstar = forks[W]["Sstar"]; cs = forks[W]["cs"]; B = cs[1]
    stream = PC.streams_for(W)[SI]
    arm = PC.grow(Sstar, B, stream, 44)
    assert arm["stop"] == "jam" and len(arm["snaps"]) == JS + 1, "replay mismatch"
    full = arm["snaps"][-1]
    band, _ = PC.skin_of(full)

    # gauge / rank (consistent, taken once from the band)
    rank = Sl.rank_of(band)

    # true growth frontier (from the FULL patch) with ownership; inner exposed boundary
    full_fr = L.Patch(list(full)).frontier()
    band_fr = L.Patch(list(band)).frontier()
    true_ek = {CC.ekey(e[0], e[1]) for e in full_fr}
    band_keyset = {CC.dk(t) for t in band}
    true_frontier = [dict(p=CC.ez(e[0]), q=CC.ez(e[1]), r=CC.ez(e[2]), owner=CC.dk(e[3]))
                     for e in band_fr if CC.ekey(e[0], e[1]) in true_ek]
    inner_boundary = [dict(p=CC.ez(e[0]), q=CC.ez(e[1]), r=CC.ez(e[2]), owner=CC.dk(e[3]))
                      for e in band_fr if CC.ekey(e[0], e[1]) not in true_ek]

    # true-frontier dead sites (zero frozen candidates), from the FULL patch
    Pfull = L.Patch(list(full))
    dead = [e for e in full_fr if len(D.candidates(Pfull, *e[:3])) == 0]
    dead_sites = [dict(p=CC.ez(e[0]), q=CC.ez(e[1]), r=CC.ez(e[2]), owner=CC.dk(e[3])) for e in dead]

    # compatibility witnesses on the jammed band (frozen constraints; not historical)
    recB, pB = P4.analyse(band, f"w{W}-jam_trigger_skin@{JS}")
    witness_vertices = []
    if pB:
        for key in pB["iis"]:
            o = pB["origin"][tuple(key)]
            witness_vertices.append(dict(constraint=list(key), vertex=o["vkey"], layer=o["layer"]))
    # feasibility of the jammed band (sanity vs audit)
    cm = Sl.constraints(band, rank)
    cl = feas.classify(cm)

    retained = dict(
        schema=1,
        provenance=dict(world=W, stream_index=SI, jam_step=JS,
                        source_commit="53692c20c68a03a96b1e682ad8c90e60b764df21",
                        note="self-contained retained-state input; no deleted interior tiles, no history, no A/B identity"),
        edge_length=float(S),
        rank={str(k): int(v) for k, v in rank.items()},
        n_tiles=len(band),
        tiles=[CC.etile(t) for t in band],
        true_frontier=true_frontier,
        inner_boundary=inner_boundary,
        dead_sites=dead_sites,
        windows=[dict(normals=[[float(x) for x in nn] for nn in n.tolist()] if hasattr(n, "tolist")
                      else [[float(a), float(b)] for a, b in n], h=float(h)) for n, h in WIN],
        compatibility_witness_vertices=witness_vertices,
        jammed_band_feasibility=dict(cls=cl["cls"], chebyshev_r=cl["r"]),
    )
    (CC.INPUT / "retained_state.json").write_text(json.dumps(retained, indent=2, default=float))

    evaluator = dict(
        schema=1,
        WARNING="EVALUATOR ONLY -- historical A/B data. MUST NOT be read by candidate generation or selection.",
        world=W, stream_index=SI, stream=stream, jam_step=JS,
        true_option_index=1, true_option="B",
        Sstar=[CC.etile(t) for t in Sstar],
        options_cs=[CC.etile(c) for c in cs],
        choice_tile_B=CC.etile(B), choice_tile_B_dkey=repr(PC.dk(B)),
    )
    (CC.INPUT / "evaluator_historical.json").write_text(json.dumps(evaluator, indent=2, default=float))

    print(f"exported retained_state.json: {len(band)} band tiles, "
          f"{len(true_frontier)} true-frontier edges, {len(inner_boundary)} inner-boundary edges, "
          f"{len(dead_sites)} dead sites, {len(witness_vertices)} witness constraints")
    print(f"jammed band feasibility: {cl['cls']} r*={cl['r']:.4e} (audit: infeasible -0.0816)")
    print("exported evaluator_historical.json (evaluator-only; not for search)")


def PC_load():
    return SC_load()


def SC_load():
    import study_common as SC
    return SC.P3.load_forks()


if __name__ == "__main__":
    main()
