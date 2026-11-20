"""Paired exhaustive leave-one-check-out replay. Omitted observations stay absent."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import time
import prepare
from prepare import ROOT, audit
E=audit.engine
RESULTS=ROOT/'results'
METRICS=('credit','gained','lost','labels','ties')

def direct_evidence(D,dz,dx,indices):
    """Independent full-record restriction: no archive reconstruction and no zero fill."""
    selected={(k,t) for k in range(D.NST) for t in (3,4)}|{(k,t) for k in indices for t in (1,2)}
    az={d:v for d,v in dz.items() if d in selected}; ax={d:v for d,v in dx.items() if d in selected}
    bz={k:dz[k,0]^dz[k,1]^dz[k,2] for k in D.s.ZSTABS}
    bx={k:dx[k,0]^dx[k,1]^dx[k,2] for k in D.s.XSTABS}
    assert set(az)|set(ax)==selected
    return az,ax,bz,bx,D.observed_frames(dz,dx)

def preflight(D,site):
    """Complete the deterministic missing-data check before accumulating any credits."""
    checked=0;zeros=0;n=0;max_error=0.
    for _,_,extra in E.prior.config_stream(E.prior.ordinary_pool(D.s)):
        for onset,vx,vz in E.prior.VARIANTS:
            n+=1
            if n%2003:continue
            loss=([('X',site['qubit'],onset)] if vx else [])+([('Z',site['qubit'],onset)] if vz else [])
            dz,dx,_,_=D.s.simulate(*E.prior.nd_run.compose(extra+tuple(loss)))
            stored=E.unpack(D,D.serialize(dz,dx,'diamond'))
            expected={a['omitted']:E.query(D,stored,a['retained_indices']) for a in site['arms']}
            method,cache=D._marginal_compute,D._mcache
            D._marginal_compute=E.Original._marginal_compute.__get__(D);D._mcache={}
            try:
                for a in site['arms']:
                    evidence=direct_evidence(D,dz,dx,a['retained_indices'])
                    observed={**evidence[0],**evidence[1]};early={d for d in observed if d[1]<3}
                    assert early=={tuple(x) for x in a['numeric_coordinates']}
                    assert all((a['index'],t) not in observed for t in (0,1,2))
                    zeros+=sum(observed[d]==0 for d in early)
                    rr=D.decide(*evidence);assert E.same(rr,expected[a['omitted']])
                    max_error=max(max_error,abs(rr['p0']-expected[a['omitted']]['p0']));checked+=1
            finally:D._marginal_compute,D._mcache=method,cache
    assert checked==768 and zeros>0
    print('PREFLIGHT PASS',site['patch'],checked,'omission comparisons',flush=True)
    return dict(comparisons=checked,mismatches=0,known_zero_readings=zeros,max_posterior_error=max_error)

def replay(site,resume=False):
    name=f"{site['patch']}_e{site['edge']}";dest=RESULTS/(name+'.json')
    if resume and dest.exists():
        old=json.loads(dest.read_text());assert old['site']==site and old['histories']==385648
        print(name,'completed checkpoint retained',flush=True);return
    start=time.time();code=audit.CorrectedPatchCode(audit.SOURCE/(site['patch']+'.json'))
    D=E.Indexed(code,site['qubit']);assert D.star==site['intact_indices']
    geom=next(e for e in code.json['eligible'] if e['edge']==site['edge'])
    for a in site['arms']:
        expected={tuple(x) for x in geom['query']}-{(a['omitted'],1),(a['omitted'],2)}
        assert {tuple(x) for x in a['retained_coordinates']}==expected
        assert a['numeric_coordinates']==[[audit.check_index(c,len(code.json['HX']),len(code.json['HZ'])),t] for c,t in a['retained_coordinates']]
        assert set(a['retained_indices'])==set(D.star)-{a['index']} and len(expected)==6
    before_scoring=preflight(D,site)
    names=['thin','intact','thick','whole']+[a['omitted'] for a in site['arms']]
    credits={a:[0.,0.,0.] for a in names};ties={a:[0,0,0] for a in names};counts=[0,0,0]
    movements={a['omitted']:{m:[0.,0.,0.] for m in METRICS[1:]} for a in site['arms']}
    checks=dict(whole_mismatches=0,json_roundtrips=0,direct_fullscan_checks=0,direct_fullscan_mismatches=0,
        max_posterior_difference=0.,omission_coordinate_checks=0,retained_zero_readings_checked=0)
    fields=['config_id','ordinary_weight']+[a+'_credit' for a in names]+[a['omitted']+'_'+m for a in site['arms'] for m in METRICS[1:]]
    h=hashlib.sha256();pool=E.prior.ordinary_pool(code);assert len(pool)==310
    with (RESULTS/(name+'.csv.gz')).open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();n=0
        for cid,k,extra in E.prior.config_stream(pool):
            h.update((json.dumps([cid,k,extra],separators=(',',':'))+'\n').encode())
            row={c:0. for c in fields};row.update(config_id=cid,ordinary_weight=k)
            for onset,vx,vz in E.prior.VARIANTS:
                loss=([('X',site['qubit'],onset)] if vx else [])+([('Z',site['qubit'],onset)] if vz else [])
                dz,dx,truth,_=code.simulate(*E.prior.nd_run.compose(extra+tuple(loss)))
                state=D.serialize(dz,dx,'diamond');stored=E.unpack(D,state)
                dec=dict(thin=E.query(D,stored,[]),intact=E.query(D,stored,D.star),thick=D.direct(dz,dx,'thick'),whole=E.query(D,stored,[],whole=True))
                for a in site['arms']:dec[a['omitted']]=E.query(D,stored,a['retained_indices'])
                checks['whole_mismatches']+=not E.same(dec['whole'],dec['thick'])
                c={a:E.prior.cred(dec[a],truth) for a in names}
                for a in names:
                    credits[a][k]+=c[a];ties[a][k]+=dec[a]['tie'];row[a+'_credit']+=c[a]
                for arm in site['arms']:
                    a=arm['omitted'];delta=c[a]-c['intact']
                    measures=dict(gained=max(delta,0),lost=max(-delta,0),labels=int(dec[a]['label']!=dec['intact']['label']),ties=int(dec[a]['tie']!=dec['intact']['tie']))
                    for m,v in measures.items():movements[a][m][k]+=v;row[a+'_'+m]+=v
                counts[k]+=1;n+=1
                if n%2003==0:
                    restored=json.loads(json.dumps(state));assert restored==state;checks['json_roundtrips']+=1
                    method,cache=D._marginal_compute,D._mcache
                    D._marginal_compute=E.Original._marginal_compute.__get__(D);D._mcache={}
                    try:
                        for a in names:
                            if a in ('thick','whole'):rr=D.direct(dz,dx,a)
                            else:
                                arm=next((x for x in site['arms'] if x['omitted']==a),None)
                                indices=[] if a=='thin' else D.star if a=='intact' else arm['retained_indices']
                                evidence=direct_evidence(D,dz,dx,indices)
                                if arm:
                                    observed={**evidence[0],**evidence[1]}
                                    early={d for d in observed if d[1]<3}
                                    assert early=={tuple(x) for x in arm['numeric_coordinates']}
                                    assert all((arm['index'],t) not in observed for t in (0,1,2))
                                    bnd={**evidence[2],**evidence[3]};assert arm['index'] in bnd
                                    assert evidence[4]==state['frame']
                                    checks['omission_coordinate_checks']+=1
                                    checks['retained_zero_readings_checked']+=sum(observed[d]==0 for d in early)
                                rr=D.decide(*evidence)
                            checks['direct_fullscan_checks']+=1
                            checks['direct_fullscan_mismatches']+=not E.same(rr,dec[a])
                            checks['max_posterior_difference']=max(checks['max_posterior_difference'],abs(rr['p0']-dec[a]['p0']))
                    finally:D._marginal_compute,D._mcache=method,cache
            writer.writerow(row)
            if len(D._mcache)>500000:D._mcache.clear()
            if cid%10000==0:print(name,cid,n,round(time.time()-start,1),flush=True)
    assert n==385648 and counts==[8,2480,383160]
    assert checks['whole_mismatches']==checks['direct_fullscan_mismatches']==0
    weights=[E.prior.ODDS**k for k in range(3)];mass=sum(c*w for c,w in zip(counts,weights))
    mean=lambda arr:sum(c*w for c,w in zip(arr,weights))/mass
    scores={a:dict(truth_credit=mean(credits[a]),credits_by_weight=credits[a],ties_by_weight=ties[a]) for a in names}
    baseline=json.loads((ROOT.parent/'fresh_site_address_audit_2026-11-20/results'/(name+'.json')).read_text())
    for a,b in [('thin','thin'),('intact','corrected_diamond'),('thick','thick'),('whole','whole')]:
        assert credits[a]==baseline['scores'][b]['credits_by_weight'] and ties[a]==baseline['scores'][b]['ties_by_weight']
    table=[]
    for arm in site['arms']:
        a=arm['omitted'];mm=movements[a];cost=100*(scores['intact']['truth_credit']-scores[a]['truth_credit'])
        gained,lost=100*mean(mm['gained']),100*mean(mm['lost'])
        assert abs(cost-(lost-gained))<1e-11
        table.append(dict(**arm,cost_pp=cost,gain_over_thin_pp=100*(scores[a]['truth_credit']-scores['thin']['truth_credit']),
            full_archive_gain_pp=100*(scores['thick']['truth_credit']-scores['thin']['truth_credit']),
            intact_gain_pp=100*(scores['intact']['truth_credit']-scores['thin']['truth_credit']),
            truth_gained_pp=gained,truth_lost_pp=lost,label_changes=int(sum(mm['labels'])),tie_status_changes=int(sum(mm['ties'])),
            label_changes_weighted_percent=100*mean(mm['labels']),tie_changes_weighted_percent=100*mean(mm['ties']),movements_by_weight=mm))
    out=dict(site=site,decoder_caps=[3,3],p=E.prior.P,histories=n,histories_by_weight=counts,configurations=cid+1,
        config_stream_sha256=h.hexdigest(),scores=scores,omissions=table,preflight=before_scoring,validation=checks,elapsed_seconds=time.time()-start)
    temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(out,indent=2)+'\n');temp.replace(dest)
    print('COMPLETE',name,[(x['omitted'],x['cost_pp']) for x in table],flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--patch',choices=[x[0] for x in prepare.SITES]);p.add_argument('--resume',action='store_true');args=p.parse_args()
    plan=json.loads((RESULTS/'arms.json').read_text())
    for site in plan['sites']:
        if not args.patch or site['patch']==args.patch:replay(site,args.resume)
    if not args.patch:
        # Imported ancestor scripts alter sys.path; bind this experiment's report explicitly.
        import importlib.util
        spec=importlib.util.spec_from_file_location('omission_report',ROOT/'report.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.main()
if __name__=='__main__':main()
