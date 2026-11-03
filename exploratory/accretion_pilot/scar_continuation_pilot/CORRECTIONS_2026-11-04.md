# Corrections & interpretation note — 2026-11-04

*Integrates the independent audit `audit/scar-continuation-2026-11-03`
(commit `3dc43ea844613f2b6e50647f2ffda14616281f68`, directory
`audit_2026-11-03/`) into the scar-continuation pilot. The original
`HANDBACK.md` is preserved verbatim as a dated historical document; read it
through this note. No frozen engine, frozen reader, matching rule, reader
threshold, or historical output was changed.*

**What survived the audit.** The full-patch scar-tolerant scheduler reproduces
exactly: all eleven recorded runs make legal progress to step 44, pre-jam
geometry and PRNG states match the frozen baseline bit-for-bit, all 7,325
additions pass `Patch.legal`, final vertex stars and overlaps are clean, and the
reader numerics agree below `6.7e-15`. The whole-band reader is
`empty_incompatible` at every endpoint; the originally-reported subsets select B
under the frozen positive-area reader.

**What the audit corrected (carried forward here).**

1. **"Selects B" is not "excludes A".** The frozen reader is a *positive-area*
   rule (hypothesis compatible iff intersection area `> 1e-9`; unique selection iff
   the subset's own area `> 1e-12`). An independent box-free LP on the same closed
   A-intersection constraints finds **12 of 22** headline endpoint selections
   retain a numerically feasible **zero-area** intersection with A (6 points, 6
   segments; point witnesses violate normalized constraints by `≤ 2.23e-16`). So
   the correct wording is *"the positive-area reader selects B"*; "overlaps B but
   not A" / "A is excluded" is too strong for those cases. (Numerical, not a
   symbolic certificate.)

2. **"Maximal arc" → "largest compatible connected subset found by the specified
   bounded scan."** The original scan picked the greatest tile count with area
   `> 1e-9` at one fixed centre; it did not search all subsets. The pilot's own
   saved secondary windows already exceed its headline (w7: 151 vs 100; w5: 222 vs
   90). "Contiguous arc" means *an angular-centroid selection reduced to its
   largest full-edge-connected component*, not a proven single interval.

3. **The w7 "32% → 50% increase" is confounded** — Phase 1 and Phase 3 used
   *different* scan centres (jam-notch opposite vs final-scar-centroid opposite)
   and resolutions. Holding either centre/resolution fixed gives a *decreasing*
   band fraction (e.g. 31.75% → 21–22% at the jam-notch centre), though absolute
   tile counts can grow. **Withdrawn:** "the readable fraction grows," "B stays
   readable the whole way," and "one trace is carried continuously." No readout at
   every intervening step was tested.

4. **Cumulative scar labels ≠ currently-blocked frontier edges.** New blocked
   edges created by a batch are not labelled until the next scan, and at step 44 a
   run can finish with unlabelled blocked edges. The w5/w21 family has **2 labels
   but 5 current blocked edges in 2 components spanning 2.655 rad** — not the tiny
   one-component notch the label-only figure implied. (In these runs no labelled
   edge ever disappeared or became extendable; permanent skipping is a policy, not
   a proof of persistent obstruction.)

5. **"611 vs 589" use different baselines.** w7 starts the jam at 417 full tiles,
   the first scar batch adds 22 (→439), and step 44 has 1,028: `1028−417 = 611`
   from the frozen jam, `1028−439 = 589` after the first batch. Corrected tables
   use the **frozen-jam baseline** and show the first batch separately.

6. **Choice-tile fate corrected.** B is absent from every selected subset. At the
   jam it still sits elsewhere in the band only for **w15/w19/w28-s0** (departing
   at step 41); the other **eight** cases lost it *before* scar continuation (w7 at
   17, w5/w21 at 29, w19-s1/w28-s1/w29-s1 at 30). At the final state B is absent
   from every band **but present in every full construction archive**. "All depart
   during continuation" and "already absent from every jam band" were both wrong.

7. **Correlated dataset.** The eleven records contain two duplicate trajectory
   pairs (the two w7 streams; the two w21 streams) → **nine distinguishable full
   trajectories, eight distinct jam geometries**, not eleven independent trials.
   Counts across them are not an independent-trial statistic.

8. **Endpoint readout ≠ continuously transported memory.** Selecting B at an
   endpoint is conditional, selected-subset readout. It is not a universally
   reliable local reader (Astra's precommitted 528-window grid: 111 B, 64
   ambiguous, 353 reader-incompatible, **0 A**; 417/528 windows give no unique B),
   and it does not establish a trace carried continuously through the steps.

**Scope reminder.** The original Phase-2 runs **retained the full construction
archive** — growth decisions could see the deleted interior. That is *not*
archive-free construction. Whether a worker retaining **only** the specified band
can continue legally without the deleted interior is a separate, preregistered
question, pursued in [`archive_free_2026-11-04/`](archive_free_2026-11-04/) (this
note's companion experiment). The audit verified the full-patch baseline and
"exposed precisely what was not tested"; it does not predict the archive-free
outcome.
