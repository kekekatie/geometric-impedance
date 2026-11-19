"""Figures are drawn only from the certified JSON records."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from matplotlib.lines import Line2D

COL={'rough':'#d87521','smooth':'#2866b1','eligible':'#00877b','example':'#a32ba3'}
def panel(ax,obj,cert):
    xy=np.array([v['xy'] for v in obj['vertices']]); edges=obj['edges']; faces=obj['faces']
    ex=obj['eligible'][0] if obj['eligible'] else None
    for f in faces:
        highlight=ex is not None and f['id'] in edges[ex['edge']]['incident_faces']
        ax.add_patch(Polygon(xy[f['vertices']],facecolor='#ffe28a' if highlight else '#f0f1f3',edgecolor='none',zorder=0))
    for e in edges:
        pts=xy[e['vertices']]; ax.plot(*pts.T,color='#666d76',lw=1,zorder=1)
        if e['qubit'] is not None:
            m=pts.mean(0); ax.plot(*m,'o',ms=2.5,color='#666d76',zorder=2)
    for arc in obj['arcs']:
        for i in arc['edges']:
            ax.plot(*xy[edges[i]['vertices']].T,color=COL[arc['label']],lw=2.5,ls='--' if arc['label']=='rough' else '-',zorder=3)
    for e in obj['eligible']: ax.plot(*xy[edges[e['edge']]['vertices']].T,color=COL['eligible'],lw=4,zorder=4,solid_capstyle='round')
    if ex:
        ep=xy[edges[ex['edge']]['vertices']]; ax.plot(*ep.T,color=COL['example'],lw=4,zorder=5)
        ax.scatter(*ep.T,s=100,facecolor='white',edgecolor=COL['example'],lw=2,zorder=6)
        centre=xy.mean(0)
        for i,v in enumerate(edges[ex['edge']]['vertices']):
            delta=xy[v]-ep.mean(0); delta/=np.linalg.norm(delta)
            ax.text(*(xy[v]+.28*delta),ex['checks'][i],ha='center',va='center',fontsize=9,color=COL['example'],bbox=dict(fc='white',ec='none',alpha=.9,pad=1.3),zorder=7)
        for f in edges[ex['edge']]['incident_faces']:
            at=xy[faces[f]['vertices']].mean(0)
            ax.text(*at,faces[f]['zcheck'],ha='center',va='center',fontsize=10,fontweight='bold',bbox=dict(fc='#ffe28a',ec='none',pad=1),zorder=7)
        m=ep.mean(0); tangent=ep[1]-ep[0]; normal=np.array([-tangent[1],tangent[0]])
        ax.text(*(m+.16*normal),f"q{ex['qubit']}",fontsize=8,ha='center',color=COL['example'],bbox=dict(fc='white',ec='none',pad=1),zorder=8)
    name={'square':'Square','AB':'Ammann–Beenker','Penrose':'Penrose P3'}[obj['family']]
    ax.set_title(f"{name}\nn={cert['n']}  k=1  (dX,dZ)=(3,3)\n{cert['eligible_edges']} eligible edges",fontsize=12,pad=14)
    pairs=', '.join(f'({a},{b})' for a,b in cert['endpoint_degree_pairs'])
    ax.set_xlabel('Endpoint degrees: '+pairs,fontsize=9)
    ax.set_aspect('equal'); ax.set_anchor('N'); ax.set_xlim(xy[:,0].min()-.7,xy[:,0].max()+.7); ax.set_ylim(xy[:,1].min()-.7,xy[:,1].max()+.7)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
def legend(fig):
    handles=[Line2D([0],[0],color=COL['rough'],lw=2.5,ls='--',label='Rough arc: edges omitted'),
        Line2D([0],[0],color=COL['smooth'],lw=2.5,label='Smooth arc'),
        Line2D([0],[0],color=COL['eligible'],lw=4,label='Eligible loss edge'),
        Line2D([0],[0],color=COL['example'],lw=4,label='Example loss edge'),
        Line2D([0],[0],marker='o',mfc='white',mec=COL['example'],ls='',label='Two endpoint X-checks'),
        Patch(fc='#ffe28a',label='Two adjacent Z-checks')]
    fig.legend(handles=handles,loc='lower center',ncol=3,fontsize=9,frameon=False,bbox_to_anchor=(.5,.015))
def run(out):
    plt.rcParams['svg.hashsalt']='aperiodic-qec-geometry-v1'
    objs=[json.loads((out/(fam+'.json')).read_text()) for fam in ('square','AB','Penrose')]
    certs=[json.loads((out/(fam+'_certificate.json')).read_text()) for fam in ('square','AB','Penrose')]
    fig,axes=plt.subplots(1,3,figsize=(16,6.4))
    for ax,o,c in zip(axes,objs,certs): panel(ax,o,c)
    fig.suptitle('Certified whole-tile patches · one edge-qubit boundary convention',fontsize=16,y=.98)
    legend(fig); fig.subplots_adjust(bottom=.22,top=.78,wspace=.18)
    fig.savefig(out/'patches.png',dpi=180); fig.savefig(out/'patches.svg',metadata={'Date':None}); plt.close(fig)
    for o,c in zip(objs,certs):
        fig,ax=plt.subplots(figsize=(7,7)); panel(ax,o,c); legend(fig); fig.subplots_adjust(bottom=.22,top=.80)
        fig.savefig(out/(o['family']+'.png'),dpi=180); plt.close(fig)
if __name__=='__main__':
    import sys
    run(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'results')
