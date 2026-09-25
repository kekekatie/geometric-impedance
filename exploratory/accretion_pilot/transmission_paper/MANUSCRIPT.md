# When the past matters, II — The fate of an expressed difference

*Working title, provisional. Successor to* When the past matters *(K. T. Niedzwiecki, Zenodo,
2026).*

> **Living manuscript.** Transcribed faithfully from Katie's assembled draft
> (`transmission_paper_stitched_a43ff0c`, PDF, 21 September 2026; pinned to commit `a43ff0c`).
> Changes since that draft are listed in [Revision notes](#revision-notes-2026-09-25) at the end
> and marked **[rev]** in the text. Passages marked **[draft for review]** are new and await
> Katie's approval. Open items: [`TODO.md`](TODO.md).

---

## Provenance and change note *(from the 21 September draft)*

This is the assembled transmission paper — Terms, §1, §2, §3 — from two sources: the front matter
(§1–§2) and Fable's 20 September 2026 §X draft (now §3), the latter verified and corrected against
the repository as below. Voice throughout: present tense, no adverbs of emphasis, claims scoped to
the enumerated sets, propositions stated with what they do and do not cover.

- **First paper.** The successor relation and all carried-over machinery reference *When the past
  matters: Retained structure, readable traces, and causal relevance in two growing graph models*
  (K. T. Niedzwiecki, Zenodo, 15 September 2026; concept DOI `10.5281/zenodo.22759878`, this
  version `10.5281/zenodo.22759879`, CC-BY-4.0). Its Proposition 1 (there, §3.3) and Proposition 2
  (there, §3.5) are quoted verbatim in §2; Proposition 3 is new here and proved in §3.2. (The
  `21200994` in the repository trail (`RESUME_HERE.md`) is the earlier preprint the deposit
  continues, not the current record.)
- **§3 verification** (against `a43ff0c`: `endogenous_pair_robustness/`,
  `endogenous_present_width/`). Depth-2 numbers reproduce exactly. The depth-3 fate split is filled
  in — 22 inert, 5 washout, 70 durable (75 expressed). Pair (22,25) is corrected from a provisional
  "durable" to washout (verified record `D_slice(1)=0`, `D_slice(2)=17/120`,
  `D_slice(3)=1423/7200`, `L=0`); (22,26) is confirmed washout (`1/6`, `17/90`, `539/2700`, `L=0`,
  one sink). Recurrent classes are confirmed singletons (SCC condensation over all 97 coasts) with
  exactly two sink shapes; a sink/fate cross-tabulation (85 two-sink, 12 single-sink) reconciles
  the counts with no remainder.
- ~~One residual soft claim.~~ **[rev] Resolved 2026-09-25:** see §3.5 and
  [`checks/soft_claim_22_26.py`](checks/soft_claim_22_26.py).
- **Terms.** BUD and CONTACT rows added; internal cross-references renumbered §X → §3.

---

## Abstract **[draft for review]**

A growth model in which a graph rewrites itself by local events lays down a persistent archive of
quiet vertices. In the first paper of this line, a second local rule (CONTACT) lets that archive
bias the distribution over present states. Here we delete the archive and ask what survives. For
a matched pair — two states with the same present and different archives — both lineages run
under the coupled rule to a horizon, the archive is erased, and the present continues under the
generative rule alone. Proposition 3 shows that the between-lineage distinguishability of the
present along this archive-free coast is non-increasing and converges to an exact limit `L`, the
total-variation distance between the two lineages' absorption distributions; for the original
pair `L = 4321/44100`. Every recurrent class of the coast is a single absorbing matching, for any
seed. Combining `L` with whether the archive difference was expressed sorts matched pairs into
three fates — inert, washout, durable — and on the enumerated depth-2 and depth-3 sets an
expressed pair is durable if and only if its coast has at least two reachable sinks. Durability is
a property of the present's own future, not of the size or timing of the imprint: the past leaves
a lasting mark only where the coast forks. Throughout, what survives is a bias in the
distribution over presents, never a record held by any single present.

---

## Terms

Terms carried over from the first paper are marked †. All others are introduced here.

| Term | Meaning |
|---|---|
| **BUD(x, y)** † | The generative event, at `k = 1`: on an active bond `x–y`, the keeper `x` stays active, the depositor `y` becomes quiet, and one new active vertex `z` is added with edges `x–z` and `y–z`. Count change `(ΔV, ΔE, ΔQ, ΔA) = (1, 2, 1, 0)`. |
| **CONTACT(a, q, b)** † | The coupling event: eligible when `a, b` are distinct active neighbours of a quiet vertex `q` and the edge `a–b` is absent; it adds `a–b` and nothing else. The archive's only causal action on the active layer. |
| **active / quiet** † | Vertex states. Only active vertices participate as BUD endpoints or CONTACT endpoints. A quiet vertex's incidence is fixed under BUD and CONTACT. |
| **archive** † | The quiet vertices together with their incident edges. |
| **active projection π(G)** † | The isomorphism class of the subgraph induced by the active vertices (Proposition 1 of the first paper). |
| **slice** | The active projection of a full state, regarded as "the present." Slice and active projection name the same object; slice is used when the archive is about to be removed. |
| **menu C_q(G)** † | The set of CONTACT-eligible active pairs at quiet vertex `q`. |
| **matched pair** | Two reachable full states with isomorphic active projections and non-isomorphic full graphs. The lineages differ only in their archives. |
| **lineage** | The distribution over full states obtained by running the dynamics from one member of a matched pair. All comparisons are between the two lineages of a pair. |
| **distinguishability D** | Total-variation distance between the two lineages' distributions over isomorphism classes. `D_full` is taken over full states; `D_slice` over slices. |
| **expressed** | A pair is expressed at horizon `H` if `D_slice(H) > 0`: the archive difference has changed the distribution over presents. `Δ ≠ 0` is used as shorthand. |
| **surviving fraction ρ(h)** | `D_slice(h) / D_full(h)`. The share of the distinguishing difference that is legible from the slice alone. |
| **ERASE / KEEP** | At horizon `H`, either delete every quiet vertex and continue under BUD alone (ERASE), or retain the archive and continue under BUD + CONTACT (KEEP). |
| **coast** | The archive-free continuation after ERASE. With no quiet vertices, CONTACT is inert, so the coast runs under the BUD-only projection kernel. |
| **sink** | An absorbing class of the coast chain. On the enumerated sets the sinks are two disjoint bonds and one bond with two isolated actives. |
| **reachable sinks** | The sinks that the coast can enter from the support of either lineage's slice distribution at `H`. |
| **limit L** | `lim_{t→∞} D_slice` along the coast. Proposition 3 shows it exists and equals the total-variation distance between the two lineages' absorption distributions. |
| **fate** | The classification of a matched pair as inert, washout, or durable (defined in §3.3). |
| **tendency** | The word used throughout for what the past leaves in the present: a bias in the distribution over presents, never a record carried by any single present. |

---

## 1. Introduction

The first paper (*When the past matters*, `10.5281/zenodo.22759878`) set out a growth model in which
a graph rewrites itself by local events, with no traveller, no coordinate, and no stored log, and
asked whether such a system can carry a record of its own history. Its answer came in two parts.
Under the generative rule alone the active front is a closed system: it lays down a persistent
archive that it never reads back (Proposition 1). A second local rule, CONTACT, lets that archive
act on the active layer — and only then. Two histories that differ solely in their archives are
indistinguishable under the generative rule, yet become distinguishable in the distribution over
present states once CONTACT is admitted. Throughout, the distinction is a property of the
ensemble — a bias in the distribution over presents, taken across histories — and never a record
held by any single present. In the phrase the first paper keeps in front of the reader: the
present does not remember; the present is biased.

This paper takes the step the first one stopped short of. Once CONTACT has let an archive bias the
present, we delete the archive and ask what survives. The object of study is a matched pair: two
reachable states with isomorphic active projections and non-isomorphic full graphs, differing only
in the archive behind an identical present. We run each member forward under the coupled dynamics
to a horizon, erase every quiet vertex, and let the present coast under the generative rule alone.
The question is the fate of the between-lineage distinguishability of the slice, `D_slice`, along
that coast: whether it falls to zero or holds above it.

Section 3 answers this on the enumerated matched-pair sets. Proposition 3 shows the coast has an
exact limit `L`, a single rational number that is the total-variation distance between the two
lineages' absorption distributions. Combined with whether the archive difference was expressed at
all, `L` sorts every pair into three fates — inert, washout, durable — and the fork law identifies
which pairs are durable: among expressed pairs, `L > 0` if and only if the coast has at least two
reachable sinks. Durability is therefore a property of the present's own future under the
archive-free rule, not of the imprint the past left: the past leaves a lasting mark only where the
coast forks.

The coupling used here is graph-local — a quiet vertex mediates between its own active neighbours.
A companion line of work replaces graph-locality with quasicrystalline address-locality: relevance
organised by perpendicular (internal) address in a cut-and-project set, where a site's local
environment is fixed by its address up to a finite cell resolution. That address-based coupling is
set aside here; §3.6 records that the results below do not depend on it. It is the natural subject
of the next paper in this line.

## 2. The model, and what carries over

This section fixes notation and restates, without proof, the first-paper results that §3 uses.
Terms marked † in the Terms table are the carried-over ones; their defining facts are collected
here.

### 2.1 The generative rule (BUD)

The substrate is a finite simple graph whose vertices each carry one label from `{A (active),
Q (quiet)}`; edges are unlabelled, an edge's role read from its endpoint labels. An active bond is
an edge with both endpoints active. The generative event, at branching parameter `k = 1`
throughout, is

> **BUD(x, y)** on an active bond `x–y`, directed: the keeper `x` stays active; the depositor `y`
> becomes quiet; one fresh active vertex `z` is created with edges `x–z` and `y–z` (so `x–y–z` is a
> triangle, with the quiet apex `y`).

Time is the event count. Two facts about BUD at `k = 1` are used repeatedly. First, its count
change is `(ΔV, ΔE, ΔQ, ΔA) = (1, 2, 1, 0)`: in particular `ΔA = 0`, so the number of active
vertices is invariant under BUD — this is what makes the archive-free coast a finite chain (§3.2).
Second, the active-bond count `B` changes by `ΔB = k − d_A(y) = 1 − d_A(y)`, where `d_A(y)` is the
depositor's active degree before the event; since `d_A(y) ≥ 1` on any bond, `B` is non-increasing
along a BUD-only run, while `|V|` grows every event. (The growth audit corrects an earlier reading:
at `k = 1` the frontier neither stalls nor goes extinct — `B` plateaus at `B ≥ 1` while the graph
keeps growing — and global non-confluence of the rule is left open. Nothing in this paper rests on
more than the two count facts above.)

### 2.2 The archive, the active projection, and Proposition 1

The active projection `π(G)` is the subgraph induced by the active vertices, keeping only
active–active edges and retaining isolated active vertices; every quiet vertex and every edge
touching one is dropped. The archive is the complement: the quiet vertices with their incident
edges. A slice is the active projection of a full state — the present, with the archive removed.

> **Proposition 1** (active-projection closure; first paper, §3.3). Under uniform selection among
> directed active bonds, the distribution of the next active projection depends only on `π(G)`.

BUD alone is therefore a closed, autonomous Markov kernel on active projections, and the archive
is causally inert for the active dynamics: the front lays the archive down and never reads it
back. Two facts give the proposition: the eligible directed events of `G` are exactly the directed
edges of `π(G)` (selection is `π`-measurable), and the projected effect reads only the active
graph (delete the depositor and its active edges, keep the keeper, add `k` fresh active leaves on
the keeper). The closure is a joint property of the projected effect and of a scheduler that reads
only `π`; a scheduler weighting events by total degree, which counts quiet neighbours, would break
it. What is not claimed is that the full future is archive-independent: archives persist and
accumulate, so two states with isomorphic active projections but different archives have
non-isomorphic full successors. The archive is where the record lives; it exerts no pull on the
active rule. A matched pair is exactly such a pair — same present, different archive — and the
coast of §3 is the run of Proposition 1's kernel from the two members' erased slices.

### 2.3 CONTACT, and the menu

Proposition 1 makes the archive silent under BUD. The coupled dynamics adds one local rule that
gives it a voice:

> **CONTACT(a, q, b)** is eligible when `a` and `b` are distinct active neighbours of a quiet vertex
> `q` and the edge `a–b` is absent; its effect is to add `a–b` and nothing else. The endpoint pair
> `{a, b}` is unordered, and distinct quiet mediators `q` are distinct events.

The archive is never edited: what CONTACT does is re-express a quiet vertex's stored relationships
as new active structure — the trace is consulted, not rewritten. One step of the extended dynamics
is a uniform choice over the union of the directed BUD events and the CONTACT events, each of
weight one; this relative weighting is a modelling assumption. The menu
`C_q(G) = { {a,b} : a,b distinct active neighbours of q, a–b absent }` collects the CONTACT
opportunities a quiet vertex currently mediates.

> **Proposition 2** (menu monotonicity; first paper, §3.5). Under BUD and CONTACT, every
> transition `G → G'` satisfies `C_q(G') ⊆ C_q(G)` for each previously quiet `q`.

A quiet vertex's incidence is frozen and its active neighbours can only turn quiet, while edges are
only ever added, so no pair enters a standing menu. Consequently an existing trace can be consulted
after a delay, but never acquires an opportunity it lacked at deposition; new menus arrive only
with freshly deposited quiet vertices. This is the result behind the "menu-equivalent" language of
§3.4: at depth 2 a pair is inert exactly when its two archives present the same one-step menu, and
the depth-3 remark records that this one-step equivalence is not preserved through time.

### 2.4 Distinguishability, erasure, and the coast

The two lineages of a matched pair start from isomorphic active projections and differ only in
their archives, so a clean measure of how legible the history is at each moment is the
total-variation distance between the lineages' distributions. `D_full` takes it over full states,
`D_slice` over slices; the surviving fraction `ρ = D_slice / D_full ∈ [0, 1]` is the share of the
distinction legible from the present alone. A pair is expressed at horizon `H` when
`D_slice(H) > 0`. The first paper's present-width study records the shape of `ρ` under the
extended dynamics: `ρ = 0` at `H = 0` (all distinction in the archive), rising with each CONTACT
but staying below 1 — the present is only ever partly legible.

At horizon `H` the paper applies one of two operations. ERASE deletes every quiet vertex, leaving
the active projection, and continues under BUD alone; with no quiet vertices CONTACT is inert, so
the continuation — the coast — runs under Proposition 1's kernel. KEEP retains the archive and
continues under the extended dynamics. The first paper establishes, for the original pair, that
the coast is non-increasing (one shared kernel, data-processing) and that KEEP holds `D_slice` at or
above the coast over the tested interval — the archive is not redundant. Section 3 takes the coast
as its object and asks where it lands.

## 3. The fate of an expressed difference

### 3.1 Setting

Fix a matched pair and a horizon `H`. Both lineages run under BUD + CONTACT for `H` events; the
archive difference may or may not be expressed in the slice by then. At `H` the archive is deleted
and the present coasts. The question of this section is what happens to `D_slice` along the coast,
and in particular whether it approaches zero.

Two facts from the first paper govern the coast. Under BUD alone the active projection is closed
(Proposition 1), so the coast is a Markov chain on active projections with one kernel applied to
both lineages. And at `k = 1` the count change is `(ΔV, ΔE, ΔQ, ΔA) = (1, 2, 1, 0)`: the number of
active vertices is constant. For the seeds used here that number is four.

### 3.2 Proposition 3: the coast has an exact limit

> **Proposition 3.** Let both lineages of a matched pair be erased at horizon `H` and continued
> under BUD alone at `k = 1`. Then `D_slice(t)` is non-increasing in `t ≥ H` and converges to
>
> `L = TV(a_0, a_1)`,
>
> where `a_i` is lineage `i`'s distribution over the recurrent classes of the coast chain.

*Proof.* With `ΔA = 0` the active projections are graphs on a fixed number of vertices, of which
there are finitely many up to isomorphism, so the coast is a finite time-homogeneous chain by
Proposition 1. Each lineage's slice distribution therefore converges to a distribution supported
on the chain's recurrent classes, and `D_slice(t)` converges to the total-variation distance
between those two limits. Monotonicity is the data-processing inequality: one fixed kernel applied
to two distributions cannot increase their total-variation distance. □

**[rev]** The recurrent classes themselves are fixed by a general fact about BUD, not only by the
enumeration.

> **Lemma** (recurrent classes of the coast). Under BUD alone at `k = 1`, from any seed, every
> recurrent class of the projection chain is a singleton `{M}` with `M` a matching plus isolated
> vertices, and `M` is absorbing. Conversely, every matching plus isolated vertices is absorbing.

*Proof sketch.* `B` is non-increasing (`ΔB = 1 − d_A(y) ≤ 0`). Within a recurrent class every state
is revisited, so no transition inside it can lower `B`; every directed bond `(x, y)` in a recurrent
state therefore has `d_A(y) = 1`, which makes every non-isolated vertex of degree one — a matching.
Budding a matching edge `x–y` deletes `y` and hangs the new tip on `x`, returning the same shape,
so the class is a single absorbing state. □ The statement is also checked exhaustively on all 208
isomorphism classes of graphs with at most six vertices (disconnected included), with exact
absorption probabilities: [`../pair_collision_toy/BUD_RECURRENT_LEMMA.md`](../pair_collision_toy/BUD_RECURRENT_LEMMA.md),
[`../pair_collision_toy/bud_recurrent_lemma.py`](../pair_collision_toy/bud_recurrent_lemma.py).

With four actives the possible sinks are the matchings of size 0, 1 and 2. Every state reached by
at least one BUD holds the keeper–tip bond, so `B ≥ 1` on every slice the coast starts from and
thereafter; the sinks reachable from any matched pair are therefore exactly two — two disjoint
bonds, and one bond with two isolated actives — which is what the depth-3 strongly-connected-
component condensation of all 97 matched-pair coasts finds (largest closed communicating class:
one vertex). `B` is non-increasing under BUD, which is why the chain drains rather than cycles.

For the original pair, `L = 4321/44100 ≈ 0.098`, with `a_0 = (43/50, 7/50)` and
`a_1 = (6721/8820, 2099/8820)` over (two disjoint bonds, one bond + two isolated). The chain
reproduces the full-graph coast exactly at `t = H, …, H+3` and is within `10⁻³⁰` of `L` by
`t = 64`.

### 3.3 Three fates

Proposition 3 makes the long-run residue of a history a single number, `L`. Combining it with
whether the difference was expressed at all gives three exhaustive cases.

- **Inert.** `D_slice(H) = 0`. The archive difference never entered the slice. Both lineages coast
  from the same distribution, so `L = 0` trivially, and KEEP is also identical for the two
  lineages. The archive is redundant for this pair's difference: both archives supply the same
  CONTACT opportunities.
- **Washout.** `D_slice(H) > 0` but `L = 0`. The difference was expressed and then spent entirely on
  the coast.
- **Durable.** `L > 0`. Some of the expressed difference is permanent: a lasting tendency in the
  distribution over presents, with no archive present.

On the 11 matched pairs of the depth-2 set the counts are 3 inert, 0 washout, 8 durable, with `L`
taking six distinct values. Pairs that share an absorption structure share `L`; (0,1) and (0,6)
both give `4321/44100`, and (8,10), whose two archives have the same quiet-degree signature (3,4)
on both sides, gives the largest value, `4/15`. The signature is not the carrier.

On the 97 matched pairs of the depth-3 set all three fates occur: 22 inert, 5 washout, 70 durable,
of which 75 are expressed. The five washouts are the first pairs on which expression does not
entail durability; they are why the depth-2 headline of the remark below is a special case rather
than a law.

### 3.4 The fork law

What decides the fate? Among expressed pairs, the enumeration gives one answer with no exceptions.

> **Observation (fork law).** On the enumerated depth-2 and depth-3 sets, an expressed pair is
> durable if and only if the coast has at least two reachable sinks.

Two of the four implications are immediate. If only one sink is reachable, both lineages absorb
into it with probability one, so `a_0 = a_1` and `L = 0`. And if `L > 0` the absorption
distributions differ, which requires at least two sinks. The content of the law is the remaining
direction: on every expressed pair with two reachable sinks, the lineages split between them
unequally. This holds on all 75 expressed depth-3 pairs and all 8 expressed depth-2 pairs, with no
exceptions, and it is verified rather than proven. Nothing in Proposition 3 forbids two lineages
with different transient distributions from absorbing identically; whether the BUD-only projection
kernel can ever do this from a reachable matched pair is open.

The qualifier *expressed* is required. Fifteen inert depth-3 pairs have two reachable sinks and
`L = 0`, because their lineages coast from identical distributions and two exits cannot separate
what is already the same. The implementation carries an assertion exhibiting these fifteen so the
qualifier cannot be dropped in a later revision.

The two conditions account for the depth-3 set exactly. Of the 97 pairs, 85 have two reachable
sinks and 12 have one. The 85 are the 70 durable pairs together with the 15 unexpressed two-sink
pairs above; the 12 are the 5 washouts and 7 of the inert pairs. Every durable pair has two
reachable sinks and every washout has one — the single-sink mechanism, exact on this set.

Both washout examples named here have a single reachable sink. Pair (22,26) is expressed at the
first event (`D_slice(1) = 1/6`) and more strongly at the second (`D_slice(2) = 17/90`), yet its
coast reaches one sink and `L = 0`: a mark that strengthens and then drains, with no fork to hold
it. Pair (22,25) is menu-equivalent at the first event (`D_slice(1) = 0`), expressed by the second
(`D_slice(2) = 17/120`), and also reaches one sink with `L = 0`. Both are washouts. Together they
are the two counterexamples to the depth-2 criterion of the next remark: (22,26) is expressed at
step one yet has `L = 0`, and (22,25) is menu-equivalent at step one yet expressed after it.

> **Remark (depth 2 as a special case).** On the depth-2 set two stronger statements hold: every
> expressed pair is durable, and a pair is inert if and only if `D_slice(1) = 0`, so its fate is
> decided by the first event. Both fail at depth 3, by the two pairs above. The first fails because
> washout pairs exist; the second because equality of the one-step projected successor
> distributions is not preserved by the dynamics. Aggregate one-step equality is not a
> bisimulation of the two lineages; the invariant that would be needed is a per-mediator
> structural equivalence of menus, which is not a one-step check.

### 3.5 Reading

The fork law relocates the question. Durability is not a matter of how much the past changes the
present, or how early. **[rev]** Pair (22,26) is marked more strongly than 20 of the 70 durable
pairs at the second event (`D_slice(2) = 17/90`; 20 of 70 at the first event, 18 of 70 at the
third) and loses everything. What matters is the shape of the present's own future under the
archive-free kernel: where the coast can end in only one place, every expressed difference is spent
on the way there; where it can end in two, the difference in which end is reached is permanent.

Durability is therefore a property of the future, not of the past. The past can leave a lasting
mark only where the coast forks.

This is consistent with the ensemble framing adopted throughout. `L` is a difference between two
absorption distributions, that is, a difference in how often each lineage's present ends up
fragmented rather than paired. No single present records its lineage. The residue of a history is a
probability of a shape, not a shape.

### 3.6 Scope

All statements in this section concern the `k = 1` rule, uniform selection over individual events,
the CONTACT coupling of the first paper, and the depth-2 and depth-3 matched-pair sets from the
four-vertex active path. Proposition 3 and the Lemma hold for any seed under these rules. The fork
law is an exact observation on the enumerated sets and is not claimed beyond them. Which seeds give
a coast with one reachable sink and which give two has not been characterised; that
characterisation is the natural next question for this model, and is independent of the
address-based coupling proposed for the following paper.

## 4. Summary and open questions **[draft for review]**

Deleting the archive does not delete the whole of what it did. On the archive-free coast the
distinction between two lineages is non-increasing and settles at an exact limit `L`, the
total-variation distance between where the two lineages end up. Because every recurrent class of
the coast is a single absorbing matching, "where they end up" is a choice among a few final shapes,
and `L` measures how differently the two lineages make that choice. Whether the past leaves a
lasting mark is then decided by the present's own future: on the enumerated sets an expressed
difference survives exactly when the coast has two reachable exits, and is spent entirely when it
has one, however strong or early the imprint was.

Three questions remain open. First, the fork law: whether two lineages with different transient
distributions can ever absorb identically when two sinks are reachable. Second, which seeds give a
coast with one reachable sink and which give two. Third, whether the three fates, and the fork
law, persist beyond the depth-2 and depth-3 matched-pair sets from the four-vertex path. None of
these needs the address-based coupling of the next paper; each is a question about the BUD-only
coast.

## Reproducibility **[draft for review]**

All numbers are exact rationals computed by scripts in the repository
(`github.com/kekekatie/geometric-impedance`, `exploratory/accretion_pilot/`), each of which asserts
its claims and exits non-zero on failure:

| result | script |
|---|---|
| Proposition 3, `L = 4321/44100` for the original pair, coast reproduction to `t = H+3` | `endogenous_present_width/coast_asymptote.py` |
| depth-2 fates and `L` values (11 pairs) | `endogenous_pair_robustness/pair_robustness.py` |
| depth-3 fates, fork law, washout exemplars (97 pairs) | `endogenous_pair_robustness/depth3_criterion.py` |
| Lemma (recurrent classes), exhaustive `n ≤ 6` | `pair_collision_toy/bud_recurrent_lemma.py` |
| §3.5 ranking of (22,26) against durable pairs | `transmission_paper/checks/soft_claim_22_26.py` |

## References

- Niedzwiecki, K. T. (2026). *When the past matters: Retained structure, readable traces, and
  causal relevance in two growing graph models.* Zenodo. Concept DOI `10.5281/zenodo.22759878`
  (version `10.5281/zenodo.22759879`). CC-BY-4.0.
- **[draft for review]** Kemeny, J. G., & Snell, J. L. (1960). *Finite Markov Chains.* Van Nostrand.
  (absorbing chains, absorption probabilities)
- **[draft for review]** Cover, T. M., & Thomas, J. A. (2006). *Elements of Information Theory* (2nd
  ed.). Wiley. (data-processing inequality)

---

## Revision notes (2026-09-25)

1. **§3.2 [rev]:** "On every seed enumerated here the recurrent classes are singletons" is now a
   Lemma for any seed (proof sketch plus exhaustive check up to six vertices). The paragraph on
   sinks now derives "exactly two reachable sinks" from the Lemma and `B ≥ 1`; the depth-3 SCC
   confirmation is kept as corroboration.
2. **§3.5 [rev]:** "marked more strongly than several durable pairs" is now "than 20 of the 70
   durable pairs at the second event", checked by `checks/soft_claim_22_26.py`, which reproduces
   (22,26)'s `D_slice = 1/6, 17/90, 539/2700` and `L = 0` exactly. The draft's "residual soft
   claim" is resolved.
3. **§3.6:** "Proposition 3 holds for any seed" is now "Proposition 3 and the Lemma hold for any
   seed".
4. **New, for review:** the Abstract, §4, the Reproducibility table and two classic references.
   No other text was changed.
