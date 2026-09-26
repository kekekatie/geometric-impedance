# Twins as mirrors — does hidden-address depth set the shared future?

**Design note plus one bounded exact feasibility test.** This is the start of the perp-space
bridge: the growth model runs *on* the Fibonacci chain of
[`../fibonacci_address_environment/`](../fibonacci_address_environment/). It is isolated, and
prior studies are preserved. Full design, controls and the parked Phase 2 (messengers and
resonance) are in [`DESIGN.md`](DESIGN.md).

## Result (exact in `ℚ(τ)`; exit 0)

**Setup.** BUD at `k=1` grows on the chain:
- every site starts active, and every tile is a bond with its length;
- rates are `1/ℓ`, and new bonds inherit their parent's length;
- time is continuous;
- **no rule ever reads the hidden address**.

For six far-apart site pairs with first-disagreement radius `r* = 1…6`, the exact short-time
expansion of `P(site still active at time s)` **agrees at every order below `r*` and first
differs exactly at order `r*`**, with no accidental cancellation in any pair. The **blind
control** (lengths ignored) makes every pair identical at every order.

> **Mirror law (on this rule):** twins in the hidden window share their future to order
> `s^{r*−1}`. Closer addresses give deeper twins and a longer shared future. There is no
> messenger here: the agreement comes from the shared mould, not from communication.

A light-cone lemma (`cₙ` reads only the tiles within distance `n`) guarantees the agreement.
The lemma is argued in `DESIGN.md` and checked computationally. The empirical part is that the
difference always *does* appear at `r*`.

Honest scope: continuous time has no hard light cone, so twins differ at any `s > 0`, by an
amount of order `s^{r*}`. What is exactly shared is the expansion. One rule, six pairs, orders up
to 6. It is a feasibility test, not the full experiment. The full experiment is proposed in
`DESIGN.md`: real-time `TV(s)` against address distance, and periodic and shuffled substrate
controls.

## Reproduce

```bash
python3 twins_mirror_feasibility.py   # ~7 min; exit 0 iff all exact checks pass
```
