"""Strict structured comparison plus independent recount of saved trial evidence."""
import json, hashlib, collections, subprocess
import run as R
from run import C,HERE,ORIGINAL

def differences(a,b,path='$'):
    if type(a)!=type(b):return [dict(path=path,old=a,new=b)]
    if isinstance(a,dict):
        if a.keys()!=b.keys():return [dict(path=path,old_keys=sorted(a),new_keys=sorted(b))]
        return [d for k in a for d in differences(a[k],b[k],path+'.'+k)]
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path,old_length=len(a),new_length=len(b))]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,f'{path}[{i}]')]
    return [] if a==b else [dict(path=path,old=a,new=b)]

def main():
    files=sorted(C.RESULTS.glob('*.json'));comparisons=[];all_diffs=[]
    for p in files:
        if p.name=='provenance.json':continue # source paths must change in isolated worktree
        old=ORIGINAL/'results'/p.name
        assert old.exists(),p
        delta=differences(json.loads(old.read_text()),json.loads(p.read_text()))
        comparisons.append(dict(file=p.name,exact_structural_equal=not delta,differences=len(delta),
            committed_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),regenerated_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        if delta:all_diffs.append(dict(file=p.name,differences=delta))
    trials=[json.loads(p.read_text()) for p in sorted(C.RESULTS.glob('w*-r*-c0.json'))]
    assert len(trials)==33
    steps=placements=0;raw_checks=[]
    for t in trials:
        w,si,r=t['world'],t['si'],t['radius']
        initial=C.load(f'w{w}-s{si}-r{r}-c0-input.pkl')
        assert set(initial)=={'schema','radius','tiles','boundary','rng_state','scars','fields'}
        assert initial['radius']==r and all(e['owner'] is None for e in initial['boundary'])
        state=C.load(f'w{w}-s{si}-r{r}-c0-states.pkl')
        base=[x for x in C.old(f'trace-{w}-{si}.pkl')['calls'] if not x['skin']]
        assert C.IW.rebuild_scars(initial)==set(base[t['jam_step']-1]['result'][3])
        assert C.IW.rebuild_rng(initial).getstate()==base[t['jam_step']-1]['rng_before']
        checks=[]
        for step,m in enumerate(state['actual'],t['jam_step']):
            b=base[step-1]
            expect=[(eid,[repr(C.dk(tile)) for tile in tiles]) for eid,tiles in b['candidates'] if tiles]
            observed=[(eid,tiles) for eid,tiles in m['candidates'] if tiles]
            assert observed==expect and m['placed']==b['added']
            assert m['rng_before']==b['rng_before'] and m['rng_after']==b['rng_after']
            assert m['result'][:3]==b['result'][:3] and m['result'][4]==0
            assert m['scars']==sorted(tuple(sorted(e)) for e in b['scars_after'])
            assert m['frontier_before']==[C.AF.frontier_id(e) for e in b['frontier_before']]
            assert m['frontier_after']==[C.AF.frontier_id(e) for e in b['frontier_after']]
            assert set(C.keys(m['placed']))<=set(C.keys(m['tiles']))
            steps+=1;placements+=len(m['placed']);checks.append(step)
        assert checks==list(range(t['jam_step'],45))
        assert t['completed'] and t['equivalent'] and t['validation_failure'] is None
        assert t['endpoint_invalid_partial_or_complete']==0 and t['endpoint_complete_stars']['invalid_complete_stars']==0
        assert t['endpoint_complete_stars']['overfull_vertices']==0 and not t['overlaps']['positive_area_overlaps']
        assert all(all(row['checks'].values()) and row['placed']>0 for row in t['rows'])
        raw_checks.append(dict(case=t['case'],radius=r,steps=len(checks),all_passed=True))
    tallies={}
    for kind in ('full_band','live_only'):
        cases=[json.loads(p.read_text()) for p in C.RESULTS.glob(f'readout-{kind}-*.json')]
        rows=[r for x in cases for r in x['rows']];assert len(cases)==11 and len(rows)==528
        tallies[kind]={conv:dict(collections.Counter(r[conv] for r in rows)) for conv in ('open','closed')}
    changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=HERE).decode().strip()
    assert not changed,'Tracked scientific inputs modified'
    out=dict(compared_files=len(comparisons),files=comparisons,differences=all_diffs,
        all_structural_and_numeric_values_exact=not all_diffs,tolerance_applied_to_comparison=None,
        raw_trace_checks=raw_checks,trials=33,steps=steps,validated_placements=placements,
        largest_overlap_residual=max(t['overlaps']['max_intersection_area'] for t in trials),reader_tallies=tallies,
        provenance_note='Original and regenerated provenance differ in isolated-worktree module paths; hashes and versions checked separately.',
        all_passed=not all_diffs)
    C.dump(HERE/'comparison.json',out)
    print(json.dumps({k:v for k,v in out.items() if k not in ('files','raw_trace_checks')},indent=2),flush=True)
    assert not all_diffs,'Discrepancies preserved in comparison.json'

if __name__=='__main__':main()
