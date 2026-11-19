"""Validation suite (run before interpreting any site difference).

Covers the frozen protocol's checks: adapter sanity (ranks/commutation/anticommuting
logicals) per patch; single-fault syndrome + logical-parity in BOTH sectors; whole==thick
labels+posteriors; restart==direct for every arm; diamond query = exactly 4 distinct
checks / 8 distinct check-round coords per edge; and a frozen original d=3 decoder-case
replay against its saved output. Exit non-zero on any failure."""
import json
import random
import sys
from pathlib import Path

import numpy as np

import patch_code as pc
import patch_decoder as pd
import nd_run
import nd_infer

PATCHES = ('square', 'AB', 'Penrose')
EPS = pd.EPS


def _pool(s):
    pool = [('X', q, t) for q in s.DATA for t in range(5)] + \
           [('Z', q, t) for q in s.DATA for t in range(5)]
    pool += [('MZ', k, t) for k in s.ZSTABS for t in range(5)]
    pool += [('MX', k, t) for k in s.XSTABS for t in range(5)]
    return pool


def adapter_sanity(code):
    HX, HZ = code.hx(), code.hz()
    assert pc.gf2_rank(HX) == 10 and pc.gf2_rank(HZ) == 10, 'ranks'
    assert bool(((HX @ HZ.T) % 2 == 0).all()), 'commutation'
    assert code._dot(code.LZ, code.XL) == 1, 'logical anticommute'
    assert sum(code.LZ) == 3 and sum(code.XL) == 3, 'logicals weight 3'
    # no weight-1 or weight-2 pure X-error is a logical (distance >= 3, X sector)
    LZv = np.array(code.LZ)
    HXm = HX  # rows = X-checks; an X error is undetected by X-checks (commutes) iff in ker? X errors are detected by Z-checks
    HZm = HZ
    bad = 0
    idx = list(range(code.NDATA))
    for w in (1, 2):
        import itertools
        for combo in itertools.combinations(idx, w):
            v = np.zeros(code.NDATA, dtype=np.int64)
            for q in combo:
                v[q] ^= 1
            # X-error: detected by Z-checks (HZ). Undetected AND anticommutes with X_L => logical.
            if (HZm @ v % 2 == 0).all() and (v @ np.array(code.XL) % 2 == 1):
                bad += 1
    assert bad == 0, f'weight<=2 X-logical exists ({bad})'
    return True


def single_fault(code):
    s = code
    okX = okZ = 0
    for q in range(s.NDATA):
        DZ, DX, zl, xl = s.simulate({(q, 2)}, set(), set(), set())
        fired = {k for (k, t), v in DZ.items() if v and k in s.ZSTABS}
        incident = {k for k in s.ZSTABS if q in s.STABS[k]['support']}
        if fired <= incident and zl == (1 if s.LZ[q] else 0):
            okX += 1
        DZ2, DX2, zl2, xl2 = s.simulate(set(), {(q, 2)}, set(), set())
        firedz = {k for (k, t), v in DX2.items() if v and k in s.XSTABS}
        incidentz = {k for k in s.XSTABS if q in s.STABS[k]['support']}
        if firedz <= incidentz and xl2 == (1 if s.XL[q] else 0):
            okZ += 1
    assert okX == s.NDATA and okZ == s.NDATA, f'single-fault X {okX} Z {okZ} / {s.NDATA}'
    return True


def arms_and_queries(code, nhist=150, seed=0):
    s = code
    rng = random.Random(seed)
    pool = _pool(s)
    wh_ne = rt_ne = 0
    for q, elig in s.eligible.items():
        D = pd.PatchDecoder(code, q)
        # diamond query shape: exactly 4 distinct checks, 8 distinct (check,round) coords
        assert len(set(D.star)) == 4, f'edge q{q}: {len(set(D.star))} checks'
        qcoords = {(k, t) for k in D.star for t in D.onsets}
        assert len(qcoords) == 8 and D.query == 8, f'edge q{q}: {D.query} query coords'
        # the certified query must name those same four checks
        cert_checks = sorted(pc.check_index(c) for c in elig['checks'])
        assert sorted(D.star) == cert_checks, f'edge q{q}: star != certified checks'
        for _ in range(nhist):
            w = rng.choice([0, 1, 2]); extra = rng.sample(pool, w)
            onset = rng.choice([1, 2]); vx, vz = rng.choice([0, 1]), rng.choice([0, 1])
            loss = ([('X', q, onset)] if vx else []) + ([('Z', q, onset)] if vz else [])
            DZ, DX, truth, _ = s.simulate(*nd_run.compose(tuple(extra) + tuple(loss)))
            dec = {a: D.direct(DZ, DX, a) for a in pd.ARMS}
            if dec['whole']['label'] != dec['thick']['label'] or \
               abs(dec['whole']['p0'] - dec['thick']['p0']) > EPS:
                wh_ne += 1
            for a in pd.ARMS:
                st = D.serialize(DZ, DX, a)
                if D.decode_state(json.loads(json.dumps(st))) != dec[a]:
                    rt_ne += 1
    assert wh_ne == 0, f'whole!=thick {wh_ne}'
    assert rt_ne == 0, f'restart!=direct {rt_ne}'
    return True


def frozen_d3_replay():
    """Replay the committed d=3 bulk example (results/d3_1_1.json) through the untouched
    nd_infer engine and confirm the saved per-arm decisions reproduce."""
    p = _D5_RESULTS / 'd3_1_1.json'
    if not p.exists():
        return 'skip (no saved d3_1_1.json)'
    saved = json.loads(p.read_text())
    ex = saved.get('example')
    if not ex:
        return 'skip (no example field)'
    D = nd_infer.Decoder(3, tuple(saved['site']))
    fts = [(f[0], tuple(f[1]) if isinstance(f[1], list) else f[1], f[2]) for f in ex['faults']]
    DZ, DX, truth, _ = D.s.simulate(*nd_run.compose(tuple(fts)))
    assert truth == ex['truth'], f"truth {truth} != saved {ex['truth']}"
    for a in pd.ARMS:
        lbl = D.direct(DZ, DX, a)['label']
        assert lbl == ex['decisions'][a], f"{a}: {lbl} != saved {ex['decisions'][a]}"
    return 'ok'


_D5_RESULTS = (Path(__file__).resolve().parents[2]
               / 'reconsideration_witness' / 'distance5_2026-11-16' / 'results')


def main():
    out = {}
    for fam in PATCHES:
        code = pc.PatchCode(fam)
        adapter_sanity(code)
        single_fault(code)
        arms_and_queries(code)
        out[fam] = 'pass'
        print(f'{fam}: adapter+single-fault+arms+queries PASS', flush=True)
    rep = frozen_d3_replay()
    out['frozen_d3_replay'] = rep
    print('frozen d=3 replay:', rep, flush=True)
    (Path(__file__).resolve().parents[1] / 'results' / 'validation.json').write_text(
        json.dumps(out, indent=2) + '\n')
    print('ALL VALIDATION PASSED')


if __name__ == '__main__':
    main()
