"""Align the AB cuts by exact parent-lattice lifts, not q/check numbering."""
import collections,itertools,json,math
import prepare
ROOT=prepare.ROOT;R=ROOT/'results'
def records(name):
    d=json.loads(prepare.patch_path(name).read_text());vs={v['id']:v for v in d['vertices']}
    lift=lambda v:tuple(vs[v]['lift'])
    ek=lambda e:tuple(sorted(lift(v) for v in e['vertices']))
    fk=lambda f:tuple(sorted(lift(v) for v in f['vertices']))
    boundary={i:a['label'] for a in d['arcs'] for i in a['edges']}
    faces={fk(f):f for f in d['faces']};edges={ek(e):dict(e,boundary=boundary.get(e['id'],'interior')) for e in d['edges']}
    byq={e['qubit']:key for key,e in edges.items() if e['qubit'] is not None}
    adj=collections.defaultdict(set)
    for u,v in edges:adj[u].add(v);adj[v].add(u)
    named={f['zcheck']:key for key,f in faces.items()}
    info={}
    for c in ('Z3','Z6'):
        key=named[c];f=faces[key];support=sorted(e['qubit'] for k,e in edges.items() if set(k)<=set(key) and e['qubit'] is not None)
        fedges=[(k,e) for k,e in edges.items() if set(k)<=set(key)]
        neighbours=sorted(other['zcheck'] for key2,other in faces.items() if key2!=key and any(set(k)<=set(key2) for k,e in fedges))
        info[c]=dict(face_id=f['id'],physical_vertices=key,xy=[vs[v]['xy'] for v in f['vertices']],data_support=support,
            physical_data_edges=[byq[q] for q in support],neighbours=neighbours,
            boundary_edges=[dict(edge=e['id'],qubit=e['qubit'],kind=e['boundary'],physical_edge=k) for k,e in fedges if e['boundary']!='interior'],
            corner_graph_degrees=sorted(len(adj[v]) for v in key))
    n=d['n'];hx=d['HX'];hz=d['HZ'];basis=prepare.E.gs._basis([sum(int(b)<<q for q,b in enumerate(row)) for row in hx])
    supports=[]
    for w in range(1,4):
        found=[]
        for qs in itertools.combinations(range(n),w):
            mask=sum(1<<q for q in qs)
            if all(sum(row[q] for q in qs)%2==0 for row in hz) and not prepare.E.gs._in_span(mask,basis):found.append(qs)
        if found:
            assert w==3
            loss=next(e for e in d['edges'] if e['id']==14)
            supports=[dict(qubits=list(qs),edges=[edges[byq[q]]['id'] for q in qs],physical_edges=sorted(byq[q] for q in qs)) for qs in found if loss['qubit'] in qs]
            break
    loss=next(e for e in d['edges'] if e['id']==14)
    out=dict(name=name,n=n,nx=len(hx),nz=len(hz),faces=len(faces),vertices=len(vs),edges=len(edges),
        loss=dict(edge=14,qubit=loss['qubit'],physical_edge=ek(loss),xy=[vs[v]['xy'] for v in loss['vertices']],
                  endpoint_checks=[vs[v]['xcheck'] for v in loss['vertices']]),
        incident_faces=info,shortest_X_through_loss=supports,scored_logical_Z=d['logical_Z'],
        scored_logical_Z_physical=[byq[q] for q in d['logical_Z']])
    return d,vs,faces,edges,out

def main():
    old,ov,of,oe,a=records('AB_1');new,nv,nf,ne,b=records('AB_bal')
    xyold={tuple(v['lift']):v['xy'] for v in ov.values()};xynew={tuple(v['lift']):v['xy'] for v in nv.values()}
    assert all(math.dist(xyold[k],xynew[k])<1e-12 for k in xyold.keys()&xynew.keys())
    added=set(nf)-set(of);removed=set(of)-set(nf)
    assert a['loss']['physical_edge']==b['loss']['physical_edge']
    changes=[];renumber=[]
    for k in sorted(set(oe)&set(ne)):
        x,y=oe[k],ne[k]
        if x['boundary']!=y['boundary']:changes.append(dict(physical_edge=k,old_edge=x['id'],new_edge=y['id'],old_q=x['qubit'],new_q=y['qubit'],before=x['boundary'],after=y['boundary']))
        if x['id']!=y['id'] or x['qubit']!=y['qubit']:renumber.append(dict(physical_edge=k,old_edge=x['id'],new_edge=y['id'],old_q=x['qubit'],new_q=y['qubit']))
    added_info=[]
    for k in sorted(added):
        f=nf[k];adjacent=[]
        for c,info in b['incident_faces'].items():
            face_vertices=set(map(tuple,info['physical_vertices']))
            shared=[e for e in ne if set(e)<=set(k)&face_vertices]
            if shared:adjacent.append(dict(check=c,shared_physical_edges=shared))
        neighbours=sorted(other['zcheck'] for k2,other in nf.items() if k2!=k and any(set(e)<=set(k)&set(k2) for e in ne))
        contacts={c:sorted(set(k)&set(map(tuple,info['physical_vertices']))) for c,info in b['incident_faces'].items()}
        added_info.append(dict(face_id=f['id'],check=f['zcheck'],physical_vertices=k,xy=[nv[v]['xy'] for v in f['vertices']],all_face_neighbours=neighbours,incident_faces_touched_by_edge=adjacent,incident_vertex_contacts=contacts))
    face_changes=[]
    def neighbours(k,faces,edges):
        return {k2 for k2 in faces if k2!=k and any(set(e)<=set(k)&set(k2) for e in edges)}
    for k in sorted(set(of)&set(nf)):
        x,y=of[k],nf[k];bn=neighbours(k,of,oe);an=neighbours(k,nf,ne)
        bs={e for e,v in oe.items() if set(e)<=set(k) and v['qubit'] is not None}
        ass={e for e,v in ne.items() if set(e)<=set(k) and v['qubit'] is not None}
        if x['zcheck']!=y['zcheck'] or bn!=an or bs!=ass:
            face_changes.append(dict(physical_vertices=k,old_check=x['zcheck'],new_check=y['zcheck'],
                old_neighbours=sorted(of[z]['zcheck'] for z in bn),new_neighbours=sorted(nf[z]['zcheck'] for z in an),
                physical_neighbours_changed=bn!=an,old_data_weight=len(bs),new_data_weight=len(ass),
                physical_data_support_changed=bs!=ass))
    vertex_changes=[]
    vbefore={tuple(v['lift']):v for v in ov.values()};vafter={tuple(v['lift']):v for v in nv.values()}
    for k in sorted(set(vbefore)&set(vafter)):
        x,y=vbefore[k],vafter[k]
        if (x['rough'],x['xcheck'])!=(y['rough'],y['xcheck']):vertex_changes.append(dict(lift=k,old_id=x['id'],new_id=y['id'],old_rough=x['rough'],new_rough=y['rough'],old_check=x['xcheck'],new_check=y['xcheck']))
    canon=lambda s:json.dumps(s['physical_edges'],sort_keys=True)
    sx={canon(s) for s in a['shortest_X_through_loss']};sy={canon(s) for s in b['shortest_X_through_loss']}
    result=dict(identity='exact integer parent-lattice lift tuples; common projected coordinates agree within 1e-12',
        same_lost_physical_edge=True,old=a,new=b,added_tiles=added_info,removed_tiles=[of[k] for k in removed],
        exactly_one_added_tile=len(added)==1 and not removed,boundary_assignment_changes=changes,
        edge_qubit_renumbering=renumber,vertex_boundary_or_check_changes=vertex_changes,common_face_changes=face_changes,
        logical_support_comparison=dict(common=len(sx&sy),old_only=len(sx-sy),new_only=len(sy-sx)))
    (R/'geometry_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    draw(old,new,added_info)
    print('GEOMETRY AUDIT',json.dumps(dict(same_edge=True,exactly_one_added_tile=result['exactly_one_added_tile'],boundary_changes=len(changes),logical_supports=result['logical_support_comparison'])))

def draw(old,new,added):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon,Circle
    plt.rcParams['svg.hashsalt']='paired-face-one-tile'
    fig,axes=plt.subplots(1,2,figsize=(10,5.4));allxy=[v['xy'] for d in (old,new) for v in d['vertices']]
    for ax,d,title in zip(axes,(old,new),('AB_1: e14 → q10','AB_bal: same e14 → q9')):
        vs={v['id']:v for v in d['vertices']};xy=lambda ids:[vs[i]['xy'] for i in ids]
        for f in d['faces']:
            added_here=any(f['zcheck']==a['check'] for a in added) and d is new
            color='#bfe6c5' if added_here else '#d2dfee' if f['zcheck']=='Z3' else '#f6d7b0' if f['zcheck']=='Z6' else '#f3f3f3'
            ax.add_patch(Polygon(xy(f['vertices']),fc=color,ec='none'))
            if f['zcheck'] in ('Z3','Z6') or added_here:
                pts=xy(f['vertices']);at=[sum(p[j] for p in pts)/len(pts) for j in (0,1)]
                ax.text(*at,('added '+f['zcheck']) if added_here else ('A: Z3' if f['zcheck']=='Z3' else 'B: Z6'),ha='center',va='center',fontsize=10,bbox=dict(fc='white',ec='none',alpha=.7))
        boundary={i:a['label'] for a in d['arcs'] for i in a['edges']}
        for e in d['edges']:
            pts=xy(e['vertices']);typ=boundary.get(e['id'],'interior')
            ax.plot([p[0] for p in pts],[p[1] for p in pts],lw=2 if typ!='interior' else 1,color='#7051a0' if typ=='rough' else '#555',ls='--' if typ=='rough' else '-')
        e=next(e for e in d['edges'] if e['id']==14);pts=xy(e['vertices']);at=[sum(p[j] for p in pts)/2 for j in (0,1)]
        ax.plot([p[0] for p in pts],[p[1] for p in pts],lw=4,color='#cc2537');ax.add_patch(Circle(at,.18,fill=False,ec='#cc2537',lw=2))
        ax.set_xlim(min(p[0] for p in allxy)-.4,max(p[0] for p in allxy)+.4);ax.set_ylim(min(p[1] for p in allxy)-.4,max(p[1] for p in allxy)+.4)
        ax.set_aspect('equal');ax.axis('off');ax.set_title(title)
    fig.suptitle('Same physical loss edge, one added tile — plus boundary changes',fontsize=13)
    fig.text(.5,.03,'A = Z3 (blue) · B = Z6 (orange) · added tile (green)\nDashed purple: rough boundary · solid outer edges: smooth boundary · red: shared loss edge',ha='center',fontsize=10)
    fig.subplots_adjust(bottom=.18,top=.87,wspace=.12)
    fig.savefig(R/'one_tile_comparison.png',dpi=180);p=R/'one_tile_comparison.svg';fig.savefig(p,metadata={'Date':None});plt.close(fig)
    p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
if __name__=='__main__':main()
