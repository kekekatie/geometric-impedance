"""Independently aggregate the per-configuration half credits using Decimal."""
import csv
import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 40
root = Path(__file__).resolve().parent / 'results'
report = json.loads((root / 'scores.json').read_text())
arms = list(report['scores'])
totals = {a: Decimal(0) for a in arms}
mass = Decimal(0)
counts = [0, 0, 0]
credits = {a: [Decimal(0)] * 3 for a in arms}
odds = Decimal(1) / Decimal(999)
with (root / 'config_scores.csv').open(newline='') as handle:
    for i, row in enumerate(csv.DictReader(handle)):
        assert int(row['config_id']) == i
        k = int(row['ordinary_weight'])
        counts[k] += 8
        w = odds ** k
        mass += 8 * w
        for a in arms:
            c = Decimal(row[a])
            assert 0 <= c <= 8 and c * 2 == int(c * 2)
            totals[a] += c * w
            credits[a][k] += c
assert i + 1 == report['configurations']
assert counts == report['histories_by_fault_weight']
for a in arms:
    assert list(map(float, credits[a])) == report['scores'][a]['credit_by_fault_weight']
    assert abs(float(totals[a] / mass) - report['scores'][a]['tie_aware_truth']) < 1e-14
print('Verified all nine arm scores from 48,206 CSV rows with Decimal arithmetic.')
