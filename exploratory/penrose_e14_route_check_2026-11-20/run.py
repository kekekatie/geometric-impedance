"""One replay command: python run.py (frozen prediction + exhaustive comparison)."""
import csv, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import predict
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'aperiodic_predict_2026-11-20/src'))
import paired_run as prior
import patch_decoder as pd
from nd_infer import Decoder as Original

class Indexed(pd.PatchDecoder):
    """Necessary-evidence prefilter only; original marginal and row order retained."""
    def __init__(self,code,site):
        super().__init__(code,site,w_dec=3,w_frame=3)
        self.index={};self.rowcache={}
        for sec in ('X','Z'):
            t=self._tab[sec];key=t['BNDP'].copy();n=len(self.s.stabs(sec))
            for j,i in enumerate(i for i,(_,r) in enumerate(self.s.positions(sec)) if r in (3,4)):
                key|=((t['SIGP']>>np.uint64(i))&np.uint64(1))<<np.uint64(n+j)
            order=np.argsort(key,kind='stable');self.index[sec]=(key[order],order)
    def _marginal_compute(self,sector,cond_dets,cond_bnd,frame,onset,split):
        det=dict(cond_dets);bnd=dict(cond_bnd);stabs=self.s.stabs(sector);pos=self.s.positions(sector)
        if not bnd:bnd={k:det[k,0]^det[k,1]^det[k,2] for k in stabs}
        live=[d for d in pos if d[1] in (3,4)]
        key=sum(int(bnd[k])<<j for j,k in enumerate(stabs))|sum(int(det[d])<<(len(stabs)+j) for j,d in enumerate(live))
        esig,_,ebnd=self._erasure[sector,onset]
        ep=sum(int(ebnd[j])<<j for j in range(len(stabs)))|sum(int(esig[pos.index(d)])<<(len(stabs)+j) for j,d in enumerate(live))
        ck=(sector,tuple(sorted({key,key^ep})))
        if ck not in self.rowcache:
            keys,order=self.index[sector]
            chunks=[order[np.searchsorted(keys,np.uint64(k),'left'):np.searchsorted(keys,np.uint64(k),'right')] for k in ck[1]]
            self.rowcache[ck]=np.sort(np.concatenate(chunks))
        rows=self.rowcache[ck];tab=self._tab[sector];cols={k:self._frame_col[k] for k in ((sector,0),(sector,onset,1))}
        try:
            self._tab[sector]={**tab,**{k:tab[k][rows] for k in ('SIGP','BNDP','LOG','ODDS')}}
            for k,v in cols.items():self._frame_col[k]=v[rows]
            return Original._marginal_compute(self,sector,cond_dets,cond_bnd,frame,onset,split)
        finally:self._tab[sector]=tab;self._frame_col.update(cols)

def unpack(D,state):
    # No access to simulator data or truth. The archive was serialized before query selection.
    live={tuple(map(int,k.split(','))):v for k,v in state['live'].items()}
    boundary={int(k):v for k,v in state['boundary'].items()}
    archive={tuple(x) for x in state['archive']}
    return live,boundary,archive,state['frame']
def query(D,stored,checks,r0=False,whole=False):
    live,boundary,archive,frames=stored;rec=dict(live)
    coords=[(k,t) for k in range(D.NST) for t in range(3)] if whole else [(k,t) for k in checks for t in (1,2)]
    for d in coords:rec[d]=int(d in archive)
    if r0:
        for k in checks:
            value=boundary[k]^rec[k,1]^rec[k,2]
            assert value==int((k,0) in archive)
            rec[k,0]=value
    az={d:v for d,v in rec.items() if d[0] in D.s.ZSTABS};ax={d:v for d,v in rec.items() if d[0] in D.s.XSTABS}
    bz={k:v for k,v in boundary.items() if k in D.s.ZSTABS};bx={k:v for k,v in boundary.items() if k in D.s.XSTABS}
    return D.decide(az,ax,bz,bx,frames)
def same(a,b):
    return a['label']==b['label'] and a['tie']==b['tie'] and abs(a['p0']-b['p0'])<=pd.EPS and abs(a['p1']-b['p1'])<=pd.EPS
def save(name,obj):(ROOT/'results'/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

def main():
    obj,pred=predict.generate();predict.draw(obj,pred)
    assert pred['selected']['route']=='X0' and pred['selected']['comparison']=='X5'
    start=time.time();code=prior.FreshPatchCode(predict.PATCH);D=Indexed(code,10)
    nx=len(obj['HX'])
    idx=lambda c:int(c[1:])+(0 if c[0]=='X' else nx)
    geom=sorted(map(idx,pred['existing_checks']));legacy=list(D.star)
    assert nx==11 and geom==[4,6,12,18] and legacy==[4,6,11,17]
    qs={'legacy_diamond':legacy,'legacy_X0':sorted(legacy+[0]),'legacy_X5':sorted(legacy+[5]),
        'incident_diamond':geom,'incident_X0':sorted(geom+[0]),'incident_X5':sorted(geom+[5])}
    arms=['thin','thick','whole']+list(qs)
    credit={a:[0.,0.,0.] for a in arms};ties={a:[0,0,0] for a in arms};counts=[0,0,0]
    tests=dict(round0_histories=0,round0_mismatches=0,round0_max_posterior_error=0.,whole_mismatches=0,
        original_direct_checks=0,original_direct_mismatches=0,unaccelerated_arm_checks=0,unaccelerated_mismatches=0,
        unaccelerated_max_posterior_error=0.,serialized_roundtrips=0,archive_query_mutations=0)
    pool=prior.ordinary_pool(code);assert len(pool)==310
    out=ROOT/'results/config_scores.csv';handle=out.open('w',newline='',encoding='utf-8');writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['config_id','ordinary_weight','odds_weight']+arms)
    h=hashlib.sha256();n=0
    for cid,k,extra in prior.config_stream(pool):
        acc={a:0. for a in arms}
        h.update((json.dumps([cid,k,extra],separators=(',',':'))+'\n').encode())
        for onset,vx,vz in prior.VARIANTS:
            loss=([('X',10,onset)] if vx else [])+([('Z',10,onset)] if vz else [])
            dz,dx,truth,_=code.simulate(*prior.nd_run.compose(extra+tuple(loss)))
            state=D.serialize(dz,dx,'diamond');stored=unpack(D,state)
            dec={'thin':query(D,stored,[]),'thick':D.direct(dz,dx,'thick'),'whole':query(D,stored,[],whole=True)}
            for a,checks in qs.items():
                dec[a]=query(D,stored,checks)
                rr=query(D,stored,checks,r0=True)
                tests['round0_histories']+=1;tests['round0_mismatches']+=not same(rr,dec[a])
                tests['round0_max_posterior_error']=max(tests['round0_max_posterior_error'],abs(rr['p0']-dec[a]['p0']))
            tests['whole_mismatches']+=not same(dec['whole'],dec['thick'])
            for a in arms:acc[a]+=prior.cred(dec[a],truth);credit[a][k]+=prior.cred(dec[a],truth);ties[a][k]+=dec[a]['tie']
            counts[k]+=1;n+=1
            if n%2003==0:
                st2=json.loads(json.dumps(state));tests['serialized_roundtrips']+=1
                assert st2==state
                for a,original in [('thin','thin'),('legacy_diamond','diamond'),('whole','whole')]:
                    tests['original_direct_checks']+=1;tests['original_direct_mismatches']+=not same(D.direct(dz,dx,original),dec[a])
                # Check the independent full scan with an empty cache, not a cached indexed answer.
                old_method=D._marginal_compute;old_cache=D._mcache;D._mcache={};D._marginal_compute=Original._marginal_compute.__get__(D)
                try:
                    for a in arms:
                        rr=D.direct(dz,dx,'thick') if a=='thick' else query(D,unpack(D,st2),qs.get(a,[]),whole=a=='whole')
                        tests['unaccelerated_arm_checks']+=1;tests['unaccelerated_mismatches']+=not same(rr,dec[a])
                        tests['unaccelerated_max_posterior_error']=max(tests['unaccelerated_max_posterior_error'],abs(rr['p0']-dec[a]['p0']))
                finally:D._marginal_compute=old_method;D._mcache=old_cache
                check=D.serialize(dz,dx,'whole');check.pop('arm');orig=dict(state);orig.pop('arm')
                tests['archive_query_mutations']+=check!=orig
        writer.writerow([cid,k,prior.ODDS**k]+[acc[a] for a in arms])
        if len(D._mcache)>500000:D._mcache.clear()
        if cid%5000==0:print('configs',cid,'histories',n,'seconds',round(time.time()-start,1),flush=True)
    handle.close();assert n==385648 and cid+1==48206
    assert all(tests[k]==0 for k in ('round0_mismatches','whole_mismatches','original_direct_mismatches','unaccelerated_mismatches','archive_query_mutations'))
    weights=[prior.ODDS**k for k in range(3)];mass=sum(c*w for c,w in zip(counts,weights))
    scores={a:sum(c*w for c,w in zip(credit[a],weights))/mass for a in arms}
    table={a:dict(tie_aware_truth=scores[a],tie_count=sum(ties[a]),credit_by_fault_weight=credit[a],ties_by_fault_weight=ties[a],
                 gain_over_thin_pp=100*(scores[a]-scores['thin']),remaining_thick_gap_pp=100*(scores['thick']-scores[a])) for a in arms}
    contrasts={}
    for base in ('legacy','incident'):
        diamond=base+'_diamond';x=base+'_X0';y=base+'_X5'
        for a in (diamond,x,y):table[a]['gain_over_own_diamond_pp']=100*(scores[a]-scores[diamond])
        contrasts[base]=dict(route_minus_comparison_pp=100*(scores[x]-scores[y]),diamond_to_thick_gap_pp=100*(scores['thick']-scores[diamond]),
            contrast_fraction_of_original_quoted_gap=100*(scores[x]-scores[y])/.12157,
            prediction_holds=scores[x]>scores[y])
    published=json.loads((ROOT.parent/'aperiodic_predict_2026-11-20/results/paired_results.json').read_text())['edges']['Penrose_1_e14']
    reproduced={'G_thick_thin':round(table['thick']['gain_over_thin_pp'],5),'diamond_thin':round(table['legacy_diamond']['gain_over_thin_pp'],5),
                'thick_diamond':round(table['legacy_diamond']['remaining_thick_gap_pp'],5)}
    assert all(reproduced[k]==published[k] for k in reproduced),(reproduced,published)
    save('scores.json',dict(starting_sha=pred['starting_sha'],prediction_commit='3174b2350faf6cdfa89cd3f02da0eb7faa17d79f',
        patch='Penrose_1',edge=14,qubit=10,scored_logical_Z=obj['logical_Z'],decoder_caps=[3,3],p=prior.P,
        histories=n,configurations=cid+1,histories_by_fault_weight=counts,config_stream_sha256=h.hexdigest(),
        original_quoted_gap_pp=.12157,queries=qs,scores=table,contrasts=contrasts,validation=tests,reproduced_published=reproduced,elapsed_seconds=time.time()-start))
    print('COMPLETE',json.dumps(contrasts),tests,flush=True)
if __name__=='__main__':main()
