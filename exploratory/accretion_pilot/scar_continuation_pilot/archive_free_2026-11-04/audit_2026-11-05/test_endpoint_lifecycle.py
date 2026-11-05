"""Lifecycle-only fixture: replay already validated additions, without searching.

This is not a new scientific continuation. It tests the endpoint helper's handling
of ActiveSkin.additions using the actual recorded w7 placement transcript.
"""
import importlib.util,json
from pathlib import Path
from unittest.mock import patch
import observe as O
import endpoint_geom as EG

def exercise(fn):
    calls=[r for r in O.load('trace-7-0.pkl')['calls'] if r['skin']]
    i=[0];rows=[];prune=O.AF.E.ActiveSkin.prune
    def scheduler(P,rng,scars,**kw):
        r=calls[i[0]];i[0]+=1
        for t in r['added']:P.add(t)
        return r['result']
    def observed_prune(P):
        n=prune(P);keys={O.AF.dk(t) for t in P.tris}
        rows.append(dict(step=i[0],transient_additions=len(P.additions),
                         deleted_tiles_in_additions=sum(O.AF.dk(t) not in keys for t in P.additions)))
        return n
    with patch.object(O.SCN,'patient_scar',side_effect=scheduler),patch.object(O.AF.E.ActiveSkin,'prune',observed_prune):
        band=fn(7,0)
    return dict(rows=rows,band=[O.IW.etile(t) for t in band])

def main():
    before=exercise(EG.worker_final_band)
    assert before['rows'][-1]['deleted_tiles_in_additions']>0
    path=Path(__file__).resolve().parents[1]/'supplement_2026-11-04/endpoint_geom.py'
    spec=importlib.util.spec_from_file_location('fixed_endpoint',path)
    fixed=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixed)
    after=exercise(fixed.worker_final_band)
    assert all(r['transient_additions']==0 for r in after['rows'] if r['step']>0)
    assert before['band']==after['band']
    result=dict(before=before['rows'][-1],after=after['rows'][-1],raw_endpoint_unchanged=True,
                scope='Diagnostic endpoint helper only; cached real placements replayed to test lifecycle. Main verifier and spawned worker already clear additions.')
    (O.CACHE/'endpoint_lifecycle_fixture.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
