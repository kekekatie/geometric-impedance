1. **What independently reproduced?**

   All 12,248 seeded connected regions of up to eight triangular tiles leave an incompatible exterior. A separate enumeration recovers exactly the same family. All fifteen six-triangle hexagons have 128 decorated fillings, with only the identity legal. Four is the numerical minimum in the defined 20-row constraint-deletion problem. The 11 selected stars span a 41-tile union in ten components. The frozen reader baseline is `empty_incompatible`. No repair qualified, so construction and post-repair readout were not attempted.

2. **What changed or failed?**

   The 41-tile example is a heuristic deletion, not a minimum connected repair: it actually removes 12 vertices, loses eight outer and four inner boundary edges, and is feasible only at zero numerical margin. The selected vertices span 12.48 edge units; the whole footprint spans 14.05. True-frontier scoring is corrected from 103 combined boundary edges / 101 growable to **73 true-frontier edges / 71 growable**. The original standalone validator accepts an empty filling; stronger checks reject that and still recover the same fifteen identity-only results. The no-change shortcut now preserves an unresolved full-band verdict in the isolated corrected helper. Protocol ordering/caps and dormant permitted-region handling also need clearer documentation.

   Exact reproduction is qualified: Part 4, Part 5 and evaluator input agree after line-ending normalization. Three exported float fields differ by at most `1.12e-16`. Part 3's internal shortcut breakdown differs by 69 regions, while all final verdicts agree. No historical file was changed to force agreement.

3. **What can we now claim safely?**

   Numerical evidence excludes compatibility-restoring fixed-boundary replacements in the **seed-containing connected size-at-most-eight family**, under the fixed physical coordinates and four-layer projection-window convention. Independent component relifting is not an allowed change of that problem. This is not an exhaustive whole-band theorem, a minimum repair size, a legal-move path, or impossibility of every conceivable continuation. The deletion example's zero-margin feasibility remains numerically fragile and uncertified symbolically.

4. **What is the smallest sensible next step?**

   Review/adopt the scoped wording, corrected true-frontier count and isolated validator safeguards. If the 41-tile example is important, certify that existing zero-margin result before drawing a robust bound from it. No expanded repair search is justified by this audit alone. The requested audit is complete and stops here.

For Katie and Astra: details and function references are in `AUDIT_REPORT.md`; exact commits, environment, commands and comparison limits are in `REPRODUCTION.md`. Machine-readable results and scripts accompany them. Audit branch: `audit/cooperative-rearrangement-2026-11-03`; final commit and push status are provided in the delivery receipt. The pinned historical pilot and engine are preserved.
