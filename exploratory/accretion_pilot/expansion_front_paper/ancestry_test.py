"""Backward support graph, single-omission sensitivity, and paired choice-29 replay."""
import json,pickle,random
from pathlib import Path
import figures as F
import choice_tracking as C
import exposure_test as E
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent; O=H/'ancestry-test'; O.mkdir(exist_ok=True)
L,D=F.L,F.D
def main():
    _,e=pickle.loads((H/'results/geometry.pkl').read_bytes())
    frames=pickle.loads((H/'choice-tracking/replay.pkl').read_bytes())[0]
    inv=json.loads((H/'choice-tracking/inventory.json').read_text())[0]
    exposure=json.loads((H/'exposure-test/measurements.json').read_text())[0]
    tiles={repr(D.dkey(t)):t for t in frames[-1]['tiles']}
    births={repr(D.dkey(t)):fr['slice'] for fr in frames for t in fr['new']}
    kinds={r['slice']:r['kind'] for r in inv['records']}
    nodes={}; links=[]
    def walk(k):
        if k in nodes: return
        s=births.get(k,0); nodes[k]=dict(birth=s,kind=kinds.get(s,'earlier'))
        if s==0 or kinds[s]=='guess': return
        P=L.Patch(frames[s-2]['tiles']) if s>1 else L.Patch(e['base']+[e['cs'][1]])
        for ed in P.frontier():
            cs=D.candidates(P,*ed[:3])
            if len(cs)==1 and repr(D.dkey(cs[0]))==k:
                parent=repr(D.dkey(ed[3])); links.append(dict(parent=parent,child=k,edge=C.ek(ed))); walk(parent)
    root=exposure['parent']; walk(root)
    print('Support graph',len(nodes),'nodes',flush=True)
    # Fixed-edge sensitivity: retain the attaching tile; omit each other tile separately.
    before=frames[41]['tiles']; P=L.Patch(before)
    ed=next(ed for ed in P.frontier() if C.ek(ed)==exposure['forced_certificates'][0]); support=repr(D.dkey(ed[3]))
    sensitive=[]
    for t in before:
        k=repr(D.dkey(t))
        if k==support: continue
        Q=L.Patch([u for u in before if D.dkey(u)!=D.dkey(t)])
        cs=D.candidates(Q,*ed[:3]); opts=[repr(D.dkey(u)) for u in cs]
        if set(opts)!={root}: sensitive.append(dict(omitted=k,birth=births.get(k,0),options=opts))
    print('Sensitive omissions',len(sensitive),flush=True)
    # Replay to 28 using original stream; swap only the draw at 29, preserving RNG advancement.
    Q=L.Patch(e['base']); Q.add(e['cs'][1]); rng=random.Random(e['streams'][0])
    for s in range(1,29):
        status,_,_=F.SN.patient(Q,rng); assert status=='ok'; assert C.keys(Q.tris)==C.keys(frames[s-1]['tiles'])
    fr=Q.frontier(); cs=F.SN.ordered(D.candidates(Q,*fr[0][:3])); chosen=rng.choice(cs)
    assert len(cs)==2 and D.dkey(chosen)==D.dkey(frames[28]['new'][0])
    other=next(t for t in cs if D.dkey(t)!=D.dkey(chosen)); Q.add(other)
    target=next(x for x in inv['events'] if x['slice']==44)['site']
    alt=[]; snapshots={29:list(Q.tris)}
    for s in range(30,61):
        st=E.state(Q.tris,target); n=len(Q.tris); status,placed,kind=F.SN.patient(Q,rng)
        alt.append(dict(slice=s,target_before=st,status=status,kind=kind,placed=placed,exposing_tile_present=root in {repr(D.dkey(t)) for t in Q.tris}))
        snapshots[s]=list(Q.tris)
        if status=='JAM': break
    result=dict(scope='Two-history paired replay through 60, plus geometric support graph and fixed-edge single omissions.',support_nodes=nodes,support_links=links,sensitive_omissions=sensitive,omission_tested=len(before)-1,alternative_replay=alt,shared_prefix_verified_through=28,rng_draw_consumed_at_29=True)
    (O/'measurements.json').write_text(json.dumps(result,indent=2))
    with (O/'alternative.pkl').open('wb') as f: pickle.dump(snapshots,f)
    # Support graph uses birth time horizontally; multiple tiles in a slice occupy separate rows.
    grouped={}
    for k,n in nodes.items(): grouped.setdefault(n['birth'],[]).append(k)
    pos={k:(s,j-(len(ks)-1)/2) for s,ks in grouped.items() for j,k in enumerate(ks)}
    fig,ax=plt.subplots(figsize=(12,4.5))
    for link in links:
        x,y=pos[link['parent']]; xx,yy=pos[link['child']]; ax.annotate('',xy=(xx,yy),xytext=(x,y),arrowprops=dict(arrowstyle='->',color='#89949c'))
    for k,(x,y) in pos.items():
        guess=nodes[k]['kind']=='guess'; ax.scatter(x,y,s=130,c='#af3881' if guess else F.A,zorder=3); ax.text(x,y+.18,str(x),ha='center',fontsize=9)
    ax.set(xlabel='Slice when the supporting tile was added (0 = before tracking)',ylim=(-1.2,max([p[1] for p in pos.values()])+1)); ax.set_yticks([])
    ax.set_title('Backward attachment-support map to the exposing tile at slice 43')
    fig.text(.05,.025,'Pink: chosen tile. Blue: forced/earlier tile. Arrows show support on a singleton-candidate edge, not all causal constraints.',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,1)); fig.savefig(O/'support-map.png',dpi=160); plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(10,5)); event=next(x for x in inv['events'] if x['slice']==44); z=complex(*event['xy'])
    for ax,ts,title in zip(axs,[frames[42]['tiles'],snapshots[43]],['Original slice-29 option','Alternative slice-29 option']):
        F.draw(ax,ts,0j,F.GRAY)
        if root in {repr(D.dkey(t)) for t in ts}: F.draw(ax,[tiles[root]],0j,F.A)
        ax.scatter(z.real,z.imag,s=140,facecolors='none',edgecolors='#af3881',linewidths=2)
        st=E.state(ts,target); ax.set_title(title+'\nTarget edge: '+(str(st['count'])+' candidates' if st['frontier'] else 'absent'))
        ax.set(xlim=(z.real-4,z.real+4),ylim=(z.imag-4,z.imag+4),aspect='equal'); ax.axis('off')
    fig.suptitle('Same history through slice 28; inspect after slice 43',fontsize=15); fig.tight_layout(); fig.savefig(O/'paired-replay.png',dpi=160); plt.close(fig)
    print('Done',json.dumps(dict(births=sorted(grouped),sensitive_births=[r['birth'] for r in sensitive],alternative_target_observations=[r for r in alt if r['target_before']['frontier']],final=alt[-1])),flush=True)
if __name__=='__main__': main()
