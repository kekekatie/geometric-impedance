import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from audit_common import *

def main():
    selected=load('selected-audit.pkl');(HERE/'figures').mkdir(exist_ok=True)
    stats=json.loads((RESULTS/'scheduler_verification.json').read_text())
    for w in [7,5]:
        jam=load(f'jam-{w}-0.pkl');res=load(f'growth-{w}-0.pkl');case=next(c for c in stats['cases'] if c['case']==f'w{w}-B-s0')
        fig,axes=plt.subplots(1,2,figsize=(14,8.5));fig.patch.set_facecolor('white')
        for ax,checkpoint,st in zip(axes,['jam','final'],[jam,res]):
            bandkeys={S.dk(t) for t in st['band']};arc=selected[(w,0,checkpoint)];arckeys={S.dk(t) for t in arc}
            groups=[([t for t in st['full'] if S.dk(t) not in bandkeys],'#e5e7eb','#c5c9ce'),([t for t in st['band'] if S.dk(t) not in arckeys],'#b8d6ef','#6b9fc6'),(arc,'#8ed3a6','#368354')]
            for tiles,face,edge in groups:
                ax.add_collection(PolyCollection([[(z.real,z.imag) for z in t[1:]] for t in tiles],facecolors=face,edgecolors=edge,linewidths=.3))
            P=S.L.Patch(st['full']);fr=P.frontier();current={S.ekey(e[0],e[1]) for e in fr};zero={S.ekey(e[0],e[1]) for e in fr if not S.D.candidates(P,*e[:3])}
            historical={frozenset(tuple(v) for v in e) for e in res['scars']} if checkpoint=='final' else set()
            for edges,color,style,lw in [(historical-current,'#a14683','--',2),(historical&current-zero,'#b77608','--',2),(zero&historical,'#c23635','-',2.4),(zero-historical,'#d17a00','-',2.4)]:
                for edge in edges:
                    a,b=[complex(*v) for v in edge];ax.plot([a.real,b.real],[a.imag,b.imag],color=color,linestyle=style,lw=lw)
            bcen=sum(st['B'][1:])/3;ax.plot(bcen.real,bcen.imag,'*',color='#5b3283',ms=10,zorder=10)
            ax.autoscale();ax.margins(.06);ax.set_aspect('equal');ax.axis('off')
            step=jam['jam_step'] if checkpoint=='jam' else res['final_step']
            ax.set_title(f"{'Frozen jam' if checkpoint=='jam' else 'Scar continuation'} — step {step}\nFull patch {len(st['full'])} • boundary band {len(st['band'])}\nSelected subset {len(arc)} ({len(arc)/len(st['band']):.1%}) • reader selects B\nCurrent blocked edges: {len(zero)} • accumulated scar labels: {len(historical)}",fontsize=10,pad=12)
        handles=[Patch(facecolor='#e5e7eb',edgecolor='#c5c9ce',label='Construction archive outside analysed band (not deleted)'),Patch(facecolor='#b8d6ef',edgecolor='#6b9fc6',label='Analysed boundary band outside selected subset'),Patch(facecolor='#8ed3a6',edgecolor='#368354',label='Largest compatible subset found in original scan'),Line2D([],[],color='#c23635',lw=2.4,label='Current blocked frontier edge, already labelled scar'),Line2D([],[],color='#d17a00',lw=2.4,label='Current blocked frontier edge, not yet labelled'),Line2D([],[],color='#b77608',ls='--',lw=2,label='Labelled current edge now extendable (if any)'),Line2D([],[],color='#a14683',ls='--',lw=2,label='Historical scar label off current frontier (if any)'),Line2D([],[],color='#5b3283',marker='*',ls='',ms=10,label='Original B tile (retained in construction archive)')]
        fig.legend(handles=handles,loc='lower center',ncol=2,fontsize=9,frameon=False,bbox_to_anchor=(.5,.025))
        fig.suptitle(f"World {w} / B / stream 0 — full-patch construction, subset-only readout",fontsize=15,y=.98)
        fig.text(.5,.915,f"Added from frozen jam to step 44: {case['added_from_frozen_jam']} = first scar-step batch {case['first_scar_step_additions']} + later batches {case['historical_added_after_scar_step']}",ha='center',fontsize=10)
        fig.text(.5,.005,'Original endpoint scans differ in centre and resolution. These panels do not establish transport of one trace between endpoints.',ha='center',fontsize=9,color='#454b54')
        fig.subplots_adjust(top=.82,bottom=.24,wspace=.1)
        path=HERE/'figures'/f'corrected_w{w}.png';fig.savefig(path,dpi=160);plt.close(fig);print(path,flush=True)

if __name__=='__main__':main()
