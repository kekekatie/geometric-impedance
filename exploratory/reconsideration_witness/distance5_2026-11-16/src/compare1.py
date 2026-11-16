"""Pass 1 cross-distance report: stratified + tie-aware, with mix standardization.

Reads results/pass1_d3_1_1.json and results/pass1_d5_2_2.json and answers Sol's
four asks:
  (1) stratify by k in {0,1,2};
  (2) hard-label AND tie-aware truth for every arm;
  (3) pairwise (thick vs thin, thick vs diamond) decomposition -- tie mass, where
      only-thick / only-thin is right, and the net, so we see whether the tiny net
      gap is agreement, cancelling opposite wins, or 50/50 ties;
  (4) recombine the strata under a COMMON (matched) mix so within-stratum behavior
      is separated from the k-mix shift (single-fault weight 11.4% -> 25.7%).

Writes results/pass1_report.json and prints the tables.
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / 'results'
G = {3: json.load(open(R / 'pass1_d3_1_1.json')), 5: json.load(open(R / 'pass1_d5_2_2.json'))}
ARMS = ('thick', 'thin', 'diamond', 'whole')
KS = ('0', '1', '2')
IDX = {0: 0.0, 1: 0.5, 2: 1.0}          # grid index -> credit


def strat(gd, k):
    return gd['strata'][k]


def pi(gd):
    W = gd['weight']
    return {k: strat(gd, k)['weight'] / W for k in KS}


def rate(gd, k, arm, scoring):
    st = strat(gd, k); S = st['weight']
    return (st['arms'][arm][scoring] / S) if S else 0.0


def overall_rate(gd, arm, scoring, mix):
    return sum(mix[k] * rate(gd, k, arm, scoring) for k in KS)


def grid_decomp(st, pair):
    g = st['pairs'][pair]; S = st['weight'] or 1.0
    cells = {(i, j): g[i][j] for i in range(3) for j in range(3)}
    both_right = cells[(2, 2)]
    both_wrong = cells[(0, 0)]
    A_only = cells[(2, 0)]                     # thick strictly right, B strictly wrong
    B_only = cells[(0, 2)]                     # B strictly right, thick strictly wrong
    tie_mass = sum(w for (i, j), w in cells.items() if i == 1 or j == 1)
    A_ahead = sum(w for (i, j), w in cells.items() if i > j)   # tie-aware: thick more correct
    B_ahead = sum(w for (i, j), w in cells.items() if j > i)
    net = A_ahead - B_ahead
    return dict(both_right=both_right, both_wrong=both_wrong, A_only=A_only, B_only=B_only,
                tie_involved_mass=tie_mass, A_ahead=A_ahead, B_ahead=B_ahead, net=net,
                A_ahead_frac=A_ahead / S, B_ahead_frac=B_ahead / S, net_frac=net / S)


def fmt(x, n=6):
    return f'{x:.{n}f}'


report = {}
for d in (3, 5):
    gd = G[d]; p = pi(gd)
    report[f'd{d}'] = dict(
        n=gd['n'], weight=gd['weight'], pi={k: round(p[k], 5) for k in KS},
        per_stratum={}, overall={})
    for k in KS:
        st = strat(gd, k)
        blk = dict(hist=st['hist'], weight=st['weight'], pi=round(p[k], 5),
                   arms={a: dict(hard=round(rate(gd, k, a, 'hard'), 6),
                                 tie=round(rate(gd, k, a, 'tie'), 6),
                                 tie_count=st['arms'][a]['tie_count'],
                                 tie_wfrac=round((st['arms'][a]['tie_wmass'] / st['weight']) if st['weight'] else 0, 6))
                         for a in ARMS},
                   pairs={pr: {kk: round(vv, 8) for kk, vv in grid_decomp(st, pr).items()}
                          for pr in ('thick_vs_thin', 'thick_vs_diamond')})
        report[f'd{d}']['per_stratum'][k] = blk
    # own-mix overall
    ov = dict(arms={a: dict(hard=round(overall_rate(gd, a, 'hard', p), 6),
                            tie=round(overall_rate(gd, a, 'tie', p), 6)) for a in ARMS})
    ov['margin_thick_minus_thin'] = dict(
        hard=round(overall_rate(gd, 'thick', 'hard', p) - overall_rate(gd, 'thin', 'hard', p), 6),
        tie=round(overall_rate(gd, 'thick', 'tie', p) - overall_rate(gd, 'thin', 'tie', p), 6))
    ov['margin_thick_minus_diamond'] = dict(
        hard=round(overall_rate(gd, 'thick', 'hard', p) - overall_rate(gd, 'diamond', 'hard', p), 6),
        tie=round(overall_rate(gd, 'thick', 'tie', p) - overall_rate(gd, 'diamond', 'tie', p), 6))
    report[f'd{d}']['overall'] = ov

# ---- standardization: both distances under a COMMON mix ----
mixes = {'d3_mix': pi(G[3]), 'd5_mix': pi(G[5]),
         'flat_k12': {'0': 0.0, '1': 0.5, '2': 0.5}}   # ignore k=0 (no fault, no signal)
std = {}
for mixname, mix in mixes.items():
    std[mixname] = {}
    for d in (3, 5):
        gd = G[d]
        row = {}
        for a in ('thick', 'thin', 'diamond'):
            row[a] = dict(hard=round(overall_rate(gd, a, 'hard', mix), 6),
                          tie=round(overall_rate(gd, a, 'tie', mix), 6))
        row['margin_thick_thin'] = dict(
            hard=round(overall_rate(gd, 'thick', 'hard', mix) - overall_rate(gd, 'thin', 'hard', mix), 6),
            tie=round(overall_rate(gd, 'thick', 'tie', mix) - overall_rate(gd, 'thin', 'tie', mix), 6))
        std[mixname][f'd{d}'] = row
report['standardization'] = std

# ---- within-stratum margins (the cleanest view) ----
report['within_stratum_margin_thick_thin'] = {
    f'd{d}': {k: dict(
        hard=round(rate(G[d], k, 'thick', 'hard') - rate(G[d], k, 'thin', 'hard'), 6),
        tie=round(rate(G[d], k, 'thick', 'tie') - rate(G[d], k, 'thin', 'tie'), 6))
        for k in KS} for d in (3, 5)}

(R / 'pass1_report.json').write_text(json.dumps(report, indent=2) + '\n')

# ---------- printout ----------
print('=== per-arm truth: hard | tie-aware  (own mix overall) ===')
print(f"{'arm':9}{'d3 hard':>11}{'d3 tie':>11}{'d5 hard':>11}{'d5 tie':>11}")
for a in ARMS:
    print(f'{a:9}{fmt(report["d3"]["overall"]["arms"][a]["hard"]):>11}'
          f'{fmt(report["d3"]["overall"]["arms"][a]["tie"]):>11}'
          f'{fmt(report["d5"]["overall"]["arms"][a]["hard"]):>11}'
          f'{fmt(report["d5"]["overall"]["arms"][a]["tie"]):>11}')

print('\n=== thick-minus-thin margin (own mix) ===')
for d in (3, 5):
    m = report[f'd{d}']['overall']['margin_thick_minus_thin']
    print(f'  d={d}: hard {fmt(m["hard"])}   tie-aware {fmt(m["tie"])}')

print('\n=== within-stratum thick-thin margin (tie-aware) ===')
w = report['within_stratum_margin_thick_thin']
print(f"{'k':4}{'d3 tie':>12}{'d5 tie':>12}{'d3 hard':>12}{'d5 hard':>12}")
for k in KS:
    print(f'{k:4}{fmt(w["d3"][k]["tie"]):>12}{fmt(w["d5"][k]["tie"]):>12}'
          f'{fmt(w["d3"][k]["hard"]):>12}{fmt(w["d5"][k]["hard"]):>12}')

print('\n=== standardization: thick-thin margin under matched mixes ===')
for mixname in mixes:
    r3 = std[mixname]['d3']['margin_thick_thin']; r5 = std[mixname]['d5']['margin_thick_thin']
    print(f'  {mixname:9}: d3 hard {fmt(r3["hard"])} tie {fmt(r3["tie"])} | '
          f'd5 hard {fmt(r5["hard"])} tie {fmt(r5["tie"])}')

print('\n=== tie weight fraction per arm (overall, own mix) ===')
for d in (3, 5):
    p = pi(G[d])
    tf = {a: sum(p[k] * (strat(G[d], k)['arms'][a]['tie_wmass'] / (strat(G[d], k)['weight'] or 1)) for k in KS) for a in ARMS}
    print(f'  d={d}: ' + '  '.join(f'{a} {fmt(tf[a])}' for a in ARMS))

print('\n=== pairwise thick_vs_thin (overall, as fraction of total weight) ===')
pair_report = {}
for d in (3, 5):
    W = G[d]['weight']; agg = {}
    for k in KS:
        dec = grid_decomp(strat(G[d], k), 'thick_vs_thin')
        for kk, vv in dec.items():
            if kk in ('both_right', 'both_wrong', 'A_only', 'B_only', 'tie_involved_mass', 'A_ahead', 'B_ahead', 'net'):
                agg[kk] = agg.get(kk, 0.0) + vv
    agg = {kk: vv / W for kk, vv in agg.items()}
    pair_report[f'd{d}'] = {kk: round(vv, 8) for kk, vv in agg.items()}
    print(f'  d={d}: thick_only_right={fmt(agg["A_only"],8)} thin_only_right={fmt(agg["B_only"],8)} '
          f'tie_involved={fmt(agg["tie_involved_mass"],8)} net(thick-thin)={fmt(agg["net"],8)}')
report['pairwise_thick_vs_thin_overall_frac'] = pair_report
(R / 'pass1_report.json').write_text(json.dumps(report, indent=2) + '\n')
