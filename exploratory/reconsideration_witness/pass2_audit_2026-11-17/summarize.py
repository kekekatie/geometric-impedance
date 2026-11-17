"""Create compact committed per-history evidence and presentation tables."""
import csv, json, hashlib
import audit

R=audit.OUT
caps=json.loads((R/'caps_summary.json').read_text(encoding='utf-8'))
panel=json.loads((R/'panel.json').read_text(encoding='utf-8'))
audit.save('panel_manifest.json',{k:v for k,v in panel.items() if k not in ('faults','tags')})
header=['history','stratum','truth','frame_X','frame_Z','absent_X','absent_Z']
for a in audit.ARMS: header += [a+'_label',a+'_tie',a+'_p0',a+'_p1']
for config in caps['summary']:
    obj=json.loads((R/f'cap_{config}.json').read_text(encoding='utf-8'))
    with (R/f'cap_{config}.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f,lineterminator='\n'); writer.writerow(header)
        for i,(r,tag) in enumerate(zip(obj['rows'],panel['tags'])):
            row=[i,tag,r['truth'],*r['frames'],int(r['absent']['X']),int(r['absent']['Z'])]
            for a in audit.ARMS: row += [r[a]['label'],int(r[a]['tie']),r[a]['p0'],r[a]['p1']]
            writer.writerow(row)

base=json.loads((R/'cap_33.json').read_text(encoding='utf-8'))['rows']
witnesses={}
for config in caps['changes']:
    rows=json.loads((R/f'cap_{config}.json').read_text(encoding='utf-8'))['rows']
    witnesses[config]=[dict(history=i,stratum=tag,fault_contributions=fts,baseline=a,raised=b)
        for i,(a,b,tag,fts) in enumerate(zip(base,rows,panel['tags'],panel['faults']))
        if any(a[arm]['label']!=b[arm]['label'] or a[arm]['tie']!=b[arm]['tie'] for arm in audit.ARMS)]
audit.save('decision_changes.json',witnesses)

# Reproduce the published thick-only comparison, including its nine-place rounding.
published=json.loads((audit.SRC.parent/'results/pass2_caps.json').read_text(encoding='utf-8'))
reproduction={}
for config in ('43','34'):
    rows=json.loads((R/f'cap_{config}.json').read_text(encoding='utf-8'))['rows']
    got=dict(n=len(rows),frame_changes=sum(a['frames']!=b['frames'] for a,b in zip(base,rows)),
        posterior_shifts=sum(abs(round(a['thick']['p0'],9)-round(b['thick']['p0'],9))>audit.EPS for a,b in zip(base,rows)),
        label_flips=sum(a['thick']['label']!=b['thick']['label'] for a,b in zip(base,rows)),
        tie_changes=sum(a['thick']['tie']!=b['thick']['tie'] for a,b in zip(base,rows)),
        thick_tie_truth_base=round(sum(audit.credit(a['thick'],a['truth']) for a in base)/len(base),6),
        thick_tie_truth_new=round(sum(audit.credit(a['thick'],a['truth']) for a in rows)/len(rows),6))
    assert got==published['comparisons'][config+'_vs_33'],(config,got,published)
    reproduction[config]=got
audit.save('published_thick_reproduction.json',reproduction)

lines=['# Paired margins (percentage points)', '',
       'Half-credit on ties; equal weighting within each panel component.', '',
       '| Caps | Weight-three thick − thin | Weight-three diamond − thin | Near-loss weight-one thick − thin | Near-loss weight-one diamond − thin |',
       '|---|---:|---:|---:|---:|']
for config, groups in caps['summary'].items():
    vals=[groups[g]['pairs'][a+'_minus_thin']['mean']*100 for g in ('triple','nearloss1') for a in ('thick','diamond')]
    lines.append('| ('+','.join(config)+') | '+' | '.join(f'{x:.6f}' for x in vals)+' |')
lines += ['', 'Weight-three: 250 sorted triples × 8 = 2,000 histories. Near-loss probes: 110 primitives × 8 = 880 histories.',
          'The sorted-prefix panel is diagnostic, not a population estimate. The full near-loss census is a separate 48,840-history result.', '',
          f"Conservative paired-mean (4,4) trigger: **{caps['escalate_44']}**.", '']
(audit.HERE/'TABLE.md').write_text('\n'.join(lines),encoding='utf-8')

# Independently recalculate all paired means from the committed CSV, not the summary generator.
for config, groups in caps['summary'].items():
    with (R/f'cap_{config}.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
    for group in ('triple','nearloss1'):
        rs=[r for r in rows if r['stratum']==group]
        def c(r,a): return .5 if int(r[a+'_tie']) else float(r[a+'_label']==r['truth'])
        for a in ('thick','diamond'):
            got=sum(c(r,a)-c(r,'thin') for r in rs)/len(rs)
            assert got==groups[group]['pairs'][a+'_minus_thin']['mean']
audit.save('csv_verification.json',dict(configs=len(caps['summary']),histories_per_config=2880,paired_means_recomputed=True))
print('\n'.join(lines).encode('ascii', 'replace').decode('ascii'))
