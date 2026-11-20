"""Geometry only: enumerate logicals and matched archive-check candidates."""
import collections, itertools, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PATCH=ROOT.parent/'aperiodic_predict_2026-11-20/results/Penrose_1.json'
def rank(rows):
    b={}
    for r in rows:
        x=sum(int(v)<<i for i,v in enumerate(r))
        while x:
            k=x.bit_length()-1
            if k in b:x^=b[k]
            else:b[k]=x;break
    return len(b)
def generate():
    obj=json.loads(PATCH.read_text()); n=obj['n']; hx=obj['HX']; hz=obj['HZ']; r=rank(hx)
    target=next(e for e in obj['eligible'] if e['edge']==14); q=target['qubit']
    supports=[]
    for w in range(1,4):
        found=[]
        for inds in itertools.combinations(range(n),w):
            v=[int(i in inds) for i in range(n)]
            if all(sum(a*b for a,b in zip(row,v))%2==0 for row in hz) and rank(hx+[v])>r: found.append(list(inds))
        if found:
            assert w==3
            supports=[s for s in found if q in s]; break
    assert supports
    union=set().union(*map(set,supports))
    checks={f'{t}{i}':{j for j,x in enumerate(row) if x} for t,rows in (('X',hx),('Z',hz)) for i,row in enumerate(rows)}
    adj=collections.defaultdict(set)
    for c,qs in checks.items():
        for j in qs:adj[c].add(f'q{j}');adj[f'q{j}'].add(c)
    dist={f'q{q}':0}; todo=collections.deque(dist)
    while todo:
        a=todo.popleft()
        for b in sorted(adj[a]):
            if b not in dist:dist[b]=dist[a]+1;todo.append(b)
    candidates=[]
    for c,qs in checks.items():
        if c in target['checks']:continue
        hit=sorted(qs&union)
        candidates.append(dict(check=c,type=c[0],weight=len(qs),distance=dist[c],route_qubits=hit,
                               classification='route' if hit else 'comparison',qubits=sorted(qs)))
    pairs=[]
    for a in candidates:
        if a['classification']!='route':continue
        for b in candidates:
            if b['classification']!='comparison' or a['distance']!=b['distance']:continue
            key=(a['type']!=b['type'],abs(a['weight']-b['weight']),a['distance'],a['check'][0],int(a['check'][1:]),b['check'][0],int(b['check'][1:]))
            pairs.append(dict(route=a['check'],comparison=b['check'],ranking=list(key)))
    pairs.sort(key=lambda x:x['ranking'])
    result=dict(starting_sha='fdeaa32a988224f98dc10b99175c99d806862522',patch='Penrose_1',loss_edge=14,loss_qubit=q,
        existing_checks=target['checks'],minimum_X_weight=3,all_minimum_X_supports_containing_loss=supports,route_union=sorted(union),
        candidates=candidates,pairs=pairs,selected=pairs[0] if pairs else None,
        distance_definition='Shortest unweighted path from lost-qubit node to check node in the bipartite retained-check/data-qubit incidence graph, including both X and Z checks.',
        ranking_definition='Require exact distance match; prefer same type, then smallest absolute weight difference, then shorter distance; tie by route type/index then comparison type/index.',
        predicted_direction='route extension minus comparison extension > 0 (tie-aware truth percentage points)',
        scope='one patch, one loss site, deterministic geometry-only matched pair; no population inference')
    (ROOT/'results/prediction.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2)); return obj,result
def draw(obj,res):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    plt.rcParams['svg.hashsalt']='penrose-e14-route-check'
    xy=np.array([v['xy'] for v in obj['vertices']]); edges=obj['edges']; es={e['qubit']:e for e in edges if e['qubit'] is not None}
    selected=res['selected']; route=selected['route']; control=selected['comparison']
    fig,ax=plt.subplots(figsize=(8,7))
    for f in obj['faces']:
        c=f['zcheck']; color='#8ed3c7' if c==route else '#f8ba88' if c==control else '#f1f2f4'
        ax.add_patch(Polygon(xy[f['vertices']],facecolor=color,edgecolor='none'))
    for e in edges:
        ax.plot(*xy[e['vertices']].T,color='#808790',lw=1,zorder=1)
    for arc in obj['arcs']:
        for i in arc['edges']:ax.plot(*xy[edges[i]['vertices']].T,color='#d87521' if arc['label']=='rough' else '#2866b1',lw=2,ls='--' if arc['label']=='rough' else '-')
    for q in res['route_union']:
        e=es[q];ax.plot(*xy[e['vertices']].T,color='#993c9d',lw=5,zorder=3)
        at=xy[e['vertices']].mean(0);ax.text(*at,f'e{e["id"]}/q{q}',fontsize=9,bbox=dict(fc='white',ec='none',alpha=.85),zorder=5)
    loss=es[res['loss_qubit']];ax.plot(*xy[loss['vertices']].T,color='#d32635',lw=6,zorder=4)
    for v in obj['vertices']:
        c=v['xcheck']
        if c not in set(res['existing_checks']+[route,control]):continue
        color='#008579' if c==route else '#c66212' if c==control else '#303640'
        ax.scatter(*xy[v['id']],s=110,facecolor='white',edgecolor=color,lw=2,zorder=6)
        ax.annotate(c,xy[v['id']],xytext=(6,9),textcoords='offset points',color=color,fontweight='bold',bbox=dict(fc='white',ec='none',alpha=.9),zorder=7)
    for f in obj['faces']:
        c=f['zcheck']
        if c not in set(res['existing_checks']+[route,control]):continue
        at=xy[f['vertices']].mean(0);ax.text(*at,c,ha='center',fontsize=12,fontweight='bold',color='#008579' if c==route else '#c66212' if c==control else '#303640',bbox=dict(fc='white',ec='none',alpha=.85),zorder=6)
    ax.set_aspect('equal');ax.axis('off')
    ax.set_title(f'Penrose_1 · loss e14 / q{res["loss_qubit"]}\nRoute-side {route} versus equally distant {control}',fontsize=14)
    fig.text(.5,.04,'Red: lost edge   Purple: union of all shortest X supports through it\nTeal: route-side check   Orange: comparison check\nPrediction: route-side two-reading extension helps more',ha='center',fontsize=10)
    fig.subplots_adjust(bottom=.18,top=.86)
    fig.savefig(ROOT/'results/prediction.png',dpi=180);fig.savefig(ROOT/'results/prediction.svg',metadata={'Date':None});plt.close(fig)
if __name__=='__main__':
    obj,res=generate()
    if res['selected']:draw(obj,res)
