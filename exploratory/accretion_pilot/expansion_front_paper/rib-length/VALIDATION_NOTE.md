# Validation note: D′ measure found contaminated before the confirmatory run

The pre-registered rib length `count_forced(before + surviving) − count_forced(before)` was validated on
one small world **before** any confirmatory run. It is **contaminated** and was **not run at scale**.

**Why.** Most catalogue settlements are *locally forced* (secretly rigid, per Experiment C): the local
forced-only wave settles the tie on its own, to whichever option the wider patch dictates. For those,
`count_forced(before)` already settles the tie — to the *other* option when `surviving` is the
non-forced one — so the subtraction compares two forced outcomes and returns noise (median −1; some −53).

**What the debug revealed (the real signal).** For the minority of ties that are *genuine free choices*
(the local wave leaves them open), committing the surviving option unlocks a large, clean forward
cascade — **107, 368 tiles** in the sampled cases — while locally-forced ties unlock essentially
nothing. So the load-bearing "ribs" appear to be the **genuine free choices**, not the rigid ones —
the opposite of D′1's lead guess, and a clean echo of Experiment D's inversion with a real mechanism.

**Decision.** Rib length is only well-defined on genuine free choices. Restricting the measure to that
domain changes both the population and the likely direction of the result, so it warrants its own fresh
pre-registration rather than an amendment after peeking. This folder is kept as the honest record of the
attempt; no confirmatory D′ numbers were produced.

**Next.** Either (a) a clean pre-registration of rib length on genuine free choices, or (b) the faithful
same-class motif renewal in the hollow active-skin growth — the direct measure of endurance that needs
no cascade proxy at all.
