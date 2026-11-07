import json,sys,hashlib,subprocess,platform,inspect,collections
import common as C
from common import AF,L,D,IW,dk
from run_continuation import local_witness

def main():
    trials=[json.loads(p.read_text()) for p in sorted(C.RESULTS.glob('w*-r*-c*.json'))]
    assert len(trials)>=33,'Wait for all fixed radius controls'
    rows=[];queries=[]
    for r in trials:
        w,si,rad,col=r['world'],r['si'],r['radius'],r['collar']
        name=f'w{w}-s{si}-r{rad}-c{col:g}';states=C.load(name+'-states.pkl')
        full=[x for x in C.old(f'trace-{w}-{si}.pkl')['calls'] if not x['skin']]
        row=dict(case=r['case'],radius=rad,collar=col,jam_step=r['jam_step'],complete=r['completed'],equivalent=r['equivalent'],
                 jam_full=r['initial_full'],jam_full_band=r['initial_full_band'],jam_live=r['initial_retention']['retained'],
                 step23_full=r['full_patch_step23'],step23_full_band=r['full_band_step23'],step23_live=len(states['snapshots']['23']) if '23' in states['snapshots'] else None,
                 final_full=r['full_patch_step44'],final_full_band=r['full_band_step44'],final_live=r['rows'][-1]['retained'] if r['completed'] else None,
                 endpoint_legal=r['validation_failure'] is None and r['endpoint_invalid_partial_or_complete']==0 and not r['overlaps']['positive_area_overlaps'],
                 monitoring_steps_differ=sum(x['monitor_mismatches']>0 for x in r['rows']),
                 final_metadata=r['rows'][-1]['retention'])
        rows.append(row)
        witness=r['monitor_witness']
        if witness:
            step=witness['step'];history=L.Patch(full[r['jam_step']-1]['pre'])
            for m in states['actual'][:step-r['jam_step']+1]:
                for t in m['placed']:history.add(t)
            band=states['actual'][step-r['jam_step']]['tiles']
            edge=next(e for e in history.frontier() if repr(AF.edge_id(*e[:2]))==witness['edge'])
            small=witness['minimal'];extra=[IW.dtile(t) for t in small['tiles']] if small else []
            verified=bool(small) and all(C.keys(D.candidates(L.Patch(band+extra[:i]+extra[i+1:]),*edge[:3]))!=witness['expected'] for i in range(len(extra)))
            # Query-specific vertex-star-only summary: no occupancy tiles are added.
            corners=L.corners(extra)
            q=L.Patch(band)
            for k,v in corners.items():q.V[k]+=v
            summary_suffices=C.keys(D.candidates(q,*edge[:3]))==witness['expected']
            kept=dict(corners);checks=small['subset_checks'] if small else 0
            if summary_suffices:
                for k in list(kept):
                    if checks>=128:break
                    trial={v:a for v,a in kept.items() if v!=k};q=L.Patch(band)
                    for v,a in trial.items():q.V[v]+=a
                    checks+=1
                    if C.keys(D.candidates(q,*edge[:3]))==witness['expected']:kept=trial
            queries.append(dict(case=r['case'],radius=rad,kind='scar_monitor',step=step,
                         witness=witness,single_deletion_minimal_verified=verified,
                         vertex_summary_only_suffices=summary_suffices,vertex_summary=[dict(vertex=k,arcs=v) for k,v in kept.items()] if summary_suffices else None,
                         diagnostic_checks=checks,scope='This first query only; summary never supplied to construction. No global minimality claim.'))
        if 'live_query' in r['first_differences']:
            first=r['first_differences']['live_query'];step=first['step'];idx=step-r['jam_step']
            hist=L.Patch(full[r['jam_step']-1]['pre'])
            for m in states['actual'][:idx]:
                for t in m['placed']:hist.add(t)
            previous=[IW.dtile(t) for t in C.load(name+'-input.pkl')['tiles']] if idx==0 else states['actual'][idx-1]['tiles']
            e=next((e for e in full[step-1]['frontier_before'] if AF.frontier_id(e)==first['edge']),None)
            queries.append(dict(case=r['case'],radius=rad,kind='live_query',first=first,
                                diagnostic=local_witness(hist,previous,e,first['baseline'] or []) if e else None))
    C.dump(C.RESULTS/'retention_summary.json',rows);C.dump(C.RESULTS/'query_diagnostics.json',queries)
    counts=json.loads((C.RESULTS/'readout_summary.json').read_text())
    for kind in counts:
        for conv in counts[kind]:
            for label in ['A','B','ambiguous','empty_incompatible','empty_selection','unreconstructible','unavailable']:counts[kind][conv].setdefault(label,0)
    C.dump(C.RESULTS/'readout_summary.json',counts)
    inputs={}
    for w,si in AF.B_JAMS:
        for pattern in ['jam-{}-{}.pkl','verify-{}-{}.pkl','trace-{}-{}.pkl']:
            p=C.OLD/pattern.format(w,si);inputs[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    import numpy,scipy,matplotlib
    git=lambda *a:subprocess.check_output(['git',*a],cwd=C.HERE).decode().strip()
    provenance=dict(base_commit='41a9952edfbe350abfd9e2807e6cb6871d9f4881',protocol_commit='62cd04b',
        prior_audit='19981c2b75a76da1787dfab04cfc1a381ec4d68e',frozen_commit=git('-C',str(AF.EB.EFP.parents[2]),'rev-parse','HEAD'),
        python=sys.version,platform=platform.platform(),numpy=numpy.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,
        fork_sha256=hashlib.sha256(AF.RD.FORKS.read_bytes()).hexdigest(),reused_audited_cache_sha256=inputs,
        loaded_modules={name:dict(path=m.__file__,sha256=hashlib.sha256(__import__('pathlib').Path(m.__file__).read_bytes()).hexdigest()) for name,m in [('engine',L),('candidates',D),('active_skin',C.E),('scheduler',C.SCN),('adapter',AF.RD)]})
    C.dump(C.RESULTS/'provenance.json',provenance)
    print(json.dumps(dict(trials=len(trials),by_radius={rad:dict(n=sum(r['radius']==rad and not r['collar'] for r in rows),equivalent=sum(r['radius']==rad and not r['collar'] and r['equivalent'] for r in rows)) for rad in (1,2,3)},readout=counts),indent=2),flush=True)
if __name__=='__main__':main()
