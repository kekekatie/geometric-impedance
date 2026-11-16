"""Distance-3 CONJUGATE edge-loss control at site (2,1), reusing Astra's E_frame model.

Identical to the (1,2) edge harness except the loss site is (2,1) (star {5,6,7} =
2 Z-arms + 1 X-arm). The scored logical Z_L is decoded by the X-sector (Z-stabs), so
(2,1) keeps both logical-sector Z-arms while the Z-open site (1,2) kept only one. This
isolates logical-sector arms from bracket size (both 6 lip bits).

Frozen by PROTOCOL_AMENDMENT_CONJUGATE.md (commit 9832cd1); model at 09a79c1.
Subcommands: run | worker <arm> | cold | summarize
"""
import sys, json, itertools, hashlib, time, subprocess, os, collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
RW = HERE.parents[0]                                    # reconsideration_witness
CORR = RW / 'correction_2026-11-14'
EDGE12 = RW / 'edge_loss_2026-11-15'
sys.path.insert(0, str(CORR / 'src'))
import model as m                                       # Astra's corrected model, unchanged
from model import frozen as sc

RESULTS = HERE / 'results'
RESULTS.mkdir(exist_ok=True)
CACHE = Path(os.environ.get('CONJ_CACHE', str(HERE / 'runtime'))).resolve()
CACHE.mkdir(parents=True, exist_ok=True)

VARIANT = 'E_frame'
SITE = (2, 1)
REPORT = {'site': [2, 1], 'onsets': [1, 2], 'deadline': 4}
QUERY = len([(k, t) for k in sc.STAR[SITE] for t in REPORT['onsets']])


def histories():
    pool = [(tag, q, t) for q in sc.DATA for t in range(5) for tag in ('X', 'Z')]
    pool += [('MZ', k, t) for k in sc.ZSTABS for t in range(5)]
    pool += [('MX', k, t) for k in sc.XSTABS for t in range(5)]
    for w in range(3):
        for extra in itertools.combinations(pool, w):
            for onset in (1, 2):
                for vx in (0, 1):
                    for vz in (0, 1):
                        loss = ([('X', SITE, onset)] if vx else []) + \
                               ([('Z', SITE, onset)] if vz else [])
                        yield w, tuple(extra) + tuple(loss), onset


def state_of(record, arm):
    state = m.prepare_before_report({d: v for d, v in record.items() if d[1] <= 3}, arm, VARIANT)
    return m.append_round4(state, {k: record[k, 4] for k in range(8)})


def expected_agreement(a, b):
    if a['tie'] and b['tie']:
        return 1.
    if a['tie'] or b['tie']:
        return .5
    return float(a['label'] == b['label'])


def run():
    cfg = m.VARIANTS[VARIANT]
    start = time.time()
    weights = 0.
    n = 0
    checks = 0
    totals = {a: dict(hard_agree=0., hard_correct=0., expected_agree=0., expected_correct=0.,
                      raw_disagree=0, ties=0, payload_weighted=0., payload_max=0,
                      wire_weighted=0., wire_max=0) for a in m.ARMS}
    share = collections.Counter()
    sample = None
    unique = {a: {} for a in m.ARMS}
    unique_expected = {a: {} for a in m.ARMS}
    file_handles = {a: (CACHE / (a + '-states.jsonl')).open('wb') for a in m.ARMS}
    recon_bad = 0
    collision_count = 0
    try:
        for w, fts, onset in histories():
            n += 1
            collision_count += len(set(fts)) != len(fts)
            weight = (sc.P / (1 - sc.P) if cfg['odds'] else sc.P) ** w
            weights += weight
            DZ, DX, truth, _ = sc.simulate(*m.compose(fts, cfg['parity']))
            record = m.full_record(DZ, DX)
            dec = {}
            states = {}
            for arm in m.ARMS:
                state = state_of(record, arm)
                wire = m.encode(state)
                restored = m.restore(wire)
                actual = m.decode(restored, REPORT)
                direct = m.direct(DZ, DX, arm, REPORT, VARIANT)
                assert actual == direct, (n, arm, 'roundtrip/direct')
                checks += 1
                dec[arm] = actual
                states[arm] = state
                t = totals[arm]
                bits = m.payload_bits(state)
                t['payload_weighted'] += weight * bits
                t['payload_max'] = max(t['payload_max'], bits)
                t['wire_weighted'] += weight * len(wire)
                t['wire_max'] = max(t['wire_max'], len(wire))
                t['ties'] += actual['tie']
                key = hashlib.sha256(wire).hexdigest()
                if key not in unique[arm]:
                    unique[arm][key] = 1
                    unique_expected[arm][key] = actual
                    entry = dict(id=key, state=restored, report=REPORT)
                    file_handles[arm].write((json.dumps(entry, separators=(',', ':')) + '\n').encode())
                else:
                    unique[arm][key] += 1
            assert states['diamond']['archive'] == states['whole']['archive']
            az, ax, *_ = m.evidence(states['whole'], REPORT)
            recon_bad += int(az != DZ or ax != DX)
            ref = dec['thick']
            assert dec['whole']['label'] == ref['label'], (n, 'whole/thick')
            assert max(abs(dec['whole'][p] - ref[p]) for p in ('p0', 'p1')) <= 1e-12
            for arm, d in dec.items():
                t = totals[arm]
                t['hard_agree'] += weight * (d['label'] == ref['label'])
                t['hard_correct'] += weight * (d['label'] == truth)
                t['expected_agree'] += weight * expected_agreement(d, ref)
                t['expected_correct'] += weight * (.5 if d['tie'] else d['label'] == truth)
                t['raw_disagree'] += d['label'] != ref['label']
            if dec['diamond']['label'] != ref['label']:
                share['diamond_right' if dec['diamond']['label'] == truth else 'reference_right'] += 1
                if sample is None or weight > sample['weight']:
                    sample = dict(weight=weight, faults=fts, onset=onset, truth=truth, decisions=dec)
            if n % 20000 == 0:
                print(VARIANT, n, 'conjugate histories', round(time.time() - start, 1), 's', flush=True)
    finally:
        for f in file_handles.values():
            f.close()
    for t in totals.values():
        for field in ('hard_agree', 'hard_correct', 'expected_agree', 'expected_correct',
                      'payload_weighted', 'wire_weighted'):
            t[field] /= weights
    out = dict(variant=VARIANT, site=list(SITE), star=sorted(sc.STAR[SITE]), report=REPORT, config=cfg,
               n_histories=n, total_weight=weights, arms=totals, diamond_disagreements=dict(share),
               example=sample,
               checks=dict(direct_roundtrip_checks=checks, mismatches=0, whole_thick_label_mismatches=0,
                           whole_thick_probabilities_within_1e_12=True,
                           archive_dense_mismatches=recon_bad, archive_arms_identical=True),
               duplicate_contribution_histories=collision_count, elapsed_seconds=time.time() - start,
               query_counts=dict(thick=40, thin=0, diamond=QUERY, whole=24),
               reconstructed_old_values=dict(diamond=QUERY, whole=24),
               note='Conjugate X-open edge (2,1); star {5,6,7} = 2 Z-arms + 1 X-arm; '
                    'diamond query 6 readings. Reuses correction_2026-11-14 model unchanged.')
    for arm in m.ARMS:
        (CACHE / (arm + '-expected.json')).write_text(json.dumps(unique_expected[arm]))
    out['cold_input'] = {a: dict(unique_states=len(unique[a]), histories=sum(unique[a].values()),
                                 sha256=hashlib.sha256((CACHE / (a + '-states.jsonl')).read_bytes()).hexdigest(),
                                 bytes=(CACHE / (a + '-states.jsonl')).stat().st_size) for a in m.ARMS}
    (RESULTS / 'conjugate_E_frame.json').write_text(json.dumps(out, indent=2) + '\n')
    print(VARIANT, 'CONJUGATE COMPLETE', json.dumps({a: t['raw_disagree'] for a, t in totals.items()}), flush=True)
    return out


def cold_worker(arm):
    source = CACHE / (arm + '-states.jsonl')
    dest = CACHE / (arm + '-restored.jsonl')
    with source.open() as inp, dest.open('w') as out:
        for line in inp:
            rec = json.loads(line)
            assert rec['state']['arm'] == arm
            state = m.restore(json.dumps(rec['state']))
            ans = m.decode(state, rec['report'])
            out.write(json.dumps(dict(id=rec['id'], answer=ans)) + '\n')
    print('cold', arm, 'complete', flush=True)


def cold_check():
    results = {}
    for arm in m.ARMS:
        cmd = [sys.executable, str(Path(__file__).resolve()), 'worker', arm]
        start = time.time()
        with (RESULTS / ('cold-' + arm + '.log')).open('w') as log:
            p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
        assert p.returncode == 0, (arm, p.returncode)
        expected = json.loads((CACHE / (arm + '-expected.json')).read_text())
        seen = set()
        delta = 0.
        for line in (CACHE / (arm + '-restored.jsonl')).read_text().splitlines():
            r = json.loads(line)
            key = r['id']
            assert key not in seen
            seen.add(key)
            a = r['answer']
            b = expected[key]
            assert a['label'] == b['label'] and a['tie'] == b['tie']
            delta = max(delta, abs(a['p0'] - b['p0']), abs(a['p1'] - b['p1']))
        assert seen == set(expected) and delta <= 1e-12
        results[arm] = dict(command=cmd, exit_code=p.returncode, unique_states=len(seen),
                            max_probability_difference=delta, elapsed_seconds=time.time() - start)
        print('cold check', arm, len(seen), 'PASS', flush=True)
    (RESULTS / 'cold_restart.json').write_text(json.dumps(results, indent=2) + '\n')


def summarize():
    bulk = json.loads((CORR / 'results' / 'E_frame.json').read_text())
    zopen = json.loads((EDGE12 / 'results' / 'edge_E_frame.json').read_text())
    xopen = json.loads((RESULTS / 'conjugate_E_frame.json').read_text())
    sites = [('bulk (1,1) 2X+2Z', bulk, '1,1', '2Z+2X', 8),
             ('Z-open (1,2) 2X+1Z', zopen, '1,2', '1Z+2X', 6),
             ('X-open (2,1) 1X+2Z', xopen, '2,1', '2Z+1X', 6)]
    rows = []
    for label, d, site, arms, qbulk in sites:
        dia = d['arms']['diamond']
        thin = d['arms']['thin']
        thick = d['arms']['thick']
        rows.append(dict(
            label=label, site=site, star_arms=arms, lip_bits=d['query_counts']['diamond'],
            thin_disagree=thin['raw_disagree'], diamond_disagree=dia['raw_disagree'],
            diamond_agree=round(dia['hard_agree'], 6), diamond_correct=round(dia['hard_correct'], 6),
            thick_correct=round(thick['hard_correct'], 6),
            diamond_split=d['diamond_disagreements'],
            diamond_payload_max=dia['payload_max'], diamond_payload_mean=round(dia['payload_weighted'], 4)))
    comp = dict(baseline_commit='09a79c1', zopen_commit='93cf914', conjugate_protocol='9832cd1',
                logical_sector='X-sector reads Z-stabs; Z-arms=logical readings, X-arms=onset readings',
                three_way=rows, conjugate_example=xopen['example'], conjugate_checks=xopen['checks'],
                cold_restart=json.loads((RESULTS / 'cold_restart.json').read_text())
                if (RESULTS / 'cold_restart.json').exists() else None)
    (RESULTS / 'three_way.json').write_text(json.dumps(comp, indent=2) + '\n')
    print('\n3-WAY diamond disagreements:',
          {r['site']: r['diamond_disagree'] for r in rows})
    return comp


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'worker':
        cold_worker(sys.argv[2])
    elif cmd == 'cold':
        cold_check()
    elif cmd == 'summarize':
        summarize()
    else:
        run()
        cold_check()
        summarize()
