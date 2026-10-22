# Observer endurance tracker — physical-space first pass

Fixed scope: skin-only checkpoints at 60 for continuation-1, continuation-3 and alternative-29; stop at 120 or jam. Growth runs in a separate process. The observer receives skin snapshots, true frontier and this-step additions; its only return messages are STEP/STOP. No perpendicular-space diagnostics or physics labels are computed.

## Alphabet

Vertex stars: all true-frontier vertices (incomplete stars), plus complete 360-degree stars within two graph edges of a frontier vertex. The graph contains actual retained tile edges. Exclude incomplete vertices created by the interior crop. Decoration is represented by triangle type and ordered A/B/C corners. Star class includes its centre and complete/incomplete label.

Frontier clusters: enumerate ALL connected subsets of 2, 3 and 4 distinct true-frontier edges, adjacency by a shared endpoint. Include their edge-supporting tiles, their decorations and the chosen edge subset. Clusters overlap; counts are not independent structures or exclusive objects. “Pocket” is a descriptive family name, not a curvature or defect claim.

Classes are translation- and proper-rotation-invariant geometric encodings, preserving scale and decorated corner roles. Reflections are classified separately; each class carries a mirror-pair identifier and a conventional +/- label or achiral flag. Canonical dimensionless coordinates round to 5 decimals, explicitly a numerical geometric equivalence rather than symbolic exact arithmetic. Validate translation/rotation/reflection invariance on fixtures before analysis.

## Identity, activity, transitions

An occurrence retains its identity only while its exact physical tile set, selected frontier edges and star centre remain identical. Record an observation per global slice. Track direct attachments to its pre-step incident frontier edges, and nearby activity if a new tile touches a pre-step graph vertex within distance 2 of its vertices. These are separate counters; zero direct attachment is called waiting, even if nearby activity occurs.

A renewal/transition candidate connects a pre-step frontier occurrence to a newly appearing same-family occurrence only if a tile added in that step is part of the daughter and shares a vertex with the parent. Daughter must remain incident to the true frontier. Same-class links are renewal candidates; different-class links are transitions. Shared old vertices alone are insufficient. Save actual witness tile IDs. Links can branch/merge and are not proof of causal dependence, objects, or repeatable decay channels.

Log persistent occurrences, class/shape loss, frontier closure, departure from the selected observation band, and eventual full removal of the occurrence's tiles separately. A lost active occurrence with nearby activity and no same-class candidate is “loss without same-class renewal”, not automatically physical dissolution. An unrelated lookalike is a newly appearing class already represented in the previous snapshot with no same-class candidate link under this rule; this does not establish no ancestry before our observation window.

Slice 60 occurrences are left-censored; run ends and jams right-censor remaining tracks. A jam is never assigned as motif dissolution. Count renewed chains by same-class candidate links and disclose overlap. No minimum meaningful endurance or physical lifetime is inferred. Viewer selection: show longest candidate chain per history deterministically, plus all links available for inspection; no hand-picked success case.
