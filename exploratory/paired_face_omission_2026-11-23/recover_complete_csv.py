"""Recover a completed enumeration rejected only by strict float-string equality.

Verify every row and rerun deterministic direct/full-scan and configuration checks;
do not infer validation counters from the failed process.
"""
import argparse,csv,gzip,hashlib,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('paired_face_replay',ROOT/'replay.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
E=P.E
def recover(site):
    start=time.time();name=site['name'];assert name in ('AB_bal','Penrose_ear')
    with gzip.open(P.R/(name+'.csv.gz'),'rt',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==48206
    code=E.CorrectedPatchCode(P.prepare.patch_path(name));D=E.Indexed(code,site['qubit']);qs={a:site['arms'][a]['indices'] for a in ('AB','A','B','0')}
    assert D.star==qs['AB'] and set(qs['0'])<=set(D.s.XSTABS) and len(qs['0'])==2
    credit={a:[0.,0.,0.] for a in P.NAMES};counts=[0,0,0];h=hashlib.sha256()
    checks=dict(new_arm_fullscan_checks=0,new_arm_mismatches=0,max_posterior_difference=0.,baseline_configuration_checks=0,
                baseline_configuration_mismatches=0,coordinate_assertions=0,recovery_joint_configuration_checks=0)
    n=0
    for cid,k,extra in E.prior.config_stream(E.prior.ordinary_pool(code)):
        row=rows[cid];assert int(row['config_id'])==cid and int(row['ordinary_weight'])==k
        h.update((json.dumps([cid,k,extra],separators=(',',':'))+'\n').encode());counts[k]+=8
        for a in P.NAMES:
            c=float(row[a]);assert 0<=c<=8 and c*2==int(c*2);credit[a][k]+=c
        sample=cid%251==0;acc={a:0. for a in P.NAMES}
        for onset,vx,vz in E.prior.VARIANTS:
            n+=1
            if not sample and n%2003:continue
            loss=([('X',site['qubit'],onset)] if vx else [])+([('Z',site['qubit'],onset)] if vz else [])
            dz,dx,truth,_=code.simulate(*E.prior.nd_run.compose(extra+tuple(loss)))
            state=D.serialize(dz,dx,'diamond');stored=E.unpack(D,state);new=E.query(D,stored,qs['0'])
            if sample:
                ds={'thin':E.query(D,stored,[]),'thick':D.direct(dz,dx,'thick'),'0':new}
                ds.update({a:E.query(D,stored,qs[a]) for a in ('AB','A','B')})
                for a,dec in ds.items():acc[a]+=E.prior.cred(dec,truth)
            if n%2003==0:
                evidence=E.direct_evidence(D,dz,dx,qs['0']);obs={**evidence[0],**evidence[1]}
                assert {d for d in obs if d[1]<3}=={(i,t) for i in qs['0'] for t in (1,2)}
                assert len(evidence[2])+len(evidence[3])==D.NST and evidence[4]==state['frame'];checks['coordinate_assertions']+=1
                method,cache=D._marginal_compute,D._mcache;D._marginal_compute=E.Original._marginal_compute.__get__(D);D._mcache={}
                try:rr=D.decide(*evidence)
                finally:D._marginal_compute,D._mcache=method,cache
                checks['new_arm_fullscan_checks']+=1;checks['new_arm_mismatches']+=not E.same(rr,new)
                checks['max_posterior_difference']=max(checks['max_posterior_difference'],abs(rr['p0']-new['p0']),abs(rr['p1']-new['p1']))
        if sample:
            for a in P.NAMES:
                assert acc[a]==float(row[a]),(name,cid,a,acc[a],row[a])
                if a=='0':checks['recovery_joint_configuration_checks']+=1
                else:checks['baseline_configuration_checks']+=1
    reference=json.loads((P.ROLE/'results'/(name+'_omission.json')).read_text())
    assert counts==[8,2480,383160] and n==385648 and h.hexdigest()==reference['config_stream_sha256']
    assert checks['new_arm_fullscan_checks']==192 and checks['new_arm_mismatches']==0
    P.finish(site,credit,counts,h.hexdigest(),checks,reference,None,time.time()-start,recovered=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--site',required=True,choices=['AB_bal','Penrose_ear']);args=ap.parse_args()
    site=next(s for s in json.loads((P.R/'arms.json').read_text())['sites'] if s['name']==args.site);recover(site)
