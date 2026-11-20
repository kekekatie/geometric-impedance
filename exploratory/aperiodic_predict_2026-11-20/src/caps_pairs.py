"""Cap sensitivity on the predicted pair edges. Preselected, outcome-independent panel per
edge: all zero- and one-fault configs (311) + a seeded two-fault sample (N=120), x8
variants = 3,448 histories/edge -- baseline-agreeing histories included so a disagreement
that first appears at a higher cap is visible. Replay the identical panel at (3,3),(4,3),
(3,4),(4,4) via the audited chunked builder (PatchCapDecoder on a FreshPatchCode). For each
edge/cap report G=thick-thin (pp), diamond-thin, prefix-absence, and label flips vs (3,3).
"""
import json
import random
import sys
import time
from pathlib import Path

PILOT_SRC = (Path(__file__).resolve().parents[2]
             / 'aperiodic_decoder_pilot_2026-11-19' / 'src')
sys.path.insert(0, str(PILOT_SRC))
import patch_decoder as pd          # noqa: E402
import nd_run                        # noqa: E402

import paired_run as pr              # FreshPatchCode, ordinary_pool, VARIANTS

RESULTS = Path(__file__).resolve().parents[1] / 'results'
CKPT = RESULTS / '_capckpt'
CAPS = [(3, 3), (4, 3)]   # frame-cap comparison (w_dec=3; fast, restart-safe). w_dec=4
# caps ((3,4),(4,4)) were dropped from the automated panel after repeated container restarts
# kept interrupting their ~20-min-per-edge 20.6M-row builds; see HANDBACK section C.
SEED = 20261120
N_K2 = 120
EPS = pd.EPS


def panel(code):
    pool = pr.ordinary_pool(code)
    rng = random.Random(SEED)
    import itertools
    allpairs = list(itertools.combinations(range(len(pool)), 2))
    k2 = [allpairs[i] for i in sorted(rng.sample(range(len(allpairs)), N_K2))]
    cfgs = [(0, ())] + [(1, (pool[i],)) for i in range(len(pool))] + \
           [(2, (pool[a], pool[b])) for a, b in k2]
    return cfgs


def cred(d, truth):
    return 0.5 if d['tie'] else (1.0 if d['label'] == truth else 0.0)


def decode(code, site, caps, cfgs):
    wf, wd = caps
    D = pd.PatchCapDecoder(code, site, w_frame=wf, w_dec=wd)
    acc = {a: 0.0 for a in pd.ARMS}; n = 0; absent = 0; labels = []
    for k, extra in cfgs:
        for (o, vx, vz) in pr.VARIANTS:
            loss = ([('X', site, o)] if vx else []) + ([('Z', site, o)] if vz else [])
            DZ, DX, truth, _ = code.simulate(*nd_run.compose(extra + tuple(loss)))
            dec = {a: D.direct(DZ, DX, a) for a in pd.ARMS}
            for a in pd.ARMS:
                acc[a] += cred(dec[a], truth)
            pa = D.prefix_absent(DZ, DX); absent += int(pa['X'] or pa['Z'])
            labels.append(tuple(dec[a]['label'] for a in pd.ARMS)); n += 1
    return dict(n=n, G=100 * (acc['thick'] - acc['thin']) / n,
                diamond_thin=100 * (acc['diamond'] - acc['thin']) / n,
                prefix_absent=absent, labels=labels)


def main():
    CKPT.mkdir(parents=True, exist_ok=True)
    sel = json.loads((RESULTS / 'selection.json').read_text())
    targets = []
    for fam in ('AB', 'Penrose'):
        for ent in sel['families'][fam]['selected']:
            pp = ent['predicted_pair']
            targets.append((ent['name'], pp['on_route_edge'], pp['off_route_edge']))
    out = {}
    for name, on_e, off_e in targets:
        code = pr.FreshPatchCode(RESULTS / f'{name}.json')
        emap = {e['edge']: q for q, e in code.eligible.items()}
        cfgs = panel(code)
        for role, eid in (('on', on_e), ('off', off_e)):
            site = emap[eid]; rec = {}
            base_labels = None
            for caps in CAPS:
                ctag = f'{caps[0]}{caps[1]}'
                ck = CKPT / f'{name}_e{eid}_{ctag}.json'
                if ck.exists():
                    r = json.loads(ck.read_text())
                else:
                    t0 = time.time(); r = decode(code, site, caps, cfgs)
                    r['secs'] = round(time.time() - t0, 1); ck.write_text(json.dumps(r))
                if ctag == '33':
                    base_labels = r['labels']; flips = 0
                else:
                    flips = sum(1 for a, b in zip(base_labels, r['labels']) for x, y in zip(a, b) if x != y)
                rec[ctag] = dict(G=round(r['G'], 5), diamond_thin=round(r['diamond_thin'], 5),
                                 prefix_absent=r['prefix_absent'], label_flips_vs33=flips,
                                 n=r['n'])
                print(f'{name} {role} e{eid} ({ctag}) G={r["G"]:+.5f} dt={r["diamond_thin"]:+.5f} '
                      f'absent={r["prefix_absent"]} flips={flips}', flush=True)
            out[f'{name}_{role}_e{eid}'] = rec
            code._cap_tab = {}; code._cap_frame = {}
    (RESULTS / 'caps_pairs.json').write_text(json.dumps(out, indent=2) + '\n')
    for ck in CKPT.glob('*.json'):
        ck.unlink()
    print('WROTE results/caps_pairs.json', flush=True)


if __name__ == '__main__':
    main()
