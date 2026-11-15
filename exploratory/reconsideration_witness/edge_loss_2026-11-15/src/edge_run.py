"""Distance-3 EDGE-loss run, reusing Astra's corrected E_frame model UNCHANGED.

The only scientific change vs the bulk baseline is the loss site: (1,1) -> (1,2).
Astra's model.py is report-routed, so the edge site enters only through the report
(driving both the diamond query geometry and the erasure hypotheses). Everything
else -- XOR parity, Bernoulli-odds weights, epsilon ties, the report-blind 2-bit
frame, shared-onset inference, the four arms, the site-agnostic archive, cold
fresh-process restart, and the accounting -- is carried forward exactly.

Frozen by PROTOCOL_AMENDMENT_EDGE.md (commit 4509bd6), reusing model at 09a79c1.
Subcommands: run | worker <arm> | cold | summarize
"""
import sys, json, itertools, hashlib, time, subprocess, os, collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
CORR = HERE.parents[0] / 'correction_2026-11-14'
sys.path.insert(0, str(CORR / 'src'))
import model as m                      # Astra's corrected model, unchanged
from model import frozen as sc

RESULTS = HERE / 'results'
RESULTS.mkdir(exist_ok=True)
CACHE = Path(os.environ.get('EDGE_CACHE', str(HERE / 'runtime'))).resolve()
CACHE.mkdir(parents=True, exist_ok=True)

VARIANT = 'E_frame'
EDGE_SITE = (1, 2)
EDGE_REPORT = {'site': [1, 2], 'onsets': [1, 2], 'deadline': 4}
# edge star {2,3,6}: Z-stab 2 (X-sector) + X-stabs 3,6 (Z-sector); query = 3 checks x 2 onsets = 6
EDGE_QUERY = len([(k, t) for k in sc.STAR[EDGE_SITE] for t in EDGE_REPORT['onsets']])


def histories():
    pool = [(tag, q, t) for q in sc.DATA for t in range(5) for tag in ('X', 'Z')]
    pool += [('MZ', k, t) for k in sc.ZSTABS for t in range(5)]
    pool += [('MX', k, t) for k in sc.XSTABS for t in range(5)]
    for w in range(3):
        for extra in itertools.combinations(pool, w):
            for onset in (1, 2):
                for vx in (0, 1):
                    for vz in (0, 1):
                        loss = ([('X', EDGE_SITE, onset)] if vx else []) + \
                               ([('Z', EDGE_SITE, onset)] if vz else [])
                        yield w, tuple(extra) + tuple(loss), onset


def state_of(record, arm):
    state = m.prepare_before_report({d: v for d, v in record.items() if d[1] <= 3},
                                    arm, VARIANT)
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
    totals = {a: dict(hard_agree=0., hard_correct=0., expected_agree=0.,
                      expected_correct=0., raw_disagree=0, ties=0,
                      payload_weighted=0., payload_max=0, wire_weighted=0., wire_max=0)
              for a in m.ARMS}
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
                actual = m.decode(restored, EDGE_REPORT)
                direct = m.direct(DZ, DX, arm, EDGE_REPORT, VARIANT)
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
                    entry = dict(id=key, state=restored, report=EDGE_REPORT)
                    file_handles[arm].write((json.dumps(entry, separators=(',', ':')) + '\n').encode())
                else:
                    unique[arm][key] += 1
            assert states['diamond']['archive'] == states['whole']['archive']
            az, ax, *_ = m.evidence(states['whole'], EDGE_REPORT)
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
                print(VARIANT, n, 'edge histories', round(time.time() - start, 1), 's', flush=True)
    finally:
        for f in file_handles.values():
            f.close()
    for t in totals.values():
        for field in ('hard_agree', 'hard_correct', 'expected_agree', 'expected_correct',
                      'payload_weighted', 'wire_weighted'):
            t[field] /= weights
    out = dict(variant=VARIANT, site=list(EDGE_SITE), star=sorted(sc.STAR[EDGE_SITE]),
               report=EDGE_REPORT, config=cfg, n_histories=n, total_weight=weights,
               arms=totals, diamond_disagreements=dict(share), example=sample,
               checks=dict(direct_roundtrip_checks=checks, mismatches=0,
                           whole_thick_label_mismatches=0,
                           whole_thick_probabilities_within_1e_12=True,
                           archive_dense_mismatches=recon_bad, archive_arms_identical=True),
               duplicate_contribution_histories=collision_count,
               elapsed_seconds=time.time() - start,
               query_counts=dict(thick=40, thin=0, diamond=EDGE_QUERY, whole=24),
               reconstructed_old_values=dict(diamond=EDGE_QUERY, whole=24),
               note='Edge site (1,2); star {2,3,6}; diamond query 6 readings. '
                    'Reuses correction_2026-11-14 model unchanged. Payload maxima are '
                    'deadline snapshots, not temporal peaks.')
    for arm in m.ARMS:
        (CACHE / (arm + '-expected.json')).write_text(json.dumps(unique_expected[arm]))
    out['cold_input'] = {a: dict(unique_states=len(unique[a]), histories=sum(unique[a].values()),
                                 sha256=hashlib.sha256((CACHE / (a + '-states.jsonl')).read_bytes()).hexdigest(),
                                 bytes=(CACHE / (a + '-states.jsonl')).stat().st_size) for a in m.ARMS}
    (RESULTS / 'edge_E_frame.json').write_text(json.dumps(out, indent=2) + '\n')
    print(VARIANT, 'EDGE COMPLETE', json.dumps({a: t['raw_disagree'] for a, t in totals.items()}), flush=True)
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
    edge = json.loads((RESULTS / 'edge_E_frame.json').read_text())
    bulk = json.loads((CORR / 'results' / 'E_frame.json').read_text())
    rows = []
    for a in m.ARMS:
        e, b = edge['arms'][a], bulk['arms'][a]
        rows.append(dict(arm=a,
                         bulk_raw_disagree=b['raw_disagree'], edge_raw_disagree=e['raw_disagree'],
                         bulk_agree=round(b['hard_agree'], 6), edge_agree=round(e['hard_agree'], 6),
                         bulk_correct=round(b['hard_correct'], 6), edge_correct=round(e['hard_correct'], 6),
                         bulk_payload_max=b['payload_max'], edge_payload_max=e['payload_max'],
                         bulk_payload_mean=round(b['payload_weighted'], 4), edge_payload_mean=round(e['payload_weighted'], 4),
                         bulk_wire_max=b['wire_max'], edge_wire_max=e['wire_max']))
    comp = dict(bulk_commit='09a79c1', edge_protocol_commit='4509bd6',
                bulk_site=[1, 1], edge_site=[1, 2],
                bulk_query=bulk['query_counts']['diamond'], edge_query=edge['query_counts']['diamond'],
                bulk_diamond_split=bulk['diamond_disagreements'],
                edge_diamond_split=edge['diamond_disagreements'],
                table=rows, edge_checks=edge['checks'],
                cold_restart=json.loads((RESULTS / 'cold_restart.json').read_text())
                if (RESULTS / 'cold_restart.json').exists() else None,
                edge_example=edge['example'])
    (RESULTS / 'bulk_vs_edge.json').write_text(json.dumps(comp, indent=2) + '\n')
    print(json.dumps({r['arm']: dict(bulk=r['bulk_raw_disagree'], edge=r['edge_raw_disagree']) for r in rows}))
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
