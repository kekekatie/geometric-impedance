# Bounded static sensitivity plan — frozen before additional outcomes

Anchor: 98cfaa6ff24a805b846bcdffa6af0c6896e21305. Written after reading the original protocol/code and handback, before executing any new angular-grid readouts. No new growth runs beyond reproducing the eleven specified cases to step 44.

## Main grid: 528 requested windows

For each of the eleven recorded cases at both the original frozen jam and the scar-run final checkpoint:

- Use that checkpoint's band centroid (triangle-vertex average, same as original).
- Anchor angular direction to the original jam's notch direction, computed from the original dead-edge midpoint centroid relative to the jam band centroid. Keep this absolute direction fixed at both checkpoints.
- Centres: anchor + j*pi/3, for j=0,1,2,3,4,5.
- Half-widths: pi/8, pi/4, pi/2, 3*pi/4.
- Select triangles by centroid angle with the original 1e-12 angular tolerance.
- Reduce each selection to its largest full-edge-connected component. Break equal component sizes by the lexicographically smallest sorted tile-key tuple; serialize selected tiles in sorted key order.
- Score every selection, including empty selections and failures, with unchanged frozen reader thresholds and original birth hypotheses/reference metadata.
- Report A, B, ambiguous, empty/incompatible and reconstruction failure separately; retain areas, intersections, component sizes and choice-tile membership.
- Select a headline only by positive compatibility area >1e-9, then maximum tile count, then first centre/width in the declared ordering. Never use the selected hypothesis or B label for selection.

No grid enlargement, outcome-based centre adjustment or search outside these existing checkpoints is allowed.

## Resolution/centre diagnostic (fixed additional budget)

For world 7 / stream 0 only, compare both checkpoints under both original angular centre directions (original jam-notch opposite and original final cumulative-scar-centroid opposite), each with 32 and 48 uniformly spaced half-widths from pi/N through pi. This is 2 checkpoints × 2 centres × (32+48) = 320 requested windows. It isolates the headline 32%→50% comparison's change of scan design. Original scans are reused where identical, and all outcomes are retained, not just best windows. This diagnostic does not add a search-selected centre.

Total static sensitivity budget: 848 requested windows, fixed in advance. Duplicate geometries/reader inputs may be cached exactly without altering thresholds or selection. Counts will retain duplicate requested windows; effective unique subsets will also be reported.

## Controls (not a repair/search expansion)

Representative whole bands and original selected subsets at jam/final for world 7 and world 5: reverse tile and edge traversal, consistent translation of tiles and origin, nontrivial common lift-gauge change (origin, layer map and hypothesis right-hand sides transformed consistently), swap A/B hypothesis order, direct versus isolated-reader comparison. Also verify physical reconstruction and common gauge against independently propagated full-patch lifts for all scored original/sensitivity subsets. No control may change the model's thresholds.

This plan is committed before the sensitivity run. Any implementation problem or departure will be disclosed rather than silently widening this budget.
