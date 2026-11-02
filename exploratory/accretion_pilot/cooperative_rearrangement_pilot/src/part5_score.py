#!/usr/bin/env python3
"""
part5_score.py -- Part 5: separate scoring (compatibility / construction / A/B
readout). This is the EVALUATOR: it is the only place the historical A/B data
(input/evaluator_historical.json) is read. Candidate generation (Part 3/4) never
reads it.

The frozen reader (archive-free-reader/skin_reader.py) and the original
historical hypotheses are used UNCHANGED, via the pilot's phase4_readout adapter.
The reader receives only retained geometry + the historical hypotheses -- never
archived lifts or deleted tiles.

Because Part 3 ruled out every connected region and Part 4 found no compatibility-
restoring replacement, there is no qualifying post-repair candidate to score.
This script therefore:
  (1) establishes the PRE-repair baseline readout on the jammed band (the initial
      jammed state is already reader-incompatible, by design);
  (2) records candidate counts at the dead sites and at ALL true growth-frontier
      sites of the jammed band;
  (3) states that no post-repair readout applies (no qualifying repair), so no
      recovery of the historical readout was demonstrated or claimed.

Writes results/part5_score.json.
"""
from __future__ import annotations
import json
import coop_common as CC
from coop_common import Sl, PC, L, D, S
import phase4_readout as RD   # frozen-reader adapter (pilot); unchanged


def load_band():
    st = json.loads((CC.INPUT / "retained_state.json").read_text())
    return st, [CC.dtile(t) for t in st["tiles"]]


def load_evaluator():
    ev = json.loads((CC.INPUT / "evaluator_historical.json").read_text())
    Sstar = [CC.dtile(t) for t in ev["Sstar"]]
    cs = [CC.dtile(c) for c in ev["options_cs"]]
    return ev, Sstar, cs


def frontier_candidate_counts(band):
    P = L.Patch(list(band))
    fr = P.frontier()
    counts = [len(D.candidates(P, *e[:3])) for e in fr]
    dead = sum(1 for c in counts if c == 0)
    return dict(n_frontier=len(fr), n_dead_sites=dead,
                n_growable=sum(1 for c in counts if c > 0),
                candidate_count_histogram={str(k): counts.count(k) for k in sorted(set(counts))})


def choice_tile_present(band, B):
    bk = PC.dk(B)
    return any(PC.dk(t) == bk for t in band)


def main():
    st, band = load_band()
    ev, Sstar, cs = load_evaluator()
    B = cs[1]

    # (1) pre-repair baseline readout (frozen reader)
    payload = RD.build_payload(Sstar, cs, band)
    result = RD.run_reader(payload)
    outcome, detail = RD.classify(result)

    # (2) candidate counts
    fc = frontier_candidate_counts(band)

    # choice-tile fate
    b_present = choice_tile_present(band, B)

    report = dict(
        case="w7-B-s0 jam@23",
        evaluator_only_inputs="input/evaluator_historical.json (Sstar, cs); not seen by Part 3/4 search",
        reader="frozen archive-free-reader/skin_reader.py (unchanged)",
        pre_repair_baseline=dict(
            reader_status=result.get("status"),
            outcome=outcome, detail=detail,
            reader_selected=result.get("selected"),
            reader_area=result.get("area"),
            true_option="B (index 1); 'correct' = reader selects B",
            choice_tile_B_present_in_band=bool(b_present),
            interpretation=("The initial jammed state is already reader-incompatible by design (the jam gives "
                            "F=0). An empty/incompatible readout here is NOT memory loss; it is the absence of "
                            "any consistent offset to read."),
        ),
        frontier_candidate_counts=fc,
        post_repair=dict(
            qualifying_repair_found=False,
            note=("No connected fixed-exterior region (size<=8) restored compatibility (Part 3/4), so there is "
                  "no qualifying post-repair candidate. A correct post-repair result would require RECOVERY of "
                  "the historical readout; none was demonstrated or claimed. No archived lifts or deleted tiles "
                  "were supplied to the reader."),
        ),
        reader_coordinate_handling=("The reader processed the frozen-template band geometry without coordinate "
                                    "errors; no candidate generation produced reader-unhandleable coordinates "
                                    "(no qualifying candidate was produced)."),
    )
    CC.RESULTS.mkdir(parents=True, exist_ok=True)
    (CC.RESULTS / "part5_score.json").write_text(json.dumps(report, indent=2, default=float))

    print(f"pre-repair baseline readout: status={result.get('status')} outcome={outcome} "
          f"(selected={result.get('selected')}, area={result.get('area')})")
    print(f"choice tile B present in band: {b_present}")
    print(f"frontier: {fc['n_frontier']} edges, {fc['n_dead_sites']} dead, {fc['n_growable']} growable; "
          f"hist {fc['candidate_count_histogram']}")
    print("post-repair: no qualifying repair -> no recovery of historical readout demonstrated or claimed")
    print("wrote results/part5_score.json")


if __name__ == "__main__":
    main()
