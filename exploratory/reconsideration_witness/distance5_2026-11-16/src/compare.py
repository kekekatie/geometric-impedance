"""Build the d=3-vs-d=5 bulk comparison table + derived quantities.

Reads results/d3_1_1.json (this method at d=3 bulk) and results/d5_2_2.json
(d=5 bulk), both scored with the SAME tractable bounded-frame decoder, and emits
results/d3_vs_d5.json. Derived metrics:
  - archive marginal value = thick_truth - thin_truth (how much the full record
    out-predicts the thin record, in weighted correctness)
  - diamond marginal value = diamond_truth - thin_truth (how much the local
    witness bracket adds on top of the thin record)
  - diamond-right fraction = of the histories where the bracket disagrees with
    the full record, how often the bracket is the one that matches the truth
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / 'results'
d3 = json.load(open(R / 'd3_1_1.json'))
d5 = json.load(open(R / 'd5_2_2.json'))


def derive(x):
    a = x['arms']
    s = x['diamond_split']
    dr, rr = s.get('diamond_right', 0), s.get('reference_right', 0)
    return dict(
        query=x['query'], histories=x['n'], weight=round(x['weight'], 4),
        raw_diamond_disagree=a['diamond']['raw_disagree'],
        wt_disagree_thin_pct=a['thin']['weighted_disagreement_pct'],
        wt_disagree_diamond_pct=a['diamond']['weighted_disagreement_pct'],
        truth_thick=a['thick']['weighted_truth'],
        truth_thin=a['thin']['weighted_truth'],
        truth_diamond=a['diamond']['weighted_truth'],
        archive_marginal=round(a['thick']['weighted_truth'] - a['thin']['weighted_truth'], 6),
        diamond_marginal=round(a['diamond']['weighted_truth'] - a['thin']['weighted_truth'], 6),
        diamond_right=dr, reference_right=rr,
        diamond_right_frac=round(dr / (dr + rr), 4) if (dr + rr) else None,
        pay_thick=a['thick']['payload_max'],
        pay_thin=a['thin']['payload_max'],
        pay_diamond_mean=a['diamond']['payload_mean'],
        pay_diamond_max=a['diamond']['payload_max'],
        pay_diamond_mean_saving_pct=round(100 * (1 - a['diamond']['payload_mean'] / a['thick']['payload_max']), 1),
        whole_ne_thick=x['whole_ne_thick'],
        roundtrip_mismatches=x['roundtrip_mismatches'],
    )


g3, g5 = derive(d3), derive(d5)
out = dict(
    d3_bulk_1_1=g3, d5_bulk_2_2=g5,
    archive_marginal_shrink=round(g3['archive_marginal'] / g5['archive_marginal'], 1),
    note=('Same tractable bounded-frame decoder at both distances. Raw counts '
          'are not comparable (8x more histories at d=5); weighted metrics are. '
          'The d=5 ensemble places more RELATIVE weight on single-fault histories '
          '(25.7% vs 11.4%), so part of the higher weighted disagreement reflects '
          'that weight-shift; the truth-based archive-marginal statement is the '
          'ensemble-robust one.'),
)
(R / 'd3_vs_d5.json').write_text(json.dumps(out, indent=2) + '\n')

print(f"{'metric':34s}{'d3 bulk (1,1)':>16}{'d5 bulk (2,2)':>16}")
print('-' * 66)
for k in ('query', 'histories', 'raw_diamond_disagree',
          'wt_disagree_thin_pct', 'wt_disagree_diamond_pct',
          'truth_thin', 'truth_diamond', 'truth_thick',
          'archive_marginal', 'diamond_marginal',
          'diamond_right', 'reference_right', 'diamond_right_frac',
          'pay_thin', 'pay_diamond_mean', 'pay_diamond_max', 'pay_thick',
          'whole_ne_thick', 'roundtrip_mismatches'):
    print(f'{k:34s}{str(g3[k]):>16}{str(g5[k]):>16}')
print(f"\narchive marginal value shrink d3->d5: {out['archive_marginal_shrink']}x")
