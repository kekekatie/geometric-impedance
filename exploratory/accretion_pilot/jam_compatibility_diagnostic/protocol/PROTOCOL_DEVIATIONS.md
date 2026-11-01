# Protocol deviations (dated)

Deviations from `PROTOCOL.md`, recorded rather than edited into the original.

## 2026-11-02 — Part 5 erosion-level definition

The protocol's formula "remove tiles whose min distance to a true-frontier vertex
exceeds `(radius - L)*S` for `L = 1,2,3`" over-erodes a radius-2 retained layer
(it would delete essentially everything by `L = 2`, thresholds `1, 0, -1`).
Replaced, before any outcome was inspected, with nested inner cut-offs that keep
tiles within distance `theta` of the true frontier:

    L0 theta = inf (full, 315 tiles)
    L1 theta = 2.0 (260)
    L2 theta = 1.5 (226)
    L3 theta = 1.0 (170)

This still peels the inner rim in nested, deterministic steps while leaving the
outer growth boundary and the dead-site neighbourhood intact, which is the intent
of the protocol. Conclusions are unchanged under the alternative levels (all
levels give the same four-way outcome).

## Notes

- Parts 2–4 followed `PROTOCOL.md` as written. No other deviations.
- Part 5 did not need to invoke the "stop if the dead-site neighbourhood is
  removed or the component disconnects" clause: inner-rim erosion never removed a
  dead-site neighbour (the dead sites lie on the outer true frontier), so all four
  levels completed. The clause remains implemented and checked.