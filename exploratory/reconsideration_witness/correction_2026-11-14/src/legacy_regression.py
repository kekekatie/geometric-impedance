"""Per-history legacy oracle check, separate from aggregate reproduction."""
import json,time
from pathlib import Path
import model as m
from run import histories
HERE=Path(__file__).resolve().parents[1]
def main():
 start=time.time();n=checks=0;largest=0.
 for w,fts,onset in histories():
  n+=1;DZ,DX,*_=m.frozen.simulate(*m.compose(fts,False))
  for arm in m.ARMS:
   old=m.frozen.decode_arm(DZ,DX,arm);new=m.direct(DZ,DX,arm,m.DEFAULT_REPORT,'A_legacy')
   assert old[0]==new['label'],(n,arm,fts,old,new)
   largest=max(largest,abs(old[1]-new['p0']),abs(old[2]-new['p1']));checks+=1
  if n%10000==0:print(n,round(time.time()-start,1),flush=True)
 assert largest<=1e-12
 out=dict(histories=n,arm_comparisons=checks,label_mismatches=0,max_probability_difference=largest,all_passed=True,elapsed_seconds=time.time()-start)
 (HERE/'results/legacy_per_history.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
