"""Independent Decimal aggregation, all-site score table and on-route picture."""
import csv
import gzip
import json
from decimal import Decimal, getcontext
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/'results'

def main():
    getcontext().prec=40
    audit=json.loads((RESULTS/'address_audit.json').read_text())
    original=json.loads((ROOT.parent/'aperiodic_predict_2026-11-20/results/paired_results.json').read_text())
    rows=[]; validations={}; hashes=set()
    for site in audit['sites']:
        name=f"{site['patch']}_e{site['edge']}"
        d=json.loads((RESULTS/(name+'.json')).read_text())
        assert d['queries']==site and d['histories']==385648
        hashes.add(d['config_stream_sha256'])
        arms=list(d['scores']); credits={a:[Decimal(0)]*3 for a in arms}; counts=[0,0,0]
        with gzip.open(RESULTS/(name+'.csv.gz'),'rt',newline='') as f:
            for i,r in enumerate(csv.DictReader(f)):
                assert int(r['config_id'])==i
                k=int(r['ordinary_weight']); counts[k]+=8
                for a in arms:
                    c=Decimal(r[a]); assert 0<=c<=8 and c*2==int(c*2)
                    credits[a][k]+=c
        assert i+1==48206 and counts==d['histories_by_weight']
        weights=[(Decimal(1)/999)**k for k in range(3)]
        mass=sum(c*w for c,w in zip(counts,weights))
        for a in arms:
            assert list(map(float,credits[a]))==d['scores'][a]['credits_by_weight']
            assert abs(float(sum(c*w for c,w in zip(credits[a],weights))/mass)-d['scores'][a]['truth_credit'])<1e-14
        s=d['scores']; gain=s['thick']['gain_over_thin_pp']; corrected=s['corrected_diamond']['gain_over_thin_pp']
        rows.append(dict(patch=site['patch'],edge=site['edge'],qubit=site['qubit'],on_route_pair=site['edge']==original['patches'][site['patch']]['on_edge'],
            thick_thin_pp=gain,legacy_diamond_thin_pp=s['legacy_diamond']['gain_over_thin_pp'],corrected_diamond_thin_pp=corrected,
            corrected_thick_gap_pp=s['corrected_diamond']['remaining_thick_gap_pp'],
            correction_gain_pp=corrected-s['legacy_diamond']['gain_over_thin_pp'],
            archive_gain_recovered_percent=100*corrected/gain))
        for k,v in d['validation'].items():
            if k.startswith('max_'): validations[k]=max(validations.get(k,0),v)
            else: validations[k]=validations.get(k,0)+v
    assert len(hashes)==1
    pairs={}
    for patch,p in original['patches'].items():
        on=next(r for r in rows if r['patch']==patch and r['edge']==p['on_edge'])
        off=next(r for r in rows if r['patch']==patch and r['edge']==p['off_edge'])
        delta=on['thick_thin_pp']-off['thick_thin_pp']
        assert round(delta,5)==p['delta']
        pairs[patch]=dict(on_edge=p['on_edge'],off_edge=p['off_edge'],thick_thin_on_minus_off_pp=delta,
            corrected_diamond_thin_on_minus_off_pp=on['corrected_diamond_thin_pp']-off['corrected_diamond_thin_pp'])
    out=dict(starting_sha=audit['starting_sha'],protocol_commit='91430382f41b5236832a378a55b5c4c2379e9dbe',
             sites=10,histories=3856480,config_stream_sha256=next(iter(hashes)),
             decimal_csv_rows_verified=482060,rows=rows,pairs=pairs,validation_totals=validations)
    (RESULTS/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    with (RESULTS/'summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    text=['| Site | Thick−thin | Old diamond−thin | Corrected diamond−thin | Thick−corrected | Recovered |',
          '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        text.append(f"| {r['patch']} e{r['edge']} | {r['thick_thin_pp']:.6f} | {r['legacy_diamond_thin_pp']:.6f} | {r['corrected_diamond_thin_pp']:.6f} | {r['corrected_thick_gap_pp']:.6f} | {r['archive_gain_recovered_percent']:.2f}% |")
    (RESULTS/'table.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    draw(rows)
    print(json.dumps(out,indent=2))

def draw(rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['svg.hashsalt']='fresh-site-address-audit'
    on=[r for r in rows if r['on_route_pair']]
    fig,ax=plt.subplots(figsize=(8,4.8))
    for j,(key,label,color) in enumerate([('legacy_diamond_thin_pp','Old addresses','#9b9fa5'),('corrected_diamond_thin_pp','Correct incident checks','#008579'),('thick_thin_pp','Full archive / thick','#75529f')]):
        ax.bar([i+(j-1)*.24 for i in range(3)],[r[key] for r in on],width=.22,label=label,color=color)
    ax.set_xticks(range(3),[f"{r['patch']} · e{r['edge']}" for r in on]);ax.set_ylabel('Gain over thin (percentage points)')
    ax.set_title('What the four incident checks actually recover\nFrozen on-route sites, corrected archive addresses')
    ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,loc='upper left',fontsize=9)
    ax.set_ylim(bottom=0,top=max(r['thick_thin_pp'] for r in on)*1.35)
    fig.text(.5,.02,'Same (3,3) decoder and exhaustive ≤2-fault histories; only local query addresses change.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.045,1,1))
    fig.savefig(RESULTS/'corrected_recovery.png',dpi=180)
    svg=RESULTS/'corrected_recovery.svg'
    fig.savefig(svg,metadata={'Date':None});plt.close(fig)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')

if __name__=='__main__':main()
