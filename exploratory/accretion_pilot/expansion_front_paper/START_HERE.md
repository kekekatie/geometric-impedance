# Expansion-front checks and figures

Work date: 16 October 2026. Manuscript title agreed in the supplied handoff:
**Decided before it is built: Local choices and their consequences in a growing Penrose tiling**.

Question: how much of an unbuilt future does a local choice already constrain?

Today's user request is to do the checks and figures first. Manuscript rewriting is deferred.
This is a new descriptive/exploratory pass, not a new preregistration or independent replication.
Source baseline and upstream head checked today: `d4e00c5d4396c38bd69b265907b5f3d6c5bc030a`.
Working branch: `codex/expansion-front-checks`, in a separate clone.

## Current progress

- Saved-data recomputation completed: all quantities in the handoff agree.
- Registered scorecards and corrected bins recomputed separately in `CHECKS.md` and `results/audit.json`.
- Representative selection recorded before reconstruction in `results/selection.json`.
- Both targeted reconstructions completed and agree with deposited results. Details in `results/reconstruction.json`.
- Three figures exported as SVG and 300 dpi PNG, visually inspected; captions in `CAPTIONS.md`.
- Numerical geometry checks agree to floating-point precision; chronology in `results/geometry_checks.json`.
- Source and interpretation review in `SCIENTIFIC_REVIEW.md`. No numerical discrepancy found in the checked claims.

## Reproduce

From this folder, with Python, NumPy, SciPy and Matplotlib installed:

```sh
python checks.py
python geometry_checks.py
python figures.py
```

The second command reconstructs just two selected world prefixes and their relevant branches.
It checks geometry against deposited results before plotting. Any mismatch raises an error.
`python figures.py --plot-only` redraws from its own local `results/geometry.pkl` cache.
The cache is excluded from Git; use the reconstruction command to regenerate it.
Original studies and deposited results are left intact.
The tested environment was Python 3.12.14; dependencies are pinned in `requirements.txt`.

## Reconstructed examples

- Overview: first-study world 19, slice 31, key `2a3cfb2c41f77386`, 84 changed half-tiles.
  Selection: median changed-region size among 41 elongated first-occurrence records; lexicographic key tie-break.
  Configuration key, cut angle, changed count, family shares, axis, ratio and all placement pairs match saved data.
  New illustrative burst diagnostic: core covers 27/42 and 29/42 changed half-tiles and all 27/27 and 29/29
  predicted-family changed tiles on A and B respectively. This is one selected case, not an all-sample result.
- Exception: follow-up world 21, slice 8, key `180fb0b920bb845b`.
  The full reconstructed situation dictionary matches the saved result exactly.
  Figure compares B continuations 1 and 3 (zero-based streams 0 and 2), the first pair with distinct geometry
  and distinct paired A/B dominant families. Both make their later choice at continuation slice 12.
  All five paired families reproduce `[2, 2, 3, 3, 3]`.

No full historical study was rerun. These checks use the original growth implementation and are not an independent implementation replication.

## Scientific status to carry into the paper

| Claim | Source | Denominator | Status |
|---|---|---|---|
| C1 dominance, C2 held-out prediction, C3 registered table, C4 elongated orientation | `../cut_direction/results/worlds.json`; original registration | 45, 17, 4 bins, 41 respectively | Registered; original binning retained |
| Five directions identify five dominant families | Same file, corrected cut-line bins | 45 configurations, including training | Corrected exploratory |
| Forced response predicts family; connected chain; continuation stability; P4 | `../settled_test/results/results.json` | 45 configurations; 90 sides; 45 configurations; 2 eligible configurations | Registered |
| 13 overlapping keys, P1 in 32 new configurations, 13/14 later-guess stability | Both saved datasets | Rounded configuration keys; 32 and 14 configurations | New descriptive |
| Orientation error <= 2.5935167334 degrees; pooled placement fit | First study saved data | 41 elongated regions; 4,331 placement instances | Descriptive verification |
| Forced sequence belongs to every completion | Completeness and valid-extension assumptions | Logical argument, not a sampling result | Conditional argument |
| Reach of the present, memory and consequence | Motivating discussion | No physical-clock measurement | Interpretation |

The forced burst is a certified subset under assumptions, not the full extent of a choice's consequences.
P4's failure does not establish that nothing beyond another choice can be settled.
66/90 bursts are censored at 40 slices; duration is not spatial width.
The follow-up has no family-1 examples. Five continuation streams do not guarantee five distinct geometries.
P4's 44/92 counts covered tile-comparison instances across ordered pairs.

## Review still needed

Review the figures and captions with Katie before incorporating them into the revised manuscript.
AI model designations and final authorship wording remain for Katie to confirm during the manuscript pass.
No universal ribbon theorem, scheduler comparison, rare-family campaign or 3D implementation is part of this pass.

Single next action after this pass: review the figure package, then revise the paper around those pictures and verified claims.
