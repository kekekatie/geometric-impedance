"""Exploratory slice-12 replay and film. See SLICE12_PLAN.md before interpreting."""
from pathlib import Path
import json, pickle, base64, io, hashlib
import figures as F
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch, Polygon
from PIL import Image, ImageOps, ImageDraw

HERE=Path(__file__).resolve().parent
OUT=HERE/'slice12'; OUT.mkdir(exist_ok=True)
CD,ST,L,D,Sl,S=F.CD,F.ST,F.L,F.D,F.Sl,F.S
keys=lambda ts:{D.dkey(t) for t in ts}

def main():
    with (HERE/'results/geometry.pkl').open('rb') as f: _,e=pickle.load(f)
    i,k=e['pair']; a,b=e['tr'][i],e['tr'][k]
    assert (i,k)==(0,2)
    for s in range(12): assert keys(a['snapshots'][s])==keys(b['snapshots'][s])
    base=a['snapshots'][11]; Q=L.Patch(base)
    assert all(len(D.candidates(Q,*edge[:3]))>1 for edge in Q.frontier())
    choices=F.SN.ordered(D.candidates(Q,*Q.frontier()[0][:3]))
    assert len(choices)==2
    picks=[tr['guesses'][0][1][0] for tr in (a,b)]
    assert [tr['guesses'][0][0] for tr in (a,b)]==[12,12]
    assert keys(picks)==keys(choices)
    assert D.dkey(picks[0])!=D.dkey(picks[1])
    # Replay both full trajectories from their recorded streams, including all intermediate slices.
    for idx,tr in zip((i,k),(a,b)):
        replay=F.trace(e['base'],e['cs'][1],e['streams'][idx])
        for s in range(21): assert keys(replay['snapshots'][s])==keys(tr['snapshots'][s])
    original_A=F.trace(e['base'],e['cs'][0],e['streams'][i])
    other_A=F.trace(e['base'],e['cs'][0],e['streams'][k])
    assert not original_A['guesses'] and not other_A['guesses']
    for s in range(21): assert keys(original_A['snapshots'][s])==keys(other_A['snapshots'][s])
    oldA,oldB=CD.strip(original_A['snapshots'][11][len(e['base']):],a['snapshots'][11][len(e['base']):])
    rank=Sl.rank_of(base); cm=Sl.constraints(base,rank)
    cms=[CD.after_first(base,c,rank) for c in picks]
    line=CD.SH.cut_line(cm,*cms)
    angle=None if line is None else ST.line_angle(line[0])
    predicted=None if angle is None else ST.predicted_family(angle)
    p0=Sl.region(cm); pieces=[Sl.region(c) for c in cms]
    # Verify the cut measurement matches actual slice 13 (one forced slice after the second choice).
    for tr,c in zip((a,b),cms):
        assert Sl.constraints(tr['snapshots'][13],rank)==c
    verts=lambda ts:{L.key(z) for t in ts for z in t[1:]}
    edges=lambda ts:{frozenset((L.key(p),L.key(q))) for t in ts for p,q in ((t[1],t[2]),(t[2],t[3]),(t[3],t[1]))}
    contact=[dict(shared_vertices=len(verts([c])&verts(oldB)),shared_edges=len(edges([c])&edges(oldB))) for c in picks]
    rows=[]
    for s in range(11,21):
        na=a['snapshots'][s][len(base):]; nb=b['snapshots'][s][len(base):]
        ka,kb=keys(na),keys(nb); da,db=CD.strip(na,nb)
        common=[t for t in na if D.dkey(t) in kb]
        ua=[t for t in na if D.dkey(t) not in kb and D.dkey(t) not in keys(da)]
        ub=[t for t in nb if D.dkey(t) not in ka and D.dkey(t) not in keys(db)]
        rows.append(dict(slice=s,new=[len(na),len(nb)],shared_new=len(common),covered_difference=[len(da),len(db)],unequal_coverage=[len(ua),len(ub)],dominant_second_difference=ST.dominant(da+db)))
        counts=[sum(j in CD.families(t) for t in da+db) for j in range(5)]
        rows[-1]['family_incidence_counts']=counts
        rows[-1]['tied_largest_families']=[j for j,n in enumerate(counts) if n==max(counts)] if da+db else []
        rows[-1]['new_contact_with_old_difference']=[dict(shared_vertices=len(verts(ts)&verts(oldB)),shared_edges=len(edges(ts)&edges(oldB))) for ts in (na,nb)]
        rows[-1]['changed_contact_with_old_difference']=[dict(shared_vertices=len(verts(ts)&verts(oldB)),shared_edges=len(edges(ts)&edges(oldB))) for ts in (da,db)]
    paired=[]
    for tr in (a,b):
        x,y=CD.strip(original_A['new'],tr['new']); paired.append(ST.dominant(x+y))
    assert paired==[2,3]
    data=dict(date='2026-10-21',key=e['result']['key'],continuations_one_based=[i+1,k+1],streams=[e['streams'][i],e['streams'][k]],original_cut_angle=e['meta']['angle'],original_predicted_family=e['result']['j'],second_cut_angle=angle,second_predicted_family=predicted,second_region_areas=[Sl.area(p0)]+[Sl.area(p) for p in pieces],second_piece_fractions=[Sl.area(p)/Sl.area(p0) for p in pieces],same_prechoice_patch=True,no_forced_site_before_second_choice=True,candidate_count=len(choices),replay_verified_all_slices=True,original_A_identical_and_no_later_guesses=True,paired_original_A_vs_B_families=paired,historical_B_difference_at_slice11=len(oldB),choice_contact_with_historical_B_difference=contact,measurements=rows,scope='One previously selected exception; original engine and existing 20-slice horizon. Contact is geometric, not a persistent-object or causal-interaction test.',cache_sha256=hashlib.sha256((HERE/'results/geometry.pkl').read_bytes()).hexdigest())
    (OUT/'measurements.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2),flush=True)
    origin=CD.cen(picks[0]); alltiles=a['snapshots'][20]+b['snapshots'][20]
    images=[]
    for row in rows:
        s=row['slice']; fig,axs=plt.subplots(1,2,figsize=(10,6.6))
        fig.suptitle(f'The same first choice, two later outcomes  |  slice {s}',fontsize=16,y=.96)
        subtitle='One shared patch, immediately before the later choice' if s==11 else ('The two alternatives are placed here' if s==12 else 'Construction after the later choice')
        fig.text(.5,.90,subtitle,ha='center',fontsize=11)
        na=a['snapshots'][s][len(base):]; nb=b['snapshots'][s][len(base):]
        ka,kb=keys(na),keys(nb); ds=CD.strip(na,nb)
        for ax,tr,new,other,changed,col,label in zip(axs,(a,b),(na,nb),(kb,ka),ds,(F.A,F.B),(1,3)):
            F.draw(ax,base,origin,F.GRAY)
            shared=[t for t in new if D.dkey(t) in other]
            unequal=[t for t in new if D.dkey(t) not in other and D.dkey(t) not in keys(changed)]
            F.draw(ax,shared,origin,'#62ae91')
            if unequal: ax.add_collection(PolyCollection(F.polygons(unequal,origin),facecolors='#fff8e3',edgecolors=col,linewidths=.45,hatch='///'))
            F.draw(ax,changed,origin,col)
            # The fixed historical comparison region is already built, not an unbuilt forecast.
            if oldB: ax.add_collection(PolyCollection(F.polygons(oldB,origin),facecolors='none',edgecolors='#45525a',linewidths=.8,linestyles='dashed'))
            if s>=12: F.draw(ax,tr['guesses'][0][1],origin,'none',edge='#13232a',lw=2)
            F.setup(ax,alltiles,origin)
            ax.set_title(f'Original option B, continuation {label}',fontsize=11)
            ix=0 if label==1 else 1
            ax.text(.5,-.02,f'{row["shared_new"]} shared  |  {row["covered_difference"][ix]} differing  |  {row["unequal_coverage"][ix]} outside coverage',transform=ax.transAxes,ha='center',fontsize=9)
        fig.legend(handles=[Patch(facecolor=F.GRAY,label='Built before slice 12'),Patch(facecolor='#62ae91',label='Shared new tiles'),Patch(facecolor=F.A,label='Different tile here (left)'),Patch(facecolor=F.B,label='Different tile here (right)'),Patch(facecolor='#fff8e3',edgecolor='#777',hatch='///',label='Other branch has not covered this place')],loc='lower center',bbox_to_anchor=(.5,.08),ncol=3,fontsize=8)
        fig.text(.06,.035,'Dark outline: later choice tile. Dashed outlines: earlier A/B difference, frozen at slice 11.\nColours compare alternatives; they do not identify two objects travelling in one world.',fontsize=9)
        fig.subplots_adjust(left=.02,right=.98,top=.83,bottom=.23,wspace=.04)
        buf=io.BytesIO(); fig.savefig(buf,format='png',dpi=140,facecolor='white'); plt.close(fig)
        im=Image.open(buf).convert('RGB'); images.append(im.copy())
        im.save(OUT/f'slice_{s:02d}.png')
    images[0].save(OUT/'slice12-film.gif',save_all=True,append_images=images[1:],duration=[1400,1400]+[850]*7+[2000],loop=0,optimize=False)
    # Standalone HTML embeds the frames so it remains usable when moved on its own.
    encoded=[]
    for im in images:
        bfr=io.BytesIO(); im.save(bfr,format='PNG'); encoded.append('data:image/png;base64,'+base64.b64encode(bfr.getvalue()).decode())
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><title>The slice-12 choice</title><style>body{font:17px system-ui;background:#f4f5f6;color:#182a32;margin:20px auto;max-width:1100px}img{width:100%;background:white}button{font:inherit;padding:8px 16px}input{width:65%}.note{line-height:1.5;padding:12px}h1{font-size:25px}</style><h1>The slice-12 choice: watch, pause, or move through time</h1><button id="play">Play</button> <input id="time" type="range" min="0" max="9" value="0" aria-label="Construction slice"><span id="label">Slice 11</span><img id="frame" alt="Two continuations of the same original option B"><p class="note">Both panels have the same history through slice 11. At slice 12 they take different legal alternatives. Green is shared new construction; solid blue/orange marks different tiles at covered places; hatching marks unequal coverage. The dashed earlier comparison region is frozen at slice 11. This is one exploratory example, not a particle or crossing test.</p><script>const frames=FRAMES;const slider=document.getElementById('time'),img=document.getElementById('frame'),label=document.getElementById('label'),button=document.getElementById('play');let timer=null;function show(){img.src=frames[Number(slider.value)];label.textContent='Slice '+(11+Number(slider.value));}slider.oninput=show;button.onclick=()=>{if(timer){clearInterval(timer);timer=null;button.textContent='Play';}else{timer=setInterval(()=>{slider.value=(Number(slider.value)+1)%frames.length;show()},1000);button.textContent='Pause';}};show();</script></html>'''.replace('FRAMES',json.dumps(encoded))
    (OUT/'WATCH-SLICE12.html').write_text(html,encoding='utf-8')
    chosen=[0,1,2,9]; thumbs=[images[n].resize((1000,660)) for n in chosen]
    sheet=Image.new('RGB',(2000,1320),'white')
    for idx,im in enumerate(thumbs): sheet.paste(im,((idx%2)*1000,(idx//2)*660))
    sheet.save(OUT/'four-moments.png')
    fig,axs=plt.subplots(1,2,figsize=(9,4.8)); fig.suptitle('The later choice has its own compatibility cut',fontsize=16)
    original_rank=Sl.rank_of(e['base']); oc=Sl.constraints(e['base'],original_rank); ocs=[CD.after_first(e['base'],c,original_rank) for c in e['cs']]
    for ax,before,after,title in [(axs[0],oc,ocs,f'Original choice: {e["meta"]["angle"]:.0f} degrees; family {e["result"]["j"]}'),(axs[1],cm,cms,f'Slice-12 choice: {angle:.0f} degrees; family {predicted}' if angle is not None else 'Slice-12 choice: no detected cut')]:
        poly=np.array(Sl.region(before)); ax.add_patch(Polygon(poly,fc=F.GRAY,ec='#26353b'))
        for cc,col in zip(after,(F.A,F.B)): ax.add_patch(Polygon(Sl.region(cc),fc=col,ec='#26353b',alpha=.7))
        lo=poly.min(0);hi=poly.max(0);pad=max(hi-lo)*.12
        ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(lo[1]-pad,hi[1]+pad),aspect='equal',title=title,xlabel='Internal coordinate 1',ylabel='Internal coordinate 2')
    fig.text(.05,.03,'Both cuts are measured after their first forced slice. Panels have different scales.\nLeft colours: original A/B. Right colours: B continuations 1/3.',fontsize=9)
    fig.tight_layout(rect=(0,.13,1,.89)); fig.savefig(OUT/'two-cuts.png',dpi=220); fig.savefig(OUT/'two-cuts.svg'); plt.close(fig)
    print('Film, viewer, contact sheet and cut plot saved.',flush=True)

if __name__=='__main__': main()
