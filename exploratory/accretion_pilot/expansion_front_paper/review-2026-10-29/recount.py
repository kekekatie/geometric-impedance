"""Descriptive saved-data recount only: no engine imports or growth."""
import collections as c
import hashlib
import json
import math
from pathlib import Path
import statistics as s

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sources = {}
def read(path):
    raw = (ROOT / path).read_bytes()
    sources[path] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)
def ties(name):
    return [t for w in read(name + '/results/worlds.json') for t in w['ties']]
def moments(values):
    return dict(n=len(values), mean=s.mean(values), mean_abs=s.mean(map(abs, values)), median=s.median(values))

a = ties('corner-response-catalogue')
ks = [t for t in a if t['drawer'] == 'single_keystone']
ns = [t for t in ks if any(k['necessary'] for k in t['keystones'])]
groups = c.defaultdict(list)
for t in a:
    if t['drawer'] in ('single_keystone', 'committee', 'stayed_open'):
        groups[t['fps']['2']].append(t['drawer'] != 'stayed_open')
stiff = {fp: s.mean(v) for fp, v in groups.items() if len(v) >= 5}
out = dict(date='2026-10-29', reviewed_commit='49b47c57d7af065b0711ca7f91e943613e795cac')
out['A'] = dict(ties=len(a), drawers=dict(c.Counter(t['drawer'] for t in a)),
    sufficient=len(ks), necessary_and_sufficient=len(ns), redundant=len(ks)-len(ns),
    redundant_fraction_of_sufficient=(len(ks)-len(ns))/len(ks),
    redundant_fraction_of_settlements=(len(ks)-len(ns))/6606,
    necessary_corner_events=sum(all(k['corner'] for k in t['keystones'] if k['necessary']) for t in ns),
    placebo_event_mean=s.mean(t['placebo_rate'] for t in ks), placebo_event_denominator=len(ks),
    placebo_pooled_numerator=sum(t['n_sufficient'] for t in ks),
    placebo_pooled_denominator=sum(t['n_local'] for t in ks),
    recurring=len(stiff), rigid=sum(v >= .9 for v in stiff.values()),
    always_settle=sum(v == 1 for v in stiff.values()), malleable=sum(v < .9 for v in stiff.values()),
    stiffness_bins=dict(sorted(c.Counter(round(v, 1) for v in stiff.values()).items())))
b = ties('depth-direction-lenses')
out['B'] = {key: moments([t[key] for t in b if t.get(key) is not None])
            for key in ('keystone_inward', 'keystone_tangential')}
ct = ties('malleable-chase')
cg = c.defaultdict(list)
for t in ct:
    cg[t['fp']].append(t['burst'] == 'settled')
mal = {fp: s.mean(v) for fp,v in cg.items() if len(v)>=5 and stiff[fp]<.9}
unresolved_classes = {fp for fp,v in mal.items() if v<.999}
out['C'] = dict(n=len(ct), burst=dict(c.Counter(t['burst'] for t in ct)),
    malleable_classes=len(mal), classes_with_unresolved=len(unresolved_classes),
    saved_fields=sorted(set().union(*(t.keys() for t in ct))))
for label, selector in (
    ('observed_settled', lambda t:t['drawer'] in ('single_keystone','committee')),
    ('observed_open', lambda t:t['drawer']=='stayed_open'),
    ('core_burst_settled', lambda t:t['fp'] in unresolved_classes and t['burst']=='settled'),
    ('core_burst_open', lambda t:t['fp'] in unresolved_classes and t['burst']!='settled')):
    vals=[t['wall'] for t in ct if selector(t) and t['wall'] is not None]
    out['C'][label]=dict(moments(vals), near_inverse_phi_squared_1e_8=sum(abs(v-(3-math.sqrt(5))/2)<1e-8 for v in vals), min=min(vals), max=max(vals))
cl=read('paired-front/results/closure_measurements.json')
arms=[a for r in cl for a in r['arms']]
sc=[a for a in arms if not a['censored']]
out['closure']=dict(forks=len(cl), arms=len(arms), scored=len(sc),
    scored_forks=sum(any(not a['censored'] for a in r['arms']) for r in cl),
    censored=sum(a['censored'] for a in arms), last_steps=sorted(set(a['last_step'] for a in sc)),
    verdicts=dict(c.Counter(a['verdict'] for a in sc)), all_correct=sum(a['all_correct'] for a in sc),
    F1=[dict(world=r['world'],measurement=r['F1']) for r in cl if r['F1'] is not None])
pilot=read('paired-front/results/measurements.json')
out['pilot']=[{k:r['meta'][k] for k in ('world','skin_equiv','departA','departB','censored','endures_on_shared_ground')} for r in pilot]
for name in ('active-skin','skin-restart'):
    data=read(name+'/results.json')
    out[name]=dict(histories=len(data), steps=sum(len(x['rows']) for x in data),
        edge_queries=sum(row['edge_queries'] for x in data for row in x['rows']),
        cases=[dict(case=x['case'], steps=len(x['rows']), last_slice=x['rows'][-1]['slice'],
                    last_status=x['rows'][-1]['status']) for x in data])
out['source_sha256']=sources
(HERE/'recount.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('active-skin','skin-restart','source_sha256')},indent=2))
