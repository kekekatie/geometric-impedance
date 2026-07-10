# Penrose fidelity — RESOLVED (mechanism corrected)

**Status:** fixed in `reverse_loop_test/geometry.py`. Max interior coordination
now **7** (was 10). AB untouched. All perp-space tripwires hold.

## The correction to the diagnosis (revise, don't massage)

`PENROSE_DIAGNOSIS.md` located the fault at the **acceptance window** (empirical
convex hull vs exact four-pentagon occupation domain) and proposed replacing the
window / gating vertex acceptance on it.

Diagnosing before editing (per the handoff) showed the window is **not** the
mechanism:

- The empirical-hull window in `_compute_depth` is used **only** to compute
  `depth`/`zone`. It never gates a vertex or an edge. Changing it cannot cap
  coordination.
- The over-coordinated vertices sit near the **centre** of perp space
  (|perp| ≤ 0.62, mean 0.365; typical interior |perp| ≈ 0.90), i.e. deep inside
  any window — shrinking the pentagon would not remove them.
- Root cause: the de Bruijn offset recipe forced **Σγ = 0.5**. A pentagrid gives
  a faithful P3 Penrose **only when Σγ ∈ ℤ**. Σγ = 0.5 produces a *generalized*
  Penrose tiling — a spurious 5th residue class (0) and vertex types up to
  coordination 10. Σγ = 0.25 → coord 8; Σγ ∈ {0,1,2} → coord 7 (true P3).

The diagnosis's *picture* was right (four pentagons, residue classes {1,2,3,4},
coord 7). That tiling is exactly what Σγ = 0 produces. It just arises naturally
from the correct offset, rather than needing a window filter bolted on
(commandment 3: let the true tiling emerge from the true construction).

## The fix

`SUBSTRATES` now carries `gamma_sum` (penrose = 0.0, ammann_beenker = 0.5). The
default gamma recipe pins the offset sum to it; individual offsets stay generic.
`Patch(..., gamma_sum=0.5)` reproduces the legacy generalized-Penrose substrate
for diffing. **AB path unchanged** (K arrays byte-identical old vs new).

## Definition of done — met

- Max interior coordination = **7**, both small and large patches (R = 10/16/22). ✓
- Connected; 4 residue classes {1,2,3,4}; mean interior degree ≈ 4.0. ✓
- Degree histogram stable across patch sizes (no size-dependent tail). ✓
- Not singular: min vertex distance = 0.618 (thin-rhombus short diagonal),
  robust under offset perturbation — no coincident/degenerate vertices. ✓

## Tripwires (perp/holonomy must not move) — all hold

- **Theorem-1** (`verify_holonomy_theorem.py`): identical. AB ker(π∥)={0};
  Penrose ker = ℤ·(1,1,1,1,1), ‖π⊥‖ = 3.5e-16; all tight-loop sums zero.
- **Torus quanta** (`torus_holonomy.py`): every order still hits the registered
  quantum. Penrose 0.236068 / **0.145898** / 0.090170 / 0.055728 (ratio 1/φ);
  AB 0.414214 / **0.171573** / … Only incidental `cell_vertices`/`seam_edges`
  counts shift (faithful phase fills the cell slightly differently, fewer seam
  misfits) — the physics is unchanged.
- **Reverse-loop Outcome A**: closed loops heal to 3.3e-16; open-walk residue =
  ‖Δperp‖ to 8.9e-16. Positional, holonomy-free — preserved.

## Expected to shift (re-run and re-report, per handoff) — NOT yet done

- Penrose **degree-based** analyses on other branches: coordination-gap Spearman
  (was 0.967) and Goldilocks intermediate-degree persistence
  (`penrose_gap_analysis`, PR #1 branch). These legitimately change with the
  faithful substrate; they are not in this branch and need a separate re-run.
- Reverse-loop sensitivity `d_zone` (~0.69 Penrose) and gap→residue Spearman are
  distributional and may shift slightly; conclusions (Outcome A) unaffected.
