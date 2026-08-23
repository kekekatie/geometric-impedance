# Result: the intrinsic transition-graph asymmetry is real but generic (H1a)

Outcome of the sealed test `PREREG_intrinsic_drift.md`. Scored first, interpreted second.

## Verdict

**The state-space geometry does carry structure beyond immediate mobility — but it is a
property of rhombus tilings in general, not of quasiperiodic order.** The exciting
version ("quasiperiodic geometry supplies a special directional tendency") is falsified
at the tested horizons. H1a is supported; H1b and H2 are rejected.

## The ladder, climbed and where it broke

1. **Branch asymmetry exists** — yes. Continuation volume varies across a state's moves.
2. **Not trivially degree** — yes, but only at deeper local horizon. The whole-patch r=2
   test found `corr(d, Omega_2) ~ 1.00`: one-step mobility and short-horizon volume are
   nearly the same quantity. Local horizon r>=3 was needed to see anything.
3. **Deeper continuation volume carries structure beyond degree** — **yes, and robustly.**
   The residual of log-Omega_r after removing local degree is 0 at r=1 (by construction),
   grows with r, and is present at every local radius R once disks are sampled inside the
   bulk (extent 9). The erratic R-dependence seen at extent 6 was finite-size/boundary
   contamination, as predicted; in the bulk the pattern is smooth and monotone in r. This
   is the real methodological finding.
4. **Quasiperiodic-specific (beyond matched scramble)** — **NO.** `control_scramble.py`,
   5 seeds, tracks residual structure from the quasiperiodic point (0.03 flips/vertex) to
   the random-tiling bulk (1.5 flips/vertex) at R=2.0, r=3. It does not decay from QC to
   scramble; it is flat or rising:

   | flips/vtx | silver | golden | platinum |
   |---|---|---|---|
   | 0.03 (near QC) | 0.072 ± .004 | 0.092 ± .009 | 0.098 ± .010 |
   | 0.15 | 0.089 ± .004 | 0.099 ± .013 | 0.096 ± .006 |
   | 0.50 | 0.105 ± .009 | 0.104 ± .007 | 0.136 ± .011 |
   | 1.50 (random tiling) | 0.098 ± .005 | 0.128 ± .023 | 0.101 ± .019 |

   near-QC minus saturated: silver **−0.026 ± .006**, golden **−0.036 ± .025**, platinum
   **−0.002 ± .021**. No family shows QC-elevation; silver is significantly *lower* near
   the QC. The residual structure lives in the random-tiling ensemble just as much as at
   the quasiperiodic point.
5. **Field-specific** — **NO.** With rung 4 dead this is moot; and the earlier
   silver<golden<platinum hint did not survive (saturated values converge, .098/.128/.101).
   The family/platinum ordering was finite-size and small-scale noise, as suspected.
6. **Branch exploitation** — not measured. With the beyond-degree structure shown generic,
   exploitation (if any) would be generic too, so it cannot rescue the quasiperiodic story
   and was not pursued.

## Scoring the pre-registration

Pre-registered credences were H0 0.35 / H1a 0.20 / H1b 0.25 / H2 0.20. **Outcome: H1a**,
the least-weighted live option — recorded as a miss on my part (I under-weighted "real but
generic"). P3 (structure beyond degree) held; **P2/P5 failed** (does not survive the
matched scramble; not field-specific); P1/P4/P6 (g_phi drift, detailed-balance current,
exploitation) were not reached. The g_phi coordinate was deprioritised after
`phason_strain.py` showed a large finite-size floor; the target-free continuation-volume
route was cleaner and is what was run.

## What survives, what is retired

**Survives.** A genuine methodological result: local configuration-space topology carries
structure beyond one-step mobility, deepening with horizon — and the machinery to measure
it (continuation_volume.py, the bulk sweep, the seeded scramble control). Also the
now-standard discipline: sensitivity gate before controls, controls before interpretation.

**Retired.** The quasiperiodic-specific and field-specific versions of the entropic-geometry
idea, and with them the platinum/family ordering. "More future behind some doors" is true
of rhombus tilings generally; it is not special to the cyclotomic fields.

## Where this sits in the arc

Three clean nulls now stand together on one theme — Branch A (no dynamic recovery), the
history test (mobility erases history), and this (no quasiperiodic-specific state-space
tendency). Together they say: **under energy-free phason dynamics, these substrates show no
quasiperiodic-specific recovery, memory, or continuation-volume asymmetry.** This coheres
with the project's earlier Stage D verdict — the geometry's special number reaches into
*static* structure and memory-in-the-pattern, but **not into the free dynamics.** The
boundary is now cross-validated from two independent directions.

## Open threads (for the crew)

- **Branch B (energetics)** — the one remaining dynamics option, still gated, and inherently
  question-begging (we would impose the restoring force). Lower priority given the above.
- **The static side** — `PREREG_degree_controlled_address.md` (drafted, never run) is where
  quasiperiodicity actually showed up historically. Returning there measures the honest,
  degree-controlled static address channel — the signal, rather than another corner where
  it is absent.
