# Distance-3 bulk corrections: before and after

**Completed: the corrected primary reduces thin/reference disagreements from 5,679 to 3,433 and diamond/reference disagreements from 514 to 341. Whole archive still matches thick exactly.** The original outcome and source at `842fdc3d367a5701e35826ff40bbe36f1941a761` remain unchanged; all new work is in this additive correction directory on `fix/distance3-bulk-audit-2026-11-14`.

The model changes were documented and committed **before running** in local protocol commit `fa18eb240880e68f76d3daa32361ea7758ff517e` (2026-11-14). The five-stage experiment and cold-restoration checks completed that day; the final diagnostics and handback were completed on 2026-11-16 after the usage interruption. See [the amendment](PROTOCOL_AMENDMENT.md). Its precise frame definition and tie convention are disclosed protocol changes, not silent repairs to the historical result.

## Short comparison

Each stage uses its own same-deadline thick reference. The scored logical, bulk site, five observed rounds, deadline 4, 68,128 contribution histories and fault bounds are unchanged. “Before” uses the published legacy model; “after” includes all corrections and the two-bit committed frame. Correctness below uses deterministic representative labels, including zero on ties, so it is directly comparable with the old scoring convention. Payloads are idealized **deadline** bits, not temporal memory peaks.

| Arm | Raw reference disagreements: before → after | Weighted hard correctness: before → after | Max payload bits: before → after |
|---|---:|---:|---:|
| thick | 0 → 0 | 99.590374% → 99.590134% | 40 → 40 |
| thin | 5,679 → 3,433 | 99.202467% → 99.300334% | 24 → 26 |
| diamond | 514 → 341 | 99.588024% → 99.589089% | 64 → 66 |
| whole | 0 → 0 | 99.590374% → 99.590134% | 64 → 66 |

| Stage | Thin disagreements | Diamond disagreements | Thick correctness | Diamond correctness | Mean archive payload, bits |
|---|---:|---:|---:|---:|---:|
| A_legacy | 5,679 | 514 | 99.590374% | 99.588024% | 34.444797 |
| B_xor | 5,679 | 514 | 99.590549% | 99.588200% | 34.434967 |
| C_prior | 5,685 | 512 | 99.590134% | 99.587780% | 34.435395 |
| D_ties | 5,683 | 510 | 99.590134% | 99.587780% | 34.435395 |
| E_frame | 3,433 | 341 | 99.590134% | 99.589089% | 36.435395 |

The ladder isolates conditional sequential effects, not a factorial decomposition. In particular, changing a prior or tie policy can change the reference itself; a disagreement-count delta is not automatically a truth-accuracy delta.

## Which fixes changed the numbers?

| Change | Measured effect in this sequence |
|---|---|
| XOR composition of ordinary and erasure contributions | Raw disagreements remain 5,679/514, but thick and diamond weighted correctness improve slightly. Mean archive payload changes 34.444797→34.434967 bits; maximum stays 64. The fixed bulk site's overlap does not directly alter the scored logical parity because it is outside that logical support, but it changes observed syndromes and decisions. |
| Exact Bernoulli odds within the bounded model | Thin/diamond raw disagreements become 5,685/512; weights and some decisions change. Mean archive payload becomes 34.435395 bits. |
| Normalized epsilon tie handling | Representative-label disagreements become 5,683/510. Deterministic weighted correctness is unchanged at the precision shown; expected tie-aware agreement is separately recorded. |
| Restoring the report-blind committed frame | Thin/diamond disagreements become 3,433/341. Primary thin correctness is 99.300334%; diamond 99.589089%. Two additional retained bits raise thin 24→26 and archive 64→66 maximum payload bits. The archive event record is unchanged by adding the frame: its mean payload rises by exactly 2 bits to 36.435395. |

The primary's 341 diamond/reference disagreements split **123 diamond-right / 218 reference-right** against simulator truth. Reference agreement remains distinct from correctness. The corrected diamond's hard weighted reference agreement is0.9999624864; its expected tie-aware agreement is0.9999628165. Tie-aware truth scores happen to equal hard truth scores in aggregate here; that equality is observed, not assumed.

## Structural fixes and wording corrections

- **Report routing is implemented:** site and onset interval drive both query geometry and erasure hypotheses; memoization keys include site/onset and the model conditioning. Alternative-site/onset regressions pass. They are routing tests, not an edge-loss ensemble. In the original fixed-site setting, the refactor reproduces every original label and posterior exactly, so routing/schema refactors alone do not explain the numerical changes above.
- **Actual serialization and cold restoration replace the old claim:** arm-specific states are JSON-encoded, restored and checked on every history. For the primary, each arm's distinct saved states are written to a file and decoded by its own fresh Python process. Thin has no archive field. The worker reads no expected-answer file or other arm's state file. This is an executed file/process boundary, not an OS security sandbox.
- **Whole archive reconstructs 24 old detector values**, including quiet zeros; diamond reconstructs 8. Those numbers are now separate from the count of stored fired-event coordinates. Neither correction changes the fixed-site legacy decisions.
- **“Peak” becomes “maximum deadline snapshot payload.”** No temporal peak was measured. The two archive arms share identical event contents. The primary weighted mean is 36.435395 bits, versus maximum 66; thick is 40. Thus the mean is below thick while the maximum is above it, even at d=3. No distance5 crossover claim is made.
- **Actual state-encoding sizes are reported separately:** primary compact JSON state maxima are 387 bytes (thick),236 (thin),299 (diamond),297 (whole); weighted means are 387,236,263.754247 and261.754247 bytes. The two-byte difference between archive arms is just the length of the arm name in this diagnostic format. These sizes include state metadata and JSON overhead, but exclude separately supplied report transport, audit-record envelopes, decoder workspace and Python object overhead. They are not a compact production-memory benchmark.
- **The example is scoped correctly:** under the corrected primary, the historical corner still has truth 0, diamond 0 and reference 1. Adding either `Z-stab 0 @ round 0 =1` or the omitted quiet value `Z-stab 0 @ round 2 =0` alone flips the diamond to the reference's wrong answer. All 16 omitted values were checked individually for this example and the highest-weight corrected disagreement (the same example). No unique-witness or universal outside-star claim is retained.

## Frame definition and validation

The saved frame is a two-bit lossy statistic of the observed prefix through round 3, computed without a report or erasure hypothesis. For each sector it is the ordinary-noise MAP estimate of the logical contribution from rounds 0–2. A finite 17-bit GF(2) probability convolution computes the full independent-Bernoulli prefix map for 52 ordinary primitives. During report-aware inference, a candidate is filtered by whether **the same pre-report map applied to its observed prefix** yields the saved frame. The stored bit is not equated with the candidate's true logical contribution. Tests include indistinguishable prefixes with different true logical values, confirming that the saved frame is not an oracle.

This resolves an underspecified/missing operation in the original implementation. The full-Bernoulli precommit map and the still-bounded report-aware decoder have different, explicitly documented bounds. Final ties use normalized epsilon 1e-12; raw counts use zero as representative, while expected scores use a common fair tie coin across arms as specified before the run. These details should be carried explicitly into any new protocol rather than assumed to follow automatically from the historical run.

## Executed checks

- Five fixed variants × 68,128 histories; **1,362,560 direct-versus-JSON-round-trip arm checks**, no mismatches.
- Separate comparison to the untouched original decoder: **272,512 arm comparisons**, zero label mismatches and **zero posterior differences**.
- Whole versus thick: zero label disagreements in every stage; posterior differences within1e-12.
- Actual archive-to-dense evidence reconstruction: zero mismatches; identical archive contents across retaining arms.
- Four fresh-process restorations cover all68,128 histories per arm via distinct-state multiplicities: **29,427 thick,5,854 thin,29,427 diamond,29,427 whole** states. All child exits are 0 and restored probabilities match within1e-12. Input hashes, byte sizes, state counts and cold-process commands are recorded.
- Focused parity, frame-convolution, report-routing, schema, deadline, shared-onset multiplication and tie tests pass. No scientific failure or tolerance relaxation was needed.

See [verification](results/verification.json), [cold checks](results/cold_restart.json), [per-history legacy check](results/legacy_per_history.json), [examples](results/examples.json), and [execution log](logs/run-execution.json). Raw JSONL runtime files remain outside Git and are regenerated by the replay.

## Replay and the edge-loss decision

From this directory:

```sh
python3 src/tests.py
python3 src/legacy_regression.py
python3 src/run.py all
python3 src/diagnose.py
python3 src/summarize.py
```

The core experiment/restart command is `python3 src/run.py all`; the other commands reproduce its regression evidence and handback tables. See [README](README.md) for environment, external-cache configuration and interruption recovery.

For an edge-loss run, carry forward parity composition, explicit report routing, actual arm-specific restoration, the separated truth/reference scores, and honest payload/query accounting. Choose and freeze the frame and tie definitions explicitly; this primary supplies one tested definition, not proof that it is the only appropriate one. The diamond remains highly reference-consistent but not exact. Nothing here establishes distance scaling, minimum memory, a production streaming peak, or performance under a circuit-level physical-loss model. No edge-loss or distance5 scientific ensemble has been run.
