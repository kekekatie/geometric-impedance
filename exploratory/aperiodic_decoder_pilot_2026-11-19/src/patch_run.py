"""Per-edge delayed-report run: metrics A (paired truth benefits + disagreement/posterior
vs thick) and B (record ambiguity + per-arm tie rate), over the frozen zero/one/two
ordinary-fault x8-variant ensemble. Reuses the audited engine via PatchDecoder.

Ensemble (frozen PROTOCOL.md): exhaustive k in {0,1}; k=2 either exhaustive or a seeded
uniform-without-replacement sample (seed 20261119, shared across all 18 sites,
Horvitz-Thompson inflation odds^2 * (C(310,2)/N)). Weights odds^k; W = exact ensemble
weight. Tie-aware truth credit (0.5 on a 1e-12 tie), hard credit alongside.
"""
import hashlib
import itertools
import json
import random
import time
from pathlib import Path

import patch_code as pc
import patch_decoder as pd
import nd_run

SEED = 20261119
P = 1e-3
ODDS = P / (1 - P)
ARMS = pd.ARMS
EPS = pd.EPS
VARIANTS = [(onset, vx, vz) for onset in (1, 2) for vx in (0, 1) for vz in (0, 1)]


def ordinary_pool(code):
    s = code
    pool = [('X', q, t) for q in s.DATA for t in range(5)] + \
           [('Z', q, t) for q in s.DATA for t in range(5)]
    pool += [('MZ', k, t) for k in s.ZSTABS for t in range(5)]
    pool += [('MX', k, t) for k in s.XSTABS for t in range(5)]
    return pool


def k2_sample(npool, N, seed=SEED):
    """Sorted index-pair list of all C(npool,2), uniformly sampled without replacement."""
    allpairs = list(itertools.combinations(range(npool), 2))
    total = len(allpairs)
    if N is None or N >= total:
        chosen = allpairs
        sampled = False
    else:
        idx = sorted(random.Random(seed).sample(range(total), N))
        chosen = [allpairs[i] for i in idx]
        sampled = True
    h = hashlib.sha256((';'.join(f'{a},{b}' for a, b in chosen)).encode()).hexdigest()
    return chosen, total, sampled, h


def config_stream(pool, k2pairs, k2_total):
    """Yield (k, extra_tuple, ht_factor). HT inflation applied to sampled k=2 configs."""
    yield 0, (), 1.0
    for i in range(len(pool)):
        yield 1, (pool[i],), 1.0
    ht = k2_total / len(k2pairs) if k2pairs else 1.0
    for (a, b) in k2pairs:
        yield 2, (pool[a], pool[b]), ht


def run_edge(code, site, k2pairs, k2_total, roundtrip_every=997):
    D = pd.PatchDecoder(code, site)
    s = code
    pool = ordinary_pool(s)
    W = 0.0
    cred = {a: {'tie': 0.0, 'hard': 0.0} for a in ARMS}
    disagree = {a: 0.0 for a in ARMS}          # weighted label-disagreement with thick
    postdiff = {a: 0.0 for a in ARMS}          # weighted fraction with |p0 - p0_thick| > EPS
    tierate = {a: 0.0 for a in ARMS}
    whole_ne = 0
    rt_checked = rt_mism = 0
    rec_groups = {}                            # full-record -> [w_truth0, w_truth1]
    archive_max = 0
    n = 0
    t0 = time.time()
    for k, extra, ht in config_stream(pool, k2pairs, k2_total):
        wbase = (ODDS ** k) * ht
        for (onset, vx, vz) in VARIANTS:
            loss = ([('X', site, onset)] if vx else []) + ([('Z', site, onset)] if vz else [])
            DZ, DX, truth, _ = s.simulate(*nd_run.compose(extra + tuple(loss)))
            dec = {a: D.direct(DZ, DX, a) for a in ARMS}
            n += 1
            W += wbase
            ref = dec['thick']
            # metric B: record grouping (by exact full detector record)
            key = (tuple(sorted(DZ.items())), tuple(sorted(DX.items())))
            g = rec_groups.get(key)
            if g is None:
                g = [0.0, 0.0]; rec_groups[key] = g
            g[truth] += wbase
            # metric A + tie rate
            for a in ARMS:
                d = dec[a]
                cred[a]['tie'] += wbase * (0.5 if d['tie'] else (1.0 if d['label'] == truth else 0.0))
                cred[a]['hard'] += wbase * (1.0 if d['label'] == truth else 0.0)
                disagree[a] += wbase * (d['label'] != ref['label'])
                postdiff[a] += wbase * (abs(d['p0'] - ref['p0']) > EPS)
                tierate[a] += wbase * (1.0 if d['tie'] else 0.0)
            if dec['whole']['label'] != ref['label'] or abs(dec['whole']['p0'] - ref['p0']) > EPS:
                whole_ne += 1
            # payload: stored-before-report archive size (diamond/whole share the sparse archive)
            stw = D.serialize(DZ, DX, 'whole')
            archive_max = max(archive_max, len(stw.get('archive', [])))
            if n % roundtrip_every == 0:
                rt_checked += 1
                for a in ARMS:
                    stt = D.serialize(DZ, DX, a)
                    if D.decode_state(json.loads(json.dumps(stt))) != dec[a]:
                        rt_mism += 1
        # keep memory bounded: thick/whole marginal evidence is ~unique per record
        if len(D._mcache) > 400000:
            D._mcache.clear()
    amb = sum(w0 + w1 for w0, w1 in rec_groups.values() if w0 > 0 and w1 > 0)
    res = dict(
        site=site, n=n, W=W,
        truth={a: {'tie': cred[a]['tie'] / W, 'hard': cred[a]['hard'] / W} for a in ARMS},
        paired_pp={
            'thick_minus_thin': 100 * (cred['thick']['tie'] - cred['thin']['tie']) / W,
            'diamond_minus_thin': 100 * (cred['diamond']['tie'] - cred['thin']['tie']) / W,
            'thick_minus_diamond': 100 * (cred['thick']['tie'] - cred['diamond']['tie']) / W,
            'thick_minus_thin_hard': 100 * (cred['thick']['hard'] - cred['thin']['hard']) / W,
            'diamond_minus_thin_hard': 100 * (cred['diamond']['hard'] - cred['thin']['hard']) / W,
        },
        disagree_with_thick={a: disagree[a] / W for a in ARMS},
        posterior_diff_from_thick={a: postdiff[a] / W for a in ARMS},
        tie_rate={a: tierate[a] / W for a in ARMS},
        record_ambiguity=amb / W,
        n_record_groups=len(rec_groups),
        whole_ne_thick=whole_ne,
        roundtrip_mismatches=rt_mism, roundtrip_checked=rt_checked,
        archive_max=archive_max, query_read=D.query,
        elapsed=round(time.time() - t0, 1),
    )
    return res
