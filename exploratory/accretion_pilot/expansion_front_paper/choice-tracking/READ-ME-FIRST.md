# Following the open choices

Open WATCH-CHOICES.html in a browser. It contains 50 frames, slices 11–60, with a slider and Play/Pause. It works offline. The whole patch is above; a fixed close-up of the earlier contact is below. Whole-patch panels fit their respective final patches and therefore have different scales; the two close-ups use identical bounds.

## What to watch

Hollow pink circles mark every frontier edge with multiple locally legal candidates immediately BEFORE the numbered slice. A pink star marks the edge selected for a choice. Blue/orange marks tiles added DURING that slice; unlike the earlier film, these colours show current additions, not differences between histories. Grey is earlier construction. Dark outlines mark the frozen historical comparison region.

Several circles may involve overlapping alternatives. Their count is not a count of independent choices, and local legality does not guarantee indefinite continuation. Sites are tracked by their undirected edge endpoints.

## Results

Both histories reached slice 60 without a jam. All reconstructed states through slice 20 matched the previous cache.

| Continuation | Choice made at slice | First observed open before slice | Interpretation |
|---|---:|---:|---|
| Both | 12 | 12 | Shared branching opportunity |
| 1 | 29 | 20 | Waited nine slice intervals |
| 1 | 44 | 44 | Newly observed opportunity, selected immediately |
| 3 | 54 | 40 | Waited fourteen slice intervals |

The slice-29 and slice-54 sites stayed continuously open with unchanged candidate sets until selected. Tracking began before slice 1; “first observed” does not describe the entire earlier history of the world.

The slice-29 edge had a single forced candidate in the other continuation before slice 19. The other later selected edges were never observed as frontier edges in the opposite history through slice 60. This establishes differences in the observed opportunities between histories, not a complete causal chain. Different geometry, selection order and later random outcomes can all contribute.

The original scheduler exhausts forced growth before choosing. When no forced placement remains, it selects the frontier edge nearest the coordinate origin, with coordinate tie-breaks. Thus the next selected choice need not be newly delivered by the preceding burst. In these runs there were 24–48 multi-option frontier edges per pre-slice inventory in continuation 1, and 22–78 in continuation 3.

The film does not establish a moving object, a knot, or a physical time. Persistence of old tiles is automatic in this additive model. A rigorous activity comparison with matched control neighbourhoods remains to be done.

## Best next question

Inspect the transition into slice 44: the selected edge was newly observed as open. Identify which immediately preceding additions exposed it, then trace their local dependencies backwards. Contrast this with the waiting slice-29 site. This would compare a newly created opportunity with an existing opportunity finally selected. Do not infer a causal link solely from consecutive selection times.

## Audit and reproduction

inventory.json contains all frontier edges, candidate identities/counts, selected edges, status and placement counts for all 120 steps. event-summary.json compares selected edges with earlier inventories and the opposite history. replay.pkl preserves reconstructed geometry for rerendering; it is a trusted local Python cache, not needed to watch the film.

choice_tracking.py runs in the original expansion_front_paper directory alongside figures.py and results/geometry.pkl. summarize_choices.py produces the event summary from the inventory and uses a workspace-relative path. Included scripts are provenance records, not a standalone installation.

Original baseline: d4e00c5d4396c38bd69b265907b5f3d6c5bc030a. Case 180fb0b920bb845b. B continuations 1 and 3; original streams 20810350027 and 20810365865. Horizon 60, two selected histories, exploratory analysis. Earlier plan: CHOICE_TRACKING_PLAN.md.
