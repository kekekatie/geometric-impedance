"""Explicit report, parity-consistent inference, committed frame and wire-state model."""
import sys, json, itertools
from pathlib import Path
from functools import lru_cache
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import stage2_surface as frozen

VARIANTS={
 'A_legacy':dict(parity=False,odds=False,epsilon=False,frame=False),
 'B_xor':dict(parity=True,odds=False,epsilon=False,frame=False),
 'C_prior':dict(parity=True,odds=True,epsilon=False,frame=False),
 'D_ties':dict(parity=True,odds=True,epsilon=True,frame=False),
 'E_frame':dict(parity=True,odds=True,epsilon=True,frame=True)}
ARMS=('thick','thin','diamond','whole')
DEFAULT_REPORT={'site':[1,1],'onsets':[1,2],'deadline':4}
EPS=1e-12

def report_key(report):
 if set(report)!={'site','onsets','deadline'}:raise ValueError('report schema')
 site=tuple(report['site']);onsets=tuple(report['onsets'])
 if site not in frozen.DATA or report['deadline']!=4:raise ValueError('unsupported site/deadline')
 if not onsets or tuple(sorted(set(onsets)))!=onsets or any(type(s)!=int or s not in range(3) for s in onsets):raise ValueError('onset interval')
 return site,onsets

def compose(contributions,parity=True):
 sets={k:set() for k in ('X','Z','MZ','MX')}
 for tag,pos,t in contributions:
  key=(pos,t)
  if parity and key in sets[tag]:sets[tag].remove(key)
  else:sets[tag].add(key)
 return tuple(sets[k] for k in ('X','Z','MZ','MX'))

def convolve(signatures,nbits,p):
 """Exact independent Bernoulli distribution of a GF(2) signature sum."""
 mass=np.zeros(1<<nbits);mass[0]=1.;indices=np.arange(1<<nbits)
 for sig in signatures:mass=(1-p)*mass+p*mass[indices^sig]
 return mass

def positions(sector):return frozen.ZDETS if sector=='X' else frozen.XDETS

def stabs(sector):return frozen.ZSTABS if sector=='X' else frozen.XSTABS

def prefix_indices(sector):return [i for i,(_,t) in enumerate(positions(sector)) if t<=3]

def prefix_codes(sig,sector):return sig[...,prefix_indices(sector)].astype(np.int64) @ (1<<np.arange(16,dtype=np.int64))

@lru_cache(None)
def frame_map(sector):
 sigs=[]
 for f in frozen._sector_faults(sector):
  if f[2]>3:continue
  sig,logical,_=frozen._unit_sig(sector,f)
  code=int(prefix_codes(sig,sector))
  if f[2]<3:code|=int(logical)<<16
  sigs.append(code)
 mass=convolve(sigs,17,frozen.P)
 p0,p1=mass[:1<<16],mass[1<<16:]
 assert np.all(p0+p1>0),'precommit map must cover every prefix'
 return ((p1-p0)>EPS*(p0+p1)).astype(np.uint8)

def observed_frames(DZ,DX):
 out=[]
 for sector,dets in [('X',DZ),('Z',DX)]:
  code=sum(int(dets[positions(sector)[i]])<<j for j,i in enumerate(prefix_indices(sector)))
  out.append(int(frame_map(sector)[code]))
 return out

@lru_cache(None)
def table(sector):
 t=frozen._build_tables(sector)
 weights=np.zeros(len(t['PRI']),dtype=np.int8)
 for w in range(4):weights[t['PRI']==frozen.P**w]=w
 t['ODDS']=(frozen.P/(1-frozen.P))**weights
 t['CODE']=prefix_codes(t['SIG'],sector)
 return t

@lru_cache(None)
def erasure(sector,site,onset):
 return frozen._unit_sig(sector,('X' if sector=='X' else 'Z',site,onset))

@lru_cache(None)
def marginal(sector,dets,boundary,frame,site,onset,odds):
 t=table(sector);esig,elog,ebnd=erasure(sector,site,onset)
 indices={d:i for i,d in enumerate(positions(sector))};si={k:i for i,k in enumerate(stabs(sector))}
 pri=t['ODDS'] if odds else t['PRI'];w0=w1=0.
 for e in (0,1):
  sig=t['SIG']^(esig if e else 0);bnd=t['BND']^(ebnd if e else 0);logical=t['LOG']^(elog if e else 0)
  mask=np.ones(len(pri),dtype=bool)
  for d,v in dets:mask &= sig[:,indices[d]]==v
  for k,v in boundary:mask &= bnd[:,si[k]]==v
  if frame is not None:
   code=t['CODE']^(int(prefix_codes(esig,sector)) if e else 0)
   mask &= frame_map(sector)[code]==frame
  pr=pri[mask]*.5;lg=logical[mask]
  w0+=float(pr[lg==0].sum());w1+=float(pr[lg==1].sum())
 return w0,w1

def decide(az,ax,bz,bx,frames,report,variant):
 cfg=VARIANTS[variant];site,onsets=report_key(report);p0=p1=0.
 for s in onsets:
  q0,q1=marginal('X',tuple(sorted(az.items())),tuple(sorted(bz.items())),frames[0],site,s,cfg['odds'])
  r0,r1=marginal('Z',tuple(sorted(ax.items())),tuple(sorted(bx.items())),frames[1],site,s,cfg['odds'])
  p0+=(r0+r1)*q0;p1+=(r0+r1)*q1
 if p0+p1<=0:raise ValueError('zero evidence probability')
 legacy_label=0 if p0>=p1 else 1;legacy_tie=p0==p1
 p0,p1=p0/(p0+p1),p1/(p0+p1)
 tied=abs(p0-p1)<=EPS if cfg['epsilon'] else legacy_tie
 label=(0 if tied or p0>=p1 else 1) if cfg['epsilon'] else legacy_label
 return dict(label=label,p0=p0,p1=p1,tie=bool(tied))

def full_record(DZ,DX):return {**DZ,**DX}

def prepare_before_report(prefix,arm,variant):
 """Only rounds0..3 accepted. No site/report argument; frame has no loss knowledge."""
 if arm not in ARMS or variant not in VARIANTS:raise ValueError('arm/model')
 expected={(k,t) for k in range(8) for t in range(4)}
 if set(prefix)!=expected or any(v not in (0,1) for v in prefix.values()):raise ValueError('prefix must stop at round3')
 state=dict(version=1,arm=arm,model=variant,through=3)
 if arm=='thick':state['dense']=[[k,t,prefix[k,t]] for k,t in sorted(prefix)];return state
 state['live']=[[k,3,prefix[k,3]] for k in range(8)]
 state['boundary']=[prefix[k,0]^prefix[k,1]^prefix[k,2] for k in range(8)]
 if VARIANTS[variant]['frame']:
  state['frame']=observed_frames({d:v for d,v in prefix.items() if d[0] in frozen.ZSTABS},{d:v for d,v in prefix.items() if d[0] in frozen.XSTABS})
 if arm in ('diamond','whole'):state['archive']=[[k,t] for k in range(8) for t in range(3) if prefix[k,t]]
 return state

def append_round4(state,round4):
 if state['through']!=3 or set(round4)!=set(range(8)) or any(v not in (0,1) for v in round4.values()):raise ValueError('round4 ordering')
 state['dense' if state['arm']=='thick' else 'live'] += [[k,4,round4[k]] for k in range(8)]
 state['through']=4
 return state

def encode(state):return json.dumps(state,sort_keys=True,separators=(',',':')).encode('utf-8')

def restore(data):
 state=json.loads(data)
 arm=state.get('arm');variant=state.get('model')
 if arm not in ARMS or variant not in VARIANTS or state.get('version')!=1 or state.get('through')!=4:raise ValueError('state header')
 keys={'version','arm','model','through'}|({'dense'} if arm=='thick' else {'live','boundary'})
 if arm!='thick' and VARIANTS[variant]['frame']:keys.add('frame')
 if arm in ('diamond','whole'):keys.add('archive')
 if set(state)!=keys:raise ValueError('state fields')
 field='dense' if arm=='thick' else 'live';rows=state[field]
 expected={(k,t) for k in range(8) for t in (range(5) if arm=='thick' else (3,4))}
 if len(rows)!=len(expected) or {(k,t) for k,t,v in rows}!=expected or any(v not in (0,1) for k,t,v in rows):raise ValueError('detector schema')
 if arm!='thick' and (len(state['boundary'])!=8 or any(v not in (0,1) for v in state['boundary'])):raise ValueError('boundary')
 if 'frame' in state and (len(state['frame'])!=2 or any(v not in (0,1) for v in state['frame'])):raise ValueError('frame')
 if 'archive' in state:
  rows=state['archive'];coords={tuple(x) for x in rows}
  if len(coords)!=len(rows) or not coords<={(k,t) for k in range(8) for t in range(3)}:raise ValueError('archive')
 return state

def evidence(state,report):
 site,onsets=report_key(report);arm=state['arm']
 avail={(k,t):v for k,t,v in state['dense' if arm=='thick' else 'live']}
 boundary={} if arm=='thick' else dict(enumerate(state['boundary']))
 frames=state.get('frame',[None,None])
 if arm in ('diamond','whole'):
  arch={tuple(x) for x in state['archive']}
  query=[(k,t) for k in (frozen.STAR[site] if arm=='diamond' else range(8)) for t in (onsets if arm=='diamond' else range(3))]
  for d in query:avail[d]=int(d in arch)
 return ({d:v for d,v in avail.items() if d[0] in frozen.ZSTABS},
         {d:v for d,v in avail.items() if d[0] in frozen.XSTABS},
         {k:v for k,v in boundary.items() if k in frozen.ZSTABS},
         {k:v for k,v in boundary.items() if k in frozen.XSTABS},frames)

def decode(state,report):return decide(*evidence(state,report),report,state['model'])

def direct(DZ,DX,arm,report,variant):
 site,onsets=report_key(report);record=full_record(DZ,DX)
 if arm=='thick':return decide(DZ,DX,{}, {},[None,None],report,variant)
 bz={k:DZ[k,0]^DZ[k,1]^DZ[k,2] for k in frozen.ZSTABS};bx={k:DX[k,0]^DX[k,1]^DX[k,2] for k in frozen.XSTABS}
 keep={(k,t) for k in range(8) for t in (3,4)}
 if arm=='diamond':keep|={(k,t) for k in frozen.STAR[site] for t in onsets}
 if arm=='whole':keep|={(k,t) for k in range(8) for t in range(3)}
 frames=observed_frames(DZ,DX) if VARIANTS[variant]['frame'] else [None,None]
 return decide({d:v for d,v in DZ.items() if d in keep},{d:v for d,v in DX.items() if d in keep},bz,bx,frames,report,variant)

def payload_bits(state):
 if state['arm']=='thick':return 40
 return 24+(2 if 'frame' in state else 0)+5*len(state.get('archive',[]))
