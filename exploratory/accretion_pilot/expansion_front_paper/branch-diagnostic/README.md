# The paired branch diagnostic (consolidation)

*Astra's clean replacement for the broken rib-length (D′).*

From a **genuine free choice** — a two-way tie the bounded forced-only wave leaves open — grow three
forced-only arms from the same locally-saturated `before` state: **no commitment**, **commit option A**,
**commit option B** (radius 7·S, cap 50, on **fresh worlds 216–225**). Then compare the **final
decorated tile sets** of the A and B arms directly: tiles common to both (grey), A-only (blue), B-only
(orange). The two committed tiles are outlined; each arm's stopping reason is recorded. This avoids the
two faults the audit found in D/D′: there is no bookkeeping offset (end states compared directly) and no
counting-opportunity asymmetry (both arms run to the same saturation condition).

## What it found

24 genuine free choices diagnosed. **Every one** produced non-zero divergence — committing A versus B
always forces different local structure. Both arms **saturated cleanly** in all 24 (no caps, no
contradictions).

- Branch divergence `|A-only| + |B-only|`: **median 176 tiles**, p10 163, p90 272, max 278 (within
  radius 7·S).
- The largest-divergence examples (the figure) are **strikingly asymmetric**: one option forces a large
  cascade (≈ 260 tiles — a "rib option") while the *other option at the same tie* forces almost nothing
  (≈ 14 tiles — a "hinge option"), with only ~10 tiles common to both.

### Honest reading

A genuine free choice is **structurally consequential**: its two options lead to substantially
different forced completions of the local neighbourhood, and often one option is heavy and the other
light. This is a clean, measured observation (final tile sets, fresh worlds, saturated arms). It does
**not** reinstate the retracted claim that "genuine free choices are *the* load-bearing ribs" — it shows
that *within* a genuine choice, the two branches diverge greatly and asymmetrically. Whether this
asymmetry predicts persistence along the advancing skin is still the separate active-skin question.

Limits: radius 7·S bounds the divergence count; 24 cases from 10 fresh worlds; the figure shows the four
largest-divergence cases, while the median (176) is the honest central value; genuine-free selection is
by the bounded screen (radius 5·S, cap 12), so "genuine" means unresolved by that screen.

## Files

| file | what |
|---|---|
| `branch_diagnostic.py` | the diagnostic |
| `divergence.png` | four largest-divergence paired panels |
| `results/report.txt`, `results/measurements.json` | the numbers |

## Reproduce

```bash
cd exploratory/accretion_pilot/expansion_front_paper/branch-diagnostic
python3 branch_diagnostic.py --worlds 10 --nadd 700
```
