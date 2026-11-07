"""Fixed paired 528-window grids; unchanged native reader + referee closed LP."""
import sys,json,math,functools,hashlib,time,collections,copy
import common as C
from common import AF,IW,dk
sys.path.insert(0,str(C.PILOT/'referee_checks_2026-11-06/src'))
import rc_common as RC
import check4b_arc_scores as CON
import readout as GRID

RC.SR.inverse=functools.lru_cache(maxsize=None)(RC.SR.inverse)
META={}
def score(w,si,tiles):
    if not tiles:return dict(open='empty_selection',closed='empty_selection',status='no_tiles')
    if (w,si) not in META:
        jp=C.old(f'jam-{w}-{si}.pkl')
        META[(w,si)]=AF.RD.build_payload(jp['Sstar'],jp['cs'],[])
    payload=dict(META[(w,si)],tiles=[IW.etile(t) for t in tiles])
    key=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    path=C.CACHE/('reader-'+key+'.pkl')
    if path.exists():return C.load(path.name)
    raw=RC.SR.read(payload)
    if raw.get('status')!='reconstructed':
        result=dict(open='unreconstructible',closed='unreconstructible',status=raw.get('status'),raw=raw)
    else:
        native,_=AF.RD.classify(raw);native={'correct':'B','wrong':'A'}.get(native,native)
        comp=[h for h in (0,1) if CON.closed_compatible(raw['constraints'],payload['windows'],payload['hypotheses'][h])]
        feasible=CON.closed_compatible(raw['constraints'],payload['windows'],[])
        closed=('A' if comp==[0] else 'B' if comp==[1] else 'ambiguous' if len(comp)==2 else 'empty_incompatible') if feasible else 'empty_incompatible'
        result=dict(open=native,closed=closed,status=raw['status'],F_area=raw['area'],intersections=raw['intersections'],
                    closed_compatible=comp,F_closed_feasible=feasible,payload_sha256=key,
                    constraints=raw['constraints'])
    C.save(path.name,result);return result

def grid(w,si,kind):
    path=C.RESULTS/f'readout-{kind}-w{w}-s{si}.json'
    if path.exists():return json.loads(path.read_text())
    jp=C.old(f'jam-{w}-{si}.pkl');original=jp['band'];jc=GRID.centroid(original)
    dm=sum((e[0]+e[1])/2 for e in jp['dead'])/len(jp['dead'])
    anchor=math.atan2((dm-jc).imag,(dm-jc).real)
    if kind=='full_band':
        trace=C.old(f'trace-{w}-{si}.pkl')
        bands=dict(jam=original,final=[IW.dtile(t) for t in trace['final_state']['tiles']])
    else:
        trial=C.RESULTS/f'w{w}-s{si}-r2-c0.json'
        while not trial.exists():time.sleep(2)
        rec=json.loads(trial.read_text());states=C.load(f'w{w}-s{si}-r2-c0-states.pkl')
        bands=dict(jam=states['snapshots']['jam'],final=states['snapshots'].get('44') if rec['completed'] else None)
    rows=[]
    for checkpoint,band in bands.items():
        centroid=GRID.centroid(band) if band else None
        for j in range(6):
            for hw in GRID.HALFWIDTHS:
                if band is None:
                    rows.append(dict(checkpoint=checkpoint,centre=j,half_width=hw,open='unavailable',closed='unavailable',n=0));continue
                comps=GRID.edge_components(GRID.window(band,centroid,anchor+j*math.pi/3,hw)) if band else []
                subset=sorted(comps[0],key=dk) if comps else []
                result=score(w,si,subset)
                rows.append(dict(checkpoint=checkpoint,centre=j,half_width=hw,n=len(subset),components=len(comps),
                                 tile_keys=C.keys(subset),choice_tile_present=any(dk(t)==dk(jp['B']) for t in subset),**result))
        print('reader',kind,w,si,checkpoint,dict(collections.Counter(r['open'] for r in rows if r['checkpoint']==checkpoint)),flush=True)
    out=dict(case=f'w{w}-B-s{si}',kind=kind,anchor=anchor,rows=rows)
    C.dump(path,out);return out

def main():
    baseline=[grid(w,si,'full_band') for w,si in AF.B_JAMS]
    tally=collections.Counter(r['open'] for c in baseline for r in c['rows'])
    assert dict(tally)==dict(B=111,ambiguous=64,empty_incompatible=353),tally
    print('Native baseline gate passed.',flush=True)
    primary=[grid(w,si,'live_only') for w,si in [(7,0)]+[c for c in AF.B_JAMS if c!=(7,0)]]
    counts={kind:{conv:dict(collections.Counter(r[conv] for c in cases for r in c['rows'])) for conv in ('open','closed')} for kind,cases in [('full_band',baseline),('live_only',primary)]}
    C.dump(C.RESULTS/'readout_summary.json',counts)
    print(json.dumps(counts),flush=True)
if __name__=='__main__':main()
