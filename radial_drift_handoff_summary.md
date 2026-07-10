# Radial Drift Alignment v0.1 — Handoff Summary

## What was tested

Other Claude predicted the shallow drift vectors point radially OUTWARD — toward the hull boundary, toward escape. This would give the arrow-of-time its orientation: boundary-ward.

We measured the angle between each vertex's drift vector and its radial position vector (from hull centroid). 0° = outward, ±180° = inward.

## The headline: THE DRIFT IS INWARD, NOT OUTWARD

**0.0% of shallow vertices point outward.** The drift is overwhelmingly INWARD — toward the hull centre.

| Depth zone | AB radial drift | Penrose radial drift | Direction |
|-----------|----------------|---------------------|-----------|
| Shallow (<0.3) | -0.753 | -0.777 | **Strongly inward** |
| Deep (>0.7) | -0.347 | -0.251 | Weakly inward |

Fig 1 is definitive: the angle distributions pile up at ±180° (inward), with nothing near 0° (outward). Both substrates. No ambiguity.

**Spearman(depth, radial_drift) = +0.73 (AB), +0.76 (Penrose).** Positive because deeper vertices have LESS inward drift (closer to zero). But it's still inward everywhere.

## Why this makes geometric sense

If you're at the edge of a disc, most of your neighbours are toward the centre. The mean displacement vector necessarily points inward. The shallower you are, the more lopsided: there's simply nothing further out — you're at the boundary of the acceptance window.

This is not a force or a tendency. It's pure geometry: the boundary truncates the available directions, leaving an inward bias.

## What this means for the walk residue mechanism

The mechanism is now completely clear:

1. Every step moves you by 1.0 in perp-space (uniform magnitude)
2. At the boundary, available directions are truncated → net inward bias
3. A random walk from a shallow vertex accumulates this inward bias → large net displacement from start → high residue
4. A random walk from a deep vertex has nearly balanced directions → steps cancel → small net displacement → low residue

The "instability" of shallow addresses isn't about escaping outward — it's about being dragged inward by the geometry's truncation. The walker doesn't drift toward the edge; it drifts toward the centre, but FROM the edge, which means it moves far from where it started.

## The arrow-of-time correction

Other Claude predicted: "drift outward, boundary-ward, toward escape."

Reality: drift is INWARD, centre-ward, toward depth.

This doesn't kill the statistical arrow entirely, but it reorients it. The "time happens at the edge" story survives in a modified form: the edge is where the strongest drift exists (shallow radial drift = -0.75), so the edge is where walkers move the most in perp-space, accumulating the most address change. The deep centre is where everything is balanced and still. But the direction of drift is centripetal, not centrifugal.

## The chirality test: NO handedness

Mean tangential drift: 0.000132 (AB), -0.000060 (Penrose). Both effectively zero. There is no chirality — no handedness — in the drift structure. The drift is purely radial (inward), with no rotational component.

The Penrose "pinwheel" that other Claude noticed in fig 5 is real in shape but not chiral — it's the 10-fold symmetry creating visual spoke patterns, not actual handedness.

Fig 3 is the cleanest summary: the radial component sweeps from -0.78 (shallow) to ~0 (deep), while the tangential component is flat at zero everywhere. The entire drift structure is radial. No twist.

## Updated story arc

1. **v0.3**: Depth predicts walk residue. EXPLAINED by directional balance.
2. **Directional balance**: Deep = balanced, shallow = biased. Spearman -0.72/-0.78.
3. **Radial alignment (this test)**: The bias is INWARD toward hull centre. 0% outward. Purely radial, no chirality.
4. **Complete mechanism**: Boundary truncation → inward directional bias → accumulated drift from start → high residue at shallow positions.

## What this does NOT claim

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- The arrow-of-time is NOT outward/escape-ward as other Claude predicted.
- No chirality/handedness.
- The "boundary = where time lives" survives but the direction is centripetal.

## Files

- radial_drift_v0_1_report.md — full report
- vertex_radial.csv / depth_bin_radial.csv / radial_stats.csv
- fig_1 — THE ALIGNMENT: angle distribution, 0% outward (KEY)
- fig_2 — Fraction outward by depth
- fig_3 — Radial vs tangential by depth (THE CLEANEST SUMMARY)
- fig_4 — Angle vs depth density
- fig_5 — Chirality test: tangential drift (zero)
- fig_6 — Polar histogram (shallow)
- fig_7 — Substrate comparison
- radial_drift_v0_1.py — reproducible script
