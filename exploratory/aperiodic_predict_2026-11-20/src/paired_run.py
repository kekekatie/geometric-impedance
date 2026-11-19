"""Paired route test: decode every eligible edge of each fresh patch over the EXHAUSTIVE
zero-/one-/two-ordinary-fault x8-variant ensemble (identical configs across edges and
arms), store per-config tie-aware credit contributions so G and the paired contrast
Delta=G(on)-G(off) get a cluster bootstrap (each config's 8 variants kept together).

Reuses the audited engine from the pilot (patch_code / patch_decoder / nd_* ) via a
FreshPatchCode that loads a patch JSON from this study's results dir. Per-edge checkpoints.
"""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

PILOT_SRC = (Path(__file__).resolve().parents[2]
             / 'aperiodic_decoder_pilot_2026-11-19' / 'src')
sys.path.insert(0, str(PILOT_SRC))
import patch_code as pcmod          # noqa: E402
import patch_decoder as pd          # noqa: E402
import nd_run                        # noqa: E402

RESULTS = Path(__file__).resolve().parents[1] / 'results'
CKPT = RESULTS / '_ckpt'
P = 1e-3
ODDS = P / (1 - P)
ARMS = pd.ARMS
VARIANTS = [(o, vx, vz) for o in (1, 2) for vx in (0, 1) for vz in (0, 1)]


class FreshPatchCode(pcmod.PatchCode):
    """Same adapter as the pilot, but load the patch JSON from an explicit path."""
    def __init__(self, path, p=1e-3, T=5):
        data = json.loads(Path(path).read_text())
        self.family = data['family']; self.json = data
        self.d = 3; self.T = T; self.P = p
        n = data['n']; self.DATA = list(range(n)); self.NDATA = n
        self.DIDX = {q: q for q in self.DATA}
        self.STABS = []
        for row in data['HX']:
            self.STABS.append({'type': 'X', 'support': tuple(q for q in range(n) if row[q])})
        for row in data['HZ']:
            self.STABS.append({'type': 'Z', 'support': tuple(q for q in range(n) if row[q])})
        self.XSTABS = [k for k, s in enumerate(self.STABS) if s['type'] == 'X']
        self.ZSTABS = [k for k, s in enumerate(self.STABS) if s['type'] == 'Z']
        self.NSTAB = len(self.STABS)
        self.ZDETS = [(k, t) for k in self.ZSTABS for t in range(T)]
        self.XDETS = [(k, t) for k in self.XSTABS for t in range(T)]
        self.LZ = [1 if q in set(data['logical_Z']) else 0 for q in range(n)]
        self.XL = [1 if q in set(data['logical_X']) else 0 for q in range(n)]
        assert self._dot(self.LZ, self.XL) == 1
        self.STAR = {}; self.eligible = {}
        for e in data['eligible']:
            self.STAR[e['qubit']] = sorted(pcmod.check_index(c) for c in e['checks'])
            self.eligible[e['qubit']] = e
        self._frame_cache = {}


def ordinary_pool(code):
    s = code
    pool = [('X', q, t) for q in s.DATA for t in range(5)] + \
           [('Z', q, t) for q in s.DATA for t in range(5)]
    pool += [('MZ', k, t) for k in s.ZSTABS for t in range(5)]
    pool += [('MX', k, t) for k in s.XSTABS for t in range(5)]
    return pool


def config_stream(pool):
    """Exhaustive k in {0,1,2}, deterministic order; yield (cfg_id, k, extra)."""
    cid = 0
    yield cid, 0, (); cid += 1
    for i in range(len(pool)):
        yield cid, 1, (pool[i],); cid += 1
    for i, j in itertools.combinations(range(len(pool)), 2):
        yield cid, 2, (pool[i], pool[j]); cid += 1


def cred(d, truth):
    return 0.5 if d['tie'] else (1.0 if d['label'] == truth else 0.0)


def decode_edge(code, site, roundtrip_every=2003):
    D = pd.PatchDecoder(code, site)
    pool = ordinary_pool(code)
    rows = []           # per config: [w, ck_thick, ck_thin, ck_diamond, ck_whole, hard_thick, hard_thin]
    whole_ne = 0; rt_checked = rt_mism = 0; n = 0
    for cid, k, extra in config_stream(pool):
        w = ODDS ** k
        acc = [w, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for (onset, vx, vz) in VARIANTS:
            loss = ([('X', site, onset)] if vx else []) + ([('Z', site, onset)] if vz else [])
            DZ, DX, truth, _ = code.simulate(*nd_run.compose(extra + tuple(loss)))
            dec = {a: D.direct(DZ, DX, a) for a in ARMS}
            acc[1] += cred(dec['thick'], truth); acc[2] += cred(dec['thin'], truth)
            acc[3] += cred(dec['diamond'], truth); acc[4] += cred(dec['whole'], truth)
            acc[5] += 1.0 if dec['thick']['label'] == truth else 0.0
            acc[6] += 1.0 if dec['thin']['label'] == truth else 0.0
            if dec['whole']['label'] != dec['thick']['label'] or abs(dec['whole']['p0'] - dec['thick']['p0']) > pd.EPS:
                whole_ne += 1
            n += 1
            if n % roundtrip_every == 0:
                rt_checked += 1
                for a in ARMS:
                    st = D.serialize(DZ, DX, a)
                    if D.decode_state(json.loads(json.dumps(st))) != dec[a]:
                        rt_mism += 1
        rows.append(acc)
        if len(D._mcache) > 500000:
            D._mcache.clear()
    return dict(site=site, n=n, rows=rows, whole_ne=whole_ne,
                rt_checked=rt_checked, rt_mism=rt_mism, query=D.query)


def main():
    CKPT.mkdir(parents=True, exist_ok=True)
    patches = ['AB_1', 'Penrose_1', 'Penrose_2']
    for name in patches:
        code = FreshPatchCode(RESULTS / f'{name}.json')
        for q, elig in sorted(code.eligible.items()):
            eid = elig['edge']
            tag = f'{name}_e{eid}_q{q}'
            ck = CKPT / f'{tag}.json'
            if ck.exists():
                print(f'{tag}: checkpoint exists', flush=True)
                continue
            t0 = time.time()
            res = decode_edge(code, q)
            res['patch'] = name; res['edge'] = eid; res['qubit'] = q
            W = sum(r[0] for r in res['rows'])
            res['W'] = W
            res['G_thick_thin'] = 100 * sum(r[0] * (r[1] - r[2]) for r in res['rows']) / (8 * W)
            res['diamond_thin'] = 100 * sum(r[0] * (r[3] - r[2]) for r in res['rows']) / (8 * W)
            res['thick_diamond'] = 100 * sum(r[0] * (r[1] - r[3]) for r in res['rows']) / (8 * W)
            ck.write_text(json.dumps(res))
            print(f'{tag}: n={res["n"]} G(thick-thin)={res["G_thick_thin"]:+.5f} '
                  f'diamond-thin={res["diamond_thin"]:+.5f} whole_ne={res["whole_ne"]} '
                  f'rt={res["rt_mism"]}/{res["rt_checked"]} [{round(time.time()-t0,1)}s]', flush=True)
    print('ALL EDGES DECODED', flush=True)


if __name__ == '__main__':
    main()
