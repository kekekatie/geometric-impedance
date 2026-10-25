# Rib length, done right: the marginal structure a settlement forces

### The corrected endurance bridge (Experiment D′)

*Pre-registration. Written and committed **before any code for D′ exists**, after Experiment D's clean
null and Argon's diagnosis of why it failed. The numbers below are our called shots.*

*Katie (direction), Argon (the diagnosis and the marginal-forcing fix), with Claude (Opus 4.8).*

---

## Why D failed, and the fix

Experiment D measured "forced-support reach" by bursting the neighbourhood **at a tie's birth** and
counting forced tiles placed. Argon diagnosed, and the data confirmed, that this measured **ambient
construction traffic**, not what the tie anchors:

> Ties that **stay open and never lock** had the *largest* reach of all — median **43**, versus **14**
> for ties that actually settle. A measure of anchoring cannot have its biggest values on things that
> anchor nothing. The burst was counting how busy the site already was, and D3 correctly caught it
> tracking the frontier-advance rate.

**The fix** is to measure the settlement's *marginal* forward forcing — and let the ambient wave
cancel:

> **rib length = (forced tiles after placing the surviving option) − (forced tiles after placing
> nothing),** both grown forced-only to local saturation from the same `before` patch.

The background domino-wave appears in both terms and subtracts out; what remains is purely the
structure the settlement *itself* unlocks and forces forward. This applies only to **settlements**
(a stayed-open tie has no surviving option — which is the whole point).

---

## Words

- **Settlement** — a tie resolving as `single_keystone` or `committee`.
- **Surviving option** — the one candidate still legal at `edge` when the tie settles (matched by
  decoration key back onto the `before` patch).
- **count_forced(patch)** — localised forced-only growth (radius 10·S, cap 60) from `patch`, counting
  tiles placed to saturation. No early stop on any edge.
- **Rib length** — `count_forced(before + surviving) − count_forced(before)`. ≥ 0; the marginal forward
  structure the settlement forces.
- **Birth-decisiveness** — A's fingerprint stiffness (rigid ≥ 0.9 vs malleable < 0.9).
- **Frontier-advance rate** — local tiles added per slice over the tie's window (the confound to rule
  out, as in D).

---

## Set-up (fixed now)

- The same 24 worlds (seeds 192–215). Rib length is computed for every recurring-fingerprint
  **settlement**, joined to its A/C birth-state.
- Two localised forced bursts per settlement (with / without the surviving option); their difference is
  the rib length. Never a slice count.

---

## Predictions (our called shots)

**D′1 — decisive births force more forward structure.**
Rigid settlements have **larger rib length** than malleable ones: median(rigid) > median(malleable)
and Spearman(stiffness, rib length) **> 0.2**. *Confidence ≈ 50%* (genuinely open — the old inversion
was an artifact, so the clean direction is unknown; we commit to reporting it either way).

**D′2 — two modes: ribs and hinges.**
Rib length is **bimodal** — a long-rib population separate from a short-hinge population. *Confidence ≈
40%* (reported with the histogram and a dip statistic regardless).

**D′3 — the fix works: it is not the stopwatch.**
Rib length does **not** track the frontier-advance rate: |Spearman(rib length, advance rate)| **< 0.2**
— the ambient-traffic confound that sank D cancels in the difference. *Confidence ≈ 70%.*

---

## Reported, but not scored

- **Old vs new.** D's ambient reach against D′'s marginal rib length, per settlement — how much the fix
  changed the measure.
- **Rib length by birth-state** — rigid/malleable, secretly-rigid/genuine-(a), with the 1/φ² wobbly
  sites marked.

---

## Limits we already know

- Rib length is a **structural proxy** for endurance (marginal forward forcing), not persistence on the
  advancing skin. The faithful same-class-renewal measure in the hollow active-skin growth remains the
  deeper follow-up if D′ shows nothing.
- Localised (radius 10·S) and capped (60 slices), so rib length is a bounded count.
- Same 24 worlds, 4 jammed; one scheduler. No claim about physical space or time.
