"""Focused regressions for the corrections; no edge-loss ensemble."""
import json,itertools,copy
from pathlib import Path
import numpy as np
import model as m
from model import frozen as sc
HERE=Path(__file__).resolve().parents[1]
def reject(fn):
 try:fn()
 except (ValueError,TypeError):return
 raise AssertionError('invalid input accepted')
def main():
 f=('X',(1,1),1)
 assert not m.compose([f,f])[0] and m.compose([f,f],False)[0]
 assert np.all(m.erasure('X',(1,1),1)[0]^sc._unit_sig('X',f)[0]==0)
 sigs=[1,2,3,5,6];p=.07;actual=m.convolve(sigs,3,p);expected=np.zeros(8)
 for bits in itertools.product((0,1),repeat=len(sigs)):
  k=0
  for bit,sig in zip(bits,sigs):
   if bit:k^=sig
  expected[k]+=p**sum(bits)*(1-p)**(len(bits)-sum(bits))
 assert np.max(abs(expected-actual))<1e-14
 assert all(len(m.frame_map(s))==65536 for s in ('X','Z'))
 clean=sc.simulate(set(),set(),set(),set())
 chain={((sc.DATA[i]),0) for i,b in enumerate(sc.XL) if b}
 hidden=sc.simulate(chain,set(),set(),set())
 assert clean[0]==hidden[0] and hidden[2]!=clean[2]
 assert m.observed_frames(*clean[:2])==m.observed_frames(*hidden[:2])
 record=m.full_record(*clean[:2]);prefix={d:v for d,v in record.items() if d[1]<=3}
 archive_before=[]
 for arm in m.ARMS:
  state=m.prepare_before_report(prefix,arm,'E_frame');assert state['through']==3
  reject(lambda:m.restore(m.encode(state)))
  m.append_round4(state,{k:record[k,4] for k in range(8)})
  restored=m.restore(m.encode(state));assert restored==state
  if arm=='thin':assert 'archive' not in state
  if arm in ('diamond','whole'):archive_before.append(state['archive'])
  assert m.decode(state,m.DEFAULT_REPORT)==m.direct(*clean[:2],arm,m.DEFAULT_REPORT,'E_frame')
  broken=dict(state,oracle_truth=0);reject(lambda:m.restore(m.encode(broken)))
 assert archive_before[0]==archive_before[1]
 state=m.prepare_before_report(prefix,'diamond','E_frame');m.append_round4(state,{k:0 for k in range(8)})
 corner=dict(site=[0,0],onsets=[0,1],deadline=4)
 az,ax,*_=m.evidence(state,corner)
 assert {(k,t) for k,t in dict(az,**{}) if t<3}|{(k,t) for k,t in ax if t<3}=={(k,t) for k in sc.STAR[(0,0)] for t in (0,1)}
 assert not np.array_equal(m.erasure('X',(0,0),1)[0],m.erasure('X',(1,1),1)[0])
 assert not np.array_equal(m.erasure('X',(1,1),1)[0],m.erasure('X',(1,1),2)[0])
 for bad in [dict(site=[9,9],onsets=[1,2],deadline=4),dict(site=[1,1],onsets=[2,1],deadline=4),dict(site=[1,1],onsets=[1,2],deadline=5)]:reject(lambda:m.report_key(bad))
 reject(lambda:m.prepare_before_report(record,'thin','E_frame'))
 old=m.marginal
 m.marginal=lambda sector,d,b,f,site,s,odds:((9.,1.) if s==1 else (1.,9.)) if sector=='X' else ((1.,0.) if s==1 else (9.,0.))
 try:ans=m.decide({}, {}, {}, {},[None,None],m.DEFAULT_REPORT,'E_frame')
 finally:m.marginal=old
 assert ans['label']==1 and ans['p0']==.18 and ans['p1']==.82
 m.marginal=lambda sector,*args:(1.,1.+1e-13) if sector=='X' else (1.,0.)
 try:
  a=m.decide({}, {}, {}, {},[None,None],m.DEFAULT_REPORT,'C_prior')
  b=m.decide({}, {}, {}, {},[None,None],m.DEFAULT_REPORT,'D_ties')
 finally:m.marginal=old
 assert a['label']==1 and not a['tie'] and b['label']==0 and b['tie']
 out=dict(parity_cancellation=True,frame_probability_convolution=True,frame_is_statistic_not_truth=True,full_prefix_support=True,wire_roundtrip_and_schema=True,arm_isolation=True,report_routing_and_erasure=True,deadline_guard=True,shared_onset_product=True,epsilon_ties=True,all_passed=True)
 (HERE/'results').mkdir(exist_ok=True);(HERE/'results/tests.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
if __name__=='__main__':main()
