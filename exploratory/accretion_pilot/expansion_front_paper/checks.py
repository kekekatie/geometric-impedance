"""Descriptive saved-data audit, 2026-10-16. Does not rerun either study."""
from pathlib import Path
import json, collections, hashlib, subprocess
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'results'
OUT.mkdir(exist_ok=True)
paths = [ROOT/'cut_direction/results/worlds.json', ROOT/'settled_test/results/results.json']
W, R = [json.loads(p.read_text()) for p in paths]
first = {}
for w in W:
    for c in w['choices']:
        first.setdefault(c['key'], c)
U = list(first.values())
T = R['situations']
new = [r for r in T if r['key'] not in first]
later = [r for r in T if any(r['guesses']['A'] + r['guesses']['B'])]
quiet = [r for r in T if not any(r['guesses']['A'] + r['guesses']['B'])]
stable = lambda rs: sum(set(r['dom_cont']) == {r['j']} for r in rs)
el = [c for c in U if c['ratio'] >= 3]
delta = lambda a,b: abs((a-b+90)%180-90)
pairs = np.array([p for c in U for p in c['built']])
slope, intercept = np.polyfit(pairs[:,0], pairs[:,1], 1)
median = float(np.median([c['n_strip'] for c in el]))
chosen = min(el, key=lambda c:(abs(c['n_strip']-median), c['key']))
selection = dict(criterion='Among first occurrences with ratio >= 3, minimize absolute distance of n_strip from the eligible median; break ties lexicographically by key.', eligible=len(el), median_n_strip=median, key=chosen['key'], world=chosen['world'], slice=chosen['slice'], n_strip=chosen['n_strip'], ratio=chosen['ratio'])
(OUT/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
families = lambda rs: dict(sorted(collections.Counter(r['j'] for r in rs).items()))
shares = [x for r in T for x in r['core_share']]
p4 = [r for r in T if r['core']['worst'] is not None]
train = [c for c in U if c['world']<12]
test = [c for c in U if c['world']>=12]
table = {d:collections.Counter(int(np.argmax(c['shares'])) for c in train if c['direction']==d).most_common(1)[0][0] for d in sorted({c['direction'] for c in train})}
corrected = {}
for c in U:
    d=int(round((c['line_angle']-18)/36))*36%180+18
    corrected.setdefault(d,collections.Counter())[int(np.argmax(c['shares']))]+=1
result = dict(date='2026-10-16', base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(), source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, unique=[len(U),len(T)], overlap=len(set(first)&{r['key'] for r in T}), new_configurations=len(new), new_P1=sum(r['dom_burst']==r['j'] for r in new), later_guess=[stable(later),len(later)], no_later_guess=[stable(quiet),len(quiet)], followup_families={j:families(T).get(j,0) for j in range(5)}, new_families=families(new), elongated=len(el), maximum_angle_deviation=max(delta(c['axis'],108-2*c['line_angle']) for c in el), placement_fit=dict(n=len(pairs),intercept=float(intercept),slope=float(slope)), registered_C1=[sum(sorted(c['shares'])[-1]-sorted(c['shares'])[-2]>=.15 for c in U),len(U)], registered_C2=[sum(table.get(c['direction'])==int(np.argmax(c['shares'])) for c in test),len(test)], registered_C3=dict(directions=len(table),families=len(set(table.values()))), registered_C4=[sum(delta(c['axis'],108+72*int(np.argmax(c['shares'])))<=20 for c in el),len(el)], corrected_bins=corrected, P1=[sum(r['dom_burst']==r['j'] for r in T),len(T)], P2=dict(passing=sum(x>=.5 for x in shares),n=len(shares),median=float(np.median(shares)),quartiles=np.quantile(shares,[.25,.75]).tolist()), P3=[sum(len(set(r['dom_cont']))==1 for r in T),len(T)], P4=dict(passing=sum(r['core']['worst']>=.99 for r in p4),n=len(p4),identical=sum(r['core']['identical'] for r in p4),covered=sum(r['core']['covered'] for r in p4)), burst_status=dict(collections.Counter(s for r in T for s in r['burst_status'])), guesses=dict(collections.Counter(g for r in T for o in 'AB' for g in r['guesses'][o])), exception=next(r for r in T if r['key']=='180fb0b920bb845b'))
result['noncore_control'] = dict(identical=sum(r['noncore']['identical'] for r in T),covered=sum(r['noncore']['covered'] for r in T))
tile_only = [m for m in R['meta'].values() if m['angle_tile_only'] is not None]
result['choice_tile_only_cut'] = dict(found=len(tile_only),total=len(R['meta']),same_direction=sum(delta(m['angle'],m['angle_tile_only'])<1 for m in tile_only))
(OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Saved-data checks - 16 October 2026','','New descriptive reanalysis of saved data; not an independent growth-engine replication. Configuration keys retain the existing rounded, translation-normalized definition. First occurrence per key is retained.','', '| Check | Recomputed result |','|---|---|']
for k,v in result.items():
    if k not in ('exception','source_sha256'):
        lines.append(f'| {k} | {json.dumps(v)} |')
lines += ['', 'P4 counts covered tile-comparison instances across ordered continuation pairs, not independent tiles or trials. Forty slices is a censoring cap, not a measured stopping time or width. The fit is a pooled placement-time association, not a propagation speed.', '', '## Figure selection',json.dumps(selection,indent=2),'','## Provenance',json.dumps(result['source_sha256'],indent=2)]
(HERE/'CHECKS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('exception','source_sha256')},indent=2))
print('SELECTION',selection)
