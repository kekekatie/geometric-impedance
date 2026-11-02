import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'src'))
import coop_common as C
import part3_necessary as P
import audit_tools as A

st,band,rank,dead,witness=P.load_band();B=C.BandConstraints(band,rank)
unresolved={'verdict':'unresolved','box_free':'unresolved'}
assert A.classify_region(B,set(),unresolved)['verdict']=='unresolved'
assert A.classify_region(B,set(),C.classify_exterior(B.full_cmax))['verdict']=='infeasible'
fc=A.true_frontier_counts(st,band)
assert fc==dict(n_frontier=73,n_dead_sites=2,n_growable=71,candidate_count_histogram={0:2,1:28,2:43})
bad=dict(st);bad['true_frontier']=[dict(st['true_frontier'][0],owner=['bad'])]
try:A.true_frontier_counts(bad,band)
except ValueError:pass
else:raise AssertionError('owner mutation was accepted')
corrected=json.loads((C.RESULTS/'part5_score.json').read_text())
corrected['frontier_candidate_counts']=fc
corrected['pre_repair_baseline']['interpretation']='For this recorded baseline, the reconstructed window-compatibility region is empty; this alone does not demonstrate erasure of historical information.'
corrected['audit_note']='Only boundary counting and interpretation corrected; reader result independently reproduced unchanged. No post-repair state exists.'
(HERE/'results'/'corrected_part5_score.json').write_text(json.dumps(corrected,indent=2))
print('PASS unresolved shortcut guard; unchanged infeasible reuse; true frontier counts; owner mutation rejection')
print('Wrote results/corrected_part5_score.json')
