"""Geometry-only arm definitions and pre-score drawing."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'fresh_site_address_audit_2026-11-20'))
import audit
SITES=[('AB_1',14),('Penrose_1',14),('Penrose_2',4)]

def prepare():
    sites=[]
    for patch,eid in SITES:
        code=audit.CorrectedPatchCode(audit.SOURCE/(patch+'.json'))
        d=code.json; e=next(e for e in d['eligible'] if e['edge']==eid)
        edge=next(x for x in d['edges'] if x['id']==eid)
        verts={v['id']:v for v in d['vertices']};faces={f['id']:f for f in d['faces']}
        geometric=[verts[v]['xcheck'] for v in edge['vertices']]+[faces[f]['zcheck'] for f in edge['incident_faces']]
        assert set(geometric)==set(e['checks']) and len(geometric)==4
        nx,nz=len(d['HX']),len(d['HZ']); idx=lambda c:audit.check_index(c,nx,nz)
        assert sorted(map(idx,geometric))==code.STAR[e['qubit']]
        intended={tuple(x) for x in e['query']}
        assert intended=={(c,t) for c in geometric for t in (1,2)}
        arms=[]
        for c in sorted(geometric,key=idx):
            coords=sorted(intended-{(c,1),(c,2)},key=lambda x:(idx(x[0]),x[1]))
            assert len(coords)==6 and all(x[0]!=c for x in coords)
            arms.append(dict(omitted=c,index=idx(c),type=c[0],role='endpoint' if c[0]=='X' else 'face',
                weight=len(code.STABS[idx(c)]['support']),withheld=[[c,1],[c,2]],
                retained_coordinates=[list(x) for x in coords],numeric_coordinates=[[idx(a),t] for a,t in coords],
                retained_indices=sorted({idx(a) for a,t in coords})))
        sites.append(dict(patch=patch,edge=eid,qubit=e['qubit'],intact_indices=code.STAR[e['qubit']],
                          scored_logical_Z=d['logical_Z'],arms=arms))
    result=dict(starting_sha='1f85f7921bf9615bfa87173eb2d77d9159e211d3',sites=sites,
        primary='100 * (weighted intact truth credit - weighted omission truth credit)',
        gained='100 * weighted mean max(omission credit - intact credit, 0)',
        lost='100 * weighted mean max(intact credit - omission credit, 0)',
        tie_credit=.5,selection='all four incident checks at each frozen site; no preselected winner')
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/arms.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def draw(plan, costs=None, filename='geometry'):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon,Circle
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib.cm import ScalarMappable
    plt.rcParams['svg.hashsalt']='local-witness-omission'
    fig,axes=plt.subplots(1,3,figsize=(13.5,5.6))
    if costs is not None:
        extent=max(abs(v) for v in costs.values()) or 1e-6
        norm=TwoSlopeNorm(vmin=-extent,vcenter=0,vmax=extent); cmap=plt.get_cmap('PuOr_r')
    for ax,site in zip(axes,plan['sites']):
        d=json.loads((audit.SOURCE/(site['patch']+'.json')).read_text())
        xy=np.array([v['xy'] for v in d['vertices']]); arms={a['omitted']:a for a in site['arms']}
        color=lambda c:cmap(norm(costs[site['patch'],c])) if costs is not None else '#b5dad3'
        label=lambda c:f'{c} · w{arms[c]["weight"]}'+(f'\n{costs[site["patch"],c]:+.5f} pp' if costs is not None else '')
        for f in d['faces']:
            c=f['zcheck']; ax.add_patch(Polygon(xy[f['vertices']],fc=color(c) if c in arms else '#f2f3f5',ec='none',zorder=0))
        for e in d['edges']:ax.plot(*xy[e['vertices']].T,color='#8b9096',lw=1,zorder=1)
        for arc in d['arcs']:
            for i in arc['edges']:ax.plot(*xy[d['edges'][i]['vertices']].T,color='#555d66',lw=1.7,ls='--' if arc['label']=='rough' else '-',zorder=2)
        loss=next(e for e in d['edges'] if e['id']==site['edge'])
        ax.plot(*xy[loss['vertices']].T,color='#cf2638',lw=3.5,zorder=3)
        at=xy[loss['vertices']].mean(0);ax.add_patch(Circle(at,.19,fill=False,ec='#cf2638',lw=2,zorder=5))
        for f in d['faces']:
            c=f['zcheck']
            if c in arms:
                p=xy[f['vertices']].mean(0);ax.text(*p,label(c),ha='center',va='center',fontsize=9,fontweight='bold',bbox=dict(fc='white',ec='none',alpha=.8),zorder=6)
        for v in d['vertices']:
            c=v['xcheck']
            if c in arms:
                ax.scatter(*xy[v['id']],s=190,c=[color(c)],ec='#20242a',lw=1.3,zorder=7)
                offsets={'AB_1':{'X4':(20,-40),'X5':(-70,30)},'Penrose_1':{'X4':(25,-40),'X6':(-70,30)},'Penrose_2':{'X0':(-75,-35),'X5':(30,30)}}
                ax.annotate(label(c),xy[v['id']],xytext=offsets[site['patch']][c],textcoords='offset points',fontsize=9,fontweight='bold',bbox=dict(fc='white',ec='none',alpha=.85),arrowprops=dict(arrowstyle='-',color='#555'),zorder=8)
        ax.set_aspect('equal');ax.axis('off');ax.margins(.22)
        ax.set_title(f"{site['patch']} · loss e{site['edge']} / q{site['qubit']}",fontsize=12)
    fig.suptitle('Withhold both old readings from one witness; keep its thin state',fontsize=14,y=.98)
    if costs is not None:
        cax=fig.add_axes([.22,.10,.56,.025]);cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal')
        cb.set_ticks([-extent,0,extent]);cb.set_ticklabels([f'{-extent:.4f}','0',f'{extent:.4f}'])
        cb.set_label('Intact minus six-reading truth credit (pp): positive = withholding hurt',fontsize=10)
    fig.text(.5,.02,'Red circle: loss edge · X markers: endpoint checks · Z faces: adjacent checks · w: check weight'+('\nGeometry only: all four omissions per site; no predicted winner.' if costs is None else '\nShared signed scale; negative costs mean improved aggregate truth credit.'),ha='center',fontsize=10)
    fig.subplots_adjust(left=.02,right=.98,top=.86,bottom=.23 if costs is not None else .12,wspace=.12)
    fig.savefig(ROOT/f'results/{filename}.png',dpi=180)
    svg=ROOT/f'results/{filename}.svg';fig.savefig(svg,metadata={'Date':None});plt.close(fig)
    svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n')

if __name__=='__main__':draw(prepare())
