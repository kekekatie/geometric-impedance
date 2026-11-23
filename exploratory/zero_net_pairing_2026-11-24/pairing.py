"""Test the frozen candidate symmetries as exact lost->gained bijections on the collected
credit-moving histories.

(a) erasure free-value swaps and (b) onset swap keep the ordinary configuration fixed and
are tested directly on the flip keys (they fail -- see results). The structural pairing is
(d): adding the on-route weight-3 X-logical to the total X-fault flips the scored truth while
leaving the full detector record (hence every arm's decision and posterior) identical, so a
credit-lost history and its partner carry equal weight and opposite credit delta. We realise
(d) by grouping movers on their exact detector record: within a record group the decoder
decides identically, so two members of opposite truth are an exact lost<->gained pair, and
their total-X-fault symmetric difference is verified to be a weight-3 X-logical (candidate c,
a patch automorphism fixing e4, is not needed and is reported as such)."""
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent / 'fresh_site_address_audit_2026-11-20'
sys.path.insert(0, str(AUDIT))
import audit                      # noqa: E402
E = audit.engine
RESULTS = ROOT / 'results'
EPS = 1e-12

VARIANT_MAPS = {
    'free_vx': lambda o, x, z: (o, 1 - x, z),
    'free_vz': lambda o, x, z: (o, x, 1 - z),
    'free_both': lambda o, x, z: (o, 1 - x, 1 - z),
    'onset': lambda o, x, z: (3 - o, x, z),
    'onset+free_vx': lambda o, x, z: (3 - o, 1 - x, z),
    'onset+free_both': lambda o, x, z: (3 - o, 1 - x, 1 - z),
}


def weight_matched(lost, gained):
    lc = Counter((r['k'], round(-r['delta'], 10)) for r in lost)
    gc = Counter((r['k'], round(r['delta'], 10)) for r in gained)
    return lc == gc


def variant_bijection(name, fn, lost, gained):
    gb = defaultdict(list)
    for g in gained:
        gb[(g['cid'], g['onset'], g['vx'], g['vz'])].append(g)
    used = set(); paired = 0
    for r in lost:
        o, x, z = fn(r['onset'], r['vx'], r['vz'])
        for g in gb.get((r['cid'], o, x, z), []):
            if id(g) not in used and abs(g['delta'] + r['delta']) <= EPS and g['k'] == r['k']:
                used.add(id(g)); paired += 1; break
    return paired == len(lost) == len(gained)


def xlogicals_w3(code):
    HX = code.hx() if hasattr(code, 'hx') else np.array(
        [[1 if q in s['support'] else 0 for q in range(code.NDATA)]
         for s in code.STABS if s['type'] == 'X'])
    HZ = np.array([[1 if q in s['support'] else 0 for q in range(code.NDATA)]
                   for s in code.STABS if s['type'] == 'Z'])

    def rint(r):
        return int(''.join('1' if b else '0' for b in r[::-1]), 2)
    def basis(ints):
        bs = []
        for v in ints:
            x = v
            for b in bs:
                x = min(x, x ^ b)
            if x:
                bs.append(x); bs.sort(reverse=True)
        return bs
    rowHX = basis([rint(r) for r in HX])
    out = []
    n = code.NDATA
    for combo in itertools.combinations(range(n), 3):
        v = 0
        for q in combo:
            v |= 1 << q
        if all(sum((rint(r) >> q) & 1 for q in combo) % 2 == 0 for r in HZ):
            x = v
            for b in rowHX:
                x = min(x, x ^ b)
            if x:
                out.append(frozenset(combo))
    return out


def xsupport(extra, q, vx):
    cnt = Counter()
    for f in extra:
        if f[0] == 'X':
            cnt[f[1]] ^= 1
    if vx:
        cnt[q] ^= 1
    return frozenset(x for x, b in cnt.items() if b)


def record_key(dz, dx):
    s = json.dumps([sorted((list(k), v) for k, v in dz.items()),
                    sorted((list(k), v) for k, v in dx.items())], separators=(',', ':'))
    return hashlib.sha1(s.encode()).hexdigest()


def structural_pairing(code, q, movers):
    """Group movers by exact detector record; pair opposite-truth members; verify the
    total-X-fault symmetric difference of each pair is a weight-3 X-logical."""
    w3 = set(xlogicals_w3(code))
    groups = defaultdict(list)
    for r in movers:
        onset, vx, vz = r['onset'], r['vx'], r['vz']
        loss = ([('X', q, onset)] if vx else []) + ([('Z', q, onset)] if vz else [])
        extra = [tuple(f) for f in r['extra']]
        dz, dx, truth, _ = code.simulate(*E.prior.nd_run.compose(tuple(extra) + tuple(loss)))
        assert truth == r['truth']
        groups[record_key(dz, dx)].append((r, xsupport(extra, q, vx)))
    pairs = 0; unpaired = []; logical_diffs = Counter(); bad_logical = 0
    for key, members in groups.items():
        lost = [(r, xs) for r, xs in members if r['delta'] < 0]
        gained = [(r, xs) for r, xs in members if r['delta'] > 0]
        used = set()
        for rl, xsl in lost:
            match = None
            for i, (rg, xsg) in enumerate(gained):
                if i in used:
                    continue
                if abs(rg['delta'] + rl['delta']) <= EPS and rg['truth'] != rl['truth'] and rg['k'] == rl['k']:
                    match = i; break
            if match is None:
                unpaired.append(rl)
            else:
                used.add(match); pairs += 1
                diff = xsl ^ gained[match][1]
                logical_diffs[len(diff)] += 1
                if diff not in w3:
                    bad_logical += 1
        unpaired += [rg for i, (rg, xsg) in enumerate(gained) if i not in used]
    return dict(n_movers=len(movers), pairs=pairs, unpaired=len(unpaired),
                record_groups=len(groups),
                symmetric_difference_weights=dict(logical_diffs),
                pairs_differing_by_weight3_xlogical=pairs - bad_logical,
                pairs_not_weight3_xlogical=bad_logical,
                unpaired_records=[dict(cid=r['cid'], onset=r['onset'], vx=r['vx'], vz=r['vz'],
                                       k=r['k'], delta=r['delta'], truth=r['truth']) for r in unpaired[:20]])


def main():
    out = {}
    for f in sorted(RESULTS.glob('flips_*.json')):
        data = json.loads(f.read_text())
        code = audit.CorrectedPatchCode(audit.SOURCE / (data['patch'] + '.json'))
        q = data['qubit']
        rep = dict(patch=data['patch'], edge=data['edge'], qubit=q, checks={})
        for c, ch in data['checks'].items():
            movers = ch['records']
            lost = [r for r in movers if r['delta'] < 0]
            gained = [r for r in movers if r['delta'] > 0]
            variants = [n for n, fn in VARIANT_MAPS.items() if variant_bijection(n, fn, lost, gained)]
            struct = structural_pairing(code, q, movers)
            rep['checks'][c] = dict(
                flips=ch['flips'], tie_changes=ch['tie_changes'],
                lost_pp=ch['lost_pp'], gained_pp=ch['gained_pp'], net_pp=ch['net_pp'],
                n_lost=len(lost), n_gained=len(gained),
                weight_matched=weight_matched(lost, gained),
                variant_swap_bijections=variants,
                structural=struct)
            print(f"{data['patch']} {c}: movers={struct['n_movers']} net={ch['net_pp']:.8f} "
                  f"weight_matched={rep['checks'][c]['weight_matched']} variant_swaps={variants} "
                  f"record-paired={struct['pairs']} unpaired={struct['unpaired']} "
                  f"diff-is-w3-Xlogical={struct['pairs_differing_by_weight3_xlogical']}/{struct['pairs']} "
                  f"sdiff_weights={struct['symmetric_difference_weights']}", flush=True)
        out[f"{data['patch']}_e{data['edge']}"] = rep
    (RESULTS / 'pairing.json').write_text(json.dumps(out, indent=2) + '\n')
    print('WROTE results/pairing.json', flush=True)


if __name__ == '__main__':
    main()
