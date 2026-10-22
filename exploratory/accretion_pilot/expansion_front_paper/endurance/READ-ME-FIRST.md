# First endurance tracker: physical-space geometry only

Open WATCH-ENDURANCE.html. It is self-contained and works offline; approximately 23 MB, so allow a moment to load. Choose a history, inspection category and slice. The example slider visits the matching records at that step. “Inspect longest candidate chain” cycles through the links of that history's deterministically selected longest same-class path.

The left view shows the preceding skin, with the selected parent in purple. The right shows the daughter in blue and new witness tiles in orange. Other new tiles are green. A/B/C labels on close-up selected triangles expose their decorated corner roles. The optional whole-skin view provides context. No example is invented when a category has no records at a step.

## Findings

| History | Observed slices | Recorded occurrences | Same-class candidate links | Longest path (links) |
|---|---|---:|---:|---:|
| Continuation 1 | 60–70, ending in jam | 2,606 | 45 | 1 |
| Continuation 3 | 60–120 | 3,711 | 87 | 2 |
| Alternative at 29 | 60–120 | 4,302 | 74 | 1 |

The clearest selected example is a frontier-star class appearing at slices 97, 98 and 99 in continuation 3. Each next occurrence includes a newly placed tile touching the preceding occurrence. The two links are real under the stated geometric rule, but do not establish an enduring object or causal transmission of a pattern. The selected class is a small incomplete star; the repeated geometry may be an ordinary feature of advancing construction.

We found no longer same-class path in these observed windows under this alphabet and connection rule. This does not rule out endurance under other definitions, larger patterns, different histories or a longer horizon. Cross-class chains are deliberately not promoted to enduring objects.

There are 150,034 different-class candidate links. These are heavily overlapping local contacts, not independent transitions or established decay channels. Repetition of such links alone is not evidence of a characteristic breakup mechanism.

Among newly observed occurrences lost with nearby construction and without a same-class successor (excluding complete stars simply leaving the selected band), the median number of nearby-active steps up to loss is 1 for both families in each history. This is descriptive of a strict fixed-pattern definition: adding a tile often changes the class immediately. It is not an inferred physical decay law. Initial and surviving occurrences are censored; no unbiased lifetime distribution is claimed.

## Operational definitions

See ENDURANCE_PROTOCOL.md for the definitions fixed before counting. Vertex stars comprise actual frontier stars and complete 360-degree stars within two retained-graph edges of the frontier. Frontier clusters comprise every connected subset of 2–4 true-frontier edges and their directly supporting decorated tiles. They overlap.

An occurrence has a fixed physical tile set, selected edge set and centre where applicable. Class ignores translation and proper rotation but preserves scale, tile type and A/B/C corner roles. Coordinates in S units are rounded to five decimals for canonicalization: these are numerical geometric classes, not a symbolic exactness proof. Reflection produces a paired class; +/− is a conventional ordering, while achiral means the class matches its reflection. These are not spin assignments.

Candidate links require a newly appearing daughter that contains a newly placed tile touching a parent vertex, with both parent and daughter incident to the actual frontier. Links stay within the star family or the cluster family; cluster size may change. Same-class links and different-class transitions are stored separately. Links need not imply replacement: a parent can still be present when a daughter appears.

Direct activity is attachment to a pre-step incident frontier edge. Nearby activity is a new tile touching a vertex within two pre-step graph edges of the occurrence. “Waiting” means no direct attachment; nearby activity may still be happening. The two clocks are recorded separately from slice number. No activity clock advances for the jam attempt.

Pattern loss, closure of all incident frontier edges, a complete star leaving the selected band, and eventual removal of its final constituent tile are separate fields. “Last constituent tile dropped” does not assert no earlier successor; inspect links separately. Unlinked lookalikes mean no same-class link under this finite-window rule, not no conceivable ancestry.

## Separation and verification

Growth was rerun from the verified skin-only checkpoints. A one-way pipe exported skin/frontier/new-tile snapshots; the observer had no return channel. All growth processes exited before motif analysis began. Every exported step's status, placement count, mode and retained count matched the prior checked run. The growth and scheduling code was unchanged.

Every one of the 150,240 candidate links was audited for a parent in the preceding snapshot, a newly born daughter, and newly added witness tiles belonging to that daughter and touching the parent. Same-class labels were checked. Synthetic classification tests and 78 actual motif translation/rotation/reflection tests passed. The jam was checked not to create activity or dissolution events.

The JavaScript passes Node's syntax check. Automatic browser preview was blocked by the browser tool's local-file URL policy, so a full rendered-browser interaction test was not performed. The standalone scientific still candidate-chain.png was rendered and visually inspected.

## Files and next step

summary.json and audit.json summarize results. The three *-observer.json files contain class/mirror catalogues, tracks, per-step events, witnesses and snapshots. skin-snapshots.pkl is the observer's trusted local replay cache, not an input to growth. Source scripts and the viewer template are included as provenance; they require the existing research checkout and environment, not a standalone installation.

Next: inspect the two-link star example and a waiting or buried comparison together. Before interpreting any chain as special, compare its frequency with ordinary frontier growth and test sensitivity to pattern size and the contact rule. Perpendicular-space diagnostics remain deferred. The scheduler still coordinates the entire frontier; neither local physical time nor physical particles are established.
