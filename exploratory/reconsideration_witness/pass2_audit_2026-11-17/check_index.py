"""Verify matching-dtype search and replay baseline after the performance-only fix."""
import json
import audit

keys=audit.np.array([0,1,2**31,2**35,2**36-1],dtype=audit.np.uint64)
for k in (0,1,2,2**31,2**35,2**36-2,2**36-1):
    for side in ('left','right'):
        assert audit.np.searchsorted(keys,k,side)==audit.np.searchsorted(keys,audit.np.uint64(k),side)
base=json.loads((audit.OUT/'cap_33.json').read_text(encoding='utf-8'))['rows']
sims,tags=audit.panel()
D=audit.IndexedDecoder(5,(2,2),3,3)
maxerr=0.; count=0
for i,(dz,dx,truth) in enumerate(sims):
    for arm in audit.ARMS:
        ref=base[i][arm]; got=D.direct(dz,dx,arm)
        err=abs(ref['p0']-got['p0']); maxerr=max(maxerr,err)
        assert ref['label']==got['label'] and ref['tie']==got['tie'] and err<=audit.EPS
        count+=1
audit.save('index_validation.json',dict(arm_checks=count,max_posterior_error=maxerr,search_boundary_checks=14))
print(count,maxerr)
