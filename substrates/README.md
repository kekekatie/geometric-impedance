# Substrates and null controls

Self-contained substrate generation and null-control auditing, so the
Silent Corruption analysis can be reproduced without external input files.

| File | Purpose |
|---|---|
| `generate_ab.py` | Ammann-Beenker generator (Z^4 cut-and-project), emits lift + edge CSVs with full perpendicular-space coordinates |
| `audit_with_nulls.py` | Reproduces the v3 identity and fresh-reconstruction audits, adds the null controls v3 omits |
| `NULL_AUDIT_FINDINGS.md` | Results and what they mean for the v3 paper |
| `null_audit_results.csv` | Per-replicate output |

```
python3 generate_ab.py --extent 37 --prefix ab
python3 audit_with_nulls.py --reps 3
```

Requires numpy and scikit-learn.
