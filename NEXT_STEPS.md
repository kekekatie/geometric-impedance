# Where We Are & Where To Go Next

## Status (June 2026)

### What's solid
- **v0.3 validation**: Depth predicts address residue on near-return paths. Stronger in Penrose than AB. 10 seeds, 20k walkers, shuffled controls.
- **Exo/endo distinction**: AB retains identity via external coordinates (AUC 0.986); Penrose does not (0.661). Published on Zenodo.
- **Holonomy proxy v0.1**: Near-closed physical paths leave depth-dependent hidden-address residue. Not area-dependent. Geometry-dependent (shuffled controls confirm).
- **Path-depth profile v0.1**: Dip-and-return walkers have LESS residue than non-dippers. The dip is not a cost — it's the recovery mechanism. Walkers that touch the stable core recover their address. Walkers stuck at the edge cannot. Penrose shows this more strongly.

### What's dead
- alpha~0.553 via cost-time walks (lambda sweep killed it)
- Loop area as a predictor (Spearman ~0)
- "More depth traversal = more residue" (wrong direction — dip-and-return = LESS residue)

### What's alive and exciting
- **The dip is the engine, not the obstacle** (the brachistochrone idea)

## THE NEXT TEST: Brachistochrone Dip Profile Analysis

### The idea (from Karen, over champagne, June 10 2026)

The dip from stable/deep to unstable/shallow and back is like a brachistochrone: the geometry provides the momentum. The walker doesn't need external energy to be reconstructed — it "falls" through the depth asymmetry and that falling is what makes it findable in the next slice of now.

A real brachistochrone has a specific SHAPE: fast drop, gradual return (a cycloid). If the depth dip works like this, the shape of the dip should matter, not just whether it happened.

### Concrete test

Among dip-and-return near-loop walkers, characterise the DIP SHAPE:

1. **Dip asymmetry**: Is the descent (deep→shallow) faster or slower than the ascent (shallow→deep)?
   - Measure: steps from start to min-depth point vs steps from min-depth point to end
   - A brachistochrone-like dip would show fast descent, gradual return
   
2. **Dip sharpness**: Is a sharp V-dip better than a gradual U-dip for address recovery?
   - Measure: how long the walker spends near its minimum depth
   - Sharp dip = few steps at minimum, U-dip = many steps at minimum

3. **Dip timing**: Does it matter WHEN in the walk the dip happens?
   - Early dip + long recovery vs late dip + short recovery
   - If recovery needs time, early dips should produce cleaner addresses

4. **The key question**: Among dip-and-return walkers (which already have low residue), does dip SHAPE predict how clean the address recovery is? And does Penrose show a stronger shape-dependence than AB?

5. **Natural gradient following**: Do walkers that follow the "natural slope" of depth (moving along the gradient rather than against it) recover better?
   - This is the brachistochrone test: the path of least resistance through depth space should produce the cleanest recovery

### Controls
- Shuffled depth as always
- Compare symmetric dips vs asymmetric dips
- Compare AB vs Penrose shape-sensitivity

### What this would show if it works
- The hidden-space depth gradient acts as a self-propelling mechanism
- Reconstruction in the next "slice of now" doesn't require external input — the geometry provides it
- Aperiodic tilings (especially Penrose) have built-in asymmetry that drives this
- The brachistochrone is a metaphor for: falling through hidden-space curvature is what makes persistence possible

## Reminder for Karen
- No more chasing alpha~0.553
- The dip-and-return finding is the freshest, most exciting result
- Your champagne insight: "the dip is the engine" / brachistochrone momentum
- All results on branch `claude/bold-ritchie-l1Mc4`
- Handoff summaries in repo root for GPT/Gemini/Claude
- Share the path-depth profile results with GPT and Gemini — they'll have thoughts on the brachistochrone angle
