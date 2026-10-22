"""Fixed original-frontier probes: candidate sets under whole-tile neighbourhoods.
No truncated patch is grown, and newly exposed artificial edges are never queried.
Radii and snapshots fixed before results: R=1,2,3,4,6 nominal S units;
original continuations after 11,19,28,42,44,59; alternative after 43,44,45.
"""
from pathlib import Path
import json,pickle
import figures as F
import choice_tracking as C
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent; O=H/'local-information'; O.mkdir(exist_ok=True)
L,D,S=F.L,F.D,F.S
def main():
    runs=pickle.loads((H/'choice-tracking/replay.pkl').read_bytes())
    alt=pickle.loads((H/'ancestry-test/alternative.pkl').read_bytes())
    samples=[(f'continuation-{i}',s,r[s-1]['tiles']) for i,r in zip([1,3],runs) for s in [11,19,28,42,44,59]]
    samples += [('alternative-29',s,alt[s]) for s in [43,44,45]]
    radii=[1,2,3,4,6]; rows=[]
    for name,s,ts in samples:
        P=L.Patch(ts); fr=P.frontier()
        for edge in fr:
            mid=(edge[0]+edge[1])/2; full={repr(D.dkey(t)) for t in D.candidates(P,*edge[:3])}
            for radius in radii:
                local=[t for t in ts if min(abs(z-mid) for z in t[1:]) <= radius*S+1e-12]
                Q=L.Patch(local); options={repr(D.dkey(t)) for t in D.candidates(Q,*edge[:3])}
                rows.append(dict(history=name,after_slice=s,site=C.ek(edge),radius=radius,full_count=len(full),local_count=len(options),same=full==options,extra=sorted(options-full),missing=sorted(full-options),retained=len(local),total=len(ts)))
        print(name,s,'edges',len(fr),flush=True)
    summary=[]
    for radius in radii:
        rr=[r for r in rows if r['radius']==radius]
        summary.append(dict(radius=radius,probes=len(rr),exact=sum(r['same'] for r in rr),extra_probes=sum(bool(r['extra']) for r in rr),missing_probes=sum(bool(r['missing']) for r in rr),mean_retained=sum(r['retained'] for r in rr)/len(rr),mean_fraction=sum(r['retained']/r['total'] for r in rr)/len(rr)))
    (O/'measurements.json').write_text(json.dumps(dict(protocol=__doc__,summary=summary,probes=rows),indent=2))
    fig,axs=plt.subplots(1,2,figsize=(10,4.5))
    axs[0].plot(radii,[100*r['exact']/r['probes'] for r in summary],'o-',color=F.A); axs[0].set(xlabel='Neighbourhood radius (S units)',ylabel='Exact candidate-set agreement (%)',ylim=(0,105),xticks=radii,title='Does the local view give the same alternatives?')
    axs[1].plot(radii,[100*r['mean_fraction'] for r in summary],'o-',color=F.B); axs[1].set(xlabel='Neighbourhood radius (S units)',ylabel='Mean fraction of built tiles retained (%)',ylim=(0,105),xticks=radii,title='How much of the built patch was retained?')
    fig.suptitle('Local information at existing frontier edges',fontsize=16)
    fig.text(.04,.025,'15 saved states; original edges only. Whole tiles retained if any vertex is inside the radius.\nThis tests candidate information, not local scheduling or a physical thickness of the present.',fontsize=9)
    fig.tight_layout(rect=(0,.12,1,.91)); fig.savefig(O/'local-information.png',dpi=160); plt.close(fig)
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__': main()
