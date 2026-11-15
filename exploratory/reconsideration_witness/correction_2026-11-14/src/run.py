"""Bounded staged run; baseline gate, wire round-trips, and primary cold processes."""
import sys,json,itertools,hashlib,time,subprocess,os,collections
from pathlib import Path
import model as m
from model import frozen as sc
HERE=Path(__file__).resolve().parents[1];RESULTS=HERE/'results';RESULTS.mkdir(exist_ok=True)
CACHE=Path(os.environ.get('DISTANCE3_FIX_CACHE',str(HERE/'runtime'))).resolve();CACHE.mkdir(parents=True,exist_ok=True)

def histories():
 pool=[(tag,q,t) for q in sc.DATA for t in range(5) for tag in ('X','Z')]
 pool += [('MZ',k,t) for k in sc.ZSTABS for t in range(5)]+[('MX',k,t) for k in sc.XSTABS for t in range(5)]
 for w in range(3):
  for extra in itertools.combinations(pool,w):
   for onset in (1,2):
    for vx in (0,1):
     for vz in (0,1):
      loss=([('X',(1,1),onset)] if vx else [])+([('Z',(1,1),onset)] if vz else [])
      yield w,tuple(extra)+tuple(loss),onset

def state_of(record,arm,variant):
 state=m.prepare_before_report({d:v for d,v in record.items() if d[1]<=3},arm,variant)
 return m.append_round4(state,{k:record[k,4] for k in range(8)})

def expected_agreement(a,b):
 if a['tie'] and b['tie']:return 1.
 if a['tie'] or b['tie']:return .5
 return float(a['label']==b['label'])

def run(variant):
 cfg=m.VARIANTS[variant];start=time.time();weights=0.;n=0;checks=0
 totals={a:dict(hard_agree=0.,hard_correct=0.,expected_agree=0.,expected_correct=0.,raw_disagree=0,ties=0,payload_weighted=0.,payload_max=0,wire_weighted=0.,wire_max=0) for a in m.ARMS}
 share=collections.Counter();sample=None;unique={a:{} for a in m.ARMS};unique_expected={a:{} for a in m.ARMS}
 file_handles={a:(CACHE/(a+'-states.jsonl')).open('wb') for a in m.ARMS} if variant=='E_frame' else {}
 archive_equal=True;recon_bad=0;collision_count=0
 try:
  for w,fts,onset in histories():
   n+=1;collision_count+=len(set(fts))!=len(fts)
   weight=(sc.P/(1-sc.P) if cfg['odds'] else sc.P)**w;weights+=weight
   DZ,DX,truth,_=sc.simulate(*m.compose(fts,cfg['parity']));record=m.full_record(DZ,DX)
   dec={};states={}
   for arm in m.ARMS:
    state=state_of(record,arm,variant);wire=m.encode(state);restored=m.restore(wire)
    actual=m.decode(restored,m.DEFAULT_REPORT);direct=m.direct(DZ,DX,arm,m.DEFAULT_REPORT,variant)
    assert actual==direct,(variant,n,arm,'roundtrip/direct');checks+=1
    dec[arm]=actual;states[arm]=state
    t=totals[arm];bits=m.payload_bits(state)
    t['payload_weighted']+=weight*bits;t['payload_max']=max(t['payload_max'],bits)
    t['wire_weighted']+=weight*len(wire);t['wire_max']=max(t['wire_max'],len(wire));t['ties']+=actual['tie']
    if variant=='E_frame':
     key=hashlib.sha256(wire).hexdigest()
     if key not in unique[arm]:
      unique[arm][key]=1;unique_expected[arm][key]=actual
      entry=dict(id=key,state=restored,report=m.DEFAULT_REPORT)
      file_handles[arm].write((json.dumps(entry,separators=(',',':'))+'\n').encode())
     else:unique[arm][key]+=1
   assert states['diamond']['archive']==states['whole']['archive']
   az,ax,*_=m.evidence(states['whole'],m.DEFAULT_REPORT)
   recon_bad+=int(az!=DZ or ax!=DX)
   ref=dec['thick'];assert dec['whole']['label']==ref['label'],(variant,n,'whole/thick')
   assert max(abs(dec['whole'][p]-ref[p]) for p in ('p0','p1'))<=1e-12,(variant,n,'whole probability')
   for arm,d in dec.items():
    t=totals[arm];t['hard_agree']+=weight*(d['label']==ref['label']);t['hard_correct']+=weight*(d['label']==truth)
    t['expected_agree']+=weight*expected_agreement(d,ref);t['expected_correct']+=weight*(.5 if d['tie'] else d['label']==truth)
    t['raw_disagree']+=d['label']!=ref['label']
   if dec['diamond']['label']!=ref['label']:
    share['diamond_right' if dec['diamond']['label']==truth else 'reference_right']+=1
    if sample is None or weight>sample['weight']:sample=dict(weight=weight,faults=fts,onset=onset,truth=truth,decisions=dec)
   if n%10000==0:print(variant,n,'histories',round(time.time()-start,1),'s',flush=True)
 finally:
  for f in file_handles.values():f.close()
 for t in totals.values():
  for field in ('hard_agree','hard_correct','expected_agree','expected_correct','payload_weighted','wire_weighted'):t[field]/=weights
 out=dict(variant=variant,config=cfg,n_histories=n,total_weight=weights,arms=totals,diamond_disagreements=dict(share),example=sample,
  checks=dict(direct_roundtrip_checks=checks,mismatches=0,whole_thick_label_mismatches=0,whole_thick_probabilities_within_1e_12=True,archive_dense_mismatches=recon_bad,archive_arms_identical=True),
  duplicate_contribution_histories=collision_count,elapsed_seconds=time.time()-start,
  query_counts=dict(thick=40,thin=0,diamond=8,whole=24),
  note='Payload maxima across deadline snapshots; wire sizes are actual UTF-8 JSON bytes. Not process-memory or time-resolved peaks.')
 if variant=='A_legacy':
  old=json.loads((HERE/'baseline_handback.json').read_text())
  for arm,t in totals.items():
   assert t['raw_disagree']==old['weighted'][arm]['raw_disagreements_vs_reference']
   assert round(t['hard_agree'],6)==old['weighted'][arm]['agreement_vs_reference']
   assert round(t['hard_correct'],6)==old['weighted'][arm]['logical_correct_vs_truth']
   assert t['payload_max']==old['storage_bits_peak'][arm]
  assert share=={'diamond_right':150,'reference_right':364}
  out['baseline_gate_passed']=True
 if variant=='E_frame':
  for arm in m.ARMS:
   (CACHE/(arm+'-expected.json')).write_text(json.dumps(unique_expected[arm]))
  out['cold_input']={a:dict(unique_states=len(unique[a]),histories=sum(unique[a].values()),sha256=hashlib.sha256((CACHE/(a+'-states.jsonl')).read_bytes()).hexdigest(),bytes=(CACHE/(a+'-states.jsonl')).stat().st_size) for a in m.ARMS}
 (RESULTS/(variant+'.json')).write_text(json.dumps(out,indent=2)+'\n')
 print(variant,'COMPLETE',json.dumps({a:t['raw_disagree'] for a,t in totals.items()}),flush=True)
 return out

def cold_worker(arm):
 source=CACHE/(arm+'-states.jsonl');dest=CACHE/(arm+'-restored.jsonl')
 with source.open() as inp,dest.open('w') as out:
  for line in inp:
   rec=json.loads(line);assert rec['state']['arm']==arm
   state=m.restore(json.dumps(rec['state']));ans=m.decode(state,rec['report'])
   out.write(json.dumps(dict(id=rec['id'],answer=ans))+'\n')
 print('cold',arm,'complete',flush=True)

def cold_check():
 results={}
 for arm in m.ARMS:
  cmd=[sys.executable,str(Path(__file__).resolve()),'worker',arm];start=time.time()
  with (RESULTS/('cold-'+arm+'.log')).open('w') as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode==0,(arm,p.returncode)
  expected=json.loads((CACHE/(arm+'-expected.json')).read_text());seen=set();delta=0.
  for line in (CACHE/(arm+'-restored.jsonl')).read_text().splitlines():
   r=json.loads(line);key=r['id'];assert key not in seen;seen.add(key);a=r['answer'];b=expected[key]
   assert a['label']==b['label'] and a['tie']==b['tie']
   delta=max(delta,abs(a['p0']-b['p0']),abs(a['p1']-b['p1']))
  assert seen==set(expected) and delta<=1e-12
  results[arm]=dict(command=cmd,exit_code=p.returncode,unique_states=len(seen),max_probability_difference=delta,elapsed_seconds=time.time()-start)
  print('cold check',arm,len(seen),'PASS',flush=True)
 (RESULTS/'cold_restart.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':
 if sys.argv[1]=='worker':cold_worker(sys.argv[2])
 elif sys.argv[1]=='cold':cold_check()
 elif sys.argv[1]=='all':
  for v in m.VARIANTS:run(v)
  cold_check()
 else:run(sys.argv[1])
