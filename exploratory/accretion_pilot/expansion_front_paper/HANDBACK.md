# Checks and figures are ready for review

16 October 2026. The manuscript rewrite is the next stage.

## What changed

Added a reproducible descriptive audit, numerical geometry checks, three scientific figures in
SVG and 300 dpi PNG, detailed captions, a scientific review and a restart note. Original registrations,
implementations and deposited results were preserved.

## What was actually run

- Recomputed the saved-data scorecards, corrected bins, overlap, stratified persistence, family coverage,
  angle errors and pooled regression.
- Checked actual window normals, indexed direction arithmetic and registration chronology.
- Reconstructed two world prefixes and selected branch growth, using the original implementation.
- Compared the overview's geometry measurements and every placement pair with the saved first-study record.
- Recomputed the complete exception record and found exact agreement with its saved dictionary.
- Inspected the three final figures visually, including labels, legends and the exception's later choice.

No full historical study rerun or independent engine implementation was performed.

## Main results

| Check | Result |
|---|---|
| Unique configurations | 45 in each study; 13 shared |
| New follow-up configurations | 32; predicted initial-burst family in 32/32 |
| Family persistence with a later choice | 13/14 configurations |
| Family persistence without a later choice | 31/31 |
| Follow-up family counts, 0 through 4 | 16, 0, 13, 6, 10 |
| Maximum orientation deviation | 2.5935167334 degrees over 41 elongated regions |
| Pooled placement fit | 4,331 instances; intercept 2.44187508, slope 1.08732214 |
| P4 | 1/2 eligible configurations; 44/92 covered comparison instances |

No discrepancy was found in these supplied numerical claims. The rough draft's stronger interpretations
still require the repairs documented in `SCIENTIFIC_REVIEW.md`.

## Figure provenance

Figure 1 uses the median-size elongated case, key `2a3cfb2c41f77386`, selected by a recorded rule
before reconstruction. Figure 2 combines all-sample orientation data with that case's actual connected chains.
Those chains contain 27/42 and 29/42 changed half-tiles and, in this selected example, all of the
predicted-family changed tiles. Figure 3 reconstructs exception `180fb0b920bb845b` and compares two
continuations of the same B option; their later choice occurs at slice 12. Seeds, streams, selection
and verification details are in `results/`.

## Remaining limits and next action

This verifies the reported computations at the checked scope. It does not prove completeness of the
local candidate generator, global extendability from nonempty F, or a universal ribbon theorem.
The largest-chain family coverage is a single-example diagnostic. Exact AI designations remain to
be confirmed during the manuscript pass.

Next: review the figures and captions, then revise the paper around them. `START_HERE.md` preserves
the restart point and commands. Work is saved locally; nothing has been merged or published.
