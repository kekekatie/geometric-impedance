from pathlib import Path
import json,pickle,math,collections,statistics
import endurance_observer as T
import figures as F
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent; O=H/'endurance'
runs=pickle.loads((O/'skin-snapshots.pkl').read_bytes()); report=[]
for run in runs:
    r=json.loads((O/(run['case']+'-observer.json')).read_text()); frames={f['slice']:f for f in run['frames']}; snap={s['slice']:s for s in r['snapshots']}
    for link in r['links']:
        s=link['slice']; p=r['tracks'][link['parent']]; c=r['tracks'][link['child']]
        added={T.E.tile_id(t):t for t in frames[s]['added']}
        assert p['id'] in snap[s-1]['occurrences'] and c['id'] in snap[s]['born']
        assert c['born']==s and bool(link['witness'])
        for w in link['witness']:
            assert w in added and w in c['tiles']
            assert {T.vk(z) for z in added[w][1:]}&set(p['vertices'])
        assert (p['cls']==c['cls'])==(link['type']=='same-class')
    if run['frames'][-1]['status']=='JAM': assert all(not any(e['slice']==70 for e in t['events']) for t in r['tracks'])
    # Exercise classification on actual frontier motifs, not only synthetic fixtures.
    motifs,graph,td,coords,ed=T.discover(run['frames'][0],{},{}); tested=0
    for m in list(motifs.values())[::max(1,len(motifs)//25)]:
        ts=[td[k] for k in sorted(m['tiles'])]; ee=[] if m['family'].startswith('star') else [(coords[a],coords[b]) for a,b in m['incident']]; centre=None if m['centre'] is None else coords[m['centre']]
        a=T.canonical(ts,ee,centre); u=complex(math.cos(.47),math.sin(.47)); v=3.7+1.9j
        trans=lambda z:z*u+v
        assert T.canonical([(t[0],*[trans(z) for z in t[1:]]) for t in ts],[(trans(x),trans(y)) for x,y in ee],None if centre is None else trans(centre))==a
        mirror=[(t[0],*[z.conjugate() for z in t[1:]]) for t in ts]
        assert T.canonical(mirror,[(x.conjugate(),y.conjugate()) for x,y in ee],None if centre is None else centre.conjugate())==T.canonical(ts,ee,centre,True)
        tested+=1
    records=[]
    for family in ['star','pocket']:
        lost=[t for t in r['tracks'] if t['family'].startswith(family) and not t['left_censored'] and 'lost_at' in t and any(e['loss_without_same_class_renewal'] for e in t['events'])]
        records.append(dict(family=family,observed_losses_without_same_class_renewal=len(lost),median_nearby_active_steps_before_loss=statistics.median(t['nearby_active_steps'] for t in lost) if lost else None))
    report.append(dict(case=run['case'],witness_links_checked=len(r['links']),real_motif_invariance_checks=tested,loss_descriptions=records))
(O/'audit.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
# A scientific still of the deterministic longest same-class candidate path.
r=json.loads((O/'continuation-3-observer.json').read_text()); chain=r['summary']['example_chain']; tracks=[r['tracks'][i] for i in chain]; run=next(x for x in runs if x['case']=='continuation-3')
tiles={T.E.tile_id(t):t for f in run['frames'] for t in f['skin']}; selected=[tiles[k] for tr in tracks for k in tr['tiles']]; origin=F.CD.cen(selected[0]); pts=[(z-origin)/F.S for t in selected for z in t[1:]]
xmin,xmax=min(z.real for z in pts)-1,max(z.real for z in pts)+1; ymin,ymax=min(z.imag for z in pts)-1,max(z.imag for z in pts)+1
fig,axs=plt.subplots(1,len(tracks),figsize=(12,4.8))
for ax,tr in zip(axs,tracks):
    fr=next(f for f in run['frames'] if f['slice']==tr['born']); F.draw(ax,fr['skin'],origin,F.GRAY)
    F.draw(ax,[tiles[k] for k in tr['tiles']],origin,F.A)
    witness={w for l in r['links'] if l['child']==tr['id'] and l['parent'] in chain for w in l['witness']}
    F.draw(ax,[tiles[k] for k in witness],origin,F.B)
    ax.set(xlim=(xmin,xmax),ylim=(ymin,ymax),aspect='equal',title=f'Slice {tr["born"]} | occurrence {tr["id"]}'); ax.axis('off')
fig.suptitle('One frontier-star class, three connected occurrences',fontsize=17)
fig.text(.04,.035,'Blue: selected decorated star. Orange: new witness tiles linking consecutive occurrences.\nSame class at slices 97, 98, 99; two candidate links. This is not evidence of an enduring physical object.',fontsize=10)
fig.tight_layout(rect=(0,.13,1,.9)); fig.savefig(O/'candidate-chain.png',dpi=160); plt.close(fig)
