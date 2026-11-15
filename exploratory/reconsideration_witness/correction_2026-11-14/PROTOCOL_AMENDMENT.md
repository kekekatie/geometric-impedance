# Distance-3 audit corrections: frozen before corrected outcomes

2026-11-14. Parent outcome `842fdc3d367a5701e35826ff40bbe36f1941a761`; original Component2 protocol `d22dbe91c467f6bfbc3648aaeda55ac97187043e`. Original source, report and handback stay unchanged. This amendment and a copy of the baseline handback are committed before executing the corrected runs. No edge-loss ensemble, distance5, later deadline or broader fault bound.

## Fixed scope and attribution

The same 130 ordinary-fault primitives, zero-to-two distinct ordinary faults, two true onsets1/2 and four freed-value pairs give68,128 contribution histories. Deadline4, five observed rounds0–4, bulk site(1,1), scored logicalZ_L, and decoder bound3 **per sector** remain fixed.

Five ordered runs isolate changes: (A) legacy set composition, p**w, literal MAP with zero-favouring ties, no frame; (B) XOR composition only; (C) B plus exact Bernoulli odds weights; (D) C plus normalized epsilon tie policy; (E) D plus the committed frame (corrected primary). A must reproduce the original hard decisions/weighted scores/counts; no result is silently replaced if this gate fails. All variants use explicit report routing and JSON round-trips; these refactors must not change the fixed-site legacy gate. Compare stages as conditional sequential effects, not order-independent causal contributions.

## Numerical/model corrections

1. Ordinary and free-erasure X/Z contributions at the same site/time compose by parity, matching the simulator's GF(2) primitive and inference signatures. History labels and their multiplicities are retained.
2. Corrected weights are `(p/(1-p))**w`, p=0.001. The omitted common `(1-p)**N` cancels within each bounded ensemble/marginal. Uniform onset and freed-value factors likewise cancel after normalization; each sector erasure value retains factor1/2. Evaluation is conditioned on at most2 ordinary faults; inference remains bounded at3 per sector. Do not call that truncation an unbounded optimal decoder.
3. For final posterior probabilities, classify a tie when `abs(P0-P1)<=1e-12`. Retain zero as the deterministic representative label for raw disagreement counts and direct/restart checks. Report both deterministic weighted correctness/agreement (comparable to baseline) and tie-aware expected scores. Expected truth score is1/2 on a tie. Expected reference agreement uses one common fair tie coin per history: both tied agree, exactly one tied agrees with probability1/2. This coupling preserves whole==thick. The committed frame itself is a deterministic bit with zero-favouring epsilon ties.

## Precise frame definition (previously unspecified operationally)

Commit after observing rounds0–3, before any report. For each sector, define the committed logical contribution as parity of its data faults in rounds0–2 along the corresponding logical support. Its frame is the ordinary-noise MAP estimate conditional on all that sector's detectors in rounds0–3, **without any erasure or report knowledge**. Use the exact independent Bernoulli prior for all52 ordinary primitives in this four-round prefix, not a bound with unsupported-prefix fallback. A finite GF(2) probability convolution over16 detector bits plus the committed logical bit computes this map. This fully specifies the formerly missing commitment and is a disclosed protocol clarification/change.

The frame is a lossy statistic of the observed prefix, **not oracle truth**. During report-aware inference, evaluate the same deterministic pre-report frame function on each candidate history's actual prefix (ordinary XOR free-erasure signature) and condition on the saved bit. Do not equate a saved MAP bit to the candidate's true committed logical. Two frame bits are kept by thin/diamond/whole. Thick already contains their input detector record and need not store or condition explicitly on them. The restored whole record must imply identical frame bits and reproduce thick.

## Retention, reports and restart

Prepare state using rounds0–3 only: prune0–2 to boundary, optional frame and site-agnostic fired archive; retain round3. Append round4 measurements before delivering the report. These are explicit ordered snapshot operations, not a claim to a full production streaming decoder. The thin state has no archive; archive arms have identical archive contents. Thick has the dense record. No state contains faults, true onset, truth or a preselected local diamond.

The report carries site, candidate-onset interval and deadline. Both the diamond query and erasure likelihood use it; memoization includes site/onset/model/frame. Reject unsupported deadlines and out-of-domain reports. Different sites/intervals are tested as small routing regressions, not as new scientific ensembles.

Every decision is checked against decoding of an actual JSON-encoded/decoded arm-specific state. For the primary run, write unique wire records per arm to separate JSONL files and decode each file in a new Python process with initially empty inference caches. No simulator record, expected result or other arm's payload is passed to that process. Compare all distinct restored states to parent predictions and retain multiplicities covering every history; also compare probabilities within1e-12. This tests file serialization and process restoration, not an operating-system security sandbox. Runtime JSONL files remain outside tracked results; record hashes, sizes, counts and child exits.

## Accounting and diagnosis

Report maximum and model-weighted mean **deadline snapshot payload** separately: thick40 detector bits; thin16 live+8 boundary (+2 frame for primary); archives add5 bits per fired coordinate (check3, round2). Counts exclude format/length/index overhead; separately measure actual compact JSON byte sizes including its metadata. Do not label either quantity a time-resolved process-memory peak. Both archive arms keep the same event record. Report stored event counts, reconstructed old values (diamond8, whole24), full detector count and boundary/frame constraints separately. No fixed claim of a larger-distance storage crossover follows.

Replay the historical corner example under the corrected primary and inspect **all16 omitted old detector values**, including zeros and same-star round0 values, one at a time. If a corrected diamond/reference disagreement exists, inspect one highest-weight example with deterministic enumeration-order tie breaking. Report reference agreement and truth separately; no universal outside-star or unique-witness claim from these examples.

## Validation and delivery

Regression tests: parity cancellation; report routing and onset likelihood/cache separation; shared-onset multiplication; frame convolution against a direct low-dimensional enumeration and its deterministic mapping; frame derived without report/future input; unsupported schema/report rejection; arm-specific round-trip; old values restored from the actual archive; cold processes; no changes to baseline files. Preserve failures and explain any harness fixes before rerunning. Commit source, amendment, compact regenerated results, logs and a concise before/after handback on the separate branch, publish without merge/force-push, and include exact replay commands and limitations.
