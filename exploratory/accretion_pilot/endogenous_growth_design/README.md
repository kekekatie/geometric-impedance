# Endogenous growth by local graph rewriting — design + feasibility (pre-experiment)

**Design proposal with tiny deterministic feasibility checks. No production experiment.**
Isolated on the existing branch; v1–v14 and `SYNTHESIS_v1_v14.md` preserved. No merges,
publishing, sealed-study access, or large simulations. No cosmology / energy-free-growth /
inexhaustibility claims. We stop before the production run for Astra's review.

## The pivot

The track and the traveller are inseparable — so **remove the traveller**. Instead of a
walker on a substrate (v1–v14), the world here is a **graph that rewrites itself**: local
*events* match a bounded pattern and rewrite it, possibly creating vertices/edges.
Eligibility is purely local — no walker, global target, history label, or A/B rule.

## Central question — three separate properties

Can purely local structural change simultaneously **(1)** leave consequences that
distinguish prior histories, **(2)** change which subsequent events are possible, and
**(3)** extend the graph beyond a finite pre-enumerated catalogue? Property (1) is the hard
one, because **genuinely independent local events commute** — so history can only be
recorded by **competition** (overlapping events that disable one another), and only when
symmetry is broken.

## Recommended model — M1, "Competitive Accretion Grammar"

Vertex states `{A active, Q quiet}`; one directed rewrite `BUD(x,y)` on an **active bond**
`A–A`: the depositor `y→Q` (a persistent quiet apex inside a new triangle), the keeper `x`
stays active, and `k` new active tips are created. Adjacent bonds **compete** through a
shared vertex, which makes the rule **non-confluent** — order leaves a permanent structural
trace. `M2` (context-free budding) is retained as the **confluent null** ("growth that
forgets"); `k=0` is the **persistence-without-extension ablation**.

See [`DESIGN_NOTE.md`](DESIGN_NOTE.md) for the full rule table, before/after patterns,
scheduling/resources, failure modes, and the proposed first experiment;
[`figures/rule_before_after.png`](figures/rule_before_after.png) for the schematic.

## Verified (tiny deterministic checks — no stochastic sweep)

`python3 feasibility_checks.py` → `results/feasibility_report.txt`. Confirms:

- **Fixed invariants:** `ΔV=k, ΔE=k+1, ΔQ=+1, ΔA=k−1` per event ⇒ tallies are set by the
  event count alone, so **no count can distinguish histories** — only graph shape can.
- **Non-confluence:** `BUD(a,b)` vs `BUD(b,a)` on `a–b–c` diverge permanently (not
  joinable); the mirror-symmetric pair washes out — memory needs competition **and** broken
  symmetry.
- **History does work:** two count-matched length-2 histories give **non-isomorphic**
  graphs with **different** future eligible-event counts (4 vs 2); length-2 histories yield
  11 distinct isomorphism classes under identical tallies.
- **Frontier fate:** `k=0` disappears, `k=1` stalls (via stranding), `k≥2` proliferates —
  continuation at `k≥2` is **built into the rule**, stated as such.
- **Ablation:** `k=0` leaves non-isomorphic quiet-patterns with **no** new vertices —
  persistence separable from extension.

## Files

- `DESIGN_NOTE.md` — the design.
- `feasibility_checks.py` → `results/feasibility_report.txt` — bounded deterministic checks.
- `make_figure.py` → `figures/rule_before_after.png` — before/after + critical-pair schematic.

## Reproduce

```bash
python3 feasibility_checks.py   # ~1 s, exact isomorphism checks on tiny graphs
python3 make_figure.py          # writes the schematic
```

**Status: awaiting Astra's review of the model before any production experiment.**
