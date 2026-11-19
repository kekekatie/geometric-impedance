"""Cap-sensitivity panel across all 18 sites. A small, seeded, diagnostic panel (not a
population estimate) is replayed at (w_frame,w_dec) = (3,3),(4,3),(3,4),(4,4) via the
audited chunked packed builder (PatchCapDecoder). Reports unsupported frame prefixes per
cap and CHANGES in the paired arm benefits (thick-thin, diamond-thin, thick-diamond)
between caps; flags edges where a feature moves or changes sign.

Panel (frozen): per site, k=0 (1 config) + seeded k=1 (8 configs) + seeded k=2 (6 configs),
x8 variants = 120 histories/site x 18 = 2,160 histories, shared ordinary configs across
sites. Seed 20261119.
"""
import json
import random
import time
from pathlib import Path

import patch_code as pc
import patch_decoder as pd
import patch_run as pr
import nd_run

RESULTS = Path(__file__).resolve().parents[1] / 'results'
CKPT = RESULTS / '_capckpt'
PATCHES = ('square', 'AB', 'Penrose')
CAPS = [(3, 3), (4, 3), (3, 4), (4, 4)]
SEED = 20261119
S1, S2 = 8, 6              # seeded k=1 and k=2 configs
EPS = pd.EPS


def panel_configs():
    rng = random.Random(SEED)
    pool_idx = list(range(310))
    k1 = sorted(rng.sample(pool_idx, S1))
    import itertools
    allpairs = list(itertools.combinations(range(310), 2))
    k2 = [allpairs[i] for i in sorted(rng.sample(range(len(allpairs)), S2))]
    return k1, k2


def cred(d, truth):
    return 0.5 if d['tie'] else (1.0 if d['label'] == truth else 0.0)


def decode_panel(code, site, Dcls, caps, k1, k2):
    wf, wd = caps
    D = Dcls(code, site, w_frame=wf, w_dec=wd)
    pool = pr.ordinary_pool(code)
    configs = [(0, ())] + [(1, (pool[i],)) for i in k1] + [(2, (pool[a], pool[b])) for a, b in k2]
    acc = {a: 0.0 for a in pd.ARMS}
    n = 0
    absent = 0
    recs = []
    for k, extra in configs:
        for (onset, vx, vz) in pr.VARIANTS:
            loss = ([('X', site, onset)] if vx else []) + ([('Z', site, onset)] if vz else [])
            DZ, DX, truth, _ = code.simulate(*nd_run.compose(extra + tuple(loss)))
            dec = {a: D.direct(DZ, DX, a) for a in pd.ARMS}
            for a in pd.ARMS:
                acc[a] += cred(dec[a], truth)
            pa = D.prefix_absent(DZ, DX)
            absent += int(pa['X'] or pa['Z'])
            recs.append({a: (dec[a]['label'], round(dec[a]['p0'], 9), dec[a]['tie']) for a in pd.ARMS}
                        | {'truth': truth})
            n += 1
    benefits = dict(
        thick_minus_thin=100 * (acc['thick'] - acc['thin']) / n,
        diamond_minus_thin=100 * (acc['diamond'] - acc['thin']) / n,
        thick_minus_diamond=100 * (acc['thick'] - acc['diamond']) / n,
    )
    return dict(n=n, benefits=benefits, prefix_absent=absent, recs=recs)


def main():
    CKPT.mkdir(parents=True, exist_ok=True)
    k1, k2 = panel_configs()
    # validation: PatchCapDecoder(3,3) must reproduce PatchDecoder(3,3) exactly
    code0 = pc.PatchCode('square')
    mism = 0
    import nd_run as _nr
    pool = pr.ordinary_pool(code0)
    Da = pd.PatchDecoder(code0, 5)
    Db = pd.PatchCapDecoder(code0, 5, w_frame=3, w_dec=3)
    for k, extra in [(0, ())] + [(1, (pool[i],)) for i in k1[:4]] + [(2, (pool[a], pool[b])) for a, b in k2[:3]]:
        for (onset, vx, vz) in pr.VARIANTS:
            loss = ([('X', 5, onset)] if vx else []) + ([('Z', 5, onset)] if vz else [])
            DZ, DX, truth, _ = code0.simulate(*_nr.compose(extra + tuple(loss)))
            for a in pd.ARMS:
                if Da.direct(DZ, DX, a) != Db.direct(DZ, DX, a):
                    mism += 1
    print(f'CapDecoder(3,3) vs PatchDecoder(3,3): {mism} mismatches', flush=True)
    assert mism == 0, 'cap builder must reproduce stock at (3,3)'

    out = dict(panel=dict(seed=SEED, s1=S1, s2=S2, k1=k1, k2=[list(x) for x in k2]),
               caps={}, by_edge={})
    for caps in CAPS:
        tag = f'{caps[0]}{caps[1]}'
        ck = CKPT / f'{tag}.json'
        if ck.exists():
            out['caps'][tag] = json.loads(ck.read_text())
            print(f'cap {tag}: loaded checkpoint', flush=True)
            continue
        t0 = time.time()
        capres = {}
        for fam in PATCHES:
            code = pc.PatchCode(fam)
            for elig in code.json['eligible']:
                site = elig['qubit']; eid = elig['edge']
                r = decode_panel(code, site, pd.PatchCapDecoder, caps, k1, k2)
                capres[f'{fam}_e{eid}'] = r
            # free the heavy per-patch cap tables before the next patch
            code._cap_tab = {}; code._cap_frame = {}
        out['caps'][tag] = capres
        ck.write_text(json.dumps(capres))
        print(f'cap {tag}: {len(capres)} edges in {round(time.time()-t0,1)}s', flush=True)

    # changes vs (3,3): per edge, benefit deltas + label flips vs baseline
    base = out['caps']['33']
    for tag in ('43', '34', '44'):
        if tag not in out['caps']:
            continue
        cur = out['caps'][tag]
        changed = []
        for e in base:
            b0 = base[e]['benefits']; b1 = cur[e]['benefits']
            flips = sum(1 for r0, r1 in zip(base[e]['recs'], cur[e]['recs'])
                        for a in pd.ARMS if r0[a][0] != r1[a][0])
            d = {k: round(b1[k] - b0[k], 4) for k in b0}
            sign = any((b0[k] > 1e-9) != (b1[k] > 1e-9) or (b0[k] < -1e-9) != (b1[k] < -1e-9)
                       for k in b0)
            if flips or any(abs(v) > 1e-9 for v in d.values()):
                changed.append(dict(edge=e, delta=d, label_flips=flips, sign_change=sign,
                                    prefix_absent_base=base[e]['prefix_absent'],
                                    prefix_absent=cur[e]['prefix_absent']))
        out['by_edge'][f'{tag}_vs_33'] = changed
        print(f'{tag} vs 33: {len(changed)} edges changed; '
              f'sign-changes {sum(c["sign_change"] for c in changed)}', flush=True)
    # drop bulky per-history recs before writing
    for tag in out['caps']:
        for e in out['caps'][tag]:
            out['caps'][tag][e].pop('recs', None)
    (RESULTS / 'caps.json').write_text(json.dumps(out, indent=2) + '\n')
    for ck in CKPT.glob('*.json'):
        ck.unlink()
    print('WROTE results/caps.json', flush=True)


if __name__ == '__main__':
    main()
