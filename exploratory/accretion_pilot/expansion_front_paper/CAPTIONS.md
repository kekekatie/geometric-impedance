# Figure captions and reading key

**Front:** the exposed boundary where new half-tiles can attach. **Choice:** a site where the
algorithm has two candidates when no site is forced. **Forced:** only one candidate remains under
the local enumeration. **F:** the computed set of compatible internal offsets. **Family:** one of
five indexed edge directions; a half-tile can have edges in two families.

## Figure 1. One local choice, two growing consequences

Actual reconstructed first-study configuration `2a3cfb2c41f77386` (world 19, slice 31).
It was selected before reconstruction by proximity to the median changed-region size among
the 41 elongated first-occurrence records, with a lexicographic key tie-break. Its changed
region contains 84 half-tiles and has aspect ratio 8.0077.

(a) The common built patch, with the choice site circled. Two magnified insets show option A and
option B separately at the same site; they are alternatives, not simultaneously placed tiles.
(c,d) Both branches after 20 patient-scheduler
slices. Saturated colour marks tiles each branch has where the other has a different tile,
using the original centroid-coverage definition. Gray is the shared base. Pale later additions
are outside that measured changed region: they may be common or outside the other branch's coverage.
Pale additions use hatching, consistent with the construction figure.
The dark outline is the boundary at the original choice, not the later boundary.
(b) Computed compatibility regions after each branch's first forced slice, directly labelled
"Compatible with A" and "Compatible with B", with the separating
line dashed. The base F is behind them in gray. This is the measurement time used by the study;
the plot does not assert that the dividing line is available from the choice tile alone.
F is a mathematical representation, not another physical location or a signal.
The time snapshots are now in the separate construction figure below.

## Figure 2. Orientation and a connected core

(a) All 45 first-occurrence configurations, plotted at their actual angles without jitter;
points can overlap. Circles mark the 41 elongated regions (aspect ratio at least 3), crosses
the other four. Colour indicates the dominant edge family. Dotted lines show
`axis = 108 - 2 * cut angle (mod 180 degrees)` in the repository's coordinate convention.
Maximum deviation among elongated regions is 2.5935167334 degrees. This is the corrected
exploratory correspondence across the full sample, including training, not the registered held-out test.
(b,c) Changed regions in the initial forced responses of the selected Figure-1 configuration,
using the original 40-slice burst cap and registered chain adjacency. Dark tile outlines mark the largest chain,
while fills retain the branch colours (blue for A, orange for B). The core contains
27/42 and 29/42 of each side's changed half-tiles. In this example these are also all of the
predicted-family changed tiles (27/27 and 29/29). These new diagnostic counts are illustrative.
The initial forced response is conditionally fixed under candidate-completeness and valid-extension
assumptions; it need not exhaust all consequences of the original choice.

## Figure 3. The same first choice can lead to different later outcomes

Actual follow-up exception `180fb0b920bb845b` (world 21, slice 8), predicted family 2.
The full reconstructed result matches the deposited record. Shown are B continuations 1 and 3,
the first indexed pair with different resulting geometry and different paired A/B dominant families.
Both begin from the same original B option and make a later choice at continuation slice 12.
A pale tile with a dark outline and arrow marks that later choice. Orange marks tiles absent from the other displayed B continuation.
The outline panel superimposes the two sets of nonidentical tiles, including both replaced places
and unequal coverage. The displayed family numbers belong to each continuation's A-versus-B
comparison, not to the B-versus-B outline alone. Across all five A/B pairs the dominant families
are `[2, 2, 3, 3, 3]`. A makes no later guess; B makes one in every continuation.
P4 evaluates only covered places and pools ordered tile-comparison instances. This example shows
that a later choice can change additional tiles; it does not show that all influence of the earlier
choice ends there. Some later details remain open while the first choice can still constrain other features.

## Figure 4. Building the response, one slice at a time

Actual branch-A construction from the Figure-1 example, after 1, 8 and 20 patient-scheduler slices.
All panels share a world scale. Gray denotes the already built base, with its original boundary outlined.
Blue consistently denotes tiles belonging to the measured A-versus-B difference at slice 20, showing
only those already built at the displayed time. Pale hatching denotes the other new additions.
The colours therefore distinguish membership in the final measured difference from construction time;
they do not assert that an early A-versus-B comparison would give the same changed set.
The first two snapshots contain no later guesses. No unbuilt or future-tile overlay is shown.
This is the same recorded example and geometry as Figure 1, separated to keep the opening overview legible.
