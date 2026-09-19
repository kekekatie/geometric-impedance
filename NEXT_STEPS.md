# Where We Are & Where To Go Next

## Status (June 2026)

### What's solid
- **v0.3 validation**: Depth predicts address residue on near-return paths. Stronger in Penrose than AB. 10 seeds, 20k walkers, shuffled controls.
- **Exo/endo distinction**: AB retains identity via external coordinates (AUC 0.986); Penrose does not (0.661). Published on Zenodo.
- **Holonomy proxy v0.1**: Near-closed physical paths leave depth-dependent hidden-address residue. Not area-dependent. Geometry-dependent (shuffled controls confirm).
- **Path-depth profile v0.1**: Dip-and-return walkers have LESS residue than non-dippers. The dip is not a cost — it's the recovery mechanism.
- **Brachistochrone v0.1**: The SHAPE of the dip matters — but not the way we expected. Lingering at minimum depth (U-dip) >> brief touch (V-dip). Smooth ascent helps. Fast-vs-slow drop doesn't matter.

### What's dead
- alpha~0.553 via cost-time walks (lambda sweep killed it)
- Loop area as a predictor (Spearman ~0)
- "More depth traversal = more residue" (wrong direction — dip-and-return = LESS residue)
- Brachistochrone fast-fall asymmetry as predictor (Spearman ~0.02, p>0.4)

### What's alive and exciting
- **Lingering time at the stable core is the engine** (U-dip >> V-dip)
- **Smooth return to depth = cleaner recovery** (ascent smoothness Spearman -0.19 to -0.25)
- **Excursion depth remains strongest predictor** (Spearman -0.25 to -0.32)
- Penrose shows stronger shape effects than AB, consistent with endohedral structure

## THE STORY SO FAR (for any new AI collaborator)

1. Depth predicts address residue (deeper start = less mismatch on return)
2. Physical near-closure ≠ address closure (the holonomy-like effect)
3. Dipping into shallow territory and returning = LESS residue (the dip is recovery)
4. The dip shape matters: it's not about falling fast, it's about **spending time at depth**
5. Penrose consistently shows stronger effects than AB

## POSSIBLE NEXT DIRECTIONS

### 1. Controlled depth profiles (highest priority)
Deliberately construct walks with specific depth trajectories instead of filtering random walks:
- Force "stay-deep" walks (never leave the core)
- Force "stay-shallow" walks (never enter the core)
- Force "dip-and-linger" walks (go to depth, stay N steps, return)
- Force "dip-and-bounce" walks (go to depth, immediately return)
- Vary the linger duration systematically to find the critical residence time

This would directly test: how many steps at depth are needed for address recovery?

### 2. Critical depth threshold
Is there a specific hull depth below which addresses snap back? The current analysis uses median splits. A finer-grained analysis could map out the recovery landscape:
- Bin walkers by their minimum depth reached
- Plot residue as a function of minimum depth
- Look for a threshold/phase transition

### 3. Depth gradient following
Do walkers that move "downhill" in depth space (following the natural gradient toward the hull centre) recover better than those that move against it? This tests whether the perpendicular-space geometry has preferred directions for address recovery.

### 4. Multi-step recovery dynamics
At what POINT along the return path does the address actually recover? Track the address residue step-by-step during the ascent phase:
- Does it recover gradually?
- Is there a snap-back moment?
- Does it recover differently in AB vs Penrose?

## Reminder for Karen
- The brachistochrone fast-fall idea didn't pan out as stated, BUT the reframed version ("lingering at depth") is strongly supported
- Penrose shows stronger effects everywhere — consistent with endohedral structure
- All results on branch `claude/bold-ritchie-l1Mc4`
- Handoff summaries in repo root for GPT/Gemini/Claude
- Share the brachistochrone results — the "U-dip vs V-dip" finding is the freshest result
