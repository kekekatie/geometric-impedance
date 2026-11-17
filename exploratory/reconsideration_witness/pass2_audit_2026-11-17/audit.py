"""Replay: python audit.py caps | near; then python summarize.py. Pinned sources are read-only."""
import sys, json, time, hashlib, itertools, gc
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / 'distance5_2026-11-16' / 'src'
sys.path.insert(0, str(SRC))
import nd_infer, nd_surface, nd_run, pass2, pass2_caps, pass2_sample

OUT = HERE / 'results'
OUT.mkdir(exist_ok=True)
ARMS = nd_infer.ARMS
EPS = nd_infer.EPS

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def credit(r, truth):
    return .5 if r['tie'] else float(r['label'] == truth)

class IndexedDecoder(pass2_caps.CapDecoder):
    """Exact prefilter by common live/boundary evidence; stock marginal does the rest."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = {}
        self._rows = {}
        for sec in ('X', 'Z'):
            t = self._tab[sec]
            key = t['BNDP'].copy()
            pos = self.s.positions(sec)
            for j, i in enumerate(i for i, (_, r) in enumerate(pos) if r in (3, 4)):
                key |= ((t['SIGP'] >> np.uint64(i)) & np.uint64(1)) << np.uint64(len(self.s.stabs(sec)) + j)
            order = np.argsort(key, kind='stable')
            self._index[sec] = (key[order], order)
        print('indexed', self.w_frame, self.w_dec, flush=True)

    def _marginal_compute(self, sector, cond_dets, cond_bnd, frame, onset, split):
        det = dict(cond_dets); bnd = dict(cond_bnd)
        stabs = self.s.stabs(sector)
        # Full-record arms imply the same boundary used explicitly by thin/diamond.
        if not bnd:
            bnd = {k: det[k, 0] ^ det[k, 1] ^ det[k, 2] for k in stabs}
        key = sum(int(bnd[k]) << j for j, k in enumerate(stabs))
        live = [(k, t) for k, t in self.s.positions(sector) if t in (3, 4)]
        key |= sum(int(det[d]) << (len(stabs) + j) for j, d in enumerate(live))
        esig, _, ebnd = self._erasure[sector, onset]
        ep = sum(int(ebnd[j]) << j for j in range(len(stabs)))
        pos = self.s.positions(sector)
        ep |= sum(int(esig[pos.index(d)]) << (len(stabs) + j) for j, d in enumerate(live))
        pair = tuple(sorted({key, key ^ ep}))
        cachekey = (sector, pair)
        if cachekey not in self._rows:
            keys, order = self._index[sector]
            # Match uint64 dtype: Python-int queries otherwise promote/copy the
            # entire 47M-row index on NumPy 2.2.6. Keys use only 36 bits, so the
            # previous float64 promotion was exact but needlessly expensive.
            chunks = [order[np.searchsorted(keys, np.uint64(k), 'left'):np.searchsorted(keys, np.uint64(k), 'right')] for k in pair]
            # Original candidate order => identical floating-point summation order.
            self._rows[cachekey] = np.sort(np.concatenate(chunks))
        rows = self._rows[cachekey]
        tab = self._tab[sector]
        oldcols = {k: self._frame_col[k] for k in ((sector, 0), (sector, onset, 1))}
        try:
            self._tab[sector] = {**tab, **{k: tab[k][rows] for k in ('SIGP', 'BNDP', 'LOG', 'ODDS')}}
            for k, v in oldcols.items():
                self._frame_col[k] = v[rows]
            return nd_infer.Decoder._marginal_compute(self, sector, cond_dets, cond_bnd, frame, onset, split)
        finally:
            self._tab[sector] = tab
            self._frame_col.update(oldcols)

def panel():
    triples, digest = pass2_sample.draw()
    assert digest == '34aa495f75035da6b0be05d7dafeef3bbbe433b7e7df1b0e61d90b16b14ffb88'
    caphash = hashlib.sha256(';'.join(','.join(map(str, t)) for t in triples[:250]).encode()).hexdigest()
    assert caphash == 'cc8be35776d64ddca09dc534666a29ee8198b449b982b686d2ed9eda0eab5310'
    s = nd_surface.Surface(5)
    class Dummy: pass
    dummy = Dummy(); dummy.s = s
    fts, tags = pass2._panel_fts(dummy)
    assert len(fts) == 2880 and tags.count('triple') == 2000
    sims = [s.simulate(*nd_run.compose(fs))[:3] for fs in fts]
    save('panel.json', dict(sample_sha256=digest, cap250_sha256=caphash, faults=fts, tags=tags,
                           diagnostic_only=True, first_primitive_counts={str(i):sum(t[0] == i for t in triples[:250]) for i in sorted({t[0] for t in triples[:250]})}))
    return sims, tags

def assess(rows, tags):
    out = {}
    for group in ('triple', 'nearloss1'):
        rs = [r for r, tag in zip(rows, tags) if tag == group]
        n = len(rs)
        arm = {a: dict(credit_sum=sum(credit(r[a], r['truth']) for r in rs), ties=sum(r[a]['tie'] for r in rs),
                       hard_correct=sum(r[a]['label'] == r['truth'] for r in rs)) for a in ARMS}
        for a in ARMS: arm[a]['tie_truth'] = arm[a]['credit_sum'] / n
        pairs = {}
        for a in ('thick', 'diamond'):
            ds = [credit(r[a], r['truth']) - credit(r['thin'], r['truth']) for r in rs]
            pairs[a + '_minus_thin'] = dict(sum=sum(ds), mean=sum(ds)/n,
                positive=sum(d > 0 for d in ds), negative=sum(d < 0 for d in ds), zero=sum(d == 0 for d in ds))
        out[group] = dict(n=n, arms=arm, pairs=pairs,
            prefix_absent=sum(any(r['absent'].values()) for r in rs),
            whole_label_ne=sum(r['whole']['label'] != r['thick']['label'] for r in rs),
            whole_post_ne=sum(abs(r['whole']['p0'] - r['thick']['p0']) > EPS for r in rs))
    return out

def changes(base, rows, tags):
    out = {}
    for group in ('triple', 'nearloss1'):
        pairs = [(a, b) for a, b, t in zip(base, rows, tags) if t == group]
        out[group] = dict(frame_changes=sum(a['frames'] != b['frames'] for a,b in pairs), arms={}, pairs={})
        for arm in ARMS:
            out[group]['arms'][arm] = dict(label_flips=sum(a[arm]['label'] != b[arm]['label'] for a,b in pairs),
                tie_changes=sum(a[arm]['tie'] != b[arm]['tie'] for a,b in pairs),
                posterior_shifts=sum(abs(a[arm]['p0'] - b[arm]['p0']) > EPS for a,b in pairs),
                credit_change=sum(credit(b[arm],b['truth']) - credit(a[arm],a['truth']) for a,b in pairs))
        for arm in ('thick','diamond'):
            ds = [(credit(b[arm],b['truth'])-credit(b['thin'],b['truth']))-(credit(a[arm],a['truth'])-credit(a['thin'],a['truth'])) for a,b in pairs]
            out[group]['pairs'][arm+'_minus_thin'] = dict(sum_change=sum(ds), mean_change=sum(ds)/len(ds), histories_changed=sum(d != 0 for d in ds))
    return out

def unaccelerated_check(D, sims, rows, indices):
    old = D._marginal_compute
    oldcache = D._mcache
    D._mcache = {}
    D._marginal_compute = nd_infer.Decoder._marginal_compute.__get__(D)
    maxerr = 0.; count = 0
    try:
        for i in sorted(indices):
            dz, dx, _ = sims[i]
            for a in ARMS:
                ref = D.direct(dz, dx, a); got = rows[i][a]
                err = abs(ref['p0'] - got['p0']); maxerr = max(maxerr, err)
                assert ref['label'] == got['label'] and ref['tie'] == got['tie'] and err <= EPS, (i,a,ref,got)
                count += 1
    finally:
        D._marginal_compute = old; D._mcache = oldcache
    return dict(histories=len(indices), arm_checks=count, max_posterior_error=maxerr)

def caps():
    sims, tags = panel()
    allrows = {}; summary = {}; diffs = {}; checks = {}
    configs = [(3,3),(4,3),(3,4)]
    for wf, wd in configs:
        name = f'{wf}{wd}'; ck = OUT / f'cap_{name}.json'
        if ck.exists():
            obj = json.loads(ck.read_text(encoding='utf-8')); rows = obj['rows']; checks[name] = obj['validation']
            print('reused audit checkpoint',name,flush=True)
        else:
            start = time.time(); print('building',name,flush=True)
            D = IndexedDecoder(5, (2,2), wf, wd)
            rows = []
            for i,(dz,dx,truth) in enumerate(sims):
                rows.append(dict(truth=truth, frames=D.observed_frames(dz,dx), absent=D.prefix_absent(dz,dx),
                                 **{a:D.direct(dz,dx,a) for a in ARMS}))
                if (i+1)%400==0: print(name,i+1,'histories',round(time.time()-start,1),'s',flush=True)
            indices = set(np.linspace(0,len(sims)-1,32,dtype=int).tolist())
            if name == '33': indices = set(range(len(sims)))
            else:
                indices.update(i for i,(a,b) in enumerate(zip(allrows['33'],rows))
                               if any(a[arm]['label'] != b[arm]['label'] or a[arm]['tie'] != b[arm]['tie'] for arm in ARMS))
            checks[name] = unaccelerated_check(D,sims,rows,indices)
            # At baseline also compare original non-chunked builder on the whole panel.
            if name == '33':
                stock = nd_infer.Decoder(5,(2,2)); maxerr=0.
                for i,(dz,dx,truth) in enumerate(sims):
                    for arm in ARMS:
                        ref=stock.direct(dz,dx,arm); got=rows[i][arm]
                        err=abs(ref['p0']-got['p0']); maxerr=max(maxerr,err)
                        assert ref['label']==got['label'] and ref['tie']==got['tie'] and err<=EPS
                checks[name]['stock_builder_checks']=len(sims)*4
                checks[name]['stock_builder_max_error']=maxerr
                stock.s.unit_sig.cache_clear(); stock.s.build_tables.cache_clear(); del stock
            save(ck.name,dict(config=[wf,wd],rows=rows,validation=checks[name],elapsed=time.time()-start))
            D.s.unit_sig.cache_clear(); del D; gc.collect()
        allrows[name]=rows; summary[name]=assess(rows,tags)
        if name!='33': diffs[name]=changes(allrows['33'],rows,tags)
        if name=='34':
            trigger=all(any(v['sum_change'] != 0 for g in diffs[c].values() for v in g['pairs'].values()) for c in ('43','34'))
            if trigger: configs.append((4,4))
            print('paired-margin 44 trigger',trigger,flush=True)
    save('caps_summary.json',dict(summary=summary,changes=diffs,validation=checks,escalate_44=trigger))

def logical_reps(s, sector):
    # X FAULT logical is XL + X stabilizers; conjugate Z fault logical is LZ + Z stabilizers.
    base=list(s.XL if sector=='X' else s.LZ)
    ids=s.XSTABS if sector=='X' else s.ZSTABS
    rows=s._support_matrix(ids)
    best=999; reps=[]
    for mask in range(1<<len(rows)):
        v=base[:]
        for j,row in enumerate(rows):
            if mask>>j&1: v=[a^b for a,b in zip(v,row)]
        if not v[s.DIDX[(2,2)]]: continue
        w=sum(v)
        if w<best: best=w; reps=[]
        if w==best: reps.append(tuple(s.DATA[i] for i,b in enumerate(v) if b))
    return best,sorted(set(reps))

def seams(D):
    out=[]; geometry={}
    for sector in ('X','Z'):
        w,reps=logical_reps(D.s,sector); geometry[sector]=dict(weight=w,count=len(reps))
        for rep in reps[:2]:
            other=[q for q in rep if q!=(2,2)]
            assert len(other)==4
            for onset in (1,2):
                members=[]; records=[]
                for half,loss in ((other[:2],0),(other[2:],1)):
                    extra=[(sector,q,onset) for q in half]
                    faults=extra+([(sector,(2,2),onset)] if loss else [])
                    dz,dx,zl,xl=D.s.simulate(*nd_run.compose(faults))
                    record=tuple(int({**dz,**dx}[k,t]) for k in range(D.s.NSTAB) for t in range(5))
                    records.append(record)
                    members.append(dict(extra=extra,erasure_value=loss,truth_z=zl,truth_x=xl,
                                        decoded={a:D.direct(dz,dx,a) for a in ARMS}))
                assert records[0]==records[1]
                truthkey='truth_z' if sector=='X' else 'truth_x'
                assert members[0][truthkey]!=members[1][truthkey]
                assert members[0]['decoded']==members[1]['decoded']
                out.append(dict(sector=sector,onset=onset,representative=rep,
                    observed_record_order='stabilizer-major, rounds 0..4',observed_record=records[0],
                    identical_records=True,opposite_sector_truth=True,members=members))
    save('seams.json',dict(geometry=geometry,pairs=out,n_pairs=len(out)))

def near():
    D=IndexedDecoder(5,(2,2),3,3); prims,_=pass2.p_loc(D.s)
    n=0; sums={a:0. for a in ARMS}; ties={a:0 for a in ARMS}; records={}
    comparisons={k:0 for k in ('label_ne','tie_ne','credit_ne','post_ne','whole_label_ne','whole_post_ne')}
    maxpost=0.; examples=[]; start=time.time()
    for extra in pass2.near_loss_configs(prims):
        for onset,vx,vz in pass2.variants():
            dz,dx,truth,_=D.s.simulate(*nd_run.compose(tuple(extra)+tuple(pass2.loss_contribs(onset,vx,vz))))
            rs={a:D.direct(dz,dx,a) for a in ARMS}
            for a in ARMS: sums[a]+=credit(rs[a],truth); ties[a]+=rs[a]['tie']
            a,b=rs['diamond'],rs['thick']; err=abs(a['p0']-b['p0']); maxpost=max(maxpost,err)
            comparisons['label_ne']+=a['label']!=b['label']; comparisons['tie_ne']+=a['tie']!=b['tie']
            comparisons['credit_ne']+=credit(a,truth)!=credit(b,truth); comparisons['post_ne']+=err>EPS
            comparisons['whole_label_ne']+=rs['whole']['label']!=b['label']
            comparisons['whole_post_ne']+=abs(rs['whole']['p0']-b['p0'])>EPS
            if a['label']!=b['label'] and len(examples)<8: examples.append(dict(extra=extra,onset=onset,vx=vx,vz=vz,truth=truth,decoded=rs))
            key=tuple(int({**dz,**dx}[k,t]) for k in range(D.s.NSTAB) for t in range(5))
            if key not in records: records[key]=[set(),0]
            records[key][0].add(truth); records[key][1]+=1; n+=1
            if n%8000==0: print('near',n,round(time.time()-start,1),'s',flush=True)
    assert n==48840
    published=json.loads((SRC.parent/'results/pass2_stress.json').read_text(encoding='utf-8'))
    for a in ARMS:
        assert round(sums[a]/n,6)==published['near_loss']['arms'][a]['tie_truth']
        assert ties[a]==published['near_loss']['arms'][a]['tie_count']
    save('near.json',dict(n=n,credit_sum=sums,tie_truth={a:sums[a]/n for a in ARMS},ties=ties,
        diamond_vs_thick=comparisons,max_posterior_difference=maxpost,record_groups=len(records),
        ambiguous_record_groups=sum(len(v[0])>1 for v in records.values()),
        ambiguous_histories=sum(v[1] for v in records.values() if len(v[0])>1),examples=examples,
        published_aggregate_reproduced=True,elapsed=time.time()-start))
    seams(D)
    print('near complete',comparisons,flush=True)

if __name__=='__main__':
    {'caps':caps,'near':near}[sys.argv[1]]()
