"""Compare pinned/reproduced artifacts and assemble bounded audit evidence."""
import json,hashlib,shutil,subprocess,sys,inspect,collections
from pathlib import Path
import observe as O
HERE=Path(__file__).resolve().parent;OUT=HERE/'results';REP=HERE/'reproduced';REP.mkdir(exist_ok=True)
PIN='e4a7503b5273dbc1fa72232de5c29b7048672b0d'
PREFIX='exploratory/accretion_pilot/scar_continuation_pilot/archive_free_2026-11-04/'
def h(b):return hashlib.sha256(b).hexdigest()
def write(n,x):(OUT/n).write_text(json.dumps(x,indent=2,default=str)+'\n',encoding='utf-8')
def differences(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        if a.keys()!=b.keys():yield dict(path=path,kind='keys',before=list(a),after=list(b))
        for k in a.keys()&b.keys():yield from differences(a[k],b[k],path+'/'+str(k))
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):yield dict(path=path,kind='length',before=len(a),after=len(b))
        for i,(x,y) in enumerate(zip(a,b)):yield from differences(x,y,path+'/'+str(i))
    elif a!=b:
        numeric=isinstance(a,(float,int)) and isinstance(b,(float,int)) and not isinstance(a,bool) and not isinstance(b,bool)
        yield dict(path=path,kind='numeric' if numeric else 'categorical',before=a,after=b,delta=abs(a-b) if numeric else None)

def main():
    compare=[]
    for suffix in ['results/verification.json','results/prescar_restart.json','results/endpoint_geometry.json','input/prescar_states.json']:
        rel=PREFIX+'supplement_2026-11-04/'+suffix
        before=subprocess.check_output(['git','show',PIN+':'+rel],cwd=O.REPO)
        after=(O.REPO/rel).read_bytes();a=json.loads(before);b=json.loads(after)
        ds=list(differences(a,b))
        compare.append(dict(file=rel,bytes_exact=before==after,line_endings_normalized_exact=before.replace(b'\r\n',b'\n')==after.replace(b'\r\n',b'\n'),
                            structured_exact=a==b,original_sha256=h(before),regenerated_sha256=h(after),differences=ds))
        if suffix.startswith('results/'):(REP/Path(suffix).name).write_text(json.dumps(b,indent=2)+'\n')
    write('artifact_comparison.json',compare)
    assert all(r['structured_exact'] for r in compare), 'Inspect any changed scientific/serialization leaf before completing audit'
    checks=json.loads((OUT/'execution_checks.json').read_text());assert len(checks)==11
    assert all(all(all(r['checks'].values()) for r in c['steps']+c['spawned_steps']) for c in checks)
    assert all(c['all_steps_progress'] and c['initial_B_legal'] for c in checks)
    assert all(all(v['ordered_raw_tiles_equal'] for v in c['raw_geometry'].values()) for c in checks)
    assert all(c['endpoint_full_stars']['all_complete_and_partial_vertices_valid'] and c['endpoint_band_stars']['all_complete_and_partial_vertices_valid'] for c in checks)
    assert all(all(r['additions']==0 and r['edges_match'] and r['vertices_match'] and r['owners_retained'] and r['boundary_vertices_retained'] for r in c['prune_observations']) for c in checks)
    fixtures={}
    for name in ['horizon_fixture.json','endpoint_lifecycle_fixture.json','import_boundary_control.json']:
        fixtures[name]=json.loads((O.CACHE/name).read_text());write(name,fixtures[name])
    readout=json.loads((O.EXP/'results/readout.json').read_text())
    tally=collections.Counter(r['outcome'] for c in readout for r in c['windows'])
    rows=json.loads((REP/'verification.json').read_text())
    baseline=[]
    import pickle
    for w,si in O.AF.B_JAMS:
        rec,pre=O.load(f'verify-{w}-{si}.pkl');jam=rec['jam_step']
        path=O.CACHE.parent/'scar-cache'/f'baseline-{w}-{si}.pkl'
        if not path.exists():
            baseline.append(dict(case=rec['case'],available=False));continue
        old=pickle.loads(path.read_bytes())
        rng=(pre['rng_state'][0],tuple(pre['rng_state'][1]),pre['rng_state'][2])
        current=O.cached_jam(w,si)
        row=dict(case=rec['case'],available=True,baseline_cache_sha256=h(path.read_bytes()),
                 prng_before_jam_matches=rng==old['_audit_rng_trace'][jam-1]['rng_before'],
                 jam_raw_geometry_matches=current['full_jam']==old['snaps'][jam],
                 initial_scars_empty=not pre['scars'])
        assert row['prng_before_jam_matches'] and row['jam_raw_geometry_matches'] and row['initial_scars_empty']
        baseline.append(row)
    write('frozen_prescar_alignment.json',baseline)
    summary=dict(cases=len(checks),full_replay_steps=sum(len(c['steps']) for c in checks),
                 spawned_postjam_steps=sum(len(c['spawned_steps']) for c in checks),
                 placements_validated=sum(r['independent_legality']['placements_validated'] for r in rows),
                 all_scientific_outcomes_unchanged=True,all_checks_passed=True,
                 final_full_vertices=sum(c['endpoint_full_stars']['vertices'] for c in checks),
                 final_band_vertices=sum(c['endpoint_band_stars']['vertices'] for c in checks),
                 completed_full_stars=sum(c['endpoint_full_stars']['n_complete_vertices'] for c in checks),
                 max_overlap_area=max(r['endpoint']['cumulative_history_overlaps']['max_area'] for r in rows),
                 reused_readout_tally=dict(tally),readout_rerun=False,
                 max_raw_coordinate_difference=max(v['max_coordinate_difference'] for c in checks for v in c['raw_geometry'].values()),
                 corrected_statuses=[dict(case=r['case'],horizon_complete=r['endpoint_status']=='horizon_complete' and r['steps_checked'][-1]==44) for r in rows])
    write('summary.json',summary)
    functions={}
    for label,fn in [('Patch.legal',O.AF.L.Patch.legal),('Patch.vertex_ok',O.AF.L.Patch.vertex_ok),('D.candidates',O.AF.D.candidates),('dk',O.AF.dk),('ordered',O.AF.ordered),('patient_scar',O.SCN.patient_scar)]:
        functions[label]=dict(file=inspect.getsourcefile(fn),line=inspect.getsourcelines(fn)[1],source=inspect.getsource(fn))
    write('decision_dependencies.json',functions)
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
