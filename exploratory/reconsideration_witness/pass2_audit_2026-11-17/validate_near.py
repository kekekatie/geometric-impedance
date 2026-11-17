"""Check near-loss weight-two probes and every seam output against the original scan."""
import json
import audit

D=audit.IndexedDecoder(5,(2,2),3,3)
loc,_=audit.pass2.p_loc(D.s)
configs=list(audit.itertools.combinations(loc,2))
indices=audit.np.linspace(0,len(configs)-1,32,dtype=int)
sims=[]; rows=[]
for i in indices:
    for onset,vx,vz in audit.pass2.variants():
        dz,dx,tr,_=D.s.simulate(*audit.nd_run.compose(tuple(configs[i])+tuple(audit.pass2.loss_contribs(onset,vx,vz))))
        sims.append((dz,dx,tr)); rows.append({a:D.direct(dz,dx,a) for a in audit.ARMS})
check=audit.unaccelerated_check(D,sims,rows,set(range(len(sims))))
seams=json.loads((audit.OUT/'seams.json').read_text(encoding='utf-8'))
D._mcache={}
D._marginal_compute=audit.nd_infer.Decoder._marginal_compute.__get__(D)
count=0; maxerr=0.
for pair in seams['pairs']:
    rec=pair['observed_record']
    record={(k,t):rec[k*5+t] for k in range(D.s.NSTAB) for t in range(5)}
    dz={d:v for d,v in record.items() if d[0] in D.s.ZSTABS}
    dx={d:v for d,v in record.items() if d[0] in D.s.XSTABS}
    for a in audit.ARMS:
        ref=D.direct(dz,dx,a); got=pair['members'][0]['decoded'][a]
        err=abs(ref['p0']-got['p0']); maxerr=max(maxerr,err)
        assert ref['label']==got['label'] and ref['tie']==got['tie'] and err<=audit.EPS
        count+=1
audit.save('near_validation.json',dict(weight_two_probes=check,seam_arm_checks=count,seam_max_posterior_error=maxerr))
print(check,count,maxerr)
