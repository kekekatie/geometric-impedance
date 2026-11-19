"""Turn results/edges_raw.json into the 18-row machine-readable table (edges.json +
edges.csv) and a short console summary. Pure post-processing; no decoding."""
import csv
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / 'results'

COLS = [
    'family', 'edge_id', 'lost_qubit', 'incident_checks', 'endpoint_degrees',
    'd_rough', 'd_smooth',
    'thick_minus_thin_pp', 'diamond_minus_thin_pp', 'thick_minus_diamond_pp',
    'thick_minus_thin_hard_pp', 'diamond_minus_thin_hard_pp',
    'truth_thick', 'truth_thin', 'truth_diamond', 'truth_whole',
    'disagree_thin', 'disagree_diamond',
    'postdiff_thin', 'postdiff_diamond',
    'tie_thick', 'tie_thin', 'tie_diamond',
    'record_ambiguity', 'n_record_groups',
    'archive_max', 'query_read', 'whole_ne_thick', 'n', 'W',
]


def flatten(row):
    p = row['paired_pp']
    return dict(
        family=row['family'], edge_id=row['edge_id'], lost_qubit=row['lost_qubit'],
        incident_checks='|'.join(row['incident_checks']),
        endpoint_degrees='-'.join(map(str, row['endpoint_degrees'])),
        d_rough=row['d_rough'], d_smooth=row['d_smooth'],
        thick_minus_thin_pp=round(p['thick_minus_thin'], 5),
        diamond_minus_thin_pp=round(p['diamond_minus_thin'], 5),
        thick_minus_diamond_pp=round(p['thick_minus_diamond'], 5),
        thick_minus_thin_hard_pp=round(p['thick_minus_thin_hard'], 5),
        diamond_minus_thin_hard_pp=round(p['diamond_minus_thin_hard'], 5),
        truth_thick=round(row['truth']['thick']['tie'], 6),
        truth_thin=round(row['truth']['thin']['tie'], 6),
        truth_diamond=round(row['truth']['diamond']['tie'], 6),
        truth_whole=round(row['truth']['whole']['tie'], 6),
        disagree_thin=round(row['disagree_with_thick']['thin'], 6),
        disagree_diamond=round(row['disagree_with_thick']['diamond'], 6),
        postdiff_thin=round(row['posterior_diff_from_thick']['thin'], 6),
        postdiff_diamond=round(row['posterior_diff_from_thick']['diamond'], 6),
        tie_thick=round(row['tie_rate']['thick'], 6),
        tie_thin=round(row['tie_rate']['thin'], 6),
        tie_diamond=round(row['tie_rate']['diamond'], 6),
        record_ambiguity=round(row['record_ambiguity'], 6),
        n_record_groups=row['n_record_groups'],
        archive_max=row['archive_max'], query_read=row['query_read'],
        whole_ne_thick=row['whole_ne_thick'], n=row['n'], W=round(row['W'], 6),
    )


def main():
    raw = json.loads((RESULTS / 'edges_raw.json').read_text())
    flat = [flatten(r) for r in raw['rows']]
    # short edge id for the figure/table: family initial + running index per patch
    tags = {}
    for r in flat:
        fam = r['family']
        tags.setdefault(fam, [])
        r['short_id'] = {'square': 'S', 'AB': 'A', 'Penrose': 'P'}[fam] + str(len(tags[fam]) + 1)
        tags[fam].append(r['short_id'])
    out = dict(mode=raw['mode'], n_k2=raw['n_k2'], k2_sha256=raw['k2_sha256'],
               caps=raw['caps'], rows=flat)
    (RESULTS / 'edges.json').write_text(json.dumps(out, indent=2) + '\n')
    with (RESULTS / 'edges.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['short_id'] + COLS)
        w.writeheader()
        for r in flat:
            w.writerow({k: r.get(k) for k in ['short_id'] + COLS})
    # summary
    print(f"{'edge':<10}{'deg':>6}{'thick-thin':>12}{'diam-thin':>11}{'tk-diam':>10}"
          f"{'rec_amb':>10}{'tie_tk':>9}")
    for r in flat:
        print(f"{r['family'][:3]}{r['short_id']:<7}{r['endpoint_degrees']:>6}"
              f"{r['thick_minus_thin_pp']:>12}{r['diamond_minus_thin_pp']:>11}"
              f"{r['thick_minus_diamond_pp']:>10}{r['record_ambiguity']:>10}{r['tie_thick']:>9}")
    inv = [(r['family'], r['edge_id'], r['whole_ne_thick']) for r in flat if r['whole_ne_thick']]
    print('whole!=thick anomalies:', inv or 'none')
    print('WROTE results/edges.json, results/edges.csv')


if __name__ == '__main__':
    main()
