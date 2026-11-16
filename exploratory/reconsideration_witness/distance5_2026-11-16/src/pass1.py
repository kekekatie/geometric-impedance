"""Pass 1: stratified (k=0,1,2) + tie-aware rescore of an existing ensemble.

Sol's audit of the d=5 126x truth-margin drop asked us to separate three things
before touching k=3 sampling:
  - within-stratum behavior vs the k=0,1,2 MIX shift (single-fault weight 11.4%
    at d=3 vs 25.7% at d=5),
  - hard-label scoring vs Astra's TIE-AWARE scoring (0.5 credit when the soft
    decision is an exact 1e-12 tie -- the highlighted d=5 example is such a tie),
  - whether the tiny net thick-thin gap is arms agreeing everywhere, opposite
    wins cancelling, or knife-edge 50/50 ties.

This re-runs the SAME decoder over the SAME ensemble (nothing re-derived), and for
every history records, per arm, the soft decision from decide() -> {label,p0,p1,
tie}. Two credits vs the simulated truth:
  hard credit = 1 if label==truth else 0      (label is zero-favouring on ties)
  tie credit  = 0.5 if tie else (1 if label==truth else 0)
Accumulated weighted, stratified by k = number of ordinary faults, with a full
3x3 (credit_A x credit_B) grid for the thick-vs-thin and thick-vs-diamond pairs.
compare1.py does the cross-distance standardization.
"""
import json, sys, time
from pathlib import Path
import nd_infer, nd_run

CRED = {0.0: 0, 0.5: 1, 1.0: 2}          # credit -> grid index
PAIRS = (('thick', 'thin'), ('thick', 'diamond'))


def blank_stratum():
    return dict(
        hist=0, weight=0.0,
        arms={a: dict(hard=0.0, tie=0.0, tie_count=0, tie_wmass=0.0) for a in nd_infer.ARMS},
        pairs={f'{a}_vs_{b}': [[0.0] * 3 for _ in range(3)] for a, b in PAIRS},
    )


def run(d, site, p=1e-3):
    D = nd_infer.Decoder(d, site, p=p)
    s = D.s
    odds = p / (1 - p)
    strata = {0: blank_stratum(), 1: blank_stratum(), 2: blank_stratum()}
    start = time.time(); n = 0
    for k, fts, onset in nd_run.histories(s, site):
        n += 1
        weight = odds ** k
        DZ, DX, truth, _ = s.simulate(*nd_run.compose(fts))
        st = strata[k]
        st['hist'] += 1; st['weight'] += weight
        dec = {}
        for arm in nd_infer.ARMS:
            r = D.direct(DZ, DX, arm)
            tie = r['tie']
            hard = 1.0 if (r['label'] == truth) else 0.0
            cred = 0.5 if tie else hard
            dec[arm] = cred
            aa = st['arms'][arm]
            aa['hard'] += weight * hard
            aa['tie'] += weight * cred
            if tie:
                aa['tie_count'] += 1; aa['tie_wmass'] += weight
        for a, b in PAIRS:
            st['pairs'][f'{a}_vs_{b}'][CRED[dec[a]]][CRED[dec[b]]] += weight
        if n % 50000 == 0:
            print(d, site, n, round(time.time() - start, 1), 's', flush=True)
    W = sum(st['weight'] for st in strata.values())
    out = dict(d=d, site=list(site), query=D.query, n=n, weight=W,
               strata={str(k): strata[k] for k in (0, 1, 2)},
               elapsed=round(time.time() - start, 1))
    # cross-check: overall hard truth per arm should match the headline run
    tot = {a: sum(strata[k]['arms'][a]['hard'] for k in (0, 1, 2)) / W for a in nd_infer.ARMS}
    out['overall_hard_truth'] = {a: round(tot[a], 6) for a in nd_infer.ARMS}
    return out


if __name__ == '__main__':
    d = int(sys.argv[1]); site = tuple(map(int, sys.argv[2].split(',')))
    out = run(d, site)
    tag = f'pass1_d{d}_{site[0]}_{site[1]}'
    Path('../results').mkdir(exist_ok=True)
    Path(f'../results/{tag}.json').write_text(json.dumps(out, indent=2) + '\n')
    print('overall hard truth', out['overall_hard_truth'], 'elapsed', out['elapsed'])
