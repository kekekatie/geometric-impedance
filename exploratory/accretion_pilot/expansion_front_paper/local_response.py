from pathlib import Path
import pickle,json,itertools,base64
import figures as F
import choice_tracking as C
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent; O=H/'local-response'; O.mkdir(exist_ok=True)
L,D,S=F.L,F.D,F.S
key=lambda t:repr(D.dkey(t))
def reasons(P,t):
    cen=sum(t[1:])/3
    overlap=[key(u) for u in P.tris if abs(u[1]-cen)<3*L.SCALE_LEN and (L.inside(cen,*u[1:]) or any(L.inside(z,*u[1:]) for z in t[1:]))]
    duplicate=L.canon(t) in {L.canon(u) for u in P.edges.get(frozenset((L.key(t[1]),L.key(t[2]))),[])}
    vertices=[list(k) for k,v in L.corners([t]).items() if not P.vertex_ok(k,v)]
    out=dict(overlaps=overlap,duplicate=duplicate,failing_vertices=vertices)
    assert P.legal(t)==(not overlap and not duplicate and not vertices)
    return out
def main():
    states=pickle.loads((H/'ancestry-test/alternative.pkl').read_bytes()); before,after=states[44],states[45]
    assert before==after[:len(before)]
    added=after[len(before):]; inv=json.loads((H/'choice-tracking/inventory.json').read_text())[0]
    site=next(x for x in inv['events'] if x['slice']==44)['site']; P=L.Patch(before)
    edge=next(e for e in P.frontier() if C.ek(e)==site)
    opts=lambda ts: sorted(key(t) for t in D.candidates(L.Patch(ts),*edge[:3]))
    a=opts(before); b=opts(after); assert len(a)==2 and len(b)==1
    candidates=D.candidates(P,*edge[:3]); rejected=next(t for t in candidates if key(t) not in b); survivor=next(t for t in candidates if key(t) in b)
    assert key(survivor) in {key(t) for t in states[46][len(after):]}
    rows=[]
    for i,t in enumerate(added):
        single=before+[t]; omission=before+added[:i]+added[i+1:]
        rows.append(dict(index=i+1,tile=key(t),legal_alone=P.legal(t),alone=opts(single),without=opts(omission),rejected_reason_alone=reasons(L.Patch(single),rejected)))
    sufficient=[r['index'] for r in rows if r['alone']==b]; pairs=[]
    if not sufficient:
        for i,j in itertools.combinations(range(len(added)),2):
            if opts(before+[added[i],added[j]])==b: pairs.append([i+1,j+1])
    prefixes=[dict(placed=i,options=opts(before+added[:i])) for i in range(len(added)+1)]
    without_all=before+[t for i,t in enumerate(added,1) if i not in sufficient]
    mid=(edge[0]+edge[1])/2; local=lambda ts:[t for t in ts if any(abs(z-mid)<=2*S+1e-12 for z in t[1:])]
    local_tests=[dict(label='before',same=opts(local(before))==a),dict(label='full',same=opts(local(after))==b)]
    local_tests += [dict(label=f'single-{r["index"]}',same=opts(local(before+[added[r['index']-1]]))==r['alone']) for r in rows]
    assert all(r['same'] for r in local_tests)
    data=dict(additions=len(added),before_options=a,after_options=b,sufficient_singletons=sufficient,sufficient_pairs_if_needed=pairs,necessary_single_omissions=[r['index'] for r in rows if r['without']!=b],without_all_sufficient_singletons=opts(without_all),rows=rows,prefixes=prefixes,full_rejection=reasons(L.Patch(after),rejected),local_checks=local_tests,survivor_placed_at_46=True)
    (O/'measurements.json').write_text(json.dumps(data,indent=2))
    example=added[sufficient[0]-1] if sufficient else added[0]
    fig,axs=plt.subplots(1,3,figsize=(12,5)); z=F.CD.cen(rejected)
    for ax,ts,title in zip(axs,[before,before+[example],after],['Before slice 45: two options','One observed addition alone','Full slice 45: one option']):
        F.draw(ax,ts,z,F.GRAY); F.draw(ax,[t for t in ts[len(before):]],z,F.B)
        for t,col in [(rejected,'#9b387f'),(survivor,F.A)]: F.draw(ax,[t],z,'none',edge=col,lw=2)
        ax.set(xlim=(-2.8,2.8),ylim=(-2.5,2.5),aspect='equal',title=title); ax.axis('off')
    fig.suptitle('How neighbouring construction settles an open option',fontsize=16)
    fig.text(.04,.035,'Orange: observed addition(s). Purple outline: option ruled out. Blue outline: surviving option.\nMiddle panel is a diagnostic partial step, not a separate simulated history.',fontsize=10)
    fig.tight_layout(rect=(0,.13,1,.92)); fig.savefig(O/'local-response.png',dpi=160); plt.close(fig)
    print(json.dumps({k:v for k,v in data.items() if k not in ['rows','prefixes','local_checks','full_rejection']},indent=2),flush=True)
    print('Reasons',[(r['index'],r['rejected_reason_alone']) for r in rows if r['index'] in sufficient],flush=True)
if __name__=='__main__': main()
