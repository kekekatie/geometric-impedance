"""Run the tractable general-d decoder over the bounded ensemble; score vs thick.

Used both to VALIDATE at d=3 (compare to Astra's exact E_frame) and to MEASURE d=5.
Keeps the same ensemble shape, compose(XOR), onsets, deadline and four arms.
"""
import itertools, json, time, collections, sys
from pathlib import Path
import nd_infer


def compose(contribs, parity=True):
    sets = {k: set() for k in ('X', 'Z', 'MZ', 'MX')}
    for tag, pos, t in contribs:
        key = (pos, t)
        if parity and key in sets[tag]:
            sets[tag].remove(key)
        else:
            sets[tag].add(key)
    return tuple(sets[k] for k in ('X', 'Z', 'MZ', 'MX'))


def histories(s, site):
    pool = [(tag, q, t) for q in s.DATA for t in range(5) for tag in ('X', 'Z')]
    pool += [('MZ', k, t) for k in s.ZSTABS for t in range(5)]
    pool += [('MX', k, t) for k in s.XSTABS for t in range(5)]
    for w in range(3):
        for extra in itertools.combinations(pool, w):
            for onset in (1, 2):
                for vx in (0, 1):
                    for vz in (0, 1):
                        loss = ([('X', site, onset)] if vx else []) + \
                               ([('Z', site, onset)] if vz else [])
                        yield w, tuple(extra) + tuple(loss), onset


def run(d, site, roundtrip=True, limit=None, p=1e-3):
    D = nd_infer.Decoder(d, site, p=p)
    s = D.s
    odds = p / (1 - p)
    start = time.time()
    W = 0.0; n = 0; rt_mism = 0; whole_ne = 0
    tot = {a: dict(raw=0, hard_agree=0.0, hard_correct=0.0, pay_max=0, pay_weighted=0.0)
           for a in nd_infer.ARMS}
    share = collections.Counter()
    example = None
    for w, fts, onset in histories(s, site):
        n += 1
        if limit and n > limit:
            n -= 1
            break
        weight = odds ** w
        W += weight
        DZ, DX, truth, _ = s.simulate(*compose(fts))
        dec = {}
        for arm in nd_infer.ARMS:
            d_arm = D.direct(DZ, DX, arm)
            if roundtrip:
                st = D.serialize(DZ, DX, arm)
                js = json.loads(json.dumps(st))      # force a JSON round-trip
                if D.decode_state(js) != d_arm:
                    rt_mism += 1
                bits = D.payload_bits(arm, st)
            else:
                bits = D.payload_bits(arm, D.serialize(DZ, DX, arm))
            dec[arm] = d_arm
            tt = tot[arm]
            tt['pay_max'] = max(tt['pay_max'], bits)
            tt['pay_weighted'] += weight * bits
        ref = dec['thick']
        if dec['whole']['label'] != ref['label']:
            whole_ne += 1
        for arm, dd in dec.items():
            tt = tot[arm]
            tt['raw'] += dd['label'] != ref['label']
            tt['hard_agree'] += weight * (dd['label'] == ref['label'])
            tt['hard_correct'] += weight * (dd['label'] == truth)
        if dec['diamond']['label'] != ref['label']:
            share['diamond_right' if dec['diamond']['label'] == truth else 'reference_right'] += 1
            if example is None or weight > example['weight']:
                example = dict(weight=weight, faults=[list(f) for f in fts], onset=onset,
                               truth=truth, decisions={a: dec[a]['label'] for a in dec})
        if n % 20000 == 0:
            print(d, site, n, 'histories', round(time.time() - start, 1), 's', flush=True)
    for tt in tot.values():
        tt['hard_agree'] /= W; tt['hard_correct'] /= W; tt['pay_weighted'] /= W
    out = dict(d=d, site=list(site), query=D.query, n=n, weight=W,
              arms={a: dict(raw_disagree=tot[a]['raw'],
                            weighted_agreement=round(tot[a]['hard_agree'], 6),
                            weighted_disagreement_pct=round((1 - tot[a]['hard_agree']) * 100, 4),
                            weighted_truth=round(tot[a]['hard_correct'], 6),
                            payload_max=tot[a]['pay_max'],
                            payload_mean=round(tot[a]['pay_weighted'], 4)) for a in nd_infer.ARMS},
              diamond_split=dict(share), roundtrip_mismatches=rt_mism,
              whole_ne_thick=whole_ne, example=example, elapsed=round(time.time() - start, 1),
              frame_table_sizes={sec: len(D._frame_table[sec]) for sec in ('X', 'Z')},
              w_dec=D.w_dec, w_frame=D.w_frame, config_table_rows={sec: len(D._tab[sec]['ODDS']) for sec in ('X', 'Z')})
    return out


if __name__ == '__main__':
    d = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    site = tuple(map(int, sys.argv[2].split(','))) if len(sys.argv) > 2 else (1, 1)
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    out = run(d, site, limit=limit)
    Path('../results').mkdir(exist_ok=True)
    tag = f'd{d}_{site[0]}_{site[1]}' + (f'_lim{limit}' if limit else '')
    Path(f'../results/{tag}.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({a: out['arms'][a]['raw_disagree'] for a in nd_infer.ARMS}),
          'split', out['diamond_split'], 'roundtrip_mism', out['roundtrip_mismatches'],
          'whole!=thick', out['whole_ne_thick'], 'elapsed', out['elapsed'])
