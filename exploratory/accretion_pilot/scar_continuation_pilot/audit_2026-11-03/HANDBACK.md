1. **What independently reproduced?**

   All eleven recorded full-patch scar runs make legal progress to step 44. Pre-jam geometry and PRNG states match the frozen baseline exactly. Every original whole-band reader is `empty_incompatible`, and every original headline subset selects B under the unchanged positive-area reader. Growth bookkeeping reproduces exactly; readout numeric differences are below `6.7e-15`. The stronger addition, decorated-star and overlap checks pass.

2. **Which headline claims changed?**

   - **B selection is not always mathematical exclusion of A.** Twelve of 22 original endpoint selections retain a numerically feasible zero-area intersection with A (six points, six segments).
   - **“Maximal arc” becomes “largest compatible connected subset found in the specified scan.”** The pilot itself already reports larger B-reading subsets: w7 151 versus headline 100, w5 222 versus 90.
   - **The w7 32%→50% increase is confounded by moving the scan centre.** Keeping either original centre and resolution fixed gives a lower final fraction, though absolute subset size can grow.
   - **Accumulated scars miss new final blocked sites.** The w5/w21 family has two labels but five currently blocked edges, spread over 2.655 radians, not a tiny one-component notch.
   - **611 and 589 count from different baselines.** W7 adds 22 in the first scar step and 589 later: 611 from the frozen jam. Corrected tables use that common baseline.
   - Eight B tiles left the band before scar continuation; three leave during it. All remain in the full construction archive. Eleven records include two duplicate trajectory pairs; nine distinguishable full trajectories are not nine proven independent trials.

3. **What can we safely say about continuation and historical discrimination?**

   The full-patch scar scheduler continues legally to the finite horizon despite whole-band projection-window incompatibility. Some geometry-selected boundary subsets discriminate B under the frozen positive-area rule without containing the B tile. The precommitted 528-window grid yields 111 B selections, 64 ambiguities, 353 reader-incompatible outcomes, zero A selections and zero reconstruction failures. The largest compatible subset found by that grid selects B at both endpoints in each case. This is conditional, selected-subset readout—not a universally reliable local reader, nor evidence of a continuously transported trace.

4. **What remains unresolved?**

   Exact symbolic certification of boundary intersections; performance outside the bounded scans and correlated all-B dataset; readout at every intervening step; indefinite growth; and construction without the archived interior. Gauge controls pass, including when the reference vertex is absent, but the reader still requires declared historical origin, layer convention, windows and birth hypotheses. The historical files do not serialize full endpoint geometries, so only their saved observables can be compared directly.

5. **Is a separate archive-free continuation experiment now justified?**

   **Yes—as a separate, carefully specified question, not as a result already demonstrated.** The audited full-patch baseline is suitable for a controlled comparison. A future experiment would need its own retained-state and frontier rules and must avoid using deleted interior geometry in construction. Nothing of that kind was implemented here, and this audit does not predict its outcome.

For Katie and Astra: `AUDIT_REPORT.md` ranks findings and references the code; `REPRODUCTION.md` records commits, environment, commands and limits. `results/` contains every declared sensitivity outcome and corrected tables. The two corrected figures distinguish construction archive, analysed band, selected subset, cumulative labels and current blocked edges. Historical files are preserved. Branch: `audit/scar-continuation-2026-11-03`; exact published commit is in the delivery receipt. The audit stops here.
