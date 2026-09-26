# Reddit post (draft)

**Suggested subreddits:**
- r/reinforcementlearning (friendliest home for it)
- r/cogsci
- r/neuroscience
- r/MachineLearning (use the `[R]` tag in the title and check their self-promotion rules first)

**Image to attach:** `figures/svc3.png` (or `figures/svc.png`).

---

**Title:** Should an AI memory keep what's *surprising* or what can *change a decision*? A
pre-registered toy study, plus an echo chamber we didn't expect

---

Several recent AI memory designs (Titans, surprise-driven replay) decide what to keep by
**surprise**: how unexpected an observation was. We tested an alternative in a small, controlled
setting: keep what can still **change a decision**.

**The setup.** An agent faces 200 situations. Some are "forced" (only one thing you can do, so any
fact about them, however startling, changes nothing). Others are close-call choices between two
actions. It sees 2,000 noisy observations but can only keep 100 (5%). Different rules decide what
stays.

**What we found:**
- **Keeping what can change a decision gave 44% lower decision regret than keeping what's
  surprising.** It still won by 14% against a surprise rule that was *also* told which situations
  offer a real choice, so it's not just "don't waste room on irrelevant stuff". The result
  replicated on fresh worlds.
- **The surprise-keeper knew the most facts, and made worse decisions.** Knowing more and choosing
  better come apart.
- **When the memory has to discover for itself where the choices are**, the main cost is
  *premature eviction*: throwing evidence away before you can know it matters. It suggests memory
  needs a short-term waiting room before it decides what to keep.
- **The ideal (cheating) memory's secret turned out to be the wisdom of crowds.** It keeps
  *typical* observations, not the loud extreme ones our rule was drawn to.
- **Then the twist.** When we tried to build that crowd-awareness honestly, judging "typical"
  against the memory's *own* beliefs, it did **42% worse**. It became an echo chamber: where it
  chose wrongly, 87% of what it kept supported the wrong answer. Judged against the truth, the
  same rule nearly matched the ideal memory. **A crowd is only wise if its judge is independent.**

**Honesty notes:**
- It's a designed toy world, built so the two strategies *can* disagree. It shows how big the gap
  can be, not how often real data looks like this.
- **Every prediction was pre-registered** (committed publicly before the code existed), across
  four rounds, two of them revised after outside review. **17 of 28 predictions held**, and the
  failures are reported as prominently as the successes.
- The core idea isn't new: Mattar & Daw (2018) proposed that the brain replays memories by how much
  they improve future choices. What's new here is a controlled test for *retention* under a tight
  memory budget, and the echo-chamber result.
- The study was designed, coded and analysed with an AI collaborator (Claude, by Anthropic), and
  all the code is public.

**Open question we'd love thoughts on:** where can a memory get an *independent* judge of what's
typical? A held-out sample? A slower, older memory? Two memory systems checking each other, like
hippocampus and cortex?

- Paper (Zenodo): [link]
- Code, pre-registrations and every result: https://github.com/kekekatie/geometric-impedance
  (`exploratory/surprise_vs_consequence/`)
