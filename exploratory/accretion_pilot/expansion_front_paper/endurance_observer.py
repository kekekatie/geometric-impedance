"""Physical-space, read-only motif observer. See ENDURANCE_PROTOCOL.md."""
from pathlib import Path
import pickle,json,hashlib,math,collections
import figures as F
import active_skin_engine as E
H=Path(__file__).resolve().parent; O=H/'endurance'
L,D,S=F.L,F.D,F.S
vk=lambda z: repr(L.key(z))
eid=lambda a,b: tuple(sorted((vk(a),vk(b))))
digest=lambda x: hashlib.sha256(repr(x).encode()).hexdigest()[:16]

def canonical(ts,edges,centre=None,reflect=False):
    z0=sum(z for t in ts for z in t[1:])/(3*len(ts))
    trans=lambda z: ((z-z0)/S).conjugate() if reflect else (z-z0)/S
    tt=[(t[0],*[trans(z) for z in t[1:]]) for t in ts]
    ee=[tuple(trans(z) for z in e) for e in edges]
    cc=None if centre is None else trans(centre)
    def xy(z): return (round(z.real,5),round(z.imag,5))
    codes=[]
    for t in tt:
        u=(t[2]-t[1])/abs(t[2]-t[1]); rot=u.conjugate()
        codes.append((tuple(sorted((t[0],*(xy(z*rot) for z in t[1:])) for t in tt)),tuple(sorted(tuple(sorted(xy(z*rot) for z in e)) for e in ee)),() if cc is None else xy(cc*rot)))
    return min(codes)

def validation():
    ts=[(0,0j,1+0j,.3+.8j),(1,1+0j,1.6+.4j,.3+.8j)]; es=[(0j,1+0j)]
    base=canonical(ts,es,0j); u=complex(math.cos(.37),math.sin(.37)); shift=7.3-2.1j
    moved=[(t[0],*[z*u+shift for z in t[1:]]) for t in ts]
    assert canonical(moved,[(a*u+shift,b*u+shift) for a,b in es],shift)==base
    assert canonical(list(reversed(ts)),es,0j)==base
    mirror=[(t[0],*[z.conjugate() for z in t[1:]]) for t in ts]
    assert canonical(mirror,[(a.conjugate(),b.conjugate()) for a,b in es],0j)==canonical(ts,es,0j,True)
    changed=[(1-ts[0][0],*ts[0][1:]),ts[1]]
    assert canonical(changed,es,0j)!=base

def discover(fr,cache,classes):
    ts=fr['skin']; td={E.tile_id(t):t for t in ts}; V=collections.defaultdict(list); graph=collections.defaultdict(set); coords={}
    for key,t in td.items():
        for z in t[1:]: V[vk(z)].append(key); coords[vk(z)]=z
        for a,b in ((t[1],t[2]),(t[2],t[3]),(t[3],t[1])): graph[vk(a)].add(vk(b)); graph[vk(b)].add(vk(a))
    fedges={eid(e[0],e[1]):e for e in fr['frontier']}; fv={v for e in fedges for v in e}
    near=set(fv)
    for _ in range(2): near |= {v for k in list(near) for v in graph[k]}
    motifs={}
    def make(family,keys,edges,centre=None):
        raw=(family,tuple(sorted(keys)),tuple(sorted(edges)),centre); key=repr(raw)
        tiles=[td[k] for k in sorted(keys)]; geom=[(coords[a],coords[b]) for a,b in sorted(edges)]
        if key not in cache:
            a=canonical(tiles,geom,None if centre is None else coords[centre]); b=canonical(tiles,geom,None if centre is None else coords[centre],True)
            cl=digest((family,a)); pair=digest((family,min(a,b))); hand='achiral' if a==b else ('+' if a<b else '-')
            cache[key]=(cl,pair,hand)
            classes.setdefault(cl,dict(family=family,mirror_pair=pair,handedness=hand,mirror_class=digest((family,b))))
        cl,pair,hand=cache[key]
        verts={vk(z) for t in tiles for z in t[1:]}
        incident=set(edges) if family.startswith('pocket') else {ed for ed in fedges if centre in ed}
        motifs[key]=dict(key=key,cls=cl,family=family,tiles=set(keys),vertices=verts,incident=incident,centre=centre)
    for v in sorted(near):
        tiles=[td[k] for k in V[v]]; angle=0
        for t in tiles:
            z=coords[v]; others=[p for p in t[1:] if vk(p)!=v]
            u,w=others[0]-z,others[1]-z
            angle+=math.acos(max(-1,min(1,(u.conjugate()*w).real/(abs(u)*abs(w)))))
        complete=abs(angle-2*math.pi)<1e-6
        if v in fv or complete: make('star-complete' if complete else 'star-frontier',V[v],[],v)
    edges=sorted(fedges); adj={i:{j for j in range(len(edges)) if i!=j and set(edges[i])&set(edges[j])} for i in range(len(edges))}
    groups={frozenset([i]) for i in adj}
    for size in [2,3,4]:
        groups={g|{j} for g in groups for i in g for j in adj[i] if j not in g}
        for g in sorted(groups,key=lambda x:tuple(sorted(x))):
            ee=[edges[i] for i in g]; keys={E.tile_id(fedges[ed][3]) for ed in ee}; make('pocket-'+str(size),keys,ee)
    return motifs,graph,td,coords,fedges

def analyse(run):
    cache={}; classes={}; tracks=[]; links=[]; snapshots=[]; previous={}; pending=set(); tile_catalog={}; counts=[]
    prev_graph={}; prev_td={}; previous_slice=None
    for fr in run['frames']:
        s=fr['slice']; current,graph,td,coords,fedges=discover(fr,cache,classes)
        for k,t in td.items(): tile_catalog.setdefault(k,[t[0],*[[z.real/S,z.imag/S] for z in t[1:]]])
        new_tiles={E.tile_id(t):t for t in fr['added']}; new_keys=set(new_tiles); new_vertices={vk(z) for t in fr['added'] for z in t[1:]}
        new_edges={eid(a,b) for t in fr['added'] for a,b in ((t[1],t[2]),(t[2],t[3]),(t[3],t[1]))}
        born=[]; lost=[]
        for key,m in current.items():
            if key in previous: m['id']=previous[key]['id']; tracks[m['id']]['last']=s
            else:
                m['id']=len(tracks); born.append(m)
                tracks.append(dict(id=m['id'],cls=m['cls'],family=m['family'],born=s,last=s,left_censored=s==60,tiles=sorted(m['tiles']),vertices=sorted(m['vertices']),nearby_active_steps=0,direct_active_steps=0,waiting_steps=0,events=[]))
        # Candidate daughters indexed by newly built witness tile's vertices.
        daughter_by_vertex=collections.defaultdict(list)
        for m in born:
            if not m['incident']: continue
            for tile in m['tiles']&new_keys:
                for z in new_tiles[tile][1:]: daughter_by_vertex[vk(z)].append((m,tile))
        linked_daughters=set(); same_linked=set(); step_links=[]
        for key,parent in previous.items():
            if fr['status']=='JAM': continue
            tr=tracks[parent['id']]; direct=bool(parent['incident']&new_edges)
            near=set(parent['vertices'])
            for _ in range(2): near |= {v for k in list(near) for v in prev_graph.get(k,())}
            active=bool(near&new_vertices); tr['nearby_active_steps']+=active; tr['direct_active_steps']+=direct; tr['waiting_steps']+=not direct
            witnesses=collections.defaultdict(set)
            if parent['incident']:
                for v in parent['vertices']:
                    for daughter,tile in daughter_by_vertex.get(v,[]):
                        if parent['family'].split('-')[0]==daughter['family'].split('-')[0]: witnesses[daughter['id']].add(tile)
            same=0
            for child,w in witnesses.items():
                typ='same-class' if tr['cls']==tracks[child]['cls'] else 'transition'
                link=dict(parent=parent['id'],child=child,slice=s,type=typ,witness=sorted(w)); links.append(link); step_links.append(len(links)-1); linked_daughters.add(child)
                if typ=='same-class': same+=1; same_linked.add(child)
            closed=bool(parent['incident']) and not (parent['incident']&set(fedges))
            gone=key not in current
            left_band=gone and parent['family']=='star-complete' and parent['tiles']<=set(td)
            if gone:
                tr['lost_at']=s; pending.add(parent['id']); lost.append(parent['id'])
            tr['events'].append(dict(slice=s,direct=direct,nearby=active,closed=closed,lost=gone,left_observation_band=left_band,same_class_candidates=same,loss_without_same_class_renewal=gone and active and same==0 and not left_band))
        for i in list(pending):
            if not (set(tracks[i]['tiles'])&set(td)):
                tracks[i]['fully_dropped_at']=s; pending.remove(i)
        prev_classes={m['cls'] for m in previous.values()}
        for m in born:
            tracks[m['id']]['unlinked_lookalike']=m['cls'] in prev_classes and m['id'] not in same_linked
        snapshots.append(dict(slice=s,status=fr['status'],skin=list(td),new=list(new_keys),frontier=[list(ed) for ed in fedges],occurrences=[m['id'] for m in current.values()],born=[m['id'] for m in born],lost=lost,links=step_links))
        counts.append(dict(slice=s,motifs=len(current),born=len(born),lost=len(lost),same_links=sum(links[i]['type']=='same-class' for i in step_links),transition_links=sum(links[i]['type']=='transition' for i in step_links)))
        previous=current; prev_graph=graph; prev_td=td; previous_slice=s
        if s%10==0: print(run['case'],s,'motifs',len(current),'tracks',len(tracks),flush=True)
    for m in previous.values(): tracks[m['id']]['right_censored']=True
    # Longest same-class path, ordered by occurrence birth. Links always enter a new occurrence.
    length={t['id']:0 for t in tracks}; pred={}
    for link in sorted((l for l in links if l['type']=='same-class'),key=lambda l:(tracks[l['child']]['born'],l['parent'],l['child'])):
        p,c=link['parent'],link['child']
        if length[p]+1>length[c]: length[c]=length[p]+1; pred[c]=p
    end=max(length,key=lambda k:(length[k],-k)); chain=[end]
    while chain[-1] in pred: chain.append(pred[chain[-1]])
    chain.reverse()
    assert all(tracks[l['child']]['born']>tracks[l['parent']]['born'] and l['witness'] for l in links)
    summary=dict(case=run['case'],last_slice=run['frames'][-1]['slice'],stop=run['frames'][-1]['status'],tracks=len(tracks),classes=len(classes),same_links=sum(l['type']=='same-class' for l in links),transition_links=sum(l['type']=='transition' for l in links),max_candidate_chain_links=length[end],example_chain=chain,unlinked_lookalikes=sum(t.get('unlinked_lookalike',False) for t in tracks),fully_dropped=sum('fully_dropped_at' in t for t in tracks),right_censored=sum(t.get('right_censored',False) for t in tracks))
    return dict(case=run['case'],classes=classes,tracks=tracks,links=links,snapshots=snapshots,tiles=tile_catalog,summary=summary,counts=counts)

def main():
    validation(); runs=pickle.loads((O/'skin-snapshots.pkl').read_bytes()); summaries=[]
    for run in runs:
        result=analyse(run); (O/(run['case']+'-observer.json')).write_text(json.dumps(result,separators=(',',':')))
        summaries.append(result['summary']); print(json.dumps(result['summary']),flush=True)
    (O/'summary.json').write_text(json.dumps(summaries,indent=2))
if __name__=='__main__': main()
