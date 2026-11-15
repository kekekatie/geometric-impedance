"""Bounded one-value interventions on the historical and primary examples."""
import json
from pathlib import Path
import model as m
from run import state_of
HERE=Path(__file__).resolve().parents[1]
def examine(label,example):
 fts=[(tag,tuple(pos) if isinstance(pos,list) else pos,t) for tag,pos,t in example['faults']]
 DZ,DX,truth,_=m.frozen.simulate(*m.compose(fts,True));record=m.full_record(DZ,DX)
 state=state_of(record,'diamond','E_frame');evidence=m.evidence(state,m.DEFAULT_REPORT)
 base=m.decide(*evidence,m.DEFAULT_REPORT,'E_frame');reference=m.direct(DZ,DX,'thick',m.DEFAULT_REPORT,'E_frame')
 rows=[]
 for i,dense in enumerate((DZ,DX)):
  for coord,value in dense.items():
   if coord in evidence[i]:continue
   ev=[dict(x) for x in evidence[:4]]+[list(evidence[4])];ev[i][coord]=value
   answer=m.decide(*ev,m.DEFAULT_REPORT,'E_frame')
   rows.append(dict(tag='Z' if i==0 else 'X',check=coord[0],round=coord[1],value=value,outside_star=coord[0] not in m.frozen.STAR[(1,1)],answer=answer,changed_label=answer['label']!=base['label']))
 return dict(label=label,faults=example['faults'],truth=truth,diamond=base,reference=reference,frame=state['frame'],interventions=rows,
  note='Single detector-value additions for this example only, including zeros. No unique or universal outside-star claim.')
def main():
 old=json.loads((HERE/'baseline_handback.json').read_text())['example_diamond_miss']
 primary=json.loads((HERE/'results/E_frame.json').read_text())['example']
 rows=[examine('historical_corner',old)]
 if primary:rows.append(examine('primary_highest_weight_disagreement',primary))
 (HERE/'results/examples.json').write_text(json.dumps(rows,indent=2)+'\n')
 for row in rows:print(row['label'],'truth',row['truth'],'diamond',row['diamond']['label'],'reference',row['reference']['label'],'flips',[(x['tag'],x['check'],x['round'],x['value']) for x in row['interventions'] if x['changed_label']],flush=True)
if __name__=='__main__':main()
