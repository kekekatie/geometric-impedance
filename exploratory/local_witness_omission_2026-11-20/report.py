"""Verify paired CSV with Decimal arithmetic and draw the twelve measured costs."""
import csv
import gzip
import json
from decimal import Decimal,getcontext
import prepare
ROOT=prepare.ROOT;RESULTS=ROOT/'results'

def main():
    getcontext().prec=40
    plan=json.loads((RESULTS/'arms.json').read_text());rows=[];valid={};baselines={};hashes=set();rankings={};preflight={}
    for site in plan['sites']:
        name=f"{site['patch']}_e{site['edge']}";data=json.loads((RESULTS/(name+'.json')).read_text())
        assert data['site']==site and data['histories']==385648
        baseline=json.loads((ROOT.parent/'fresh_site_address_audit_2026-11-20/results'/(name+'.json')).read_text())
        assert data['config_stream_sha256']==baseline['config_stream_sha256']
        assert data['preflight']['comparisons']==768 and data['preflight']['mismatches']==0
        preflight[name]=data['preflight']
        counts=[0,0,0];totals={}
        with gzip.open(RESULTS/(name+'.csv.gz'),'rt',newline='') as f:
            for i,r in enumerate(csv.DictReader(f)):
                assert int(r['config_id'])==i
                k=int(r['ordinary_weight']);counts[k]+=8
                for field,v in r.items():
                    if field in ('config_id','ordinary_weight'):continue
                    x=Decimal(v);assert 0<=x<=8 and x*2==int(x*2)
                    totals.setdefault(field,[Decimal(0)]*3)[k]+=x
                for a in site['arms']:
                    c=a['omitted']
                    assert Decimal(r['intact_credit'])-Decimal(r[c+'_credit'])==Decimal(r[c+'_lost'])-Decimal(r[c+'_gained'])
        assert i+1==48206 and counts==data['histories_by_weight']
        w=[(Decimal(1)/999)**k for k in range(3)];mass=sum(c*x for c,x in zip(counts,w))
        mean=lambda field:sum(c*x for c,x in zip(totals[field],w))/mass
        for a,s in data['scores'].items():
            assert list(map(float,totals[a+'_credit']))==s['credits_by_weight']
            assert abs(float(mean(a+'_credit'))-s['truth_credit'])<1e-14
        for a in data['omissions']:
            c=a['omitted']
            for m in ('gained','lost','labels','ties'):
                assert list(map(float,totals[c+'_'+m]))==a['movements_by_weight'][m]
            cost=100*(mean('intact_credit')-mean(c+'_credit'))
            assert abs(float(cost)-a['cost_pp'])<1e-11
            assert abs(cost-100*(mean(c+'_lost')-mean(c+'_gained')))<Decimal('1e-35')
            for m in ('gained','lost'):assert abs(float(100*mean(c+'_'+m))-a['truth_'+m+'_pp'])<1e-12
            row=dict(site=name,patch=site['patch'],edge=site['edge'],omitted=c,type=a['type'],role=a['role'],weight=a['weight'],
                cost_pp=a['cost_pp'],six_reading_gain_pp=a['gain_over_thin_pp'],intact_gain_pp=a['intact_gain_pp'],
                full_archive_gain_pp=a['full_archive_gain_pp'],archive_gain_recovered_percent=100*a['gain_over_thin_pp']/a['full_archive_gain_pp'],
                truth_lost_pp=a['truth_lost_pp'],truth_gained_pp=a['truth_gained_pp'],label_changes=a['label_changes'],
                tie_status_changes=a['tie_status_changes'],label_changes_weighted_percent=a['label_changes_weighted_percent'],
                tie_changes_weighted_percent=a['tie_changes_weighted_percent'])
            rows.append(row)
        hashes.add(data['config_stream_sha256'])
        baselines[name]={a:data['scores'][a]['truth_credit'] for a in ('thin','intact','thick','whole')}
        for k,v in data['validation'].items():valid[k]=max(valid.get(k,0),v) if k.startswith('max_') else valid.get(k,0)+v
        here=[r for r in rows if r['site']==name];lo=min(r['cost_pp'] for r in here);hi=max(r['cost_pp'] for r in here)
        rankings[name]=dict(most_affordable=[r['omitted'] for r in here if abs(r['cost_pp']-lo)<1e-12],
                           least_affordable=[r['omitted'] for r in here if abs(r['cost_pp']-hi)<1e-12],minimum_cost_pp=lo,maximum_cost_pp=hi)
    assert len(hashes)==1 and len(rows)==12
    summary=dict(starting_sha=plan['starting_sha'],protocol_commit='9434ea1d04c87ce28c77d1b059d3cde207e95911',
        histories=1156944,config_rows_verified=144618,config_stream_sha256=next(iter(hashes)),baselines=baselines,
        rows=rows,rankings=rankings,preflight=preflight,validation=valid)
    (RESULTS/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (RESULTS/'omissions.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    lines=['All gains/costs are percentage points. Positive cost means withholding hurt.','',
        '| Site | Omit | Role / weight | Cost | Six-reading gain | Full gain | Credit lost | Credit gained | Label changes | Tie changes |',
        '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['site']} | {r['omitted']} | {r['role']} / {r['weight']} | {r['cost_pp']:+.8f} | {r['six_reading_gain_pp']:+.8f} | {r['full_archive_gain_pp']:.8f} | {r['truth_lost_pp']:.8f} | {r['truth_gained_pp']:.8f} | {r['label_changes']} | {r['tie_status_changes']} |")
    (RESULTS/'table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    prepare.draw(plan,{(r['patch'],r['omitted']):r['cost_pp'] for r in rows},'omission_costs')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
