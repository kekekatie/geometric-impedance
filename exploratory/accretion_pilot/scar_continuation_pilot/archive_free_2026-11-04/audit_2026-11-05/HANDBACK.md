# Handback for Katie and Astra — 2026-11-05

1. **What independently reproduced?**

   All eleven prescribed, correlated B-jam cases reach step 44 with positive placement progress at every scientific step. The retained-band worker agrees with the full-patch comparator in actual candidate enumeration, ordered placements/frontier, PRNG transitions and scar state. Newly spawned pre-scar restarts agree with both. Every actual worker placement passes the separate full-history evaluator; endpoint decorated-star and triangle-overlap checks pass. The original focused tests pass. These are executed results, with replay caches reused for repeated reports.

2. **Did actual deletion and pre-scar restart survive scrutiny?**

   Yes. The restart is before the first scar-tolerant batch. Its geometry, ordered true frontier, PRNG and empty initial scar set align with the frozen checkpoint. After pruning, the constructor's tile/edge/vertex indexes contain the retained geometry, with boundary owners retained and cavity edges excluded from the declared construction frontier. It needs the **band plus true-frontier metadata, PRNG state and persistent scar labels**. A separate process is not a filesystem sandbox: an unrelated historical summary is loaded by a transitive import, but source inspection and a focused control show it is unnecessary for the tested constructor decisions.

3. **Did any scientific outcome change?**

   No. Raw jam/final coordinates and tile order match the pinned exports, supporting reuse of the unchanged endpoint readout inputs. The original 528-window totals are therefore reused, not rescanned: 111 B, 64 ambiguous, 353 incompatible, zero A and zero reconstruction failures. Positive-area B selection remains conditional; some selected subsets have zero-area closed-A intersections. Endpoint readout does not demonstrate continuous memory transport.

4. **What defects or reporting corrections remain?**

   Two small defects are fixed on the audit branch. An arrest exactly at step 44 could incorrectly set `horizon_complete=True`; the flag now excludes arrest. The endpoint diagnostic helper retained deleted tiles in its uncleared transient additions list; it now clears that list before pruning, without changing its returned band. The main verifier and spawned constructor already cleared it. None of the scientific runs arrested or changed outcome.

   Reporting should say **shared-engine legality validation plus separate convex-clipping overlap checks**, distinguish partial from complete vertex-star checks, and distinguish actual decision inputs from incidental import-time reads. Band width is measured from the entire declared frontier, blocked components included. Current blocked edges and cumulative labels differ in the w5/w21 family. The eleven labels are correlated; neither state hashes nor a geometric grouping count establishes independent trials.

5. **What exact, bounded claim can Katie safely use?**

   > On the eleven recorded correlated B-jam cases, a constructor initialized immediately before the first scar-tolerant batch, retaining the radius-2 boundary band together with the declared true-frontier metadata, PRNG state and persistent scar labels, reproduced the audited full-patch continuation through step 44. It made positive placement progress at every tested step without using deleted interior geometry for its decisions. The tested placement, frontier, PRNG and scar trajectories agreed, and legality/endpoint checks passed at the stated numerical tolerances.

   This establishes finite continuation from these exported jam states. It does not establish construction from the original seed, indefinite growth, an unaugmented tile-only constructor, a band close only to the advancing outer perimeter, or a universally reliable local memory reader.

`AUDIT_REPORT.md` ranks the findings. `REPRODUCTION.md` records commands, dependency identities, reused-input provenance and comparison limits. `results/` contains the separate checks and defect fixtures; `reproduced/` contains regenerated original reports. Branch: `audit/archive-free-scar-2026-11-05`. The delivery receipt gives the exact published commit. No merge or force-push; the bounded audit stops here.
