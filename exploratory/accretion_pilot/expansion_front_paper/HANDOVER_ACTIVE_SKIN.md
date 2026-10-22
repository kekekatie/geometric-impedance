# Active-skin research handover

Prepared 22 October 2026 for a pause in work. Branch: `codex/expansion-front-checks`.
Repository: https://github.com/kekekatie/geometric-impedance

This is an exploratory extension of the expansion-front checks, not a manuscript claiming matter, mass, physical time or a universally valid local universe. Original scientific baseline: `d4e00c5d4396c38bd69b265907b5f3d6c5bc030a`. The earlier figure checkpoint is `9222abb39edfcc86070f29b728f1e84ab1da3d86`.

## Start here

All source scripts, plans, source data/checkpoints and generated scientific outputs for this work are under this directory. Nothing needs the previous chat's workspace paths or Downloads directory to run. Read-only local HTML viewers embed their data and need no server. Download/open them locally; GitHub source view is not an interactive viewer.

| Experiment | Directory / viewer | Main source |
|---|---|---|
| Slice-12 film (called `slice12-film` in user Downloads packages) | `slice12/WATCH-SLICE12.html` | `slice12_film.py` |
| All-frontier choice tracking | `choice-tracking/WATCH-CHOICES.html` | `choice_tracking.py`, `summarize_choices.py` |
| Exposing a choice | `exposure-test/OPEN-EXPOSURE-TEST.html` | `exposure_test.py` |
| Support ancestry / changed choice 29 | `ancestry-test/OPEN-ANCESTRY.html` | `ancestry_test.py`, `ancestry_package.py` |
| Local candidate information | `local-information/OPEN-LOCAL-NOW-CHECK.html` | `local_information_test.py`, `local_information_package.py` |
| Self-maintaining skin | `active-skin/WATCH-ACTIVE-SKIN.html` | `active_skin_engine.py`, `active_skin_verify.py`, `active_skin_present.py` |
| Cold restart | `skin-restart/results.json` | `skin_restart.py` |
| Observer endurance tracker | `endurance/WATCH-ENDURANCE.html` | `endurance_capture.py`, `endurance_observer.py`, `endurance_audit.py`, `endurance_package.py`, `endurance_viewer.html` |
| Local response at slice 45 | `local-response/OPEN-LOCAL-RESPONSE.html` | `local_response.py`, `local_response_present.py` |

Each output directory has measurements and/or a report; `skin-restart/results.json` is interpreted in this handover. Protocols are the `*_PLAN.md` files and `ENDURANCE_PROTOCOL.md`. Existing manuscript-stage reports are preserved, not silently rewritten. The endurance JSON and viewer files are large because all inspected instances and links are retained; no file exceeds GitHub's 100 MB individual-file limit.

## Common case and provenance

Selected exceptional case `180fb0b920bb845b`, original world 21 / slice 8. Both continuing histories take original option B. Continuations 1 and 3 are one-based labels, streams `20810350027` and `20810365865`. Alternative-29 changes only continuation 1's legal choice at slice 29, consuming the same random draw. The original engine is imported through `figures.py`; fixed matching-rule templates are part of the rules, not archived input from these runs.

`results/geometry.pkl` is now intentionally versioned (302,352 bytes), along with the later checkpoint files. Only load these pickle files from a trusted checkout: pickle is executable serialization. Runtime caches, `__pycache__`, and a local `.venv` remain ignored. `CHECKPOINT_MANIFEST.json` hashes the deliverable files; `verify_checkpoint.py` checks them without loading pickle or rerunning the experiments.

## Verified findings

1. **Slice 12:** histories identical through slice 11 diverge at a two-way choice at 12. Original compatibility cut: 18 degrees/family 2; later cut: 162 degrees/family 3. Later covered differences contact the frozen earlier B-side comparison region by a vertex at 15 and an edge at 16. This compares histories, not interacting objects in one world.
2. **Tracking to 60:** continuation 1 makes later choices at 29 (edge open since before 20) and 44 (first observed open then); continuation 3 at 54 (open since before 40). Waiting alternatives stay unchanged. Record every original frontier edge, not just the selected site. The global scheduler affects selection order.
3. **Exposure:** forced additions during 19 and 43 expose the sites selected at 29 and 44. Each exposing tile alone reproduces the respective two candidates in the pre-step patch. Partial-step additions and omission patches are diagnostic tests, not complete alternative scheduler histories.
4. **Ancestry:** a 16-tile attachment-support graph reaches from 29 to 43, branching and rejoining. It is not a complete causal/constraint graph. Removing each of 267 other tiles separately at the final fixed attachment edge does not change its singleton candidate; joint/redundant constraints were not exhausted.
5. **Changed choice at 29:** the same later target opportunity appears before 45 instead of 44. Construction during 45 reduces its two candidates to one, placed during 46. Alternative steps 30–60 are all forced, without a jam. This is a scheduler-specific intervention result, not a universal causal chain.
6. **Local information:** 841 edge observations across 15 saved states, each at radii 1, 2, 3, 4, 6 S units: all 4,205 decorated candidate sets match the full patch. Radius 1 retains 8.64 half-tiles on average (mean 2.71% of the corresponding patch). This is not a measured physical width of now. It queries original edges only; artificially exposed crop edges are excluded.
7. **Active skin:** all **21,185 pre-step frontier candidate comparisons** and all ordered placements, statuses and post-step frontiers match the full-history reference over **310 steps**. Continuation 1 jams at **70 in both engines**; continuation 3 and alternative-29 reach **120**. Final retained/full half-tiles: **456/883**, **497/1056**, **538/1180** respectively. Radius fixed at 2*S. Whole tiles with a vertex near a true-frontier vertex are retained; the skin extends beyond that radius by the tile footprint.
8. **Cold restart:** worker-generated slice-60 checkpoints contain only retained tiles, true-frontier state, radius, RNG state, step/intervention metadata and format version. Original processes exit before fresh ones resume. All **12,078 post-restart candidate checks** and **130 steps** match, including ordered placements, frontier and RNG states. At checkpoint: **356/586**, **383/617**, **385/669** retained/full half-tiles. Serialized sizes: **20,091**, **20,886**, **21,117 bytes**. The jam at 70 is reproduced, not fixed.
9. **Endurance observer:** 60–70/120 windows, 2–4-edge clusters and decorated stars. Same-class candidate links: **45, 87, 74**; longest paths **1, 2, 1** links. The selected two-link example is continuation 3 at **97, 98, 99** (occurrences 2525, 2546, 2571). All **150,240** candidate-link witnesses were audited; 78 actual motif invariance checks and synthetic checks passed. Cross-class links are overlapping contacts, not independent decay channels. Numerical class canonicalization rounds dimensionless coordinates to 5 decimals; it is not symbolic exact arithmetic.
10. **Slice-45 local response:** among 19 observed additions, **tile #2 alone** is sufficient to remove the rejected option. Omitting it while retaining the other 18 restores both options; omitting any other single tile does not. It is itself legal on the pre-step patch. Failure is the vertex-compatibility rule at rounded coordinate **(0.383516, 0.145898)**, not overlap or duplicate placement. All 21 local queries (before, full step, 19 singletons) agree at radius 2*S. Necessary/sufficient means within these diagnostic additions, not every possible history. Survivor is verified placed at 46.

## What the architecture does and does not establish

The skin updates an explicit true frontier; it does not infer frontier from a cropped patch. A separate spawned worker accepts only STEP/STOP after initialization. The archive-owning verifier receives decisions and can stop on mismatch, but never returns archived geometry or repairs. Worker and verifier share the historical legality implementation: this tests retained-state equivalence, not independent mathematical correctness of that implementation. Cold restart supplies only serialized active state. Endurance capture is one-way and completes before observation begins.

The scheduler remains global: forced placement anywhere on the frontier takes priority, then origin-distance order selects a guess. “Only present information retained” and “fully local scheduling” are distinct requirements. Total memory can grow with boundary length. Finite successful runs do not prove state completeness for all geometries or futures. A jam, end of observation, or burial is not physical decay. Initial and final motif lifetimes are censored; same-class geometric links are not established persisting objects.

Katie's guiding idea shifted during discussion from an enclosing balloon to renewal throughout space; the current advancing-edge model does not implement that. Keep historical observation distinct from information accessible to the simulated present. The earlier soft-zone “about two tile edges” width was corrected for footprint leakage; see `../quiet_lasts_longer/README.md`. The June directional-balance paper is background, not a required input, and its PDF is not included in this checkpoint. Perpendicular-space diagnostics remain deferred.

## Exact reproduction commands

Run from repository root in PowerShell. These are instructions for a fresh session; housekeeping did not repeat the expensive growth experiments. Use an installed Python compatible with the pinned packages. The original run used the Codex bundled Python; `requirements.txt` records NumPy, SciPy, Matplotlib and Pillow versions.

```powershell
git switch codex/expansion-front-checks
Set-Location exploratory/accretion_pilot/expansion_front_paper
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
$py = (Resolve-Path ./.venv/Scripts/python.exe).Path
& $py verify_checkpoint.py
```

With the committed checkpoints present, any individual stage can run. To reproduce the whole sequence in dependency order:

```powershell
& $py checks.py
& $py geometry_checks.py
# Optional: regenerates the original two-prefix geometry cache and four figures.
& $py figures.py
& $py slice12_film.py
& $py choice_tracking.py
& $py summarize_choices.py
& $py exposure_test.py
& $py ancestry_test.py
& $py ancestry_package.py
& $py local_information_test.py
& $py local_information_package.py
& $py active_skin_verify.py
& $py active_skin_present.py
& $py skin_restart.py
& $py endurance_capture.py
& $py endurance_observer.py
& $py endurance_audit.py
& $py endurance_package.py
& $py local_response.py
& $py local_response_present.py
```

Output paths are relative to the scripts, not the caller's working directory. Helpers formerly outside the checkout (`summarize_choices.py` and `local_response_present.py`) are now portable. Regeneration can alter image bytes, timestamps/process IDs and pickle bytes even if the scientific values agree; the manifest verifies this saved snapshot, not byte-identical future computation. Review differences before regenerating the manifest with `& $py verify_checkpoint.py --write-manifest`.

## Viewer verification

Scientific stills were visually inspected. Endurance JavaScript passed Node syntax checking. The automated browser tool rejected local-file URLs, so no full browser interaction QA is claimed. No workaround was used. User-facing viewers are self-contained files, including the roughly 23 MB endurance viewer.

## Pending research and Argon's 3D proposal

No 3D engine or E8 experiment has been implemented. Argon proposes testing whether sheet intersections in a volumetric growth model could meet a moving front in repeatedly renewed sites, and whether extra spatial directions permit line structures to pass around each other. Preserve this as a motivation, not an established explanation of matter.

Intersection dimensionality alone does not imply indefinite renewal, stability, or a special response. Finite-width strips/sheets, the chosen growth law, embedding and timing must be specified. A crossing in a spatial drawing does not by itself establish a simultaneous collision. Before a 3D experiment, define what observable distinguishes it from the current model and which projection/matching rules are being transferred. Do not silently identify perpendicular-space coordinates with extra physical space or holonomy-like near-return displacement with exact-loop residue.

Good next choices: (a) catalogue repeated local corner-response configurations with controls; (b) test sensitivity of short motif chains to alphabet/contact definitions and ordinary-growth controls; (c) design a small, explicitly new 3D model with a specified target behaviour. Larger seed coverage and local scheduling remain open. No background task, automation, or running simulation is left behind.

## Git handoff

After pulling the branch, `git status --short` should be empty before new work. Preserve the scoped checkpoint; do not reset it to upstream main. If desktop push authentication is unavailable, from repository root run:

```powershell
git push -u origin codex/expansion-front-checks
```

If Git for Windows reports the same Schannel credential error encountered during housekeeping, the certificate-verifying alternative is:

```powershell
git -c http.sslBackend=openssl push -u origin codex/expansion-front-checks
```

Never disable certificate verification or force-push to bypass a remote conflict. The chat's completion message records whether the push was actually verified and the final commit ID.
