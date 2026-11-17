# Pass 2 independent audit

Pinned input: `f8e15d863a141404f152629d279612236264472f`. Audit protocol committed before execution as `d056d31`. All additions are on `audit/pass2-paired-2026-11-17`; frozen files are unchanged. Replay commands are in [README.md](README.md).

## What the two checks distinguish

```text
Raise decoder caps -> score thick, thin AND diamond on each identical history
                   -> compare paired benefits, separately within each panel

History A: two ordinary faults, loss value 0 -> identical 120 detector bits
History B: two ordinary faults, loss value 1 -> identical 120 detector bits
Opposite sector truths; same decoder output; a 50/50 posterior is NOT required.
```

## Cap sensitivity must be measured by paired benefit

The first 250 sorted triples are **diagnostic**, not a representative second sample: 194 begin with primitive 0 and 56 with primitive 1 (respectively X and Z at data (0,0), round 0). They produce 2,000 histories; the separately scored near-loss weight-one probes produce 880. The original sample and cap-panel hashes are verified.

At (3,3), the diagnostic weight-three margins are **0.30 percentage points thick-minus-thin** and **0.05 points diamond-minus-thin**. Raising only the frame cap to (4,3) changes **six thin labels and five diamond labels**, all wrong-to-right, while thick changes none. Both margins become **zero**. The changes span seven distinct histories. Thus the assertion that the archive comparison is robust because thick did not move is **not supported**.

All seven label-change histories had an absent X-sector prefix at frame cap 3 and a changed saved frame at cap 4. Across the full cap panel, prefix absence changes from **128 to 0**, and 112 saved frames change. The original claim that fallback zeros are “not decision-relevant” is too broad: thin and diamond decisions do change on those histories. The experiment changes both the observed-frame map and candidate-frame filter together, so it does not isolate their individual causal contributions.

See [TABLE.md](TABLE.md) for all completed cap settings, [caps_summary.json](results/caps_summary.json) for stratified counts and paired changes, and [decision_changes.json](results/decision_changes.json) for replayable histories. The original protocol's word “materially” has no numerical threshold. The audit predeclares a conservative trigger: run (4,4) if both individual cap increases change either paired mean in either component by any nonzero amount. This is a disclosed operationalization of the original paired question, not the old thick-only label-flip test.

Raising inference alone to (3,4) flips one thick/whole decision from right to wrong (history 785); thin and diamond labels do not change. Both separate cap increases therefore change a paired mean, and **the conservative (4,4) trigger fires**. At (4,4), the six thin and five diamond improvements remain, alongside the one thick loss. No arm has a tie on this diagnostic panel at any of the four settings.

| Caps (frame, inference) | Weight-three thick − thin (pp) | Weight-three diamond − thin (pp) | Near-loss weight-one thick − thin (pp) | Near-loss weight-one diamond − thin (pp) |
|---|---:|---:|---:|---:|
| (3,3) | 0.30 | 0.05 | 0 | 0 |
| (4,3) | 0 | 0 | 0 | 0 |
| (3,4) | 0.25 | 0.05 | 0 | 0 |
| (4,4) | −0.05 | 0 | 0 | 0 |

These are paired half-credit truth margins, not reference-agreement rates. At (4,4), thick/whole get 1,997 of the 2,000 weight-three histories right; thin/diamond get 1,998. All arms get all 880 near-loss probes right under every cap. The negative thick margin is one history in this biased diagnostic subset, not evidence of a population-level advantage for discarding information. It also is not a contradiction of optimal Bayesian decision theory: these are bounded decoders evaluated on a distinct diagnostic ensemble.

The original **thick-only** cap statistics reproduce exactly, including the 2,108 posterior shifts after nine-place rounding. The new report uses unrounded posteriors: 2,676 thick posterior shifts exceed 1e-12 at (3,4). That numerical-count difference comes from reporting precision, not a changed decoder. The original statement that these thick-only results establish robustness of the paired archive comparison must be replaced.

## Sentences the paper can use

* **Use:** “On the frozen diagnostic cap panel, the weight-three thick-minus-thin margin was sensitive to the frame bound: it changed from 0.30 percentage points at (3,3) to zero at (4,3), and to −0.05 points at (4,4). The corresponding diamond-minus-thin margins were 0.05, zero and zero. These are diagnostic-panel results, not population estimates.”
* **Use:** “At (3,3), diamond and thick agreed in decision on all 48,840 enumerated near-loss histories, although their posteriors differed on 41,196 histories.”
* **Use:** “The near-loss census contained no same-record, opposite-scored-truth group within its enumerated support. Separately constructed nonlocal seam pairs at supported onsets shared exact full detector records while having opposite scored truths; those examples did not produce decoder ties.” The last clause refers to the four X-fault pairs; conjugate pairs are separately documented.
* **Do not use:** “The archive advantage is robust to higher decoder caps,” “fallback prefixes are not decision-relevant,” “diamond exactly recovers thick inference,” or “the near-loss panel identifies the cause of global ties.”

The original full-sample (3,3) result is not rerun or invalidated by this audit. Its extrapolation to higher caps is unverified. Before claiming population-level cap robustness, freeze a representative sensitivity sample or rerun the primary sample at the selected higher caps; do not promote the first sorted 250 triples to that role.

## Validation and scope

All baseline cap-panel histories match the original scan and original table builder: **11,520 arm checks against each**, maximum posterior error zero. Raised-cap original-scan checks cover **39 histories at (4,3), 33 at (3,4), and 40 at (4,4)**, including every changed label/tie plus the fixed 32-history diagnostic selection; all match exactly. Separate checks cover 256 weight-two near-loss histories (1,024 arm outputs), all eight shared seam records (32 arm outputs), and 11,520 baseline outputs after the index performance fix, all with zero posterior error. The original thick-only report reproduces, and an independent CSV calculation reproduces every paired mean. Whole/thick posterior and label agreement holds throughout all cap panels.

Replay commands are in README.md. Per-history CSVs, changed-history specifications, aggregate counts and validation reports are committed. The only interrupted scientific attempt was the unfinished (3,4) run stopped for the performance-only index correction; the subsequent complete run and validation passed. A Windows console encoding error in the summary printer was also fixed; result files and numerical assertions had already completed, and the summary command was rerun successfully. No scientific outcomes were repaired, excluded or reweighted.

## Near-loss census: decision agreement reproduced, posterior identity rejected

All **48,840** frozen near-loss histories were replayed at (3,3). Diamond and thick have **zero label, tie-status or truth-credit disagreements**. Both score 48,728/48,840 = 0.9977067977; thin scores 48,704/48,840 = 0.9972153972. Thus both paired advantages over thin are **24/48,840 = 0.049140049 percentage points**. All four arms have zero ties on this census.

However, diamond and thick posteriors differ by more than 1e-12 on **41,196/48,840** histories, with maximum absolute p0 difference **0.1720894412**. Therefore “diamond exactly equals thick” must say **decision agreement on this particular census**, not identical posterior inference or full recovery of all archived information. Whole archive agrees with thick in labels and posteriors throughout.

Exact record tuples reproduce **39,511 record groups**, with **zero groups containing opposite scored truths within the enumerated near-loss census**. This is a statement about this panel's support. It does not establish the absence of any opposite-truth history outside that support, nor locate the cause of all ties in the global ensemble. The old code grouped integer hashes rather than exact tuples; this audit avoids the unnecessary collision assumption.

## Constructed seams: eight verified examples at supported onsets

The audit uses two deterministic minimum crossing representatives per fault sector, at onsets **1 and 2**, for eight pairs total. Each member has two ordinary faults. One member has erasure value 0 and the other 1, so their symmetric difference is the complete weight-five logical fault, including the loss site. Each pair has an **exactly identical full detector record** and opposite relevant simulated logical truth. Every arm returns the same result for both members of a pair.

Four X-fault pairs have opposite **scored Z-logical truth**. Four conjugate Z-fault pairs have opposite **X-logical truth**; the present decoder still scores Z-logical truth and is not a conjugate decoder. These should not be combined into eight opposite-*scored*-truth examples.

**None of the eight examples produces a tie in any arm.** For the four scored-truth examples, thick p0 is about 0.1112 or 0.6660, not 0.5. Two equal-weight witness histories alone need not exhaust or symmetrically balance the decoder's hypothesis mass. These witnesses demonstrate record ambiguity; they neither explain nor count the causes of global ensemble ties.

There are still **16 minimum weight-five crossing representatives per fault sector**, verified by simulator syndrome and relevant truth parity at both supported onsets. The old helper uses the opposite sector's logical/stabilizer family: all 16 old representatives per sector have nonzero syndrome when used as the indicated fault type. It also gives both members the same erasure value and uses unsupported onset 3. Moreover, the published `stress()` never invokes that helper, so the old stress JSON did not actually contain replayed seam pairs. The audit's corrected examples are separate additions, not retroactive evidence for the original report.

Evidence: [near.json](results/near.json), [seams.json](results/seams.json), [geometry validation](results/geometry_validation.json), [independent near/seam scan checks](results/near_validation.json).

## Source findings relevant to paper wording

Pinned source links:

* [`pass2.py:354–377`](https://github.com/kekekatie/geometric-impedance/blob/f8e15d863a141404f152629d279612236264472f/exploratory/reconsideration_witness/distance5_2026-11-16/src/pass2.py#L354-L377): the cap report retains only thick's tie/posterior and reports only thick's truth score. Thin/diamond paired margins cannot be recovered from the committed summary.
* [`pass2.py:438–440`](https://github.com/kekekatie/geometric-impedance/blob/f8e15d863a141404f152629d279612236264472f/exploratory/reconsideration_witness/distance5_2026-11-16/src/pass2.py#L438-L440): the implemented escalation tests thick label flips, replacing the protocol's paired-comparison criterion.
* [`nd_infer.py:151–174`](https://github.com/kekekatie/geometric-impedance/blob/f8e15d863a141404f152629d279612236264472f/exploratory/reconsideration_witness/distance5_2026-11-16/src/nd_infer.py#L151-L174): candidate frame is a function of the observed prefix. For thick, full detector conditioning already fixes that prefix; changing its frame map alone cannot alter the selected hypothesis set. Thick frame-cap invariance therefore cannot establish invariance of the thin/diamond comparisons.
* [`pass2.py:202–203`](https://github.com/kekekatie/geometric-impedance/blob/f8e15d863a141404f152629d279612236264472f/exploratory/reconsideration_witness/distance5_2026-11-16/src/pass2.py#L202-L203), [`264–269`](https://github.com/kekekatie/geometric-impedance/blob/f8e15d863a141404f152629d279612236264472f/exploratory/reconsideration_witness/distance5_2026-11-16/src/pass2.py#L264-L269), [`290–318`](https://github.com/kekekatie/geometric-impedance/blob/f8e15d863a141404f152629d279612236264472f/exploratory/reconsideration_witness/distance5_2026-11-16/src/pass2.py#L290-L318): old seam construction issues and its absence from the executed stress routine.
* [`pass2.py:114–123`](https://github.com/kekekatie/geometric-impedance/blob/f8e15d863a141404f152629d279612236264472f/exploratory/reconsideration_witness/distance5_2026-11-16/src/pass2.py#L114-L123): `grid_decomp.net` counts the signs of credit differences; it is not their half-credit-weighted mean. The primary report's 0.002735 net must not be substituted for its separately computed, correct 0.0023425 paired tie-aware margin. This audit does not rerun the full primary sample.

The claim that a same-record seam “needs weight-four ordinary support” must distinguish the **union/symmetric difference across two histories** from the weight of either history: these examples have ordinary weight two on each side. Also remove the original comparison of one label in 2,880 with the combined population margin: they concern different panels/estimands, and 1/2,880 is numerically larger than 3.68e-5, not smaller.
