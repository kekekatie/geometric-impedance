"""Combine the per-edge checkpoints into the paired route result: G per eligible edge,
Delta_patch = G(on) - G(off), and a paired cluster bootstrap over the shared ordinary-fault
configurations (each config's 8 variants kept together). Writes results/paired_results.json.
"""
import json
from pathlib import Path

import numpy as np

RESULTS = Path(__file__).resolve().parents[1] / 'results'
CKPT = RESULTS / '_ckpt'
BOOT = 10000
BOOT_SEED = 20261120
PATCHES = ('AB_1', 'Penrose_1', 'Penrose_2')


def load_edges():
    edges = {}
    for f in sorted(CKPT.glob('*.json')):
        r = json.loads(f.read_text())
        edges[(r['patch'], r['edge'])] = r
    return edges


def g_series(rows):
    """Per-config contribution arrays for G = thick-thin (numerator terms) and weight."""
    a = np.array(rows, dtype=np.float64)       # [,0]=w [,1]=thick [,2]=thin [,3]=diamond
    w = a[:, 0]
    num = w * (a[:, 1] - a[:, 2])              # thick-thin
    dnum = w * (a[:, 3] - a[:, 2])             # diamond-thin
    return w, num, dnum, a


def main():
    edges = load_edges()
    sel = json.loads((RESULTS / 'selection.json').read_text())
    pairs = {}
    for fam in ('AB', 'Penrose'):
        for ent in sel['families'][fam]['selected']:
            name = ent['name']
            pairs[name] = (ent['predicted_pair']['on_route_edge'],
                           ent['predicted_pair']['off_route_edge'])
    rng = np.random.default_rng(BOOT_SEED)
    out = {'edges': {}, 'patches': {}}
    # per-edge G values
    for (patch, eid), r in edges.items():
        out['edges'][f'{patch}_e{eid}'] = dict(
            patch=patch, edge=eid, qubit=r['qubit'],
            G_thick_thin=round(r['G_thick_thin'], 5),
            diamond_thin=round(r['diamond_thin'], 5),
            thick_diamond=round(r['thick_diamond'], 5),
            whole_ne=r['whole_ne'], rt_mism=r['rt_mism'], rt_checked=r['rt_checked'],
            n=r['n'])
    # per-patch paired contrast + cluster bootstrap
    for patch, (on_e, off_e) in pairs.items():
        if (patch, on_e) not in edges or (patch, off_e) not in edges:
            continue
        ron, roff = edges[(patch, on_e)], edges[(patch, off_e)]
        won, non, _, _ = g_series(ron['rows'])
        woff, noff, _, _ = g_series(roff['rows'])
        Won, Woff = won.sum(), woff.sum()
        G_on = 100 * non.sum() / (8 * Won)
        G_off = 100 * noff.sum() / (8 * Woff)
        delta = G_on - G_off
        # paired cluster bootstrap over shared config indices (same order both edges)
        m = len(won); boot = np.empty(BOOT)
        for b in range(BOOT):
            idx = rng.integers(0, m, m)
            go = 100 * non[idx].sum() / (8 * won[idx].sum())
            gf = 100 * noff[idx].sum() / (8 * woff[idx].sum())
            boot[b] = go - gf
        lo, hi = np.percentile(boot, [2.5, 97.5])
        out['patches'][patch] = dict(
            on_edge=on_e, off_edge=off_e,
            G_on=round(G_on, 5), G_off=round(G_off, 5),
            delta=round(delta, 5), ci=[round(lo, 5), round(hi, 5)],
            prediction_holds=bool(delta > 0),
            ci_excludes_zero=bool(lo > 0 or hi < 0),
            diamond_thin_on=round(ron['diamond_thin'], 5),
            thick_diamond_on=round(ron['thick_diamond'], 5),
            diamond_thin_off=round(roff['diamond_thin'], 5))
        print(f'{patch}: G_on(e{on_e})={G_on:+.5f}  G_off(e{off_e})={G_off:+.5f}  '
              f'Delta={delta:+.5f}  CI[{lo:+.5f},{hi:+.5f}]  '
              f'{"HOLDS" if delta>0 else "MISS"}{" (CI>0)" if lo>0 else ""}', flush=True)
    (RESULTS / 'paired_results.json').write_text(json.dumps(out, indent=2) + '\n')
    inv = [(k, v['whole_ne'], v['rt_mism']) for k, v in out['edges'].items()
           if v['whole_ne'] or v['rt_mism']]
    print('invariant anomalies (whole_ne / rt_mism):', inv or 'none')
    print('WROTE results/paired_results.json')


if __name__ == '__main__':
    main()
