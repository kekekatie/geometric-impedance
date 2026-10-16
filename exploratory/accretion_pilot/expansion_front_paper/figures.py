"""Targeted reconstruction and scientific figures; exploratory, 2026-10-16.
Run checks.py first. Only the two selected world prefixes are reconstructed.
Use --plot-only to redraw the locally generated geometry cache.
"""
from pathlib import Path
import sys, json, random, pickle, platform, os
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'results/mpl-cache'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.patches import Polygon, Patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'settled_test'))
# A historical transitive import reads argv at module import time.
_args=sys.argv[:]
try:
    sys.argv=sys.argv[:1]
    import settled_test as ST
finally:
    sys.argv=_args
CD, L, D, Sl, SN, S = ST.CD, ST.L, ST.D, ST.Sl, ST.SN, ST.S
OUT=HERE/'figures'; OUT.mkdir(exist_ok=True)
RES=HERE/'results'
A,B,CORE='#167c9b','#d66a34','#713c91'
GRAY,EDGE='#dce1e4','#929da3'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'svg.fonttype':'none'})

def prefix(module, world, target_slice, key):
    """Same pre-choice loop as the original world(), stopped at selected slice."""
    rng=random.Random(module.SEED0+world)
    P=L.Patch(L.seed_patch(module.centres()[world],3*S)); n0=len(P.tris)
    for r in range(1,target_slice+1):
        fr=P.frontier(); forced={}
        for e in fr:
            cs=D.candidates(P,*e[:3])
            if not cs: raise RuntimeError('JAM before selected choice')
            if len(cs)==1: forced.setdefault(D.dkey(cs[0]),cs[0])
        placed=0
        for t in forced.values():
            if len(P.tris)-n0>=module.N_ADD: break
            if P.legal(t): P.add(t); placed+=1
        if placed or forced: continue
        cs=SN.ordered(D.candidates(P,*fr[0][:3]))
        if r==target_slice:
            actual=CD.whole_key(P.tris,(fr[0][0]+fr[0][1])/2)
            if actual!=key: raise RuntimeError(f'Configuration mismatch: {actual} != {key}')
            if len(cs)!=2: raise RuntimeError('Not a two-way choice')
            return list(P.tris),cs
        P.add(rng.choice(cs))
    raise RuntimeError('Selected slice did not contain a choice')

def trace(base,c,stream,steps=20):
    Q=L.Patch(list(base)); Q.add(c); rng=random.Random(stream)
    built={D.dkey(c):0}; snapshots={0:list(Q.tris)}; guesses=[]
    for s in range(1,steps+1):
        n0=len(Q.tris); status,n,kind=SN.patient(Q,rng)
        if status=='JAM': raise RuntimeError('Reconstruction jammed')
        for t in Q.tris[n0:]: built[D.dkey(t)]=s
        if kind=='guess': guesses.append((s,list(Q.tris[n0:])))
        snapshots[s]=list(Q.tris)
    return dict(new=Q.tris[len(base):],built=built,snapshots=snapshots,guesses=guesses)

def reconstruct():
    sel=json.loads((RES/'selection.json').read_text())
    saved=json.loads((ROOT/'settled_test/results/results.json').read_text())
    print('Reconstructing overview prefix',sel,flush=True)
    base,cs=prefix(CD,sel['world'],sel['slice'],sel['key'])
    stream=CD.SEED0*1000+int(sel['key'],16)%(2**31)
    tr=[trace(base,c,stream) for c in cs]
    changed=CD.strip(tr[0]['new'],tr[1]['new'])
    W=json.loads((ROOT/'cut_direction/results/worlds.json').read_text())
    rec=next(c for w in W for c in w['choices'] if c['key']==sel['key'])
    rank=Sl.rank_of(base); cm=Sl.constraints(base,rank)
    cms=[CD.after_first(base,c,rank) for c in cs]
    line=CD.SH.cut_line(cm,*cms)
    angle=ST.line_angle(line[0]); tiles=changed[0]+changed[1]
    shares=[sum(j in CD.families(t) for t in tiles)/len(tiles) for j in range(5)]
    pts=np.array([CD.cen(t)/S for t in tiles]); X=np.c_[pts.real-pts.real.mean(),pts.imag-pts.imag.mean()]
    w,v=np.linalg.eigh(X.T@X/len(pts)); axis=float(np.degrees(np.arctan2(v[1,-1],v[0,-1]))%180)
    ratio=float(np.sqrt(w[-1]/max(w[0],1e-12)))
    u=complex(*v[:,-1]); zc=CD.cen(cs[0])
    built=[(abs(((CD.cen(t)-zc)*u.conjugate()).real)/S,tr[i]['built'][D.dkey(t)]) for i in range(2) for t in changed[i]]
    assert len(tiles)==rec['n_strip']
    assert np.allclose(shares,rec['shares'],rtol=0,atol=1e-12)
    assert np.isclose(angle,rec['line_angle'],atol=1e-9)
    assert np.isclose(axis,rec['axis'],atol=1e-9) and np.isclose(ratio,rec['ratio'],atol=1e-9)
    assert np.allclose(built,rec['built'],atol=1e-9)
    bursts=[ST.burst(base,c) for c in cs]
    bc=CD.strip(bursts[0][0],bursts[1][0]); j=ST.predicted_family(angle)
    core=[ST.core(t,j) for t in bc]
    diagnostics=[dict(changed=len(t),core=len(k),predicted_family=sum(j in CD.families(x) for x in t),core_family=sum(D.dkey(x) in k and j in CD.families(x) for x in t)) for t,k in zip(bc,core)]
    overview=dict(base=base,cs=cs,tr=tr,changed=changed,cm=cm,cms=cms,line=line,bursts=bursts,bc=bc,core=core,selection=sel,j=j)
    print('Overview matches saved size, shares, angle, axis, ratio and placement pairs.',flush=True)
    key='180fb0b920bb845b'; meta=saved['meta'][key]
    print('Reconstructing exception prefix',meta,flush=True)
    eb,ec=prefix(ST,meta['world'],meta['slice'],key)
    rank=Sl.rank_of(eb); line=CD.SH.cut_line(Sl.constraints(eb,rank),*[CD.after_first(eb,c,rank) for c in ec])
    angle=ST.line_angle(line[0]); assert np.isclose(angle,meta['angle'])
    actual=ST.situation((key,eb,ec,angle)); expected=next(r for r in saved['situations'] if r['key']==key)
    assert actual==expected, 'Exception result differs from deposited summary'
    streams=[ST.SEED0*1000+int(key,16)%(2**31)+7919*i for i in range(5)]
    et=[trace(eb,ec[1],s) for s in streams]
    pair=next((i,k) for i in range(5) for k in range(i+1,5) if actual['dom_cont'][i]!=actual['dom_cont'][k] and {D.dkey(t) for t in et[i]['new']}!={D.dkey(t) for t in et[k]['new']})
    exception=dict(base=eb,cs=ec,tr=et,pair=pair,result=actual,meta=meta,streams=streams)
    provenance=dict(base_commit='d4e00c5d4396c38bd69b265907b5f3d6c5bc030a',overview_checks='Matched configuration key, changed count, family shares, cut angle, PCA axis and ratio, and all placement-time pairs.',overview_stream=stream,overview_world_seed=CD.SEED0+sel['world'],core_diagnostics=diagnostics,exception_checks='Full reconstructed situation dictionary equals saved dictionary.',exception_world_seed=ST.SEED0+meta['world'],exception_streams=streams,exception_pair=list(pair),exception_later_guesses=[{'continuation':i,'slices':[s for s,t in et[i]['guesses']]} for i in pair],versions=dict(python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__),scope='Two world prefixes; selected branch continuations and bursts only. No full study rerun.')
    (RES/'reconstruction.json').write_text(json.dumps(provenance,indent=2)+'\n')
    with (RES/'geometry.pkl').open('wb') as f: pickle.dump((overview,exception),f)
    print('Exception matches every deposited field.',flush=True)
    return overview,exception

def polygons(ts,origin):
    return [[((z-origin).real/S,(z-origin).imag/S) for z in t[1:]] for t in ts]
def draw(ax,ts,origin,color,edge=EDGE,lw=.3,alpha=1):
    if ts: ax.add_collection(PolyCollection(polygons(ts,origin),facecolors=color,edgecolors=edge,linewidths=lw,alpha=alpha))
def border(ax,base,origin):
    lines=[[((z-origin).real/S,(z-origin).imag/S) for z in e[:2]] for e in L.Patch(base).frontier()]
    ax.add_collection(LineCollection(lines,colors='#28383f',linewidths=.8))
def setup(ax,tiles,origin):
    p=np.array([q for t in polygons(tiles,origin) for q in t]); lo=p.min(0)-.8; hi=p.max(0)+.8
    ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),aspect='equal'); ax.axis('off')
def save(fig,name):
    for ext in ('svg','png'): fig.savefig(OUT/f'{name}.{ext}',dpi=300,facecolor='white',bbox_inches='tight')
    svg=OUT/f'{name}.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    plt.close(fig)

def overview_plot(o):
    base=o['base']; origin=CD.cen(o['cs'][0]); alltiles=base+o['tr'][0]['new']+o['tr'][1]['new']
    fig,axs=plt.subplots(2,2,figsize=(8.3,10.2))
    fig.suptitle('One local choice,\ntwo growing consequences',fontsize=19,y=.98)
    ax=axs[0,0]; draw(ax,base,origin,GRAY); border(ax,base,origin)
    for c,col in zip(o['cs'],(A,B)): draw(ax,[c],origin,col,edge=col,lw=2,alpha=.7)
    setup(ax,base+o['cs'],origin); ax.set_title('a  The common patch')
    ax.plot(0,0,'o',mfc='none',mec='#172d39',ms=14,lw=1)
    for i,(c,col) in enumerate(zip(o['cs'],(A,B))):
        inset=ax.inset_axes([.02+i*.25,.74,.23,.23])
        draw(inset,base,origin,GRAY); draw(inset,[c],origin,col,edge='#24343c',lw=.8)
        inset.set(xlim=(-1.3,1.3),ylim=(-1.3,1.3),aspect='equal',xticks=[],yticks=[])
        inset.set_title('Option '+ 'AB'[i],fontsize=8,pad=2)
        for spine in inset.spines.values(): spine.set_color('#929da3')
    for i,(col,label) in enumerate(zip((A,B),('A','B'))):
        ax=axs[1,i]; draw(ax,base,origin,GRAY)
        ax.add_collection(PolyCollection(polygons(o['tr'][i]['new'],origin),facecolors='#fff8e3',edgecolors='#ae945e',linewidths=.35,hatch='///'))
        draw(ax,o['changed'][i],origin,col); border(ax,base,origin); setup(ax,alltiles,origin)
        ax.set_title(f'{chr(99+i)}  Branch {label}, after 20 slices')
    ax=axs[0,1]
    for cm,col in [(o['cm'],GRAY),(o['cms'][0],A),(o['cms'][1],B)]:
        ax.add_patch(Polygon(Sl.region(cm),facecolor=col,edgecolor='#36464d',alpha=.65,lw=1))
    p=np.array(Sl.region(o['cm'])); lo=p.min(0); hi=p.max(0); pad=max(hi-lo)*.15
    ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(lo[1]-pad,hi[1]+pad),aspect='equal')
    n,c=o['line']; center=np.mean(p,axis=0); foot=center+(c-np.dot(n,center))*np.array(n)/np.dot(n,n); d=np.array([-n[1],n[0]])
    ax.plot(*np.array([foot-10*d,foot+10*d]).T,'--',color='#172d39',lw=1.2)
    for cm,label in zip(o['cms'],('A','B')):
        center=np.mean(np.unique(np.round(Sl.region(cm),10),axis=0),axis=0)
        ax.text(*center,'Compatible\nwith '+label,ha='center',va='center',fontsize=8,color='#142630')
    ax.tick_params(labelsize=8); ax.set_title('b  Remaining possibilities, F\nafter the first forced slice')
    ax.set_xlabel('Internal coordinate 1'); ax.set_ylabel('Internal coordinate 2')
    fig.legend(handles=[Patch(facecolor=GRAY,label='Already built'),Patch(facecolor='#fff8e3',edgecolor='#ae945e',hatch='///',label='Other new additions'),Patch(facecolor=A,label='A: differing tiles'),Patch(facecolor=B,label='B: differing tiles')],loc='lower center',ncol=2,fontsize=9,bbox_to_anchor=(.5,.04))
    fig.text(.07,.025,'Dark outline: original boundary. Hatching: outside the measured difference.',fontsize=8)
    fig.subplots_adjust(left=.07,right=.97,bottom=.11,top=.86,wspace=.30,hspace=.22)
    save(fig,'01_choice_overview')

def construction_plot(o):
    base=o['base']; origin=CD.cen(o['cs'][0])
    fig,axs=plt.subplots(1,3,figsize=(12,4.8))
    fig.suptitle('Building the response, one slice at a time',fontsize=17)
    changed={D.dkey(t) for t in o['changed'][0]}
    for ax,s in zip(axs,(1,8,20)):
        ts=o['tr'][0]['snapshots'][s]; new=ts[len(base):]
        draw(ax,base,origin,GRAY)
        if new: ax.add_collection(PolyCollection(polygons(new,origin),facecolors='#fff8e3',edgecolors='#ae945e',linewidths=.35,hatch='///'))
        draw(ax,[t for t in new if D.dkey(t) in changed],origin,A)
        border(ax,base,origin); setup(ax,base+o['tr'][0]['new'],origin)
        ax.set_title(f'Branch A, slice {s}')
        if s<=8: assert not [g for g in o['tr'][0]['guesses'] if g[0]<=s]
    fig.legend(handles=[Patch(facecolor=GRAY,label='Already built'),Patch(facecolor='#fff8e3',edgecolor='#ae945e',hatch='///',label='Other new additions'),Patch(facecolor=A,label='Built part of the slice-20 difference')],loc='lower center',ncol=3,fontsize=9,bbox_to_anchor=(.5,.045))
    fig.text(.06,.02,'Blue has the same meaning at every time: membership in the measured slice-20 difference. No unbuilt tiles are shown.',fontsize=9)
    fig.subplots_adjust(left=.03,right=.98,top=.83,bottom=.20,wspace=.12)
    save(fig,'04_construction_over_time')

def evidence_plot(o):
    W=json.loads((ROOT/'cut_direction/results/worlds.json').read_text()); first={}
    for w in W:
        for c in w['choices']: first.setdefault(c['key'],c)
    fig,axs=plt.subplots(1,3,figsize=(14,4.8)); fig.suptitle('Orientation across the sample; a connected core in one reconstructed case',fontsize=15)
    colors=['#a07a00','#287aa6','#23845f','#a74376','#7356a6']; ax=axs[0]
    x=np.linspace(0,180,500)
    for k in range(-1,3): ax.plot(x,108-2*x+180*k,':',color='#888888',lw=.8)
    for c in first.values():
        ax.scatter(c['line_angle'],c['axis'],color=colors[int(np.argmax(c['shares']))],marker='o' if c['ratio']>=3 else 'x',s=32,alpha=.8)
    ax.set(xlim=(0,180),ylim=(-4,184),xlabel='Cut-line direction (degrees)',ylabel='Changed-region axis (degrees)',title='a  45 configurations; points can overlap')
    ax.legend(handles=[Patch(facecolor=colors[j],label=f'Family {j}') for j in range(5)],fontsize=7,loc='upper left',bbox_to_anchor=(0,-.23),ncol=3,frameon=False)
    origin=CD.cen(o['cs'][0])
    for i,ax in enumerate(axs[1:]):
        draw(ax,o['bc'][i],origin,A if i==0 else B)
        draw(ax,[t for t in o['bc'][i] if D.dkey(t) in o['core'][i]],origin,'none',edge='#182a32',lw=1.5)
        setup(ax,o['bc'][0]+o['bc'][1],origin)
        ax.set_title(f'{chr(98+i)}  Branch {"AB"[i]}: initial forced response\nCore {len(o["core"][i])}/{len(o["bc"][i])} changed half-tiles')
    fig.text(.05,.035,'Circles: 41 elongated regions. Crosses: 4 rounder regions. Dotted line: orientation rule (see caption).\nDark outlines in b/c mark the connected core; fill colours continue to identify the branch.',fontsize=9)
    fig.subplots_adjust(bottom=.31,top=.80,wspace=.35)
    save(fig,'02_orientation_and_core')

def exception_plot(e):
    i,k=e['pair']; origin=CD.cen(e['cs'][1]); base=e['base']; a,b=e['tr'][i],e['tr'][k]
    ka={D.dkey(t) for t in a['new']}; kb={D.dkey(t) for t in b['new']}
    da=[t for t in a['new'] if D.dkey(t) not in kb]; db=[t for t in b['new'] if D.dkey(t) not in ka]
    fig,axs=plt.subplots(1,3,figsize=(13,5.5)); fig.suptitle('The same first choice can lead to different later outcomes',fontsize=16)
    for ax,tr,label,changed in zip(axs[:2],(a,b),(i,k),(da,db)):
        draw(ax,base,origin,GRAY); draw(ax,tr['new'],origin,'#edf0f1'); draw(ax,changed,origin,B)
        for s,ts in tr['guesses']:
            draw(ax,ts,origin,'#fff8e3',edge='#182a32',lw=2)
            z=CD.cen(ts[0]); xy=((z-origin).real/S,(z-origin).imag/S)
            ax.annotate(f'Later choice\nat slice {s}',xy=xy,xytext=(xy[0]-5,xy[1]+4),fontsize=9,arrowprops={'arrowstyle':'->'})
        border(ax,base,origin); setup(ax,base+a['new']+b['new'],origin)
        ax.set_title(f'Branch B, continuation {label+1}')
    ax=axs[2]; draw(ax,da,origin,'none',edge=A,lw=1.3); draw(ax,db,origin,'none',edge=B,lw=1.3)
    setup(ax,da+db,origin); ax.set_title('Difference between these B continuations\nOutlines show nonidentical tiles')
    ax.legend(handles=[Patch(facecolor='none',edgecolor=A,label=f'B continuation {i+1}'),Patch(facecolor='none',edgecolor=B,label=f'B continuation {k+1}')],loc='lower left',fontsize=8,frameon=False)
    fig.text(.045,.055,'Both start from the same B option. The marked later choice changes some subsequent details.\nOrange marks nonidentical tiles; the differences include unequal coverage as well as replacements.',fontsize=9)
    fig.subplots_adjust(bottom=.23,top=.80,wspace=.15)
    save(fig,'03_later_choice_exception')

if __name__=='__main__':
    if '--plot-only' in sys.argv:
        with (RES/'geometry.pkl').open('rb') as f: o,e=pickle.load(f)
    else: o,e=reconstruct()
    overview_plot(o); construction_plot(o); evidence_plot(o); exception_plot(e)
    print('Saved four SVG/PNG figure pairs.',flush=True)
