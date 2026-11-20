"""Replay all affected sites; --patch selects an independent resumable patch job."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import time
from pathlib import Path
import audit
from audit import engine as E

ROOT = Path(__file__).resolve().parent
ARMS = ('thin', 'thick', 'whole', 'legacy_diamond', 'corrected_diamond')

def replay(code, site, resume=False):
    name = f"{site['patch']}_e{site['edge']}"
    dest = ROOT / 'results' / (name + '.json')
    if resume and dest.exists():
        old = json.loads(dest.read_text())
        assert old['histories'] == 385648 and old['queries'] == site
        print(name, 'verified checkpoint present', flush=True)
        return
    start = time.time()
    D = E.Indexed(code, site['qubit'])
    assert D.star == site['corrected_indices']
    counts = [0, 0, 0]
    credits = {a: [0., 0., 0.] for a in ARMS}
    ties = {a: [0, 0, 0] for a in ARMS}
    checks = dict(whole_mismatches=0, round0_comparisons=0, round0_mismatches=0,
                  json_roundtrips=0, direct_checks=0, direct_mismatches=0,
                  fullscan_checks=0, fullscan_mismatches=0, max_fullscan_posterior_error=0.,
                  changed_labels=0, changed_ties=0, changed_truth_credit=0)
    cfg_hash = hashlib.sha256()
    pool = E.prior.ordinary_pool(code)
    assert len(pool) == 310
    # Deterministic gzip metadata; CSV records exact half-credit sums over eight variants.
    csv_path = ROOT / 'results' / (name + '.csv.gz')
    with csv_path.open('wb') as raw, gzip.GzipFile(filename='', mode='wb',fileobj=raw,mtime=0) as gz, io.TextIOWrapper(gz,encoding='utf-8',newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(['config_id','ordinary_weight'] + list(ARMS))
        n = 0
        for cid, k, extra in E.prior.config_stream(pool):
            cfg_hash.update((json.dumps([cid,k,extra],separators=(',',':'))+'\n').encode())
            acc = {a: 0. for a in ARMS}
            for onset, vx, vz in E.prior.VARIANTS:
                loss = ([('X',site['qubit'],onset)] if vx else []) + ([('Z',site['qubit'],onset)] if vz else [])
                dz, dx, truth, _ = code.simulate(*E.prior.nd_run.compose(extra+tuple(loss)))
                state = D.serialize(dz, dx, 'diamond')
                stored = E.unpack(D,state)
                dec = dict(thin=E.query(D,stored,[]), thick=D.direct(dz,dx,'thick'), whole=E.query(D,stored,[],whole=True),
                           legacy_diamond=E.query(D,stored,site['legacy_indices']), corrected_diamond=E.query(D,stored,D.star))
                checks['whole_mismatches'] += not E.same(dec['whole'],dec['thick'])
                r0 = E.query(D,stored,D.star,r0=True)
                checks['round0_comparisons'] += 1
                checks['round0_mismatches'] += not E.same(r0,dec['corrected_diamond'])
                before, after = dec['legacy_diamond'], dec['corrected_diamond']
                checks['changed_labels'] += before['label'] != after['label']
                checks['changed_ties'] += before['tie'] != after['tie']
                checks['changed_truth_credit'] += E.prior.cred(before,truth) != E.prior.cred(after,truth)
                for a in ARMS:
                    c = E.prior.cred(dec[a],truth)
                    acc[a] += c; credits[a][k] += c; ties[a][k] += dec[a]['tie']
                counts[k] += 1; n += 1
                if n % 2003 == 0:
                    st2 = json.loads(json.dumps(state)); assert st2 == state
                    checks['json_roundtrips'] += 1
                    for a, direct in [('thin','thin'),('whole','whole'),('corrected_diamond','diamond')]:
                        checks['direct_checks'] += 1
                        checks['direct_mismatches'] += not E.same(D.direct(dz,dx,direct),dec[a])
                    method, cache = D._marginal_compute, D._mcache
                    D._mcache = {}; D._marginal_compute = E.Original._marginal_compute.__get__(D)
                    try:
                        stored2 = E.unpack(D,st2)
                        for a in ARMS:
                            rr = D.direct(dz,dx,'thick') if a == 'thick' else E.query(D,stored2,
                                site['legacy_indices'] if a == 'legacy_diamond' else D.star if a == 'corrected_diamond' else [],whole=a=='whole')
                            checks['fullscan_checks'] += 1
                            checks['fullscan_mismatches'] += not E.same(rr,dec[a])
                            checks['max_fullscan_posterior_error'] = max(checks['max_fullscan_posterior_error'],abs(rr['p0']-dec[a]['p0']))
                    finally:
                        D._marginal_compute, D._mcache = method, cache
            writer.writerow([cid,k]+[acc[a] for a in ARMS])
            if len(D._mcache) > 500000: D._mcache.clear()
            if cid % 10000 == 0: print(name,cid,n,round(time.time()-start,1),flush=True)
    assert n == 385648 and counts == [8,2480,383160]
    assert all(checks[k] == 0 for k in ('whole_mismatches','round0_mismatches','direct_mismatches','fullscan_mismatches'))
    weights = [E.prior.ODDS**k for k in range(3)]
    mass = sum(c*w for c,w in zip(counts,weights))
    scores = {a: sum(c*w for c,w in zip(credits[a],weights))/mass for a in ARMS}
    table = {a:dict(truth_credit=scores[a],credits_by_weight=credits[a],ties_by_weight=ties[a],
                   gain_over_thin_pp=100*(scores[a]-scores['thin']),remaining_thick_gap_pp=100*(scores['thick']-scores[a])) for a in ARMS}
    original = json.loads((audit.SOURCE/'paired_results.json').read_text())['edges'][name]
    reproduced = dict(G_thick_thin=round(table['thick']['gain_over_thin_pp'],5),diamond_thin=round(table['legacy_diamond']['gain_over_thin_pp'],5),thick_diamond=round(table['legacy_diamond']['remaining_thick_gap_pp'],5))
    assert all(reproduced[k] == original[k] for k in reproduced), (name,reproduced,original)
    if name == 'Penrose_1_e14':
        prior = json.loads((ROOT.parent/'penrose_e14_route_check_2026-11-20/results/scores.json').read_text())
        assert table['corrected_diamond']['credits_by_weight'] == prior['scores']['incident_diamond']['credit_by_fault_weight']
    result = dict(queries=site, decoder_caps=[3,3],p=E.prior.P,scored_logical_Z=code.json['logical_Z'],histories=n,
                  histories_by_weight=counts,configurations=cid+1,config_stream_sha256=cfg_hash.hexdigest(),
                  scores=table,validation=checks,reproduced_original=reproduced,elapsed_seconds=time.time()-start)
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print('COMPLETE',name,json.dumps(table['corrected_diamond']),flush=True)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--patch',choices=['AB_1','Penrose_1','Penrose_2'])
    parser.add_argument('--resume',action='store_true',help='Skip completed site checkpoints; default reruns them.')
    args=parser.parse_args()
    sites=json.loads((ROOT/'results/address_audit.json').read_text())['sites']
    for patch in ('AB_1','Penrose_1','Penrose_2'):
        if args.patch and args.patch != patch: continue
        code=audit.CorrectedPatchCode(audit.SOURCE/(patch+'.json'))
        for site in sites:
            if site['patch'] == patch and site['affected']: replay(code,site,args.resume)
    if not args.patch:
        import report
        report.main()

if __name__ == '__main__': main()
