# The Penrose Investigation — a plain-language story

*A readable thread through what we did, why, and what it meant. No maths required
to follow it. Written for anyone — including future us — who wants the human
version before the technical one.*

---

## 0. Where it began

It started with a small, honest question: **were the flaws in "the Penrose
situation" real, and could we work them out?**

Two of the shapes this project builds worlds on are famous tilings — **Ammann–
Beenker** (call it *silver*) and **Penrose** (call it *golden*). They're patterns
that never quite repeat, and each vertex secretly carries a hidden "address" in an
internal space. A lot of the project's results stand on these two tilings being
*faithful* — genuinely themselves. So: were they?

---

## 1. Penrose wasn't quite Penrose

The first thing we found, digging in, was that our Penrose was **subtly wrong**.

A real Penrose vertex touches **at most 7** neighbours. Ours had vertices touching
**up to 10**. Something was letting in points that shouldn't exist — the tiling was
a slightly-bloated impostor of the real thing. (Ammann–Beenker, reassuringly, was
fine.)

The earlier diagnosis had blamed the "acceptance window" — the shape that decides
which points are allowed. But when we looked properly, that shape wasn't even being
used to admit points; it only labelled them afterward. The *real* culprit was a
single setting — a de Bruijn "offset sum" — quietly set to a half-number when a
faithful Penrose needs a whole number. At the half value, the machine was building
a *different* tiling entirely (a "generalised" Penrose), which grows those extra
over-connected vertices.

**The fix was essentially one line.** Pin the offset to a whole number, and Penrose
snapped into its true self: coordination-7, exactly right, everywhere. Ammann–
Beenker: untouched. And — the part that mattered most — every deep result we care
about (the holonomy quanta, the theorems, the reverse-loop) held *exactly*. We'd
fixed the foundation without disturbing anything built on it.

---

## 2. The thing that looked broken but wasn't

Faithful Penrose in hand, the next checker said Penrose still "failed": its
periodic approximant was only **~40% periodic**. Alarming — a periodic thing that's
only 40% periodic is a contradiction.

It turned out **nothing was broken.** The checker was sliding the tiling by the
wrong-sized ruler. Penrose carries a discrete "class" label on every vertex (one of
four kinds — a little packet of pure *this-or-that*). To slide the tiling perfectly
onto itself, you have to move far enough to bring every point home to its **own**
kind — and that distance is **five times** the naive one. Slide by the right,
five-times-bigger step, and **100%** of points land home.

The lovely part: **that factor of five *is* the four-class structure made physical.**
The "wiggle room" that makes Penrose richer than its silver cousin has a measurable
footprint, and the footprint is ×5. (This is the point Katie's instinct kept
circling — that the *this/that* difference was the load-bearing thing. It was.)

---

## 3. The doughnut that fixed the mirror

One more worry: to be a fair scientific "control," the approximant's fingerprint (a
histogram of how many neighbours vertices have) had to match the ideal's. On a flat
patch it *didn't* quite — Penrose looked short on certain vertex types.

The fix was topological: wrap the tiling into a **doughnut** (a torus), so it has no
edges to fray at. Give it no boundary, and the fingerprint matches the ideal
beautifully — the earlier mismatch had been an *edge-of-the-patch* artefact all
along, not something real about Penrose. We checked it up the whole ladder of
approximant sizes, both tilings: they all converge to the ideal. The control is
valid. (And a proper Penrose doughnut has to be wrapped by that same ×5 cell — so
the discovery and the control rest on the same stone.)

---

## 4. Teaching the instrument to see straight

The bigger goal is a real experiment (Stage D, below), but you don't trust a
telescope you haven't focused. So we built and checked the measuring instrument
first — twice.

- **Stage B** built the standard "circle map" and confirmed it reproduces two famous
  universal numbers of a *devil's staircase* (a fractal dimension of 0.87 and a
  step-shrink exponent of 3). We hit them — after a couple of honest wrong turns,
  including me hunting for a feature in entirely the wrong place because a giant
  plateau had shoved it sideways. Calibration, never a finding: the point was only
  to prove the instrument doesn't lie.

- **Stage C** fed each tiling's *own special number* into that instrument and
  confirmed the map treats them correctly: **golden** (the most stubbornly
  irrational number there is) resists falling into lock-step harder than **silver**.
  It fought me — the obvious way to measure it produced artefacts — but the honest
  version came through: golden keeps more open room, exactly as pure arithmetic
  demands.

---

## 5. The metronome room, and an honest wall

**Stage D** is the one with real content, the only place a genuine discovery could
live. The picture: make every vertex a little **metronome**, connect neighbours with
springs, and slowly turn up a coupling dial. At some threshold **K\***, the whole
room snaps into sync. The question: as a tiling climbs toward its perfect ideal,
does that snap-point stay flat (the geometry stays quiet), or slide toward the
tiling's *own* special shrink-rate (the geometry singing all the way into the
dynamics)?

We built the room. It syncs. And then the experiment **fought back** in the most
instructive way: the snap-point kept *climbing as the tiling grew*. That looked like
a problem — until we saw it was **physics, not a bug**. These tilings are 2-D
sheets, and a 2-D sheet of metronomes simply *cannot* hold a room-wide sync once
it's big enough (the same reason a 2-D magnet has no long-range order). Our safety
check — the "canary" — caught it before we could mistake a size-artefact for a
discovery. *That's the whole point of the canary, and it earned its keep.*

The fix is a **fair race**: compare all the tilings at the **same size**, so the
size-effect cancels and only the golden-vs-silver question remains. And there's a
clean companion measure — the tiling's "connectivity," which *is* stable with size —
that a first look suggests is **flat** up the ladder: leaning toward the honest
**null** we'd predicted from the start. (Final verdict: see below.)

> **[Stage D verdict — to be filled when the fair race finishes running.]**

---

## 6. What this is, and what it isn't

No grand claims. What we have is a handful of small, checkable bricks laid straight:

- Penrose is now genuinely Penrose (a real bug, quietly fixed).
- Its true repeating unit is five times the naive one — and that ×5 is the physical
  shadow of its four-class *this/that* structure.
- The torus is the right, validated control; the instrument reproduces the textbook
  universal numbers; each tiling's special number transports correctly.
- And the real experiment is running honestly, canary and all, most likely toward a
  clean null — which is a perfectly good result, and one we'd have reported either
  way.

The throughline, if there is one: **let the theory be itself, and when it fights
back, listen.** Twice the thing that looked like failure turned out to be the
geometry telling us something truer than we'd asked. That's the good kind of day.

*— written mid-investigation; the record lives in the commit history and the
`winding_staircase/` and `approximant/` folders.*
