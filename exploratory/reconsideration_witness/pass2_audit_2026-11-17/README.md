# Independent Pass 2 audit

Input commit: `f8e15d863a141404f152629d279612236264472f`.
Audit branch: `audit/pass2-paired-2026-11-17`.
Pre-execution audit protocol: `d056d31` (`PROTOCOL.md`).

From the repository root, with Python 3 and NumPy installed:

```sh
cd exploratory/reconsideration_witness/pass2_audit_2026-11-17
python3 check_geometry.py
python3 audit.py near
python3 validate_near.py
python3 audit.py caps
python3 check_index.py
python3 summarize.py
```

No frozen source, result or sampled panel is modified. The audit imports the adjacent pinned distance-five implementation. `audit.py caps` verifies the sample hashes and evaluates all four arms on the same 2,880 histories. It automatically runs (4,4) if the conservative paired-margin trigger fires. It resumes completed audit-only JSON checkpoints; use a fresh checkout for a cold replay. The original 200,000-history primary run is not rerun by these commands; this audit concerns cap sensitivity, the full near-loss census and constructed seams.

`results/cap_*.csv` contains the committed per-history outputs, including both posterior components and tie flags. History ordering is the original `_panel_fts`: 250 sorted triples, then 110 weight-one local primitives, each with the eight original variants. Large, redundant JSON checkpoints and fault lists are ignored; replay regenerates them. `summarize.py` independently recalculates the paired margins from the CSV and verifies equality with the summary.

The query accelerator indexes only live detectors and round-two boundary parity, both already available or implied by every arm. For each erasure value it retains every candidate matching those necessary conditions, then invokes the original marginal filter on their union in the original enumeration order. It changes neither the candidate bound, the prior nor the decision rule. Baseline checks cover every cap-panel history against the unaccelerated scan and original table builder. Raised-cap checks cover 32 evenly spaced histories plus every label/tie change from baseline. Separate checks cover 256 weight-two near-loss histories and all eight seam records. Validation results and maximum posterior errors are committed.

The seam records have 120 detector values in stabilizer-major, round-minor order. The four X-fault pairs have opposite **scored Z-logical** truth. The four Z-fault pairs instead have opposite **conjugate X-logical** truth; the present decoder still scores Z-logical truth and is not a conjugate decoder. No pair is claimed to explain the full ensemble's ties.

Storage accounting and distance-three results are outside this audit. No new population inference is made from the sorted 250-triple diagnostic subset.

Execution note: the first unfinished (3,4) attempt was stopped after diagnosing an unnecessary NumPy index copy. Matching search-key dtype (`uint64`) avoids that copy; keys occupy at most 36 bits, so the earlier float64 promotion was exact and this is only a performance fix. Completed (3,3)/(4,3) checkpoints were retained. `check_index.py` repeats all 11,520 baseline arm checks after the fix and checks search boundaries. The restarted higher-cap runs retain the original unaccelerated validation requirement. No panel or scientific protocol was changed. Environment: CPython 3.12.16, NumPy 2.2.6.
