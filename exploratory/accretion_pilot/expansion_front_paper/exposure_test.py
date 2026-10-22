"""Fixed-site exposure tests for choices at 44 and 29; diagnostic subpatches, not new worlds."""
import json,pickle,io,base64
from pathlib import Path
import figures as F
import choice_tracking as C
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent; O=H/'exposure-test'; O.mkdir(exist_ok=True)
L,D=F.L,F.D
def state(ts,site):
    P=L.Patch(ts)
    for ed in P.frontier():
        if C.ek(ed)==site:
            cs=F.SN.ordered(D.candidates(P,*ed[:3]))
            return dict(frontier=True,count=len(cs),options=[repr(D.dkey(t)) for t in cs])
    return dict(frontier=False,count=None,options=[])
def main():
    runs=pickle.loads((H/'choice-tracking/replay.pkl').read_bytes()); report=json.loads((H/'choice-tracking/inventory.json').read_text())
    frames=runs[0]; rows=[]; pictures=[]
    for selected,expose in [(44,43),(29,19)]:
        event=next(e for e in report[0]['events'] if e['slice']==selected); site=event['site']
        before=frames[expose-2]['tiles']; after=frames[expose-1]['tiles']; added=frames[expose-1]['new']
        ed=next(ed for ed in L.Patch(after).frontier() if C.ek(ed)==site)
        edgekey=frozenset((L.key(ed[0]),L.key(ed[1])))
        support=L.Patch(after).edges[edgekey]; assert len(support)==1
        parent=support[0]; assert D.dkey(parent) in C.keys(added)
        P=L.Patch(before); cert=[]
        for ee in P.frontier():
            cs=D.candidates(P,*ee[:3])
            if len(cs)==1 and D.dkey(cs[0])==D.dkey(parent): cert.append(C.ek(ee))
        assert cert and P.legal(parent)
        alone=state(before+[parent],site); full=state(after,site)
        omissions=[]
        for t in added:
            remaining=[x for x in after if D.dkey(x)!=D.dkey(t)]
            st=state(remaining,site)
            omissions.append(dict(omitted_parent=D.dkey(t)==D.dkey(parent),same_as_full=st==full,state=st))
        # Find supporting tiles for the pre-slice singleton certificates, and their birth steps.
        births={D.dkey(t):fr['slice'] for fr in frames for t in fr['new']}
        predecessors=[]
        for ee in P.frontier():
            if C.ek(ee) in cert: predecessors.append(dict(birth_slice=births.get(D.dkey(ee[3]),'before tracking'),tile=repr(D.dkey(ee[3]))))
        row=dict(selected_slice=selected,exposed_during_slice=expose,before=state(before,site),after=full,parent_alone=alone,parent_alone_same_as_full=alone==full,slice_additions=len(added),parent=repr(D.dkey(parent)),forced_certificates=cert,certificate_supports=predecessors,omissions=omissions)
        rows.append(row)
        centre=complex(*event['xy']); fig,axs=plt.subplots(1,3,figsize=(12,4.6))
        for ax,ts,title in zip(axs,[before,before+[parent],after],[f'Before slice {expose}', 'Add only the exposing tile',f'After all of slice {expose}']):
            F.draw(ax,ts,0j,F.GRAY)
            if D.dkey(parent) in C.keys(ts): F.draw(ax,[parent],0j,F.A,edge='#124457',lw=1.2)
            ax.plot([z.real/F.S for z in ed[:2]],[z.imag/F.S for z in ed[:2]],color='#af3881',lw=3,linestyle='--')
            st=state(ts,site); label=str(st['count'])+' alternatives' if st['frontier'] else 'Edge not yet on frontier'
            ax.set_title(title+'\n'+label,fontsize=11); ax.set(xlim=(centre.real-2.4,centre.real+2.4),ylim=(centre.imag-2.4,centre.imag+2.4),aspect='equal'); ax.axis('off')
        fig.suptitle(f'The site selected at slice {selected}: how its edge appears',fontsize=16)
        fig.text(.04,.04,'Pink dashed line: target edge. Blue: the forced tile that exposes it. Middle panel is a diagnostic partial step.',fontsize=10)
        fig.tight_layout(rect=(0,.09,1,.91)); path=O/f'choice-{selected}.png'; fig.savefig(path,dpi=150); plt.close(fig); pictures.append(path)
    (O/'measurements.json').write_text(json.dumps(rows,indent=2))
    html='<meta charset="utf-8"><title>How the choices appear</title><style>body{font:18px system-ui;max-width:1250px;margin:24px auto}img{width:100%}</style><h1>What exposes a new choice?</h1><p>Both sites are exposed by a forced tile. One is selected immediately; the other waits nine slice intervals. These tests concern the specific frontier edge, not all opportunities in its neighbourhood.</p>'
    for p in pictures: html+='<img alt="Three stages of edge exposure" src="data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()+'">'
    (O/'OPEN-EXPOSURE-TEST.html').write_text(html,encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k!='omissions'} for r in rows],indent=2),flush=True)
if __name__=='__main__': main()
