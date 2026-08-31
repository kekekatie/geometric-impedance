# SEAL RECORD — radius-saturation design suite (SEALED / NOT RUN)

**Seal type:** documentation-only **design** seal. The design is frozen; **the study has NOT been
run.** No scientific outcomes, address values, LDOS, β, or targets were accessed to produce this
seal. The science branch was not touched.

**Sealed on:** 2026-09-01 · **Branch:** `gpt/workbench`
**Reviewed parent design commit:** **`e3d7af3`** — Work-GPT/Sol's final concordance review approved
this commit as the final reviewed design state. This seal commit is its child and changes only the
three manifest status headers (`DRAFT / NOT sealed` → `SEALED / NOT RUN`) and adds this record.
**Authority:** sealing authorized by the human principal (Katie); design reviewed and approved for
sealing by Work-GPT/Sol.

---

## 1. Normative frozen artifacts (the sealed protocol)
These five files **are** the protocol. Hashes are of the exact sealed bytes; verify at the tag with
`git hash-object <path>` (git-blob) or `sha256sum <path>`.

| # | path | git-blob (SHA-1) | SHA-256 |
|---|---|---|---|
| 1 | `gpt_workbench/PHYSICAL_RADIUS_MANIFEST_DRAFT.md` (v7) | `e3c32a2df760627fd9b009929c24423a51522e9f` | `148301ab6e18af6bd03720495a12ddb64ecc48efb5376607b6cd43548606ed1a` |
| 2 | `gpt_workbench/MSD_ENDPOINT_MANIFEST_DRAFT.md` (v8.1) | `95814aac8ef1c9b570a757d2a92cd313a10b497e` | `4347f1e09df1de379fbbed28c0c6ca1093bc5d66cb525a28d7a790f9bdb53502` |
| 3 | `gpt_workbench/CONDITIONAL_NULL_MANIFEST_DRAFT.md` (v4.1) | `d88b91e519288a68f7bb5740d3b82cdbdef26964` | `9da947178befb0dc37c1e2e2409b1fd57637a7b7aea239cad7c00aa071e85bdf` |
| 4 | `gpt_workbench/DECISION_GATE_CONCORDANCE.md` | `a6cff0dd34b97ac088a340eac0938ddda27d1dbd` | `93f0b4ec6fd46525bad84c930435af81b2e982d763e4d8ace655da05b8192e4c` |
| 5 | `gpt_workbench/snapped_beta_times.txt` | `57be292518a34bd2f6ecc96c4db9ebc83722916c` | `5c2fdd32c5291775377c679b025e71fd8b17aa5ba4dc699d0727ad664251b506` |

*(Hashes 1–3 are the sealed versions carrying the `SEALED / NOT RUN` status header; their design
content is otherwise identical to the reviewed parent `e3d7af3`.)*

## 2. Supporting artifacts — PROVENANCE ONLY (not normative protocol)
These record how the design was reached and diagnosed. They are **not** part of the sealed protocol
and carry no normative force; a future conflict between any of these and the five normative artifacts
is resolved in favour of the normative artifacts.
- **Design reports / audits:** `LOCALITY_LADDER_REPORT.md`, `SIX_OFFSET_AUDIT_REPORT.md`,
  `EXTERNAL_LITERATURE_SCOUT_SYNTHESIS_DRAFT.md`, `EXTERNAL_SCOUT_CLAIM_AUDIT.md`,
  `PREFLIGHT_GEOMETRY_REPORT.md`, `PREFLIGHT_GEOMETRY_REPORT_V2.md`,
  `RESPONSE_TO_CONSOLIDATED_REVIEW.md`, `WORK_GPT_CONSOLIDATED_REVIEW.md`, `README.md`.
- **Diagnostic code + outputs (geometry/feature/synthetic only):** `locality_ladder.py`,
  `locality_ladder.csv`, `locality_final.csv`, `singleton_54.csv`, `singleton_audit_v2.py`,
  `matching_feasibility.py`, `preflight_geometry.py`, `preflight_geometry_v2.py`,
  `pad_convergence_check.py`, `benchmark_msd.py`, `benchmark_msd_grid.py`, `compute_checks_v3.py`.

## 3. Frozen design parameters (normative summary; manifests are authoritative)
- **Six offsets:** `(0.13,0.37) (0.29,0.11) (0.41,0.23) (0.05,0.47) (0.19,0.31) (0.37,0.09)`.
- **Nine family×tier configs:** small `silver e14 / golden e18 / platinum e16`; medium
  `silver e16 / golden e20 / platinum e18`; large `silver e18 / golden e22 / platinum e20`.
  **`M₉` always spans all nine.** **`M_perm,7`** spans the seven permutation-feasible configs
  (silver×3, golden×3, platinum e20); **platinum e16/e18 cannot pass the local-permutation stress
  control (G2)**.
- **Radius ladder:** `S = {2,4,8,12,16}`, reference `r=16`; `physical_extra(r)` dims 11/22/35/48/61;
  evaluated population = the `d_bound ≥ 16ℓ` common interior set, fixed across rungs.
- **Matching law (ratified):** distance-weighted additive stochastic assignment,
  `cost = feature_distance + λ·U(0,1)`, **`k=32`**, **`λ=1.0`**, **Policy-A** escalation
  (32→64→full), 40-rep stable-seeded diagnostic; features = the M3 continuous physical family
  (`dens=g(2.0), deg, g(1.6), g(2.6), g(4.0), g(6.0), ψ_N, ψ_{N/2}, ψ_{2N}`).
- **Seeds:** address-permutation root `SeedSequence(20260829)` → 1000 children; capacity root
  `SeedSequence(20260830)` → 200 children (indices 0…199); locality-ladder registry
  `SEED_ROOT=20260829` via `blake2b(SEED_ROOT|key)` keyed substreams; parity deterministic (no seed).
- **Grids:** boundary-monitoring grid `linspace(0, 8, 161)`, `Δt=0.05`; 48 snapped β-fit times on
  `[2,8]` (frozen list in `snapped_beta_times.txt`); `L=200` launches, batch 50; `B=1000`
  permutation reps; 200 capacity draws; boundary crossing `ΔP_strip ≥ 0.01`; `t_bound* > 8` strict.
- **Gates (G0–G8, per `DECISION_GATE_CONCORDANCE.md`):** primary coherent transport ⟺
  `G0 ∧ coherentG1 ∧ G2 ∧ G3 ∧ G4 ∧ G6`; the cross-engine non-reproduction modifier ⟺
  `classicalG1 ∧ G5` (a G5 failure does not erase the coherent result). Thresholds: G1 `R²_fit ≥ 0.90`;
  G2 `q_ref < 0.05`; G3 `M₉,address > δ_cap`; G4 `R_kill ≥ 0.70` (any undefined required reduction →
  global G4 undefined → mixed); G5 `classical ≤ 0.2 × coherent`; G6 `M₉ of ΔR²_resid > δ_cap`; G7
  parity descriptive only (no threshold); G8 Westfall–Young over the 7 feasible cells.
  **`δ_cap`** = 95th percentile of the 200-draw `M₉` capacity distribution; **`ρ*=0.25`** classification
  heuristic (not an equivalence margin). Frozen top-line claim: *"the address representation predicts
  heterogeneity in full-spectrum wavepacket spreading beyond the frozen physical descriptions and
  controls."*

## 4. Implementation status — PENDING (not sealed here)
Implementation of the sealed protocol (the production run code) is **pending** and is **not** governed
by this design seal. Before any scientific run, the implementation **must undergo conformance review**
against these five normative artifacts. The diagnostic code in §2 is design tooling, **not** the
sealed study implementation. **The study has NOT been run.**

## 5. Post-seal amendment policy
Once sealed, **any** change to a normative artifact (§1) — wording, threshold, gate, statistic,
config set, seed, grid, or parameter — requires a **dated, explicit amendment record** committed
**before any scientific outcome is accessed**. The amendment record must name: the artifact and exact
change, the reason, the author/authority, the date, and the parent seal. **No outcome, address value,
LDOS, β, or target may be accessed until such an amendment record (if any) is in place.** Silent
edits after outcome access void the pre-registration guarantee this seal exists to provide.

---
*Sealed at reviewed design commit `e3d7af3`. Documentation-only; nothing run; science branch
untouched. See the annotated Git tag for the immutable seal reference.*
