# Stage 1.5 addendum: live-vs-live, and the onset-lip geometry

*Addendum to `STAGE1_REPORT.md`. Diagnostic frozen in `stage1_5_onset_lip.py`
(predictions L1–L6 in its docstring, committed at `1cf1865` **before** the run).
Replay: `python3 stage1_5_onset_lip.py` -> `stage1_5_handback.json`.*

## The two headline answers

**The ~15% pruning gap is *exactly* the 4-bit onset bracket, and nothing else.**
Keeping all four detectors around the lost qubit — `(c0,t0),(c1,t0),(c0,t1),(c1,t1)`
— makes the restorer reproduce the deadline-reference **exactly** (agreement
**1.000** vs deadline-ref, on every set and both onset models). Because
`bracket4 + m2` pins the whole 6-detector core to a single syndrome, the committed
`frame` bit is then **100% redundant** (7188/7188 and 6676/6676 identical with and
without conditioning on `frame`). The pruned "reason" is precisely these four bits.

**But you cannot buy the 4th bit back with `frame`.** `frame` is a non-invertible
MAP threshold, so `3 bits + frame` does **not** reconstruct the bracket: it leaves
~2 core candidates (mean 1.88) and agrees with `bracket4` only 95.3% (ONSET_AVG) /
97.0% (FREE_BOTH). All four detector bits are genuinely needed; `frame` rides along
for free once you have them but can substitute for none of them.

## (1) Live-vs-live confirms Katie's read of the ~5%

Scoring every decoder **directly against the deadline-reference** (the unpruned
decoder's actual prediction *at* the Round-4 deadline) instead of the omniscient
end-of-film reference raises agreement everywhere — the gap that closes is the
"presentish future that hasn't dropped its tile yet." Examples (ONSET_AVG):

| decoder | vs deadline-ref | vs full-ref | (future-noise removed) |
|---|---|---|---|
| t0-restorer, witness, flag-after | 0.810 | 0.771 | +3.9% |
| t0-restorer, fresh, flag-after | 0.906 | 0.765 | +14.1% |
| 0-bit, fresh, flag-after | 0.873 | 0.742 | +13.1% |

**L1 HELD.** The clean decomposition now reads, on the ONSET_AVG witness set:
`bracket4` vs full-ref = 0.953 (the *pure deadline/future* cost, since bracket4 =
deadline-optimal), and `t0` vs deadline-ref = 0.810 (the *pure t0-pruning* cost).

## (2) The onset-lip hypothesis: direction right, magnitude modest, witness set biased

Argon's geometry predicts the **t0/t1 asymmetry should flip with the model**:
FREE_BOTH (rounds 1–2 merged into one hole, floor at round 0) should favour **t0**;
ONSET_AVG (the stone may wait until round 2, leaving round 1 as the lip, which also
dates the drop) should favour **t1**. On the **unbiased fresh weight-4 set** (vs
deadline-ref, flag-after) that is exactly what happens:

| 2-bit variant | FREE_BOTH (fresh) | ONSET_AVG (fresh) |
|---|---|---|
| t0 | **0.974** | 0.906 |
| t1 | 0.941 | **0.917** |
| lip_parity `t0^t1` | 0.930 | **0.928** |

Under FREE_BOTH, t0 leads and t1 is weakest; under ONSET_AVG the order inverts and
the **timing parity `t0^t1` is the best two bits** — the "when did it drop" bit, as
Argon argued. The effect is real but **small** (~1–2%), because most fresh histories
sit far from the boundary.

On the **witness set**, the asymmetry is swamped by selection bias: those pairs were
defined under FREE_BOTH where Stage 0 found *t0* to be the splitting detector, so t0
dominates there for *both* models (ONSET_AVG witness: t0 = 0.810, t1 = 0.647,
lip_parity = 0.496 — worse than 0-bit). This is a property of how the witness set was
chosen, not evidence against the lip.

**So, honestly scored:** L2 (t1 > t0 under ONSET_AVG) **failed on the witness set**
but its **direction held on unbiased data**; L3 (FREE_BOTH favours t0) **held in
direction** but t0 is *not* near-complete (0.85, not ~1.0 — the bracket is needed);
L5 (lip_parity beats t0 under ONSET_AVG) **held on fresh, failed on the biased
witness set**. The crisp, selection-free statement is: **neither single corner pair
suffices; the asymmetry between which pair helps more follows the lip geometry; and
only the full four-corner bracket closes the pruning gap.**

## Scorecard (frozen L1–L6)

| | prediction | verdict |
|---|---|---|
| L1 | vs deadline-ref > vs full-ref everywhere | **HELD** |
| L2 | ONSET_AVG: t1 > t0 on witnesses | **failed on witnesses; direction holds on fresh** |
| L3 | FREE_BOTH: t0 near-complete, t1 weak | **partial** (t1 weak ✓; t0 not near-complete — bracket needed) |
| L4 | bracket4 = deadline-reference (1.000) | **HELD, exactly** |
| L5 | lip_parity beats t0 (ONSET_AVG), below bracket4 | **held on fresh; failed on biased witness set** |
| L6 | bracket4 ⇒ frame redundant; 3bit < bracket4 (all 4 needed) | **HELD, cleanly** |

## What this nails down

- The information the streaming cut sheds, at a realistic deadline, is **exactly the
  four onset-bracket detectors** `(c0,t0),(c1,t0),(c0,t1),(c1,t1)`. Retain them and
  the restorer is the deadline-optimal; the only residual gap to the omniscient
  reference (~5%) is genuine future that has not happened yet.
- The committed `frame` verdict is **redundant** once the bracket is kept, but it is
  a non-invertible threshold, so it cannot stand in for any bracket bit — a sharp
  statement of why the *verdict* (1 bit) and the *reason* (4 bits) are different
  currencies, which is the whole theme ported from the paper.
- Argon's lip picture is the **right mechanism** for the t0/t1 asymmetry (confirmed
  in direction on unbiased data); it is modest in size and masked on the t0-selected
  witness set, which is itself a useful caution about scoring on a constructed set.

*Limits unchanged from Stage 1. The deadline-reference remains a post-hoc diagnostic;
`lip_parity`, `3bit` and `bracket4` restorers are exact-Bayesian for this instance.*
