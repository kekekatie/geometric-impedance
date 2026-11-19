"""Discriminator cap test (honest replacement for the vacuous seeded panel).

The frozen seeded cap panel contained NO history on which the arms disagree, so its
paired benefits are identically 0 at every cap -- it cannot test cap sensitivity of the
benefits (only prefix coverage, which it confirms). This module instead finds, at (3,3),
every history on a chosen edge where the four arms do not all agree (the only histories
that carry any paired benefit), then re-decodes exactly those at (3,3),(4,3),(3,4),(4,4).
Because non-discriminators contribute 0 to every paired benefit, the benefit reconstructed
from the discriminators (weighted by the true ensemble weight, divided by the full W)
equals the primary benefit at (3,3) -- a built-in check -- and its change at higher caps
is the real cap-sensitivity test on the signal-carrying histories.
"""
import json
import time
from pathlib import Path

import patch_code as pc
import patch_decoder as pd
import patch_run as pr
import nd_run

RESULTS = Path(__file__).resolve().parents[1] / 'results'
EDGES = [('square', 14, 'square_e18'),   # the one on-logical edge (+0.114 pp)
         ('AB', 16, 'AB_e22'),           # high-degree aperiodic (+0.0045)
         ('Penrose', 3, 'Penrose_e2')]   # the clearly-negative aperiodic edge
CAPS = [(3, 3), (4, 3), (3, 4), (4, 4)]
ODDS = pr.ODDS


def collect_discriminators(code, site):
    """Return [(extra, onset, vx, vz, weight, truth)] for histories where the four arms
    do not all share a label at (3,3)."""
    D = pd.PatchDecoder(code, site)
    pool = pr.ordinary_pool(code)
    pairs, total, _, _ = pr.k2_sample(310, 8000)
    disc = []
    W = 0.0
    for k, extra, ht in pr.config_stream(pool, pairs, total):
        w = (ODDS ** k) * ht
        for (onset, vx, vz) in pr.VARIANTS:
            W += w
            loss = ([('X', site, onset)] if vx else []) + ([('Z', site, onset)] if vz else [])
            DZ, DX, truth, _ = code.simulate(*nd_run.compose(extra + tuple(loss)))
            labels = {D.direct(DZ, DX, a)['label'] for a in pd.ARMS}
            if len(labels) > 1:
                disc.append((extra, onset, vx, vz, w, truth))
        if len(D._mcache) > 400000:
            D._mcache.clear()
    return disc, W


def benefit(code, site, Dcls, caps, disc, W):
    wf, wd = caps
    D = Dcls(code, site, w_frame=wf, w_dec=wd)
    acc = {a: 0.0 for a in pd.ARMS}
    recs = []
    for (extra, onset, vx, vz, w, truth) in disc:
        loss = ([('X', site, onset)] if vx else []) + ([('Z', site, onset)] if vz else [])
        DZ, DX, truth2, _ = code.simulate(*nd_run.compose(extra + tuple(loss)))
        dec = {a: D.direct(DZ, DX, a) for a in pd.ARMS}
        for a in pd.ARMS:
            d = dec[a]
            acc[a] += w * (0.5 if d['tie'] else (1.0 if d['label'] == truth2 else 0.0))
        recs.append({a: dec[a]['label'] for a in pd.ARMS})
    return dict(
        thick_minus_thin=100 * (acc['thick'] - acc['thin']) / W,
        diamond_minus_thin=100 * (acc['diamond'] - acc['thin']) / W,
        thick_minus_diamond=100 * (acc['thick'] - acc['diamond']) / W,
    ), recs


def main():
    out = {}
    for fam, site, tag in EDGES:
        code = pc.PatchCode(fam)
        t0 = time.time()
        disc, W = collect_discriminators(code, site)
        print(f'{tag}: {len(disc)} discriminator histories (of ensemble W={W:.5f}) '
              f'in {round(time.time()-t0,1)}s', flush=True)
        rec = {'n_disc': len(disc), 'W': W, 'caps': {}}
        base_recs = None
        for caps in CAPS:
            t1 = time.time()
            ben, recs = benefit(code, site, pd.PatchCapDecoder, caps, disc, W)
            ctag = f'{caps[0]}{caps[1]}'
            if ctag == '33':
                base_recs = recs
                flips = 0
            else:
                flips = sum(1 for r0, r1 in zip(base_recs, recs)
                            for a in pd.ARMS if r0[a] != r1[a])
            rec['caps'][ctag] = dict(benefits={k: round(v, 5) for k, v in ben.items()},
                                     label_flips_vs_33=flips)
            print(f'  ({ctag}) tt={ben["thick_minus_thin"]:+.5f} dt={ben["diamond_minus_thin"]:+.5f} '
                  f'tk-d={ben["thick_minus_diamond"]:+.5f} flips_vs33={flips} '
                  f'[{round(time.time()-t1,1)}s]', flush=True)
        out[tag] = rec
        code._cap_tab = {}; code._cap_frame = {}
    (RESULTS / 'caps_discriminator.json').write_text(json.dumps(out, indent=2) + '\n')
    print('WROTE results/caps_discriminator.json', flush=True)


if __name__ == '__main__':
    main()
