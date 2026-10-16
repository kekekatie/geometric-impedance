# Presentation revision after Astra's visual review

16 October 2026. This pass redraws the verified cached geometry; it does not change the selected
cases, measured values, growth rules or interpretation of the tests.

- Opening overview: portrait layout, four larger panels, two separate magnified choice insets,
  and directly labelled compatibility regions. Construction snapshots moved to a companion figure.
- Construction: blue consistently means membership in the measured slice-20 difference.
  Other new additions have pale hatching. Only already built tiles appear at each time.
- Connected core: branch-coloured fills with dark outlines replace purple. Family-colour legend
  and graph explanation sit outside the plotting area.
- Later-choice example: requested shorter title, family numbers in the caption, and a simple
  dark-outlined marker for the later choice. The caption retains the unequal-coverage distinction
  and the point that some later details remain open without erasing all earlier constraints.

## For Astra's verification

Read `HANDBACK.md`, `CHECKS.md`, `SCIENTIFIC_REVIEW.md`, and `results/reconstruction.json`.
The executable reconstruction and comparisons with original saved data are in `figures.py`;
the saved-data audit is `checks.py`; arithmetic and chronology checks are `geometry_checks.py`.
`START_HERE.md` has reproduction commands and the exact baseline.

The previous run matched the overview's key, changed count, shares, cut angle, fitted axis, ratio,
and every placement-time pair. It also reproduced the exception's entire saved situation dictionary.
This presentation pass uses that run's local geometry cache and performs visual QA on all four images.
No manuscript draft has been written in this task; the manuscript pass remains the next stage.
