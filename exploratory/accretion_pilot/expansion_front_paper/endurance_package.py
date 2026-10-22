import json,ast
from pathlib import Path
H=Path(__file__).resolve().parent; O=H/'endurance'; compact=[]
for case in ['continuation-1','continuation-3','alternative-29']:
    r=json.loads((O/(case+'-observer.json')).read_text()); tile_ids={k:i for i,k in enumerate(r['tiles'])}
    # Vertex IDs use the original coordinate rounding, converted to S units here.
    import figures as F
    point=lambda v:[x/F.S for x in ast.literal_eval(v)]
    tracks=[dict(family=t['family'],cls=t['cls'],hand=r['classes'][t['cls']]['handedness'],born=t['born'],left=t['left_censored'],last=t['last'],lost=t.get('lost_at'),dropped=t.get('fully_dropped_at'),lookalike=t.get('unlinked_lookalike',False),tiles=[tile_ids[k] for k in t['tiles']],events=t['events']) for t in r['tracks']]
    frames=[dict(s=f['slice'],status=f['status'],skin=[tile_ids[k] for k in f['skin']],new=[tile_ids[k] for k in f['new']],frontier=[[point(v) for v in edge] for edge in f['frontier']]) for f in r['snapshots']]
    links=[dict(p=l['parent'],c=l['child'],s=l['slice'],kind=l['type'],w=[tile_ids[k] for k in l['witness']]) for l in r['links']]
    compact.append(dict(case=case,tiles=list(r['tiles'].values()),tracks=tracks,frames=frames,links=links,summary=r['summary']))
page=(H/'endurance_viewer.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(compact,separators=(',',':')))
(O/'WATCH-ENDURANCE.html').write_text(page,encoding='utf-8')
print('Viewer bytes',len(page.encode()))
