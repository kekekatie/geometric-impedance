"""Exploratory extension: inventory frontier alternatives before every slice.
Fixed horizon 60; same two streams and original patient scheduler. No causal arrows.
Site identity is an undirected frontier edge; sites are not independent choices.
"""
from pathlib import Path
import pickle, random, json, io, base64
import figures as F
import matplotlib.pyplot as plt
from PIL import Image

H=Path(__file__).resolve().parent
OUT=H/'choice-tracking'; OUT.mkdir(exist_ok=True)
L,D,S=F.L,F.D,F.S
def ek(e): return repr(sorted([L.key(e[0]),L.key(e[1])]))
def keys(ts): return {D.dkey(t) for t in ts}
def inventory(Q):
    out=[]
    for edge in Q.frontier():
        cs=F.SN.ordered(D.candidates(Q,*edge[:3])); z=(edge[0]+edge[1])/2
        out.append(dict(site=ek(edge),xy=[z.real/S,z.imag/S],count=len(cs),options=[repr(D.dkey(t)) for t in cs]))
    return out

def main():
    _,e=pickle.loads((H/'results/geometry.pkl').read_bytes())
    runs=[]; report=[]
    for idx in e['pair']:
        Q=L.Patch(list(e['base'])); Q.add(e['cs'][1]); rng=random.Random(e['streams'][idx])
        frames=[]; records=[]; seen={}; events=[]
        for s in range(1,61):
            inv=inventory(Q); lookup={x['site']:x for x in inv}
            for x in inv:
                if x['count']>1: seen.setdefault(x['site'],s)
            n=len(Q.tris); status,placed,kind=F.SN.patient(Q,rng)
            selected=inv[0] if kind=='guess' else None
            row=dict(slice=s,status=status,kind=kind,placed=placed,frontier=inv,selected=selected)
            if selected:
                previous=[r['slice'] for r in records if any(x['site']==selected['site'] and x['count']>1 for x in r['frontier'])]
                event=dict(slice=s,site=selected['site'],xy=selected['xy'],first_observed_open_before_slice=seen[selected['site']],earlier_open_observations=previous,options=selected['options'])
                events.append(event)
            records.append(row); frames.append(dict(slice=s,tiles=list(Q.tris),new=list(Q.tris[n:]),inventory=inv,selected=selected))
            if s<=20: assert keys(Q.tris)==keys(e['tr'][idx]['snapshots'][s])
            print(f'Continuation {idx+1}, slice {s}: {kind}, {placed} placed, {sum(x["count"]>1 for x in inv)} open edges',flush=True)
            if status=='JAM': break
        runs.append(frames); report.append(dict(continuation=idx+1,stream=e['streams'][idx],events=events,records=records))
    (OUT/'inventory.json').write_text(json.dumps(report,indent=2))
    with (OUT/'replay.pkl').open('wb') as f: pickle.dump(runs,f)
    render(e,runs,report)

def render(e,runs,report):
    origin=0j
    A=F.trace(e['base'],e['cs'][0],e['streams'][0])
    old=F.CD.strip(A['snapshots'][11][len(e['base']):],e['tr'][0]['snapshots'][11][len(e['base']):])[1]
    new=e['tr'][0]['snapshots'][16][len(e['tr'][0]['snapshots'][11]):]
    v={L.key(z):z for t in old for z in t[1:]}
    contact=[v[k] for k in {L.key(z) for t in new for z in t[1:]} & set(v)]
    centre=sum(contact)/len(contact)/S
    imgs=[]; encoded=[]
    for s in range(11,min(map(len,runs))+1):
        fig,axs=plt.subplots(2,2,figsize=(12,9))
        for col,(frames,color) in enumerate(zip(runs,(F.A,F.B))):
            fr=frames[s-1]; base=fr['tiles'][:-len(fr['new'])] if fr['new'] else fr['tiles']
            for ax in axs[:,col]:
                F.draw(ax,base,origin,F.GRAY); F.draw(ax,old,origin,'none',edge='#4b555f',lw=.65)
                F.draw(ax,fr['new'],origin,color,edge=color)
                pts=[x['xy'] for x in fr['inventory'] if x['count']>1]
                if pts: ax.scatter(*zip(*pts),s=16,facecolors='none',edgecolors='#af3881',linewidths=.7)
                if fr['selected']: ax.scatter(*fr['selected']['xy'],s=70,c='#af3881',marker='*',zorder=10)
                ax.set_aspect('equal'); ax.axis('off')
            F.setup(axs[0,col],frames[-1]['tiles'],origin)
            axs[1,col].set(xlim=(centre.real-4,centre.real+4),ylim=(centre.imag-4,centre.imag+4))
            r=report[col]['records'][s-1]
            axs[0,col].set_title(f'Continuation {report[col]["continuation"]}: {r["kind"]}; {r["placed"]} new tiles')
            axs[1,col].set_title('Fixed close-up of the slice-15/16 contact')
        fig.suptitle(f'Where are the open choices?  |  Slice {s}',fontsize=18)
        fig.text(.04,.025,'Hollow pink circles: all multi-option frontier edges BEFORE this slice; star: selected choice.\nBlue/orange: tiles added DURING this slice. Dark earlier-region outlines are a historical comparison.\nMultiple edges can describe overlapping alternatives. A circle is not a guaranteed safe future.',fontsize=10)
        fig.subplots_adjust(top=.90,bottom=.13,hspace=.12,wspace=.03)
        b=io.BytesIO(); fig.savefig(b,format='png',dpi=110,facecolor='white'); plt.close(fig)
        raw=b.getvalue(); encoded.append('data:image/png;base64,'+base64.b64encode(raw).decode()); imgs.append(Image.open(io.BytesIO(raw)).convert('RGB'))
    imgs[0].save(OUT/'choice-tracking.gif',save_all=True,append_images=imgs[1:],duration=500,loop=0)
    imgs[-1].save(OUT/'final-frame.png')
    html='''<!doctype html><meta charset="utf-8"><title>Following open choices</title><style>body{max-width:1200px;margin:20px auto;font:18px system-ui;background:#f4f5f6}img{width:100%}input{width:65%}button{font:inherit}</style><h1>Following the choices, slices 11–60</h1><button id="p">Play</button> <input id="s" aria-label="Slice" type="range" min="0" value="0"><span id="l"></span><img id="i" alt="Whole patches and contact close-ups"><p>Circles show locally available alternatives immediately before each slice. Coloured tiles show construction during that slice. Choices at different edges need not be independent.</p><script>const f=FRAMES;let t=null;const s=document.getElementById('s'),p=document.getElementById('p');s.max=f.length-1;function show(){document.getElementById('i').src=f[+s.value];document.getElementById('l').textContent='Slice '+(11+(+s.value))}s.oninput=show;p.onclick=()=>{if(t){clearInterval(t);t=null;p.textContent='Play'}else{t=setInterval(()=>{s.value=(+s.value+1)%f.length;show()},650);p.textContent='Pause'}};show()</script>'''.replace('FRAMES',json.dumps(encoded))
    (OUT/'WATCH-CHOICES.html').write_text(html,encoding='utf-8')
    print(json.dumps([dict(continuation=r['continuation'],events=r['events']) for r in report],indent=2),flush=True)

if __name__=='__main__': main()
