import collections,math,random,hashlib,json
from audit_common import *

def normalized_hash(tiles):
    origin=min((z for t in tiles for z in t[1:]),key=lambda z:(round(z.real,9),round(z.imag,9)))
    rec=sorted((t[0],)+tuple((round((z-origin).real/S.S,7),round((z-origin).imag/S.S,7)) for z in t[1:]) for t in tiles)
    return hashlib.sha256(repr(rec).encode()).hexdigest()

def main():
    out=[];front_cache={};geom_cache={};baseline_groups=collections.defaultdict(list);final_groups=collections.defaultdict(list);sequence_groups=collections.defaultdict(list)
    path=RESULTS/'scheduler_verification.json'
    previous={c['case']:c for c in json.loads(path.read_text())['cases']} if path.exists() else {}
    for w,si in S.B_JAMS:
        tag=f'w{w}-B-s{si}';jam=load(f'jam-{w}-{si}.pkl');res=load(f'growth-{w}-{si}.pkl');trace=load(f'trace-{w}-{si}.pkl');base=load(f'baseline-{w}-{si}.pkl');js=jam['jam_step']
        if tag in previous:
            out.append(previous[tag]);continue
        checks=[]
        for step in range(1,js):
            tr=trace[step-1];br=base['_audit_rng_trace'][step-1]
            checks.append(dict(step=step,geometry_exact=tr['post']==base['snaps'][step],rng_before_equal=tr['rng_before']==br['rng_before'],rng_after_equal=tr['rng_after']==br['rng_after'],result_equal=tr['result'][:3]==br['result']))
        assert all(all(v for k,v in c.items() if k!='step') for c in checks)
        assert trace[js-1]['pre']==jam['full'] and base['snaps'][js]==base['snaps'][js-1]
        rows=[];zero_steps=[];departure=None
        for step,tr in enumerate(trace,1):
            full=tr['post'];key=exacthash(full)
            if key not in front_cache:
                P=S.L.Patch(full);fr=P.frontier();counts={S.ekey(e[0],e[1]):len(S.D.candidates(P,*e[:3])) for e in fr};band,_=S.PC.skin_of(full)
                front_cache[key]=(counts,band)
            counts,band=front_cache[key];current=set(counts);blocked={e for e,n in counts.items() if n==0};ever=tr['scars'];alive=ever&current;recovered={e for e in alive if counts[e]>0};missing=ever-current
            if departure is None and S.dk(res['B']) not in {S.dk(t) for t in band}:departure=step
            if not tr['added']:zero_steps.append(dict(step=step,status=tr['result'][0],kind=tr['result'][2],nonpinned_growable=sum(n>0 and e not in ever for e,n in counts.items()),pinned_extendable=len(recovered)))
            rows.append(dict(step=step,placed=len(tr['added']),full_tiles=len(full),band_tiles=len(band),frontier_edges=len(current),cumulative_scar=edge_stats(ever,band),labelled_current=edge_stats(alive,band),current_zero_candidate=edge_stats(blocked,band),labelled_disappeared=len(missing),labelled_extendable=len(recovered),unlabelled_current_zero=len(blocked-ever),current_nonpinned_growable=sum(n>0 and e not in ever for e,n in counts.items()),B_in_band=S.dk(res['B']) in {S.dk(t) for t in band},geometry_hash=tilehash(full),new_labels=sorted([sorted(e) for e in tr['result'][3]])))
        full=res['full'];key=exacthash(full)
        if key not in geom_cache:
            P=S.L.Patch(full);bad=[v for v in P.V if not P.vertex_ok(v,[])];overlap=overlap_check(full)
            geom_cache[key]=dict(vertices=len(P.V),invalid_decorated_stars=bad,overlap=overlap)
        geo=geom_cache[key];assert not geo['invalid_decorated_stars'] and not geo['overlap']['positive_area_overlaps']
        assert departure==res['choice_departs_step']
        postjam=res['log'][js-1]['n_tiles'];from_baseline=len(full)-len(jam['full']);first_batch=len(trace[js-1]['added'])
        assert from_baseline==len(full)-postjam+first_batch
        baseline_groups[tilehash(jam['full'])].append(tag);final_groups[normalized_hash(full)].append(tag)
        sequence_key=hashlib.sha256(repr([normalized_hash(t['post']) for t in trace]).encode()).hexdigest();sequence_groups[sequence_key].append(tag)
        rec=dict(case=tag,stream=res['stream'],jam_step=js,final_step=res['final_step'],prejam_exact=checks,first_scar_step_pre_equals_frozen_jam=True,prejam_all_rng_and_geometry_equal=True,total_additions_checked=sum(len(t['added']) for t in trace),baseline_jam_full_tiles=len(jam['full']),post_first_scar_batch_tiles=postjam,first_scar_step_additions=first_batch,final_full_tiles=len(full),added_from_frozen_jam=from_baseline,historical_added_after_scar_step=len(full)-postjam,zero_placement_steps=zero_steps,choice_departure_step=departure,B_in_jam_band=any(S.dk(t)==S.dk(res['B']) for t in jam['band']),B_in_final_band=rows[-1]['B_in_band'],B_in_final_archive=any(S.dk(t)==S.dk(res['B']) for t in full),legality=geo,checkpoints=rows,final_full_hash=tilehash(full),final_band_hash=tilehash(res['band']))
        out.append(rec);dump('scheduler_verification.json',dict(cases=out,complete=False));print(tag,'placements',rec['total_additions_checked'],'postjam',from_baseline,'scars',rows[-1]['cumulative_scar']['edges'],'current',rows[-1]['labelled_current']['edges'],'blocked',rows[-1]['current_zero_candidate']['edges'],flush=True)
    baseline_groups=collections.defaultdict(list);final_groups=collections.defaultdict(list);sequence_groups=collections.defaultdict(list);all_states=set();all_finals=set()
    for w,si in S.B_JAMS:
        tag=f'w{w}-B-s{si}';jam=load(f'jam-{w}-{si}.pkl');res=load(f'growth-{w}-{si}.pkl');trace=load(f'trace-{w}-{si}.pkl')
        baseline_groups[tilehash(jam['full'])].append(tag);final_groups[normalized_hash(res['full'])].append(tag)
        sequence_key=hashlib.sha256(repr([normalized_hash(t['post']) for t in trace]).encode()).hexdigest();sequence_groups[sequence_key].append(tag)
        all_states.update(exacthash(t['post']) for t in trace);all_finals.add(exacthash(res['full']))
    dump('scheduler_verification.json',dict(cases=out,complete=True,exact_jam_geometry_groups=list(baseline_groups.values()),translation_normalized_final_groups=list(final_groups.values()),translation_normalized_full_trajectory_groups=list(sequence_groups.values()),unique_frontier_states_checked=len(all_states),unique_final_geometries_checked=len(all_finals)))

if __name__=='__main__':main()
