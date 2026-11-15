# Distance-3 edge-loss run: frozen before outcomes

2026-11-15. Built on Astra's corrected **E_frame** baseline at
`09a79c1d8d082702c93e1cd6b9f4a45d3df4d729` (branch `fix/distance3-bulk-audit-2026-11-14`),
whose protocol amendment is `fa18eb2` and whose bulk E_frame result is
(thin 3433, diamond 341, whole 0; diamond split 123 right / 218 reference-right),
reproduced byte-for-byte in this environment before this amendment was written.

This amendment is committed **before** the edge harness is run. Single distance-3
**edge** site only. No boundary-corner site, no distance-5, no later deadline, no
broader fault bound.

## The one change

Relocate the loss from the bulk site **(1,1)** to the non-corner **edge site (1,2)**.
From the pinned layout, (1,2)'s star is three checks — **Z-stab 2, X-stabs 3 and 6**
— versus the bulk site's four. Like the bulk site, (1,2) lies outside both chosen
logical supports (`Z_L` = {(0,0),(1,0),(2,0)}, `X_L` = {(0,0),(0,1),(0,2)}), so the
scored logical convention (`Z_L`, X-errors / Z-stabs) is unchanged. The local query
therefore drops from **eight readings to six**:
- X-sector (Z-stabs): Z-stab 2 × onsets {1,2} = **2** readings;
- Z-sector (X-stabs): X-stabs 3, 6 × onsets {1,2} = **4** readings.

## Everything carried forward unchanged (from E_frame)

Astra's `correction_2026-11-14/src/model.py` is **reused unchanged** — it is already
report-routed, so the only input that differs is the report's site. Carried forward:
the same 130 ordinary-fault primitives, 0–2 distinct ordinary faults, two true onsets
{1,2}, four freed-value pairs → **68,128 contribution histories** (with the loss
relocated to (1,2)); XOR parity composition of ordinary and free-erasure contributions;
exact Bernoulli-odds weights `(p/(1-p))^w`, p=1e-3; normalized ε=1e-12 ties with
zero-favouring representative labels and tie-aware expected scores (shared fair coin
per history, preserving whole==thick); the **report-blind two-bit committed MAP frame**
(exact 17-bit Bernoulli convolution, a lossy statistic, not an oracle); five observed
rounds 0–4; deadline 4; decoder bound 3 **per sector**; shared-onset inference
(condition on the shared candidate onset, then combine the two sectors' likelihoods,
then average over onset).

## Arms, retention, report, restart (unchanged structure)

Four arms: **thick, thin alone, thin+diamond (local checks), thin+whole archive.** The
pre-report state is built from rounds 0–3 only (prune 0–2 to boundary + the two frame
bits + the **site-agnostic** fired archive; retain round 3), then round 4 is appended,
then the report is delivered. The report (site (1,2), onsets {1,2}, deadline 4) drives
**both** the diamond query geometry **and** the erasure hypotheses. The two archive arms
keep **identical** event records; they differ only in what the report lets them read.
Every decision is checked against decoding of an actual JSON-encoded/decoded
arm-specific state; the primary arms are additionally restored by **fresh Python
processes** reading only their own state file. No state holds faults, true onset, truth
or a preselected diamond.

## Accounting (unchanged definitions)

Deadline-snapshot payload bits (not temporal/process peaks): thick 40; thin 16 live +
8 boundary + 2 frame = 26; archives add 5 bits per fired coordinate. Compact JSON state
byte sizes reported separately. Query readings and reconstructed old-detector counts
reported separately from stored fired-event counts: for the **edge** diamond, the
reconstructed old values number **6** (vs 8 bulk); whole reconstructs 24.

## Frozen predictions (edge, d=3)

- **G1 — query size.** The edge diamond query reconstructs exactly **6** old detector
  values (2 X-sector + 4 Z-sector). Essentially certain by geometry. Conf ~98%.
- **G2 — whole == thick.** Thin+whole-archive reproduces the thick same-deadline
  reference exactly (0 disagreements, posteriors within 1e-12), as at the bulk site.
  Conf ~90%.
- **G3 — the witness persists.** Thin+diamond has strictly fewer reference-disagreements
  than thin-alone at the edge site. Conf ~80%.
- **G4 — restart.** Cold fresh-process restoration reproduces every arm decision
  (restart == direct; probabilities within 1e-12). Conf ~95%.
- **G5 — OPEN.** Whether the remaining diamond disagreement rate (and its
  diamond-right / reference-right split, and the weighted agreement/correctness) **rises
  or falls** relative to the bulk site is deliberately **not predicted** — it is the
  open scientific outcome this run measures.

## Handback

One bulk-versus-edge table: raw disagreements and weighted agreement with each site's
own same-deadline thick reference; weighted logical correctness vs simulator truth; who
was right when local (diamond) and thick disagreed; query size separated from mean and
maximum packed deadline payload bits and serialized JSON byte sizes; one replayable
disagreement if found; the protocol and result commits and the exact replay command.
Scope limited to this single distance-3 edge site.
