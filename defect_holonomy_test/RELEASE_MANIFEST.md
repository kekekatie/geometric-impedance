# Defect-Holonomy Test — frozen results bundle (paper citation)

This bundle is the immutable result set for the arrow-of-time / geometric-memory
paper. Cite the frozen reference so the paper references one fixed state:

- **Release branch:** `release/defect-holonomy-v3` (pinned to the commit of this
  file). This environment's managed git remote does not accept tag pushes, so a
  pinned branch stands in for a tag.
- **Immutable anchor:** the commit SHA that this `RELEASE_MANIFEST.md` lands on
  (reported in the session) — the true fixed reference regardless of ref name.

## The result, in one line

**A matched theorem pair, constructively verified:** on the ideal quasicrystal a
perfectly rigid tiling *cannot* carry perpendicular-space (address) holonomy —
every closed loop heals, exactly and provably; on a rational approximant it
*must* carry holonomy, quantised at the frozen phason misfit `π⊥(M)`, hitting
pre-registered values across four convergent orders on both substrates, and
shrinking geometrically toward zero (ratio `√2−1` for Ammann–Beenker, `1/φ` for
Penrose) as the crystal approaches perfection. Memory is the flaw.

## Frozen artifacts

| File | Contents |
|---|---|
| `phase0_registration.json` | Pre-registered holonomy quanta `π⊥(M_a)`, `π⊥(M_b)` and derived shrink ratios, committed **before** construction. |
| `results/v3_torus_pricelist.json` | E4+E2 torus measurement: measured quantum vs registered quantum, 4 orders × 2 substrates, with measured shrink ratios. All orders hit registered. |
| `results/theorem_verification.txt` | Brute-force confirmation of the rigid-edge holonomy theorem: `ker(π∥)∩Z⁴={0}` (AB), `=Z·(1,1,1,1,1)` (Penrose), `π⊥` of the kernel = 0; v2 loop-sums literally `m=0`. |
| `summary.json` | E0 metric validation + v1/v2 defect diagnostics (healers, `√2+1`/`φ²` canary artifacts, boundary-escape). |
| `FINDINGS.md` | Full narrative chain, iterations 1–4b: metric E0; v1 heals / ramp artifacts; v2 topology-correct-but-heals via boundary escape; iteration-3 theorem; iteration-4 torus crown; iteration-4b surgical wall. Negative results retained with equal prominence. |
| `figures/v3_approximant_winding_memory.png` | The winding-loop figure + price list. |

## Provenance / integrity notes for the paper

- **Split convention** (torus): edges classified against the substrate's own
  stars at the floating-point floor; perp increments taken from the *ideal*
  projection — holonomy = frozen phason strain integrated around the loop.
- **Integrity locks upheld throughout:** defects made by tile-level construction;
  address measured by lift-by-integration from edge geometry alone; the
  displacement-ramp method formally rejected as an injection of non-exactness.
- **Canary signatures:** `1+√2` (AB), `φ²` (Penrose) — seam-misclassification
  artifacts from v1; absent in v2/v3.
- **Open (flagged):** v3.2 seamless phason-shear approximant + Bravais dipole —
  the surgical robustness / §6 statistics arc. The naive planar approximant
  refuses motif-tiling (imperfection must be worn globally, not seam-confined);
  construction path specified in `FINDINGS.md` iteration 4b.

## Reproduce

```bash
pip install numpy scipy scikit-learn matplotlib pandas
cd defect_holonomy_test
python3 phase0_prereg.py            # (re)register quanta
python3 run_dh.py                   # E0 + v1/v2 diagnostics
python3 verify_holonomy_theorem.py  # the theorem
python3 torus_holonomy.py           # E4 + E2 price list
python3 render_figure.py            # the figure
```

Deterministic; fixed seeds. Reconstructed machinery reuses `reverse_loop_test/`
(geometry, walker, stats). Predecessor result: `reverse_loop_test/FINDINGS.md`.
