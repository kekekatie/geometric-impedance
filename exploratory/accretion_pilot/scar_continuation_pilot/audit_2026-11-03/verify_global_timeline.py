"""Whole-band feasibility on existing cached checkpoints; no intermediate arc search."""
from audit_common import *
def main():
    out=[];cache={}
    for w,si in S.B_JAMS:
        res=load(f'growth-{w}-{si}.pkl');trace=load(f'trace-{w}-{si}.pkl');p=S.RD.build_payload(res['Sstar'],res['cs'],[]);rank={int(k):v for k,v in p['rank'].items()};rows=[]
        for step,tr in enumerate(trace,1):
            full=tr['post'];key=exacthash(full)+repr(p['origin'])
            if key not in cache:
                band,_=S.PC.skin_of(full);vkeys={S.L.key(z) for t in band for z in t[1:]};K,_,conf=S.EB.M.lift(full);assert not conf;shift=K[S.L.key(complex(*p['origin']))];cm={}
                for v in vkeys:
                    k=K[v]-shift;layer=int(sum(k));assert layer in rank
                    rk=rank[layer];z=S.EB.M.perp(k);win=p['windows'][rk]
                    for i,(nx,ny) in enumerate(win['normals']):cm[(rk,i)]=max(cm.get((rk,i),-math.inf),nx*z.real+ny*z.imag-win['h'])
                raw=dict(status='reconstructed',constraints=[[r,i,c] for (r,i),c in sorted(cm.items())]);cache[key]=margin(raw,p)
            rows.append(dict(step=step,**cache[key]))
        post=[r for r in rows if r['step']>=res['jam_step']]
        out.append(dict(case=f'w{w}-B-s{si}',checkpoints=rows,all_post_scar_band_margins_strictly_negative=all(r['status']==0 and r['margin']<-1e-9 for r in post)))
        print(out[-1]['case'],'post-scar band infeasible',out[-1]['all_post_scar_band_margins_strictly_negative'],flush=True)
    dump('global_timeline.json',dict(cases=out,unique_states=len(cache),note='Only whole-band constraints tested at intermediate steps. No intervening selected-arc readout or trace transport inferred.'))
if __name__=='__main__':main()
