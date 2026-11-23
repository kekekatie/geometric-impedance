"""Independent Decimal score aggregation and the fixed A/B four-arm comparison."""
import csv,gzip,json
from decimal import Decimal,getcontext
import prepare
ROOT=prepare.ROOT;R=ROOT/'results'

def main():
    getcontext().prec=45
    plan=json.loads((R/'arms.json').read_text());summary=[];gains_table=[];cost_table=[];checks={}
    for site in plan['sites']:
        d=json.loads((R/(site['name']+'.json')).read_text());assert d['site']==site and d['histories']==385648
        names=list(d['credits']);tot={a:[Decimal(0)]*3 for a in names};counts=[0,0,0]
        with gzip.open(R/(site['name']+'.csv.gz'),'rt',newline='') as f:
            for i,row in enumerate(csv.DictReader(f)):
                assert int(row['config_id'])==i;k=int(row['ordinary_weight']);counts[k]+=8
                for a in names:
                    v=Decimal(row[a]);assert 0<=v<=8 and v*2==int(v*2);tot[a][k]+=v
        assert i+1==48206 and counts==d['counts']
        weights=[(Decimal(1)/999)**k for k in range(3)];mass=sum(c*w for c,w in zip(counts,weights))
        exact={a:sum(c*w for c,w in zip(tot[a],weights))/mass for a in names}
        for a in names:
            assert list(map(float,tot[a]))==d['credits'][a]
            assert abs(float(exact[a])-d['scores'][a])<1e-14
        exactI=100*(exact['A']+exact['B']-exact['AB']-exact['0'])
        assert abs(float(exactI)-d['costs_pp']['I'])<1e-11
        c=d['costs_pp']
        assert abs(c['A_loss_B_absent']-c['A_loss_B_present']-c['I'])<1e-12
        assert abs(c['B_loss_A_absent']-c['B_loss_A_present']-c['I'])<1e-12
        s=dict(site=site['name'],edge=site['edge'],A=site['A'],A_role=site['A_role'],B=site['B'],B_role=site['B_role'],
               full_gain_pp=d['gains_pp']['thick'],gains_pp={a:d['gains_pp'][a] for a in ('AB','A','B','0')},
               recovered_percent=d['recovered_percent'],costs_pp=d['costs_pp'],baseline_equality=d['baseline_equality'],
               baseline_precision=d.get('baseline_precision'),recovered_complete_csv=d.get('recovered_complete_csv',False),validation=d['validation'])
        summary.append(s)
        gains_table.append(dict(site=site['name'],A=site['A'],B=site['B'],full_gain_pp=s['full_gain_pp'],
            **{f'G_{a}_pp':s['gains_pp'][a] for a in ('AB','A','B','0')},**{f'G_{a}_percent_full':s['recovered_percent'][a] for a in ('AB','A','B','0')}))
        cost_table.append(dict(site=site['name'],A=site['A'],B=site['B'],G_0_pp=s['gains_pp']['0'],**s['costs_pp']))
        for k,v in d['validation'].items():checks[k]=max(checks.get(k,0),v) if k.startswith('max_') else checks.get(k,0)+v
    for filename,rows in [('gains.csv',gains_table),('interactions.csv',cost_table)]:
        with (R/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    out=dict(starting_sha=prepare.BASE,protocol_commit='1b95282be3837da01ae8ac859f561b99f38b0ef7',
        histories=1928240,csv_rows_verified=241030,sites=summary,validation_totals=checks)
    (R/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    lines=['All gains and costs are percentage points; percentages are fractions of full-archive gain.','',
        '| Site (A / B) | Both gain (%) | A only gain (%) | B only gain (%) | Neither gain (%) | Full gain |',
        '|---|---:|---:|---:|---:|---:|']
    for s in summary:
        cells=[f"{s['gains_pp'][a]:+.8f} ({s['recovered_percent'][a]:.3f}%)" for a in ('AB','A','B','0')]
        lines.append(f"| {s['site']} ({s['A']} / {s['B']}) | "+' | '.join(cells)+f" | {s['full_gain_pp']:.8f} |")
    lines+=['','| Site | Lose A, B present | Lose A, B absent | Lose B, A present | Lose B, A absent | I |',
            '|---|---:|---:|---:|---:|---:|']
    for s in summary:lines.append('| '+s['site']+' | '+' | '.join(f'{v:+.8f}' for v in s['costs_pp'].values())+' |')
    (R/'table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    draw(summary);print(json.dumps(out,indent=2))

def draw(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['svg.hashsalt']='paired-face-four-arms'
    fig,axes=plt.subplots(2,3,figsize=(13,8));colors=['#71599b','#467ca4','#d89545','#777e86']
    bottom=min(0,min(s['recovered_percent'][a] for s in summary for a in ('AB','A','B','0')))-3
    for ax,s in zip(axes.flat,summary):
        vals=[s['recovered_percent'][a] for a in ('AB','A','B','0')]
        ax.bar(range(4),vals,color=colors,width=.65)
        for i,v in enumerate(vals):ax.text(i,v+(2 if v>=0 else -2),f'{v:.2f}%',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
        ax.axhline(100,color='#999',ls='--',lw=.8);ax.axhline(0,color='#333',lw=.6)
        ax.set_xticks(range(4),['Both\nA+B','A only','B only','Neither'])
        ax.set_ylim(bottom,112);ax.set_ylabel('% of full-archive gain',fontsize=9)
        ax.set_title(f"{s['site']} · e{s['edge']}\nA = {s['A']} ({s['A_role']})\nB = {s['B']} ({s['B_role']})",fontsize=10)
        ax.spines[['right','top']].set_visible(False)
    ax=axes.flat[-1];ax.axis('off')
    text='Interaction I (percentage points)\n\n'+'\n'.join(f"{s['site']}: {s['costs_pp']['I']:+.6f}" for s in summary)
    text+='\n\nPositive: a face costs more to lose\nwhen its partner is already absent.\nAccuracy comparison, not a measure\nof independent stored information.'
    ax.text(.02,.95,text,va='top',fontsize=11)
    fig.suptitle('Which face readings are still available?',fontsize=16)
    fig.text(.5,.015,'All four arms retain both endpoint X-checks’ four early readings, live observations, boundary parity and committed frame.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.04,1,.95),h_pad=3)
    fig.savefig(R/'four_arm_comparison.png',dpi=180);p=R/'four_arm_comparison.svg';fig.savefig(p,metadata={'Date':None});plt.close(fig)
    p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
if __name__=='__main__':main()
