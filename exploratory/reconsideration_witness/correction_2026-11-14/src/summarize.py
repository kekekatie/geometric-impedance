"""Verify the completed bounded run and produce the handback tables."""
import json,hashlib,sys,platform,subprocess
from pathlib import Path
import numpy as np
import model as m
HERE=Path(__file__).resolve().parents[1];R=HERE/'results'
def main():
 rows=[json.loads((R/(v+'.json')).read_text()) for v in m.VARIANTS]
 legacy=json.loads((R/'legacy_per_history.json').read_text());cold=json.loads((R/'cold_restart.json').read_text())
 assert legacy['all_passed'] and legacy['histories']==68128
 assert all(r['n_histories']==68128 and r['checks']['mismatches']==0 and r['checks']['archive_dense_mismatches']==0 for r in rows)
 assert all(x['exit_code']==0 and x['max_probability_difference']<=1e-12 for x in cold.values())
 a,e=rows[0],rows[-1]
 import run
 for arm,data in e['cold_input'].items():
  source=run.CACHE/(arm+'-states.jsonl')
  assert hashlib.sha256(source.read_bytes()).hexdigest()==data['sha256']
  n=0
  for line in source.read_text().splitlines():
   rec=json.loads(line);assert rec['id']==hashlib.sha256(m.encode(rec['state'])).hexdigest();n+=1
  assert n==data['unique_states']==cold[arm]['unique_states'] and data['histories']==68128
 def pct(x):return f'{100*x:.6f}%'
 before=['| Arm | Raw reference disagreements: before → after | Weighted hard correctness: before → after | Max payload bits: before → after |','|---|---:|---:|---:|']
 for arm in m.ARMS:
  x,y=a['arms'][arm],e['arms'][arm]
  before.append(f"| {arm} | {x['raw_disagree']:,} → {y['raw_disagree']:,} | {pct(x['hard_correct'])} → {pct(y['hard_correct'])} | {x['payload_max']} → {y['payload_max']} |")
 ladder=['| Stage | Thin disagreements | Diamond disagreements | Thick correctness | Diamond correctness | Mean archive payload, bits |','|---|---:|---:|---:|---:|---:|']
 for r in rows:
  d=r['arms'];ladder.append(f"| {r['variant']} | {d['thin']['raw_disagree']:,} | {d['diamond']['raw_disagree']:,} | {pct(d['thick']['hard_correct'])} | {pct(d['diamond']['hard_correct'])} | {d['diamond']['payload_weighted']:.6f} |")
 accounting=[]
 for r in rows:
  base=26 if r['config']['frame'] else 24
  accounting.append(dict(variant=r['variant'],archive_weighted_mean_events=(r['arms']['diamond']['payload_weighted']-base)/5,archive_max_events=(r['arms']['diamond']['payload_max']-base)//5))
 (R/'accounting.json').write_text(json.dumps(accounting,indent=2)+'\n')
 (HERE/'BEFORE_AFTER.md').write_text('\n'.join(before)+'\n\n'+ '\n'.join(ladder)+'\n',encoding='utf-8')
 out=dict(all_passed=True,variants=5,histories_per_variant=68128,total_direct_roundtrip_checks=sum(r['checks']['direct_roundtrip_checks'] for r in rows),legacy_per_history=legacy,cold=cold,
  python=sys.version,numpy=np.__version__,platform=platform.platform(),protocol_commit=subprocess.check_output(['git','rev-parse','fa18eb2'],cwd=HERE).decode().strip(),
  source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((HERE/'src').glob('*.py'))})
 (R/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
 print('\n'.join(before));print('\n'.join(ladder));print('All completed-run checks passed.',flush=True)
if __name__=='__main__':main()
