# PROTOCOL — referee-proofing checks 3 and 4 (pre-registered)

*Pre-registered 2026-11-05 (folder/branch labelled 2026-11-06 per the brief), committed
**before** running checks 3 and 4. For Katie / Fable / Astra. Exploratory diagnostics on
worlds already grown, before drafting Paper 1. A null or ambiguous outcome is an acceptable
result. Nothing here changes the frozen engine, the frozen reader, or any audited result.*

## Scope and framing

These checks probe a literature-suggested **mechanism** for the recurring "never A" readout:
the A/B fork may be the two orientations of a **Conway worm** (Onoda–Steinhardt–DiVincenzo–
Socolar 1988; Hann–Socolar–Steinhardt, PRB 94, 014113, 2016; Jang–Robinson, arXiv:2504.10838,
2025 — exactly 5 non-expansive "worm" directions). "Selects B" is kept strictly separate from
"excludes A" throughout. Every numerical statement is model-specific and reported with the move
class and tolerance that produced it.

## Frozen inputs (read-only)

- Engine / lattice: `engine_bridge` → `L`, `D`, `S` (frozen `84130b9` on
  `codex/manuscript-reconciliation`, via `EFP_SNAPSHOT`).
- Perp-space lift: `perp_map` → `lift`, `perp`, `edge_dir`.
- Replay helpers: `pilot_common` → `grow`, `skin_of`, `dead_sites`.
- Reader: `archive-free-reader/skin_reader.py` → `read(payload)`; adapter
  `phase4_readout` → `build_payload`, `classify`, `load_forks`, `B_JAMS`.
- Direction bases, identical to the reader: `PHYS[j] = exp(i(18+72j)°)` (parallel space),
  `PERP[j] = exp(4πij/5)` (internal space), j = 0..4. Both sum to zero, so `(1,1,1,1,1)` lies
  in the kernel of each projection.
- The **five worm / non-expansive directions** are the five physical edge directions `PHYS[j]`
  (lines are undirected, so `PHYS[j]` and `−PHYS[j]` are the same direction).

Reproduction gate (must pass before these checks; it did, see HANDBACK): the archive-free
528-window readout reproduces **111 B / 64 ambiguous / 353 empty-incompatible / 0 A**.

## Datasets

- **22 forks**: `RD.load_forks()` worlds `[0,1,2,3,5,7,11,12,13,15,19,21,23,25,28,29,30,37,39,40,41,46]`;
  fork options `cs = (A, B)` with `A = cs[0]`, `B = cs[1]`.
- **11 jammed bands**: the archive-free worker's retained band at the recorded jam checkpoint,
  `worker_band_exports.json` (`B_JAMS` = (5,0),(7,0),(7,1),(15,0),(19,0),(19,1),(21,0),(21,1),
  (28,0),(28,1),(29,1)).
- **49 recovery-case skins**: the archive-free-reader recovery payloads under the frozen
  snapshot (`archive-free-reader/results/cases/*.json`), the band data behind the 49/49 recovery.
  Reader **evidence** is each payload's surviving-skin tiles; the analyst `reference.true_index`
  is used only to label true A/B for reporting, never as reader input.

## Two reader conventions (fixed here)

For a tile set we build the frozen payload (`RD.build_payload`) and call `SR.read`. The reader
returns the compatibility region **F** (polygon in the 2-D perp/offset plane), its area, and the
area of F ∩ each hypothesis (`intersections[0]`=A, `intersections[1]`=B).

- **Open convention** (the reader's native rule): hypothesis *h* is compatible iff
  `intersections[h] > AREA_TOL` (`1e-9`); `selected` is the unique compatible hypothesis when
  `area(F) > 1e-12`, else `None`.
- **Closed convention**: hypothesis *h* is compatible iff F ∩ (h's half-planes) is **feasible as
  a closed region** (an LP feasibility test; a zero-area point or segment counts as compatible);
  `selected_closed` is the unique closed-compatible hypothesis when F itself is closed-feasible,
  else `None`. The closed convention can only **add** compatibilities (zero-area boundary
  contacts), so it can turn an open "B-only" into an "A-and-B" tie.

*Note:* Katie's `check2_conventions.py` was not attached to this run. The closed convention above
is reconstructed directly from the reader's own region semantics (feasible closed region incl.
measure-zero contact). It reproduces check 2's qualitative report (B-only falls, some headlines
tie). If the canonical `check2_conventions.py` is later attached, these counts should be
reconciled to it; the open convention is the reader's own and is not reconstructed.

Outcome labels (both conventions): `correct` = selects B (index 1); `wrong` = selects A
(index 0); `ambiguous` = both compatible; `empty_incompatible` = neither compatible or F empty;
`unreconstructible` = reader could not lift/reconstruct the skin.

---

## Check 4 — is the fork a worm flip?

### 4a. A/B forced-consequence diff (all 22 forks)

**Method.**
1. For each fork, build `Sstar + A` and `Sstar + B`.
2. **Forced closure** (move class: *forced only*): repeatedly place every frontier edge that has
   exactly one legal candidate (`D.candidates` == 1, `Patch.legal` true), in rounds, until no
   single-candidate frontier edge remains. **No free choices.** Cap 20000 rounds. Zero-candidate
   (locally jammed) edges are left in place and counted, not resolved.
3. Diff = symmetric difference of the two closures' decorated-key sets
   (`A_only = A∖B`, `B_only = B∖A`, `diff = A_only ∪ B_only`).
4. Lift the diff tiles (`perp_map.lift`). Classify the diff as a **single strip along one of the
   5 directions** iff ALL hold:
   - (i) the diff tiles form exactly **one** edge-connected component (empty diff → "no_difference");
   - (ii) the diff's principal physical axis (PCA on tile centroids) lies within **12°** (mod 180°)
     of one of the 5 `PHYS` directions;
   - (iii) **aspect ratio** length/width ≥ **3**, where length = centroid extent along that axis
     and width = extent transverse, in units of S.
5. Report per fork: `n_A_only`, `n_B_only`, component count, nearest worm-direction index and the
   angular residual, length and width (S units), aspect ratio, `single_strip` (bool), and —
   cheap Ammann proxy only — whether the strip is bounded transversely by two lines along the worm
   direction and their separation (width). Lift conflicts in the diff are reported if any.

**Prediction P4a:** in **≥ 20 of 22** forks the A/B forced-closure diff is a single strip along
one of the 5 directions.

### 4b. Crossing vs parallel arcs

**Worm line (per world).** From 4a: direction `d_w` = unit vector of the fork's strip worm
direction; point `p_w` = centroid of the fork's diff tiles; transverse unit `n_w = i·d_w`. Worlds
whose 4a diff is **not** a single strip have `worm_undefined` and their arcs are reported
separately, excluded from the crossing/parallel comparison.

**Arcs (matched tile count).** An arc is a connected tile set of **exactly K = 32 tiles** grown by
nearest-first BFS over edge adjacency from a seed tile (one component). Seeds = the band/skin's
boundary tiles in angular order about the centroid, sub-sampled to ≈ 20 seeds per band/skin
(step = max(1, n_boundary // 20)). K = 32 was fixed by a feasibility probe (100% reconstruct;
≈ 88% positive-area F) with **no reference to A/B outcomes**.

**Classification (geometric, fixed before scoring).** For arc tile centroids, let
`s = Re((centroid − p_w)·conj(d_w))`, `t = Re((centroid − p_w)·conj(n_w))`.
- **crossing**: `min(t) < −0.5·S` AND `max(t) > +0.5·S` (the worm line passes through the arc,
  ≥ half a tile each side).
- **parallel**: NOT crossing, AND `(max t − min t) < (max s − min s)` (elongated along the worm),
  AND the arc's PCA principal axis within **20°** of `d_w`.
- **oblique**: neither (reported, not in the binary).

**Scoring.** Score every arc with the frozen reader under both conventions; report outcome counts
by class (crossing / parallel / oblique), separately for the 49 recovery skins and the 11 jammed
bands.

**Predictions:**
- **P4b:** crossing arcs select B far more often than parallel arcs; parallel arcs are mostly
  ambiguous.
- **Falsifier:** any arc that uniquely selects **A** (under either convention) falsifies "never A"
  and is reported prominently (world, checkpoint, arc seed, convention, tiles).

---

## Check 3 — loop closure, and step vs slope on the 11 jammed bands

### 3a. Loop closure

**Method.** For each jammed band, find the boundary legs (rhombus edges of length S belonging to
exactly one tile) and chain them into closed vertex loops (outer loop and inner loops around
cavities/scars). For each loop, sum the **raw lifted edge increments** `±e_j` from
`perp_map.edge_dir` along consecutive loop vertices (not differences of a precomputed global lift,
so a genuine holonomy would show): `H ∈ Z^5`. Report `b∥ = Σ H_j PHYS[j]`,
`b⊥ = Σ H_j PERP[j]`, and the index component `Σ_j H_j`. Also report the band's global lift
conflict count (`perp_map.lift`).

**Prediction P3a:** `|b⊥| = 0` (≤ `1e-6`) on every legal-rhombus loop (repo Theorem 1,
`defect_holonomy_test/`; a non-zero value means a genuine defect or a bug).

### 3b. Local offset profile

**Method.**
1. Order each jammed band's tiles by angle about the centroid; slide an **arc of K = 32 tiles**
   (fixed by the same feasibility probe), step **1 tile**, around the ring (cyclic).
2. For each position, build the reader payload for the arc and compute F's **Chebyshev centre**
   `(x1, x2)` (centre of the largest inscribed circle, by LP) and **radius**. Positions where F is
   empty/unreconstructible are recorded as gaps.
3. Plot the two centre components against mean arc angle around the band (one figure).
4. Classify each band's profile with a criterion fixed here. Let `J_i = |centre_{i+1} − centre_i|`
   over defined consecutive positions and `TV = Σ J_i`; let `Wk` = the largest sum of `J` over any
   window of **k = 3** consecutive positions.
   - **step**: `Wk / TV ≥ 0.50` (half or more of the total offset change is concentrated in ≤ 3
     positions);
   - **ramp**: `Wk / TV ≤ 0.25` (change spread smoothly);
   - **mixed**: otherwise.
   Steps are the positions with `J_i ≥ 0.25·TV`.
5. Report each step's location relative to the dead sites and scars, and the step direction
   (the displacement `centre_{i+1} − centre_i` in the perp plane) relative to the 5 worm
   directions and to the fork worm (from 4a).

**Predictions:**
- **P3b:** profiles are step-like, with steps along worm directions **other than** the fork
  worm's. (Candidate explanation for "never A" from the literature review; not established.)
- **P3c:** if a step runs **parallel to the fork worm** in any band, that band is the place to
  look for an A-only arc (cross-referenced with 4b).

---

## Deliverables

`HANDBACK.md` (plain language first), machine-readable results per check under `results/`, one
figure per check under `figures/`, and focused tests under `tests/`. Commit and push to
`claude/referee-checks-2026-11-06`; no merge, no force-push. "Selects B" is reported separately
from "excludes A"; all move classes and limits are stated.
