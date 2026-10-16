"""Recheck numerical geometry ingredients and Git registration chronology."""
import json, math, subprocess
import numpy as np
from figures import HERE, ROOT, Sl

W=json.loads((ROOT/'cut_direction/results/worlds.json').read_text()); first={}
for w in W:
    for c in w['choices']: first.setdefault(c['key'],c)
delta=lambda a,b:abs((a-b+90)%180-90)
normals=sorted({round(math.degrees(math.atan2(n[1],n[0]))%180,6)%180 for rk in range(4) for n in Sl.WIN[rk][0]})
star=sorted((144*j)%180 for j in range(5))
normal_error=max(delta(c['line_angle']-90,144*int(np.argmax(c['shares']))) for c in first.values())
arithmetic_error=max(delta(108+72*int(np.argmax(c['shares'])),108-2*c['line_angle']) for c in first.values())
chronology={}
for study in ('cut_direction','settled_test'):
    chronology[study]={}
    for name in ('PREREGISTRATION.md',study+'.py'):
        path=f'exploratory/accretion_pilot/{study}/{name}'
        chronology[study][name]=subprocess.check_output(['git','log','--reverse','--diff-filter=A','--format=%H %aI','--',path],cwd=HERE.parents[2],text=True).strip()
r=dict(facet_normal_directions=normals,indexed_star_directions=star,same_sets=normals==star,maximum_observed_normal_error=normal_error,maximum_conditional_arithmetic_error=arithmetic_error,chronology=chronology)
(HERE/'results/geometry_checks.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
