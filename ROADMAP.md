# Roadmap — the address/reader programme, next checks

*A durable, ordered to-do list so any instance or model can pick up where we are, and so a
refreshed Karen has it to hand. From GPT's outline (2026-08-26), with Claude's small additions
marked. **We reserve the right to stray** — this is a compass, not a cage. Status tags:
TODO · DOING · DONE · PARKED.*

## Where the "address" decomposition stands

Confined-state role currently decomposes (see `substrates/RESULTS_ADDRESS_SPLIT.md`) into:
- **pointwise / radial depth** — largest single term, family-dependent (silver 0.68, golden
  0.45, platinum 0.21);
- **neighbourhood / relational address organisation** — large, non-radial, survives fixing the
  exact fine vertex type (+0.22 / +0.34 / +0.53); the *same* multiscale features the coherent
  wave reads in transport;
- **angular position** — ≈0 (pointwise window field is radially symmetric).

## Ordered checks

1. **[DONE] Nonlinear residualization cross-check** (`substrates/RESULTS_RESIDUALIZE.md`).
   Result (golden): the plain +0.027 increment reproduces, but the **M3-orthogonal residual of
   the address adds only +0.004** — the address's transport value is in the part *shared with*
   the physical descriptors (a multiscale re-encoding), not an orthogonal hidden channel.
   Consistent with the shuffle-kill and M3far-survival. Tempers the story toward the humble
   language (rule 6). Caveat: nonlinear residualization is lossy, so +0.004 is a lower bound.

2. **[TODO] Progressive physical-radius ladder.** Instead of one M3-far, enrich the physical
   baseline r = 2 → 4 → 8 → 12 and watch the address increment. Fades ⇒ address is a brilliant
   compression of long-range geometry; survives stubbornly ⇒ more interesting.

3. **[TODO] Verify the radial-vs-neighbourhood split across families AND observables.** Done for
   confined weight on all three families (`RESULTS_ADDRESS_SPLIT.md`). *Claude's addition:* also
   run it for the observable the wave actually reads — **mid-band LDOS** — and for IPR, not just
   confined-state weight. Quantify radial / neighbourhood / residual-fine each time.

4. **[TODO] Has the old "weave" idea returned in a better form?** Not a mystical second
   substance, but perhaps **weave = multiscale organisation of addresses across a
   neighbourhood.** Compare the old weave metrics against the new neighbourhood-address features.
   *Claude's flag:* the old weave metrics predate this session — dig them out of the repo history
   first, so the comparison is fair, not hand-waved.

5. **[TODO — Claude says do this early, it's cheap and the most interpretive] Ablate the
   neighbourhood-address features group by group** (shell-averaged perp vs its variance vs the
   gradient vs hull depth) and see which actually carry the transport increment. Tells us *what
   specifically* the address is doing.

## Language discipline (standing rules)

6. **[RULE] Hold off on "perpendicular space is physical."** Safe claim: *perpendicular-space
   descriptors capture transport-relevant multiscale structure not exhausted by the tested
   physical descriptors.* Stronger ontology waits.

7. **[RULE] Keep the coherence result precise.** *Address sensitivity lives in the stationary
   spectral structure of the coherent tight-binding Hamiltonian and does not require
   inter-eigenstate dynamical phase interference.* Do NOT slide back to "phase-memory of the
   journey" as the mechanism.

## Parked / optional

8. **[PARKED, optional-later] Haken–Strobl dephasing sweep.** Now a robustness / mechanism-shape
   test: how does the address-sensitive spectral organisation die as quantum coherence is
   progressively destroyed? Not urgent; potentially lovely (and the home of Karen's "compounding,
   depending on circumstances" intuition).

9. **[PARKED] Holonomy / time / motion — kept separate.** Later, revisit the old holonomy-like
   results and ask whether they provide path-dependent phase or momentum-like structure. Do NOT
   glue them to time yet.

10. **[PARKED, banked as a null] The defect result.** Lesson: clean single-valued lift
    constructions do not cheaply generate localized Burgers-charged objects. Don't force a "thing
    made of map" if the grammar isn't giving one. (`substrates/RESULTS_GATE0_DEFECT.md`.)

11. **[TODO — only after 1–5 settle] The proper synthesis.** Organise the project around:
    carrier · reader · coupling · pointwise vs relational address · static spectral structure vs
    dynamics · what survives confound control.

## Ultra-short order of operations (GPT)

1. residualization → 2. radius ladder → 3. verify radial-vs-neighbourhood split across
families/observables → 4. test whether neighbourhood-address = mature "weave" → 5. only then
decide: dephasing sweep, or write the synthesis.

*(Claude would slot the cheap ablation, #5, in alongside 1–3 rather than after — it is the most
interpretive and costs little.)*
