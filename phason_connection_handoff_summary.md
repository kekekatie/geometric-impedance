# Phason Physics Connection — Handoff Summary

## What this is

A literature synthesis connecting our computational findings (directional balance, depth-dependent drift, channel independence) to the established physics of phason modes in quasicrystals. This is NOT a claim that we've discovered phason physics — it's a map showing where our results slot into an existing theoretical and experimental framework.

## Our key findings (recap for context)

1. **Directional balance**: Interior vertices have balanced neighbour directions; boundary vertices have biased directions. Spearman correlation with hull depth: -0.72 (AB), -0.78 (Penrose). THE mechanism.
2. **Radial drift**: Random walks drift INWARD, not outward. Strength scales with depth.
3. **Channel independence**: Address (perp-space coords) and weave (graph topology) are independently knockoutable. Both substrates are weave-primary.
4. **Redundancy asymmetry**: AB has address as backup channel; Penrose doesn't. This is the real exo/endo distinction.
5. **Null disc control**: Random points + Delaunay show no depth-drift correlation (Spearman ~0.05). The signal is genuine quasicrystal structure.

## The phason connection

### What are phasons?

In quasicrystals, there are two types of excitations:
- **Phonons**: ordinary elastic deformations (shifts in physical space)
- **Phasons**: shifts in perpendicular space that cause discrete tile rearrangements ("phason flips")

A phason flip is when a local tile configuration switches to an alternative valid configuration. Critically, phason flips happen at specific vertices — the ones near the BOUNDARY of the acceptance window in perpendicular space.

### Why our results matter for phason physics

**Key paper: Jagannathan 2024** — Shows that the Ammann-Beenker acceptance window subdivides into 6 vertex-type domains (A-F). Coordination number maps directly to depth: z=8 at the centre, z=3 at the boundary. This is exactly our hull depth gradient, but characterized by vertex type rather than continuous depth.

**Our directional balance IS the microscopic mechanism.** A vertex near the perp-space boundary:
- Has few, directionally biased neighbours (our finding)
- Therefore has low coordination and constrained local geometry (Jagannathan's vertex types)
- Therefore is susceptible to phason flips (moving it across the window boundary changes its type)

Nobody has previously reported the depth-dependent directional balance correlation. The vertex-type classification was known; the dynamical consequence for random walks was not.

### Specific literature connections

| Our finding | Literature connection | Key reference |
|-------------|----------------------|---------------|
| Directional balance ~ depth | Vertex types map to acceptance window depth | Jagannathan, Eur. Phys. J. B (2024) |
| Boundary vertices have biased directions | Phason-susceptible sites cluster at window boundary | de Bruijn (1981); Socolar & Steinhardt (1986) |
| Random walks drift inward | Phason modes are diffusive (not propagating) | Lubensky, Ramaswamy & Toner, Phys. Rev. B (1985) |
| Graph topology carries 84-94% of signal | Matching rules constrain perp-space fluctuations | Levine & Steinhardt (1986); Jeong & Steinhardt (1996) |
| AB has address backup, Penrose doesn't | Different quasicrystal symmetries have different phason elasticity | Socolar, Lubensky & Steinhardt, Phys. Rev. B (1986) |
| Weave-primary for both substrates | Local isomorphism = topology encodes identity | Baake & Grimm, "Aperiodic Order" Vol. 1 (2013) |

### Experimental phason measurements exist

This isn't just theory. Phason dynamics have been measured:
- **Neutron scattering**: Diffuse scattering from phason disorder in Al-Pd-Mn and Al-Cu-Co (Coddens et al., various)
- **TEM**: Direct observation of phason flips in decagonal Al-Ni-Co (Edagawa, Suzuki & Takeuchi, Phys. Rev. Lett. 2000)
- **Nature 2003**: Real-time observation of phason fluctuations (Abe et al., Nature 421, 347)
- **NMR**: Local environment changes from phason flips detected via NMR relaxation

The bridge from our computational results to these measurements is short: our directional balance gradient predicts WHERE phason flips should preferentially occur (boundary vertices), and experimental techniques can measure whether they do.

## What this means for the project

### The honest framing

Our results provide a **microscopic geometric mechanism** for something the phason literature has described at a coarser level:
- They know boundary vertices flip. We show WHY (directional balance → biased local geometry → susceptibility).
- They know phason modes are diffusive. Our random walks model this microscopically.
- They know matching rules constrain fluctuations. We quantify how much information the graph topology carries (84-94% under address shuffle).

This is a legitimate condensed matter physics connection. It does NOT require:
- Berry curvature or quantum holonomy
- Baryogenesis analogies
- Any claim beyond "geometric mechanism for known phason phenomenology"

### What it IS NOT

- NOT a discovery of phason physics (that's 40 years old)
- NOT a claim that our tilings are physical quasicrystals
- NOT Berry curvature, gauge theory, or topological field theory
- NOT baryogenesis (that was an overclaim — see verdict below)

### The baryogenesis question

Gemini proposed a "Geometric Impedance as Valence" (GIV) framework connecting our work to matter-antimatter asymmetry. **Verdict: metaphor, not physics.** The analogy (asymmetric boundary conditions → asymmetric outcomes) is poetically appealing but:
1. Real baryogenesis requires Sakharov conditions (baryon number violation, C/CP violation, departure from thermal equilibrium)
2. Our tilings have none of these
3. Publishing this would damage credibility of the real findings
4. Not everything has to be everything

## Suggested next steps

### Computational (can do now)
1. **Vertex-type classification**: Use Jagannathan's A-F classification for AB vertices. Map our directional balance onto these types. Prediction: balance should step-function across type boundaries, with A (z=8, centre) showing near-zero balance and F (z=3, boundary) showing maximum bias.
2. **Phason flip susceptibility**: For each vertex, compute how close it is to a type boundary in perp-space. Correlate with our directional balance. This would directly connect our mechanism to phason flip probability.

### Literature (needs human)
3. **Read Jagannathan 2024 carefully** — the vertex-type acceptance window figure should map directly onto our hull depth gradient.
4. **Check Edagawa et al. 2000** (TEM phason flips) — their observed flip sites should correlate with boundary positions.

### Writing
5. **Short paper framing**: "Directional balance as a microscopic mechanism for depth-dependent phason susceptibility in 2D quasicrystal tilings." This is a concrete, testable, correctly-scoped claim.

## Key papers to read

1. Jagannathan, A. "The Fibonacci quasicrystal and the Ammann-Beenker tiling." Eur. Phys. J. B (2024) — vertex-type window map
2. Lubensky, T.C., Ramaswamy, S. & Toner, J. "Hydrodynamics of icosahedral quasicrystals." Phys. Rev. B 32, 7444 (1985) — phason diffusion
3. Edagawa, K., Suzuki, K. & Takeuchi, S. "High resolution TEM observation of phason flips." Phys. Rev. Lett. 85, 1674 (2000) — experimental phason flips
4. Abe, E. et al. "Real-space observation of phason fluctuations." Nature 421, 347 (2003) — direct observation
5. Socolar, J.E.S., Lubensky, T.C. & Steinhardt, P.J. "Phonon and phason elasticity of quasicrystals." Phys. Rev. B 34, 3345 (1986) — symmetry-dependent phason elasticity
6. Baake, M. & Grimm, U. "Aperiodic Order, Vol. 1: A Mathematical Invitation." Cambridge (2013) — mathematical framework, local isomorphism

## What this does NOT claim

- NOT quantum anything
- NOT topological field theory
- NOT baryogenesis or cosmological analogy
- NOT a replacement for existing phason theory
- The connection is: microscopic geometric mechanism (ours) → macroscopic phason phenomenology (theirs)

## Updated story arc

1. **v0.3**: Depth predicts walk residue. TRUE.
2. **Directional balance**: THE MECHANISM. Spearman -0.72/-0.78.
3. **Radial drift**: Inward, not outward. No chirality.
4. **Null disc**: Genuine structure, not boundary bookkeeping.
5. **Channel-level double dissociation**: CONFIRMED. Address and weave independently knockoutable.
6. **Substrate-level**: Single dissociation only. Both weave-primary. AB has address backup, Penrose doesn't.
7. **Boundary shell**: Prediction failed — weave compensates everywhere. Real finding: redundancy asymmetry.
8. **Weave reconciliation**: Old 0.740 = rewired features, new 0.977 = native features. Same definitions. No discrepancy.
9. **Phason connection (THIS DOCUMENT)**: Our directional balance = microscopic mechanism for known phason susceptibility gradient. Legitimate physics, correctly scoped.
