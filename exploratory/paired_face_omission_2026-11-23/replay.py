"""Only G_0 is a new intervention; retain or replay the sealed paired baselines."""
import argparse,csv,gzip,hashlib,importlib.util,io,json,time
from pathlib import Path
import prepare
from prepare import E,ROOT,ROLE
R=ROOT/'results';NAMES=['thin','thick','AB','A','B','0']

def sealed_rows(site):
    name=f"{site['name']}_e{site['edge']}"
    manifest=json.loads((ROOT/'inputs/manifest.json').read_text())
    for x in manifest:
        if name not in x['local']:continue
        assert hashlib.sha256((ROOT/x['local']).read_bytes()).hexdigest()==x['sha256']
    data=json.loads((ROOT/'inputs'/(name+'.json')).read_text())
    mapping={'thin':'thin','thick':'thick','AB':'intact','A':site['B'],'B':site['A']}
    totals={a:[0.,0.,0.] for a in mapping};rows=[];counts=[0,0,0]
    with gzip.open(ROOT/'inputs'/(name+'.csv.gz'),'rt',newline='') as f:
        for i,row in enumerate(csv.DictReader(f)):
            assert int(row['config_id'])==i
            k=int(row['ordinary_weight']);counts[k]+=8
            small={a:float(row[b+'_credit']) for a,b in mapping.items()};small['k']=k;rows.append(small)
            for a in mapping:totals[a][k]+=small[a]
    assert len(rows)==48206 and counts==[8,2480,383160]
    for a,b in mapping.items():assert totals[a]==data['scores'][b]['credits_by_weight']
    return rows,data,mapping

def replay(site,resume=False):
    name=site['name'];dest=R/(name+'.json')
    if resume and dest.exists():
        d=json.loads(dest.read_text());assert d['site']==site and d['histories']==385648
        print(name,'completed checkpoint retained',flush=True);return
    start=time.time();code=E.CorrectedPatchCode(prepare.patch_path(name));D=E.Indexed(code,site['qubit'])
    assert D.star==site['arms']['AB']['indices'] and hashlib.sha256(prepare.patch_path(name).read_text().encode()).hexdigest()==site['patch_lf_sha256']
    qs={a:site['arms'][a]['indices'] for a in ('AB','A','B','0')}
    assert len(qs['0'])==2 and all(i in D.s.XSTABS for i in qs['0'])
    cached=name not in E.TARGETS
    rows,reference,mapping=sealed_rows(site) if cached else (None,json.loads((ROLE/'results'/(name+'_omission.json')).read_text()),None)
    credits={a:[0.,0.,0.] for a in NAMES};counts=[0,0,0]
    checks=dict(new_arm_fullscan_checks=0,new_arm_mismatches=0,max_posterior_difference=0.,
        baseline_configuration_checks=0,baseline_configuration_mismatches=0,coordinate_assertions=0)
    h=hashlib.sha256();pool=E.prior.ordinary_pool(code);assert len(pool)==310
    with (R/(name+'.csv.gz')).open('wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf-8',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['config_id','ordinary_weight']+NAMES);n=0
        for cid,k,extra in E.prior.config_stream(pool):
            h.update((json.dumps([cid,k,extra],separators=(',',':'))+'\n').encode())
            acc={a:0. for a in NAMES};sample_baseline=cached and cid%251==0
            if cached:
                assert rows[cid]['k']==k
                for a in NAMES[:-1]:acc[a]=rows[cid][a]
            checked={a:0. for a in NAMES[:-1]}
            for onset,vx,vz in E.prior.VARIANTS:
                loss=([('X',site['qubit'],onset)] if vx else [])+([('Z',site['qubit'],onset)] if vz else [])
                dz,dx,truth,_=code.simulate(*E.prior.nd_run.compose(extra+tuple(loss)))
                state=D.serialize(dz,dx,'diamond');stored=E.unpack(D,state)
                new=E.query(D,stored,qs['0']);acc['0']+=E.prior.cred(new,truth)
                if not cached or sample_baseline:
                    dec={'thin':E.query(D,stored,[]),'thick':D.direct(dz,dx,'thick')}
                    dec.update({a:E.query(D,stored,qs[a]) for a in ('AB','A','B')})
                    for a in dec:
                        c=E.prior.cred(dec[a],truth)
                        if cached:checked[a]+=c
                        else:acc[a]+=c
                counts[k]+=1;n+=1
                if n%2003==0:
                    evidence=E.direct_evidence(D,dz,dx,qs['0']);observed={**evidence[0],**evidence[1]}
                    early={d for d in observed if d[1]<3};assert early=={(i,t) for i in qs['0'] for t in (1,2)}
                    assert len(early)==4 and all(i not in D.s.ZSTABS for i,t in early)
                    assert len(evidence[2])+len(evidence[3])==D.NST and evidence[4]==state['frame']
                    checks['coordinate_assertions']+=1
                    method,cache=D._marginal_compute,D._mcache;D._marginal_compute=E.Original._marginal_compute.__get__(D);D._mcache={}
                    try:rr=D.decide(*evidence)
                    finally:D._marginal_compute,D._mcache=method,cache
                    checks['new_arm_fullscan_checks']+=1;checks['new_arm_mismatches']+=not E.same(rr,new)
                    checks['max_posterior_difference']=max(checks['max_posterior_difference'],abs(rr['p0']-new['p0']),abs(rr['p1']-new['p1']))
            if sample_baseline:
                for a in checked:
                    checks['baseline_configuration_checks']+=1
                    checks['baseline_configuration_mismatches']+=checked[a]!=acc[a]
            for a in NAMES:credits[a][k]+=acc[a]
            writer.writerow([cid,k]+[acc[a] for a in NAMES])
            if len(D._mcache)>500000:D._mcache.clear()
            if cid%10000==0:print(name,cid,n,round(time.time()-start,1),flush=True)
    assert n==385648 and counts==[8,2480,383160]
    assert checks['new_arm_fullscan_checks']==192 and checks['new_arm_mismatches']==checks['baseline_configuration_mismatches']==0
    assert h.hexdigest()==reference['config_stream_sha256']
    finish(site,credits,counts,h.hexdigest(),checks,reference,mapping,time.time()-start)

def finish(site,credits,counts,stream_hash,checks,reference,mapping,elapsed,recovered=False):
    name=site['name'];dest=R/(name+'.json');cached=name not in E.TARGETS
    weights=[E.prior.ODDS**k for k in range(3)];mass=sum(c*w for c,w in zip(counts,weights))
    scores={a:sum(c*w for c,w in zip(credits[a],weights))/mass for a in NAMES}
    gains={a:100*(scores[a]-scores['thin']) for a in NAMES}
    precision=None
    if cached:
        for a,b in mapping.items():assert credits[a]==reference['scores'][b]['credits_by_weight'] and scores[a]==reference['scores'][b]['truth_credit']
        baseline_equality='exact sealed credit totals and binary-float scores; sampled per-config replay'
    else:
        spec=importlib.util.spec_from_file_location('paired_face_precision',ROOT/'baseline_precision.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        precision=m.verify(credits,counts,gains,reference,site)
        baseline_equality='same exact weighted half-credit score; last-bit float differences disclosed'
    AB,A,B,Z=(gains[a] for a in ('AB','A','B','0'))
    costs=dict(A_loss_B_present=AB-B,A_loss_B_absent=A-Z,B_loss_A_present=AB-A,B_loss_A_absent=B-Z,I=A+B-AB-Z)
    out=dict(site=site,histories=sum(counts),counts=counts,configurations=48206,config_stream_sha256=stream_hash,credits=credits,
        scores=scores,gains_pp=gains,recovered_percent={a:100*gains[a]/gains['thick'] for a in ('AB','A','B','0')},
        costs_pp=costs,validation=checks,baseline_equality=baseline_equality,baseline_precision=precision,
        recovered_complete_csv=recovered,elapsed_seconds=elapsed)
    tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(dest)
    print('COMPLETE',name,json.dumps(dict(G0=gains['0'],percent=out['recovered_percent']['0'],I=costs['I'])),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--site',choices=[x[0] for x in prepare.CONFIG]);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    if not args.site:
        spec=importlib.util.spec_from_file_location('paired_face_geometry_audit',ROOT/'geometry_audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main()
    for site in json.loads((R/'arms.json').read_text())['sites']:
        if not args.site or site['name']==args.site:replay(site,args.resume)
    if not args.site:
        spec=importlib.util.spec_from_file_location('paired_face_report',ROOT/'report.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main()
if __name__=='__main__':main()
