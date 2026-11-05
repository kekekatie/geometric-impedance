"""Controlled status-only fixture; synthetic scheduler, no scientific trajectory."""
import json, importlib.util
from pathlib import Path
from unittest.mock import patch
import observe as O

def fixture(module, arrest_step):
    B=O.AF.RD.load_forks()[7]['cs'][1]
    jp=dict(Sstar=[], B=B, stream=0, jam_step=1, full_jam=[B], band=[B])
    count=[0]
    def scheduler(*args, **kw):
        count[0]+=1
        s=(count[0]+1)//2
        return ('total_arrest' if s==arrest_step else 'ok',0,None,[],0)
    with patch.object(module.AF,'jam_prep',return_value=jp), patch.object(module,'ordered_inventory',return_value=[]), patch.object(module.E,'inventory',return_value=[]), patch.object(module.SCN,'patient_scar',side_effect=scheduler):
        rec,_=module.verify_case(7,0)
    return {k:rec[k] for k in ('endpoint_status','horizon_complete','growth_steps_executed','steps_checked')}

def main():
    before=fixture(O.VS,44)
    assert before['endpoint_status']=='total_arrest' and before['horizon_complete'] is True
    print('CONFIRMED pinned defect:',before,flush=True)
    path=Path(__file__).resolve().parents[1]/'supplement_2026-11-04/verify_supplement.py'
    spec=importlib.util.spec_from_file_location('corrected_verifier',path)
    fixed=importlib.util.module_from_spec(spec); spec.loader.exec_module(fixed)
    after=fixture(fixed,44); earlier=fixture(fixed,43); ordinary=fixture(fixed,None)
    assert after['endpoint_status']=='total_arrest' and after['horizon_complete'] is False
    assert earlier['horizon_complete'] is False and earlier['growth_steps_executed']==43
    assert ordinary['endpoint_status']=='horizon_complete' and ordinary['horizon_complete'] is True
    result=dict(before=before,after=after,earlier_arrest=earlier,ordinary_loop_completion=ordinary,
                scope='Status control only; zero-placement synthetic steps do not demonstrate construction progress.')
    (O.CACHE/'horizon_fixture.json').write_text(json.dumps(result,indent=2))
    print('Corrected status regression passed.',flush=True)
if __name__=='__main__':main()
